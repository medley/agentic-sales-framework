"""
Cadence Package - Multi-step outbound sequence generation

This package provides:
1. Cadence template registry (standard_12day, soft_3touch, inmail_first)
2. Cadence generator for creating sequence files
3. Step rendering with inherited strategy

Core Principle:
    Strategy is decided once. Rendering can happen many times.
    All cadence steps inherit persona, product eligibility, confidence mode,
    angle, and offer from the initial email_context.json.
"""

from .cadence_registry import (
    CADENCES,
    get_cadence,
    get_cadence_steps,
    list_cadences,
    validate_cadence_name,
)

from .cadence_generator import (
    CadenceGenerator,
    generate_sequence,
)

__all__ = [
    'CADENCES',
    'get_cadence',
    'get_cadence_steps',
    'list_cadences',
    'validate_cadence_name',
    'CadenceGenerator',
    'generate_sequence',
]
