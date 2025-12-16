"""
Tests for Channel Constraints

Tests channel-specific constraint profiles:
- Email constraints (50-100 words, must end with question, subject required)
- InMail constraints (35-75 words, question optional, no subject)
- Voicemail constraints (40-65 words, script format)
- Step-type modifiers (bump, reframe, breakup)
"""

import pytest
from src.channel_constraints import (
    CHANNELS,
    STEP_TYPES,
    get_channel_constraints,
    get_step_modifications,
    get_step_constraints,
    get_channel_format,
    get_step_rules,
    allows_new_claims,
    validate_channel,
    validate_step_type,
)


class TestChannelDefinitions:
    """Test channel constraint definitions."""

    def test_email_channel_exists(self):
        """Email channel should be defined."""
        assert 'email' in CHANNELS
        assert CHANNELS['email']['description'] == 'Standard first-touch email'

    def test_inmail_channel_exists(self):
        """InMail channel should be defined."""
        assert 'inmail' in CHANNELS
        assert CHANNELS['inmail']['description'] == 'LinkedIn InMail message'

    def test_voicemail_channel_exists(self):
        """Voicemail channel should be defined."""
        assert 'voicemail' in CHANNELS
        assert CHANNELS['voicemail']['description'] == 'Voicemail script for cold outreach'

    def test_email_constraints(self):
        """Email should have correct constraints."""
        constraints = get_channel_constraints('email')
        assert constraints['word_count_min'] == 50
        assert constraints['word_count_max'] == 100
        assert constraints['sentence_count_min'] == 3
        assert constraints['sentence_count_max'] == 4
        assert constraints['subject_required'] is True
        assert constraints['must_end_with_question'] is True

    def test_inmail_constraints(self):
        """InMail should have correct constraints."""
        constraints = get_channel_constraints('inmail')
        assert constraints['word_count_min'] == 35
        assert constraints['word_count_max'] == 75
        assert constraints['paragraph_count_min'] == 2
        assert constraints['paragraph_count_max'] == 3
        assert constraints['subject_required'] is False
        assert constraints['must_end_with_question'] is False

    def test_voicemail_constraints(self):
        """Voicemail should have correct constraints."""
        constraints = get_channel_constraints('voicemail')
        assert constraints['word_count_min'] == 40
        assert constraints['word_count_max'] == 65
        assert constraints['duration_seconds_min'] == 20
        assert constraints['duration_seconds_max'] == 30

    def test_invalid_channel_raises(self):
        """Invalid channel should raise ValueError."""
        with pytest.raises(ValueError) as excinfo:
            get_channel_constraints('telegram')
        assert 'Unknown channel' in str(excinfo.value)


class TestStepTypes:
    """Test step-type modifier definitions."""

    def test_initial_step_exists(self):
        """Initial step type should be defined."""
        assert 'initial' in STEP_TYPES
        assert STEP_TYPES['initial']['allows_new_claims'] is True

    def test_bump_step_exists(self):
        """Bump step type should be defined."""
        assert 'bump' in STEP_TYPES
        assert STEP_TYPES['bump']['allows_new_claims'] is False

    def test_reframe_step_exists(self):
        """Reframe step type should be defined."""
        assert 'reframe' in STEP_TYPES
        assert STEP_TYPES['reframe']['allows_new_claims'] is False

    def test_breakup_step_exists(self):
        """Breakup step type should be defined."""
        assert 'breakup' in STEP_TYPES
        assert STEP_TYPES['breakup']['allows_new_claims'] is False

    def test_bump_modifications(self):
        """Bump step should have short constraints."""
        mods = get_step_modifications('bump')
        assert mods['word_count_min'] == 10
        assert mods['word_count_max'] == 25
        assert mods['sentence_count_min'] == 1
        assert mods['sentence_count_max'] == 1
        assert mods['is_reply'] is True

    def test_breakup_modifications(self):
        """Breakup step should not require question ending."""
        mods = get_step_modifications('breakup')
        assert mods['must_end_with_question'] is False

    def test_invalid_step_type_raises(self):
        """Invalid step type should raise ValueError."""
        with pytest.raises(ValueError) as excinfo:
            get_step_modifications('handshake')
        assert 'Unknown step_type' in str(excinfo.value)


