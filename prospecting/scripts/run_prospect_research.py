#!/usr/bin/env python3
"""
Run prospect research for a contact

Usage:
    python3 scripts/run_prospect_research.py "John Smith" "Acme Corp"
    python3 scripts/run_prospect_research.py "Jane Doe" "Example Pharma" --force-refresh
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.zoominfo_client import ZoomInfoClient
from src.perplexity_client import PerplexityClient
from src.caching import ContactCache
from src.research_orchestrator import ResearchOrchestrator
from src.context_synthesizer import ContextSynthesizer, format_research_brief
from src.path_resolver import get_research_raw_path, get_prospect_status_path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print colored header."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")

def print_section(text):
    """Print section header."""
    print(f"\n{GREEN}{text}{RESET}")
    print("-" * 40)

def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")

def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")

def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")

def main():
    """Main research workflow."""
    parser = argparse.ArgumentParser(
        description='Research prospect and generate email context'
    )
    parser.add_argument('name', help='Contact name (e.g., "John Smith")')
    parser.add_argument('company', help='Company name (e.g., "Acme Corp")')
    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='Skip cache and force fresh research'
    )
    parser.add_argument(
        '--save-brief',
        help='Save research brief to file (provide path)'
    )

    args = parser.parse_args()

    print_header(f"Prospect Research: {args.name} at {args.company}")

    # Load API keys
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        print_error(f".env file not found at {env_path}")
        print_warning("Copy .env.example to .env and add your API keys")
        return 1

    load_dotenv(env_path)

    perplexity_key = os.getenv('PERPLEXITY_API_KEY')

    if not perplexity_key or perplexity_key == 'pplx-your_perplexity_api_key_here':
        print_error("PERPLEXITY_API_KEY not configured in .env")
        return 1

    # Initialize clients
    print_section("Initializing API clients")
    try:
        from src.zoominfo_jwt_manager import ZoomInfoJWTManager

        jwt_manager = ZoomInfoJWTManager()
        zoominfo = ZoomInfoClient(jwt_manager)
        print_success("ZoomInfo client ready")

        perplexity = PerplexityClient(api_key=perplexity_key)
        print_success("Perplexity client ready")

        cache = ContactCache()
        print_success("Cache system ready")

    except Exception as e:
        print_error(f"Failed to initialize clients: {e}")
        return 1

    # Run research
    print_section(f"Researching {args.name} at {args.company}")
    orchestrator = ResearchOrchestrator(zoominfo, perplexity, cache)

    try:
        research = orchestrator.research_prospect(
            args.name,
            args.company,
            force_refresh=args.force_refresh
        )

        if research.get('cached'):
            print_warning("Using cached data (90-day TTL)")
        else:
            print_success("Fresh research completed")

        sources = research.get('sources_succeeded', [])
        print_success(f"Data sources: {', '.join(sources)}")

        if research.get('errors'):
            print_warning("Some errors occurred:")
            for error in research['errors']:
                print(f"  - {error}")

    except Exception as e:
        print_error(f"Research failed: {e}")
        return 1

    # Synthesize context
    print_section("Synthesizing email context")
    try:
        synthesizer = ContextSynthesizer()
        context = synthesizer.synthesize(research)

        quality = context['synthesis_quality']
        confidence = quality['confidence']

        if confidence == 'high':
            print_success(f"Synthesis quality: HIGH confidence")
        elif confidence == 'medium':
            print_warning(f"Synthesis quality: MEDIUM confidence")
        else:
            print_error(f"Synthesis quality: LOW confidence")

        print(f"  - Contact found: {'Yes' if quality['contact_found'] else 'No'}")
        print(f"  - Company data: {'Yes' if quality['company_data_available'] else 'No'}")
        print(f"  - Triggers found: {quality['triggers_found']}")

    except Exception as e:
        print_error(f"Context synthesis failed: {e}")
        return 1

    # Display results
    print_section("Contact Profile")
    contact = context['contact_profile']
    print(f"Name: {contact['first_name']} {contact['last_name']}")
    print(f"Title: {contact.get('title') or 'Unknown'}")
    print(f"Email: {contact.get('email') or 'Not found'}")
    print(f"Phone: {contact.get('phone') or 'Not found'}")
    print(f"Company: {contact.get('company') or args.company}")

    print_section("Company Profile")
    company = context['company_profile']
    print(f"Industry: {company.get('industry') or 'Unknown'}")
    print(f"Size: {company.get('size') or 'Unknown'}")
    print(f"Revenue: {company.get('revenue') or 'Unknown'}")
    if company.get('tech_stack'):
        print(f"Tech Stack: {', '.join(company['tech_stack'][:5])}")
    print(f"Manual Processes: {'Yes' if company.get('manual_processes_detected') else 'No'}")

    print_section("Likely Pain Points")
    for pain in company['likely_pains'][:5]:
        print(f"  • {pain}")

    if context['triggers']:
        print_section("Triggers")
        for trigger in context['triggers']:
            print(f"  • [{trigger['type'].upper()}] {trigger['description']}")

    print_section("Email Context")
    email_ctx = context['email_context']
    if email_ctx.get('specific_reference'):
        print(f"Opening Reference: {email_ctx['specific_reference']}")
    if email_ctx.get('primary_pain'):
        print(f"Primary Pain: {email_ctx['primary_pain']}")
    if email_ctx.get('personalization_hooks'):
        print("Personalization Hooks:")
        for hook in email_ctx['personalization_hooks']:
            print(f"  • {hook}")

    # Save research brief if requested
    if args.save_brief:
        print_section("Saving Research Brief")
        try:
            brief = format_research_brief(context)
            save_path = Path(args.save_brief)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_text(brief)
            print_success(f"Saved to: {save_path}")
        except Exception as e:
            print_error(f"Failed to save brief: {e}")

    # Persist structured outputs for downstream scripts (via path_resolver)
    raw_path = get_research_raw_path()
    context_path = raw_path.parent / "prospect_context.json"

    try:
        raw_path.write_text(json.dumps(research, indent=2))
        print_success(f"Saved raw research to: {raw_path}")
    except Exception as e:
        print_error(f"Failed to save raw research JSON: {e}")

    try:
        context_path.write_text(json.dumps(context, indent=2))
        print_success(f"Saved synthesized context to: {context_path}")
    except Exception as e:
        print_error(f"Failed to save context JSON: {e}")

    # Output JSON for programmatic use (context)
    print_section("JSON Output - Synthesized Context")
    print(json.dumps(context, indent=2))

    print_header("Research Complete")
    print_success("Use the context above to draft a first-touch email")
    print("\nNext steps:")
    print("1. Draft email using the sales rep's voice (75-125 words, binary question)")
    print("2. Validate with quality linter")
    print("3. Save to account folder deliverables/_drafts/")

    return 0

if __name__ == '__main__':
    sys.exit(main())
