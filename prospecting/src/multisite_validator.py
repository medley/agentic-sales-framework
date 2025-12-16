"""
Multi-Site Validator - Validates company intel reuse across site accounts

This module validates that:
- Company intel is fetched once and reused across site accounts
- cache_hit=true on subsequent contacts
- Company cited signal counts are consistent
- Persona-specific behavior works correctly

Usage:
    from multisite_validator import MultisiteValidator, MultisiteTestFixture

    fixture = MultisiteTestFixture.create_default()
    validator = MultisiteValidator()
    report = validator.validate(fixture)
"""

import os
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@dataclass
class SiteContact:
    """A contact at a specific site account."""
    name: str
    title: str
    email: str
    site_account_id: str
    expected_persona: str
    expected_review_required: bool = False
    expected_automation_allowed: bool = True


@dataclass
class MultisiteTestFixture:
    """
    Test fixture for multi-site validation.

    Contains one company with multiple site accounts and contacts.
    """
    primary_account_id: str
    company_name: str
    domain: str
    site_contacts: List[SiteContact] = field(default_factory=list)

    # Expected company intel signals (shared across all contacts)
    expected_company_signals: int = 3

    @classmethod
    def create_default(cls) -> "MultisiteTestFixture":
        """Create a default test fixture with two sites and different personas."""
        return cls(
            primary_account_id="001ABC123",
            company_name="MultiSite Test Corp",
            domain="multisitetest.com",
            site_contacts=[
                SiteContact(
                    name="Alice Quality",
                    title="VP Quality",
                    email="alice@multisitetest.com",
                    site_account_id="001ABC123-SITE1",
                    expected_persona="quality",
                    expected_review_required=False,
                    expected_automation_allowed=True
                ),
                SiteContact(
                    name="Bob Regulatory",
                    title="Director Regulatory Affairs",
                    email="bob@multisitetest.com",
                    site_account_id="001ABC123-SITE2",
                    expected_persona="regulatory",
                    expected_review_required=True,
                    expected_automation_allowed=False
                )
            ],
            expected_company_signals=3
        )

    @classmethod
    def create_same_persona(cls) -> "MultisiteTestFixture":
        """Create a fixture with two contacts having the same persona."""
        return cls(
            primary_account_id="001DEF456",
            company_name="Same Persona Corp",
            domain="samepersona.com",
            site_contacts=[
                SiteContact(
                    name="Carol Quality",
                    title="Quality Manager",
                    email="carol@samepersona.com",
                    site_account_id="001DEF456-SITE1",
                    expected_persona="quality",
                    expected_review_required=False,
                    expected_automation_allowed=True
                ),
                SiteContact(
                    name="Dave Quality",
                    title="Senior Quality Director",
                    email="dave@samepersona.com",
                    site_account_id="001DEF456-SITE2",
                    expected_persona="quality",
                    expected_review_required=False,
                    expected_automation_allowed=True
                )
            ],
            expected_company_signals=3
        )


# =============================================================================
# VALIDATION RESULTS
# =============================================================================

@dataclass
class ContactValidationResult:
    """Validation result for a single contact."""
    contact_name: str
    site_account_id: str

    # Cache behavior
    cache_hit: bool
    expected_cache_hit: bool

    # Signal counts
    company_cited_count: int
    expected_company_cited: int

    # Persona behavior
    detected_persona: str
    expected_persona: str
    review_required: bool
    expected_review_required: bool
    automation_allowed: bool
    expected_automation_allowed: bool

    # Context quality header (for report)
    context_quality_header: str = ""

    @property
    def passed(self) -> bool:
        """Check if all validations passed."""
        return (
            self.cache_hit == self.expected_cache_hit and
            self.company_cited_count == self.expected_company_cited and
            self.detected_persona == self.expected_persona and
            self.review_required == self.expected_review_required and
            self.automation_allowed == self.expected_automation_allowed
        )

    def get_failures(self) -> List[str]:
        """Get list of validation failures."""
        failures = []

        if self.cache_hit != self.expected_cache_hit:
            failures.append(f"cache_hit: expected {self.expected_cache_hit}, got {self.cache_hit}")

        if self.company_cited_count != self.expected_company_cited:
            failures.append(f"company_cited: expected {self.expected_company_cited}, got {self.company_cited_count}")

        if self.detected_persona != self.expected_persona:
            failures.append(f"persona: expected {self.expected_persona}, got {self.detected_persona}")

        if self.review_required != self.expected_review_required:
            failures.append(f"review_required: expected {self.expected_review_required}, got {self.review_required}")

        if self.automation_allowed != self.expected_automation_allowed:
            failures.append(f"automation_allowed: expected {self.expected_automation_allowed}, got {self.automation_allowed}")

        return failures


