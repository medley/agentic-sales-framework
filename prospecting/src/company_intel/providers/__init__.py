"""
Company Intel Providers - Data source integrations for company intelligence

Each provider fetches company data from a specific source and extracts signals.
All providers inherit from BaseIntelProvider.

Available Providers:
- SECProvider: SEC EDGAR filings (10-K, 10-Q, 8-K)
- FDAProvider: FDA enforcement, warning letters (stub)
- NewsProvider: News aggregation (stub)
- JobsProvider: Job postings/hiring signals (stub)
- ZoomInfoProvider: ZoomInfo scoops/intent (stub)
"""

from .base_provider import BaseIntelProvider
from .sec_provider import SECProvider

__all__ = [
    'BaseIntelProvider',
    'SECProvider',
]
