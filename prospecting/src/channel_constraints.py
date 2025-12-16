"""
Channel Constraints - Channel-specific constraint profiles for rendering

Provides:
1. Channel definitions (email, inmail, voicemail)
2. Step-type modifiers (initial, bump, reframe, breakup)
3. Constraint merging for channel + step combinations

Usage:
    from channel_constraints import get_step_constraints, CHANNELS

    constraints = get_step_constraints(
        channel='email',
        step_type='initial',
        base_constraints=context.get('prospect_brief', {}).get('constraints', {})
    )
"""

from typing import Dict, Any, Optional
import copy

# =============================================================================
# CHANNEL DEFINITIONS
# =============================================================================

CHANNELS = {
    'email': {
        'description': 'Standard first-touch email',
        'constraints': {
            'word_count_min': 50,
            'word_count_max': 100,
            'sentence_count_min': 3,
            'sentence_count_max': 4,
            'subject_required': True,
            'subject_word_max': 4,
            'subject_style': 'lowercase',
            'must_end_with_question': True,
            'no_meeting_ask': True,
            'no_product_pitch': True,
            'question_style': 'binary',  # yes/no question
        },
        'format': {
            'greeting': 'Hey {first_name}',
            'structure': 'sentences',  # flat sentence structure
            'closing': '[Your Name]',
        },
    },

    'inmail': {
        'description': 'LinkedIn InMail message',
        'constraints': {
            'word_count_min': 35,
            'word_count_max': 75,
            'paragraph_count_min': 2,
            'paragraph_count_max': 3,
            'subject_required': False,
            'must_end_with_question': False,  # Question allowed but not required
            'softer_cta_allowed': True,
            'no_meeting_ask': True,
            'no_product_pitch': True,
            'question_style': 'open',  # Can be open-ended
        },
        'format': {
            'greeting': 'Hi {first_name}',
            'structure': 'paragraphs',  # Short paragraphs, not numbered sentences
            'closing': '[Your Name]',
        },
        'notes': 'Platform character limits apply (~1900 chars), but our constraint is tighter',
    },

    'voicemail': {
        'description': 'Voicemail script for cold outreach',
        'constraints': {
            'duration_seconds_min': 20,
            'duration_seconds_max': 30,
            'word_count_min': 40,
            'word_count_max': 65,
            'must_include_callback': True,
            'no_product_pitch': True,
            'no_meeting_ask': True,
        },
        'format': {
            'structure': 'script',
            'pace_wpm': 130,  # Words per minute for timing
        },
        'template': (
            "Hey {first_name}, this is {sender_name} with {company_name}.\n"
            "{angle_hook}\n"
            "Thought it was worth a quick call.\n"
            "My number is {callback_number}. Looking forward to connecting."
        ),
    },
}


# =============================================================================
# STEP-TYPE MODIFIERS
# =============================================================================

STEP_TYPES = {
    'initial': {
        'description': 'Initial outreach message',
        'modifications': {},  # Uses full channel constraints
        'rules': [
            'Uses full email_plan from context',
            'May cite verified signals',
        ],
        'allows_new_claims': True,
    },

    'bump': {
        'description': 'Short follow-up bump',
        'modifications': {
            'word_count_min': 10,
            'word_count_max': 25,
            'sentence_count_min': 1,
            'sentence_count_max': 1,
            'subject_required': False,
            'is_reply': True,
        },
        'rules': [
            'Reference original angle only',
            'No new claims',
            'No new signals',
        ],
        'allows_new_claims': False,
        'template': "Just floating this back up - {angle_question}",
    },

    'reframe': {
        'description': 'Follow-up with alternative value framing',
        'modifications': {
            'word_count_min': 30,
            'word_count_max': 60,
            'sentence_count_min': 2,
            'sentence_count_max': 3,
            'subject_required': False,
            'is_reply': True,
        },
        'rules': [
            'Present alternative value from same angle',
            'No new claims',
            'No new signals',
        ],
        'allows_new_claims': False,
    },

    'breakup': {
        'description': 'Final soft close message',
        'modifications': {
            'word_count_min': 20,
            'word_count_max': 40,
            'sentence_count_min': 2,
            'sentence_count_max': 2,
            'must_end_with_question': False,
            'subject_required': False,
            'is_reply': True,
        },
        'rules': [
            'Graceful exit',
            'No pressure',
            'Leave door open',
        ],
        'allows_new_claims': False,
        'template': "Not trying to fill your inbox. If {angle_topic} isn't a priority, no worries at all.",
    },

    'follow_on': {
        'description': 'Follow-on after InMail (for inmail_first cadence)',
        'modifications': {
            'word_count_min': 40,
            'word_count_max': 80,
            'sentence_count_min': 3,
            'sentence_count_max': 4,
            'must_end_with_question': True,
            'subject_required': True,
            'subject_word_max': 4,
        },
        'rules': [
            'References InMail sent',
            'Same angle as InMail',
            'No new claims',
        ],
        'allows_new_claims': False,
    },

    'gentle_bump': {
        'description': 'Softer bump for soft_3touch cadence',
        'modifications': {
            'word_count_min': 25,
            'word_count_max': 45,
            'sentence_count_min': 2,
            'sentence_count_max': 2,
            'must_end_with_question': True,
            'subject_required': False,
            'is_reply': True,
        },
        'rules': [
            'Helpful tone',
            'No pressure',
            'Reference original offer',
        ],
        'allows_new_claims': False,
    },
}


