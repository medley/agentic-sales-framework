#!/usr/bin/env python3
"""
Interactive contact selection by role

Searches ZoomInfo for contacts matching a role at a company,
displays them in a numbered list, and lets the user select one.

Usage:
    python3 scripts/select_contact_by_role.py "quality director" "Ultradent Products"
    python3 scripts/select_contact_by_role.py "VP Quality" "Boston Scientific"

Output:
    Displays interactive list, user selects contact, outputs JSON to stdout:
    {"first_name": "Casey", "last_name": "Hughes", "title": "Director, Quality Engineering"}
"""

import sys
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.zoominfo_client import ZoomInfoClient
from src.zoominfo_jwt_manager import ZoomInfoJWTManager
from src.research_orchestrator import ResearchOrchestrator
from src.perplexity_client import PerplexityClient
from src.caching import ContactCache


def display_contacts(contacts: list, company_name: str, role: str):
    """
    Display formatted list of contacts.

    Args:
        contacts: List of contact dicts from ZoomInfo
        company_name: Company name
        role: Role searched for
    """
    # Send display to stderr so stdout is clean for JSON
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"Found {len(contacts)} contacts for '{role}' at {company_name}:", file=sys.stderr)
    print(f"{'='*70}\n", file=sys.stderr)

    for i, contact in enumerate(contacts, 1):
        print(f"[{i}] {contact['first_name']} {contact['last_name']}", file=sys.stderr)
        print(f"    Title: {contact['title']}", file=sys.stderr)

        # Management level (if available)
        mgmt_level = contact.get('management_level', [])
        if mgmt_level:
            level_str = ', '.join(mgmt_level)
            print(f"    Level: {level_str}", file=sys.stderr)

        # Job function (if available)
        job_func = contact.get('job_function', [])
        if job_func and isinstance(job_func, list):
            func_names = [f['name'] for f in job_func if isinstance(f, dict) and 'name' in f]
            if func_names:
                print(f"    Function: {', '.join(func_names)}", file=sys.stderr)

        # Location (if available)
        location = contact.get('location', 'N/A')
        if location and location != 'N/A':
            print(f"    Location: {location}", file=sys.stderr)

        print(file=sys.stderr)

    print(f"{'='*70}\n", file=sys.stderr)


def get_user_selection(contacts: list) -> int:
    """
    Prompt user to select a contact.

    Args:
        contacts: List of contacts

    Returns:
        Selected contact index (0-based)
    """
    max_index = len(contacts)

    while True:
        try:
            # Prompt to stderr, read from stdin
            print(f"Select contact [1-{max_index}] or [q]uit: ", file=sys.stderr, end='', flush=True)
            choice = input().strip().lower()

            if choice == 'q' or choice == 'quit':
                print("\n✗ Selection cancelled\n", file=sys.stderr)
                sys.exit(0)

            index = int(choice)
            if 1 <= index <= max_index:
                return index - 1  # Convert to 0-based index
            else:
                print(f"✗ Please enter a number between 1 and {max_index}\n", file=sys.stderr)

        except ValueError:
            print(f"✗ Invalid input. Please enter a number between 1 and {max_index} or 'q' to quit\n", file=sys.stderr)
        except KeyboardInterrupt:
            print("\n\n✗ Selection cancelled\n", file=sys.stderr)
            sys.exit(0)


def main():
    """Main function"""
    # Parse arguments
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/select_contact_by_role.py 'role' 'company'", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  python3 scripts/select_contact_by_role.py 'quality director' 'Ultradent Products'", file=sys.stderr)
        print("  python3 scripts/select_contact_by_role.py 'VP Quality' 'Boston Scientific'", file=sys.stderr)
        sys.exit(1)

    role = sys.argv[1]
    company = sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    # Initialize clients
    try:
        jwt_manager = ZoomInfoJWTManager()
        zoominfo = ZoomInfoClient(jwt_manager)
        perplexity = PerplexityClient(api_key=os.getenv('PERPLEXITY_API_KEY'))
        cache = ContactCache()

        orchestrator = ResearchOrchestrator(zoominfo, perplexity, cache)
    except Exception as e:
        print(f"✗ Error initializing clients: {e}", file=sys.stderr)
        sys.exit(1)

    # Search for contacts by role
    try:
        results = orchestrator.list_contacts_by_role(
            role=role,
            company=company,
            limit=limit
        )

        contacts = results.get('contacts', [])

        if not contacts:
            errors = results.get('errors', [])
            if errors:
                print(f"\n✗ Error: {errors[0]}", file=sys.stderr)
            else:
                print(f"\n✗ No contacts found for '{role}' at {company}", file=sys.stderr)
            print("\nPossible reasons:", file=sys.stderr)
            print("  - No one with that role at the company", file=sys.stderr)
            print("  - Company name doesn't match ZoomInfo records (try variations)", file=sys.stderr)
            print("  - Role keywords too specific (try broader terms like 'quality' or 'director')", file=sys.stderr)
            print("", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error searching for contacts: {e}", file=sys.stderr)
        sys.exit(1)

    # Display contacts and get user selection
    display_contacts(contacts, company, role)
    selected_index = get_user_selection(contacts)
    selected_contact = contacts[selected_index]

    # Output selected contact as JSON to stdout (captured by prospect.md)
    output = {
        'first_name': selected_contact['first_name'],
        'last_name': selected_contact['last_name'],
        'title': selected_contact['title'],
        'contact_id': selected_contact['contact_id']
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
