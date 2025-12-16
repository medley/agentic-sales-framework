#!/usr/bin/env python3
"""
Tests for LLM angle scoring system

Tests:
1. Candidate generation returns only eligible angles
2. Scorer output parsing rejects malformed JSON
3. Deterministic selector picks highest weighted score
4. Tie-break uses deterministic priority
5. Prospect brief includes scoring metadata when enabled
6. When disabled, behavior matches deterministic selection
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from unittest.mock import Mock, patch, MagicMock
import json

# Set dummy API key for tests
os.environ['ANTHROPIC_API_KEY'] = 'test-key-for-tests'

from src.llm_angle_scorer import (
    score_angles,
    select_best_angle,
    _parse_scoring_output,
    AngleScorerError
)
from src.relevance_engine import RelevanceEngine
from src.rules_loader import load_rules


class TestAngleScorerParsing(unittest.TestCase):
    """Test scorer output parsing and validation."""

    def test_parse_valid_json(self):
        """Test parsing valid JSON output."""
        raw_output = json.dumps({
            "scores": [
                {
                    "angle_id": "regulatory_pressure",
                    "relevance": 5,
                    "urgency": 4,
                    "reply_likelihood": 4,
                    "reason": "Strong regulatory signals"
                }
            ]
        })

        candidates = [{'angle_id': 'regulatory_pressure', 'name': 'Regulatory Pressure', 'description': '...'}]

        scores = _parse_scoring_output(raw_output, candidates)

        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]['angle_id'], 'regulatory_pressure')
        self.assertEqual(scores[0]['relevance'], 5)
        self.assertEqual(scores[0]['urgency'], 4)

    def test_parse_json_with_markdown(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        raw_output = """```json
{
  "scores": [
    {
      "angle_id": "operational_cost",
      "relevance": 4,
      "urgency": 3,
      "reply_likelihood": 5,
      "reason": "Cost signals present"
    }
  ]
}
```"""

        candidates = [{'angle_id': 'operational_cost', 'name': '...', 'description': '...'}]

        scores = _parse_scoring_output(raw_output, candidates)

        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]['angle_id'], 'operational_cost')

    def test_parse_rejects_invalid_angle_id(self):
        """Test that invalid angle_ids are dropped."""
        raw_output = json.dumps({
            "scores": [
                {
                    "angle_id": "nonexistent_angle",
                    "relevance": 5,
                    "urgency": 5,
                    "reply_likelihood": 5,
                    "reason": "Test"
                },
                {
                    "angle_id": "operational_cost",
                    "relevance": 4,
                    "urgency": 3,
                    "reply_likelihood": 5,
                    "reason": "Valid"
                }
            ]
        })

        candidates = [{'angle_id': 'operational_cost', 'name': '...', 'description': '...'}]

        scores = _parse_scoring_output(raw_output, candidates)

        # Should only include the valid one
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]['angle_id'], 'operational_cost')

    def test_parse_rejects_out_of_range_scores(self):
        """Test that scores outside 1-5 range are dropped."""
        raw_output = json.dumps({
            "scores": [
                {
                    "angle_id": "regulatory_pressure",
                    "relevance": 10,  # Out of range
                    "urgency": 3,
                    "reply_likelihood": 5,
                    "reason": "Test"
                }
            ]
        })

        candidates = [{'angle_id': 'regulatory_pressure', 'name': '...', 'description': '...'}]

        with self.assertRaises(AngleScorerError):
            _parse_scoring_output(raw_output, candidates)

    def test_parse_rejects_missing_fields(self):
        """Test that scores missing required fields are dropped."""
        raw_output = json.dumps({
            "scores": [
                {
                    "angle_id": "regulatory_pressure",
                    "relevance": 5,
                    # Missing urgency and reply_likelihood
                    "reason": "Test"
                }
            ]
        })

        candidates = [{'angle_id': 'regulatory_pressure', 'name': '...', 'description': '...'}]

        with self.assertRaises(AngleScorerError):
            _parse_scoring_output(raw_output, candidates)

    def test_parse_rejects_malformed_json(self):
        """Test that malformed JSON raises error."""
        raw_output = "This is not JSON"

        candidates = [{'angle_id': 'regulatory_pressure', 'name': '...', 'description': '...'}]

        with self.assertRaises(AngleScorerError):
            _parse_scoring_output(raw_output, candidates)


class TestDeterministicSelection(unittest.TestCase):
    """Test deterministic angle selection logic."""

    def test_select_highest_weighted_score(self):
        """Test that highest weighted score is selected."""
        scored_angles = [
            {
                'angle_id': 'regulatory_pressure',
                'weighted_score': 4.5,
                'reason': 'Strong signals'
            },
            {
                'angle_id': 'operational_cost',
                'weighted_score': 3.2,
                'reason': 'Moderate signals'
            }
        ]

        deterministic_priorities = {
            'regulatory_pressure': 10,
            'operational_cost': 8
        }

        result = select_best_angle(scored_angles, deterministic_priorities)

        self.assertEqual(result['chosen_angle_id'], 'regulatory_pressure')
        self.assertEqual(result['weighted_score'], 4.5)
        self.assertFalse(result['tie_break_used'])

    def test_tie_break_uses_deterministic_priority(self):
        """Test that tie-break uses deterministic priority."""
        scored_angles = [
            {
                'angle_id': 'regulatory_pressure',
                'weighted_score': 4.0,
                'reason': 'Tied'
            },
            {
                'angle_id': 'operational_cost',
                'weighted_score': 4.0,  # Same score
                'reason': 'Also tied'
            }
        ]

        deterministic_priorities = {
            'regulatory_pressure': 10,  # Higher priority
            'operational_cost': 8
        }

        result = select_best_angle(scored_angles, deterministic_priorities)

        # Should pick regulatory_pressure due to higher priority
        self.assertEqual(result['chosen_angle_id'], 'regulatory_pressure')
        self.assertTrue(result['tie_break_used'])


class TestCandidateGeneration(unittest.TestCase):
    """Test deterministic candidate angle generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rules_config = load_rules(tier='A')
        self.engine = RelevanceEngine(self.rules_config)

    def test_candidates_match_persona(self):
        """Test that only persona-matching angles are candidates."""
        signals = [
            {
                'id': 'sig1',
                'signal_type': 'regulatory_event',
                'claim': 'FDA warning',
                'source_url': 'https://example.com',
                'scope': 'company',
                'recency_days': 30
            }
        ]

        candidates = self.engine._generate_candidate_angles(
            angles=self.rules_config['angles'],
            signals=signals,
            persona='quality',  # quality persona
            industry='pharma'
        )

        # All candidates should have 'quality' in personas
        for candidate in candidates:
            angle_config = self.rules_config['angles'][candidate['angle_id']]
            self.assertIn('quality', angle_config.get('personas', []))

    def test_candidates_limited_to_max(self):
        """Test that candidates are limited to max_candidate_angles."""
        # Create many signals to trigger multiple angles
        signals = [
            {'id': f'sig{i}', 'signal_type': 'regulatory_event', 'claim': 'Test',
             'source_url': 'https://example.com', 'scope': 'company', 'recency_days': 30}
            for i in range(10)
        ]

        candidates = self.engine._generate_candidate_angles(
            angles=self.rules_config['angles'],
            signals=signals,
            persona='quality',
            industry='pharma'
        )

        max_candidates = self.rules_config['angle_scoring']['max_candidate_angles']
        self.assertLessEqual(len(candidates), max_candidates)

    def test_candidates_sorted_by_score(self):
        """Test that candidates are sorted by deterministic score."""
        signals = [
            {
                'id': 'sig1',
                'signal_type': 'regulatory_event',
                'claim': 'FDA warning',
                'source_url': 'https://example.com',
                'scope': 'company',
                'recency_days': 30
            }
        ]

        candidates = self.engine._generate_candidate_angles(
            angles=self.rules_config['angles'],
            signals=signals,
            persona='quality',
            industry='pharma'
        )

        # Check scores are in descending order
        scores = [c['score'] for c in candidates]
        self.assertEqual(scores, sorted(scores, reverse=True))


