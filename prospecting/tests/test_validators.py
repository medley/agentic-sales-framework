"""
Tests for Validators

Tests deterministic validation functions:
- Claim integrity validation
- Must end with question validation
- Combined validation
"""

import pytest
from src.validators import (
    validate_claim_integrity,
    validate_must_end_with_question,
    validate_all,
    ValidationError
)


@pytest.fixture
def sample_verified_signals():
    """Sample verified signals for testing."""
    return [
        {
            'id': 'signal_001',
            'claim': 'FDA increased inspection frequency by 23% in 2024',
            'source_url': 'https://example.com/fda-stats',
            'source_type': 'public_url',
            'citability': 'cited',
            'scope': 'industry_wide',
            'recency_days': 30
        },
        {
            'id': 'signal_002',
            'claim': 'QMSR enforcement deadline is February 2, 2026',
            'source_url': 'https://fda.gov/qmsr',
            'source_type': 'public_url',
            'citability': 'cited',
            'scope': 'regulatory',
            'recency_days': 180
        },
        {
            'id': 'signal_003',
            'claim': 'Industry benchmarks show 30-50% audit finding reductions with automated compliance',
            'source_url': 'https://example.com/compliance-benchmarks',
            'source_type': 'public_url',
            'citability': 'cited',
            'scope': 'industry',
            'recency_days': 90
        }
    ]


@pytest.fixture
def sample_constraints():
    """Sample constraints for testing."""
    return {
        'word_count_min': 50,
        'word_count_max': 100,
        'sentence_count_min': 3,
        'sentence_count_max': 4,
        'subject_word_max': 4,
        'must_end_with_question': True,
        'no_meeting_ask': True,
        'no_product_pitch': True
    }


class TestClaimIntegrityValidation:
    """Test suite for claim integrity validation."""

    def test_valid_signal_ids_pass(self, sample_verified_signals):
        """Test that valid signal IDs pass validation."""
        variant = {
            'subject': 'Test Subject',
            'body': 'Test body with FDA claim.',
            'used_signal_ids': ['signal_001', 'signal_002']
        }

        issues = validate_claim_integrity(variant, sample_verified_signals)

        assert len(issues) == 0

    def test_single_valid_signal_passes(self, sample_verified_signals):
        """Test that single valid signal ID passes."""
        variant = {
            'subject': 'Test',
            'body': 'Body',
            'used_signal_ids': ['signal_001']
        }

        issues = validate_claim_integrity(variant, sample_verified_signals)
        assert len(issues) == 0

    def test_all_valid_signals_pass(self, sample_verified_signals):
        """Test that all valid signal IDs pass."""
        variant = {
            'subject': 'Test',
            'body': 'Body',
            'used_signal_ids': ['signal_001', 'signal_002', 'signal_003']
        }

        issues = validate_claim_integrity(variant, sample_verified_signals)
        assert len(issues) == 0

    def test_empty_signal_ids_pass(self, sample_verified_signals):
        """Test that empty signal IDs list passes (no claims)."""
        variant = {
            'subject': 'Test',
            'body': 'Generic body with no specific claims.',
            'used_signal_ids': []
        }

        issues = validate_claim_integrity(variant, sample_verified_signals)
        assert len(issues) == 0

    def test_missing_signal_id_fails(self, sample_verified_signals):
        """Test that missing signal ID fails validation."""
        variant = {
            'subject': 'Test',
            'body': 'Body with invalid claim reference',
            'used_signal_ids': ['signal_999']
        }

        issues = validate_claim_integrity(variant, sample_verified_signals)

        assert len(issues) == 1
        assert 'signal_999' in issues[0]
        assert 'not found' in issues[0].lower()

    def test_multiple_missing_signal_ids_fail(self, sample_verified_signals):
        """Test that multiple missing signal IDs all reported."""
        variant = {
            'subject': 'Test',
            'body': 'Body',
            'used_signal_ids': ['signal_001', 'signal_999', 'signal_888']
        }

        issues = validate_claim_integrity(variant, sample_verified_signals)

        assert len(issues) == 1
        assert 'signal_999' in issues[0]
        assert 'signal_888' in issues[0]

    def test_mix_of_valid_and_invalid_signal_ids(self, sample_verified_signals):
        """Test mix of valid and invalid signal IDs."""
        variant = {
            'subject': 'Test',
            'body': 'Body',
            'used_signal_ids': ['signal_001', 'signal_invalid', 'signal_002']
        }

        issues = validate_claim_integrity(variant, sample_verified_signals)

        assert len(issues) == 1
        assert 'signal_invalid' in issues[0]
        # Valid signals should not be mentioned
        assert 'signal_001' not in issues[0]
        assert 'signal_002' not in issues[0]

    def test_invalid_signal_ids_format(self, sample_verified_signals):
        """Test handling of invalid signal IDs format."""
        variant = {
            'subject': 'Test',
            'body': 'Body',
            'used_signal_ids': 'not_a_list'  # Invalid format
        }

        issues = validate_claim_integrity(variant, sample_verified_signals)

        assert len(issues) == 1
        assert 'invalid' in issues[0].lower()
        assert 'format' in issues[0].lower()

    def test_missing_used_signal_ids_field(self, sample_verified_signals):
        """Test handling of missing used_signal_ids field."""
        variant = {
            'subject': 'Test',
            'body': 'Body'
            # No used_signal_ids field
        }

        issues = validate_claim_integrity(variant, sample_verified_signals)

        # Should treat as empty list (no claims)
        assert len(issues) == 0

    def test_empty_verified_signals_list(self):
        """Test validation against empty verified signals list."""
        variant = {
            'subject': 'Test',
            'body': 'Body',
            'used_signal_ids': ['signal_001']
        }

        issues = validate_claim_integrity(variant, [])

        assert len(issues) == 1
        assert 'signal_001' in issues[0]


