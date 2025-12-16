#!/usr/bin/env python3
"""
Speed Test - Compare old vs new prospecting performance

Tests:
1. Cold research (no cache) - should be ~5-10s with parallel execution
2. Warm research (company cached) - should be <2s
3. Multiple contacts at same company - should be instant after first

Usage:
    python3 test_speed.py
"""

import sys
import os
import time
from dotenv import load_dotenv

# Load API keys
load_dotenv()

# Import modules
sys.path.append(os.path.dirname(__file__))
from src.zoominfo_client import ZoomInfoClient
from src.zoominfo_jwt_manager import ZoomInfoJWTManager
from src.perplexity_client import PerplexityClient
from src.webfetch_client import WebFetchClient
from src.caching import ContactCache
from src.company_cache import CompanyCache
from src.research_orchestrator import ResearchOrchestrator


def test_cold_research():
    """Test: Cold research with no cache."""
    print("\n" + "=" * 60)
    print("TEST 1: Cold Research (No Cache)")
    print("=" * 60)

    # Initialize clients
    jwt_manager = ZoomInfoJWTManager()
    zoominfo = ZoomInfoClient(jwt_manager)
    perplexity = PerplexityClient(api_key=os.getenv('PERPLEXITY_API_KEY'))
    webfetch = WebFetchClient()
    contact_cache = ContactCache()
    company_cache = CompanyCache()

    orchestrator = ResearchOrchestrator(
        zoominfo,
        perplexity,
        contact_cache,
        company_cache,
        webfetch
    )

    # Clear cache for test company
    company_cache.invalidate_company("Varex Imaging")
    contact_cache.invalidate("Chris Price", "Varex Imaging")

    print("\nResearching Chris Price at Varex Imaging (no cache)...")
    start = time.time()

    try:
        results = orchestrator.research_prospect("Chris Price", "Varex Imaging")
        elapsed = time.time() - start

        print(f"\n✓ Research complete in {elapsed:.2f}s")
        print(f"  Sources: {', '.join(results['sources_succeeded'])}")
        print(f"  Company cached: {results.get('company_cached', False)}")

        if elapsed < 10:
            print(f"  ⚡ FAST! (target: <10s)")
        else:
            print(f"  ⚠️  Slower than expected (target: <10s)")

        return elapsed

    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return None


def test_warm_research():
    """Test: Warm research with company cache."""
    print("\n" + "=" * 60)
    print("TEST 2: Warm Research (Company Cached)")
    print("=" * 60)

    # Initialize clients
    jwt_manager = ZoomInfoJWTManager()
    zoominfo = ZoomInfoClient(jwt_manager)
    perplexity = PerplexityClient(api_key=os.getenv('PERPLEXITY_API_KEY'))
    webfetch = WebFetchClient()
    contact_cache = ContactCache()
    company_cache = CompanyCache()

    orchestrator = ResearchOrchestrator(
        zoominfo,
        perplexity,
        contact_cache,
        company_cache,
        webfetch
    )

    # Clear contact cache but NOT company cache
    contact_cache.invalidate("John Doe", "Varex Imaging")

    print("\nResearching John Doe at Varex Imaging (company cached)...")
    start = time.time()

    try:
        results = orchestrator.research_prospect("John Doe", "Varex Imaging")
        elapsed = time.time() - start

        print(f"\n✓ Research complete in {elapsed:.2f}s")
        print(f"  Sources: {', '.join(results['sources_succeeded'])}")
        print(f"  Company cached: {results.get('company_cached', False)}")

        if elapsed < 2:
            print(f"  ⚡ FAST! (target: <2s)")
        else:
            print(f"  ⚠️  Slower than expected (target: <2s)")

        return elapsed

    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return None


def test_multiple_contacts():
    """Test: Multiple contacts at same company."""
    print("\n" + "=" * 60)
    print("TEST 3: Multiple Contacts (Same Company)")
    print("=" * 60)

    # Initialize clients
    jwt_manager = ZoomInfoJWTManager()
    zoominfo = ZoomInfoClient(jwt_manager)
    perplexity = PerplexityClient(api_key=os.getenv('PERPLEXITY_API_KEY'))
    webfetch = WebFetchClient()
    contact_cache = ContactCache()
    company_cache = CompanyCache()

    orchestrator = ResearchOrchestrator(
        zoominfo,
        perplexity,
        contact_cache,
        company_cache,
        webfetch
    )

    # Clear all caches
    company_cache.invalidate_company("Example Electronics")
    for name in ["Contact 1", "Contact 2", "Contact 3"]:
        contact_cache.invalidate(name, "Example Electronics")

    contacts = ["Contact 1", "Contact 2", "Contact 3"]
    times = []

    for i, contact in enumerate(contacts, 1):
        print(f"\n[{i}/3] Researching {contact} at Example Electronics...")
        start = time.time()

        try:
            results = orchestrator.research_prospect(contact, "Example Electronics")
            elapsed = time.time() - start
            times.append(elapsed)

            print(f"  ✓ Complete in {elapsed:.2f}s (company_cached: {results.get('company_cached', False)})")

        except Exception as e:
            print(f"  ✗ Failed: {str(e)}")
            times.append(None)

    # Analyze results
    print(f"\n{'─' * 60}")
    print("Results:")
    if all(t is not None for t in times):
        print(f"  Contact 1: {times[0]:.2f}s (cold)")
        print(f"  Contact 2: {times[1]:.2f}s (warm)")
        print(f"  Contact 3: {times[2]:.2f}s (warm)")

        if times[1] < 2 and times[2] < 2:
            print(f"\n  ⚡ Company caching working! Contacts 2-3 were instant.")
        else:
            print(f"\n  ⚠️  Company caching may not be working properly")

    return times


def main():
    """Run all speed tests."""
    print("\n" + "=" * 60)
    print("PROSPECTING SPEED TESTS")
    print("=" * 60)
    print("\nTesting new parallel research implementation:")
    print("  ✓ Parallel WebFetch + Perplexity + ZoomInfo")
    print("  ✓ Separate company cache")
    print("  ✓ Cached company data for multi-contact speed\n")

    # Run tests
    cold_time = test_cold_research()
    time.sleep(2)  # Brief pause between tests

    warm_time = test_warm_research()
    time.sleep(2)

    multi_times = test_multiple_contacts()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if cold_time:
        improvement = ((15 - cold_time) / 15) * 100 if cold_time < 15 else 0
        print(f"\n✓ Cold research: {cold_time:.2f}s (was ~15s) → {improvement:.0f}% faster")

    if warm_time:
        print(f"✓ Warm research: {warm_time:.2f}s (instant when company cached)")

    if multi_times and all(t is not None for t in multi_times):
        avg_warm = (multi_times[1] + multi_times[2]) / 2
        print(f"✓ Multi-contact: {avg_warm:.2f}s avg for contacts 2-3 (company cached)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