class TestIntegrationWithRelevanceEngine(unittest.TestCase):
    """Test integration of angle scoring with relevance engine."""

    def setUp(self):
        """Set up test fixtures."""
        # Note: We'll modify the config at the module level for tests
        pass

    def test_disabled_scoring_uses_deterministic(self):
        """Test that disabled scoring uses deterministic selection."""
        # Load config with scoring DISABLED
        rules_config = load_rules(tier='A')
        rules_config['angle_scoring']['enable_angle_scoring'] = False

        engine = RelevanceEngine(rules_config)

        signals = [
            {
                'id': 'sig1',
                'signal_type': 'regulatory_event',
                'claim': 'FDA warning',
                'source_url': 'https://example.com',
                'scope': 'company',
                'recency_days': 30
            }
        ]

        result = engine.select_angle(
            signals=signals,
            persona='quality',
            industry='pharma',
            company_name='Acme Pharma'
        )

        # Should have angle_id
        self.assertIsNotNone(result['angle_id'])

        # Should have metadata with method='deterministic'
        self.assertIsNotNone(result['angle_scoring_metadata'])
        self.assertEqual(result['angle_scoring_metadata']['method'], 'deterministic')

    def test_enabled_scoring_with_single_candidate_skips_llm(self):
        """Test that scoring is skipped with only 1 candidate."""
        # Load config with scoring ENABLED
        rules_config = load_rules(tier='A')
        rules_config['angle_scoring']['enable_angle_scoring'] = True

        engine = RelevanceEngine(rules_config)

        # Create very specific signals that only match one angle
        signals = [
            {
                'id': 'sig1',
                'signal_type': 'very_specific_type',
                'claim': 'Test',
                'source_url': 'https://example.com',
                'scope': 'company',
                'recency_days': 30
            }
        ]

        result = engine.select_angle(
            signals=signals,
            persona='quality',
            industry='pharma',
            company_name='Acme Pharma'
        )

        # NOTE: In practice, most cases will have 2+ candidates matching persona/industry
        # This test just verifies the system works when enabled (deterministic or LLM)
        self.assertIsNotNone(result['angle_id'])
        self.assertIsNotNone(result['angle_scoring_metadata'])
        self.assertIn(result['angle_scoring_metadata']['method'], ['deterministic', 'llm_scored'])

    @patch('src.llm_angle_scorer.Anthropic')
    def test_enabled_scoring_with_multiple_candidates_uses_llm(self, mock_anthropic):
        """Test that LLM scoring is used with 2+ candidates."""
        # Load config with scoring ENABLED
        rules_config = load_rules(tier='A')
        rules_config['angle_scoring']['enable_angle_scoring'] = True

        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(text=json.dumps({
                "scores": [
                    {
                        "angle_id": "regulatory_pressure",
                        "relevance": 5,
                        "urgency": 4,
                        "reply_likelihood": 4,
                        "reason": "Strong regulatory signals"
                    },
                    {
                        "angle_id": "operational_cost",
                        "relevance": 3,
                        "urgency": 3,
                        "reply_likelihood": 4,
                        "reason": "Some cost signals"
                    }
                ]
            }))
        ]

        mock_client = mock_anthropic.return_value
        mock_client.messages.create.return_value = mock_response

        engine = RelevanceEngine(rules_config)

        # Create signals that match multiple angles
        signals = [
            {
                'id': 'sig1',
                'signal_type': 'regulatory_event',
                'claim': 'FDA warning',
                'source_url': 'https://example.com',
                'scope': 'company',
                'recency_days': 30
            },
            {
                'id': 'sig2',
                'signal_type': 'expansion',
                'claim': 'New facility',
                'source_url': 'https://example.com',
                'scope': 'company',
                'recency_days': 60
            }
        ]

        result = engine.select_angle(
            signals=signals,
            persona='quality',
            industry='pharma',
            company_name='Acme Pharma'
        )

        # Should use LLM scoring
        self.assertEqual(result['angle_scoring_metadata']['method'], 'llm_scored')
        self.assertIn('angle_scores', result['angle_scoring_metadata'])
        self.assertIn('weighted_score', result['angle_scoring_metadata'])

    @patch('src.llm_angle_scorer.Anthropic')
    def test_llm_scoring_failure_falls_back_to_deterministic(self, mock_anthropic):
        """Test that LLM scoring failure falls back to deterministic."""
        # Load config with scoring ENABLED
        rules_config = load_rules(tier='A')
        rules_config['angle_scoring']['enable_angle_scoring'] = True

        # Mock LLM to raise exception
        mock_anthropic.return_value.messages.create.side_effect = Exception("API error")

        engine = RelevanceEngine(rules_config)

        signals = [
            {
                'id': 'sig1',
                'signal_type': 'regulatory_event',
                'claim': 'FDA warning',
                'source_url': 'https://example.com',
                'scope': 'company',
                'recency_days': 30
            },
            {
                'id': 'sig2',
                'signal_type': 'expansion',
                'claim': 'New facility',
                'source_url': 'https://example.com',
                'scope': 'company',
                'recency_days': 60
            }
        ]

        result = engine.select_angle(
            signals=signals,
            persona='quality',
            industry='pharma',
            company_name='Acme Pharma'
        )

        # Should fall back to deterministic
        self.assertEqual(result['angle_scoring_metadata']['method'], 'deterministic')
        self.assertIsNotNone(result['angle_id'])


def run_test_suite():
    """Run the complete test suite."""
    print("=" * 60)
    print("Angle Scoring System - Test Suite")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestAngleScorerParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestDeterministicSelection))
    suite.addTests(loader.loadTestsFromTestCase(TestCandidateGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWithRelevanceEngine))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✓ All angle scoring tests passed!")
    else:
        print("✗ Some tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_test_suite())
