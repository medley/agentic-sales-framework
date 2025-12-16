"""
Tests for Cadence System

Tests cadence template registry and generator:
- Cadence template definitions (standard_12day, soft_3touch, inmail_first)
- Step inheritance rules
- Cadence generation without re-selecting strategy
- Forbidden products blocked in follow-ups
- Confidence mode respected across all steps
"""

import pytest
from src.cadence.cadence_registry import (
    CADENCES,
    get_cadence,
    get_cadence_steps,
    get_required_steps,
    list_cadences,
    validate_cadence_name,
    get_step_by_number,
    get_steps_by_channel,
    get_cadence_channels,
    get_cadence_duration_days,
)
from src.cadence.cadence_generator import (
    CadenceGenerator,
    generate_sequence,
    StepResult,
    format_sequence_markdown,
)


class TestCadenceRegistry:
    """Test cadence template registry."""

    def test_standard_12day_exists(self):
        """standard_12day cadence should be defined."""
        assert 'standard_12day' in CADENCES
        cadence = get_cadence('standard_12day')
        assert cadence['name'] == 'Standard 12-Day Sequence'

    def test_soft_3touch_exists(self):
        """soft_3touch cadence should be defined."""
        assert 'soft_3touch' in CADENCES
        cadence = get_cadence('soft_3touch')
        assert cadence['name'] == 'Soft 3-Touch Sequence'

    def test_inmail_first_exists(self):
        """inmail_first cadence should be defined."""
        assert 'inmail_first' in CADENCES
        cadence = get_cadence('inmail_first')
        assert cadence['name'] == 'InMail-First Sequence'

    def test_list_cadences_returns_all(self):
        """list_cadences should return all defined cadences."""
        cadences = list_cadences()
        ids = [c['id'] for c in cadences]
        assert 'standard_12day' in ids
        assert 'soft_3touch' in ids
        assert 'inmail_first' in ids

    def test_validate_cadence_name(self):
        """validate_cadence_name should validate correctly."""
        assert validate_cadence_name('standard_12day') is True
        assert validate_cadence_name('soft_3touch') is True
        assert validate_cadence_name('nonexistent') is False


class TestStandard12DayCadence:
    """Test standard_12day cadence structure."""

    def test_has_correct_step_count(self):
        """standard_12day should have 6 total steps (4 required, 2 optional)."""
        steps = get_cadence_steps('standard_12day')
        assert len(steps) == 6

        required = get_required_steps('standard_12day')
        assert len(required) == 4

    def test_step_1_is_email_initial(self):
        """Step 1 should be email initial."""
        step = get_step_by_number('standard_12day', 1)
        assert step['channel'] == 'email'
        assert step['step_type'] == 'initial'
        assert step['day'] == 1
        assert step['allows_new_claims'] is True

    def test_step_2_is_bump(self):
        """Step 2 should be bump on day 3."""
        step = get_step_by_number('standard_12day', 2)
        assert step['channel'] == 'email'
        assert step['step_type'] == 'bump'
        assert step['day'] == 3
        assert step['allows_new_claims'] is False

    def test_step_3_is_reframe(self):
        """Step 3 should be reframe on day 7."""
        step = get_step_by_number('standard_12day', 3)
        assert step['channel'] == 'email'
        assert step['step_type'] == 'reframe'
        assert step['day'] == 7
        assert step['allows_new_claims'] is False

    def test_step_4_is_breakup(self):
        """Step 4 should be breakup on day 12."""
        step = get_step_by_number('standard_12day', 4)
        assert step['channel'] == 'email'
        assert step['step_type'] == 'breakup'
        assert step['day'] == 12
        assert step['allows_new_claims'] is False

    def test_optional_steps_are_marked(self):
        """Optional steps should be marked."""
        steps = get_cadence_steps('standard_12day')
        optional_steps = [s for s in steps if s.get('optional', False)]
        assert len(optional_steps) == 2

    def test_cadence_duration(self):
        """Cadence duration should be 12 days."""
        assert get_cadence_duration_days('standard_12day') == 12


