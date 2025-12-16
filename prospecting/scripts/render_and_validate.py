#!/usr/bin/env python3
"""
Render and Validate Email - Auto-repair pipeline for prospect emails

This script takes draft sentences from the email context and:
1. Renders email variants (supports email, inmail, voicemail channels)
2. Validates each variant against channel-specific constraints
3. Auto-repairs failures (up to 2 attempts)
4. Returns validated email or reports failure
5. Optionally generates multi-step cadence sequences

Usage:
    # Standard email rendering
    python3 scripts/render_and_validate.py [--context path] [--max-repairs 2]

    # InMail rendering
    python3 scripts/render_and_validate.py --channel inmail

    # Cadence sequence generation
    python3 scripts/render_and_validate.py --cadence standard_12day

Output:
    JSON with rendered and validated email variants

The repair loop is deterministic - all repairs follow strict rules:
- Sentence count too high: Merge sentences
- Sentence count too low: Split or add transition
- Doesn't end with question: Convert last sentence to question
- Word count issues: Trim or expand

Channels:
- email: Standard first-touch email (50-100 words, must end with question)
- inmail: LinkedIn InMail (35-75 words, question optional, no subject)
- voicemail: Voicemail script (20-30 seconds)

Cadences:
- standard_12day: 4 required steps + 2 optional over 12 days
- soft_3touch: 3 lighter touches over 10 days
- inmail_first: InMail-led sequence for hard-to-reach executives
"""

import sys
import json
import argparse
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from path_resolver import get_email_context_path
from rules_loader import load_rules

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Render email from draft sentences and validate with auto-repair"
    )
    parser.add_argument(
        "--context",
        help="Path to email_context.json (default: from path_resolver)",
        default=None
    )
    parser.add_argument(
        "--max-repairs",
        type=int,
        default=2,
        help="Maximum repair attempts per variant (default: 2)"
    )
    parser.add_argument(
        "--output",
        help="Output format: json or summary",
        default="json"
    )
    # New channel support
    parser.add_argument(
        "--channel",
        choices=["email", "inmail", "voicemail"],
        default="email",
        help="Output channel: email (default), inmail, or voicemail"
    )
    # New cadence support
    parser.add_argument(
        "--cadence",
        choices=["standard_12day", "soft_3touch", "inmail_first"],
        default=None,
        help="Generate multi-step cadence sequence"
    )
    parser.add_argument(
        "--include-optional",
        action="store_true",
        help="Include optional steps in cadence generation"
    )
    return parser.parse_args()


def load_context(context_path: str) -> Tuple[dict, bool, Optional[str]]:
    """Load email context from JSON file."""
    try:
        with open(context_path, 'r') as f:
            return json.load(f), True, None
    except FileNotFoundError:
        return {}, False, f"Context file not found: {context_path}"
    except json.JSONDecodeError as e:
        return {}, False, f"Invalid JSON in context file: {e}"


def count_sentences(text: str) -> int:
    """Count sentences in text, excluding greeting and signature."""
    # Remove greeting line (e.g., "Jeffrey," or "Hi,")
    lines = text.strip().split('\n')
    body_lines = []
    for line in lines:
        line = line.strip()
        # Skip greeting (single word followed by comma)
        if re.match(r'^[A-Za-z]+,$', line):
            continue
        # Skip signature (just a name)
        if re.match(r'^[A-Za-z]+$', line) and len(line) < 20:
            continue
        if line:
            body_lines.append(line)

    body_text = ' '.join(body_lines)
    sentences = re.split(r'[.!?]+', body_text)
    return len([s.strip() for s in sentences if s.strip()])


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def ends_with_question(text: str) -> bool:
    """Check if the main body (before signature) ends with a question mark."""
    text = text.strip()

    # Remove signature line if present (just a name at the end)
    lines = text.split('\n')
    while lines and re.match(r'^[A-Za-z]+$', lines[-1].strip()) and len(lines[-1].strip()) < 20:
        lines.pop()

    body = '\n'.join(lines).strip()
    return body.endswith('?')


