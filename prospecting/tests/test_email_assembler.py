#!/usr/bin/env python3
"""
Test Email Assembler - Verify intelligent component matching

Shows how the system:
1. Detects persona from title
2. Matches pains to persona + industry
3. Selects appropriate CTA
4. Assembles personalized email

Usage:
    python3 test_email_assembler.py
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))
from src.email_assembler import EmailAssembler
from src.email_components import EmailComponentLibrary


def test_persona_detection():
    """Test persona detection from various titles."""
    print("\n" + "=" * 60)
    print("TEST 1: Persona Detection")
    print("=" * 60)

    library = EmailComponentLibrary()

    test_titles = [
        "VP Quality",
        "Director of Operations",
        "Chief Information Officer",
        "VP Regulatory Affairs",
        "Head of Manufacturing",
        "Quality Director"
    ]

    for title in test_titles:
        persona = library.detect_persona(title)
        print(f"  {title:30} → {persona or 'unknown'}")


def test_pain_matching():
    """Test pain matching for different personas."""
    print("\n" + "=" * 60)
    print("TEST 2: Pain Matching")
    print("=" * 60)

    library = EmailComponentLibrary()

    test_cases = [
        ("quality", "pharma"),
        ("operations", "pharma"),
        ("it", "medical_device"),
        ("regulatory", "medical_device")
    ]

    for persona, industry in test_cases:
        pains = library.get_pains(persona, industry, limit=2)
        print(f"\n  Persona: {persona}, Industry: {industry}")
        for pain in pains:
            print(f"    - {pain['key']}")


def test_trigger_detection():
    """Test regulatory trigger detection."""
    print("\n" + "=" * 60)
    print("TEST 3: Trigger Detection")
    print("=" * 60)

    library = EmailComponentLibrary()

    for industry in ["pharma", "biotech", "medical_device"]:
        triggers = library.get_triggers(industry)
        print(f"\n  Industry: {industry}")
        for trigger in triggers:
            print(f"    - {trigger['key']}: {trigger['text'][:60]}...")


def test_full_email_generation():
    """Test full email generation with sample data."""
    print("\n" + "=" * 60)
    print("TEST 4: Full Email Generation")
    print("=" * 60)

    assembler = EmailAssembler()

    # Test Case 1: Quality leader at pharma company
    print("\n  Case 1: VP Quality at Pharma")
    print("  " + "-" * 56)

    research_pharma = {
        'contact': {
            'title': 'VP Quality',
            'company': 'Acme Pharma'
        },
        'company': {
            'industry': 'Pharmaceutical Manufacturing'
        },
        'perplexity': {},
        'webfetch': {}
    }

    email1 = assembler.generate_email(research_pharma, "Sarah")

    print(f"\n  Subject: {email1['subject']}")
    print(f"\n  Body ({email1['stats']['word_count']} words, {email1['stats']['sentence_count']} sentences):")
    print("  " + email1['body'].replace('\n', '\n  '))
    print(f"\n  Persona: {email1['stats']['persona_detected']}")
    print(f"  Pain: {email1['stats']['pain_matched']}")
    print(f"  Trigger used: {email1['stats']['trigger_used']}")

    # Test Case 2: Ops leader at med device company
    print("\n\n  Case 2: Director Operations at Medical Device")
    print("  " + "-" * 56)

    research_medtech = {
        'contact': {
            'title': 'Director of Operations',
            'company': 'Varex Imaging'
        },
        'company': {},
        'webfetch': {
            'industries': ['medical device', 'industrial']
        }
    }

    email2 = assembler.generate_email(research_medtech, "Chris")

    print(f"\n  Subject: {email2['subject']}")
    print(f"\n  Body ({email2['stats']['word_count']} words, {email2['stats']['sentence_count']} sentences):")
    print("  " + email2['body'].replace('\n', '\n  '))
    print(f"\n  Persona: {email2['stats']['persona_detected']}")
    print(f"  Pain: {email2['stats']['pain_matched']}")
    print(f"  Trigger used: {email2['stats']['trigger_used']}")

    # Test Case 3: CIO at biotech
    print("\n\n  Case 3: CIO at Biotech")
    print("  " + "-" * 56)

    research_biotech = {
        'contact': {
            'title': 'Chief Information Officer',
            'company': 'BioTech Innovations'
        },
        'company': {
            'industry': 'Biotechnology'
        }
    }

    email3 = assembler.generate_email(research_biotech, "Michael")

    print(f"\n  Subject: {email3['subject']}")
    print(f"\n  Body ({email3['stats']['word_count']} words, {email3['stats']['sentence_count']} sentences):")
    print("  " + email3['body'].replace('\n', '\n  '))
    print(f"\n  Persona: {email3['stats']['persona_detected']}")
    print(f"  Pain: {email3['stats']['pain_matched']}")
    print(f"  Trigger used: {email3['stats']['trigger_used']}")


def test_manual_override():
    """Test manual override functionality."""
    print("\n" + "=" * 60)
    print("TEST 5: Manual Override")
    print("=" * 60)

    assembler = EmailAssembler()

    research = {
        'contact': {
            'title': 'VP Quality',  # Would normally select quality pains
            'company': 'Test Company'
        },
        'company': {
            'industry': 'Pharmaceutical'
        }
    }

    # Override to use operations pain instead
    email = assembler.generate_email_with_override(
        research,
        "John",
        persona="operations",
        pain_area="batch_release"
    )

    print(f"\n  Overridden to: persona=operations, pain_area=batch_release")
    print(f"\n  Subject: {email['subject']}")
    print(f"\n  Body:")
    print("  " + email['body'].replace('\n', '\n  '))


def test_list_options():
    """Test listing available options."""
    print("\n" + "=" * 60)
    print("TEST 6: Available Options")
    print("=" * 60)

    assembler = EmailAssembler()

    options = assembler.list_available_options()

    print(f"\n  Available Personas:")
    for persona in options['personas']:
        print(f"    - {persona}")

    print(f"\n  Available Industries:")
    for industry in options['industries']:
        print(f"    - {industry}")

    print(f"\n  Available Pain Areas:")
    for pain_area in options['pain_areas']:
        print(f"    - {pain_area}")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("EMAIL ASSEMBLER TEST SUITE")
    print("=" * 60)

    test_persona_detection()
    test_pain_matching()
    test_trigger_detection()
    test_full_email_generation()
    test_manual_override()
    test_list_options()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
