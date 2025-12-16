"""
Tests for LLM Renderer

Tests the LLM renderer's ability to:
- Render variants from email plan
- Parse used_signal_ids from LLM output
- Auto-repair failed variants
- Handle edge cases
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.llm_renderer import LLMRenderer, LLMRendererError, render_variants


@pytest.fixture
def sample_prospect_brief():
    """Sample prospect brief for testing."""
    return {
        'status': 'ready',
        'persona': 'quality',
        'industry': 'pharma',
        'verified_signals': [
            {
                'id': 'signal_001',
                'claim': 'FDA increased inspection frequency by 23% in 2024',
                'source_url': 'https://example.com/fda-stats',
                'scope': 'industry_wide',
                'recency_days': 30,
                'signal_type': 'regulatory_climate'
            },
            {
                'id': 'signal_002',
                'claim': 'QMSR enforcement deadline is February 2, 2026',
                'source_url': 'https://fda.gov/qmsr',
                'scope': 'regulatory',
                'recency_days': 180,
                'signal_type': 'regulatory_deadline'
            },
            {
                'id': 'signal_003',
                'claim': 'Industry benchmarks show 30-50% audit finding reductions with automated compliance',
                'source_url': 'https://example.com/compliance-benchmarks',
                'scope': 'industry',
                'recency_days': 90,
                'signal_type': 'industry_trend'
            }
        ],
        'constraints': {
            'word_count_min': 50,
            'word_count_max': 100,
            'sentence_count_min': 3,
            'sentence_count_max': 4,
            'subject_word_max': 4,
            'must_end_with_question': True,
            'no_meeting_ask': True,
            'no_product_pitch': True
        }
    }


@pytest.fixture
def sample_email_plan():
    """Sample email plan for testing."""
    return {
        'sentence_1_draft': 'FDA increased inspection frequency by 23% in 2024, so documentation rigor is rising.',
        'sentence_2_draft': 'QA teams are pushed to shorten CAPA cycle time, but manual handoffs keep approvals slow.',
        'sentence_3_draft': 'How are you measuring deviation cycle time today?',
        'sentence_4_draft': 'I can send a 1-page checklist QA leaders use to find time sinks. Want it?',
        'subject_candidates': ['CAPA backlog', 'Deviation cycle time', 'Audit prep']
    }


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response."""
    response_text = """Variant 1:
Subject: CAPA backlog
Body: FDA increased inspection frequency by 23% this year, so documentation rigor around deviations is rising. QA teams are being pushed to shorten CAPA cycle time, but manual handoffs keep approvals slow. How are you measuring deviation cycle time today? I can send a 1-page checklist QA leaders use to find time sinks. Want it?
Used_signal_ids: [signal_001]

Variant 2:
Subject: Deviation cycle time
Body: We're seeing more detailed FDA inspections in 2024. Most QA teams tell me CAPA cycle time is slow due to manual handoffs and training gaps. How are you measuring deviation cycle time today? I can send the 1-page checklist QA leaders use. Want it?
Used_signal_ids: [signal_001]

Variant 3:
Subject: Audit prep
Body: FDA inspection frequency jumped 23% this year according to recent enforcement data. CAPA and deviation cycle time keeps coming up as a constraint. Is deviation cycle time trending the way you want? Happy to send a simple 1-page checklist for finding time sinks.
Used_signal_ids: [signal_001]"""

    mock_response = Mock()
    mock_response.content = [Mock(text=response_text)]
    return mock_response


