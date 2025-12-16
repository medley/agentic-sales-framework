"""
FDA Provider - Extract company intelligence from FDA enforcement/warning letters

STUB: Not yet implemented.

Future implementation will provide:
- FDA warning letter lookup
- 483 observation extraction
- Consent decree detection
- Enforcement action signals
"""

from typing import Dict, List, Optional, Any

from .base_provider import BaseIntelProvider
from ..models import CompanySignal


class FDAProvider(BaseIntelProvider):
    """
    FDA provider for regulatory enforcement intelligence.

    NOT YET IMPLEMENTED - Stub for future development.
    """

    provider_name = "fda"
    metadata_ttl_days = 30
    data_ttl_days = 7

    def lookup_company(
        self,
        company_name: str,
        hints: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Look up company in FDA databases."""
        raise NotImplementedError(
            "FDA provider not yet implemented. "
            "Future: FDA warning letters, 483s, consent decrees."
        )

    def fetch_data(
        self,
        metadata: Dict[str, Any],
        cache: Any = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch FDA enforcement data."""
        raise NotImplementedError("FDA provider not yet implemented.")

    def extract_signals(
        self,
        data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[CompanySignal]:
        """Extract signals from FDA data."""
        raise NotImplementedError("FDA provider not yet implemented.")