def validate_email(subject: str, body: str, constraints: dict, channel: str = 'email') -> Dict:
    """
    Run validation checks on email/inmail/voicemail.

    Args:
        subject: Subject line (may be None for inmail/voicemail)
        body: Message body
        constraints: Constraint dict (channel-specific)
        channel: Output channel ('email', 'inmail', 'voicemail')

    Returns dict with:
        passed: bool
        failures: list of failure strings
        checks: dict of individual check results
    """
    results = {
        "passed": True,
        "failures": [],
        "checks": {},
        "channel": channel
    }

    # Word count
    word_count = count_words(body)
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
        if word_count < word_min:
            results["failures"].append(f"word_count_low:{word_count}:{word_min}")
        else:
            results["failures"].append(f"word_count_high:{word_count}:{word_max}")

    # Sentence/paragraph count (channel-specific)
    if channel == 'inmail':
        # Count paragraphs for InMail
        paragraphs = [p.strip() for p in body.split('\n\n') if p.strip()]
        # Filter out greeting and signature
        content_paras = [p for p in paragraphs
                         if not re.match(r'^(Hi|Hey)\s+\w+,?$', p, re.IGNORECASE)
                         and not re.match(r'^[A-Za-z]+$', p)]
        para_count = len(content_paras)
        para_min = constraints.get('paragraph_count_min', 2)
        para_max = constraints.get('paragraph_count_max', 3)
        para_passed = para_min <= para_count <= para_max
        results["checks"]["paragraph_count"] = {
            "passed": para_passed,
            "actual": para_count,
            "min": para_min,
            "max": para_max
        }
        if not para_passed:
            if para_count < para_min:
                results["failures"].append(f"paragraph_count_low:{para_count}:{para_min}")
            else:
                results["failures"].append(f"paragraph_count_high:{para_count}:{para_max}")
    else:
        # Count sentences for email/voicemail
        sentence_count = count_sentences(body)
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
            if sentence_count < sentence_min:
                results["failures"].append(f"sentence_count_low:{sentence_count}:{sentence_min}")
            else:
                results["failures"].append(f"sentence_count_high:{sentence_count}:{sentence_max}")

    # Ends with question (channel-specific - required for email, optional for inmail)
    if constraints.get('must_end_with_question', channel == 'email'):
        ends_q = ends_with_question(body)
        results["checks"]["ends_with_question"] = {"passed": ends_q, "required": True}
        if not ends_q:
            results["failures"].append("no_question_ending")
    else:
        # Check but don't fail
        ends_q = ends_with_question(body)
        results["checks"]["ends_with_question"] = {"passed": True, "required": False, "actual": ends_q}

    # Subject validation (channel-specific - required for email, not for inmail/voicemail)
    if constraints.get('subject_required', channel == 'email'):
        if not subject:
            results["checks"]["subject_length"] = {"passed": False, "error": "missing"}
            results["failures"].append("missing_subject")
        else:
            subject_words = count_words(subject)
            subject_max = constraints.get('subject_word_max', 4)
            subject_passed = subject_words <= subject_max
            results["checks"]["subject_length"] = {
                "passed": subject_passed,
                "actual": subject_words,
                "max": subject_max
            }
            if not subject_passed:
                results["failures"].append(f"subject_too_long:{subject_words}:{subject_max}")
    else:
        # Subject not required for this channel
        results["checks"]["subject_length"] = {"passed": True, "required": False}

    # Banned phrases
    banned_phrases = constraints.get('banned_phrases', [])
    found_banned = [p for p in banned_phrases if p.lower() in body.lower()]
    results["checks"]["banned_phrases"] = {
        "passed": len(found_banned) == 0,
        "found": found_banned
    }
    if found_banned:
        results["failures"].append(f"banned_phrases:{','.join(found_banned)}")

    # No product pitch
    pitch_terms = ['product_name', 'qx', 'mx', 'our platform', 'our solution',
                   'our software', 'we offer', 'we provide']
    found_pitch = [t for t in pitch_terms if t.lower() in body.lower()]
    results["checks"]["no_product_pitch"] = {
        "passed": len(found_pitch) == 0,
        "found": found_pitch
    }
    if found_pitch:
        results["failures"].append(f"product_pitch:{','.join(found_pitch)}")

    results["passed"] = len(results["failures"]) == 0
    return results


