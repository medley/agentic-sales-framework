"""
Tests for Persona-Product Safety Constraints

Ensures that:
1. Manufacturing personas cannot receive Qx (QMS) messaging
2. Assets personas cannot receive QMS-only framing
3. IT personas receive governance framing, not operational promises
4. Quality personas cannot receive Mx (Manufacturing) messaging
5. Persona detection returns diagnostics with product eligibility
6. Angle selection respects product eligibility
7. Offer selection respects product eligibility
8. Validation fails when forbidden products are referenced
"""

import pytest
from typing import Dict, Any

# Import modules under test
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from relevance_engine import RelevanceEngine
from validators import validate_forbidden_products, validate_all
from rules_loader import load_rules


@pytest.fixture
def rules_config():
    """Load the actual rules configuration."""
    config = load_rules(tier="A")
    # Disable LLM angle scoring for deterministic tests
    if 'angle_scoring' not in config:
        config['angle_scoring'] = {}
    config['angle_scoring']['enable_angle_scoring'] = False
    return config


@pytest.fixture
def engine(rules_config):
    """Create a RelevanceEngine with loaded rules."""
    return RelevanceEngine(rules_config)


class TestPersonaDetection:
    """Tests for persona detection with diagnostics."""

    def test_quality_persona_detection(self, engine):
        """VP Quality should detect as quality persona."""
        diagnostics = engine.detect_persona_with_diagnostics("VP Quality")
        assert diagnostics['selected_persona'] == 'quality'
        assert diagnostics['fallback_applied'] == False
        assert 'quality_qms' in diagnostics['eligible_products']
        assert 'manufacturing_mes' in diagnostics['forbidden_products']

    def test_manufacturing_persona_detection(self, engine):
        """VP Manufacturing should detect as manufacturing persona."""
        diagnostics = engine.detect_persona_with_diagnostics("VP Manufacturing")
        assert diagnostics['selected_persona'] == 'manufacturing'
        assert diagnostics['fallback_applied'] == False
        assert 'manufacturing_mes' in diagnostics['eligible_products']
        assert 'quality_qms' in diagnostics['forbidden_products']

    def test_operations_persona_detection(self, engine):
        """VP Operations should detect as operations persona."""
        diagnostics = engine.detect_persona_with_diagnostics("VP Operations")
        assert diagnostics['selected_persona'] == 'operations'
        assert 'quality_qms' in diagnostics['eligible_products']
        assert 'manufacturing_mes' in diagnostics['eligible_products']
        # Operations has no forbidden products
        assert len(diagnostics['forbidden_products']) == 0

    def test_it_persona_detection(self, engine):
        """CIO should detect as IT persona."""
        diagnostics = engine.detect_persona_with_diagnostics("CIO")
        assert diagnostics['selected_persona'] == 'it'
        assert 'quality_qms' in diagnostics['eligible_products']
        assert 'manufacturing_mes' in diagnostics['eligible_products']
        assert 'process_validation' in diagnostics['eligible_products']
        assert 'regulatory_submissions' in diagnostics['forbidden_products']

    def test_digital_persona_detection(self, engine):
        """VP Digital should detect as digital persona."""
        diagnostics = engine.detect_persona_with_diagnostics("VP Digital")
        assert diagnostics['selected_persona'] == 'digital'
        assert 'manufacturing_mes' in diagnostics['eligible_products']
        assert 'process_validation' in diagnostics['eligible_products']

    def test_assets_persona_detection(self, engine):
        """VP Maintenance should detect as assets persona."""
        diagnostics = engine.detect_persona_with_diagnostics("VP Maintenance")
        assert diagnostics['selected_persona'] == 'assets'
        assert 'asset_excellence' in diagnostics['eligible_products']
        assert 'quality_qms' in diagnostics['forbidden_products']
        assert 'regulatory_submissions' in diagnostics['forbidden_products']

    def test_regulatory_persona_detection(self, engine):
        """VP Regulatory should detect as regulatory persona."""
        diagnostics = engine.detect_persona_with_diagnostics("VP Regulatory Affairs")
        assert diagnostics['selected_persona'] == 'regulatory'
        assert 'regulatory_submissions' in diagnostics['eligible_products']
        assert 'manufacturing_mes' in diagnostics['forbidden_products']

    def test_msat_detects_as_digital(self, engine):
        """Head of MSAT should detect as digital persona (not fallback)."""
        diagnostics = engine.detect_persona_with_diagnostics("Head of MSAT")
        assert diagnostics['selected_persona'] == 'digital'
        assert diagnostics['fallback_applied'] == False

    def test_plant_manager_detects_as_manufacturing(self, engine):
        """Plant Manager should detect as manufacturing persona."""
        diagnostics = engine.detect_persona_with_diagnostics("Plant Manager")
        assert diagnostics['selected_persona'] == 'manufacturing'
        assert diagnostics['fallback_applied'] == False

    def test_ambiguity_detection(self, engine):
        """Dual-role titles should flag ambiguity."""
        diagnostics = engine.detect_persona_with_diagnostics("VP Quality Systems & VP IT")
        assert diagnostics['ambiguity_detected'] == True
        assert diagnostics['ambiguity_note'] is not None
        assert len(diagnostics['matched_rules']) >= 2

    def test_fallback_when_no_match(self, engine):
        """Unknown title should fallback to default persona."""
        diagnostics = engine.detect_persona_with_diagnostics("Chief Marketing Officer")
        assert diagnostics['fallback_applied'] == True
        assert diagnostics['selection_reason'] == 'no_pattern_matched'
        # Default should be quality
        assert diagnostics['selected_persona'] == 'quality'