class TestConstraintMerging:
    """Test constraint merging for channel + step combinations."""

    def test_email_initial_uses_email_constraints(self):
        """Email initial should use full email constraints."""
        constraints = get_step_constraints('email', 'initial')
        assert constraints['word_count_min'] == 50
        assert constraints['word_count_max'] == 100
        assert constraints['must_end_with_question'] is True
        assert constraints['_channel'] == 'email'
        assert constraints['_step_type'] == 'initial'

    def test_email_bump_overrides_constraints(self):
        """Email bump should override with shorter constraints."""
        constraints = get_step_constraints('email', 'bump')
        assert constraints['word_count_min'] == 10
        assert constraints['word_count_max'] == 25
        assert constraints['sentence_count_min'] == 1
        assert constraints['_step_type'] == 'bump'

    def test_inmail_initial_uses_inmail_constraints(self):
        """InMail initial should use inmail constraints."""
        constraints = get_step_constraints('inmail', 'initial')
        assert constraints['word_count_min'] == 35
        assert constraints['word_count_max'] == 75
        assert constraints['must_end_with_question'] is False
        assert constraints['_channel'] == 'inmail'

    def test_base_constraints_are_included(self):
        """Base constraints from context should be included."""
        base = {'banned_phrases': ['touch base', 'circle back']}
        constraints = get_step_constraints('email', 'initial', base)
        assert 'banned_phrases' in constraints

    def test_channel_overrides_base(self):
        """Channel constraints should override base constraints."""
        base = {'word_count_max': 200}
        constraints = get_step_constraints('email', 'initial', base)
        assert constraints['word_count_max'] == 100  # Email max, not base

    def test_step_overrides_channel(self):
        """Step modifications should override channel constraints."""
        constraints = get_step_constraints('email', 'bump')
        assert constraints['word_count_max'] == 25  # Bump max, not email 100


class TestChannelFormat:
    """Test channel format specifications."""

    def test_email_format(self):
        """Email should have sentence structure."""
        fmt = get_channel_format('email')
        assert fmt['greeting'] == 'Hey {first_name}'
        assert fmt['structure'] == 'sentences'
        assert fmt['closing'] == '[Your Name]'

    def test_inmail_format(self):
        """InMail should have paragraph structure."""
        fmt = get_channel_format('inmail')
        assert fmt['greeting'] == 'Hi {first_name}'
        assert fmt['structure'] == 'paragraphs'


class TestStepRules:
    """Test step rendering rules."""

    def test_initial_allows_claims(self):
        """Initial step should allow new claims."""
        assert allows_new_claims('initial') is True

    def test_bump_forbids_claims(self):
        """Bump step should forbid new claims."""
        assert allows_new_claims('bump') is False

    def test_reframe_forbids_claims(self):
        """Reframe step should forbid new claims."""
        assert allows_new_claims('reframe') is False

    def test_breakup_forbids_claims(self):
        """Breakup step should forbid new claims."""
        assert allows_new_claims('breakup') is False

    def test_bump_rules_reference_angle_only(self):
        """Bump rules should require referencing original angle only."""
        rules = get_step_rules('bump')
        assert 'Reference original angle only' in rules
        assert 'No new claims' in rules


class TestValidation:
    """Test validation helper functions."""

    def test_validate_valid_channel(self):
        """Valid channels should pass validation."""
        assert validate_channel('email') is True
        assert validate_channel('inmail') is True
        assert validate_channel('voicemail') is True

    def test_validate_invalid_channel(self):
        """Invalid channels should fail validation."""
        assert validate_channel('telegram') is False
        assert validate_channel('sms') is False

    def test_validate_valid_step_type(self):
        """Valid step types should pass validation."""
        assert validate_step_type('initial') is True
        assert validate_step_type('bump') is True
        assert validate_step_type('breakup') is True

    def test_validate_invalid_step_type(self):
        """Invalid step types should fail validation."""
        assert validate_step_type('handshake') is False
        assert validate_step_type('aggressive') is False
