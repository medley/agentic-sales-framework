"""
Jobs Provider - Extract company intelligence from job postings

STUB: Not yet implemented.

Future implementation will provide:
- Job posting aggregation
- Hiring trend signals
- Technology stack inference from job requirements
- Growth/contraction indicators
"""

from typing import Dict, List, Optional, Any

from .base_provider import BaseIntelProvider
from ..models import CompanySignal


class JobsProvider(BaseIntelProvider):
    """
    Jobs provider for hiring/technology intelligence.

    NOT YET IMPLEMENTED - Stub for future development.
    """

    provider_name = "jobs"
    metadata_ttl_days = 7   # Job postings change frequently
    data_ttl_days = 3

    def lookup_company(
        self,
        company_name: str,
        hints: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Look up company in job boards."""
        raise NotImplementedError(
            "Jobs provider not yet implemented. "
            "Future: Job postings, hiring trends, tech stack inference."
        )

    def fetch_data(
        self,
        metadata: Dict[str, Any],
        cache: Any = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch job postings."""
        raise NotImplementedError("Jobs provider not yet implemented.")

    def extract_signals(
        self,
        data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[CompanySignal]:
        """Extract signals from job data."""
        raise NotImplementedError("Jobs provider not yet implemented.")
