"""
Research Orchestrator - Coordinates parallel prospect research

Runs ZoomInfo and Perplexity research in parallel, handles errors gracefully,
and caches results for 90 days to minimize API costs.

Usage:
    from research_orchestrator import ResearchOrchestrator
    from zoominfo_client import ZoomInfoClient
    from perplexity_client import PerplexityClient
    from caching import ProspectCache

    orchestrator = ResearchOrchestrator(zoominfo, perplexity, cache)
    results = orchestrator.research_prospect("John Smith", "Acme Corp")
"""

import logging
from typing import Dict, Optional, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json

from .zoominfo_client import (
    ZoomInfoClient,
    ZoomInfoRateLimitError,
    ZoomInfoAuthenticationError,
    ZoomInfoAPIError
)
from .perplexity_client import PerplexityClient
from .caching import ContactCache
from .company_cache import CompanyCache
from .webfetch_client import WebFetchClient

# Optional import for company intel (may not be initialized)
try:
    from .company_intel import CompanyIntelService
except ImportError:
    CompanyIntelService = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResearchOrchestrator:
    """
    Orchestrates parallel prospect research across multiple data sources.

    Coordinates ZoomInfo (contact/company data) and Perplexity (pain insights)
    research in parallel with proper error handling and caching.
    """

    def __init__(
        self,
        zoominfo_client: ZoomInfoClient,
        perplexity_client: PerplexityClient,
        cache: ContactCache,
        company_cache: Optional[CompanyCache] = None,
        webfetch_client: Optional[WebFetchClient] = None,
        company_intel_service: Optional['CompanyIntelService'] = None,
        timeout_seconds: int = 10
    ):
        """
        Initialize research orchestrator.

        Args:
            zoominfo_client: ZoomInfo API client
            perplexity_client: Perplexity API client
            cache: Contact cache for 90-day TTL
            company_cache: Company-level cache (faster multi-contact research)
            webfetch_client: Website data extraction client (parallel with APIs)
            company_intel_service: Company intelligence service for SEC/FDA/news
            timeout_seconds: Max time per research source
        """
        self.zoominfo = zoominfo_client
        self.perplexity = perplexity_client
        self.cache = cache
        self.company_cache = company_cache or CompanyCache()
        self.webfetch = webfetch_client or WebFetchClient()
        self.company_intel = company_intel_service
        self.timeout = timeout_seconds

    def research_prospect(
        self,
        name: str,
        company: str,
        force_refresh: bool = False,
        refresh_company_intel: bool = False,
        primary_account_id: str = None
    ) -> Dict[str, Any]:
        """
        Research a prospect using parallel data sources.

        Workflow:
        1. Fetch company intel (SEC, FDA, news) if available
        2. Check cache first (unless force_refresh=True)
        3. Run parallel research:
           - ZoomInfo: Contact search + company enrichment
           - Perplexity: Company research + pain insights
        4. Combine results with error handling
        5. Cache results (90-day TTL)

        Args:
            name: Contact name (e.g., "John Smith")
            company: Company name (e.g., "Acme Corp")
            force_refresh: Skip cache and force new research
            refresh_company_intel: Force refresh company intel (SEC, FDA, etc.)
            primary_account_id: Salesforce Primary Account ID (for company intel)

        Returns:
            {
                'contact': {contact_id, first_name, last_name, title, email, phone, company_id},
                'company': {revenue, employee_count, industry, tech_stack, intent_signals},
                'perplexity': {company_news, business_challenges, role_pains, initiatives},
                'company_intel': {signals, sources, ...} or None,
                'errors': [list of error messages],
                'cached': bool,
                'timestamp': ISO timestamp,
                'sources_succeeded': [list of successful sources]
            }

        Raises:
            Exception: If ALL research sources fail
        """
        # Fetch company intel first (if service available)
        company_intel_result = None
        if self.company_intel:
            try:
                logger.info(f"Fetching company intel for {company}")
                company_intel_result = self.company_intel.get_company_intel(
                    company_name=company,
                    primary_account_id=primary_account_id,
                    refresh=refresh_company_intel
                )
                if company_intel_result:
                    logger.info(
                        f"Company intel fetched: {company_intel_result.total_signals} signals"
                    )
            except Exception as e:
                logger.warning(f"Company intel fetch failed (continuing): {e}")

        # Check cache first
        if not force_refresh:
            cached = self._check_cache(name, company)
            if cached:
                logger.info(f"Cache hit for {name} at {company}")
                cached['cached'] = True
                cached['company_name'] = company  # Ensure company_name is always set
                # Add company_intel to cached result if we have it
                if company_intel_result:
                    cached['company_intel'] = company_intel_result.to_dict()
                return cached

        logger.info(f"Starting research for {name} at {company}")

        # Check company cache first (fast path for multiple contacts at same company)
        cached_company_data = self.company_cache.get_company(company)

        # Run parallel research
        results = {
            'contact': None,
            'company': None,
            'company_name': company,  # Explicit company name (never None)
            'perplexity': None,
            'webfetch': None,
            'company_intel': company_intel_result.to_dict() if company_intel_result else None,
            'errors': [],
            'cached': False,
            'company_cached': cached_company_data is not None,
            'timestamp': datetime.utcnow().isoformat(),
            'sources_succeeded': []
        }

        # Add company_intel to sources if available
        if company_intel_result and company_intel_result.total_signals.get('public_url', 0) > 0:
            results['sources_succeeded'].append('company_intel')

        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all research tasks in parallel
            futures = {
                executor.submit(self._research_zoominfo_contact, name, company): 'zoominfo_contact'
            }

            # Only run company research if not cached
            if not cached_company_data:
                futures[executor.submit(self._research_perplexity, company, None)] = 'perplexity'
                futures[executor.submit(self._research_webfetch, company)] = 'webfetch'
            else:
                logger.info(f"Using cached company data for {company}")
                results['perplexity'] = cached_company_data.get('perplexity')
                results['webfetch'] = cached_company_data.get('webfetch')
                results['sources_succeeded'].extend(['perplexity', 'webfetch'])

            # Collect results as they complete
            for future in as_completed(futures, timeout=self.timeout + 5):
                source = futures[future]
                try:
                    result = future.result(timeout=2)

                    if source == 'zoominfo_contact':
                        results['contact'] = result.get('contact')
                        results['company'] = result.get('company')
                        if result.get('contact') or result.get('company'):
                            results['sources_succeeded'].append('zoominfo')
                        if result.get('errors'):
                            results['errors'].extend(result['errors'])

                    elif source == 'perplexity':
                        results['perplexity'] = result
                        if result:
                            results['sources_succeeded'].append('perplexity')

                    elif source == 'webfetch':
                        results['webfetch'] = result
                        if result:
                            results['sources_succeeded'].append('webfetch')

                except Exception as e:
                    error_msg = f"{source} failed: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)

        # Check if at least one source succeeded
        if not results['sources_succeeded']:
            error = f"All research sources failed for {name} at {company}"
            logger.error(error)
            raise Exception(error)

        # Cache successful results
        self._cache_results(name, company, results)

        # Cache company data separately for faster multi-contact research
        if not cached_company_data and (results.get('perplexity') or results.get('webfetch')):
            company_data = {
                'perplexity': results.get('perplexity'),
                'webfetch': results.get('webfetch'),
                'company': results.get('company')
            }
            sources = [s for s in ['perplexity', 'webfetch'] if s in results['sources_succeeded']]
            self.company_cache.set_company(company, company_data, sources)

        logger.info(
            f"Research complete for {name} at {company}. "
            f"Sources: {', '.join(results['sources_succeeded'])} "
            f"(company_cached: {results['company_cached']})"
        )

        return results

    def list_contacts_by_role(
        self,
        role: str,
        company: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Get list of contacts by role WITHOUT full enrichment.

        This is a lightweight method for role-based contact discovery.
        Only searches ZoomInfo for contacts - does NOT run Perplexity/WebFetch.
        Company research happens later when user selects a specific contact.

        Args:
            role: Job title keywords (e.g., "quality director", "vp operations")
            company: Company name
            limit: Max contacts to return (default: 5)

        Returns:
            {
                'contacts': [
                    {contact_id, first_name, last_name, title, management_level,
                     job_function, location, company_id, company_name},
                    ...
                ],
                'company_name': str,
                'company_id': int or None,
                'count': int,
                'errors': []
            }

        Raises:
            Exception: If ZoomInfo search fails
        """
        logger.info(f"Listing contacts by role '{role}' at {company}")

        results = {
            'contacts': [],
            'company_name': company,
            'company_id': None,
            'count': 0,
            'errors': []
        }

        try:
            # Search ZoomInfo for contacts by role
            contacts = self.zoominfo.search_contacts_by_role(
                role_keywords=role,
                company_name=company,
                limit=limit
            )

            if contacts:
                results['contacts'] = contacts
                results['count'] = len(contacts)

                # Extract company_id from first contact
                if contacts[0].get('company_id'):
                    results['company_id'] = contacts[0]['company_id']

                logger.info(f"Found {len(contacts)} contacts with role '{role}' at {company}")
            else:
                error_msg = f"No contacts found for role '{role}' at {company}"
                logger.warning(error_msg)
                results['errors'].append(error_msg)

        except ZoomInfoRateLimitError as e:
            error_msg = f"ZoomInfo rate limit hit: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            raise Exception(error_msg)

        except ZoomInfoAuthenticationError as e:
            error_msg = f"ZoomInfo authentication failed: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            raise Exception(error_msg)

        except ZoomInfoAPIError as e:
            error_msg = f"ZoomInfo API error: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            raise Exception(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error listing contacts: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            raise Exception(error_msg)

        return results

    def _research_zoominfo_contact(
        self,
        name: str,
        company: str
    ) -> Dict[str, Any]:
        """
        Research contact via ZoomInfo (contact search + company enrichment).

        Returns:
            {
                'contact': {...} or None,
                'company': {...} or None,
                'errors': [list of errors]
            }
        """
        result = {
            'contact': None,
            'company': None,
            'errors': []
        }

        try:
            # Search for contact
            logger.info(f"Searching ZoomInfo for {name} at {company}")
            contact = self.zoominfo.search_contact(name, company)

            if contact:
                result['contact'] = contact
                logger.info(f"Found contact: {contact.get('title')} at {company}")

                # Enrich company data if we have company_id
                if contact.get('company_id'):
                    try:
                        logger.info(f"Enriching company data for {company}")
                        company_data = self.zoominfo.enrich_company(contact['company_id'])
                        result['company'] = company_data
                        logger.info(f"Company enrichment complete: {company}")
                    except Exception as e:
                        error_msg = f"Company enrichment failed: {str(e)}"
                        logger.warning(error_msg)
                        result['errors'].append(error_msg)
            else:
                error_msg = f"Contact not found: {name} at {company}"
                logger.warning(error_msg)
                result['errors'].append(error_msg)

        except ZoomInfoRateLimitError as e:
            error_msg = f"ZoomInfo rate limit hit: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        except ZoomInfoAuthenticationError as e:
            error_msg = f"ZoomInfo authentication failed: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        except ZoomInfoAPIError as e:
            error_msg = f"ZoomInfo API error: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        except Exception as e:
            error_msg = f"Unexpected ZoomInfo error: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        return result

    def _research_perplexity(
        self,
        company: str,
        role: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Research company via Perplexity AI.

        Returns:
            {
                'company_news': [...],
                'business_challenges': [...],
                'role_specific_pains': [...],
                'recent_initiatives': [...]
            }
            or None if research fails
        """
        try:
            logger.info(f"Researching {company} via Perplexity")
            research = self.perplexity.research_company(company, role)

            if research:
                logger.info(f"Perplexity research complete for {company}")
                return research
            else:
                logger.warning(f"Perplexity returned no results for {company}")
                return None

        except Exception as e:
            error_msg = f"Perplexity research failed: {str(e)}"
            logger.error(error_msg)
            return None

    def _research_webfetch(
        self,
        company: str
    ) -> Optional[Dict[str, Any]]:
        """
        Research company via website data extraction (WebFetch).

        Returns:
            {
                'company_description': str,
                'industries': [str],
                'products': [str],
                'recent_news': [str],
                'regulatory_keywords': [str]
            }
            or None if fetch fails
        """
        try:
            logger.info(f"Fetching website for {company}")
            data = self.webfetch.research_company(company)

            if data:
                logger.info(f"WebFetch complete for {company}")
                return data
            else:
                logger.warning(f"WebFetch returned no data for {company}")
                return None

        except Exception as e:
            error_msg = f"WebFetch failed: {str(e)}"
            logger.error(error_msg)
            return None

    def _check_cache(
        self,
        name: str,
        company: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check if prospect research is cached.

        Args:
            name: Contact name
            company: Company name

        Returns:
            Cached research dict or None
        """
        cache_key = f"prospect_research_{name.lower()}_{company.lower()}"

        try:
            cached_data = self.cache.get_profile(name, company)
            if cached_data:
                logger.info(f"Cache hit for {name} at {company}")
                return cached_data
        except Exception as e:
            logger.warning(f"Cache read failed: {str(e)}")

        return None

    def _cache_results(
        self,
        name: str,
        company: str,
        results: Dict[str, Any]
    ) -> None:
        """
        Cache research results (90-day TTL).

        Args:
            name: Contact name
            company: Company name
            results: Research results dict
        """
        try:
            self.cache.set_profile(name, company, results)
            logger.info(f"Cached results for {name} at {company}")
        except Exception as e:
            logger.warning(f"Cache write failed: {str(e)}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.

        Returns:
            {
                'total_requests': int,
                'cache_hits': int,
                'cache_misses': int,
                'hit_rate': float
            }
        """
        return self.cache.get_stats()

    def clear_cache_for_prospect(
        self,
        name: str,
        company: str
    ) -> bool:
        """
        Clear cached data for a specific prospect.

        Args:
            name: Contact name
            company: Company name

        Returns:
            True if cache cleared successfully
        """
        try:
            # Clear from ProspectCache
            cache_key = f"prospect_research_{name.lower()}_{company.lower()}"
            self.cache.invalidate(name, company)
            logger.info(f"Cleared cache for {name} at {company}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            return False


class ProspectResearchError(Exception):
    """Base exception for prospect research errors."""
    pass


class NoDataSourcesAvailableError(ProspectResearchError):
    """Raised when all research sources fail."""
    pass