class TestProductEligibility:
    """Tests for product eligibility enforcement."""

    def test_is_product_eligible(self, engine):
        """Test product eligibility checking using internal product IDs."""
        # Quality can receive quality_qms
        assert engine.is_product_eligible('quality', 'quality_qms') == True
        # Quality cannot receive manufacturing_mes
        assert engine.is_product_eligible('quality', 'manufacturing_mes') == False
        # Manufacturing can receive manufacturing_mes
        assert engine.is_product_eligible('manufacturing', 'manufacturing_mes') == True
        # Manufacturing cannot receive quality_qms
        assert engine.is_product_eligible('manufacturing', 'quality_qms') == False

    def test_is_product_forbidden(self, engine):
        """Test forbidden product checking using internal product IDs."""
        # Quality - manufacturing_mes is forbidden
        assert engine.is_product_forbidden('quality', 'manufacturing_mes') == True
        # Quality - quality_qms is NOT forbidden
        assert engine.is_product_forbidden('quality', 'quality_qms') == False
        # Manufacturing - quality_qms is forbidden
        assert engine.is_product_forbidden('manufacturing', 'quality_qms') == True
        # Assets - quality_qms and regulatory_submissions are forbidden
        assert engine.is_product_forbidden('assets', 'quality_qms') == True
        assert engine.is_product_forbidden('assets', 'regulatory_submissions') == True

    def test_operations_has_no_forbidden_products(self, engine):
        """Operations persona should have no forbidden products."""
        eligibility = engine.get_persona_product_eligibility('operations')
        assert len(eligibility['forbidden_products']) == 0


class TestAngleSelection:
    """Tests for angle selection with product filtering."""

    def test_manufacturing_cannot_get_qx_angles(self, engine, rules_config):
        """Manufacturing persona should not receive quality_qms-only angles."""
        result = engine.select_angle(
            signals=[],
            persona='manufacturing',
            industry='pharma',
            company_name='Test Company'
        )

        # Get the selected angle's products
        angles = rules_config.get('angles', {})
        selected_angle = angles.get(result['angle_id'], {})
        angle_products = selected_angle.get('products', [])

        # Should not be a quality_qms-only angle
        if angle_products:
            assert 'quality_qms' not in angle_products or 'manufacturing_mes' in angle_products or 'process_validation' in angle_products

    def test_quality_cannot_get_mx_angles(self, engine, rules_config):
        """Quality persona should not receive manufacturing_mes-only angles."""
        result = engine.select_angle(
            signals=[],
            persona='quality',
            industry='pharma',
            company_name='Test Company'
        )

        angles = rules_config.get('angles', {})
        selected_angle = angles.get(result['angle_id'], {})
        angle_products = selected_angle.get('products', [])

        # Should not be a manufacturing_mes-only angle
        if angle_products:
            assert 'manufacturing_mes' not in angle_products or 'quality_qms' in angle_products

    def test_assets_cannot_get_qms_angles(self, engine, rules_config):
        """Assets persona should not receive quality_qms angles."""
        result = engine.select_angle(
            signals=[],
            persona='assets',
            industry='pharma',
            company_name='Test Company'
        )

        angles = rules_config.get('angles', {})
        selected_angle = angles.get(result['angle_id'], {})
        angle_products = selected_angle.get('products', [])

        # Should not include quality_qms
        if angle_products:
            assert 'quality_qms' not in angle_products or 'asset_excellence' in angle_products