class TestInMailFirstCadence:
    """Test inmail_first cadence structure."""

    def test_step_1_is_inmail(self):
        """Step 1 should be InMail."""
        step = get_step_by_number('inmail_first', 1)
        assert step['channel'] == 'inmail'
        assert step['step_type'] == 'initial'

    def test_step_2_is_follow_on_email(self):
        """Step 2 should be follow-on email."""
        step = get_step_by_number('inmail_first', 2)
        assert step['channel'] == 'email'
        assert step['step_type'] == 'follow_on'

    def test_uses_multiple_channels(self):
        """inmail_first should use both inmail and email channels."""
        channels = get_cadence_channels('inmail_first')
        assert 'inmail' in channels
        assert 'email' in channels


class TestCadenceGenerator:
    """Test cadence sequence generation."""

    @pytest.fixture
    def sample_context(self):
        """Sample email context for testing."""
        return {
            'status': 'ready_for_rendering',
            'tier': 'A',
            'prospect_brief': {
                'persona': 'quality',
                'company_name': 'Acme Corp',
                'confidence_tier': 'high',
                'signal_count': 3,
                'verified_signals': [],
                'angle_id': 'capa_cycle_time',
                'offer_id': 'checklist_capa',
                'constraints': {
                    'word_count_min': 50,
                    'word_count_max': 100,
                    'banned_phrases': []
                }
            },
            'email_plan': {
                'sentence_1_draft': 'When quality workflows live across too many tools, small issues turn into inspection risks.',
                'sentence_2_draft': 'Seeing if this is on your radar.',
                'sentence_3_draft': 'If useful, I can send a 1-page checklist. Want it?',
                'subject_candidates': ['CAPA backlog', 'Quality tech debt']
            },
            'contact': {
                'first_name': 'Casey',
                'last_name': 'Hughes',
                'title': 'VP Quality'
            }
        }

    def test_generator_inherits_strategy(self, sample_context):
        """Generator should inherit strategy from context."""
        generator = CadenceGenerator(sample_context)
        assert generator.persona == 'quality'
        assert generator.confidence_mode == 'high'
        assert generator.angle_id == 'capa_cycle_time'
        assert generator.offer_id == 'checklist_capa'

    def test_generate_returns_inherited_strategy(self, sample_context):
        """Generated sequence should include inherited strategy."""
        result = generate_sequence(sample_context, 'standard_12day')
        assert result['inherited_strategy']['persona'] == 'quality'
        assert result['inherited_strategy']['confidence_mode'] == 'high'
        assert result['inherited_strategy']['angle_id'] == 'capa_cycle_time'

    def test_generate_includes_all_steps(self, sample_context):
        """Generated sequence should include all required steps."""
        result = generate_sequence(sample_context, 'standard_12day', include_optional=False)
        assert len(result['steps']) == 4  # 4 required steps

    def test_generate_includes_optional_when_requested(self, sample_context):
        """Generated sequence should include optional steps when requested."""
        result = generate_sequence(sample_context, 'standard_12day', include_optional=True)
        assert len(result['steps']) == 6  # 4 required + 2 optional

    def test_invalid_cadence_returns_error(self, sample_context):
        """Invalid cadence name should return error."""
        result = generate_sequence(sample_context, 'nonexistent_cadence')
        assert result['status'] == 'error'
        assert 'Unknown cadence' in result['error']

    def test_step_results_have_required_fields(self, sample_context):
        """Step results should have all required fields."""
        result = generate_sequence(sample_context, 'soft_3touch')
        for step in result['steps']:
            assert 'step' in step
            assert 'day' in step
            assert 'channel' in step
            assert 'step_type' in step
            assert 'status' in step
            assert 'copy' in step


