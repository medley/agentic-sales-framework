"""
Tests for Validator Fixes - Verification Report Implementation

Tests the four minimum fixes from the verification report:
1. YAML confidence mode rule enforcement (forbid_numbers, forbid_named_entities)
2. Semantic guard tightening (50% coverage, 2 absolute minimum)
3. Citation format validation (warning on missing citations)
4. Terminology rename (cited_signals, citability)

Run with: pytest tests/test_validators_fixes.py -v
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from validators import (
    validate_confidence_mode_rules,
    validate_semantic_guard,
    validate_source_type,
    validate_all,
    load_validation_rules_from_yaml,
    load_semantic_guard_config,
    get_cited_signals_for_claims,
    DEFAULT_CONFIDENCE_MODES,
    DEFAULT_SEMANTIC_GUARD
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_rules_config():
    """Sample rules config matching base_config.yaml structure."""
    return {
        'confidence_modes': {
            'validation_rules': {
                'high': {
                    'max_used_signal_ids': 2,
                    'forbid_company_name_mentions': False,
                    'forbid_numbers': False,
                    'forbid_named_entities': False,
                    'require_source_type': ['public_url', 'user_provided']
                },
                'medium': {
                    'max_used_signal_ids': 1,
                    'forbid_company_name_mentions': False,
                    'forbid_numbers': True,
                    'forbid_named_entities': True,
                    'require_source_type': ['public_url', 'user_provided']
                },
                'low': {
                    'max_used_signal_ids': 1,
                    'forbid_company_name_mentions': True,
                    'forbid_numbers': True,
                    'forbid_named_entities': True,
                    'require_source_type': []
                },
                'generic': {
                    'max_used_signal_ids': 0,
                    'forbid_company_name_mentions': True,
                    'forbid_numbers': True,
                    'forbid_named_entities': True,
                    'require_source_type': []
                }
            }
        },
        'semantic_guard': {
            'min_term_coverage': 0.5,
            'min_absolute_terms': 2,
            'max_key_terms_per_signal': 10,
            'min_key_term_length': 3
        }
    }


@pytest.fixture
def cited_signal_with_terms():
    """Signal with citability='cited' and key terms."""
    return {
        'id': 'signal_001',
        'claim': 'Company announced $50M expansion of Boston manufacturing facility',
        'source_url': 'https://example.com/news/expansion',
        'source_type': 'public_url',
        'citability': 'cited',
        'verifiability': 'cited',  # Backward compat
        'key_terms': ['Company', 'announced', '50M', 'expansion', 'Boston', 'manufacturing', 'facility']
    }


@pytest.fixture
def uncited_signal():
    """Signal with citability='uncited' (vendor data)."""
    return {
        'id': 'signal_002',
        'claim': 'Uses SAP for ERP system',
        'source_url': '',
        'source_type': 'vendor_data',
        'citability': 'uncited',
        'verifiability': 'uncited',
        'key_terms': ['SAP', 'ERP']
    }


# =============================================================================
# Fix #1: YAML Confidence Mode Rule Enforcement
# =============================================================================

class TestConfidenceModeRuleEnforcement:
    """Test that YAML rules are actually enforced by validators."""

    def test_forbid_numbers_in_medium_mode(self, sample_rules_config):
        """Medium mode should reject emails containing specific numbers."""
        variant = {
            'subject': 'CAPA backlog',
            'body': 'Similar companies reduced CAPA cycle time by 40% in Q3 using this approach.',
            'used_signal_ids': ['signal_001']
        }

        issues = validate_confidence_mode_rules(
            variant=variant,
            cited_signals=[],
            confidence_mode='medium',
            company_name='Acme Pharma',
            rules_config=sample_rules_config
        )

        assert len(issues) > 0
        assert any('40%' in issue or 'number' in issue.lower() for issue in issues)

    def test_forbid_numbers_allows_high_mode(self, sample_rules_config):
        """High mode should allow numbers."""
        variant = {
            'subject': 'CAPA backlog',
            'body': 'Similar companies reduced CAPA cycle time by 40% in Q3 using this approach.',
            'used_signal_ids': ['signal_001']
        }

        issues = validate_confidence_mode_rules(
            variant=variant,
            cited_signals=[],
            confidence_mode='high',
            company_name='Acme Pharma',
            rules_config=sample_rules_config
        )

        # Should not have number-related issues
        number_issues = [i for i in issues if 'number' in i.lower() or '%' in i]
        assert len(number_issues) == 0

    def test_forbid_named_entities_in_medium_mode(self, sample_rules_config):
        """Medium mode should reject named entities like 'Project Apollo'."""
        variant = {
            'subject': 'Quality initiative',
            'body': 'Given your Project Apollo initiative, many teams face similar challenges.',
            'used_signal_ids': []
        }

        issues = validate_confidence_mode_rules(
            variant=variant,
            cited_signals=[],
            confidence_mode='medium',
            company_name='Acme Pharma',
            rules_config=sample_rules_config
        )

        assert len(issues) > 0
        assert any('Project Apollo' in issue or 'named entity' in issue.lower() for issue in issues)

    def test_forbid_company_name_in_low_mode(self, sample_rules_config):
        """Low mode should reject company name mentions."""
        variant = {
            'subject': 'Quality challenges',
            'body': 'At Acme Pharma, teams often struggle with CAPA backlogs.',
            'used_signal_ids': []
        }

        issues = validate_confidence_mode_rules(
            variant=variant,
            cited_signals=[],
            confidence_mode='low',
            company_name='Acme Pharma',
            rules_config=sample_rules_config
        )

        assert len(issues) > 0
        assert any('Acme Pharma' in issue or 'company name' in issue.lower() for issue in issues)

    def test_generic_mode_max_signal_ids_zero(self, sample_rules_config):
        """Generic mode should reject any used_signal_ids."""
        variant = {
            'subject': 'Industry trends',
            'body': 'Many pharma teams face validation challenges. Want a checklist?',
            'used_signal_ids': ['signal_001']  # Should not be allowed
        }

        issues = validate_confidence_mode_rules(
            variant=variant,
            cited_signals=[],
            confidence_mode='generic',
            company_name=None,
            rules_config=sample_rules_config
        )

        assert len(issues) > 0
        assert any('signal' in issue.lower() or 'maximum' in issue.lower() for issue in issues)

    def test_rules_loaded_from_yaml(self, sample_rules_config):
        """Verify rules are loaded from YAML config, not hardcoded."""
        rules = load_validation_rules_from_yaml(sample_rules_config)

        assert 'high' in rules
        assert 'medium' in rules
        assert 'low' in rules
        assert 'generic' in rules

        # Verify YAML-specific values
        assert rules['medium']['forbid_numbers'] == True
        assert rules['medium']['forbid_named_entities'] == True
        assert rules['low']['forbid_company_name_mentions'] == True


# =============================================================================
# Fix #2: Semantic Guard Tightening
# =============================================================================

class TestSemanticGuardTightening:
    """Test that semantic guard uses 50% coverage and 2 absolute minimum."""

    def test_semantic_guard_requires_50_percent_coverage(self, sample_rules_config, cited_signal_with_terms):
        """Semantic guard should require 50% key term coverage."""
        # Signal has 7 key terms, email only has 2 (28% coverage) - should fail
        variant = {
            'subject': 'Expansion news',
            'body': 'Given the expansion plans, quality teams often need help.',
            'used_signal_ids': ['signal_001']
        }

        issues = validate_semantic_guard(
            variant=variant,
            cited_signals=[cited_signal_with_terms],
            rules_config=sample_rules_config
        )

        assert len(issues) > 0
        assert any('coverage' in issue.lower() or 'key terms' in issue.lower() for issue in issues)

    def test_semantic_guard_requires_2_absolute_terms(self, sample_rules_config):
        """Semantic guard should require at least 2 key terms even if coverage is high."""
        # Signal with only 2 key terms, email has 1 (50% but < 2 absolute)
        signal_with_few_terms = {
            'id': 'signal_001',
            'claim': 'FDA warning',
            'source_url': 'https://example.com/fda',
            'source_type': 'public_url',
            'citability': 'cited',
            'key_terms': ['FDA', 'warning']
        }

        variant = {
            'subject': 'FDA news',
            'body': 'FDA requirements are challenging. Want help?',
            'used_signal_ids': ['signal_001']
        }

        issues = validate_semantic_guard(
            variant=variant,
            cited_signals=[signal_with_few_terms],
            rules_config=sample_rules_config
        )

        # Should pass: has 1 term (50% coverage), but might fail 2-term minimum
        # Actually 'FDA' appears, so 1/2 = 50% but only 1 term
        assert len(issues) > 0
        assert any('minimum' in issue.lower() or 'terms found' in issue.lower() for issue in issues)

    def test_semantic_guard_passes_with_sufficient_coverage(self, sample_rules_config, cited_signal_with_terms):
        """Semantic guard should pass with 50%+ coverage and 2+ terms."""
        # Signal has 7 key terms, email has 4 (57% coverage, 4 absolute) - should pass
        variant = {
            'subject': 'Boston expansion',
            'body': 'Given the Boston manufacturing expansion, facility teams need support.',
            'used_signal_ids': ['signal_001']
        }

        issues = validate_semantic_guard(
            variant=variant,
            cited_signals=[cited_signal_with_terms],
            rules_config=sample_rules_config
        )

        assert len(issues) == 0

    def test_semantic_guard_config_from_yaml(self, sample_rules_config):
        """Verify semantic guard thresholds are loaded from YAML."""
        config = load_semantic_guard_config(sample_rules_config)

        assert config['min_term_coverage'] == 0.5
        assert config['min_absolute_terms'] == 2


# =============================================================================
# Fix #3: Citation Format Validation
# =============================================================================

class TestCitationFormatValidation:
    """Test citation format warnings and confidence downgrades."""

    def test_source_type_validation_rejects_fake_urls(self, sample_rules_config):
        """Source type validation should reject Google search URLs."""
        signal_with_fake_url = {
            'id': 'signal_001',
            'claim': 'Company news',
            'source_url': 'https://www.google.com/search?q=company+news',
            'source_type': 'public_url',
            'citability': 'cited'
        }

        variant = {
            'subject': 'News',
            'body': 'Given recent news, want help?',
            'used_signal_ids': ['signal_001']
        }

        issues = validate_source_type(
            variant=variant,
            cited_signals=[signal_with_fake_url],
            confidence_mode='high',
            rules_config=sample_rules_config
        )

        assert len(issues) > 0
        assert any('google.com/search' in issue.lower() or 'fake' in issue.lower() for issue in issues)

    def test_source_type_validation_allows_real_urls(self, sample_rules_config, cited_signal_with_terms):
        """Source type validation should allow real URLs."""
        variant = {
            'subject': 'Expansion',
            'body': 'Given recent expansion, want help?',
            'used_signal_ids': ['signal_001']
        }

        issues = validate_source_type(
            variant=variant,
            cited_signals=[cited_signal_with_terms],
            confidence_mode='high',
            rules_config=sample_rules_config
        )

        # Should not have fake URL issues
        fake_url_issues = [i for i in issues if 'fake' in i.lower() or 'google.com' in i.lower()]
        assert len(fake_url_issues) == 0


# =============================================================================
# Fix #4: Terminology Rename (cited_signals, citability)
# =============================================================================

class TestTerminologyRename:
    """Test that new terminology works with backward compatibility."""

    def test_get_cited_signals_filters_correctly(self, cited_signal_with_terms, uncited_signal):
        """get_cited_signals_for_claims should filter to only cited signals."""
        all_signals = [cited_signal_with_terms, uncited_signal]

        cited_only = get_cited_signals_for_claims(all_signals)

        assert len(cited_only) == 1
        assert cited_only[0]['id'] == 'signal_001'

    def test_backward_compat_verifiability_field(self, cited_signal_with_terms):
        """Signals with old 'verifiability' field should still work."""
        # Remove new field, keep old
        old_style_signal = {
            'id': 'signal_001',
            'claim': 'Test claim',
            'source_url': 'https://example.com',
            'source_type': 'public_url',
            'verifiability': 'verified',  # Old terminology
            'key_terms': ['Test']
        }

        cited_only = get_cited_signals_for_claims([old_style_signal])

        # Should still be recognized as cited
        assert len(cited_only) == 1

    def test_validate_all_accepts_cited_signals_key(self, sample_rules_config, cited_signal_with_terms):
        """validate_all should accept cited_signals parameter."""
        variant = {
            'subject': 'Test',
            'body': 'Many teams struggle. Want help?',
            'used_signal_ids': []
        }

        result = validate_all(
            variant=variant,
            cited_signals=[cited_signal_with_terms],  # New terminology
            constraints={'must_end_with_question': True},
            confidence_mode='high',
            company_name=None,
            rules_config=sample_rules_config
        )

        assert 'passed' in result
        assert 'issues' in result


# =============================================================================
# Integration Tests
# =============================================================================

class TestValidatorIntegration:
    """Integration tests for full validation pipeline."""

    def test_full_validation_high_confidence_valid(self, sample_rules_config, cited_signal_with_terms):
        """Valid high-confidence email should pass all validators."""
        variant = {
            'subject': 'Boston expansion',
            'body': 'Given the Boston manufacturing expansion, many facility teams need support with quality systems. Want a checklist?',
            'used_signal_ids': ['signal_001']
        }

        result = validate_all(
            variant=variant,
            cited_signals=[cited_signal_with_terms],
            constraints={'must_end_with_question': True},
            confidence_mode='high',
            company_name='Acme Pharma',
            rules_config=sample_rules_config
        )

        # Check overall result
        assert result['passed'] == True or result['total_issues'] == 0

    def test_full_validation_medium_confidence_numbers_fail(self, sample_rules_config, cited_signal_with_terms):
        """Medium-confidence email with numbers should fail."""
        variant = {
            'subject': 'Quality metrics',
            'body': 'Teams using this approach reduced CAPA time by 40%. Want similar results?',
            'used_signal_ids': []
        }

        result = validate_all(
            variant=variant,
            cited_signals=[cited_signal_with_terms],
            constraints={'must_end_with_question': True},
            confidence_mode='medium',
            company_name=None,
            rules_config=sample_rules_config
        )

        assert result['passed'] == False
        assert result['total_issues'] > 0

    def test_full_validation_generic_with_signals_fail(self, sample_rules_config, cited_signal_with_terms):
        """Generic-confidence email with signal IDs should fail."""
        variant = {
            'subject': 'Industry trends',
            'body': 'Many pharma teams face challenges. Want a checklist?',
            'used_signal_ids': ['signal_001']  # Not allowed in generic
        }

        result = validate_all(
            variant=variant,
            cited_signals=[cited_signal_with_terms],
            constraints={'must_end_with_question': True},
            confidence_mode='generic',
            company_name=None,
            rules_config=sample_rules_config
        )

        assert result['passed'] == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
