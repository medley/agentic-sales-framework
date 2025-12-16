"""
Cadence Registry - Template definitions for multi-step outbound sequences

Provides:
1. Cadence template definitions (standard_12day, soft_3touch, inmail_first)
2. Step definitions with channel, type, tone, and constraints
3. Lookup functions for cadence retrieval

All cadence steps inherit from email_context.json:
    - persona
    - product eligibility (eligible_products, forbidden_products)
    - confidence_mode
    - angle_id
    - offer_id
    - verified_signals (but only step 1 may cite new claims)

IMPORTANT: No new research, no new angle selection, no new scoring.
Strategy is decided once. Rendering can happen many times.
"""

from typing import Dict, List, Any, Optional
import copy


# =============================================================================
# CADENCE TEMPLATE DEFINITIONS
# =============================================================================

CADENCES = {
    'standard_12day': {
        'name': 'Standard 12-Day Sequence',
        'description': 'Standard 12-day B2B outbound sequence for life sciences',
        'steps': [
            {
                'step': 1,
                'day': 1,
                'channel': 'email',
                'step_type': 'initial',
                'tone': 'curious',
                'constraints': {
                    'word_count_min': 50,
                    'word_count_max': 100,
                    'sentence_count_min': 3,
                    'sentence_count_max': 4,
                    'must_end_with_question': True,
                    'subject_required': True,
                    'subject_word_max': 4,
                },
                'notes': 'Uses full email_plan from context',
                'allows_new_claims': True,
            },
            {
                'step': 2,
                'day': 3,
                'channel': 'email',
                'step_type': 'bump',
                'tone': 'brief',
                'constraints': {
                    'word_count_min': 10,
                    'word_count_max': 25,
                    'sentence_count_min': 1,
                    'sentence_count_max': 1,
                    'must_end_with_question': True,
                    'subject_required': False,
                    'is_reply': True,
                },
                'template': "Just floating this back up - {angle_question}",
                'notes': 'Single sentence, references original angle only',
                'allows_new_claims': False,
            },
            {
                'step': 3,
                'day': 7,
                'channel': 'email',
                'step_type': 'reframe',
                'tone': 'alternative_value',
                'constraints': {
                    'word_count_min': 30,
                    'word_count_max': 60,
                    'sentence_count_min': 2,
                    'sentence_count_max': 3,
                    'must_end_with_question': True,
                    'subject_required': False,
                    'is_reply': True,
                },
                'notes': 'Reframes original offer, no new claims, no new signals',
                'allows_new_claims': False,
            },
            {
                'step': 4,
                'day': 12,
                'channel': 'email',
                'step_type': 'breakup',
                'tone': 'soft_close',
                'constraints': {
                    'word_count_min': 20,
                    'word_count_max': 40,
                    'sentence_count_min': 2,
                    'sentence_count_max': 2,
                    'must_end_with_question': False,
                    'subject_required': False,
                    'is_reply': True,
                },
                'template': "Not trying to fill your inbox. If {angle_topic} isn't a priority, no worries at all.",
                'notes': 'Graceful exit, question optional',
                'allows_new_claims': False,
            },
            {
                'step': 5,
                'day': 1,
                'channel': 'voicemail',
                'step_type': 'initial',
                'tone': 'warm_brief',
                'constraints': {
                    'duration_seconds_min': 20,
                    'duration_seconds_max': 30,
                    'word_count_min': 40,
                    'word_count_max': 65,
                },
                'optional': True,
                'notes': 'Matches email angle, includes callback mention',
                'allows_new_claims': False,
            },
            {
                'step': 6,
                'day': 1,
                'channel': 'inmail',
                'step_type': 'initial',
                'tone': 'curious',
                'constraints': {
                    'word_count_min': 35,
                    'word_count_max': 75,
                    'paragraph_count_min': 2,
                    'paragraph_count_max': 3,
                    'must_end_with_question': False,
                    'subject_required': False,
                },
                'optional': True,
                'notes': 'LinkedIn InMail variant of step 1',
                'allows_new_claims': True,  # Same as step 1, just different channel
            },
        ],
    },

    'soft_3touch': {
        'name': 'Soft 3-Touch Sequence',
        'description': 'Lighter 3-touch sequence for warm leads or referrals',
        'steps': [
            {
                'step': 1,
                'day': 1,
                'channel': 'email',
                'step_type': 'initial',
                'tone': 'curious',
                'constraints': {
                    'word_count_min': 50,
                    'word_count_max': 100,
                    'sentence_count_min': 3,
                    'sentence_count_max': 4,
                    'must_end_with_question': True,
                    'subject_required': True,
                    'subject_word_max': 4,
                },
                'notes': 'Standard initial email',
                'allows_new_claims': True,
            },
            {
                'step': 2,
                'day': 5,
                'channel': 'email',
                'step_type': 'gentle_bump',
                'tone': 'helpful',
                'constraints': {
                    'word_count_min': 25,
                    'word_count_max': 45,
                    'sentence_count_min': 2,
                    'sentence_count_max': 2,
                    'must_end_with_question': True,
                    'subject_required': False,
                    'is_reply': True,
                },
                'notes': 'Gentle follow-up, helpful tone',
                'allows_new_claims': False,
            },
            {
                'step': 3,
                'day': 10,
                'channel': 'email',
                'step_type': 'breakup',
                'tone': 'soft_close',
                'constraints': {
                    'word_count_min': 20,
                    'word_count_max': 40,
                    'sentence_count_min': 2,
                    'sentence_count_max': 2,
                    'must_end_with_question': False,
                    'subject_required': False,
                    'is_reply': True,
                },
                'notes': 'Graceful close',
                'allows_new_claims': False,
            },
        ],
    },

    'inmail_first': {
        'name': 'InMail-First Sequence',
        'description': 'InMail-led sequence for hard-to-reach executives',
        'steps': [
            {
                'step': 1,
                'day': 1,
                'channel': 'inmail',
                'step_type': 'initial',
                'tone': 'curious',
                'constraints': {
                    'word_count_min': 35,
                    'word_count_max': 75,
                    'paragraph_count_min': 2,
                    'paragraph_count_max': 3,
                    'must_end_with_question': False,
                    'subject_required': False,
                },
                'notes': 'LinkedIn InMail initial touch',
                'allows_new_claims': True,
            },
            {
                'step': 2,
                'day': 4,
                'channel': 'email',
                'step_type': 'follow_on',
                'tone': 'reference_inmail',
                'constraints': {
                    'word_count_min': 40,
                    'word_count_max': 80,
                    'sentence_count_min': 3,
                    'sentence_count_max': 4,
                    'must_end_with_question': True,
                    'subject_required': True,
                    'subject_word_max': 4,
                },
                'notes': 'References InMail sent, same angle',
                'allows_new_claims': False,
            },
            {
                'step': 3,
                'day': 9,
                'channel': 'email',
                'step_type': 'breakup',
                'tone': 'soft_close',
                'constraints': {
                    'word_count_min': 20,
                    'word_count_max': 40,
                    'sentence_count_min': 2,
                    'sentence_count_max': 2,
                    'must_end_with_question': False,
                    'subject_required': False,
                    'is_reply': True,
                },
                'notes': 'Graceful close',
                'allows_new_claims': False,
            },
        ],
    },
}


