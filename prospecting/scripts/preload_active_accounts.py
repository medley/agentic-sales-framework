#!/usr/bin/env python3
"""
Preload Active Accounts - Pre-cache company data for fast prospecting

Scans active account folders and pre-caches company intel, so that when
you run /prospect for contacts at these companies, research is instant.

Usage:
    python3 preload_active_accounts.py
    python3 preload_active_accounts.py --force-refresh
    python3 preload_active_accounts.py --company "Acme Corp"
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
import argparse

# Load API keys
load_dotenv()

# Import modules
sys.path.append(os.path.dirname(__file__))
from src.perplexity_client import PerplexityClient
from src.webfetch_client import WebFetchClient
from src.company_cache import CompanyCache
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Configure this to point to your active accounts directory
# Override with ACTIVE_ACCOUNTS_DIR environment variable
ACTIVE_ACCOUNTS_DIR = Path(
    os.environ.get('ACTIVE_ACCOUNTS_DIR', os.path.expanduser("~/prospecting/accounts"))
)


def get_active_companies() -> List[str]:
    """
    Get list of active company names from folder structure.

    Returns:
        List of company names
    """
    if not ACTIVE_ACCOUNTS_DIR.exists():
        logger.error(f"Active accounts directory not found: {ACTIVE_ACCOUNTS_DIR}")
        return []

    companies = []
    for item in ACTIVE_ACCOUNTS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('00-'):
            companies.append(item.name)

    logger.info(f"Found {len(companies)} active companies")
    return companies


def research_company_parallel(
    company_name: str,
    perplexity: PerplexityClient,
    webfetch: WebFetchClient
) -> Dict[str, Any]:
    """
    Research a single company using parallel sources.

    Args:
        company_name: Company name
        perplexity: Perplexity client
        webfetch: WebFetch client

    Returns:
        {
            'perplexity': {...},
            'webfetch': {...},
            'sources_succeeded': [str]
        }
    """
    results = {
        'perplexity': None,
        'webfetch': None,
        'sources_succeeded': []
    }

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(perplexity.research_company, company_name, None): 'perplexity',
            executor.submit(webfetch.research_company, company_name): 'webfetch'
        }

        for future in as_completed(futures, timeout=20):
            source = futures[future]
            try:
                result = future.result(timeout=2)
                if result:
                    results[source] = result
                    results['sources_succeeded'].append(source)
                    logger.info(f"✓ {company_name}: {source} succeeded")
            except Exception as e:
                logger.warning(f"✗ {company_name}: {source} failed - {str(e)}")

    return results


def preload_companies(
    companies: List[str],
    force_refresh: bool = False
):
    """
    Preload company data into cache.

    Args:
        companies: List of company names to preload
        force_refresh: Skip cache and re-research everything
    """
    # Initialize clients
    perplexity = PerplexityClient(api_key=os.getenv('PERPLEXITY_API_KEY'))
    webfetch = WebFetchClient()
    company_cache = CompanyCache()

    # Cleanup expired entries first
    expired = company_cache.cleanup_expired()
    if expired > 0:
        logger.info(f"Cleaned up {expired} expired cache entries")

    # Filter out already cached companies (unless force_refresh)
    if not force_refresh:
        companies_to_research = []
        for company in companies:
            cached = company_cache.get_company(company)
            if cached:
                logger.info(f"⚡ {company}: already cached (skipping)")
            else:
                companies_to_research.append(company)
    else:
        companies_to_research = companies
        logger.info("Force refresh enabled - re-researching all companies")

    if not companies_to_research:
        logger.info("All companies already cached!")
        return

    logger.info(f"\nPreloading {len(companies_to_research)} companies...")
    logger.info("=" * 60)

    # Research companies sequentially (to respect API rate limits)
    for i, company in enumerate(companies_to_research, 1):
        logger.info(f"\n[{i}/{len(companies_to_research)}] Researching {company}...")

        try:
            # Research in parallel
            results = research_company_parallel(company, perplexity, webfetch)

            # Cache if at least one source succeeded
            if results['sources_succeeded']:
                company_data = {
                    'perplexity': results['perplexity'],
                    'webfetch': results['webfetch']
                }
                company_cache.set_company(
                    company,
                    company_data,
                    results['sources_succeeded']
                )
                logger.info(f"✓ {company}: Cached (sources: {', '.join(results['sources_succeeded'])})")
            else:
                logger.warning(f"✗ {company}: All sources failed - not cached")

        except Exception as e:
            logger.error(f"✗ {company}: Unexpected error - {str(e)}")

    logger.info("\n" + "=" * 60)
    logger.info("Preload complete!")

    # Show cache stats
    stats = company_cache.get_stats()
    logger.info(f"\nCache Stats:")
    logger.info(f"  Active companies: {stats['active_companies']}")
    logger.info(f"  Total companies: {stats['total_companies']}")
    logger.info(f"  Cache size: {stats['cache_size_mb']} MB")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Preload active accounts into company cache for faster prospecting"
    )
    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='Re-research even if already cached'
    )
    parser.add_argument(
        '--company',
        type=str,
        help='Preload specific company only'
    )

    args = parser.parse_args()

    # Get companies to preload
    if args.company:
        companies = [args.company]
        logger.info(f"Preloading single company: {args.company}")
    else:
        companies = get_active_companies()

    if not companies:
        logger.error("No companies to preload")
        sys.exit(1)

    # Run preload
    preload_companies(companies, force_refresh=args.force_refresh)


if __name__ == "__main__":
    main()
