"""
Company Intel Cache - File-based persistent storage for company intelligence

All company intel is stored under:
    $PROSPECTING_OUTPUT_ROOT/accounts/{primary_account_id}/intel/

This module handles:
- Reading/writing index.json (master index with provider status + aliases)
- Reading/writing signals_*.json files
- Reading/writing provider-specific data (e.g., sec/metadata.json)
- TTL checking for cached data
- Alias lookup across all cached accounts
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any, List

try:
    from path_resolver import (
        get_accounts_root,
        get_intel_folder,
        get_provider_folder,
        ensure_intel_folders_exist,
    )
except ImportError:
    # Fallback for when running from different contexts
    from ..path_resolver import (
        get_accounts_root,
        get_intel_folder,
        get_provider_folder,
        ensure_intel_folders_exist,
    )
from .models import (
    CompanySignal,
    CompanyAliases,
    ProviderStatus,
    CompanyIntelResult,
    SECMetadata,
    SECFiling,
)

logger = logging.getLogger(__name__)


class CompanyIntelCache:
    """
    File-based cache for company intelligence.

    Storage layout:
        {accounts_root}/{primary_account_id}/intel/
        ├── index.json              # Master index with aliases
        ├── signals_public.json     # public_url signals
        ├── signals_vendor.json     # vendor_data signals
        ├── signals_user.json       # user_provided signals
        ├── sources.json            # All source URLs
        └── sec/
            ├── metadata.json
            ├── filings_index.json
            ├── 10k_latest.txt
            └── signals.json
    """

    # Global alias index file for cross-account lookups
    ALIAS_INDEX_FILE = "alias_index.json"

    def __init__(self, accounts_root: Path = None):
        """
        Initialize cache.

        Args:
            accounts_root: Override accounts root path (for testing)
        """
        self.accounts_root = accounts_root or get_accounts_root()
        self._alias_index: Optional[Dict[str, str]] = None

    # =========================================================================
    # Path Helpers (use self.accounts_root for test compatibility)
    # =========================================================================

    def _get_intel_folder(self, primary_account_id: str) -> Path:
        """Get intel folder path using self.accounts_root."""
        return self.accounts_root / primary_account_id / "intel"

    def _get_provider_folder(self, primary_account_id: str, provider: str) -> Path:
        """Get provider folder path using self.accounts_root."""
        return self._get_intel_folder(primary_account_id) / provider

    def _ensure_intel_folders(self, primary_account_id: str, providers: list = None) -> None:
        """Ensure intel folders exist."""
        intel_folder = self._get_intel_folder(primary_account_id)
        intel_folder.mkdir(parents=True, exist_ok=True)

        if providers:
            for provider in providers:
                provider_folder = self._get_provider_folder(primary_account_id, provider)
                provider_folder.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # Index Management
    # =========================================================================

    def get_index(self, primary_account_id: str) -> Optional[Dict[str, Any]]:
        """
        Load index.json for an account.

        Args:
            primary_account_id: Salesforce Primary Account ID

        Returns:
            Index dict or None if not found
        """
        index_path = self._get_intel_folder(primary_account_id) / "index.json"

        if not index_path.exists():
            return None

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to read index for {primary_account_id}: {e}")
            return None

    def save_index(self, primary_account_id: str, index: Dict[str, Any]) -> bool:
        """
        Save index.json for an account.

        Args:
            primary_account_id: Salesforce Primary Account ID
            index: Index dict to save

        Returns:
            True if saved successfully
        """
        self._ensure_intel_folders(primary_account_id)
        index_path = self._get_intel_folder(primary_account_id) / "index.json"

        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved index for {primary_account_id}")

            # Update alias index
            if 'aliases' in index:
                self._update_alias_index(primary_account_id, index['aliases'])

            return True
        except IOError as e:
            logger.error(f"Failed to save index for {primary_account_id}: {e}")
            return False

    def create_index(
        self,
        primary_account_id: str,
        company_name: str,
        aliases: CompanyAliases = None
    ) -> Dict[str, Any]:
        """
        Create a new index for an account.

        Args:
            primary_account_id: Salesforce Primary Account ID
            company_name: Company display name
            aliases: Initial aliases

        Returns:
            New index dict (not yet saved)
        """
        now = datetime.utcnow().isoformat() + 'Z'

        return {
            'company_name': company_name,
            'primary_account_id': primary_account_id,
            'aliases': (aliases or CompanyAliases()).to_dict(),
            'created_at': now,
            'last_refreshed': now,
            'providers': {},
            'total_signals': {
                'public_url': 0,
                'vendor_data': 0,
                'user_provided': 0,
                'inferred': 0
            }
        }

    # =========================================================================
    # Signal Management
    # =========================================================================

    def get_signals(
        self,
        primary_account_id: str,
        source_type: str
    ) -> List[Dict[str, Any]]:
        """
        Load signals of a specific source_type.

        Args:
            primary_account_id: Salesforce Primary Account ID
            source_type: 'public_url', 'vendor_data', 'user_provided', or 'inferred'

        Returns:
            List of signal dicts
        """
        filename = f"signals_{source_type.replace('_url', '')}.json"
        signals_path = self._get_intel_folder(primary_account_id) / filename

        if not signals_path.exists():
            return []

        try:
            with open(signals_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('signals', [])
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to read signals for {primary_account_id}: {e}")
            return []

    def save_signals(
        self,
        primary_account_id: str,
        source_type: str,
        signals: List[Dict[str, Any]]
    ) -> bool:
        """
        Save signals of a specific source_type.

        Args:
            primary_account_id: Salesforce Primary Account ID
            source_type: 'public_url', 'vendor_data', 'user_provided', or 'inferred'
            signals: List of signal dicts

        Returns:
            True if saved successfully
        """
        self._ensure_intel_folders(primary_account_id)

        # Map source_type to filename
        filename_map = {
            'public_url': 'signals_public.json',
            'vendor_data': 'signals_vendor.json',
            'user_provided': 'signals_user.json',
            'inferred': 'signals_inferred.json'
        }
        filename = filename_map.get(source_type, f"signals_{source_type}.json")
        signals_path = self._get_intel_folder(primary_account_id) / filename

        try:
            data = {
                'source_type': source_type,
                'updated_at': datetime.utcnow().isoformat() + 'Z',
                'signals': signals
            }
            with open(signals_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(signals)} {source_type} signals for {primary_account_id}")
            return True
        except IOError as e:
            logger.error(f"Failed to save signals for {primary_account_id}: {e}")
            return False

    def get_all_signals(self, primary_account_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load all signals for an account, grouped by source_type.

        Args:
            primary_account_id: Salesforce Primary Account ID

        Returns:
            Dict mapping source_type to list of signals
        """
        return {
            'public_url': self.get_signals(primary_account_id, 'public_url'),
            'vendor_data': self.get_signals(primary_account_id, 'vendor_data'),
            'user_provided': self.get_signals(primary_account_id, 'user_provided'),
            'inferred': self.get_signals(primary_account_id, 'inferred'),
        }

    # =========================================================================
    # Provider Data Management
    # =========================================================================

    def get_provider_data(
        self,
        primary_account_id: str,
        provider: str,
        filename: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load provider-specific data file.

        Args:
            primary_account_id: Salesforce Primary Account ID
            provider: Provider name (e.g., 'sec')
            filename: File within provider folder (e.g., 'metadata.json')

        Returns:
            Data dict or None if not found
        """
        data_path = self._get_provider_folder(primary_account_id, provider) / filename

        if not data_path.exists():
            return None

        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to read {provider}/{filename} for {primary_account_id}: {e}")
            return None

    def save_provider_data(
        self,
        primary_account_id: str,
        provider: str,
        filename: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Save provider-specific data file.

        Args:
            primary_account_id: Salesforce Primary Account ID
            provider: Provider name (e.g., 'sec')
            filename: File within provider folder (e.g., 'metadata.json')
            data: Data dict to save

        Returns:
            True if saved successfully
        """
        self._ensure_intel_folders(primary_account_id, providers=[provider])
        data_path = self._get_provider_folder(primary_account_id, provider) / filename

        try:
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {provider}/{filename} for {primary_account_id}")
            return True
        except IOError as e:
            logger.error(f"Failed to save {provider}/{filename} for {primary_account_id}: {e}")
            return False

    def get_provider_text(
        self,
        primary_account_id: str,
        provider: str,
        filename: str
    ) -> Optional[str]:
        """
        Load provider-specific text file (e.g., 10k_latest.txt).

        Args:
            primary_account_id: Salesforce Primary Account ID
            provider: Provider name (e.g., 'sec')
            filename: File within provider folder (e.g., '10k_latest.txt')

        Returns:
            File contents or None if not found
        """
        text_path = self._get_provider_folder(primary_account_id, provider) / filename

        if not text_path.exists():
            return None

        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            logger.error(f"Failed to read {provider}/{filename} for {primary_account_id}: {e}")
            return None

    def save_provider_text(
        self,
        primary_account_id: str,
        provider: str,
        filename: str,
        text: str
    ) -> bool:
        """
        Save provider-specific text file.

        Args:
            primary_account_id: Salesforce Primary Account ID
            provider: Provider name (e.g., 'sec')
            filename: File within provider folder (e.g., '10k_latest.txt')
            text: Text content to save

        Returns:
            True if saved successfully
        """
        self._ensure_intel_folders(primary_account_id, providers=[provider])
        text_path = self._get_provider_folder(primary_account_id, provider) / filename

        try:
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text)
            logger.info(f"Saved {provider}/{filename} ({len(text)} chars) for {primary_account_id}")
            return True
        except IOError as e:
            logger.error(f"Failed to save {provider}/{filename} for {primary_account_id}: {e}")
            return False

    # =========================================================================
    # TTL Management
    # =========================================================================

    def is_expired(
        self,
        primary_account_id: str,
        provider: str = None
    ) -> bool:
        """
        Check if cached data has expired.

        Args:
            primary_account_id: Salesforce Primary Account ID
            provider: Optional specific provider to check

        Returns:
            True if expired or not found
        """
        index = self.get_index(primary_account_id)
        if not index:
            return True

        if provider:
            provider_status = index.get('providers', {}).get(provider)
            if not provider_status:
                return True

            expires_at = provider_status.get('expires_at')
            if not expires_at:
                return True

            try:
                expires = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                return datetime.now(expires.tzinfo) > expires
            except (ValueError, TypeError):
                return True
        else:
            # Check if all providers are expired
            providers = index.get('providers', {})
            if not providers:
                return True

            for prov, status in providers.items():
                expires_at = status.get('expires_at')
                if expires_at:
                    try:
                        expires = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                        if datetime.now(expires.tzinfo) <= expires:
                            return False  # At least one provider is not expired
                    except (ValueError, TypeError):
                        pass

            return True

    def get_expiry_time(self, ttl_days: int) -> str:
        """
        Calculate expiry timestamp from now.

        Args:
            ttl_days: Number of days until expiry

        Returns:
            ISO timestamp string
        """
        expires = datetime.utcnow() + timedelta(days=ttl_days)
        return expires.isoformat() + 'Z'

    # =========================================================================
    # Alias Management
    # =========================================================================

    def _load_alias_index(self) -> Dict[str, str]:
        """
        Load the global alias index (maps aliases to primary_account_ids).

        Returns:
            Dict mapping alias values to primary_account_ids
        """
        if self._alias_index is not None:
            return self._alias_index

        alias_index_path = self.accounts_root / self.ALIAS_INDEX_FILE

        if not alias_index_path.exists():
            self._alias_index = {}
            return self._alias_index

        try:
            with open(alias_index_path, 'r', encoding='utf-8') as f:
                self._alias_index = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load alias index: {e}")
            self._alias_index = {}

        return self._alias_index

    def _save_alias_index(self) -> bool:
        """
        Save the global alias index.

        Returns:
            True if saved successfully
        """
        if self._alias_index is None:
            return True

        alias_index_path = self.accounts_root / self.ALIAS_INDEX_FILE

        try:
            self.accounts_root.mkdir(parents=True, exist_ok=True)
            with open(alias_index_path, 'w', encoding='utf-8') as f:
                json.dump(self._alias_index, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            logger.error(f"Failed to save alias index: {e}")
            return False

    def _update_alias_index(
        self,
        primary_account_id: str,
        aliases: Dict[str, Any]
    ) -> None:
        """
        Update the global alias index with new aliases.

        Args:
            primary_account_id: Salesforce Primary Account ID
            aliases: Aliases dict from index.json
        """
        alias_index = self._load_alias_index()

        # Add all alias values
        for site_id in aliases.get('site_account_ids', []):
            alias_index[f"site:{site_id}"] = primary_account_id

        for domain in aliases.get('domains', []):
            alias_index[f"domain:{domain.lower()}"] = primary_account_id

        for zi_id in aliases.get('zoominfo_company_ids', []):
            alias_index[f"zoominfo:{zi_id}"] = primary_account_id

        if aliases.get('sec_cik'):
            alias_index[f"sec_cik:{aliases['sec_cik']}"] = primary_account_id

        for name in aliases.get('normalized_names', []):
            alias_index[f"name:{name.lower()}"] = primary_account_id

        self._alias_index = alias_index
        self._save_alias_index()

    def lookup_by_alias(
        self,
        alias_type: str,
        alias_value: str
    ) -> Optional[str]:
        """
        Find primary_account_id by alias.

        Args:
            alias_type: 'site', 'domain', 'zoominfo', 'sec_cik', or 'name'
            alias_value: The alias value to look up

        Returns:
            primary_account_id or None if not found
        """
        alias_index = self._load_alias_index()
        key = f"{alias_type}:{alias_value.lower()}"
        return alias_index.get(key)

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
        # Update in-memory index
        alias_index = self._load_alias_index()

        # Map alias_type to prefix
        prefix_map = {
            'site_account_id': 'site',
            'domain': 'domain',
            'zoominfo_id': 'zoominfo',
            'sec_cik': 'sec_cik',
            'name': 'name'
        }
        prefix = prefix_map.get(alias_type, alias_type)
        key = f"{prefix}:{alias_value.lower()}"

        alias_index[key] = primary_account_id
        self._alias_index = alias_index

        # Also update index.json
        index = self.get_index(primary_account_id)
        if index:
            aliases = CompanyAliases.from_dict(index.get('aliases', {}))
            aliases.add_alias(alias_type, alias_value)
            index['aliases'] = aliases.to_dict()
            self.save_index(primary_account_id, index)

        return self._save_alias_index()

    # =========================================================================
    # Full Result Loading
    # =========================================================================

    def load_company_intel(self, primary_account_id: str) -> Optional[CompanyIntelResult]:
        """
        Load complete company intel for an account.

        Args:
            primary_account_id: Salesforce Primary Account ID

        Returns:
            CompanyIntelResult or None if not found
        """
        index = self.get_index(primary_account_id)
        if not index:
            return None

        # Load all signals
        signals = self.get_all_signals(primary_account_id)

        # Convert to CompanySignal objects
        signals_converted = {}
        for source_type, signal_list in signals.items():
            signals_converted[source_type] = [
                CompanySignal.from_dict(s) if isinstance(s, dict) else s
                for s in signal_list
            ]

        # Build result
        return CompanyIntelResult(
            company_name=index.get('company_name', ''),
            primary_account_id=primary_account_id,
            aliases=CompanyAliases.from_dict(index.get('aliases', {})),
            created_at=index.get('created_at'),
            last_refreshed=index.get('last_refreshed'),
            sources={
                k: ProviderStatus.from_dict(v)
                for k, v in index.get('providers', {}).items()
            },
            signals=signals_converted,
            total_signals=index.get('total_signals', {}),
            errors=[]
        )

    # =========================================================================
    # Account Discovery
    # =========================================================================

    def list_accounts(self) -> List[str]:
        """
        List all cached account IDs.

        Returns:
            List of primary_account_ids
        """
        if not self.accounts_root.exists():
            return []

        accounts = []
        for item in self.accounts_root.iterdir():
            if item.is_dir() and (item / "intel" / "index.json").exists():
                accounts.append(item.name)

        return accounts

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats
        """
        accounts = self.list_accounts()
        alias_index = self._load_alias_index()

        total_signals = 0
        providers_used = set()

        for account_id in accounts:
            index = self.get_index(account_id)
            if index:
                for count in index.get('total_signals', {}).values():
                    total_signals += count
                providers_used.update(index.get('providers', {}).keys())

        return {
            'account_count': len(accounts),
            'alias_count': len(alias_index),
            'total_signals': total_signals,
            'providers_used': list(providers_used)
        }