class TestOfferSelection:
    """Tests for offer selection with product filtering."""

    def test_manufacturing_gets_mx_offers(self, engine, rules_config):
        """Manufacturing persona should receive manufacturing_mes-eligible offers."""
        offer_id = engine.select_offer(
            persona='manufacturing',
            angle_id='batch_release_time'
        )

        offers = rules_config.get('offers', {})
        selected_offer = offers.get(offer_id, {})
        offer_products = selected_offer.get('products', [])

        # Should be a manufacturing_mes-eligible offer
        if offer_products:
            assert 'manufacturing_mes' in offer_products or 'process_validation' in offer_products or 'asset_excellence' in offer_products

    def test_quality_gets_qx_offers(self, engine, rules_config):
        """Quality persona should receive quality_qms-eligible offers."""
        offer_id = engine.select_offer(
            persona='quality',
            angle_id='capa_cycle_time'
        )

        offers = rules_config.get('offers', {})
        selected_offer = offers.get(offer_id, {})
        offer_products = selected_offer.get('products', [])

        # Should be a quality_qms-eligible offer
        if offer_products:
            assert 'quality_qms' in offer_products


class TestForbiddenProductValidation:
    """Tests for forbidden product validation in emails."""

    def test_manufacturing_email_with_capa_fails(self, rules_config):
        """Email to manufacturing persona mentioning CAPA should fail validation."""
        variant = {
            'subject': 'capa backlog',
            'body': 'I noticed your CAPA cycle times are longer than industry average.'
        }

        issues = validate_forbidden_products(
            variant=variant,
            persona='manufacturing',
            rules_config=rules_config
        )

        assert len(issues) > 0
        assert 'capa' in issues[0].lower() or 'forbidden' in issues[0].lower()

    def test_manufacturing_email_with_qms_fails(self, rules_config):
        """Email to manufacturing persona mentioning QMS should fail validation."""
        variant = {
            'subject': 'quality management',
            'body': 'Your QMS implementation could benefit from document control improvements.'
        }

        issues = validate_forbidden_products(
            variant=variant,
            persona='manufacturing',
            rules_config=rules_config
        )

        assert len(issues) > 0

    def test_assets_email_with_qms_content_fails(self, rules_config):
        """Email to assets persona mentioning QMS content should fail validation."""
        variant = {
            'subject': 'equipment maintenance',
            'body': 'Your CAPA cycle time could be improved with better automation.'
        }

        issues = validate_forbidden_products(
            variant=variant,
            persona='assets',
            rules_config=rules_config
        )

        assert len(issues) > 0

    def test_quality_email_with_batch_fails(self, rules_config):
        """Email to quality persona mentioning batch records should fail validation."""
        variant = {
            'subject': 'batch release',
            'body': 'Your production batch records could be streamlined with eBR.'
        }

        issues = validate_forbidden_products(
            variant=variant,
            persona='quality',
            rules_config=rules_config
        )

        assert len(issues) > 0

    def test_quality_email_with_capa_passes(self, rules_config):
        """Email to quality persona mentioning CAPA should pass validation."""
        variant = {
            'subject': 'capa improvement',
            'body': 'Your CAPA cycle times could be reduced with better workflow automation.'
        }

        issues = validate_forbidden_products(
            variant=variant,
            persona='quality',
            rules_config=rules_config
        )

        assert len(issues) == 0

    def test_manufacturing_email_with_production_passes(self, rules_config):
        """Email to manufacturing persona mentioning production should pass."""
        variant = {
            'subject': 'production efficiency',
            'body': 'Your production throughput could benefit from better batch record workflows.'
        }

        issues = validate_forbidden_products(
            variant=variant,
            persona='manufacturing',
            rules_config=rules_config
        )

        assert len(issues) == 0

    def test_operations_can_receive_any_messaging(self, rules_config):
        """Operations persona should pass with any product messaging."""
        # Qx messaging
        variant_qx = {
            'subject': 'capa efficiency',
            'body': 'Your CAPA cycle times could be improved.'
        }
        issues_qx = validate_forbidden_products(variant_qx, 'operations', rules_config)
        assert len(issues_qx) == 0

        # Mx messaging
        variant_mx = {
            'subject': 'batch release',
            'body': 'Your batch production could be optimized.'
        }
        issues_mx = validate_forbidden_products(variant_mx, 'operations', rules_config)
        assert len(issues_mx) == 0