class TestStepResult:
    """Test StepResult data class."""

    def test_step_result_creation(self):
        """StepResult should create with required fields."""
        result = StepResult(
            step_number=1,
            day=1,
            channel='email',
            step_type='initial',
            status='PASSED',
            copy='Test email body'
        )
        assert result.step_number == 1
        assert result.channel == 'email'
        assert result.status == 'PASSED'

    def test_step_result_to_dict(self):
        """StepResult should convert to dict correctly."""
        result = StepResult(
            step_number=2,
            day=3,
            channel='email',
            step_type='bump',
            status='PASSED',
            copy='Bump copy'
        )
        d = result.to_dict()
        assert d['step'] == 2
        assert d['day'] == 3
        assert d['channel'] == 'email'
        assert d['step_type'] == 'bump'


class TestSequenceMarkdownFormat:
    """Test sequence markdown formatting."""

    @pytest.fixture
    def sample_result(self):
        """Sample sequence result for formatting."""
        return {
            'status': 'success',
            'cadence_name': 'standard_12day',
            'cadence_display_name': 'Standard 12-Day Sequence',
            'cadence_duration_days': 12,
            'generated_at': '2024-12-11T10:00:00',
            'inherited_strategy': {
                'persona': 'quality',
                'confidence_mode': 'high',
                'angle_id': 'capa_cycle_time',
                'offer_id': 'checklist_capa'
            },
            'contact': {
                'first_name': 'Casey',
                'company_name': 'Acme Corp'
            },
            'step_summary': {
                'total': 4,
                'required': 4,
                'passed': 4,
                'failed': 0,
                'skipped': 0
            },
            'steps': [
                {
                    'step': 1,
                    'day': 1,
                    'channel': 'email',
                    'step_type': 'initial',
                    'status': 'PASSED',
                    'copy': 'Test email',
                    'subject': 'CAPA backlog'
                }
            ]
        }

    def test_markdown_includes_header(self, sample_result):
        """Markdown should include cadence name as header."""
        md = format_sequence_markdown(sample_result)
        assert '# Standard 12-Day Sequence' in md

    def test_markdown_includes_strategy(self, sample_result):
        """Markdown should include inherited strategy."""
        md = format_sequence_markdown(sample_result)
        assert 'Persona:' in md
        assert 'quality' in md
        assert 'Confidence Mode:' in md
        assert 'high' in md

    def test_markdown_includes_steps(self, sample_result):
        """Markdown should include step details."""
        md = format_sequence_markdown(sample_result)
        assert 'Step 1' in md
        assert 'EMAIL' in md
        assert 'PASSED' in md

    def test_markdown_includes_disclaimer(self, sample_result):
        """Markdown should include NOT auto-sent disclaimer."""
        md = format_sequence_markdown(sample_result)
        assert 'NOT auto-sent' in md


class TestNoNewClaimsEnforcement:
    """Test that follow-up steps don't introduce new claims."""

    def test_step_1_allows_claims(self):
        """Step 1 (initial) should allow new claims."""
        step = get_step_by_number('standard_12day', 1)
        assert step['allows_new_claims'] is True

    def test_step_2_forbids_claims(self):
        """Step 2 (bump) should forbid new claims."""
        step = get_step_by_number('standard_12day', 2)
        assert step['allows_new_claims'] is False

    def test_step_3_forbids_claims(self):
        """Step 3 (reframe) should forbid new claims."""
        step = get_step_by_number('standard_12day', 3)
        assert step['allows_new_claims'] is False

    def test_step_4_forbids_claims(self):
        """Step 4 (breakup) should forbid new claims."""
        step = get_step_by_number('standard_12day', 4)
        assert step['allows_new_claims'] is False

    def test_all_follow_ups_forbid_claims(self):
        """All follow-up steps should forbid new claims."""
        for cadence_name in CADENCES:
            steps = get_cadence_steps(cadence_name)
            for step in steps:
                if step['step'] > 1 and step['step_type'] != 'initial':
                    assert step['allows_new_claims'] is False, \
                        f"{cadence_name} step {step['step']} should forbid claims"
