"""
Phase 2 Tests - Multi-Site Validation, Promotion Rules, and Batch Rendering

Tests:
1. Multi-site reuse and cache_hit behavior
2. Promotion gating (allowed vs blocked)
3. Promotion dry_run output
4. Batch rendering eligibility per persona
5. Regulatory persona batch render block
6. Force overrides working as expected
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from src.approval_rules import (
    ApprovalGate,
    BatchRenderGate,
    ProspectState,
    ApprovalEligibilityResult,
    BatchRenderEligibilityResult,
    BLOCKING_WARNINGS,
    BATCH_RENDER_BLOCKING_WARNINGS,
    get_prospect_state,
    format_eligibility_report,
    # Backwards compatibility aliases
    PromotionGate,
    PromotionEligibilityResult,
    get_promotion_state
)
from src.multisite_validator import (
    MultisiteValidator,
    MultisiteTestFixture,
    MultisiteValidationReport,
    SiteContact,
    write_validation_report
)
from src.context_quality import ContextQualityBuilder


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def high_confidence_context_quality():
    """Context quality with HIGH confidence and no warnings."""
    return {
        "generated_at": datetime.now().isoformat(),
        "company": {"name": "Test Corp"},
        "contact": {
            "name": "John Smith",
            "persona": "quality",
            "review_required": False
        },
        "mode": {
            "tier": "A",
            "confidence_mode": "HIGH"
        },
        "sources": {
            "company_intel": {"cache_hit": False, "status": "ok"}
        },
        "signals": {
            "counts": {
                "total_cited": 5,
                "company_cited": 3,
                "person_cited": 2,
                "total_vendor": 1
            },
            "freshness": {
                "newest_cited_age_days": 30
            },
            "warnings": []
        }
    }


@pytest.fixture
def generic_confidence_context_quality():
    """Context quality with GENERIC confidence."""
    return {
        "generated_at": datetime.now().isoformat(),
        "company": {"name": "Test Corp"},
        "contact": {
            "name": "Jane Doe",
            "persona": "quality",
            "review_required": False
        },
        "mode": {
            "tier": "B",
            "confidence_mode": "GENERIC"
        },
        "sources": {},
        "signals": {
            "counts": {
                "total_cited": 0,
                "company_cited": 0,
                "person_cited": 0,
                "total_vendor": 2
            },
            "freshness": {},
            "warnings": ["NO_CITED_SIGNALS: no cited signals found"]
        }
    }


@pytest.fixture
def thin_research_context_quality():
    """Context quality with THIN_RESEARCH warning."""
    return {
        "generated_at": datetime.now().isoformat(),
        "company": {"name": "Test Corp"},
        "contact": {
            "name": "Bob Jones",
            "persona": "quality",
            "review_required": False
        },
        "mode": {
            "tier": "A",
            "confidence_mode": "MEDIUM"
        },
        "sources": {},
        "signals": {
            "counts": {
                "total_cited": 2,
                "company_cited": 1,
                "person_cited": 1,
                "total_vendor": 0
            },
            "freshness": {
                "oldest_cited_age_days": 100
            },
            "warnings": ["THIN_RESEARCH: only 2 signals with oldest 100 days old"]
        }
    }


@pytest.fixture
def regulatory_persona_context_quality():
    """Context quality for regulatory persona (review required)."""
    return {
        "generated_at": datetime.now().isoformat(),
        "company": {"name": "Test Corp"},
        "contact": {
            "name": "Reg Person",
            "persona": "regulatory",
            "review_required": True
        },
        "mode": {
            "tier": "A",
            "confidence_mode": "HIGH"
        },
        "sources": {},
        "signals": {
            "counts": {
                "total_cited": 4,
                "company_cited": 2,
                "person_cited": 2,
                "total_vendor": 1
            },
            "freshness": {
                "newest_cited_age_days": 15
            },
            "warnings": []
        }
    }


@pytest.fixture
def regulatory_persona_diagnostics():
    """Persona diagnostics for regulatory persona."""
    return {
        "selected_persona": "regulatory",
        "persona": "regulatory",
        "automation_allowed": False,
        "safe_angle_only": True,
        "ambiguity_detected": False
    }


@pytest.fixture
def quality_persona_diagnostics():
    """Persona diagnostics for quality persona."""
    return {
        "selected_persona": "quality",
        "persona": "quality",
        "automation_allowed": True,
        "safe_angle_only": False,
        "ambiguity_detected": False
    }


# =============================================================================
# PROMOTION GATE TESTS
# =============================================================================

class TestPromotionGate:
    """Tests for PromotionGate eligibility evaluation."""

    def test_eligible_when_all_conditions_met(self, high_confidence_context_quality):
        """Promotion allowed when all conditions are met."""
        gate = PromotionGate()
        result = gate.evaluate(
            context_quality=high_confidence_context_quality,
            status=ProspectState.RENDERED_VALIDATED.value,
            validation_passed=True
        )

        assert result.eligible is True
        assert len(result.reasons) == 0

    def test_blocked_when_status_not_rendered(self, high_confidence_context_quality):
        """Promotion blocked when status is not rendered_validated."""
        gate = PromotionGate()
        result = gate.evaluate(
            context_quality=high_confidence_context_quality,
            status=ProspectState.PREPARED_FOR_RENDERING.value,
            validation_passed=True
        )

        assert result.eligible is False
        assert any("rendered_validated" in r for r in result.reasons)

    def test_blocked_when_confidence_generic(self, generic_confidence_context_quality):
        """Promotion blocked when confidence mode is GENERIC."""
        gate = PromotionGate()
        result = gate.evaluate(
            context_quality=generic_confidence_context_quality,
            status=ProspectState.RENDERED_VALIDATED.value,
            validation_passed=True
        )

        assert result.eligible is False
        assert any("GENERIC" in r for r in result.reasons)

    def test_blocked_when_review_required(self, regulatory_persona_context_quality):
        """Promotion blocked when review_required is True."""
        gate = PromotionGate()
        result = gate.evaluate(
            context_quality=regulatory_persona_context_quality,
            status=ProspectState.RENDERED_VALIDATED.value,
            validation_passed=True,
            force=False
        )

        assert result.eligible is False
        assert any("review required" in r.lower() for r in result.reasons)

    def test_review_required_bypassed_with_force(self, regulatory_persona_context_quality):
        """Review required can be bypassed with --force."""
        gate = PromotionGate()
        result = gate.evaluate(
            context_quality=regulatory_persona_context_quality,
            status=ProspectState.RENDERED_VALIDATED.value,
            validation_passed=True,
            force=True
        )

        # Should be eligible with force (review_required is forceable)
        assert result.eligible is True

    def test_blocked_with_thin_research_warning(self, thin_research_context_quality):
        """Promotion blocked with THIN_RESEARCH warning."""
        gate = PromotionGate()
        result = gate.evaluate(
            context_quality=thin_research_context_quality,
            status=ProspectState.RENDERED_VALIDATED.value,
            validation_passed=True
        )

        assert result.eligible is False
        assert "THIN_RESEARCH" in result.warnings_present

    def test_thin_research_cannot_be_forced(self, thin_research_context_quality):
        """THIN_RESEARCH is a blocking warning that cannot be forced."""
        gate = PromotionGate()
        result = gate.evaluate(
            context_quality=thin_research_context_quality,
            status=ProspectState.RENDERED_VALIDATED.value,
            validation_passed=True,
            force=True
        )

        # THIN_RESEARCH cannot be forced
        assert result.eligible is False
        assert result.can_force is False

    def test_vendor_only_cannot_be_forced(self):
        """VENDOR_DATA_ONLY is a blocking warning that cannot be forced."""
        cq = {
            "mode": {"confidence_mode": "LOW"},
            "contact": {"review_required": False},
            "signals": {
                "counts": {"total_cited": 0, "total_vendor": 3},
                "warnings": ["VENDOR_DATA_ONLY: only vendor data available"]
            }
        }

        gate = PromotionGate()
        result = gate.evaluate(
            context_quality=cq,
            status=ProspectState.RENDERED_VALIDATED.value,
            validation_passed=True,
            force=True
        )

        assert result.eligible is False
        assert result.can_force is False
        assert "VENDOR_DATA_ONLY" in result.warnings_present


# =============================================================================
# BATCH RENDER GATE TESTS
# =============================================================================

class TestBatchRenderGate:
    """Tests for BatchRenderGate eligibility evaluation."""

    def test_eligible_with_high_confidence(
        self,
        high_confidence_context_quality,
        quality_persona_diagnostics
    ):
        """Batch render allowed with HIGH confidence and quality persona."""
        gate = BatchRenderGate()
        result = gate.evaluate(
            context_quality=high_confidence_context_quality,
            persona_diagnostics=quality_persona_diagnostics
        )

        assert result.eligible is True
        assert len(result.reasons) == 0

    def test_blocked_with_low_confidence(self):
        """Batch render blocked with LOW confidence."""
        cq = {
            "mode": {"confidence_mode": "LOW"},
            "contact": {"review_required": False},
            "signals": {
                "counts": {"total_cited": 3},
                "warnings": []
            }
        }

        gate = BatchRenderGate()
        result = gate.evaluate(context_quality=cq)

        assert result.eligible is False
        assert any("confidence mode" in r.lower() for r in result.reasons)

    def test_blocked_with_insufficient_signals(self):
        """Batch render blocked with fewer than 2 cited signals."""
        cq = {
            "mode": {"confidence_mode": "HIGH"},
            "contact": {"review_required": False},
            "signals": {
                "counts": {"total_cited": 1},
                "warnings": []
            }
        }

        gate = BatchRenderGate()
        result = gate.evaluate(context_quality=cq)

        assert result.eligible is False
        assert any("minimum" in r.lower() for r in result.reasons)

    def test_blocked_with_review_required(self, regulatory_persona_context_quality):
        """Batch render blocked when review_required is True."""
        gate = BatchRenderGate()
        result = gate.evaluate(context_quality=regulatory_persona_context_quality)

        assert result.eligible is False
        assert any("review required" in r.lower() for r in result.reasons)

    def test_blocked_with_old_signals_warning(self):
        """Batch render blocked with OLD_SIGNALS_PRESENT warning."""
        cq = {
            "mode": {"confidence_mode": "HIGH"},
            "contact": {"review_required": False},
            "signals": {
                "counts": {"total_cited": 5},
                "warnings": ["OLD_SIGNALS_PRESENT: oldest signal is 400 days old"]
            }
        }

        gate = BatchRenderGate()
        result = gate.evaluate(context_quality=cq)

        assert result.eligible is False
        assert any("OLD_SIGNALS_PRESENT" in r for r in result.reasons)

    def test_regulatory_persona_blocked(
        self,
        high_confidence_context_quality,
        regulatory_persona_diagnostics
    ):
        """Regulatory persona blocked from batch render."""
        # Override review_required to False to isolate automation_allowed check
        cq = high_confidence_context_quality.copy()
        cq["contact"] = {"review_required": False, "persona": "regulatory"}

        gate = BatchRenderGate()
        result = gate.evaluate(
            context_quality=cq,
            persona_diagnostics=regulatory_persona_diagnostics
        )

        assert result.eligible is False
        assert any("automation_allowed=false" in r.lower() for r in result.reasons)

    def test_regulatory_cannot_be_forced_in_strict_mode(
        self,
        high_confidence_context_quality,
        regulatory_persona_diagnostics
    ):
        """Regulatory persona cannot be forced in strict mode."""
        cq = high_confidence_context_quality.copy()
        cq["contact"] = {"review_required": False, "persona": "regulatory"}

        gate = BatchRenderGate()
        result = gate.evaluate(
            context_quality=cq,
            persona_diagnostics=regulatory_persona_diagnostics,
            force=True,
            policy="strict"
        )

        # In strict mode, regulatory cannot be forced
        assert result.can_force is False

    def test_regulatory_can_be_forced_in_permissive_mode(
        self,
        high_confidence_context_quality,
        regulatory_persona_diagnostics
    ):
        """Regulatory persona can be forced in permissive mode."""
        cq = high_confidence_context_quality.copy()
        cq["contact"] = {"review_required": False, "persona": "regulatory"}

        gate = BatchRenderGate()
        result = gate.evaluate(
            context_quality=cq,
            persona_diagnostics=regulatory_persona_diagnostics,
            force=True,
            policy="permissive"
        )

        # In permissive mode, can_force should be True
        assert result.can_force is True


# =============================================================================
# MULTI-SITE VALIDATION TESTS
# =============================================================================

class TestMultisiteValidator:
    """Tests for multi-site company intel reuse validation."""

    def test_cache_hit_on_second_contact(self):
        """Second contact should have cache_hit=True."""
        fixture = MultisiteTestFixture.create_default()

        # Simulate two context qualities
        cq1 = {
            "contact": {"persona": "quality", "review_required": False},
            "sources": {"company_intel": {"cache_hit": False}},
            "signals": {"counts": {"company_cited": 3}}
        }
        cq2 = {
            "contact": {"persona": "regulatory", "review_required": True},
            "sources": {"company_intel": {"cache_hit": True}},
            "signals": {"counts": {"company_cited": 3}}
        }

        validator = MultisiteValidator()
        report = validator.validate_from_context_quality(fixture, [cq1, cq2])

        # First should be cache miss
        assert report.contact_results[0].cache_hit is False
        assert report.contact_results[0].expected_cache_hit is False

        # Second should be cache hit
        assert report.contact_results[1].cache_hit is True
        assert report.contact_results[1].expected_cache_hit is True

    def test_company_signals_consistent(self):
        """Company cited signals should be consistent across contacts."""
        fixture = MultisiteTestFixture.create_default()

        cq1 = {
            "contact": {"persona": "quality", "review_required": False},
            "sources": {"company_intel": {"cache_hit": False}},
            "signals": {"counts": {"company_cited": 3}}
        }
        cq2 = {
            "contact": {"persona": "regulatory", "review_required": True},
            "sources": {"company_intel": {"cache_hit": True}},
            "signals": {"counts": {"company_cited": 3}}
        }

        validator = MultisiteValidator()
        report = validator.validate_from_context_quality(fixture, [cq1, cq2])

        # Both should have same company_cited count
        assert report.contact_results[0].company_cited_count == 3
        assert report.contact_results[1].company_cited_count == 3

    def test_personas_differ_correctly(self):
        """Different contacts should have different personas detected."""
        fixture = MultisiteTestFixture.create_default()

        cq1 = {
            "contact": {"persona": "quality", "review_required": False},
            "sources": {"company_intel": {"cache_hit": False}},
            "signals": {"counts": {"company_cited": 3}}
        }
        cq2 = {
            "contact": {"persona": "regulatory", "review_required": True},
            "sources": {"company_intel": {"cache_hit": True}},
            "signals": {"counts": {"company_cited": 3}}
        }

        validator = MultisiteValidator()
        report = validator.validate_from_context_quality(fixture, [cq1, cq2])

        # Personas should differ
        assert report.contact_results[0].detected_persona == "quality"
        assert report.contact_results[1].detected_persona == "regulatory"

    def test_review_required_reflects_persona(self):
        """Review required should reflect persona correctly."""
        fixture = MultisiteTestFixture.create_default()

        cq1 = {
            "contact": {"persona": "quality", "review_required": False},
            "sources": {"company_intel": {"cache_hit": False}},
            "signals": {"counts": {"company_cited": 3}}
        }
        cq2 = {
            "contact": {"persona": "regulatory", "review_required": True},
            "sources": {"company_intel": {"cache_hit": True}},
            "signals": {"counts": {"company_cited": 3}}
        }

        validator = MultisiteValidator()
        report = validator.validate_from_context_quality(fixture, [cq1, cq2])

        # Quality persona - no review required
        assert report.contact_results[0].review_required is False
        assert report.contact_results[0].expected_review_required is False

        # Regulatory persona - review required
        assert report.contact_results[1].review_required is True
        assert report.contact_results[1].expected_review_required is True

    def test_validation_report_markdown(self):
        """Validation report generates valid markdown."""
        fixture = MultisiteTestFixture.create_default()

        cq1 = {
            "contact": {"persona": "quality", "review_required": False},
            "sources": {"company_intel": {"cache_hit": False}},
            "signals": {"counts": {"company_cited": 3}}
        }
        cq2 = {
            "contact": {"persona": "regulatory", "review_required": True},
            "sources": {"company_intel": {"cache_hit": True}},
            "signals": {"counts": {"company_cited": 3}}
        }

        validator = MultisiteValidator()
        report = validator.validate_from_context_quality(fixture, [cq1, cq2])

        markdown = report.to_markdown()

        # Check key sections exist
        assert "# Multi-Site Validation Report" in markdown
        assert "## Test Fixture" in markdown
        assert "## Overall Status" in markdown
        assert "## Contact Results" in markdown
        assert "## Cache Behavior Summary" in markdown
        assert fixture.company_name in markdown


# =============================================================================
# PROMOTION STATE TESTS
# =============================================================================

class TestPromotionState:
    """Tests for prospect state determination."""

    def test_prepared_for_rendering_state(self):
        """Status ready_for_rendering maps to PREPARED_FOR_RENDERING."""
        state = get_promotion_state("ready_for_rendering")
        assert state == ProspectState.PREPARED_FOR_RENDERING

    def test_rendered_validated_state(self):
        """Validation passed maps to RENDERED_VALIDATED."""
        state = get_promotion_state(
            "ready_for_rendering",
            validation_passed=True
        )
        assert state == ProspectState.RENDERED_VALIDATED

    def test_approved_for_send_state(self):
        """Approved flag takes precedence."""
        state = get_promotion_state(
            "ready_for_rendering",
            validation_passed=True,
            promoted=True  # approved=True maps to this via alias
        )
        assert state == ProspectState.APPROVED_FOR_SEND

    def test_rejected_state(self):
        """Error status maps to REJECTED."""
        state = get_promotion_state("error")
        assert state == ProspectState.REJECTED

    def test_review_required_state(self):
        """requires_manual_review maps to REVIEW_REQUIRED."""
        state = get_promotion_state("requires_manual_review")
        assert state == ProspectState.REVIEW_REQUIRED


# =============================================================================
# ELIGIBILITY REPORT TESTS
# =============================================================================

class TestEligibilityReport:
    """Tests for eligibility report formatting."""

    def test_report_contains_approval_section(self):
        """Report contains approval eligibility section."""
        promo_result = PromotionEligibilityResult(
            eligible=False,
            reasons=["Status is not rendered_validated"],
            warnings_present=["THIN_RESEARCH"],
            can_force=False
        )

        report = format_eligibility_report(promo_result)

        assert "APPROVAL" in report
        assert "NOT ELIGIBLE" in report
        assert "THIN_RESEARCH" in report
        assert "Can force: No" in report

    def test_report_contains_render_section_when_provided(self):
        """Report contains batch render section when provided."""
        promo_result = PromotionEligibilityResult(eligible=True)
        render_result = BatchRenderEligibilityResult(
            eligible=False,
            reasons=["Confidence mode 'LOW' not allowed"],
            can_force=True
        )

        report = format_eligibility_report(promo_result, render_result)

        assert "BATCH RENDERING" in report
        assert "NOT ELIGIBLE" in report
        assert "confidence" in report.lower()


# =============================================================================
# FORCE OVERRIDE TESTS
# =============================================================================

class TestForceOverrides:
    """Tests for --force flag behavior."""

    def test_force_bypasses_review_required_in_promotion(self):
        """Force bypasses review_required in promotion gate."""
        cq = {
            "mode": {"confidence_mode": "HIGH"},
            "contact": {"review_required": True},
            "signals": {"counts": {"total_cited": 5}, "warnings": []}
        }

        gate = PromotionGate()

        # Without force - blocked
        result_no_force = gate.evaluate(
            context_quality=cq,
            status=ProspectState.RENDERED_VALIDATED.value,
            validation_passed=True,
            force=False
        )
        assert result_no_force.eligible is False

        # With force - allowed
        result_force = gate.evaluate(
            context_quality=cq,
            status=ProspectState.RENDERED_VALIDATED.value,
            validation_passed=True,
            force=True
        )
        assert result_force.eligible is True

    def test_force_does_not_bypass_blocking_warnings(self):
        """Force cannot bypass blocking warnings (THIN_RESEARCH, VENDOR_DATA_ONLY)."""
        cq = {
            "mode": {"confidence_mode": "HIGH"},
            "contact": {"review_required": False},
            "signals": {
                "counts": {"total_cited": 2},
                "warnings": ["THIN_RESEARCH: thin research"]
            }
        }

        gate = PromotionGate()
        result = gate.evaluate(
            context_quality=cq,
            status=ProspectState.RENDERED_VALIDATED.value,
            validation_passed=True,
            force=True
        )

        assert result.eligible is False
        assert result.can_force is False

    def test_blocking_warnings_list_is_complete(self):
        """Verify blocking warnings set contains expected warnings."""
        assert "THIN_RESEARCH" in BLOCKING_WARNINGS
        assert "VENDOR_DATA_ONLY" in BLOCKING_WARNINGS

    def test_batch_render_blocking_warnings_list(self):
        """Verify batch render blocking warnings set."""
        assert "THIN_RESEARCH" in BATCH_RENDER_BLOCKING_WARNINGS
        assert "OLD_SIGNALS_PRESENT" in BATCH_RENDER_BLOCKING_WARNINGS