# =============================================================================
# CONSTRAINT MERGING
# =============================================================================

def get_channel_constraints(channel: str) -> Dict[str, Any]:
    """
    Get base constraints for a channel.

    Args:
        channel: Channel name ('email', 'inmail', 'voicemail')

    Returns:
        Dict of constraints for the channel

    Raises:
        ValueError: If channel is not recognized
    """
    if channel not in CHANNELS:
        raise ValueError(f"Unknown channel: {channel}. Valid channels: {list(CHANNELS.keys())}")

    return copy.deepcopy(CHANNELS[channel]['constraints'])


def get_step_modifications(step_type: str) -> Dict[str, Any]:
    """
    Get constraint modifications for a step type.

    Args:
        step_type: Step type name ('initial', 'bump', 'reframe', 'breakup', etc.)

    Returns:
        Dict of constraint modifications for the step type

    Raises:
        ValueError: If step_type is not recognized
    """
    if step_type not in STEP_TYPES:
        raise ValueError(f"Unknown step_type: {step_type}. Valid types: {list(STEP_TYPES.keys())}")

    return copy.deepcopy(STEP_TYPES[step_type]['modifications'])


def get_step_constraints(
    channel: str,
    step_type: str = 'initial',
    base_constraints: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get merged constraints for a channel + step combination.

    Merge order (later overrides earlier):
    1. Base constraints from email_context.json (if provided)
    2. Channel-specific constraints
    3. Step-type modifications

    Args:
        channel: Channel name ('email', 'inmail', 'voicemail')
        step_type: Step type name ('initial', 'bump', 'reframe', 'breakup')
        base_constraints: Optional base constraints from email_context.json

    Returns:
        Merged constraint dict
    """
    # Start with base constraints or empty dict
    constraints = copy.deepcopy(base_constraints) if base_constraints else {}

    # Apply channel constraints
    channel_constraints = get_channel_constraints(channel)
    constraints.update(channel_constraints)

    # Apply step-type modifications
    step_mods = get_step_modifications(step_type)
    constraints.update(step_mods)

    # Add metadata
    constraints['_channel'] = channel
    constraints['_step_type'] = step_type
    constraints['_allows_new_claims'] = STEP_TYPES.get(step_type, {}).get('allows_new_claims', True)

    return constraints


def get_channel_format(channel: str) -> Dict[str, Any]:
    """
    Get format specification for a channel.

    Args:
        channel: Channel name

    Returns:
        Dict with greeting, structure, closing, etc.
    """
    if channel not in CHANNELS:
        raise ValueError(f"Unknown channel: {channel}")

    return copy.deepcopy(CHANNELS[channel].get('format', {}))


def get_step_rules(step_type: str) -> list:
    """
    Get rendering rules for a step type.

    Args:
        step_type: Step type name

    Returns:
        List of rule strings
    """
    if step_type not in STEP_TYPES:
        raise ValueError(f"Unknown step_type: {step_type}")

    return STEP_TYPES[step_type].get('rules', [])


def get_step_template(step_type: str) -> Optional[str]:
    """
    Get template for a step type (if available).

    Args:
        step_type: Step type name

    Returns:
        Template string or None if no template
    """
    return STEP_TYPES.get(step_type, {}).get('template')


def allows_new_claims(step_type: str) -> bool:
    """
    Check if a step type allows new claims/signals.

    Args:
        step_type: Step type name

    Returns:
        True if new claims are allowed, False otherwise
    """
    return STEP_TYPES.get(step_type, {}).get('allows_new_claims', True)


def validate_channel(channel: str) -> bool:
    """Check if channel is valid."""
    return channel in CHANNELS


def validate_step_type(step_type: str) -> bool:
    """Check if step_type is valid."""
    return step_type in STEP_TYPES


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python channel_constraints.py <command> [args]")
        print("Commands:")
        print("  channels                    - List all channels")
        print("  step-types                  - List all step types")
        print("  constraints <channel> [step] - Get constraints for channel/step")
        print("  format <channel>            - Get format for channel")
        sys.exit(1)

    command = sys.argv[1]

    if command == "channels":
        for name, config in CHANNELS.items():
            print(f"{name}: {config['description']}")

    elif command == "step-types":
        for name, config in STEP_TYPES.items():
            print(f"{name}: {config['description']}")

    elif command == "constraints":
        if len(sys.argv) < 3:
            print("Usage: python channel_constraints.py constraints <channel> [step_type]")
            sys.exit(1)
        channel = sys.argv[2]
        step_type = sys.argv[3] if len(sys.argv) > 3 else 'initial'
        constraints = get_step_constraints(channel, step_type)
        print(json.dumps(constraints, indent=2))

    elif command == "format":
        if len(sys.argv) < 3:
            print("Usage: python channel_constraints.py format <channel>")
            sys.exit(1)
        channel = sys.argv[2]
        fmt = get_channel_format(channel)
        print(json.dumps(fmt, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