class TestMustEndWithQuestionValidation:
    """Test suite for must end with question validation."""

    def test_ends_with_yes_no_question_passes(self):
        """Test that body ending with yes/no question passes."""
        bodies = [
            "This is a test. Want it?",
            "Here's some info. Should I send more?",
            "Context here. Are you interested?",
            "Details provided. Open to discussing?",
            "Info about topic. Does this make sense?",
            "Some context. Want to learn more, or not?",
            "Background provided. Is this helpful, or already covered?"
        ]

        for body in bodies:
            issues = validate_must_end_with_question(body)
            assert len(issues) == 0, f"Failed for: {body}"

    def test_ends_with_non_yes_no_question_fails(self):
        """Test that non-yes/no questions fail (or warn)."""
        bodies = [
            "Context here. What do you think?",
            "Some info. How are you handling this?",
            "Details. When can we discuss?",
            "Background. Where should we start?"
        ]

        for body in bodies:
            issues = validate_must_end_with_question(body)
            # These should have issues (not yes/no questions)
            assert len(issues) > 0, f"Should fail for: {body}"

    def test_no_question_mark_fails(self):
        """Test that body without question mark fails."""
        body = "This is a statement. No question here."

        issues = validate_must_end_with_question(body)

        assert len(issues) > 0
        assert 'question mark' in issues[0].lower()

    def test_question_mark_not_at_end_fails(self):
        """Test that question mark not at end fails."""
        body = "Is this a test? Yes it is."

        issues = validate_must_end_with_question(body)

        assert len(issues) > 0
        assert 'question mark' in issues[0].lower()

    def test_empty_body_fails(self):
        """Test that empty body fails."""
        issues = validate_must_end_with_question("")

        assert len(issues) > 0

    def test_whitespace_handling(self):
        """Test that trailing whitespace is handled correctly."""
        body = "Context. Want it?   \n  "

        issues = validate_must_end_with_question(body)

        assert len(issues) == 0  # Should strip whitespace