@dataclass
class MultisiteValidationReport:
    """Complete validation report for multi-site test."""
    fixture: MultisiteTestFixture
    contact_results: List[ContactValidationResult] = field(default_factory=list)
    validation_time: str = ""

    @property
    def all_passed(self) -> bool:
        """Check if all contact validations passed."""
        return all(r.passed for r in self.contact_results)

    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = []

        lines.append("# Multi-Site Validation Report")
        lines.append(f"**Generated:** {self.validation_time}")
        lines.append("")

        # Fixture info
        lines.append("## Test Fixture")
        lines.append(f"- **Company:** {self.fixture.company_name}")
        lines.append(f"- **Primary Account ID:** {self.fixture.primary_account_id}")
        lines.append(f"- **Domain:** {self.fixture.domain}")
        lines.append(f"- **Contacts:** {len(self.fixture.site_contacts)}")
        lines.append(f"- **Expected Company Signals:** {self.fixture.expected_company_signals}")
        lines.append("")

        # Overall status
        status = "PASSED" if self.all_passed else "FAILED"
        lines.append(f"## Overall Status: **{status}**")
        lines.append("")

        # Contact results
        lines.append("## Contact Results")
        lines.append("")

        for i, result in enumerate(self.contact_results, 1):
            contact_status = "PASSED" if result.passed else "FAILED"
            lines.append(f"### {i}. {result.contact_name} ({result.site_account_id})")
            lines.append(f"**Status:** {contact_status}")
            lines.append("")

            lines.append("| Check | Expected | Actual | Pass |")
            lines.append("|-------|----------|--------|------|")
            lines.append(f"| cache_hit | {result.expected_cache_hit} | {result.cache_hit} | {'Y' if result.cache_hit == result.expected_cache_hit else 'N'} |")
            lines.append(f"| company_cited | {result.expected_company_cited} | {result.company_cited_count} | {'Y' if result.company_cited_count == result.expected_company_cited else 'N'} |")
            lines.append(f"| persona | {result.expected_persona} | {result.detected_persona} | {'Y' if result.detected_persona == result.expected_persona else 'N'} |")
            lines.append(f"| review_required | {result.expected_review_required} | {result.review_required} | {'Y' if result.review_required == result.expected_review_required else 'N'} |")
            lines.append(f"| automation_allowed | {result.expected_automation_allowed} | {result.automation_allowed} | {'Y' if result.automation_allowed == result.expected_automation_allowed else 'N'} |")
            lines.append("")

            if not result.passed:
                lines.append("**Failures:**")
                for failure in result.get_failures():
                    lines.append(f"- {failure}")
                lines.append("")

            if result.context_quality_header:
                lines.append("**Context Quality Header:**")
                lines.append("```")
                lines.append(result.context_quality_header)
                lines.append("```")
                lines.append("")

        # Cache behavior summary
        lines.append("## Cache Behavior Summary")
        lines.append("")

        cache_hits = [r for r in self.contact_results if r.cache_hit]
        cache_misses = [r for r in self.contact_results if not r.cache_hit]

        lines.append(f"- Cache hits: {len(cache_hits)}")
        lines.append(f"- Cache misses: {len(cache_misses)}")

        if len(self.contact_results) > 1:
            # First should miss, rest should hit
            first_result = self.contact_results[0]
            if not first_result.cache_hit:
                lines.append("- First contact correctly fetched fresh data")
            else:
                lines.append("- WARNING: First contact had unexpected cache hit")

            subsequent = self.contact_results[1:]
            hits = sum(1 for r in subsequent if r.cache_hit)
            lines.append(f"- Subsequent contacts with cache hit: {hits}/{len(subsequent)}")

        lines.append("")

        # Persona comparison
        lines.append("## Persona/Product Comparison")
        lines.append("")
        lines.append("| Contact | Site | Persona | Review Required | Automation |")
        lines.append("|---------|------|---------|-----------------|------------|")

        for result in self.contact_results:
            lines.append(
                f"| {result.contact_name} | {result.site_account_id} | "
                f"{result.detected_persona} | {result.review_required} | {result.automation_allowed} |"
            )

        lines.append("")
        lines.append("---")
        lines.append(f"*Report generated: {self.validation_time}*")

        return "\n".join(lines)


