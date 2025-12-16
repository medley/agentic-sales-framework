#!/usr/bin/env python3
"""
Email Validator CLI - Deterministic validation for prospect emails

This script provides a CLI interface to the validators module.
All validation results are deterministic and come from this script,
NOT from Claude's judgment.

Usage:
    python3 scripts/validate_email.py <subject> <body> [--signals signal_ids] [--context path]

Output:
    JSON with validation results including:
    - status: PASSED, FAILED, or SKIPPED
    - checks: individual check results
    - failures: list of specific failures

Example:
    python3 scripts/validate_email.py "capa cycle time" "Email body here..." --signals "signal_001,signal_002"
"""

import sys
import json
import argparse
import logging
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rules_loader import load_rules
from path_resolver import get_email_context_path

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate a prospect email against deterministic rules"
    )
    parser.add_argument("subject", help="Email subject line")
    parser.add_argument("body", help="Email body text")
    parser.add_argument(
        "--signals",
        help="Comma-separated list of used signal IDs",
        default=""
    )
    parser.add_argument(
        "--context",
        help="Path to email_context.json (default: from path_resolver)",
        default=None
    )
    parser.add_argument(
        "--tier",
        help="Tier level (A or B)",
        default="A"
    )
    parser.add_argument(
        "--output",
        help="Output format: json or table",
        default="json"
    )
    return parser.parse_args()


def load_context(context_path: str) -> tuple:
    """
    Load email context from JSON file.

    Returns:
        tuple: (context_dict, context_loaded_bool, error_message)
    """
    try:
        with open(context_path, 'r') as f:
            return json.load(f), True, None
    except FileNotFoundError:
        return {}, False, f"Context file not found: {context_path}"
    except json.JSONDecodeError as e:
        return {}, False, f"Invalid JSON in context file: {e}"


def get_constraints(context: dict, tier: str) -> dict:
    """Extract constraints from context or use defaults."""
    # Try to get from context
    if 'prospect_brief' in context and 'constraints' in context['prospect_brief']:
        return context['prospect_brief']['constraints']

    # Load from rules config
    rules_config = load_rules(tier=tier)
    return rules_config.get('constraints', {
        'word_count_min': 50,
        'word_count_max': 100,
        'sentence_count_min': 3,
        'sentence_count_max': 4,
        'subject_word_max': 4,
        'must_end_with_question': True,
        'no_meeting_ask': True,
        'no_product_pitch': True,
        'banned_phrases': []
    })


def get_cited_signals(context: dict) -> list:
    """Extract cited signals from context."""
    if 'prospect_brief' in context and 'cited_signals' in context['prospect_brief']:
        return context['prospect_brief']['cited_signals']
    # Fallback to verified_signals for backward compatibility
    if 'prospect_brief' in context and 'verified_signals' in context['prospect_brief']:
        return context['prospect_brief']['verified_signals']
    return []