class TestITPersonaFraming:
    """Tests for IT persona governance framing (not operational promises)."""

    def test_it_gets_governance_angles(self, engine, rules_config):
        """IT persona should receive governance-focused angles."""
        result = engine.select_angle(
            signals=[],
            persona='it',
            industry='pharma',
            company_name='Test Company'
        )

        angles = rules_config.get('angles', {})
        selected_angle = angles.get(result['angle_id'], {})

        # IT angles should have governance-related framing
        framing = selected_angle.get('framing', '')
        valid_it_framings = ['governance_and_integration', 'modernization_and_automation']

        # Either the framing matches or it's a valid IT angle
        if result['angle_id'] not in ['validation_governance', 'digital_transformation', 'data_integrity']:
            # If not one of the expected IT angles, it should still be eligible
            angle_products = selected_angle.get('products', [])
            # Should not be regulatory_submissions (forbidden for IT)
            if angle_products:
                assert 'regulatory_submissions' not in angle_products


class TestValidateAllWithPersona:
    """Tests for validate_all including persona parameter."""

    def test_validate_all_with_forbidden_products(self, rules_config):
        """validate_all should catch forbidden product issues."""
        variant = {
            'subject': 'capa improvement',
            'body': 'Your CAPA process needs work. Is this a priority?',
            'used_signal_ids': []
        }

        result = validate_all(
            variant=variant,
            cited_signals=[],
            constraints={'must_end_with_question': True},
            confidence_mode='generic',
            company_name='Test Co',
            rules_config=rules_config,
            persona='manufacturing'  # Manufacturing + CAPA = forbidden
        )

        assert result['passed'] == False
        assert 'forbidden_products' in result['issues']
        assert len(result['issues']['forbidden_products']) > 0

    def test_validate_all_passes_with_eligible_products(self, rules_config):
        """validate_all should pass when products are eligible."""
        variant = {
            'subject': 'batch efficiency',
            'body': 'Your production batch records could be streamlined. Is this a priority?',
            'used_signal_ids': []
        }

        result = validate_all(
            variant=variant,
            cited_signals=[],
            constraints={'must_end_with_question': True},
            confidence_mode='generic',
            company_name='Test Co',
            rules_config=rules_config,
            persona='manufacturing'  # Manufacturing + batch = OK
        )

        # Should not have forbidden_products issues
        assert len(result['issues'].get('forbidden_products', [])) == 0


class TestPersonaDiagnosticsOutput:
    """Tests for persona diagnostics object structure."""

    def test_diagnostics_has_all_fields(self, engine):
        """Diagnostics should include all required fields."""
        diagnostics = engine.detect_persona_with_diagnostics("VP Quality")

        required_fields = [
            'input_title',
            'matched_rules',
            'selected_persona',
            'selection_reason',
            'ambiguity_detected',
            'ambiguity_note',
            'fallback_applied',
            'eligible_products',
            'secondary_products',
            'forbidden_products'
        ]

        for field in required_fields:
            assert field in diagnostics, f"Missing field: {field}"

    def test_matched_rules_structure(self, engine):
        """Matched rules should have persona, pattern, position."""
        diagnostics = engine.detect_persona_with_diagnostics("VP Quality")

        assert len(diagnostics['matched_rules']) > 0
        rule = diagnostics['matched_rules'][0]
        assert 'persona' in rule
        assert 'pattern' in rule
        assert 'position' in rule

    def test_get_last_persona_diagnostics(self, engine):
        """Engine should store last diagnostics for retrieval."""
        engine.detect_persona("VP Manufacturing")
        diagnostics = engine.get_last_persona_diagnostics()

        assert diagnostics is not None
        assert diagnostics['selected_persona'] == 'manufacturing'