def repair_email(subject: str, body: str, failures: List[str], constraints: dict) -> Tuple[str, str, List[str]]:
    """
    Apply deterministic repairs to email based on failures.

    Returns:
        (repaired_subject, repaired_body, repairs_applied)
    """
    repairs_applied = []
    repaired_body = body
    repaired_subject = subject

    for failure in failures:
        if failure == "no_question_ending":
            # Convert last sentence to question or add question ending
            repaired_body = repair_question_ending(repaired_body)
            repairs_applied.append("converted_to_question")

        elif failure.startswith("sentence_count_high:"):
            # Merge sentences
            repaired_body = repair_merge_sentences(repaired_body, constraints)
            repairs_applied.append("merged_sentences")

        elif failure.startswith("sentence_count_low:"):
            # Split long sentences or this is usually fine with question fix
            repairs_applied.append("sentence_count_adjusted")

        elif failure.startswith("word_count_high:"):
            # Trim words
            repaired_body = repair_trim_words(repaired_body, constraints)
            repairs_applied.append("trimmed_words")

        elif failure.startswith("word_count_low:"):
            # Usually okay - binary question emails can be short
            repairs_applied.append("word_count_accepted")

        elif failure.startswith("subject_too_long:"):
            # Truncate subject
            repaired_subject = repair_truncate_subject(repaired_subject, constraints)
            repairs_applied.append("truncated_subject")

    return repaired_subject, repaired_body, repairs_applied


def repair_question_ending(body: str) -> str:
    """Convert last sentence to end with question mark."""
    body = body.strip()

    # If already ends with ?, return as-is
    if body.endswith('?'):
        return body

    # Find last sentence
    # Look for last period, exclamation, or the end
    last_period = max(body.rfind('.'), body.rfind('!'))

    if last_period == -1:
        # No sentence ending found, just add ?
        return body.rstrip('.!') + '?'

    # Get everything after last sentence ending
    last_sentence_start = last_period + 1
    last_sentence = body[last_sentence_start:].strip()

    if not last_sentence:
        # Last char was the period, need to convert the final sentence
        # Find the second-to-last sentence ending
        earlier_text = body[:last_period]
        prev_period = max(earlier_text.rfind('.'), earlier_text.rfind('!'), earlier_text.rfind('?'))

        if prev_period == -1:
            # Only one sentence, convert it
            return body.rstrip('.!') + '?'

        # Convert final sentence
        final_sentence = body[prev_period+1:last_period].strip()
        # Simple conversion: replace period with question mark
        return body[:last_period] + '?'

    # There's text after the last period - convert that to question
    return body[:last_sentence_start] + ' ' + last_sentence.rstrip('.!') + '?'


def repair_merge_sentences(body: str, constraints: dict) -> str:
    """Merge sentences to reduce count."""
    sentence_max = constraints.get('sentence_count_max', 4)

    # Split into paragraphs first (preserve structure)
    paragraphs = body.split('\n\n')

    # Work on the main body (usually second paragraph after greeting)
    if len(paragraphs) >= 2:
        main_para = paragraphs[1] if len(paragraphs) > 1 else paragraphs[0]
    else:
        main_para = paragraphs[0]

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', main_para)
    sentences = [s.strip() for s in sentences if s.strip()]

    # If too many sentences, merge adjacent short ones
    while len(sentences) > sentence_max and len(sentences) >= 2:
        # Find two shortest adjacent sentences to merge
        min_combined = float('inf')
        merge_idx = 0

        for i in range(len(sentences) - 1):
            combined_len = len(sentences[i]) + len(sentences[i+1])
            if combined_len < min_combined:
                min_combined = combined_len
                merge_idx = i

        # Merge: replace period with semicolon or dash
        merged = sentences[merge_idx].rstrip('.!?') + ' - ' + sentences[merge_idx+1][0].lower() + sentences[merge_idx+1][1:]
        sentences = sentences[:merge_idx] + [merged] + sentences[merge_idx+2:]

    # Reconstruct
    if len(paragraphs) >= 2:
        paragraphs[1] = ' '.join(sentences)
        return '\n\n'.join(paragraphs)
    else:
        return ' '.join(sentences)


