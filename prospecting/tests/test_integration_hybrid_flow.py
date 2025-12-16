#!/usr/bin/env python3
"""
Integration test for hybrid email generation flow

Tests the complete end-to-end flow:
1. Research data → Relevance engine → Prospect brief
2. Prospect brief → Email assembler → Email plan
3. Email plan → LLM renderer → Variants (mocked)
4. Variants → Validators → Final output

Usage:
    python3 tests/test_integration_hybrid_flow.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from unittest.mock import Mock, patch
import json

from src.hybrid_email_generator import HybridEmailGenerator, format_email_output


class TestHybridFlowIntegration(unittest.TestCase):
    """Integration tests for complete hybrid email generation flow."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample research data (typical structure from research_orchestrator)
        self.research_data = {
            'contact': {
                'first_name': 'John',
                'last_name': 'Smith',
                'title': 'VP Quality',
                'email': 'john.smith@acme.com',
                'company': 'Acme Pharma'
            },
            'company': {
                'name': 'Acme Pharma',
                'industry': 'Pharmaceutical Manufacturing',
                'size': '500-1000',
                'revenue': '$100M-$500M'
            },
            'perplexity': {
                'recent_news': [
                    {
                        'title': 'Acme Pharma expands CAPA program',
                        'url': 'https://example.com/news1',
                        'date': '2024-11-15',
                        'summary': 'Company investing in quality systems'
                    },
                    {
                        'title': 'FDA inspection upcoming',
                        'url': 'https://example.com/news2',
                        'date': '2024-12-01',
                        'summary': 'Acme preparing for FDA visit'
                    }
                ]
            },
            'webfetch': {
                'industries': ['Pharmaceutical Manufacturing'],
                'tech_stack': ['SAP', 'Oracle', 'Excel']
            }
        }

        # Mock voice references
        self.voice_refs = {
            'persona': 'Sales Rep - consultative seller',
            'style': 'Short, plain English. Mobile-friendly.',
            'binary_questions': 'Want X, or not a priority?'
        }

    def test_hybrid_flow_tier_a_success(self):
        """Test successful hybrid flow with Tier A (3+ signals)."""
        generator = HybridEmailGenerator(
            mode='hybrid',
            tier='A',
            fallback='legacy'
        )

        # Mock LLM renderer to avoid API calls
        mock_renderer = Mock()
        mock_renderer.render_variants.return_value = [
            {
                'subject': 'CAPA backlog',
                'body': 'FDA inspections are getting more detailed. QA teams are pushed to shorten CAPA cycle time, but manual handoffs keep approvals slow. How are you measuring deviation cycle time today? I can send a 1-page checklist. Want it?',
                'used_signal_ids': ['signal_001', 'signal_002'],
                'attempt': 0
            }
        ]
        generator._llm_renderer = mock_renderer

        result = generator.generate(
            research_data=self.research_data,
            voice_refs=self.voice_refs,
            n_variants=1
        )

        # Check result structure
        self.assertEqual(result['mode'], 'hybrid')
        self.assertEqual(result['tier'], 'A')
        self.assertIn('variants', result)
        self.assertIn('prospect_brief', result)
        self.assertIn('email_plan', result)

        # Check variants
        variants = result['variants']
        self.assertGreater(len(variants), 0)

        variant = variants[0]
        self.assertIn('subject', variant)
        self.assertIn('body', variant)
        self.assertIn('validation', variant)
        self.assertIn('quality_issues', variant)

    def test_hybrid_flow_insufficient_signals(self):
        """Test hybrid flow with insufficient signals for Tier A."""
        # Research with only 1 signal (need 3 for Tier A)
        minimal_research = {
            'contact': {
                'first_name': 'Jane',
                'last_name': 'Doe',
                'title': 'Quality Manager',
                'company': 'Small Biotech'
            },
            'company': {
                'name': 'Small Biotech',
                'industry': 'Biotechnology'
            },
            'perplexity': {
                'recent_news': []  # No news
            }
        }

        generator = HybridEmailGenerator(
            mode='hybrid',
            tier='A',
            fallback='legacy'
        )

        result = generator.generate(
            research_data=minimal_research,
            voice_refs=self.voice_refs,
            n_variants=1
        )

        # Should indicate needs more research OR fallback to legacy
        self.assertIn(result['status'], ['needs_more_research', 'fallback'])

    def test_hybrid_flow_tier_b_success(self):
        """Test hybrid flow with Tier B (2+ signals, more lenient)."""
        generator = HybridEmailGenerator(
            mode='hybrid',
            tier='B',
            fallback='legacy'
        )

        # Mock LLM renderer
        mock_renderer = Mock()
        mock_renderer.render_variants.return_value = [
            {
                'subject': 'Batch release',
                'body': 'Sites are trying to cut batch release time. Is batch release a constraint right now? I can share a benchmark sheet. Want it?',
                'used_signal_ids': ['signal_001'],
                'attempt': 0
            }
        ]
        generator._llm_renderer = mock_renderer

        result = generator.generate(
            research_data=self.research_data,
            voice_refs=self.voice_refs,
            n_variants=1
        )

        self.assertEqual(result['tier'], 'B')
        self.assertIn('variants', result)

    def test_legacy_mode(self):
        """Test legacy mode (old system)."""
        generator = HybridEmailGenerator(
            mode='legacy'
        )

        result = generator.generate(
            research_data=self.research_data,
            voice_refs=self.voice_refs,
            n_variants=1
        )

        # Check legacy result structure
        self.assertEqual(result['mode'], 'legacy')
        self.assertEqual(result['status'], 'success')
        self.assertIn('variants', result)

        variant = result['variants'][0]
        self.assertIn('subject', variant)
        self.assertIn('body', variant)
        self.assertIn('stats', variant)
        self.assertIn('components', variant)

    def test_format_email_output(self):
        """Test email output formatting."""
        # Mock result
        result = {
            'mode': 'hybrid',
            'tier': 'A',
            'status': 'success',
            'variants': [
                {
                    'subject': 'CAPA backlog',
                    'body': 'Test body text with question?',
                    'used_signal_ids': ['signal_001', 'signal_002'],
                    'validation': {
                        'claim_integrity': {'passed': True},
                        'question_present': {'passed': True}
                    },
                    'quality_issues': [],
                    'passed_validation': True,
                    'passed_quality': True
                }
            ]
        }

        formatted = format_email_output(result, 'John')

        # Check formatting
        self.assertIn('John,', formatted)
        self.assertIn('CAPA backlog', formatted)
        self.assertIn('Test body text', formatted)
        self.assertIn('[Your Name]', formatted)
        self.assertIn('✓', formatted)  # Success emoji
        self.assertIn('signal_001', formatted)

    def test_format_email_output_insufficient_signals(self):
        """Test email output formatting for insufficient signals."""
        result = {
            'mode': 'hybrid',
            'tier': 'A',
            'status': 'needs_more_research',
            'variants': [],
            'signal_count': 1,
            'tier_minimum': 3
        }

        formatted = format_email_output(result, 'John')

        self.assertIn('INSUFFICIENT SIGNALS', formatted)
        self.assertIn('Found: 1', formatted)
        self.assertIn('Required: 3', formatted)

    def test_validation_integration(self):
        """Test that validators are properly integrated."""
        generator = HybridEmailGenerator(
            mode='hybrid',
            tier='A'
        )

        # Mock LLM renderer with bad output
        mock_renderer = Mock()
        mock_renderer.render_variants.return_value = [
            {
                'subject': 'Test subject line that is way too long',
                'body': 'Short body',  # Too short
                'used_signal_ids': ['nonexistent_signal'],  # Bad signal ID
                'attempt': 0
            }
        ]
        generator._llm_renderer = mock_renderer

        result = generator.generate(
            research_data=self.research_data,
            voice_refs=self.voice_refs,
            n_variants=1
        )

        variant = result['variants'][0]

        # Should have validation issues
        self.assertIn('validation', variant)
        self.assertIn('quality_issues', variant)

        # Check that validation detected issues
        passed_validation = variant.get('passed_validation', True)
        passed_quality = variant.get('passed_quality', True)

        # At least one should fail
        self.assertFalse(passed_validation or passed_quality)

    def test_multiple_variants(self):
        """Test generating multiple variants."""
        generator = HybridEmailGenerator(
            mode='hybrid',
            tier='A'
        )

        # Mock LLM renderer with 2 variants
        mock_renderer = Mock()
        mock_renderer.render_variants.return_value = [
            {
                'subject': 'Subject 1',
                'body': 'FDA inspections are more detailed now. QA teams are pushed to shorten CAPA cycle time. Is this a priority?',
                'used_signal_ids': ['signal_001'],
                'attempt': 0
            },
            {
                'subject': 'Subject 2',
                'body': 'Documentation rigor is rising. Are you measuring deviation cycle time? I can send a checklist. Want it?',
                'used_signal_ids': ['signal_002'],
                'attempt': 0
            }
        ]
        generator._llm_renderer = mock_renderer

        result = generator.generate(
            research_data=self.research_data,
            voice_refs=self.voice_refs,
            n_variants=2
        )

        self.assertEqual(len(result['variants']), 2)
        self.assertEqual(result['variants'][0]['subject'], 'Subject 1')
        self.assertEqual(result['variants'][1]['subject'], 'Subject 2')


def run_integration_test_suite():
    """Run the complete test suite."""
    print("=" * 60)
    print("Hybrid Email Generation - Integration Tests")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestHybridFlowIntegration)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✓ All integration tests passed!")
    else:
        print("✗ Some integration tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_integration_test_suite())
