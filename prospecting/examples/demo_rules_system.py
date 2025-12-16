#!/usr/bin/env python3
"""
Demo script for Phase 1 rules system

Shows how to load and use rules configuration.
"""

import sys
from pathlib import Path

# Add src to path (go up one level from examples/ to find src/)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rules_loader import (
    load_rules,
    get_persona_patterns,
    get_constraints,
    get_signal_rules
)


def print_section(title: str):
    """Print section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def demo_basic_loading():
    """Demo basic configuration loading"""
    print_section("BASIC LOADING")

    # Load Tier A config
    rules_a = load_rules(tier="A")
    print(f"\nLoaded Tier A config")
    print(f"  Active tier: {rules_a['active_tier']['tier']}")
    print(f"  Min signals: {rules_a['active_tier']['min_signals']}")
    print(f"  Description: {rules_a['active_tier']['description']}")

    # Load Tier B config
    rules_b = load_rules(tier="B")
    print(f"\nLoaded Tier B config")
    print(f"  Active tier: {rules_b['active_tier']['tier']}")
    print(f"  Min signals: {rules_b['active_tier']['min_signals']}")
    print(f"  Description: {rules_b['active_tier']['description']}")


def demo_personas():
    """Demo persona patterns"""
    print_section("PERSONA PATTERNS")

    rules = load_rules(tier="A")
    patterns = get_persona_patterns(rules)

    print("\nAvailable personas:")
    for persona, pattern_list in patterns.items():
        print(f"\n  {persona.upper()}: ({len(pattern_list)} patterns)")
        print(f"    Sample patterns: {pattern_list[:3]}")


def demo_angles():
    """Demo messaging angles"""
    print_section("MESSAGING ANGLES")

    rules = load_rules(tier="A")
    angles = rules["angles"]

    print("\nAvailable angles:")
    for angle_key, angle_data in angles.items():
        print(f"\n  {angle_key}:")
        print(f"    Name: {angle_data['name']}")
        print(f"    Description: {angle_data['description']}")
        print(f"    Personas: {', '.join(angle_data['personas'])}")
        print(f"    Pain areas: {', '.join(angle_data['pain_areas'])}")


def demo_offers():
    """Demo CTA offers"""
    print_section("OFFERS / CTAs")

    rules = load_rules(tier="A")
    offers = rules["offers"]

    print("\nAvailable offers:")
    for offer_key, offer_data in offers.items():
        print(f"\n  {offer_key}:")
        print(f"    Deliverable: {offer_data['deliverable']}")
        print(f"    Pain areas: {', '.join(offer_data['pain_areas'])}")
        print(f"    Text: {offer_data['text'][:80]}...")


def demo_constraints():
    """Demo writing constraints"""
    print_section("WRITING CONSTRAINTS")

    rules = load_rules(tier="A")
    constraints = get_constraints(rules)

    print("\nConstraint settings:")
    print(f"  Word count: {constraints['word_count_min']}-{constraints['word_count_max']}")
    print(f"  Sentence count: {constraints['sentence_count_min']}-{constraints['sentence_count_max']}")
    print(f"  Subject max words: {constraints['subject_word_max']}")
    print(f"  No meeting ask: {constraints['no_meeting_ask']}")
    print(f"  No product pitch: {constraints['no_product_pitch']}")
    print(f"\n  Banned phrases ({len(constraints['banned_phrases'])} total):")
    for phrase in constraints['banned_phrases'][:5]:
        print(f"    - '{phrase}'")
    print(f"    ... and {len(constraints['banned_phrases']) - 5} more")


def demo_signal_rules():
    """Demo signal detection rules"""
    print_section("SIGNAL DETECTION RULES")

    rules = load_rules(tier="A")
    signal_rules = get_signal_rules(rules)

    print("\nScope types:")
    for scope_type in signal_rules['scope_types']:
        print(f"  - {scope_type}")

    print("\nRecency thresholds (days):")
    for scope_type, days in signal_rules['recency_thresholds'].items():
        print(f"  - {scope_type}: {days} days")


def demo_subjects():
    """Demo subject lines"""
    print_section("SUBJECT LINES")

    rules = load_rules(tier="A")
    subjects = rules["subjects"]

    print("\nSubject line options by pain area:")
    for pain_area, subject_list in list(subjects.items())[:4]:  # Show first 4
        print(f"\n  {pain_area}:")
        for subject in subject_list:
            print(f"    - {subject}")


def demo_tier_differences():
    """Demo tier A vs B differences"""
    print_section("TIER A vs TIER B COMPARISON")

    rules_a = load_rules(tier="A")
    rules_b = load_rules(tier="B")

    print("\n  Tier A:")
    print(f"    Min signals: {rules_a['active_tier']['min_signals']}")
    print(f"    Description: {rules_a['active_tier']['description']}")

    print("\n  Tier B:")
    print(f"    Min signals: {rules_b['active_tier']['min_signals']}")
    print(f"    Description: {rules_b['active_tier']['description']}")

    print("\n  Key difference:")
    print(f"    Tier A requires {rules_a['active_tier']['min_signals']} qualifying signals")
    print(f"    Tier B requires {rules_b['active_tier']['min_signals']} qualifying signals")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("  PHASE 1 RULES SYSTEM DEMO")
    print("=" * 60)

    try:
        demo_basic_loading()
        demo_personas()
        demo_angles()
        demo_offers()
        demo_constraints()
        demo_signal_rules()
        demo_subjects()
        demo_tier_differences()

        print("\n" + "=" * 60)
        print("  Demo completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
