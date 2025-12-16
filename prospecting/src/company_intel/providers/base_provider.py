"""
Base Intel Provider - Abstract base class for company intelligence providers

All providers (SEC, FDA, news, jobs, ZoomInfo) inherit from this class.
Each provider is responsible for:
1. Looking up company data from their source
2. Fetching and caching raw data
3. Extracting signals from the raw data
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..models import CompanySignal, ProviderStatus

logger = logging.getLogger(__name__)


@dataclass
class ProviderResult:
    """
    Result from a provider execution.

    Contains status, signals, and any metadata to store.
    """
    status: str                         # 'success', 'error', 'skipped', 'not_found'
    signals: List[CompanySignal]        # Extracted signals
    metadata: Optional[Dict[str, Any]] = None  # Provider-specific metadata
    error: Optional[str] = None         # Error message if status='error'

    def to_provider_status(self, ttl_days: int) -> ProviderStatus:
        """Convert to ProviderStatus for index.json."""
        now = datetime.utcnow()
        expires = now + __import__('datetime').timedelta(days=ttl_days)

        return ProviderStatus(
            status=self.status,
            ran=True,
            last_run=now.isoformat() + 'Z',
            expires_at=expires.isoformat() + 'Z',
            signal_count=len(self.signals),
            error=self.error
        )


class BaseIntelProvider(ABC):
    """
    Abstract base class for company intelligence providers.

    Each provider must implement:
    - provider_name: Unique identifier for the provider
    - metadata_ttl_days: How long to cache metadata
    - lookup_company(): Find company in provider's data source
    - fetch_data(): Download/fetch full data for the company
    - extract_signals(): Extract signals from the fetched data

    Lifecycle:
    1. lookup_company() - Quick lookup to see if data exists
    2. fetch_data() - Full data fetch (may be expensive)
    3. extract_signals() - Signal extraction from fetched data
    """

    # Class attributes (override in subclasses)
    provider_name: str = "base"
    metadata_ttl_days: int = 30
    data_ttl_days: int = 14

    def __init__(self):
        """Initialize provider."""
        self.logger = logging.getLogger(f"{__name__}.{self.provider_name}")

    @abstractmethod
    def lookup_company(
        self,
        company_name: str,
        hints: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Look up company in this provider's data source.

        This should be a quick lookup to determine if data exists
        and retrieve basic metadata (IDs, names, etc.).

        Args:
            company_name: Company name to search for
            hints: Optional hints like domain, CIK, etc.

        Returns:
            Provider-specific metadata dict or None if not found
        """
        pass

    @abstractmethod
    def fetch_data(
        self,
        metadata: Dict[str, Any],
        cache: Any = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch full data for the company.

        This may be an expensive operation (downloading documents, etc.).
        The cache parameter allows checking for cached data.

        Args:
            metadata: Metadata from lookup_company()
            cache: Optional cache instance for checking existing data

        Returns:
            Full data dict or None if fetch fails
        """
        pass

    @abstractmethod
    def extract_signals(
        self,
        data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[CompanySignal]:
        """
        Extract signals from fetched data.

        Signals should have:
        - Real source URLs (never fake)
        - Proper source_type classification
        - Key terms for semantic validation
        - as_of_date when available

        Args:
            data: Data from fetch_data()
            metadata: Metadata from lookup_company()

        Returns:
            List of CompanySignal objects
        """
        pass

    def run(
        self,
        company_name: str,
        cache: Any = None,
        hints: Optional[Dict[str, str]] = None,
        force_refresh: bool = False
    ) -> ProviderResult:
        """
        Execute full provider workflow.

        1. Lookup company
        2. Fetch data (if found)
        3. Extract signals

        Args:
            company_name: Company to research
            cache: Optional cache instance
            hints: Optional lookup hints
            force_refresh: Force re-fetch even if cached

        Returns:
            ProviderResult with status and signals
        """
        self.logger.info(f"Running {self.provider_name} provider for {company_name}")

        # Step 1: Lookup
        try:
            metadata = self.lookup_company(company_name, hints)
            if not metadata:
                self.logger.info(f"{company_name} not found in {self.provider_name}")
                return ProviderResult(
                    status='not_found',
                    signals=[],
                    error=f"Company not found in {self.provider_name}"
                )
        except Exception as e:
            self.logger.error(f"Lookup failed: {e}")
            return ProviderResult(
                status='error',
                signals=[],
                error=f"Lookup failed: {str(e)}"
            )

        # Step 2: Fetch data
        try:
            data = self.fetch_data(metadata, cache)
            if not data:
                self.logger.warning(f"No data fetched for {company_name}")
                return ProviderResult(
                    status='error',
                    signals=[],
                    metadata=metadata,
                    error="Data fetch returned empty"
                )
        except Exception as e:
            self.logger.error(f"Fetch failed: {e}")
            return ProviderResult(
                status='error',
                signals=[],
                metadata=metadata,
                error=f"Fetch failed: {str(e)}"
            )

        # Step 3: Extract signals
        try:
            signals = self.extract_signals(data, metadata)
            self.logger.info(f"Extracted {len(signals)} signals for {company_name}")

            return ProviderResult(
                status='success',
                signals=signals,
                metadata=metadata
            )
        except Exception as e:
            self.logger.error(f"Signal extraction failed: {e}")
            return ProviderResult(
                status='error',
                signals=[],
                metadata=metadata,
                error=f"Signal extraction failed: {str(e)}"
            )

    def should_refresh(
        self,
        cache: Any,
        primary_account_id: str,
        force: bool = False
    ) -> bool:
        """
        Check if provider data should be refreshed.

        Args:
            cache: CompanyIntelCache instance
            primary_account_id: Account to check
            force: Force refresh regardless of TTL

        Returns:
            True if data should be refreshed
        """
        if force:
            return True

        return cache.is_expired(primary_account_id, self.provider_name)