def repair_trim_words(body: str, constraints: dict) -> str:
    """Trim words to meet max constraint."""
    word_max = constraints.get('word_count_max', 100)
    words = body.split()

    if len(words) <= word_max:
        return body

    # Keep first word_max words, try to end at sentence boundary
    trimmed = ' '.join(words[:word_max])

    # Find last sentence ending
    last_period = max(trimmed.rfind('.'), trimmed.rfind('!'), trimmed.rfind('?'))

    if last_period > len(trimmed) * 0.7:  # If we're keeping most of it
        return trimmed[:last_period+1]

    return trimmed


def repair_truncate_subject(subject: str, constraints: dict) -> str:
    """Truncate subject to max words."""
    subject_max = constraints.get('subject_word_max', 4)
    words = subject.split()

    if len(words) <= subject_max:
        return subject

    return ' '.join(words[:subject_max])


def render_email_from_drafts(context: dict, channel: str = 'email') -> List[Dict]:
    """
    Render email/inmail/voicemail variants from draft sentences in context.

    Args:
        context: email_context.json contents
        channel: Output channel ('email', 'inmail', 'voicemail')

    Returns list of variants with subject, body, used_signals.
    """
    email_plan = context.get('email_plan', {})
    prospect_brief = context.get('prospect_brief', {})

    # Get draft sentences
    sentences = []
    for i in range(1, 5):
        sent = email_plan.get(f'sentence_{i}_draft', '')
        if sent:
            sentences.append(sent)

    if not sentences:
        return []

    # Get subject candidates (only used for email)
    subjects = email_plan.get('subject_candidates', ['quick question'])

    # Get contact info for greeting
    first_name = 'there'
    contact = context.get('contact', {})
    if contact.get('first_name') and contact['first_name'] not in ['[First Name]', None]:
        first_name = contact['first_name']

    # Build body based on channel
    if channel == 'email':
        greeting = f"{first_name},"
        body_sentences = '\n\n'.join(sentences)
        closing = "\n\n[Your Name]"
        base_body = f"{greeting}\n\n{body_sentences}{closing}"

        # Create variants with different subjects
        variants = []
        for i, subject in enumerate(subjects[:2]):  # Max 2 variants
            variants.append({
                "variant_id": f"variant_{i+1}",
                "subject": subject,
                "body": base_body,
                "channel": "email",
                "used_signal_ids": [],
                "source": "draft_sentences"
            })

    elif channel == 'inmail':
        greeting = f"Hi {first_name},"
        # Convert to paragraph format for InMail (shorter, 2-3 paragraphs)
        if len(sentences) >= 2:
            para1 = sentences[0]
            para2 = ' '.join(sentences[1:])
            base_body = f"{greeting}\n\n{para1}\n\n{para2}\n\n[Your Name]"
        else:
            base_body = f"{greeting}\n\n{sentences[0]}\n\n[Your Name]"

        # InMail has no subject, single variant
        variants = [{
            "variant_id": "inmail_1",
            "subject": None,
            "body": base_body,
            "channel": "inmail",
            "used_signal_ids": [],
            "source": "draft_sentences"
        }]

    elif channel == 'voicemail':
        # Voicemail script format
        angle_hook = sentences[0] if sentences else "Thought it was worth reaching out."
        base_body = (
            f"Hey {first_name}, this is {{sender_name}} with {{company_name}}.\n"
            f"{angle_hook}\n"
            "Thought it was worth a quick call.\n"
            "My number is [callback]. Looking forward to connecting."
        )

        variants = [{
            "variant_id": "voicemail_1",
            "subject": None,
            "body": base_body,
            "channel": "voicemail",
            "used_signal_ids": [],
            "source": "draft_sentences"
        }]

    else:
        # Fallback to email format
        greeting = f"{first_name},"
        body_sentences = '\n\n'.join(sentences)
        closing = "\n\n[Your Name]"
        base_body = f"{greeting}\n\n{body_sentences}{closing}"

        variants = [{
            "variant_id": "variant_1",
            "subject": subjects[0] if subjects else "quick question",
            "body": base_body,
            "channel": channel,
            "used_signal_ids": [],
            "source": "draft_sentences"
        }]

    return variants


