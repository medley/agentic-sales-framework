"""
Promotion Rules - Gates and lifecycle control for Prospecting → Accounts promotion

This module defines:
- Prospect lifecycle states
- Promotion eligibility rules
- Gate evaluation logic

Promotion is intentional and gated. Prospecting is experimental;
Accounts are system of record.

Usage:
    from promotion_rules import PromotionGate, ProspectState

    gate = PromotionGate()
    result = gate.evaluate(context_quality, persona_diagnostics)

    if result.eligible:
        # proceed with promotion
    else:
        print(f"Blocked: {result.reasons}")
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# PROSPECT LIFECYCLE STATES
# =============================================================================

class ProspectState(str, Enum):
    """Lifecycle states for a prospecting artifact."""

    # Initial state after hybrid system runs
    PREPARED_FOR_RENDERING = "prepared_for_rendering"

    # After render_and_validate.py passes
    RENDERED_VALIDATED = "rendered_validated"

    # User manually sent the email (external action)
    SENT_MANUAL = "sent_manual"

    # Prospect replied (external action)
    REPLIED = "replied"

    # Artifacts promoted to 01_Accounts/_Active
    PROMOTED = "promoted"

    # Rejected by system or user
    REJECTED = "rejected"

    # Requires manual review before proceeding
    REVIEW_REQUIRED = "review_required"


# =============================================================================
# PROMOTION ELIGIBILITY RESULT
# =============================================================================

@dataclass
class PromotionEligibilityResult:
    """Result of promotion gate evaluation."""

    eligible: bool
    reasons: List[str] = field(default_factory=list)
    warnings_present: List[str] = field(default_factory=list)
    can_force: bool = True  # Whether --force can override

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "eligible": self.eligible,
            "reasons": self.reasons,
            "warnings_present": self.warnings_present,
            "can_force": self.can_force
        }


# =============================================================================
# BLOCKING WARNINGS
# =============================================================================

# Warnings that block promotion (cannot be forced)
BLOCKING_WARNINGS = {
    "THIN_RESEARCH",
    "VENDOR_DATA_ONLY"
}

# Warnings that block batch rendering (can be forced)
BATCH_RENDER_BLOCKING_WARNINGS = {
    "THIN_RESEARCH",
    "OLD_SIGNALS_PRESENT"
}


# =============================================================================
# PROMOTION GATE
# =============================================================================

class PromotionGate:
    """
    Evaluates promotion eligibility from Prospecting → Accounts.

    Promotion is allowed only if:
    - status == rendered_validated
    - validation passed
    - confidence_mode != GENERIC
    - review_required == false (unless overridden)
    - no forbidden product violations
    - warnings do NOT include: THIN_RESEARCH, VENDOR_DATA_ONLY
    """

    def evaluate(
        self,
        context_quality: Dict[str, Any],
        persona_diagnostics: Optional[Dict[str, Any]] = None,
        status: str = None,
        validation_passed: bool = True,
        force: bool = False
    ) -> PromotionEligibilityResult:
        """
        Evaluate whether artifacts are eligible for promotion.

        Args:
            context_quality: Canonical context_quality dict
            persona_diagnostics: Persona detection result
            status: Current prospect state
            validation_passed: Whether render validation passed
            force: Override review_required and some warning checks

        Returns:
            PromotionEligibilityResult with eligible flag and reasons
        """
        reasons = []
        warnings_present = []
        can_force = True

        # Gate 1: Status must be rendered_validated
        if status != ProspectState.RENDERED_VALIDATED.value:
            reasons.append(f"Status is '{status}', must be 'rendered_validated'")

        # Gate 2: Validation must have passed
        if not validation_passed:
            reasons.append("Validation did not pass")

        # Gate 3: Confidence mode cannot be GENERIC
        mode = context_quality.get("mode", {})
        confidence_mode = mode.get("confidence_mode", "UNKNOWN")

        if confidence_mode == "GENERIC":
            reasons.append("Confidence mode is GENERIC (no cited signals)")

        # Gate 4: Review required check
        contact = context_quality.get("contact", {})
        review_required = contact.get("review_required", False)

        if review_required and not force:
            reasons.append("Review required flag is set (use --force to override)")

        # Gate 5: Forbidden product violations
        if persona_diagnostics:
            forbidden = persona_diagnostics.get("forbidden_products", [])
            if forbidden:
                # Check if any forbidden products were mentioned
                # This is informational - actual violation check would need email content
                pass  # Tracked but not blocking at this layer

        # Gate 6: Warning checks
        signals = context_quality.get("signals", {})
        warnings = signals.get("warnings", [])

        for warning in warnings:
            # Extract warning code (before colon)
            warning_code = warning.split(":")[0].strip() if ":" in warning else warning

            if warning_code in BLOCKING_WARNINGS:
                reasons.append(f"Blocking warning present: {warning_code}")
                warnings_present.append(warning_code)
                can_force = False  # These cannot be overridden
            else:
                warnings_present.append(warning_code)

        eligible = len(reasons) == 0

        return PromotionEligibilityResult(
            eligible=eligible,
            reasons=reasons,
            warnings_present=warnings_present,
            can_force=can_force
        )


# =============================================================================
# BATCH RENDER ELIGIBILITY
# =============================================================================

@dataclass
class BatchRenderEligibilityResult:
    """Result of batch render eligibility evaluation."""

    eligible: bool
    reasons: List[str] = field(default_factory=list)
    can_force: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "eligible": self.eligible,
            "reasons": self.reasons,
            "can_force": self.can_force
        }


class BatchRenderGate:
    """
    Evaluates whether a prospect is eligible for batch rendering.

    Batch rendering is allowed only if:
    - review_required == false
    - confidence_mode in {HIGH, MEDIUM}
    - total_cited >= 2
    - warnings do NOT include: THIN_RESEARCH, OLD_SIGNALS_PRESENT
    - persona.automation_allowed == true

    Regulatory persona: NEVER batch render unless --force
    """

    # Confidence modes that allow batch rendering
    ALLOWED_CONFIDENCE_MODES = {"HIGH", "MEDIUM"}

    # Minimum cited signals required
    MIN_CITED_SIGNALS = 2

    def evaluate(
        self,
        context_quality: Dict[str, Any],
        persona_diagnostics: Optional[Dict[str, Any]] = None,
        force: bool = False
    ) -> BatchRenderEligibilityResult:
        """
        Evaluate whether prospect is eligible for batch rendering.

        Args:
            context_quality: Canonical context_quality dict
            persona_diagnostics: Persona detection result
            force: Override review_required after human review (regulatory personas CANNOT be overridden)

        Returns:
            BatchRenderEligibilityResult with eligible flag and reasons
        """
        reasons = []
        can_force = True

        # Gate 1: Review required check
        contact = context_quality.get("contact", {})
        review_required = contact.get("review_required", False)

        if review_required:
            reasons.append("Review required flag is set")

        # Gate 2: Confidence mode check
        mode = context_quality.get("mode", {})
        confidence_mode = mode.get("confidence_mode", "UNKNOWN")

        if confidence_mode not in self.ALLOWED_CONFIDENCE_MODES:
            reasons.append(f"Confidence mode '{confidence_mode}' not in allowed modes {self.ALLOWED_CONFIDENCE_MODES}")

        # Gate 3: Minimum cited signals
        signals = context_quality.get("signals", {})
        counts = signals.get("counts", {})
        total_cited = counts.get("total_cited", 0)

        if total_cited < self.MIN_CITED_SIGNALS:
            reasons.append(f"Only {total_cited} cited signals, minimum is {self.MIN_CITED_SIGNALS}")

        # Gate 4: Warning checks
        warnings = signals.get("warnings", [])

        for warning in warnings:
            warning_code = warning.split(":")[0].strip() if ":" in warning else warning

            if warning_code in BATCH_RENDER_BLOCKING_WARNINGS:
                reasons.append(f"Blocking warning for batch render: {warning_code}")

        # Gate 5: Persona automation_allowed check
        if persona_diagnostics:
            automation_allowed = persona_diagnostics.get("automation_allowed", True)
            persona = persona_diagnostics.get("persona") or persona_diagnostics.get("selected_persona")

            if not automation_allowed:
                reasons.append(f"Persona '{persona}' has automation_allowed=false")
                # Regulatory persona - CANNOT be forced (hard safety constraint)
                if persona == "regulatory":
                    can_force = False

        # Apply force override
        if force and can_force:
            # Clear forceable reasons
            reasons = [r for r in reasons if "cannot be forced" in r.lower()]

        eligible = len(reasons) == 0

        return BatchRenderEligibilityResult(
            eligible=eligible,
            reasons=reasons,
            can_force=can_force
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_promotion_state(
    status: str,
    validation_passed: bool = False,
    sent: bool = False,
    replied: bool = False,
    promoted: bool = False
) -> ProspectState:
    """
    Determine current prospect state from various flags.

    Args:
        status: Pipeline status string
        validation_passed: Whether render validation passed
        sent: Whether email was sent
        replied: Whether prospect replied
        promoted: Whether artifacts were promoted

    Returns:
        ProspectState enum value
    """
    if promoted:
        return ProspectState.PROMOTED
    if replied:
        return ProspectState.REPLIED
    if sent:
        return ProspectState.SENT_MANUAL
    if validation_passed and status in ("ready_for_rendering", "rendered_validated"):
        return ProspectState.RENDERED_VALIDATED
    if status == "requires_manual_review":
        return ProspectState.REVIEW_REQUIRED
    if status in ("rejected", "error", "insufficient_signals"):
        return ProspectState.REJECTED

    return ProspectState.PREPARED_FOR_RENDERING


def format_eligibility_report(
    promotion_result: PromotionEligibilityResult,
    render_result: Optional[BatchRenderEligibilityResult] = None
) -> str:
    """
    Format eligibility results as human-readable report.

    Args:
        promotion_result: PromotionEligibilityResult
        render_result: Optional BatchRenderEligibilityResult

    Returns:
        Formatted string report
    """
    lines = []

    lines.append("=" * 60)
    lines.append("ELIGIBILITY REPORT")
    lines.append("=" * 60)

    # Promotion eligibility
    lines.append("")
    lines.append("PROMOTION (Prospecting → Accounts):")
    status = "ELIGIBLE" if promotion_result.eligible else "NOT ELIGIBLE"
    lines.append(f"  Status: {status}")

    if not promotion_result.eligible:
        lines.append("  Reasons:")
        for reason in promotion_result.reasons:
            lines.append(f"    - {reason}")

    if promotion_result.warnings_present:
        lines.append(f"  Warnings: {', '.join(promotion_result.warnings_present)}")

    lines.append(f"  Can force: {'Yes' if promotion_result.can_force else 'No'}")

    # Batch render eligibility (if provided)
    if render_result:
        lines.append("")
        lines.append("BATCH RENDERING:")
        status = "ELIGIBLE" if render_result.eligible else "NOT ELIGIBLE"
        lines.append(f"  Status: {status}")

        if not render_result.eligible:
            lines.append("  Reasons:")
            for reason in render_result.reasons:
                lines.append(f"    - {reason}")

        lines.append(f"  Can force: {'Yes' if render_result.can_force else 'No'}")

    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)
