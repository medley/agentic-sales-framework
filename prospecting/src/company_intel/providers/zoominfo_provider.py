"""
ZoomInfo Provider - Extract company intelligence from ZoomInfo scoops/intent

STUB: Not yet implemented.

Future implementation will provide:
- ZoomInfo scoops (company news/events)
- Intent data signals
- Technology install base
- Organizational changes

Note: ZoomInfo data is vendor_data, not public_url - signals from this
provider can only guide angle selection, not make explicit claims.
"""

from typing import Dict, List, Optional, Any

from .base_provider import BaseIntelProvider
from ..models import CompanySignal


class ZoomInfoProvider(BaseIntelProvider):
    """
    ZoomInfo provider for company scoops and intent signals.

    NOT YET IMPLEMENTED - Stub for future development.

    IMPORTANT: ZoomInfo data is source_type='vendor_data' which means:
    - Signals can guide angle/offer selection
    - Signals CANNOT be used for explicit company claims
    - Must be phrased generically in emails
    """

    provider_name = "zoominfo"
    metadata_ttl_days = 30
    data_ttl_days = 7

    def lookup_company(
        self,
        company_name: str,
        hints: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Look up company in ZoomInfo."""
        raise NotImplementedError(
            "ZoomInfo provider not yet implemented. "
            "Future: Scoops, intent data, tech install base."
        )

    def fetch_data(
        self,
        metadata: Dict[str, Any],
        cache: Any = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch ZoomInfo company data."""
        raise NotImplementedError("ZoomInfo provider not yet implemented.")

    def extract_signals(
        self,
        data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[CompanySignal]:
        """
        Extract signals from ZoomInfo data.

        Note: All signals from this provider MUST have:
        - source_type = 'vendor_data'
        - citability = 'uncited'
        """
        raise NotImplementedError("ZoomInfo provider not yet implemented.")