# =============================================================================
# LOOKUP FUNCTIONS
# =============================================================================

def get_cadence(cadence_name: str) -> Optional[Dict[str, Any]]:
    """
    Get full cadence definition by name.

    Args:
        cadence_name: Name of cadence (e.g., 'standard_12day')

    Returns:
        Cadence definition dict or None if not found
    """
    return copy.deepcopy(CADENCES.get(cadence_name))


def get_cadence_steps(cadence_name: str, include_optional: bool = True) -> List[Dict[str, Any]]:
    """
    Get list of steps for a cadence.

    Args:
        cadence_name: Name of cadence
        include_optional: Whether to include optional steps (default: True)

    Returns:
        List of step dicts
    """
    cadence = get_cadence(cadence_name)
    if not cadence:
        return []

    steps = cadence.get('steps', [])

    if not include_optional:
        steps = [s for s in steps if not s.get('optional', False)]

    return steps


def get_required_steps(cadence_name: str) -> List[Dict[str, Any]]:
    """
    Get only required (non-optional) steps for a cadence.

    Args:
        cadence_name: Name of cadence

    Returns:
        List of required step dicts
    """
    return get_cadence_steps(cadence_name, include_optional=False)


def list_cadences() -> List[Dict[str, str]]:
    """
    List all available cadences.

    Returns:
        List of dicts with 'name' and 'description'
    """
    return [
        {
            'id': cadence_id,
            'name': cadence['name'],
            'description': cadence['description'],
            'step_count': len(cadence['steps']),
            'required_step_count': len([s for s in cadence['steps'] if not s.get('optional', False)]),
        }
        for cadence_id, cadence in CADENCES.items()
    ]


