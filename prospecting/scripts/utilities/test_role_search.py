#!/usr/bin/env python3
"""
Test script for ZoomInfo role-based contact search

Usage:
    python3 scripts/test_role_search.py "quality director" "Ultradent Products"
    python3 scripts/test_role_search.py "VP Quality" "Boston Scientific"

Tests the search_contacts_by_role() method to verify:
- API endpoint works correctly
- Returns list of contacts
- Includes management level, job function, location data
- Handles errors gracefully
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.zoominfo_client import ZoomInfoClient
from src.zoominfo_jwt_manager import ZoomInfoJWTManager


def test_role_search(role: str, company: str, limit: int = 5):
    """
    Test role-based contact search.

    Args:
        role: Job title keywords (e.g., "quality director")
        company: Company name
        limit: Max contacts to return
    """
    print(f"\n{'='*70}")
    print(f"TESTING ZOOMINFO ROLE-BASED CONTACT SEARCH")
    print(f"{'='*70}\n")
    print(f"Role: {role}")
    print(f"Company: {company}")
    print(f"Limit: {limit}\n")

    # Initialize ZoomInfo client
    try:
        jwt_manager = ZoomInfoJWTManager()
        client = ZoomInfoClient(jwt_manager)
        print("✓ ZoomInfo client initialized\n")
    except Exception as e:
        print(f"✗ Failed to initialize ZoomInfo client: {e}")
        return False

    # Search for contacts
    try:
        contacts = client.search_contacts_by_role(
            role_keywords=role,
            company_name=company,
            limit=limit
        )

        if not contacts:
            print(f"✗ No contacts found for '{role}' at {company}\n")
            print("This could mean:")
            print("  - No one with that role at the company")
            print("  - Company name doesn't match ZoomInfo records")
            print("  - Role keywords too specific\n")
            return False

        # Display results
        print(f"✓ Found {len(contacts)} contacts:\n")
        print(f"{'-'*70}\n")

        for i, contact in enumerate(contacts, 1):
            print(f"[{i}] {contact['first_name']} {contact['last_name']}")
            print(f"    Title: {contact['title']}")

            # Management level
            mgmt_level = contact.get('management_level', [])
            if mgmt_level:
                level_str = ', '.join(mgmt_level)
                print(f"    Level: {level_str}")
            else:
                print(f"    Level: N/A")

            # Job function
            job_func = contact.get('job_function', [])
            if job_func:
                func_names = [f['name'] for f in job_func if isinstance(f, dict) and 'name' in f]
                if func_names:
                    print(f"    Function: {', '.join(func_names)}")

            # Location
            location = contact.get('location', 'N/A')
            print(f"    Location: {location}")

            # IDs (for debugging)
            print(f"    Contact ID: {contact['contact_id']}")
            print(f"    Company ID: {contact['company_id']}")
            print()

        print(f"{'-'*70}\n")
        print("✓ TEST PASSED - Role search working correctly\n")
        return True

    except Exception as e:
        print(f"✗ Error during contact search: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    # Parse arguments
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/test_role_search.py 'role' 'company'")
        print("\nExamples:")
        print("  python3 scripts/test_role_search.py 'quality director' 'Ultradent Products'")
        print("  python3 scripts/test_role_search.py 'VP Quality' 'Boston Scientific'")
        print("  python3 scripts/test_role_search.py 'director quality' 'Genentech'")
        sys.exit(1)

    role = sys.argv[1]
    company = sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    # Run test
    success = test_role_search(role, company, limit)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
