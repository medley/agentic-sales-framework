"""
Example usage of relevance_engine.py

This demonstrates how to use the relevance engine in the hybrid prospect system.
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from relevance_engine import build_prospect_brief


def main():
    """Demonstrate relevance engine with example data."""

    # Example rules configuration (normally loaded from YAML by rules_loader)
    rules_config = {
        'personas': {
            'quality': {
                'patterns': ['VP Quality', 'Director Quality', 'QA Director']
            },
            'operations': {
                'patterns': ['VP Operations', 'Director Operations']
            }
        },
        'angles': {
            'regulatory_pressure': {
                'personas': ['quality'],
                'industries': ['pharma', 'biotech'],
                'signal_types': ['regulatory_climate', 'regulatory_deadline'],
                'pain_text': 'QA teams are pushed to shorten CAPA cycle time, but manual handoffs keep approvals slow.',
                'question': 'How are you measuring deviation cycle time today?',
                'subjects': ['CAPA backlog', 'Deviation cycle time']
            }
        },
        'offers': {
            'checklist_capa': {
                'personas': ['quality'],
                'compatible_angles': ['regulatory_pressure'],
                'deliverable': 'checklist',
                'cta_text': 'I can send a 1-page checklist QA leaders use to find time sinks. Want it?',
                'subjects': ['CAPA checklist']
            }
        },
        'constraints': {
            'word_count_min': 50,
            'word_count_max': 100,
            'sentence_count_min': 3,
            'sentence_count_max': 4,
            'subject_word_max': 4,
            'subject_style': 'lowercase',
            'banned_phrases': ['circle back', 'synergies', 'touch base']
        },
        'tiering': {
            'A': {
                'min_signals': 3,
                'word_count_min': 50,
                'word_count_max': 100,
                'sentence_count_min': 3,
                'sentence_count_max': 4,
                'must_end_with_question': True,
                'no_meeting_ask': True,
                'no_product_pitch': True
            }
        }
    }

    # Example research data (from orchestrator)
    research_data = {
        'perplexity': {
            'company_info': {
                'name': 'Acme Pharma',
                'industry': 'Pharmaceutical Manufacturing'
            },
            'recent_news': [
                {
                    'headline': 'Acme Pharma expands manufacturing facility in Boston',
                    'url': 'https://example.com/acme-expansion',
                    'date': '2025-11-15'
                },
                {
                    'headline': 'FDA approves Acme drug for rare disease treatment',
                    'url': 'https://example.com/fda-approval',
                    'date': '2025-10-20'
                }
            ]
        },
        'webfetch': [
            {
                'fact': 'FDA increased inspection frequency by 23% in 2024',
                'url': 'https://fda.gov/inspection-stats',
                'type': 'regulatory_climate',
                'scope': 'industry_wide',
                'date': '2025-09-01'
            }
        ]
    }

    # Example context (from synthesizer)
    context = {
        'contact': {
            'name': 'Jane Smith',
            'title': 'VP Quality',
            'email': 'jane.smith@acmepharma.com'
        },
        'company': {
            'name': 'Acme Pharma',
            'industry': 'Pharmaceutical Manufacturing'
        },
        'triggers': [
            {
                'text': 'FDA increased inspection frequency by 23% in 2024',
                'type': 'regulatory_climate',
                'source_url': 'https://fda.gov/inspection-stats',
                'date': '2025-09-01'
            },
            {
                'text': 'New QMSR requirements take effect February 2, 2026',
                'type': 'regulatory_deadline',
                'source_url': 'https://fda.gov/qmsr',
                'date': '2024-12-01'
            }
        ]
    }

    print("=" * 80)
    print("RELEVANCE ENGINE EXAMPLE")
    print("=" * 80)
    print()

    # Build prospect brief
    print("Building prospect brief for Jane Smith, VP Quality at Acme Pharma...")
    print()

    prospect_brief = build_prospect_brief(
        research_data=research_data,
        context=context,
        tier='A',
        rules_config=rules_config
    )

    # Display results
    print("PROSPECT BRIEF:")
    print("-" * 80)
    print(f"Status: {prospect_brief['status']}")
    print(f"Persona: {prospect_brief['persona']}")
    print(f"Industry: {prospect_brief['industry']}")
    print()

    if prospect_brief['status'] == 'ready':
        print(f"Verified Signals: {len(prospect_brief['verified_signals'])}")
        print()

        print("SIGNALS:")
        for signal in prospect_brief['verified_signals']:
            print(f"  [{signal['id']}] {signal['claim']}")
            print(f"    Source: {signal['source_url']}")
            print(f"    Scope: {signal['scope']}, Recency: {signal['recency_days']} days")
            print()

        print(f"Angle: {prospect_brief['angle_id']}")
        print(f"Offer: {prospect_brief['offer_id']}")
        print(f"Hook: {prospect_brief['chosen_hook_id']}")
        print()

        print("EMAIL PLAN:")
        print("-" * 80)
        email_plan = prospect_brief['email_plan']
        print(f"Sentence 1: {email_plan['sentence_1_draft']}")
        print(f"Sentence 2: {email_plan['sentence_2_draft']}")
        print(f"Sentence 3: {email_plan['sentence_3_draft']}")
        print(f"Sentence 4: {email_plan['sentence_4_draft']}")
        print()
        print(f"Subject candidates: {', '.join(email_plan['subject_candidates'])}")
        print()

        print("CONSTRAINTS:")
        print("-" * 80)
        constraints = prospect_brief['constraints']
        print(f"Word count: {constraints['word_count_min']}-{constraints['word_count_max']}")
        print(f"Sentence count: {constraints['sentence_count_min']}-{constraints['sentence_count_max']}")
        print(f"Must end with question: {constraints['must_end_with_question']}")
        print(f"No meeting ask: {constraints['no_meeting_ask']}")
        print(f"No product pitch: {constraints['no_product_pitch']}")

    else:
        print(f"Reason: {prospect_brief['reason']}")
        print(f"Signals found: {prospect_brief['signals_found']}/{prospect_brief['signals_required']}")
        print()
        print("Recommendations:")
        for rec in prospect_brief['recommendations']:
            print(f"  - {rec}")

    print()
    print("=" * 80)
    print("Next step: Pass prospect_brief to llm_renderer to generate email variants")
    print("=" * 80)


if __name__ == '__main__':
    main()