class TestValidateAll:
    """Test suite for combined validation."""

    def test_all_validations_pass(self, sample_verified_signals, sample_constraints):
        """Test when all validations pass."""
        variant = {
            'subject': 'Test Subject',
            'body': 'This is a good email with proper structure. It has verified claims. Everything looks right. Want to learn more?',
            'used_signal_ids': ['signal_001', 'signal_002']
        }

        results = validate_all(variant, sample_verified_signals, sample_constraints)

        # All validators should return empty lists
        assert results['passed'] == True
        for validator_name, issues in results['issues'].items():
            assert len(issues) == 0, f"{validator_name} had issues: {issues}"

    def test_claim_integrity_fails(self, sample_verified_signals, sample_constraints):
        """Test when claim integrity fails."""
        variant = {
            'subject': 'Test',
            'body': 'Good email body with question at end. Has multiple sentences here. All structured properly. Want it?',
            'used_signal_ids': ['signal_999']  # Invalid signal
        }

        results = validate_all(variant, sample_verified_signals, sample_constraints)

        assert len(results['issues']['claim_integrity']) > 0
        assert len(results['issues']['must_end_with_question']) == 0

    def test_must_end_with_question_fails(self, sample_verified_signals, sample_constraints):
        """Test when must end with question fails."""
        variant = {
            'subject': 'Test',
            'body': 'Good email body. Has valid signals. No question though.',
            'used_signal_ids': ['signal_001']
        }

        results = validate_all(variant, sample_verified_signals, sample_constraints)

        assert len(results['issues']['claim_integrity']) == 0
        assert len(results['issues']['must_end_with_question']) > 0

    def test_multiple_validations_fail(self, sample_verified_signals, sample_constraints):
        """Test when multiple validations fail."""
        variant = {
            'subject': 'Test',
            'body': 'Bad email. No question. Invalid signal reference.',
            'used_signal_ids': ['signal_999']
        }

        results = validate_all(variant, sample_verified_signals, sample_constraints)

        assert len(results['issues']['claim_integrity']) > 0
        assert len(results['issues']['must_end_with_question']) > 0

    def test_constraint_disabled_skips_validation(
        self,
        sample_verified_signals,
        sample_constraints
    ):
        """Test that disabled constraint skips validation."""
        variant = {
            'subject': 'Test',
            'body': 'Email without question at end.',
            'used_signal_ids': ['signal_001']
        }

        # Disable must_end_with_question
        constraints = sample_constraints.copy()
        constraints['must_end_with_question'] = False

        results = validate_all(variant, sample_verified_signals, constraints)

        # Should have no issues since constraint is disabled
        assert len(results['issues']['must_end_with_question']) == 0

    def test_returns_dict_structure(self, sample_verified_signals, sample_constraints):
        """Test that validate_all returns proper dict structure."""
        variant = {
            'subject': 'Test',
            'body': 'Test body. Multiple sentences. Good structure. Want it?',
            'used_signal_ids': []
        }

        results = validate_all(variant, sample_verified_signals, sample_constraints)

        # Check structure
        assert isinstance(results, dict)
        assert 'passed' in results
        assert 'issues' in results
        assert 'total_issues' in results
        assert 'claim_integrity' in results['issues']
        assert 'must_end_with_question' in results['issues']
        assert 'forbidden_products' in results['issues']
        assert all(isinstance(v, list) for v in results['issues'].values())


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_none_values_handled_gracefully(self):
        """Test that None values don't cause crashes."""
        variant = {
            'subject': None,
            'body': None,
            'used_signal_ids': None
        }

        # Should not crash
        issues = validate_claim_integrity(variant, [])
        assert isinstance(issues, list)

    def test_unicode_in_signal_ids(self):
        """Test handling of unicode in signal IDs."""
        signals = [
            {'id': 'signal_001_émoji', 'claim': 'Test', 'source_url': 'http://test.com'}
        ]

        variant = {
            'used_signal_ids': ['signal_001_émoji']
        }

        issues = validate_claim_integrity(variant, signals)
        assert len(issues) == 0

    def test_very_long_signal_id(self):
        """Test handling of very long signal IDs."""
        long_id = 'signal_' + 'x' * 1000

        signals = [
            {'id': long_id, 'claim': 'Test', 'source_url': 'http://test.com'}
        ]

        variant = {
            'used_signal_ids': [long_id]
        }

        issues = validate_claim_integrity(variant, signals)
        assert len(issues) == 0

    def test_duplicate_signal_ids_in_variant(self):
        """Test handling of duplicate signal IDs in variant."""
        signals = [
            {'id': 'signal_001', 'claim': 'Test', 'source_url': 'http://test.com'}
        ]

        variant = {
            'used_signal_ids': ['signal_001', 'signal_001', 'signal_001']
        }

        # Should still pass (duplicates are okay)
        issues = validate_claim_integrity(variant, signals)
        assert len(issues) == 0

    def test_signal_without_id_field(self):
        """Test handling of signal without id field."""
        signals = [
            {'claim': 'Test', 'source_url': 'http://test.com'}  # No 'id' field
        ]

        variant = {
            'used_signal_ids': ['signal_001']
        }

        issues = validate_claim_integrity(variant, signals)
        # Should fail since no valid signal IDs exist
        assert len(issues) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