def process_with_repair(variant: dict, constraints: dict, max_repairs: int, channel: str = 'email') -> dict:
    """
    Process a variant through validation with auto-repair loop.

    Args:
        variant: Variant dict with subject, body, etc.
        constraints: Constraint dict (channel-specific)
        max_repairs: Maximum repair attempts
        channel: Output channel ('email', 'inmail', 'voicemail')

    Returns:
        {
            "variant_id": str,
            "subject": str,
            "body": str,
            "channel": str,
            "validation": {...},
            "repairs_applied": [...],
            "repair_attempts": int,
            "final_status": "PASSED" | "FAILED"
        }
    """
    result = {
        "variant_id": variant["variant_id"],
        "subject": variant.get("subject"),
        "body": variant["body"],
        "channel": variant.get("channel", channel),
        "used_signal_ids": variant.get("used_signal_ids", []),
        "repairs_applied": [],
        "repair_attempts": 0,
        "final_status": "PENDING"
    }

    current_subject = variant.get("subject")
    current_body = variant["body"]
    variant_channel = variant.get("channel", channel)

    for attempt in range(max_repairs + 1):
        # Validate current version
        validation = validate_email(current_subject, current_body, constraints, variant_channel)
        result["validation"] = validation

        if validation["passed"]:
            result["subject"] = current_subject
            result["body"] = current_body
            result["final_status"] = "PASSED"
            result["repair_attempts"] = attempt
            return result

        # If this was the last attempt, fail
        if attempt >= max_repairs:
            result["subject"] = current_subject
            result["body"] = current_body
            result["final_status"] = "FAILED"
            result["repair_attempts"] = attempt
            return result

        # Apply repairs
        repaired_subject, repaired_body, repairs = repair_email(
            current_subject or '', current_body, validation["failures"], constraints
        )

        result["repairs_applied"].extend(repairs)
        current_subject = repaired_subject if repaired_subject else None
        current_body = repaired_body

    return result


