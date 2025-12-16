"""
Artifact Scanner - Read-only scanning of prospecting artifacts

This module provides utilities to scan the prospecting output folder
and extract metadata from context_quality.json files.

Used by:
- review_queue.py
- inbox_view.py
- prospecting_stats.py

This is READ-ONLY - no writes to artifacts.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, date
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Iterator
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

# Default prospecting output root
# Override with PROSPECTING_OUTPUT_ROOT environment variable
DEFAULT_PROSPECTING_ROOT = os.path.expanduser(
    os.environ.get('PROSPECTING_OUTPUT_ROOT', "~/prospecting-output")
)


class ProspectStatus(str, Enum):
    """Status for display purposes."""
    PREPARED = "prepared"
    RENDERED = "rendered"
    APPROVABLE = "approvable"  # Ready to approve for send
    APPROVED_FOR_SEND = "approved_for_send"  # Human approved to send
    REVIEW_REQUIRED = "review_required"
    REJECTED = "rejected"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ProspectArtifact:
    """A single prospecting artifact with metadata."""

    # Identifiers
    company_name: str
    contact_name: str
    run_date: str  # YYYY-MM-DD

    # Paths
    context_quality_path: Path
    email_path: Optional[Path] = None
    drafts_folder: Path = None

    # Context quality data
    confidence_mode: str = "UNKNOWN"
    tier: str = "A"
    persona: str = "unknown"

    # Status
    status: ProspectStatus = ProspectStatus.PREPARED
    rendered_validated: bool = False
    approval_eligible: bool = False  # Ready to approve for send
    review_required: bool = False

    # Signals
    total_cited: int = 0
    company_cited: int = 0
    person_cited: int = 0
    newest_cited_age_days: Optional[int] = None

    # Warnings
    warnings: List[str] = field(default_factory=list)

    # Multi-site
    primary_account_id: Optional[str] = None
    site_account_id: Optional[str] = None

    # Timestamps
    generated_at: Optional[str] = None

    @property
    def warning_codes(self) -> List[str]:
        """Extract warning codes from full warning strings."""
        codes = []
        for w in self.warnings:
            if ":" in w:
                codes.append(w.split(":")[0].strip())
            else:
                codes.append(w)
        return codes

    @property
    def display_status(self) -> str:
        """Human-readable status for display."""
        if self.review_required:
            return "REVIEW"
        if self.approval_eligible:
            return "APPROVABLE"
        if self.rendered_validated:
            return "RENDERED"
        return "PREPARED"

    @property
    def is_actionable(self) -> bool:
        """Whether this artifact needs human action."""
        return self.status in (
            ProspectStatus.PREPARED,
            ProspectStatus.RENDERED,
            ProspectStatus.APPROVABLE,
            ProspectStatus.REVIEW_REQUIRED
        )

    # Backwards compatibility alias
    @property
    def promotion_eligible(self) -> bool:
        """Backwards compatibility alias for approval_eligible."""
        return self.approval_eligible

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "company_name": self.company_name,
            "contact_name": self.contact_name,
            "run_date": self.run_date,
            "confidence_mode": self.confidence_mode,
            "tier": self.tier,
            "persona": self.persona,
            "status": self.status.value,
            "rendered_validated": self.rendered_validated,
            "approval_eligible": self.approval_eligible,
            "review_required": self.review_required,
            "total_cited": self.total_cited,
            "company_cited": self.company_cited,
            "warnings": self.warnings,
            "primary_account_id": self.primary_account_id
        }


# =============================================================================
# SCANNER
# =============================================================================

class ArtifactScanner:
    """
    Scans prospecting output folder for artifacts.

    This is READ-ONLY - no writes to the filesystem.
    """

    def __init__(self, root_path: Optional[Path] = None):
        """
        Initialize scanner.

        Args:
            root_path: Root path to scan (default: PROSPECTING_OUTPUT_ROOT)
        """
        if root_path:
            self.root = Path(root_path)
        else:
            self.root = Path(os.environ.get(
                "PROSPECTING_OUTPUT_ROOT",
                DEFAULT_PROSPECTING_ROOT
            ))

        self.approval_log = self._load_approval_log()

    def _load_approval_log(self) -> Dict[str, Any]:
        """Load approval log to check approved items."""
        log_path = self.root / "approval_log.json"
        if log_path.exists():
            try:
                with open(log_path, "r") as f:
                    entries = json.load(f)
                # Index by company+contact for quick lookup
                return {
                    f"{e.get('company')}:{e.get('contact')}": e
                    for e in entries
                }
            except Exception as e:
                logger.warning(f"Could not load approval log: {e}")
        return {}

    def _is_approved(self, company: str, contact: str) -> bool:
        """Check if artifact was already approved for send."""
        key = f"{company}:{contact}"
        return key in self.approval_log

    def _parse_context_quality(
        self,
        path: Path,
        company_name: str
    ) -> Optional[ProspectArtifact]:
        """
        Parse a context_quality.json file into ProspectArtifact.

        Args:
            path: Path to context_quality.json
            company_name: Company name from folder structure

        Returns:
            ProspectArtifact or None if parsing fails
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.warning(f"Could not parse {path}: {e}")
            return None

        # Extract date and contact from filename
        # Format: YYYY-MM-DD_contactname_context_quality.json
        filename = path.name
        parts = filename.split("_")

        if len(parts) >= 3:
            run_date = parts[0]
            # Contact name is between date and "context_quality"
            contact_parts = []
            for p in parts[1:]:
                if p == "context":
                    break
                contact_parts.append(p)
            contact_name = " ".join(contact_parts).replace("-", " ").title()
        else:
            run_date = datetime.now().strftime("%Y-%m-%d")
            contact_name = "Unknown"

        # Extract from context quality data
        company_data = data.get("company", {})
        contact_data = data.get("contact", {})
        mode_data = data.get("mode", {})
        signals_data = data.get("signals", {})
        counts = signals_data.get("counts", {})
        freshness = signals_data.get("freshness", {})

        # Determine status
        review_required = contact_data.get("review_required", False)

        # Check if there's a corresponding email.md (indicates rendering)
        email_pattern = filename.replace("_context_quality.json", "_email.md")
        email_path = path.parent / email_pattern
        rendered_validated = email_path.exists()

        # Check approval eligibility (basic check without running full gate)
        warnings = signals_data.get("warnings", [])
        warning_codes = [w.split(":")[0].strip() if ":" in w else w for w in warnings]

        confidence_mode = mode_data.get("confidence_mode", "UNKNOWN")

        # Simple eligibility check (mirrors ApprovalGate logic)
        approval_eligible = (
            rendered_validated and
            confidence_mode != "GENERIC" and
            not review_required and
            "THIN_RESEARCH" not in warning_codes and
            "VENDOR_DATA_ONLY" not in warning_codes
        )

        # Check if already approved for send
        is_approved = self._is_approved(company_name, contact_name)

        # Determine display status
        if is_approved:
            status = ProspectStatus.APPROVED_FOR_SEND
        elif review_required:
            status = ProspectStatus.REVIEW_REQUIRED
        elif approval_eligible:
            status = ProspectStatus.APPROVABLE
        elif rendered_validated:
            status = ProspectStatus.RENDERED
        else:
            status = ProspectStatus.PREPARED

        return ProspectArtifact(
            company_name=company_name,
            contact_name=contact_data.get("name", contact_name),
            run_date=run_date,
            context_quality_path=path,
            email_path=email_path if email_path.exists() else None,
            drafts_folder=path.parent,
            confidence_mode=confidence_mode,
            tier=mode_data.get("tier", "A"),
            persona=contact_data.get("persona", "unknown"),
            status=status,
            rendered_validated=rendered_validated,
            approval_eligible=approval_eligible,
            review_required=review_required,
            total_cited=counts.get("total_cited", 0),
            company_cited=counts.get("company_cited", 0),
            person_cited=counts.get("person_cited", 0),
            newest_cited_age_days=freshness.get("newest_cited_age_days"),
            warnings=warnings,
            primary_account_id=company_data.get("primary_account_id"),
            site_account_id=company_data.get("site_account_id"),
            generated_at=data.get("generated_at")
        )

    def scan_all(self) -> List[ProspectArtifact]:
        """
        Scan all artifacts in the prospecting root.

        Returns:
            List of ProspectArtifact sorted by date (newest first)
        """
        artifacts = []

        if not self.root.exists():
            logger.warning(f"Prospecting root does not exist: {self.root}")
            return artifacts

        # Iterate through company folders
        for company_folder in self.root.iterdir():
            if not company_folder.is_dir():
                continue

            # Skip special folders
            if company_folder.name in ("runs", "cache", ".git"):
                continue

            company_name = company_folder.name
            drafts_folder = company_folder / "drafts"

            if not drafts_folder.exists():
                continue

            # Find all context_quality.json files
            for cq_path in drafts_folder.glob("*_context_quality.json"):
                artifact = self._parse_context_quality(cq_path, company_name)
                if artifact:
                    artifacts.append(artifact)

        # Sort by date (newest first), then company, then contact
        artifacts.sort(
            key=lambda a: (a.run_date, a.company_name, a.contact_name),
            reverse=True
        )

        return artifacts

    def scan_by_date(
        self,
        target_date: Optional[date] = None
    ) -> List[ProspectArtifact]:
        """
        Scan artifacts for a specific date.

        Args:
            target_date: Date to filter (default: today)

        Returns:
            List of ProspectArtifact for that date
        """
        if target_date is None:
            target_date = date.today()

        date_str = target_date.strftime("%Y-%m-%d")
        all_artifacts = self.scan_all()

        return [a for a in all_artifacts if a.run_date == date_str]

    def scan_actionable(self) -> List[ProspectArtifact]:
        """
        Scan only actionable artifacts (not promoted, not rejected).

        Returns:
            List of actionable ProspectArtifact
        """
        all_artifacts = self.scan_all()
        return [a for a in all_artifacts if a.is_actionable]

    def filter_artifacts(
        self,
        artifacts: List[ProspectArtifact],
        confidence: Optional[str] = None,
        persona: Optional[str] = None,
        only_approvable: bool = False,
        only_renderable: bool = False
    ) -> List[ProspectArtifact]:
        """
        Filter artifacts by various criteria.

        Args:
            artifacts: List to filter
            confidence: Filter by confidence mode
            persona: Filter by persona
            only_approvable: Only show items ready for approval
            only_renderable: Only show items ready to render

        Returns:
            Filtered list
        """
        result = artifacts

        if confidence:
            result = [a for a in result if a.confidence_mode == confidence.upper()]

        if persona:
            result = [a for a in result if a.persona == persona.lower()]

        if only_approvable:
            result = [a for a in result if a.approval_eligible]

        if only_renderable:
            result = [
                a for a in result
                if a.status == ProspectStatus.PREPARED and not a.review_required
            ]

        return result