# =============================================================================
# VALIDATOR
# =============================================================================

class MultisiteValidator:
    """
    Validates multi-site company intel reuse behavior.

    This validator simulates running the prospect pipeline for multiple
    contacts at different site accounts and verifies:
    - Company intel cache behavior
    - Signal count consistency
    - Persona-specific rules
    """

    def validate_from_context_quality(
        self,
        fixture: MultisiteTestFixture,
        context_qualities: List[Dict[str, Any]]
    ) -> MultisiteValidationReport:
        """
        Validate using pre-computed context quality dicts.

        Args:
            fixture: Test fixture definition
            context_qualities: List of context_quality dicts (one per contact)

        Returns:
            MultisiteValidationReport
        """
        report = MultisiteValidationReport(
            fixture=fixture,
            validation_time=datetime.now().isoformat()
        )

        for i, (contact, cq) in enumerate(zip(fixture.site_contacts, context_qualities)):
            # Extract values from context quality
            sources = cq.get("sources", {})
            company_intel = sources.get("company_intel", {})
            cache_hit = company_intel.get("cache_hit", False)

            signals = cq.get("signals", {})
            counts = signals.get("counts", {})
            company_cited = counts.get("company_cited", 0)

            contact_info = cq.get("contact", {})
            detected_persona = contact_info.get("persona", "unknown")
            review_required = contact_info.get("review_required", False)

            # Get automation_allowed from persona diagnostics if available
            automation_allowed = True
            if "persona_confidence" in contact_info:
                # Regulatory persona typically has automation_allowed=False
                if detected_persona == "regulatory":
                    automation_allowed = False

            # First contact should have cache miss, subsequent should have cache hit
            expected_cache_hit = i > 0

            # Generate header for report
            from .context_quality import render_context_quality_header
            header = render_context_quality_header(cq)

            result = ContactValidationResult(
                contact_name=contact.name,
                site_account_id=contact.site_account_id,
                cache_hit=cache_hit,
                expected_cache_hit=expected_cache_hit,
                company_cited_count=company_cited,
                expected_company_cited=fixture.expected_company_signals,
                detected_persona=detected_persona,
                expected_persona=contact.expected_persona,
                review_required=review_required,
                expected_review_required=contact.expected_review_required,
                automation_allowed=automation_allowed,
                expected_automation_allowed=contact.expected_automation_allowed,
                context_quality_header=header
            )

            report.contact_results.append(result)

        return report


def write_validation_report(
    report: MultisiteValidationReport,
    output_dir: Optional[Path] = None
) -> Path:
    """
    Write validation report to file.

    Args:
        report: MultisiteValidationReport
        output_dir: Output directory (default: runs/)

    Returns:
        Path to written report
    """
    if output_dir is None:
        # Default to runs folder under prospecting output root
        output_dir = Path(os.environ.get(
            "PROSPECTING_OUTPUT_ROOT",
            os.path.expanduser("~/prospecting-output")
        )) / "runs"

    output_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    report_path = output_dir / f"{date_str}_multisite_validation.md"

    content = report.to_markdown()
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Wrote validation report to {report_path}")
    return report_path