def validate_email(subject: str, body: str, used_signal_ids: list,
                   constraints: dict, cited_signals: list,
                   context_loaded: bool, context_error: str = None) -> dict:
    """
    Run all validation checks and return structured results.

    Returns:
        {
            "status": "PASSED" | "FAILED" | "SKIPPED",
            "context_loaded": bool,
            "context_error": str or None,
            "checks": {
                "word_count": {"passed": bool, "actual": int, "min": int, "max": int},
                "sentence_count": {"passed": bool, "actual": int, "min": int, "max": int},
                "ends_with_question": {"passed": bool},
                "banned_phrases": {"passed": bool, "found": []},
                "no_product_pitch": {"passed": bool, "found": []},
                "subject_length": {"passed": bool, "actual": int, "max": int},
                "signal_integrity": {"status": "PASSED"|"FAILED"|"SKIPPED", ...}
            },
            "failures": ["list of failure messages"]
        }
    """
    results = {
        "status": "PASSED",
        "context_loaded": context_loaded,
        "context_error": context_error,
        "checks": {},
        "failures": []
    }

    # Word count
    word_count = len(body.split())
    word_min = constraints.get('word_count_min', 50)
    word_max = constraints.get('word_count_max', 100)
    word_passed = word_min <= word_count <= word_max
    results["checks"]["word_count"] = {
        "passed": word_passed,
        "actual": word_count,
        "min": word_min,
        "max": word_max
    }
    if not word_passed:
        results["failures"].append(f"Word count {word_count} outside range {word_min}-{word_max}")

    # Sentence count (simple heuristic: count . ! ?)
    sentences = re.split(r'[.!?]+', body)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)
    sentence_min = constraints.get('sentence_count_min', 3)
    sentence_max = constraints.get('sentence_count_max', 4)
    sentence_passed = sentence_min <= sentence_count <= sentence_max
    results["checks"]["sentence_count"] = {
        "passed": sentence_passed,
        "actual": sentence_count,
        "min": sentence_min,
        "max": sentence_max
    }
    if not sentence_passed:
        results["failures"].append(f"Sentence count {sentence_count} outside range {sentence_min}-{sentence_max}")

    # Ends with question
    ends_with_q = body.strip().endswith('?')
    results["checks"]["ends_with_question"] = {
        "passed": ends_with_q
    }
    if not ends_with_q:
        results["failures"].append("Email must end with a question")

    # Banned phrases
    banned_phrases = constraints.get('banned_phrases', [])
    found_banned = [p for p in banned_phrases if p.lower() in body.lower()]
    results["checks"]["banned_phrases"] = {
        "passed": len(found_banned) == 0,
        "found": found_banned
    }
    if found_banned:
        results["failures"].append(f"Found banned phrases: {found_banned}")

    # No product pitch
    pitch_terms = ['product_name', 'qx', 'mx', 'our platform', 'our solution',
                   'our software', 'we offer', 'we provide']
    found_pitch = [t for t in pitch_terms if t.lower() in body.lower()]
    results["checks"]["no_product_pitch"] = {
        "passed": len(found_pitch) == 0,
        "found": found_pitch
    }
    if found_pitch:
        results["failures"].append(f"Found product pitch terms: {found_pitch}")

    # Subject length
    subject_words = len(subject.split())
    subject_max = constraints.get('subject_word_max', 4)
    subject_passed = subject_words <= subject_max
    results["checks"]["subject_length"] = {
        "passed": subject_passed,
        "actual": subject_words,
        "max": subject_max
    }
    if not subject_passed:
        results["failures"].append(f"Subject has {subject_words} words, max is {subject_max}")

    # Signal integrity - FAIL if context not loaded and signals were claimed
    if not context_loaded:
        if used_signal_ids:
            # Signals were claimed but we can't validate them
            results["checks"]["signal_integrity"] = {
                "status": "FAILED",
                "passed": False,
                "reason": "Context not loaded - cannot validate signal IDs",
                "context_error": context_error,
                "claimed_signals": used_signal_ids,
                "valid": 0,
                "total": len(used_signal_ids),
                "invalid": used_signal_ids
            }
            results["failures"].append(f"SIGNAL VALIDATION FAILED: Context not loaded ({context_error})")
        else:
            # No signals claimed, mark as skipped
            results["checks"]["signal_integrity"] = {
                "status": "SKIPPED",
                "passed": True,  # No signals to validate
                "reason": "No signals claimed and context not loaded",
                "context_error": context_error,
                "valid": 0,
                "total": 0,
                "invalid": []
            }
    else:
        # Context loaded - perform full validation
        cited_ids = {s.get('signal_id', s.get('id', '')) for s in cited_signals}
        valid_signals = [sid for sid in used_signal_ids if sid in cited_ids]
        invalid_signals = [sid for sid in used_signal_ids if sid not in cited_ids]
        signal_passed = len(invalid_signals) == 0

        results["checks"]["signal_integrity"] = {
            "status": "PASSED" if signal_passed else "FAILED",
            "passed": signal_passed,
            "valid": len(valid_signals),
            "total": len(used_signal_ids),
            "available_in_context": len(cited_ids),
            "invalid": invalid_signals
        }
        if invalid_signals:
            results["failures"].append(f"Invalid signal IDs (not in cited_signals): {invalid_signals}")

    # Set overall status
    if results["failures"]:
        results["status"] = "FAILED"

    return results