# =============================================================================
# GROUPING UTILITIES
# =============================================================================

def group_by_company(
    artifacts: List[ProspectArtifact]
) -> Dict[str, List[ProspectArtifact]]:
    """Group artifacts by company name."""
    groups = {}
    for a in artifacts:
        if a.company_name not in groups:
            groups[a.company_name] = []
        groups[a.company_name].append(a)
    return groups


def group_by_persona(
    artifacts: List[ProspectArtifact]
) -> Dict[str, List[ProspectArtifact]]:
    """Group artifacts by persona."""
    groups = {}
    for a in artifacts:
        if a.persona not in groups:
            groups[a.persona] = []
        groups[a.persona].append(a)
    return groups


def group_by_date(
    artifacts: List[ProspectArtifact]
) -> Dict[str, List[ProspectArtifact]]:
    """Group artifacts by run date."""
    groups = {}
    for a in artifacts:
        if a.run_date not in groups:
            groups[a.run_date] = []
        groups[a.run_date].append(a)
    return groups


def group_by_primary_account(
    artifacts: List[ProspectArtifact]
) -> Dict[str, List[ProspectArtifact]]:
    """Group artifacts by primary account ID."""
    groups = {}
    for a in artifacts:
        key = a.primary_account_id or a.company_name
        if key not in groups:
            groups[key] = []
        groups[key].append(a)
    return groups
