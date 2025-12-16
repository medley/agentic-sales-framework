#!/usr/bin/env python3
"""
Test script for ZoomInfo API client

Usage:
    python scripts/test_zoominfo.py "John Smith" "Acme Corporation"

Requirements:
    - Set ZOOMINFO_API_KEY environment variable
    - Or edit API_KEY variable below
"""

import sys
import os
import logging

# Add parent directory to path to import from src/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.zoominfo_client import (
    ZoomInfoClient,
    ZoomInfoAPIError,
    ZoomInfoRateLimitError,
    ZoomInfoAuthenticationError
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_contact_search(client, name, company):
    """Test contact search functionality"""
    print(f"\n{'='*60}")
    print(f"Testing Contact Search")
    print(f"{'='*60}")
    print(f"Name: {name}")
    print(f"Company: {company}")
    print()

    try:
        contact = client.search_contact(name, company)

        if contact:
            print("✓ Contact found!")
            print(f"  Contact ID: {contact['contact_id']}")
            print(f"  Name: {contact['first_name']} {contact['last_name']}")
            print(f"  Title: {contact['title']}")
            print(f"  Email: {contact['email']}")
            print(f"  Phone: {contact['phone']}")
            print(f"  Company ID: {contact['company_id']}")
            return contact
        else:
            print("✗ No contact found")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def test_company_enrichment(client, company_id):
    """Test company enrichment functionality"""
    print(f"\n{'='*60}")
    print(f"Testing Company Enrichment")
    print(f"{'='*60}")
    print(f"Company ID: {company_id}")
    print()

    try:
        company = client.enrich_company(company_id)

        print("✓ Company data enriched!")
        print(f"  Revenue: {company['revenue']}")
        print(f"  Employees: {company['employee_count']:,}")
        print(f"  Industry: {company['industry']}")
        print(f"  Technologies: {len(company['tech_stack'])} found")

        if company['tech_stack']:
            print(f"    - {', '.join(company['tech_stack'][:5])}")
            if len(company['tech_stack']) > 5:
                print(f"    - ... and {len(company['tech_stack']) - 5} more")

        print(f"  Intent Signals: {len(company['intent_signals'])} found")
        if company['intent_signals']:
            print(f"    - {', '.join(company['intent_signals'][:5])}")
            if len(company['intent_signals']) > 5:
                print(f"    - ... and {len(company['intent_signals']) - 5} more")

        return company

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def main():
    """Main test function"""
    # Get API key from environment or hardcode for testing
    api_key = os.environ.get('ZOOMINFO_API_KEY')

    if not api_key:
        print("ERROR: ZOOMINFO_API_KEY environment variable not set")
        print("\nUsage:")
        print("  export ZOOMINFO_API_KEY='your_key_here'")
        print("  python scripts/test_zoominfo.py 'John Smith' 'Acme Corp'")
        print("\nOr edit this script to hardcode API_KEY for testing")
        sys.exit(1)

    # Get contact name and company from command line
    if len(sys.argv) < 3:
        print("Usage: python scripts/test_zoominfo.py 'Name' 'Company'")
        print("\nExample:")
        print("  python scripts/test_zoominfo.py 'John Smith' 'Acme Corporation'")
        sys.exit(1)

    name = sys.argv[1]
    company_name = sys.argv[2]

    print(f"\n{'#'*60}")
    print(f"# ZoomInfo API Client Test")
    print(f"{'#'*60}")

    # Initialize client using context manager
    with ZoomInfoClient(api_key=api_key) as client:
        # Test 1: Contact search
        contact = test_contact_search(client, name, company_name)

        # Test 2: Company enrichment (if contact found)
        if contact and contact.get('company_id'):
            test_company_enrichment(client, contact['company_id'])
        else:
            print("\nSkipping company enrichment (no company ID)")

    print(f"\n{'='*60}")
    print("Tests completed!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except ZoomInfoRateLimitError as e:
        print(f"\n✗ RATE LIMIT ERROR: {e}")
        print("Wait before making more requests")
        sys.exit(1)
    except ZoomInfoAuthenticationError as e:
        print(f"\n✗ AUTHENTICATION ERROR: {e}")
        print("Check your API key")
        sys.exit(1)
    except ZoomInfoAPIError as e:
        print(f"\n✗ API ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