def format_table(results: dict) -> str:
    """Format results as a text table."""
    lines = []
    lines.append("┌─────────────────────────────────────────────────────────────┐")
    lines.append("│ VALIDATION REPORT (from validate_email.py)                  │")
    lines.append("├─────────────────────────────────────────────────────────────┤")

    status = results['status']
    context_loaded = results.get('context_loaded', False)
    context_indicator = "✓" if context_loaded else "✗"

    lines.append(f"│ Status: {status:<52}│")
    lines.append(f"│ Context Loaded: {context_indicator:<43}│")

    if not context_loaded and results.get('context_error'):
        error = results['context_error'][:45] + "..." if len(results.get('context_error', '')) > 45 else results.get('context_error', '')
        lines.append(f"│ Context Error: {error:<44}│")

    lines.append("├─────────────────────────────────────────────────────────────┤")
    lines.append("│ Checks:                                                     │")

    checks = results['checks']

    # Word count
    wc = checks['word_count']
    mark = "✓" if wc['passed'] else "✗"
    lines.append(f"│   Word count:      {wc['actual']} ({wc['min']}-{wc['max']}) {mark:<18}│")

    # Sentence count
    sc = checks['sentence_count']
    mark = "✓" if sc['passed'] else "✗"
    lines.append(f"│   Sentence count:  {sc['actual']} ({sc['min']}-{sc['max']}) {mark:<18}│")

    # Ends with question
    eq = checks['ends_with_question']
    mark = "✓" if eq['passed'] else "✗"
    lines.append(f"│   Ends with \"?\":   {mark:<40}│")

    # Banned phrases
    bp = checks['banned_phrases']
    mark = "✓" if bp['passed'] else "✗"
    lines.append(f"│   No banned phrases: {mark:<38}│")

    # No product pitch
    pp = checks['no_product_pitch']
    mark = "✓" if pp['passed'] else "✗"
    lines.append(f"│   No product pitch: {mark:<39}│")

    # Subject length
    sl = checks['subject_length']
    mark = "✓" if sl['passed'] else "✗"
    lines.append(f"│   Subject length:  {sl['actual']} words (max {sl['max']}) {mark:<16}│")

    # Signal integrity
    si = checks['signal_integrity']
    si_status = si.get('status', 'PASSED' if si['passed'] else 'FAILED')
    if si_status == "SKIPPED":
        mark = "⊘"
        lines.append(f"│   Signal integrity: SKIPPED (no context) {mark:<13}│")
    elif si_status == "FAILED" and not results.get('context_loaded'):
        mark = "✗"
        lines.append(f"│   Signal integrity: FAILED (no context) {mark:<14}│")
    else:
        mark = "✓" if si['passed'] else "✗"
        lines.append(f"│   Signal integrity: {si['valid']}/{si['total']} valid {mark:<21}│")

    lines.append("├─────────────────────────────────────────────────────────────┤")

    if results['failures']:
        lines.append("│ Failures:                                                   │")
        for failure in results['failures']:
            # Truncate long failures
            if len(failure) > 55:
                failure = failure[:52] + "..."
            lines.append(f"│   - {failure:<55}│")
    else:
        lines.append("│ Failures: None                                              │")

    lines.append("└─────────────────────────────────────────────────────────────┘")

    return "\n".join(lines)


def main():
    args = parse_args()

    # Get context path from path_resolver if not specified
    if args.context is None:
        context_path = str(get_email_context_path())
    else:
        context_path = args.context

    # Load context
    context, context_loaded, context_error = load_context(context_path)

    # Get constraints
    constraints = get_constraints(context, args.tier)

    # Get cited signals
    cited_signals = get_cited_signals(context)

    # Parse used signal IDs
    used_signal_ids = []
    if args.signals:
        used_signal_ids = [s.strip() for s in args.signals.split(',') if s.strip()]

    # Run validation
    results = validate_email(
        subject=args.subject,
        body=args.body,
        used_signal_ids=used_signal_ids,
        constraints=constraints,
        cited_signals=cited_signals,
        context_loaded=context_loaded,
        context_error=context_error
    )

    # Output
    if args.output == "table":
        print(format_table(results))
    else:
        print(json.dumps(results, indent=2))

    # Exit code based on status
    sys.exit(0 if results['status'] == 'PASSED' else 1)


if __name__ == "__main__":
    main()