def validate_cadence_name(cadence_name: str) -> bool:
    """
    Check if cadence name is valid.

    Args:
        cadence_name: Name to validate

    Returns:
        True if valid, False otherwise
    """
    return cadence_name in CADENCES


def get_step_by_number(cadence_name: str, step_number: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific step from a cadence by step number.

    Args:
        cadence_name: Name of cadence
        step_number: Step number (1-indexed)

    Returns:
        Step dict or None if not found
    """
    steps = get_cadence_steps(cadence_name)
    for step in steps:
        if step.get('step') == step_number:
            return copy.deepcopy(step)
    return None


def get_steps_by_channel(cadence_name: str, channel: str) -> List[Dict[str, Any]]:
    """
    Get all steps for a specific channel.

    Args:
        cadence_name: Name of cadence
        channel: Channel name ('email', 'inmail', 'voicemail')

    Returns:
        List of step dicts for that channel
    """
    steps = get_cadence_steps(cadence_name)
    return [s for s in steps if s.get('channel') == channel]


def get_cadence_channels(cadence_name: str) -> List[str]:
    """
    Get unique channels used in a cadence.

    Args:
        cadence_name: Name of cadence

    Returns:
        List of unique channel names
    """
    steps = get_cadence_steps(cadence_name)
    channels = list(set(s.get('channel') for s in steps if s.get('channel')))
    return sorted(channels)


def get_cadence_duration_days(cadence_name: str) -> int:
    """
    Get total duration of cadence in days.

    Args:
        cadence_name: Name of cadence

    Returns:
        Number of days from first to last step
    """
    steps = get_cadence_steps(cadence_name, include_optional=False)
    if not steps:
        return 0

    days = [s.get('day', 1) for s in steps]
    return max(days)


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python cadence_registry.py <command> [args]")
        print("Commands:")
        print("  list                      - List all cadences")
        print("  get <cadence_name>        - Get full cadence definition")
        print("  steps <cadence_name>      - Get steps for cadence")
        print("  step <cadence_name> <num> - Get specific step")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        cadences = list_cadences()
        for c in cadences:
            print(f"{c['id']}: {c['name']} ({c['required_step_count']} required, {c['step_count']} total)")

    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: python cadence_registry.py get <cadence_name>")
            sys.exit(1)
        cadence_name = sys.argv[2]
        cadence = get_cadence(cadence_name)
        if cadence:
            print(json.dumps(cadence, indent=2))
        else:
            print(f"Cadence not found: {cadence_name}")
            sys.exit(1)

    elif command == "steps":
        if len(sys.argv) < 3:
            print("Usage: python cadence_registry.py steps <cadence_name>")
            sys.exit(1)
        cadence_name = sys.argv[2]
        steps = get_cadence_steps(cadence_name)
        if steps:
            for step in steps:
                optional = " (optional)" if step.get('optional') else ""
                print(f"Step {step['step']} | Day {step['day']} | {step['channel']} | {step['step_type']}{optional}")
        else:
            print(f"Cadence not found: {cadence_name}")
            sys.exit(1)

    elif command == "step":
        if len(sys.argv) < 4:
            print("Usage: python cadence_registry.py step <cadence_name> <step_number>")
            sys.exit(1)
        cadence_name = sys.argv[2]
        step_number = int(sys.argv[3])
        step = get_step_by_number(cadence_name, step_number)
        if step:
            print(json.dumps(step, indent=2))
        else:
            print(f"Step not found: {cadence_name} step {step_number}")
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
