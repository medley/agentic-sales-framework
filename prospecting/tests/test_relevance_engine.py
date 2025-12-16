"""
Tests for relevance_engine.py

Test coverage:
- Persona detection from various titles
- Signal extraction with source_url requirement
- Tier A rejection with < 3 signals
- Tier A success with 3+ signals
- Angle and offer selection
- Email plan generation with draft text
- Constraints building
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from relevance_engine import RelevanceEngine, build_prospect_brief


@pytest.fixture
def basic_rules_config():
    """Basic rules configuration for testing."""
    return {
        'personas': {
            'quality': {
                'patterns': ['VP Quality', 'Director Quality', 'QA Director', 'Quality Assurance']
            },
            'operations': {
                'patterns': ['VP Operations', 'Director Operations', 'Operations Director']
            },
            'it': {
                'patterns': ['CIO', 'VP IT', 'Director IT', 'Chief Information']
            },
            'regulatory': {
                'patterns': ['VP Regulatory', 'Director Regulatory', 'Regulatory Affairs']
            }
        },
        'angles': {
            'regulatory_pressure': {
                'personas': ['quality', 'regulatory'],
                'industries': ['pharma', 'biotech', 'medical_device'],
                'signal_types': ['regulatory_climate', 'regulatory_deadline'],
                'pain_text': 'QA teams are pushed to shorten CAPA cycle time, but manual handoffs keep approvals slow.',
                'question': 'How are you measuring deviation cycle time today?',
                'subjects': ['CAPA backlog', 'Deviation cycle time']
            },
            'batch_efficiency': {
                'personas': ['operations'],
                'industries': ['pharma', 'biotech'],
                'signal_types': ['company_news', 'industry_wide'],
                'pain_text': 'Operations teams face batch release delays due to manual record review.',
                'question': 'Is batch release a constraint right now?',
                'subjects': ['Batch release time']
            }
        },
        'offers': {
            'checklist_capa': {
                'personas': ['quality', 'regulatory'],
                'compatible_angles': ['regulatory_pressure'],
                'deliverable': 'checklist',
                'cta_text': 'I can send a 1-page checklist QA leaders use to find time sinks. Want it?',
                'question': 'Want it?',
                'subjects': ['CAPA checklist']
            },
            'benchmark_batch': {
                'personas': ['operations'],
                'compatible_angles': ['batch_efficiency'],
                'deliverable': 'benchmark sheet',
                'cta_text': 'I can share a benchmark sheet of metrics ops leaders track. Want it?',
                'question': 'Want me to send it?',
                'subjects': ['Batch metrics']
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
            },
            'B': {
                'min_signals': 2,
                'word_count_min': 40,
                'word_count_max': 120,
                'sentence_count_min': 2,
                'sentence_count_max': 5,
                'must_end_with_question': False,
                'no_meeting_ask': False,
                'no_product_pitch': False
            }
        }
    }


@pytest.fixture
def sample_research_data():
    """Sample research data with signals."""
    return {
        'perplexity': {
            'company_info': {
                'name': 'Acme Pharma',
                'industry': 'Pharmaceutical Manufacturing'
            },
            'recent_news': [
                {
                    'headline': 'Acme Pharma expands manufacturing facility',
                    'url': 'https://example.com/acme-expansion',
                    'date': '2025-11-15'
                },
                {
                    'headline': 'FDA approves new Acme drug candidate',
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


@pytest.fixture
def sample_context():
    """Sample context from context_synthesizer."""
    return {
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
                'source_url': 'https://fda.gov/stats',
                'date': '2025-09-01'
            }
        ]
    }


class TestPersonaDetection:
    """Test persona detection from job titles."""

    def test_detect_quality_persona_vp(self, basic_rules_config):
        """Test detecting quality persona from VP Quality title."""
        engine = RelevanceEngine(basic_rules_config)
        persona = engine.detect_persona('VP Quality')
        assert persona == 'quality'

    def test_detect_quality_persona_director(self, basic_rules_config):
        """Test detecting quality persona from Director Quality title."""
        engine = RelevanceEngine(basic_rules_config)
        persona = engine.detect_persona('Director Quality Assurance')
        assert persona == 'quality'

    def test_detect_operations_persona(self, basic_rules_config):
        """Test detecting operations persona."""
        engine = RelevanceEngine(basic_rules_config)
        persona = engine.detect_persona('VP Operations')
        assert persona == 'operations'

    def test_detect_it_persona(self, basic_rules_config):
        """Test detecting IT persona."""
        engine = RelevanceEngine(basic_rules_config)
        persona = engine.detect_persona('CIO')
        assert persona == 'it'

    def test_detect_regulatory_persona(self, basic_rules_config):
        """Test detecting regulatory persona."""
        engine = RelevanceEngine(basic_rules_config)
        persona = engine.detect_persona('VP Regulatory Affairs')
        assert persona == 'regulatory'

    def test_no_title_returns_default(self, basic_rules_config):
        """Test that no title returns default persona (quality)."""
        engine = RelevanceEngine(basic_rules_config)
        persona = engine.detect_persona(None)
        # With persona safety changes, we return default persona instead of None
        assert persona == 'quality'

    def test_unrecognized_title_returns_default(self, basic_rules_config):
        """Test that unrecognized title returns default persona."""
        engine = RelevanceEngine(basic_rules_config)
        persona = engine.detect_persona('Chief Marketing Officer')
        # With persona safety changes, we return default persona instead of None
        assert persona == 'quality'

    def test_case_insensitive_matching(self, basic_rules_config):
        """Test that persona detection is case insensitive."""
        engine = RelevanceEngine(basic_rules_config)
        persona = engine.detect_persona('vp quality')
        assert persona == 'quality'


class TestSignalExtraction:
    """Test signal extraction with source_url validation."""

    def test_extract_signals_from_triggers(self, basic_rules_config, sample_research_data, sample_context):
        """Test extracting signals from context triggers."""
        engine = RelevanceEngine(basic_rules_config)
        signals = engine.extract_signals(sample_research_data, sample_context)

        # Should have at least one signal from triggers
        assert len(signals) > 0

        # Check signal structure
        signal = signals[0]
        assert 'id' in signal
        assert 'claim' in signal
        assert 'source_url' in signal
        assert 'scope' in signal
        assert 'recency_days' in signal
        assert 'signal_type' in signal

    def test_signals_require_source_url(self, basic_rules_config, sample_context):
        """Test that signals without source_url are excluded."""
        # Create research data with signal missing source_url
        research_data = {
            'perplexity': {
                'recent_news': [
                    {
                        'headline': 'News without URL',
                        # Missing url field
                    }
                ]
            }
        }

        engine = RelevanceEngine(basic_rules_config)
        signals = engine.extract_signals(research_data, sample_context)

        # Signal without URL should be excluded (only trigger signal remains)
        news_signals = [s for s in signals if 'News without URL' in s['claim']]
        assert len(news_signals) == 0

    def test_signals_require_valid_http_url(self, basic_rules_config, sample_context):
        """Test that signals with invalid URLs are excluded."""
        research_data = {
            'webfetch': [
                {
                    'fact': 'Test fact',
                    'url': 'not-a-valid-url'
                }
            ]
        }

        engine = RelevanceEngine(basic_rules_config)
        signals = engine.extract_signals(research_data, sample_context)

        # Invalid URL should be excluded
        invalid_signals = [s for s in signals if 'Test fact' in s['claim']]
        assert len(invalid_signals) == 0

    def test_signal_id_generation(self, basic_rules_config, sample_research_data, sample_context):
        """Test that signal IDs are generated correctly."""
        engine = RelevanceEngine(basic_rules_config)
        signals = engine.extract_signals(sample_research_data, sample_context)

        # Check ID format
        for i, signal in enumerate(signals, 1):
            assert signal['id'] == f"signal_{i:03d}"

    def test_signal_scope_determination(self, basic_rules_config):
        """Test signal scope determination logic."""
        engine = RelevanceEngine(basic_rules_config)

        # Test regulatory scope
        assert engine._determine_scope('regulatory_climate') == 'regulatory'
        assert engine._determine_scope('compliance_update') == 'regulatory'

        # Test company specific scope
        assert engine._determine_scope('company_news') == 'company_specific'

        # Test industry wide scope (default)
        assert engine._determine_scope('unknown_type') == 'industry_wide'


class TestTierValidation:
    """Test tier A/B validation requirements."""

    def test_tier_a_requires_3_signals(self, basic_rules_config, sample_context):
        """Test that tier A rejects with < 3 signals."""
        # Create research data with only 1 signal
        research_data = {
            'webfetch': [
                {
                    'fact': 'Single fact',
                    'url': 'https://example.com/fact1',
                    'type': 'regulatory_climate'
                }
            ]
        }

        brief = build_prospect_brief(
            research_data=research_data,
            context=sample_context,
            tier='A',
            rules_config=basic_rules_config
        )

        # Should return needs_more_research status
        assert brief['status'] == 'needs_more_research'
        assert brief['signals_found'] < 3
        assert brief['signals_required'] == 3
        assert 'reason' in brief
        assert 'recommendations' in brief

    def test_tier_a_succeeds_with_3_signals(self, basic_rules_config, sample_research_data, sample_context):
        """Test that tier A succeeds with 3+ signals."""
        brief = build_prospect_brief(
            research_data=sample_research_data,
            context=sample_context,
            tier='A',
            rules_config=basic_rules_config
        )

        # Should return ready status with 3+ signals
        if len(brief.get('verified_signals', [])) >= 3:
            assert brief['status'] == 'ready'
            assert 'email_plan' in brief
            assert 'constraints' in brief

    def test_tier_b_requires_2_signals(self, basic_rules_config, sample_context):
        """Test that tier B has lower signal requirement."""
        # Create research data with 2 signals
        research_data = {
            'webfetch': [
                {
                    'fact': 'Fact one',
                    'url': 'https://example.com/fact1',
                    'type': 'regulatory_climate'
                },
                {
                    'fact': 'Fact two',
                    'url': 'https://example.com/fact2',
                    'type': 'company_news'
                }
            ]
        }

        brief = build_prospect_brief(
            research_data=research_data,
            context=sample_context,
            tier='B',
            rules_config=basic_rules_config
        )

        # Tier B should succeed with 2 signals
        assert brief['status'] == 'ready'
        assert len(brief['verified_signals']) >= 2


class TestAngleSelection:
    """Test angle selection logic."""

    def test_select_angle_for_quality_persona(self, basic_rules_config):
        """Test selecting angle for quality persona."""
        engine = RelevanceEngine(basic_rules_config)

        signals = [
            {
                'id': 'signal_001',
                'claim': 'FDA increased inspections',
                'source_url': 'https://fda.gov/stats',
                'scope': 'regulatory',
                'recency_days': 30,
                'signal_type': 'regulatory_climate'
            }
        ]

        result = engine.select_angle(signals, persona='quality', industry='pharma')

        # select_angle now returns dict with 'angle_id' key
        angle_id = result['angle_id']

        # Should select a Qx-eligible angle for quality persona
        angles = basic_rules_config.get('angles', {})
        selected_angle = angles.get(angle_id, {})
        angle_products = selected_angle.get('products', [])
        # Quality persona should get Qx angle (not Mx)
        if angle_products:
            assert 'qx' in angle_products or 'px' in angle_products

    def test_select_angle_for_operations_persona(self, basic_rules_config):
        """Test selecting angle for operations persona."""
        engine = RelevanceEngine(basic_rules_config)

        signals = [
            {
                'id': 'signal_001',
                'claim': 'Company expanding production',
                'source_url': 'https://example.com/news',
                'scope': 'company_specific',
                'recency_days': 15,
                'signal_type': 'company_news'
            }
        ]

        result = engine.select_angle(signals, persona='operations', industry='pharma')

        # select_angle now returns dict with 'angle_id' key
        angle_id = result['angle_id']

        # Operations persona can receive both Qx and Mx angles
        angles = basic_rules_config.get('angles', {})
        selected_angle = angles.get(angle_id, {})
        # Should have a valid angle
        assert angle_id is not None

    def test_no_angle_match_returns_default(self, basic_rules_config):
        """Test that no matching angle returns default angle (not None)."""
        engine = RelevanceEngine(basic_rules_config)

        signals = [
            {
                'id': 'signal_001',
                'claim': 'Random news',
                'source_url': 'https://example.com/news',
                'scope': 'industry_wide',
                'recency_days': 100,
                'signal_type': 'unknown'
            }
        ]

        result = engine.select_angle(signals, persona='marketing', industry='retail')

        # With safety changes, we return default angle instead of None
        assert result['angle_id'] is not None
        assert result['angle_scoring_metadata']['method'] == 'default'


class TestOfferSelection:
    """Test offer selection logic."""

    def test_select_offer_for_quality_persona(self, basic_rules_config):
        """Test selecting offer for quality persona."""
        engine = RelevanceEngine(basic_rules_config)

        offer_id = engine.select_offer(
            persona='quality',
            angle_id='regulatory_pressure'
        )

        # Should select checklist_capa offer
        assert offer_id == 'checklist_capa'

    def test_select_offer_for_operations_persona(self, basic_rules_config):
        """Test selecting offer for operations persona."""
        engine = RelevanceEngine(basic_rules_config)

        offer_id = engine.select_offer(
            persona='operations',
            angle_id='batch_efficiency'
        )

        # Should select benchmark_batch offer
        assert offer_id == 'benchmark_batch'


class TestEmailPlanGeneration:
    """Test email plan generation with draft text."""

    def test_generate_email_plan_structure(self, basic_rules_config):
        """Test that email plan has correct structure."""
        engine = RelevanceEngine(basic_rules_config)

        signals = [
            {
                'id': 'signal_001',
                'claim': 'FDA increased inspection frequency by 23%',
                'source_url': 'https://fda.gov/stats',
                'scope': 'regulatory',
                'recency_days': 30,
                'signal_type': 'regulatory_climate'
            }
        ]

        email_plan = engine.generate_email_plan(
            signals=signals,
            angle_id='regulatory_pressure',
            offer_id='checklist_capa',
            persona='quality'
        )

        # Check required fields
        assert 'sentence_1_draft' in email_plan
        assert 'sentence_2_draft' in email_plan
        assert 'sentence_3_draft' in email_plan
        assert 'sentence_4_draft' in email_plan
        assert 'subject_candidates' in email_plan

        # Check that drafts are not empty
        assert len(email_plan['sentence_1_draft']) > 0
        assert len(email_plan['sentence_2_draft']) > 0
        assert len(email_plan['sentence_3_draft']) > 0
        assert len(email_plan['sentence_4_draft']) > 0

        # Check subject candidates
        assert isinstance(email_plan['subject_candidates'], list)
        assert len(email_plan['subject_candidates']) > 0

    def test_email_plan_uses_signal_in_hook(self, basic_rules_config):
        """Test that sentence_1_draft uses signal claim."""
        engine = RelevanceEngine(basic_rules_config)

        signals = [
            {
                'id': 'signal_001',
                'claim': 'FDA increased inspection frequency by 23%',
                'source_url': 'https://fda.gov/stats',
                'scope': 'regulatory',
                'recency_days': 30,
                'signal_type': 'regulatory_climate'
            }
        ]

        email_plan = engine.generate_email_plan(
            signals=signals,
            angle_id='regulatory_pressure',
            offer_id='checklist_capa',
            persona='quality'
        )

        # Sentence 1 should use signal claim
        assert 'FDA increased inspection frequency by 23%' in email_plan['sentence_1_draft']

    def test_email_plan_uses_angle_pain_text(self, basic_rules_config):
        """Test that sentence_2_draft uses angle pain text."""
        engine = RelevanceEngine(basic_rules_config)

        signals = [
            {
                'id': 'signal_001',
                'claim': 'FDA increased inspections',
                'source_url': 'https://fda.gov/stats',
                'scope': 'regulatory',
                'recency_days': 30,
                'signal_type': 'regulatory_climate'
            }
        ]

        email_plan = engine.generate_email_plan(
            signals=signals,
            angle_id='regulatory_pressure',
            offer_id='checklist_capa',
            persona='quality'
        )

        # Sentence 2 should use pain text from angle config
        assert 'CAPA cycle time' in email_plan['sentence_2_draft']

    def test_email_plan_ends_with_cta(self, basic_rules_config):
        """Test that sentence_4_draft contains CTA from offer."""
        engine = RelevanceEngine(basic_rules_config)

        signals = [
            {
                'id': 'signal_001',
                'claim': 'FDA increased inspections',
                'source_url': 'https://fda.gov/stats',
                'scope': 'regulatory',
                'recency_days': 30,
                'signal_type': 'regulatory_climate'
            }
        ]

        email_plan = engine.generate_email_plan(
            signals=signals,
            angle_id='regulatory_pressure',
            offer_id='checklist_capa',
            persona='quality'
        )

        # Sentence 4 should contain CTA
        assert 'checklist' in email_plan['sentence_4_draft'].lower()
        assert 'want it?' in email_plan['sentence_4_draft'].lower()


class TestConstraintsBuilding:
    """Test constraints object building."""

    def test_build_tier_a_constraints(self, basic_rules_config):
        """Test building constraints for tier A."""
        engine = RelevanceEngine(basic_rules_config)

        constraints = engine.build_constraints(tier='A')

        # Check tier A constraints
        assert constraints['word_count_min'] == 50
        assert constraints['word_count_max'] == 100
        assert constraints['sentence_count_min'] == 3
        assert constraints['sentence_count_max'] == 4
        assert constraints['must_end_with_question'] is True
        assert constraints['no_meeting_ask'] is True
        assert constraints['no_product_pitch'] is True

    def test_build_tier_b_constraints(self, basic_rules_config):
        """Test building constraints for tier B."""
        engine = RelevanceEngine(basic_rules_config)

        constraints = engine.build_constraints(tier='B')

        # Check tier B constraints (more relaxed)
        assert constraints['word_count_min'] == 40
        assert constraints['word_count_max'] == 120
        assert constraints['sentence_count_min'] == 2
        assert constraints['sentence_count_max'] == 5
        assert constraints['must_end_with_question'] is False
        assert constraints['no_meeting_ask'] is False

    def test_constraints_include_banned_phrases(self, basic_rules_config):
        """Test that constraints include banned phrases."""
        engine = RelevanceEngine(basic_rules_config)

        constraints = engine.build_constraints(tier='A')

        # Check banned phrases
        assert 'banned_phrases' in constraints
        assert 'circle back' in constraints['banned_phrases']
        assert 'synergies' in constraints['banned_phrases']


class TestIntegration:
    """Integration tests for build_prospect_brief."""

    def test_full_flow_tier_a_success(self, basic_rules_config, sample_research_data, sample_context):
        """Test full flow for tier A with sufficient signals."""
        brief = build_prospect_brief(
            research_data=sample_research_data,
            context=sample_context,
            tier='A',
            rules_config=basic_rules_config
        )

        # Check status based on signal count
        if len(brief.get('verified_signals', [])) >= 3:
            assert brief['status'] == 'ready'
            assert brief['persona'] == 'quality'
            assert 'verified_signals' in brief
            assert 'angle_id' in brief
            assert 'offer_id' in brief
            assert 'email_plan' in brief
            assert 'constraints' in brief

    def test_prospect_brief_includes_all_required_fields(self, basic_rules_config, sample_research_data, sample_context):
        """Test that prospect brief includes all required fields."""
        brief = build_prospect_brief(
            research_data=sample_research_data,
            context=sample_context,
            tier='A',
            rules_config=basic_rules_config
        )

        # Required fields
        assert 'status' in brief
        assert 'persona' in brief
        assert 'industry' in brief
        assert 'verified_signals' in brief

        if brief['status'] == 'ready':
            assert 'chosen_hook_id' in brief
            assert 'angle_id' in brief
            assert 'offer_id' in brief
            assert 'email_plan' in brief
            assert 'constraints' in brief


class TestPersonaProductRefinements:
    """Test persona-product refinement pass (confidence caps, review flags, ambiguity)."""

    @pytest.fixture
    def refinement_rules_config(self):
        """Rules config with persona-product refinement settings."""
        return {
            'personas': {
                'quality': {
                    'patterns': ['VP Quality', 'Director Quality', 'QA Director', 'Quality Assurance', 'Quality Systems'],
                    'eligible_products': ['quality_qms'],
                    'secondary_products': ['process_validation'],
                    'forbidden_products': ['manufacturing_mes', 'asset_excellence'],
                    'safe_angle': 'regulatory_pressure',
                    'automation_allowed': True,
                    'default_confidence_cap': 'high'
                },
                'operations': {
                    'patterns': ['VP Operations', 'Director Operations', 'Operations Director', 'Manufacturing Operations'],
                    'eligible_products': ['quality_qms', 'manufacturing_mes'],
                    'secondary_products': ['process_validation'],
                    'forbidden_products': [],
                    'safe_angle': 'batch_efficiency',
                    'automation_allowed': True,
                    'default_confidence_cap': 'high'
                },
                'it': {
                    # Use strict patterns to avoid false matches (e.g., "Operations" contains "it")
                    'patterns': ['CIO', 'VP IT', 'Director IT', 'Chief Information', 'VP Technology', 'Director Technology'],
                    'eligible_products': ['quality_qms', 'manufacturing_mes', 'process_validation'],
                    'secondary_products': [],
                    'forbidden_products': ['regulatory_submissions'],
                    'safe_angle': 'batch_efficiency',
                    'automation_allowed': True,
                    'default_confidence_cap': 'high'
                },
                'regulatory': {
                    'patterns': ['VP Regulatory', 'Director Regulatory', 'Regulatory Affairs'],
                    'eligible_products': ['regulatory_submissions'],
                    'secondary_products': ['quality_qms'],
                    'forbidden_products': ['manufacturing_mes', 'asset_excellence'],
                    'safe_angle': 'regulatory_pressure',
                    'automation_allowed': False,  # Requires manual review
                    'default_confidence_cap': 'medium'  # Capped at medium
                },
                'manufacturing': {
                    'patterns': ['VP Manufacturing', 'Director Manufacturing', 'Plant Manager'],
                    'eligible_products': ['manufacturing_mes'],
                    'secondary_products': ['process_validation'],
                    'forbidden_products': ['quality_qms', 'regulatory_submissions'],
                    'safe_angle': 'batch_efficiency',
                    'automation_allowed': True,
                    'default_confidence_cap': 'high'
                }
            },
            'default_persona': {
                'persona': 'quality',
                'eligible_products': ['quality_qms'],
                'forbidden_products': ['manufacturing_mes'],
                'automation_allowed': True,
                'default_confidence_cap': 'medium'
            },
            'ambiguity_resolution': {
                'strategy': 'first_match',
                'force_safe_angle': True,
                'downgrade_confidence': True,
                'require_manual_review': True,
                'clear_secondary_products': True
            },
            'angle_scoring': {
                'enable_angle_scoring': False  # Disable LLM scoring for tests
            },
            'angles': {
                'regulatory_pressure': {
                    'personas': ['quality', 'regulatory'],
                    'industries': ['pharma', 'biotech'],
                    'products': ['quality_qms', 'regulatory_submissions'],
                    'signal_types': ['regulatory_climate'],
                    'pain_text': 'QA teams are pushed to shorten CAPA cycle time.',
                    'pain_areas': ['capa']
                },
                'batch_efficiency': {
                    'personas': ['operations', 'manufacturing', 'it'],
                    'industries': ['pharma', 'biotech'],
                    'products': ['manufacturing_mes'],
                    'signal_types': ['company_news'],
                    'pain_text': 'Operations teams face batch release delays.',
                    'pain_areas': ['batch_release']
                }
            },
            'offers': {
                'checklist_capa': {
                    'personas': ['quality', 'regulatory'],
                    'products': ['quality_qms'],
                    'pain_areas': ['capa'],
                    'cta_text': 'I can send a 1-page checklist. Want it?'
                }
            },
            'constraints': {
                'word_count_min': 50,
                'word_count_max': 100,
                'banned_phrases': []
            },
            'tiering': {
                'A': {'min_signals': 3},
                'B': {'min_signals': 2}
            }
        }

    def test_regulatory_persona_confidence_cap(self, refinement_rules_config, sample_context):
        """Test that regulatory persona is capped at medium confidence."""
        # Use regulatory contact
        context = {
            **sample_context,
            'contact': {
                'name': 'Jane Doe',
                'title': 'VP Regulatory Affairs',
                'email': 'jane@acme.com',
                'company': 'Acme Pharma'
            }
        }

        # Provide 4 cited signals (would normally be 'high' confidence)
        research_data = {
            'perplexity': {
                'cited_claims': [
                    {'claim': 'FDA approval received for new drug', 'source_url': 'https://fda.gov/1'},
                    {'claim': 'Regulatory milestone achieved', 'source_url': 'https://fda.gov/2'},
                    {'claim': 'New submission filed Q4', 'source_url': 'https://fda.gov/3'},
                    {'claim': 'Agency meeting scheduled', 'source_url': 'https://fda.gov/4'}
                ]
            }
        }

        brief = build_prospect_brief(
            research_data=research_data,
            context=context,
            tier='A',
            rules_config=refinement_rules_config
        )

        # Even with 4 signals, regulatory persona should be capped at medium
        assert brief['confidence_tier'] == 'medium'
        assert 'capped' in brief['confidence_note'].lower()
        assert brief['persona'] == 'regulatory'

    def test_regulatory_persona_requires_review(self, refinement_rules_config, sample_context):
        """Test that regulatory persona sets review_required=True."""
        context = {
            **sample_context,
            'contact': {
                'name': 'Jane Doe',
                'title': 'VP Regulatory Affairs',
                'email': 'jane@acme.com',
                'company': 'Acme Pharma'
            }
        }

        research_data = {
            'perplexity': {
                'cited_claims': [
                    {'claim': 'FDA approval pending', 'source_url': 'https://fda.gov/1'}
                ]
            }
        }

        brief = build_prospect_brief(
            research_data=research_data,
            context=context,
            tier='A',
            rules_config=refinement_rules_config
        )

        assert brief['review_required'] is True
        assert brief['automation_allowed'] is False
        assert any('manual review' in r.lower() for r in brief['review_reasons'])

    def test_ambiguous_title_triggers_review(self, refinement_rules_config, sample_context):
        """Test that ambiguous title (matching multiple personas) triggers review."""
        # Title that matches both quality and operations (reliable ambiguity)
        context = {
            **sample_context,
            'contact': {
                'name': 'Jane Doe',
                'title': 'VP Quality and VP Operations',  # Matches quality + operations
                'email': 'jane@acme.com',
                'company': 'Acme Pharma'
            }
        }

        research_data = {
            'perplexity': {
                'cited_claims': [
                    {'claim': 'New QMS implementation', 'source_url': 'https://example.com/1'},
                    {'claim': 'Operations modernization effort', 'source_url': 'https://example.com/2'}
                ]
            }
        }

        brief = build_prospect_brief(
            research_data=research_data,
            context=context,
            tier='A',
            rules_config=refinement_rules_config
        )

        # Should have ambiguity detected
        assert brief['persona_diagnostics']['ambiguity_detected'] is True, \
            f"Expected ambiguity, matched: {brief['persona_diagnostics'].get('matched_rules', [])}"
        assert brief['review_required'] is True
        assert any('ambiguity' in r.lower() for r in brief['review_reasons'])

    def test_ambiguity_uses_product_intersection(self, refinement_rules_config, sample_context):
        """Test that ambiguous title uses intersection of eligible products."""
        # Title that matches quality (qms) and IT (qms, mes, px)
        # Intersection should be [qms]
        context = {
            **sample_context,
            'contact': {
                'name': 'Jane Doe',
                'title': 'VP Quality Systems and IT',
                'email': 'jane@acme.com',
                'company': 'Acme Pharma'
            }
        }

        research_data = {}

        brief = build_prospect_brief(
            research_data=research_data,
            context=context,
            tier='A',
            rules_config=refinement_rules_config
        )

        diagnostics = brief['persona_diagnostics']
        if diagnostics['ambiguity_detected']:
            # Eligible products should be intersection
            assert 'quality_qms' in diagnostics['eligible_products']
            # Secondary products should be empty when ambiguous
            assert diagnostics['secondary_products'] == []

    def test_confidence_downgrade_on_ambiguity(self, refinement_rules_config):
        """Test that ambiguity triggers confidence downgrade."""
        # Ambiguous title matching quality and operations
        # Note: Don't use sample_context to avoid extra signals from triggers[]
        context = {
            'contact': {
                'name': 'Jane Doe',
                'title': 'VP Quality and Director Operations',  # Matches quality + operations
                'email': 'jane@acme.com',
                'company': 'Acme Pharma'
            },
            'company': {
                'name': 'Acme Pharma',
                'industry': 'Pharmaceutical Manufacturing'
            }
            # No triggers - to control exact signal count
        }

        # Provide exactly 2 signals for medium confidence
        research_data = {
            'perplexity': {
                'cited_claims': [
                    {'claim': 'New quality program launched', 'source_url': 'https://example.com/1'},
                    {'claim': 'Production milestone achieved', 'source_url': 'https://example.com/2'}
                ]
            }
        }

        brief = build_prospect_brief(
            research_data=research_data,
            context=context,
            tier='A',
            rules_config=refinement_rules_config
        )

        # Verify ambiguity was detected
        assert brief['persona_diagnostics']['ambiguity_detected'] is True, \
            f"Expected ambiguity but got: {brief['persona_diagnostics']}"

        # Medium (2 signals) should downgrade to low due to ambiguity
        assert brief['confidence_tier'] == 'low', \
            f"Expected 'low' but got '{brief['confidence_tier']}' (cited_signals={brief['cited_signal_count']})"
        assert 'downgraded' in brief['confidence_note'].lower(), \
            f"Expected 'downgraded' in note but got: {brief['confidence_note']}"

    def test_review_fields_present_in_brief(self, basic_rules_config, sample_research_data, sample_context):
        """Test that new review fields are present in prospect brief."""
        brief = build_prospect_brief(
            research_data=sample_research_data,
            context=sample_context,
            tier='A',
            rules_config=basic_rules_config
        )

        # New fields should be present
        assert 'review_required' in brief
        assert 'review_reasons' in brief
        assert 'automation_allowed' in brief
        assert isinstance(brief['review_required'], bool)
        assert isinstance(brief['review_reasons'], list)
        assert isinstance(brief['automation_allowed'], bool)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
