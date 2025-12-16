#!/usr/bin/env python3
"""
Prepare Email Context - Runs deterministic hybrid system logic

This script runs all deterministic processing (YAML rules, signal extraction, angle filtering)
and outputs a JSON structure for Claude Code to complete the email rendering.

Usage:
    python3 scripts/prepare_email_context.py /tmp/prospect_research_raw.json

Output:
    JSON to stdout with email_context ready for Claude Code rendering
"""

import sys
import json
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rules_loader import load_rules
from src.relevance_engine import build_prospect_brief, RelevanceEngine
from src.email_assembler import EmailAssembler
from src.llm_angle_scorer import _build_scoring_prompt
from src.path_resolver import get_email_context_path, get_prospect_status_path
from src.product_resolver import ProductResolver
from src.context_quality import ContextQualityBuilder, render_context_quality_header

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_research_data(filepath: str) -> dict:
    """Load research data from JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load research data: {e}")
        raise


def prepare_email_context(
    research_filepath: str,
    tier: str = "A",
    force_automation: bool = False
) -> dict:
    """
    Run all deterministic hybrid system processing.

    REGULATORY PERSONA HANDLING:
    - If persona is 'regulatory' and automation_allowed=False in config,
      returns status='requires_manual_review' instead of generating email
    - Use force_automation=True to override this safety check

    Args:
        research_filepath: Path to prospect_research_raw.json
        tier: "A" (3+ signals) or "B" (2+ signals)
        force_automation: Override automation_allowed check for regulatory persona

    Returns:
        Email context dict ready for Claude Code rendering
    """
    logger.info(f"Preparing email context (tier={tier}, force_automation={force_automation})")

    # Step 1: Load research data
    research_data = load_research_data(research_filepath)
    logger.info("Loaded research data")

    # Step 2: Load rules configuration
    rules_config = load_rules(experiment=None, tier=tier)
    logger.info(f"Loaded rules config for tier {tier}")

    # Step 2.5: Get persona with diagnostics for regulatory safety check
    engine = RelevanceEngine(rules_config)
    contact = research_data.get('contact', {})
    title = contact.get('title', '')
    persona_diagnostics = engine.detect_persona_with_diagnostics(title)

    # REGULATORY PERSONA SAFETY CHECK
    # If persona is regulatory and automation_allowed=False, require manual review
    if not force_automation and not persona_diagnostics.get('automation_allowed', True):
        logger.warning(
            f"Persona '{persona_diagnostics['selected_persona']}' requires manual review "
            f"(automation_allowed=False). Use force_automation=True to override."
        )
        return {
            'status': 'requires_manual_review',
            'reason': f"Persona '{persona_diagnostics['selected_persona']}' has automation_allowed=False",
            'persona': persona_diagnostics['selected_persona'],
            'persona_diagnostics': persona_diagnostics,
            'contact': {
                'first_name': contact.get('first_name'),
                'last_name': contact.get('last_name'),
                'title': contact.get('title'),
                'email': contact.get('email'),
                'company': contact.get('company')
            },
            'suggested_action': 'Review contact manually or use --force-automation flag',
            'default_confidence_cap': persona_diagnostics.get('default_confidence_cap', 'medium')
        }

    # Step 3: Build prospect brief (deterministic signal extraction + angle selection)
    prospect_brief = build_prospect_brief(
        research_data=research_data,
        context=research_data,  # Context is same as research_data in this case
        tier=tier,
        rules_config=rules_config
    )

    logger.info(f"Prospect brief status: {prospect_brief['status']}")
    logger.info(f"Confidence tier: {prospect_brief.get('confidence_tier', 'unknown')}")

    # Step 3.5: Build canonical context quality
    context_quality_builder = ContextQualityBuilder()
    context_quality = context_quality_builder.build(
        research_data=research_data,
        prospect_brief=prospect_brief,
        company_intel=research_data.get('company_intel'),
        persona_result=persona_diagnostics
    )
    logger.info("Built canonical context quality")

    # Log context quality header for visibility
    cq_header = render_context_quality_header(context_quality)
    for line in cq_header.split('\n'):
        logger.info(f"[CQ] {line}")

    # Initialize product resolver for display names
    product_resolver = ProductResolver(rules_config)

    # Build primary product motion with display name
    primary_product_motion = None
    if persona_diagnostics.get('eligible_products'):
        primary_product_id = persona_diagnostics['eligible_products'][0]
        primary_product_motion = {
            'product_id': primary_product_id,
            'display_name': product_resolver.get_display_name(primary_product_id)
        }

    # Build secondary products list with display names
    secondary_products = []
    for prod_id in persona_diagnostics.get('secondary_products', []):
        secondary_products.append({
            'product_id': prod_id,
            'display_name': product_resolver.get_display_name(prod_id)
        })

    # Build forbidden products list with display names
    forbidden_products = []
    for prod_id in persona_diagnostics.get('forbidden_products', []):
        forbidden_products.append({
            'product_id': prod_id,
            'display_name': product_resolver.get_display_name(prod_id)
        })

    # Write confidence summary to path_resolver location (with visibility fields)
    confidence_summary = {
        'confidence_tier': prospect_brief.get('confidence_tier'),
        'confidence_note': prospect_brief.get('confidence_note'),
        'signal_count': prospect_brief.get('signal_count', 0),
        'persona': prospect_brief.get('persona'),
        'industry': prospect_brief.get('industry'),
        # NEW: Output visibility fields
        'primary_product_motion': primary_product_motion,
        'secondary_products': secondary_products,
        'forbidden_products': forbidden_products,
        'ambiguity_detected': persona_diagnostics.get('ambiguity_detected', False),
        'automation_allowed': persona_diagnostics.get('automation_allowed', True),
        'safe_angle_only': persona_diagnostics.get('safe_angle_only', False),
        'sources_available': {
            'perplexity': bool(research_data.get('perplexity')),
            'webfetch': bool(research_data.get('webfetch')),
            'contact': bool(research_data.get('contact'))
        }
    }

    status_file = get_prospect_status_path()
    with open(status_file, 'w') as f:
        json.dump(confidence_summary, f, indent=2)

    logger.info(f"Wrote confidence summary to {status_file}")

    # Step 4: Build email plan (draft sentences using rules)
    assembler = EmailAssembler()
    email_plan = assembler.build_email_plan(
        prospect_brief=prospect_brief,
        rules_config=rules_config
    )

    logger.info("Built email plan with draft sentences")

    # Step 5: Prepare angle scoring prompt (if multiple candidates)
    candidate_angles = prospect_brief.get('candidate_angles', [])
    angle_scoring_needed = len(candidate_angles) > 1

    angle_scoring_prompt = None
    if angle_scoring_needed:
        try:
            from src.llm_angle_scorer import _build_scoring_prompt
            angle_scoring_prompt = _build_scoring_prompt(
                persona=prospect_brief['persona'],
                company_name=prospect_brief['company_name'],
                verified_signals=prospect_brief['verified_signals'],
                candidate_angles=candidate_angles
            )
            logger.info(f"Prepared angle scoring prompt for {len(candidate_angles)} candidates")
        except Exception as e:
            logger.warning(f"Could not build angle scoring prompt: {e}")

    # Step 6: Build rendering prompt template (will be filled in by Claude Code)
    # We provide the structure but Claude Code will do the actual rendering
    rendering_prompt_template = {
        'draft_sentences': [
            email_plan.get('sentence_1_draft'),
            email_plan.get('sentence_2_draft'),
            email_plan.get('sentence_3_draft'),
            email_plan.get('sentence_4_draft')
        ],
        'subject_candidates': email_plan.get('subject_candidates', []),
        'verified_signals': prospect_brief['verified_signals'],
        'constraints': prospect_brief['constraints']
    }
    logger.info("Prepared rendering prompt template")

    # Step 7: Build output context (with visibility fields)
    context = {
        'status': 'ready_for_rendering',
        'tier': tier,
        'context_quality': context_quality,  # Canonical context quality schema
        'prospect_brief': {
            'persona': prospect_brief['persona'],
            'company_name': prospect_brief['company_name'],
            'industry': prospect_brief.get('industry'),
            'verified_signals': prospect_brief['verified_signals'],
            'angle_id': prospect_brief.get('angle_id'),
            'offer_id': prospect_brief.get('offer_id'),
            'constraints': prospect_brief['constraints'],
            'confidence_tier': prospect_brief.get('confidence_tier')  # For backward compat
        },
        # NEW: Output visibility fields at top level for easy access
        'persona_diagnostics': {
            'persona': persona_diagnostics.get('selected_persona'),
            'primary_product_motion': primary_product_motion,
            'secondary_products': secondary_products,
            'forbidden_products': forbidden_products,
            'ambiguity_detected': persona_diagnostics.get('ambiguity_detected', False),
            'ambiguity_note': persona_diagnostics.get('ambiguity_note'),
            'safe_angle_only': persona_diagnostics.get('safe_angle_only', False),
            'confidence_downgrade': persona_diagnostics.get('confidence_downgrade', False),
            'automation_allowed': persona_diagnostics.get('automation_allowed', True),
            'default_confidence_cap': persona_diagnostics.get('default_confidence_cap', 'high'),
            'matched_rules': persona_diagnostics.get('matched_rules', []),
            'fallback_applied': persona_diagnostics.get('fallback_applied', False)
        },
        'email_plan': {
            'sentence_1_draft': email_plan.get('sentence_1_draft'),
            'sentence_2_draft': email_plan.get('sentence_2_draft'),
            'sentence_3_draft': email_plan.get('sentence_3_draft'),
            'sentence_4_draft': email_plan.get('sentence_4_draft'),
            'subject_candidates': email_plan.get('subject_candidates', [])
        },
        'candidate_angles': candidate_angles if angle_scoring_needed else [],
        'angle_scoring_prompt': angle_scoring_prompt,
        'angle_scoring_needed': angle_scoring_needed,
        'rendering_prompt_template': rendering_prompt_template,
        'contact': {
            'first_name': research_data.get('contact', {}).get('first_name'),
            'last_name': research_data.get('contact', {}).get('last_name'),
            'title': research_data.get('contact', {}).get('title'),
            'email': research_data.get('contact', {}).get('email'),
            'phone': research_data.get('contact', {}).get('phone')
        }
    }

    logger.info("Email context prepared successfully")
    return context


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 prepare_email_context.py <research_json_path> [tier] [--force-automation]", file=sys.stderr)
        sys.exit(1)

    research_filepath = sys.argv[1]
    tier = "A"
    force_automation = False

    # Parse optional arguments
    for arg in sys.argv[2:]:
        if arg == '--force-automation':
            force_automation = True
        elif arg in ('A', 'B'):
            tier = arg

    try:
        context = prepare_email_context(
            research_filepath,
            tier=tier,
            force_automation=force_automation
        )

        # Write email_context.json to path_resolver location
        email_context_path = get_email_context_path()
        with open(email_context_path, 'w') as f:
            json.dump(context, f, indent=2)
        logger.info(f"Wrote email context to {email_context_path}")

        # Also output JSON to stdout for visibility
        print(json.dumps(context, indent=2))

    except Exception as e:
        logger.error(f"Failed to prepare email context: {e}", exc_info=True)
        error_output = {
            'status': 'error',
            'error': str(e)
        }
        print(json.dumps(error_output, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
