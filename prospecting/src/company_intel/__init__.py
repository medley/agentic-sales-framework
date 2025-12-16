"""
Company Intelligence Module - Durable account-level intelligence caching

Fetches company-level intelligence once, caches it to disk under accounts/{primary_account_id}/intel/,
and reuses it across contacts. Supports SEC EDGAR, with hooks for FDA, news, jobs, and ZoomInfo.

Key Concepts:
- primary_account_id (Salesforce) is the CANONICAL key for all company intel
- Site accounts inherit company intel automatically
- SEC, FDA, news, jobs, zoominfo are all "providers" that contribute signals
- Signals are classified by source_type: public_url (sayable) vs vendor_data (guidance only)

Usage:
    from company_intel import CompanyIntelService

    service = CompanyIntelService()
    intel = service.get_company_intel(
        company_name="Acme Pharmaceuticals",
        primary_account_id="001ABC123456789"
    )
"""

from .company_intel_service import CompanyIntelService
from .company_intel_cache import CompanyIntelCache
from .models import (
    CompanySignal,
    CompanyAliases,
    ProviderStatus,
    CompanyIntelResult,
)

__all__ = [
    'CompanyIntelService',
    'CompanyIntelCache',
    'CompanySignal',
    'CompanyAliases',
    'ProviderStatus',
    'CompanyIntelResult',
]