class TestLLMRenderer:
    """Test suite for LLMRenderer class."""

    def test_initialization_with_api_key(self):
        """Test renderer initializes with provided API key."""
        renderer = LLMRenderer(api_key="test-key")
        assert renderer.api_key == "test-key"
        # Model should be set (either from env or default)
        assert renderer.model is not None
        assert len(renderer.model) > 0

    def test_initialization_without_api_key_raises_error(self):
        """Test renderer raises error when no API key provided."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                LLMRenderer()

    def test_initialization_with_env_var(self):
        """Test renderer initializes with API key from environment."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'env-key'}):
            renderer = LLMRenderer()
            assert renderer.api_key == "env-key"

    @patch('src.llm_renderer.Anthropic')
    def test_render_variants_success(
        self,
        mock_anthropic_class,
        sample_prospect_brief,
        sample_email_plan,
        mock_anthropic_response
    ):
        """Test successful variant rendering."""
        # Setup mock
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_anthropic_response
        mock_anthropic_class.return_value = mock_client

        # Render variants
        renderer = LLMRenderer(api_key="test-key")
        variants = renderer.render_variants(
            prospect_brief=sample_prospect_brief,
            email_plan=sample_email_plan,
            voice_refs={},
            n=3,
            rules_config={}
        )

        # Assertions
        assert len(variants) == 3
        assert all('subject' in v for v in variants)
        assert all('body' in v for v in variants)
        assert all('used_signal_ids' in v for v in variants)
        assert all('attempt' in v for v in variants)

        # Check signal IDs were parsed
        assert variants[0]['used_signal_ids'] == ['signal_001']
        assert variants[1]['used_signal_ids'] == ['signal_001']
        assert variants[2]['used_signal_ids'] == ['signal_001']

    @patch('src.llm_renderer.Anthropic')
    def test_render_variants_api_error(
        self,
        mock_anthropic_class,
        sample_prospect_brief,
        sample_email_plan
    ):
        """Test handling of API errors."""
        # Setup mock to raise exception
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic_class.return_value = mock_client

        # Attempt to render
        renderer = LLMRenderer(api_key="test-key")

        with pytest.raises(LLMRendererError, match="Failed to render variants"):
            renderer.render_variants(
                prospect_brief=sample_prospect_brief,
                email_plan=sample_email_plan,
                voice_refs={},
                n=3,
                rules_config={}
            )

    def test_parse_variants_success(self):
        """Test parsing of variant blocks from LLM response."""
        renderer = LLMRenderer(api_key="test-key")

        response_text = """Variant 1:
Subject: Test Subject
Body: This is a test body with multiple sentences. It contains a question? Here is the end.
Used_signal_ids: [signal_001, signal_002]

Variant 2:
Subject: Another Subject
Body: Another test body. Does this work? Yes.
Used_signal_ids: [signal_003]"""

        variants = renderer._parse_variants(response_text)

        assert len(variants) == 2

        # Check first variant
        assert variants[0]['subject'] == 'Test Subject'
        assert 'test body' in variants[0]['body'].lower()
        assert variants[0]['used_signal_ids'] == ['signal_001', 'signal_002']

        # Check second variant
        assert variants[1]['subject'] == 'Another Subject'
        assert 'another test body' in variants[1]['body'].lower()
        assert variants[1]['used_signal_ids'] == ['signal_003']

    def test_parse_variants_with_no_signal_ids(self):
        """Test parsing variants that don't reference any signals."""
        renderer = LLMRenderer(api_key="test-key")

        response_text = """Variant 1:
Subject: Test
Body: Simple body text. No claims needed. Want to learn more?
Used_signal_ids: []"""

        variants = renderer._parse_variants(response_text)

        assert len(variants) == 1
        assert variants[0]['used_signal_ids'] == []

    def test_parse_variants_malformed_response(self):
        """Test handling of malformed LLM responses."""
        renderer = LLMRenderer(api_key="test-key")

        # Missing body
        response_text = """Variant 1:
Subject: Test
Used_signal_ids: [signal_001]"""

        variants = renderer._parse_variants(response_text)
        assert len(variants) == 0  # Should skip malformed variants

    def test_build_prompt_includes_all_elements(
        self,
        sample_email_plan,
        sample_prospect_brief
    ):
        """Test that prompt includes all required elements."""
        renderer = LLMRenderer(api_key="test-key")

        prompt = renderer._build_prompt(
            email_plan=sample_email_plan,
            verified_signals=sample_prospect_brief['verified_signals'],
            constraints=sample_prospect_brief['constraints'],
            n=3
        )

        # Check all draft sentences are included
        assert sample_email_plan['sentence_1_draft'] in prompt
        assert sample_email_plan['sentence_2_draft'] in prompt
        assert sample_email_plan['sentence_3_draft'] in prompt
        assert sample_email_plan['sentence_4_draft'] in prompt

        # Check signal IDs are included
        assert 'signal_001' in prompt
        assert 'signal_002' in prompt
        assert 'signal_003' in prompt

        # Check constraints are mentioned
        assert '50 to 100 words' in prompt
        assert '3 to 4 sentences' in prompt

        # Check hard rules are included
        assert 'do not ask for a call, meeting' in prompt.lower()
        assert 'do not pitch product' in prompt.lower()
        assert 'used_signal_ids' in prompt.lower()

    @patch('src.llm_renderer.Anthropic')
    def test_repair_variant_success(
        self,
        mock_anthropic_class,
        sample_prospect_brief,
        sample_email_plan
    ):
        """Test successful variant repair."""
        # Setup mock for repair response
        repair_response_text = """Subject: Fixed Subject
Body: This is the repaired body text. It now meets all constraints. Does this work for you? Perfect.
Used_signal_ids: [signal_001]"""

        mock_response = Mock()
        mock_response.content = [Mock(text=f"Variant 1:\n{repair_response_text}")]

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        # Create renderer and repair
        renderer = LLMRenderer(api_key="test-key")

        failed_variant = {
            'subject': 'Bad Subject',
            'body': 'Bad body.',
            'used_signal_ids': []
        }

        violations = ['Too short', 'Missing question']

        repaired = renderer.repair_variant(
            variant=failed_variant,
            violations=violations,
            prospect_brief=sample_prospect_brief,
            email_plan=sample_email_plan,
            attempt=1
        )

        # Assertions
        assert repaired['subject'] == 'Fixed Subject'
        assert 'repaired body text' in repaired['body'].lower()
        assert repaired['attempt'] == 1

    @patch('src.llm_renderer.Anthropic')
    def test_repair_variant_api_error_returns_original(
        self,
        mock_anthropic_class,
        sample_prospect_brief,
        sample_email_plan
    ):
        """Test repair returns original variant on API error."""
        # Setup mock to raise exception
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic_class.return_value = mock_client

        renderer = LLMRenderer(api_key="test-key")

        original_variant = {
            'subject': 'Original',
            'body': 'Original body',
            'used_signal_ids': []
        }

        repaired = renderer.repair_variant(
            variant=original_variant,
            violations=['Some issue'],
            prospect_brief=sample_prospect_brief,
            email_plan=sample_email_plan,
            attempt=1
        )

        # Should return original variant unchanged
        assert repaired == original_variant

    def test_build_repair_prompt_includes_violations(
        self,
        sample_email_plan,
        sample_prospect_brief
    ):
        """Test that repair prompt includes violations."""
        renderer = LLMRenderer(api_key="test-key")

        variant = {
            'subject': 'Test',
            'body': 'Test body',
            'used_signal_ids': []
        }

        violations = [
            'Too short: 2 words',
            'Missing question mark',
            'Contains banned phrase: "circle back"'
        ]

        prompt = renderer._build_repair_prompt(
            variant=variant,
            violations=violations,
            email_plan=sample_email_plan,
            verified_signals=sample_prospect_brief['verified_signals'],
            constraints=sample_prospect_brief['constraints']
        )

        # Check violations are in prompt
        for violation in violations:
            assert violation in prompt

        # Check current email is included
        assert 'Test body' in prompt

        # Check instructions
        assert 'fix' in prompt.lower() or 'repair' in prompt.lower()


class TestConvenienceFunction:
    """Test the convenience function."""

    @patch('src.llm_renderer.LLMRenderer')
    def test_render_variants_function(
        self,
        mock_renderer_class,
        sample_prospect_brief,
        sample_email_plan
    ):
        """Test the render_variants convenience function."""
        # Setup mock
        mock_renderer = Mock()
        mock_renderer.render_variants.return_value = [
            {'subject': 'Test', 'body': 'Test body', 'used_signal_ids': []}
        ]
        mock_renderer_class.return_value = mock_renderer

        # Call function
        result = render_variants(
            prospect_brief=sample_prospect_brief,
            email_plan=sample_email_plan,
            voice_refs={},
            n=3
        )

        # Assertions
        assert len(result) == 1
        mock_renderer.render_variants.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
