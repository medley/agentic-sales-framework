"""
Company Intel Service - Main orchestrator for company intelligence

This service:
1. Resolves company identifiers to primary_account_id
2. Coordinates provider execution (SEC, FDA, news, etc.)
3. Manages caching and TTL expiration
4. Aggregates signals from all providers

Usage:
    service = CompanyIntelService()
    intel = service.get_company_intel(
        company_name="Acme Pharmaceuticals",
        primary_account_id="001ABC123456789"
    )
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from .company_intel_cache import CompanyIntelCache
from .models import (
    CompanySignal,
    CompanyAliases,
    ProviderStatus,
    CompanyIntelResult,
)
from .providers.base_provider import BaseIntelProvider, ProviderResult
from .providers.sec_provider import SECProvider

logger = logging.getLogger(__name__)


class CompanyIntelService:
    """
    Main service for company intelligence.

    Orchestrates:
    - Company key resolution (primary_account_id as canonical)
    - Provider execution (SEC, FDA, news, jobs, ZoomInfo)
    - Caching and refresh logic
    - Signal aggregation
    """

    # Default providers to run
    DEFAULT_PROVIDERS = ['sec']

    def __init__(
        self,
        cache: CompanyIntelCache = None,
        providers: Dict[str, BaseIntelProvider] = None
    ):
        """
        Initialize service.

        Args:
            cache: CompanyIntelCache instance (created if not provided)
            providers: Dict of provider_name -> provider instance
        """
        self.cache = cache or CompanyIntelCache()

        # Initialize default providers
        self.providers = providers or {
            'sec': SECProvider()
        }

    def get_company_intel(
        self,
        company_name: str,
        primary_account_id: str = None,
        site_account_id: str = None,
        domain: str = None,
        refresh: bool = False,
        providers: List[str] = None
    ) -> CompanyIntelResult:
        """
        Get company intelligence.

        Resolution priority:
        1. primary_account_id (if provided, use directly)
        2. site_account_id (resolve to primary via aliases)
        3. domain (resolve via aliases)
        4. Generate new from company_name

        Args:
            company_name: Company display name
            primary_account_id: Salesforce Primary Account ID (canonical)
            site_account_id: Salesforce Site Account ID (will resolve)
            domain: Company domain (will resolve)
            refresh: Force refresh all providers
            providers: List of provider names to run (default: all)

        Returns:
            CompanyIntelResult with signals and metadata
        """
        # Resolve to canonical primary_account_id
        resolved_id = self.resolve_primary_account_id(
            company_name=company_name,
            primary_account_id=primary_account_id,
            site_account_id=site_account_id,
            domain=domain
        )

        logger.info(f"Getting company intel for {company_name} (id: {resolved_id})")

        # Check cache
        if not refresh:
            cached = self.cache.load_company_intel(resolved_id)
            if cached and not self.cache.is_expired(resolved_id):
                logger.info(f"Using cached intel for {resolved_id}")
                return cached

        # Create or update index
        index = self.cache.get_index(resolved_id)
        if not index:
            aliases = CompanyAliases()
            if site_account_id:
                aliases.add_alias('site_account_id', site_account_id)
            if domain:
                aliases.add_alias('domain', domain)

            index = self.cache.create_index(resolved_id, company_name, aliases)

        # Determine which providers to run
        providers_to_run = providers or self.DEFAULT_PROVIDERS
        active_providers = [
            self.providers[p] for p in providers_to_run
            if p in self.providers
        ]

        if not active_providers:
            logger.warning("No active providers configured")
            return self._build_empty_result(resolved_id, company_name, index)

        # Run providers
        all_signals: Dict[str, List[CompanySignal]] = {
            'public_url': [],
            'vendor_data': [],
            'user_provided': [],
            'inferred': []
        }
        errors = []

        for provider in active_providers:
            should_run = refresh or self.cache.is_expired(resolved_id, provider.provider_name)

            if not should_run:
                logger.info(f"Skipping {provider.provider_name} (not expired)")
                continue

            logger.info(f"Running {provider.provider_name} provider")

            # Build hints from aliases
            hints = self._build_hints(index)

            # Run provider
            result = provider.run(
                company_name=company_name,
                cache=self.cache,
                hints=hints,
                force_refresh=refresh
            )

            # Store provider status
            provider_status = result.to_provider_status(provider.metadata_ttl_days)
            index['providers'][provider.provider_name] = provider_status.to_dict()

            # Store provider-specific data
            if result.metadata:
                self.cache.save_provider_data(
                    resolved_id,
                    provider.provider_name,
                    'metadata.json',
                    result.metadata
                )

                # Register SEC CIK alias if found
                if provider.provider_name == 'sec' and result.metadata.get('sec_cik'):
                    self.register_alias(
                        resolved_id,
                        'sec_cik',
                        result.metadata['sec_cik']
                    )

            # Collect signals
            for signal in result.signals:
                source_type = signal.source_type
                if source_type not in all_signals:
                    all_signals[source_type] = []
                all_signals[source_type].append(signal)

            if result.error:
                errors.append(f"{provider.provider_name}: {result.error}")

        # Save signals by source_type
        for source_type, signals in all_signals.items():
            if signals:
                signal_dicts = [s.to_dict() for s in signals]
                self.cache.save_signals(resolved_id, source_type, signal_dicts)

        # Update totals
        index['total_signals'] = {
            source_type: len(signals)
            for source_type, signals in all_signals.items()
        }
        index['last_refreshed'] = datetime.utcnow().isoformat() + 'Z'

        # Save index
        self.cache.save_index(resolved_id, index)

        # Build result
        return CompanyIntelResult(
            company_name=company_name,
            primary_account_id=resolved_id,
            aliases=CompanyAliases.from_dict(index.get('aliases', {})),
            created_at=index.get('created_at'),
            last_refreshed=index.get('last_refreshed'),
            sources={
                k: ProviderStatus.from_dict(v)
                for k, v in index.get('providers', {}).items()
            },
            signals=all_signals,
            total_signals=index['total_signals'],
            errors=errors
        )

    def resolve_primary_account_id(
        self,
        company_name: str = None,
        primary_account_id: str = None,
        site_account_id: str = None,
        domain: str = None,
        zoominfo_id: str = None,
        sec_cik: str = None
    ) -> str:
        """
        Resolve any identifier to the canonical primary_account_id.

        Priority:
        1. primary_account_id (if provided)
        2. site_account_id (lookup in aliases)
        3. domain (lookup in aliases)
        4. zoominfo_id (lookup in aliases)
        5. sec_cik (lookup in aliases)
        6. Generate from normalized company name

        Args:
            company_name: Company display name (used as fallback)
            primary_account_id: Direct primary account ID
            site_account_id: Site account to resolve
            domain: Domain to resolve
            zoominfo_id: ZoomInfo ID to resolve
            sec_cik: SEC CIK to resolve

        Returns:
            Canonical primary_account_id
        """
        # 1. Direct ID
        if primary_account_id:
            return primary_account_id

        # 2. Site account lookup
        if site_account_id:
            resolved = self.cache.lookup_by_alias('site', site_account_id)
            if resolved:
                return resolved

        # 3. Domain lookup
        if domain:
            resolved = self.cache.lookup_by_alias('domain', domain)
            if resolved:
                return resolved

        # 4. ZoomInfo lookup
        if zoominfo_id:
            resolved = self.cache.lookup_by_alias('zoominfo', zoominfo_id)
            if resolved:
                return resolved

        # 5. SEC CIK lookup
        if sec_cik:
            resolved = self.cache.lookup_by_alias('sec_cik', sec_cik)
            if resolved:
                return resolved

        # 6. Generate from company name (last resort)
        if company_name:
            normalized = self._normalize_company_name(company_name)
            # Check if we have this normalized name
            resolved = self.cache.lookup_by_alias('name', normalized)
            if resolved:
                return resolved

            # Generate new ID based on normalized name
            # Format: name_{normalized} (this is the fallback format)
            return f"name_{normalized}"

        raise ValueError("Unable to resolve primary_account_id: no identifiers provided")

    def _normalize_company_name(self, name: str) -> str:
        """
        Normalize company name for use as identifier.

        Args:
            name: Raw company name

        Returns:
            Normalized name (lowercase, alphanumeric, hyphens)
        """
        # Remove common suffixes
        suffixes = [
            ' inc', ' inc.', ' incorporated',
            ' llc', ' l.l.c.',
            ' ltd', ' ltd.', ' limited',
            ' corp', ' corp.', ' corporation',
            ' company', ' co', ' co.',
            ' plc', ' sa', ' ag', ' gmbh'
        ]
        name_lower = name.lower()
        for suffix in suffixes:
            if name_lower.endswith(suffix):
                name_lower = name_lower[:-len(suffix)]

        # Convert to alphanumeric + hyphens
        normalized = re.sub(r'[^a-z0-9]', '-', name_lower)
        normalized = re.sub(r'-+', '-', normalized)
        normalized = normalized.strip('-')

        return normalized

    def register_alias(
        self,
        primary_account_id: str,
        alias_type: str,
        alias_value: str
    ) -> bool:
        """
        Register a new alias for an account.

        Args:
            primary_account_id: Salesforce Primary Account ID
            alias_type: 'site_account_id', 'domain', 'zoominfo_id', 'sec_cik', or 'name'
            alias_value: The alias value

        Returns:
            True if registered successfully
        """
        return self.cache.register_alias(primary_account_id, alias_type, alias_value)

    def _build_hints(self, index: Dict[str, Any]) -> Dict[str, str]:
        """
        Build provider hints from index aliases.

        Args:
            index: Index dict with aliases

        Returns:
            Hints dict for provider lookup
        """
        hints = {}
        aliases = index.get('aliases', {})

        if aliases.get('sec_cik'):
            hints['sec_cik'] = aliases['sec_cik']

        if aliases.get('domains'):
            hints['domain'] = aliases['domains'][0]

        if aliases.get('zoominfo_company_ids'):
            hints['zoominfo_id'] = aliases['zoominfo_company_ids'][0]

        return hints

    def _build_empty_result(
        self,
        primary_account_id: str,
        company_name: str,
        index: Dict[str, Any]
    ) -> CompanyIntelResult:
        """
        Build empty result when no providers run.
        """
        return CompanyIntelResult(
            company_name=company_name,
            primary_account_id=primary_account_id,
            aliases=CompanyAliases.from_dict(index.get('aliases', {})),
            created_at=index.get('created_at'),
            last_refreshed=index.get('last_refreshed'),
            sources={},
            signals={
                'public_url': [],
                'vendor_data': [],
                'user_provided': [],
                'inferred': []
            },
            total_signals={
                'public_url': 0,
                'vendor_data': 0,
                'user_provided': 0,
                'inferred': 0
            },
            errors=['No providers configured or available']
        )

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def refresh_company_intel(
        self,
        primary_account_id: str,
        company_name: str = None,
        providers: List[str] = None
    ) -> CompanyIntelResult:
        """
        Force refresh company intel.

        Args:
            primary_account_id: Account to refresh
            company_name: Company name (optional, will be loaded from cache)
            providers: Specific providers to refresh

        Returns:
            Updated CompanyIntelResult
        """
        # Get company name from cache if not provided
        if not company_name:
            index = self.cache.get_index(primary_account_id)
            company_name = index.get('company_name', '') if index else ''

        return self.get_company_intel(
            company_name=company_name,
            primary_account_id=primary_account_id,
            refresh=True,
            providers=providers
        )

    def get_signals_for_relevance_engine(
        self,
        primary_account_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get signals formatted for the relevance engine.

        Converts CompanySignal objects to the dict format expected
        by relevance_engine.extract_signals().

        Args:
            primary_account_id: Account to get signals for

        Returns:
            List of signal dicts compatible with relevance engine
        """
        intel = self.cache.load_company_intel(primary_account_id)
        if not intel:
            return []

        signals = []
        signal_counter = 1

        # Get cited signals (public_url, user_provided)
        for source_type in ['public_url', 'user_provided']:
            for signal in intel.signals.get(source_type, []):
                signals.append({
                    'id': f"ci_{signal_counter:03d}",
                    'claim': signal.claim,
                    'source_url': signal.source_url,
                    'source_type': signal.source_type,
                    'citability': signal.citability,
                    'verifiability': signal.citability,  # Backward compat
                    'scope': 'company_specific',
                    'recency_days': signal.recency_days,
                    'signal_type': f"{signal.provider}_filing",
                    'key_terms': signal.key_terms,
                    '_origin': 'company_intel',
                    '_provider': signal.provider
                })
                signal_counter += 1

        # Add vendor_data signals (uncited, for angle guidance)
        for signal in intel.signals.get('vendor_data', []):
            signals.append({
                'id': f"ci_{signal_counter:03d}",
                'claim': signal.claim,
                'source_url': signal.source_url,
                'source_type': signal.source_type,
                'citability': 'uncited',
                'verifiability': 'uncited',
                'scope': 'company_specific',
                'recency_days': signal.recency_days,
                'signal_type': f"{signal.provider}_data",
                'key_terms': signal.key_terms,
                '_origin': 'company_intel',
                '_provider': signal.provider
            })
            signal_counter += 1

        return signals

    def list_cached_accounts(self) -> List[Dict[str, Any]]:
        """
        List all cached accounts with basic info.

        Returns:
            List of account info dicts
        """
        accounts = []
        for account_id in self.cache.list_accounts():
            index = self.cache.get_index(account_id)
            if index:
                accounts.append({
                    'primary_account_id': account_id,
                    'company_name': index.get('company_name', ''),
                    'last_refreshed': index.get('last_refreshed'),
                    'providers': list(index.get('providers', {}).keys()),
                    'total_signals': sum(index.get('total_signals', {}).values())
                })

        return accounts

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats
        """
        return self.cache.get_cache_stats()
