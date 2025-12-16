"""
News Provider - Extract company intelligence from news aggregation

STUB: Not yet implemented.

Future implementation will provide:
- News article aggregation
- M&A activity detection
- Leadership change signals
- Expansion/contraction signals
"""

from typing import Dict, List, Optional, Any

from .base_provider import BaseIntelProvider
from ..models import CompanySignal


class NewsProvider(BaseIntelProvider):
    """
    News provider for company news intelligence.

    NOT YET IMPLEMENTED - Stub for future development.
    """

    provider_name = "news"
    metadata_ttl_days = 1   # News is time-sensitive
    data_ttl_days = 1

    def lookup_company(
        self,
        company_name: str,
        hints: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Look up company in news sources."""
        raise NotImplementedError(
            "News provider not yet implemented. "
            "Future: News aggregation, M&A, leadership changes."
        )

    def fetch_data(
        self,
        metadata: Dict[str, Any],
        cache: Any = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch news articles."""
        raise NotImplementedError("News provider not yet implemented.")

    def extract_signals(
        self,
        data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[CompanySignal]:
        """Extract signals from news data."""
        raise NotImplementedError("News provider not yet implemented.")