def main():
    args = parse_args()

    # Get context path
    if args.context is None:
        context_path = str(get_email_context_path())
    else:
        context_path = args.context

    # Load context
    context, context_loaded, context_error = load_context(context_path)

    if not context_loaded:
        output = {
            "status": "error",
            "error": context_error,
            "variants": []
        }
        print(json.dumps(output, indent=2))
        sys.exit(1)

    # Check status
    if context.get('status') != 'ready_for_rendering':
        output = {
            "status": "error",
            "error": f"Context status is '{context.get('status')}', expected 'ready_for_rendering'",
            "variants": []
        }
        print(json.dumps(output, indent=2))
        sys.exit(1)

    # Get channel
    channel = args.channel

    # Handle cadence generation mode
    if args.cadence:
        output = handle_cadence_generation(context, args)
        if args.output == "summary":
            print_cadence_summary(output)
        else:
            print(json.dumps(output, indent=2))
        sys.exit(0 if output.get('status') != 'error' else 1)

    # Get constraints (channel-specific)
    base_constraints = context.get('prospect_brief', {}).get('constraints', {})

    # Apply channel-specific constraint overrides
    try:
        from channel_constraints import get_step_constraints
        constraints = get_step_constraints(
            channel=channel,
            step_type='initial',
            base_constraints=base_constraints
        )
    except ImportError:
        # Fallback if channel_constraints not available
        if not base_constraints:
            rules_config = load_rules(tier=context.get('tier', 'A'))
            constraints = rules_config.get('constraints', {
                'word_count_min': 50,
                'word_count_max': 100,
                'sentence_count_min': 3,
                'sentence_count_max': 4,
                'subject_word_max': 4,
                'must_end_with_question': True,
                'banned_phrases': []
            })
        else:
            constraints = base_constraints

    # Render variants from draft sentences
    variants = render_email_from_drafts(context, channel)

    if not variants:
        output = {
            "status": "error",
            "error": "No draft sentences found in email_plan",
            "channel": channel,
            "variants": []
        }
        print(json.dumps(output, indent=2))
        sys.exit(1)

    # Process each variant with repair loop
    processed_variants = []
    for variant in variants:
        result = process_with_repair(variant, constraints, args.max_repairs, channel)
        processed_variants.append(result)

    # Determine overall status
    any_passed = any(v["final_status"] == "PASSED" for v in processed_variants)

    output = {
        "status": "success" if any_passed else "all_failed",
        "channel": channel,
        "max_repairs": args.max_repairs,
        "variants": processed_variants,
        "best_variant": next(
            (v for v in processed_variants if v["final_status"] == "PASSED"),
            processed_variants[0] if processed_variants else None
        )
    }

    if args.output == "summary":
        print(f"Status: {output['status']}")
        print(f"Channel: {channel}")
        for v in processed_variants:
            print(f"\n{v['variant_id']}: {v['final_status']}")
            print(f"  Repairs: {v['repair_attempts']} attempts")
            if v['repairs_applied']:
                print(f"  Applied: {', '.join(v['repairs_applied'])}")
            if v['final_status'] == 'PASSED':
                if v.get('subject'):
                    print(f"\nSubject: {v['subject']}")
                print(f"\n{v['body']}")
    else:
        print(json.dumps(output, indent=2))

    sys.exit(0 if any_passed else 1)


def handle_cadence_generation(context: dict, args) -> dict:
    """
    Handle cadence sequence generation.

    Args:
        context: email_context.json contents
        args: Parsed arguments

    Returns:
        Cadence generation result dict
    """
    try:
        from cadence.cadence_generator import generate_sequence, format_sequence_markdown
        from rules_loader import load_rules
    except ImportError as e:
        return {
            "status": "error",
            "error": f"Cadence generation requires cadence module: {e}",
            "cadence_name": args.cadence,
        }

    # Load rules for validation
    rules_config = load_rules(tier=context.get('tier', 'A'))

    # Generate sequence
    result = generate_sequence(
        context=context,
        cadence_name=args.cadence,
        rules_config=rules_config,
        include_optional=args.include_optional,
    )

    return result


def print_cadence_summary(result: dict):
    """Print human-readable cadence summary."""
    try:
        from cadence.cadence_generator import format_sequence_markdown
        print(format_sequence_markdown(result))
    except ImportError:
        # Fallback summary
        print(f"Cadence: {result.get('cadence_display_name', 'Unknown')}")
        print(f"Status: {result.get('status', 'Unknown')}")
        print(f"Duration: {result.get('cadence_duration_days', 0)} days")
        print("")

        summary = result.get('step_summary', {})
        print(f"Steps: {summary.get('passed', 0)}/{summary.get('required', 0)} passed")
        print("")

        for step in result.get('steps', []):
            status = step.get('status', 'UNKNOWN')
            optional = " (optional)" if step.get('optional') else ""
            print(f"Step {step.get('step')}: {step.get('channel')} | {status}{optional}")
            if step.get('copy'):
                print(f"  Copy: {step['copy'][:80]}...")


if __name__ == "__main__":
    main()
