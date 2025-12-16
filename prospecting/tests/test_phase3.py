"""
Phase 3 Tests - Daily Prospecting UX & Workflow

Tests:
1. Artifact scanner filtering
2. Review queue filtering and display
3. Interactive promotion (mocked input)
4. Inbox view rendering
5. Stats aggregation correctness
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock
from io import StringIO

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.artifact_scanner import (
    ArtifactScanner,
    ProspectArtifact,
    ProspectStatus,
    group_by_company,
    group_by_persona,
    group_by_date,
    group_by_primary_account
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_prospecting_root(tmp_path):
    """Create a temporary prospecting root with sample artifacts."""
    root = tmp_path / "agent-prospecting"
    root.mkdir()

    # Company 1: Acme Corp - two contacts
    acme = root / "acme-corp" / "drafts"
    acme.mkdir(parents=True)

    today = date.today().strftime("%Y-%m-%d")
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Acme - John Smith (HIGH confidence, promotable)
    cq1 = {
        "generated_at": datetime.now().isoformat(),
        "company": {"name": "Acme Corp", "primary_account_id": "acme-123"},
        "contact": {
            "name": "John Smith",
            "persona": "quality",
            "review_required": False
        },
        "mode": {
            "tier": "A",
            "confidence_mode": "HIGH"
        },
        "signals": {
            "counts": {
                "total_cited": 5,
                "company_cited": 3,
                "person_cited": 2,
                "total_vendor": 1
            },
            "freshness": {"newest_cited_age_days": 30},
            "warnings": []
        }
    }
    with open(acme / f"{today}_john-smith_context_quality.json", "w") as f:
        json.dump(cq1, f)
    # Create corresponding email to make it "rendered"
    (acme / f"{today}_john-smith_email.md").write_text("Subject: Test\n\nHello John")

    # Acme - Jane Doe (MEDIUM confidence, rendered but not promotable due to THIN_RESEARCH warning)
    cq2 = {
        "generated_at": datetime.now().isoformat(),
        "company": {"name": "Acme Corp", "primary_account_id": "acme-123"},
        "contact": {
            "name": "Jane Doe",
            "persona": "manufacturing",
            "review_required": False
        },
        "mode": {
            "tier": "A",
            "confidence_mode": "MEDIUM"
        },
        "signals": {
            "counts": {"total_cited": 3, "company_cited": 2, "person_cited": 1},
            "freshness": {"newest_cited_age_days": 100},
            "warnings": ["THIN_RESEARCH: only 3 signals and oldest is 100 days"]
        }
    }
    with open(acme / f"{today}_jane-doe_context_quality.json", "w") as f:
        json.dump(cq2, f)
    (acme / f"{today}_jane-doe_email.md").write_text("Subject: Test\n\nHello Jane")

    # Company 2: Beta Inc - one contact (regulatory, review required)
    beta = root / "beta-inc" / "drafts"
    beta.mkdir(parents=True)

    cq3 = {
        "generated_at": datetime.now().isoformat(),
        "company": {"name": "Beta Inc", "primary_account_id": "beta-456"},
        "contact": {
            "name": "Bob Jones",
            "persona": "regulatory",
            "review_required": True
        },
        "mode": {
            "tier": "A",
            "confidence_mode": "HIGH"
        },
        "signals": {
            "counts": {"total_cited": 4, "company_cited": 2, "person_cited": 2},
            "freshness": {"newest_cited_age_days": 15},
            "warnings": []
        }
    }
    with open(beta / f"{yesterday}_bob-jones_context_quality.json", "w") as f:
        json.dump(cq3, f)
    (beta / f"{yesterday}_bob-jones_email.md").write_text("Subject: Test\n\nHello Bob")

    # Company 3: Gamma Corp - one contact (GENERIC, prepared only)
    gamma = root / "gamma-corp" / "drafts"
    gamma.mkdir(parents=True)

    cq4 = {
        "generated_at": datetime.now().isoformat(),
        "company": {"name": "Gamma Corp"},
        "contact": {
            "name": "Alice Wong",
            "persona": "it",
            "review_required": False
        },
        "mode": {
            "tier": "B",
            "confidence_mode": "GENERIC"
        },
        "signals": {
            "counts": {"total_cited": 0, "company_cited": 0, "person_cited": 0},
            "freshness": {},
            "warnings": ["NO_CITED_SIGNALS: no cited signals"]
        }
    }
    with open(gamma / f"{today}_alice-wong_context_quality.json", "w") as f:
        json.dump(cq4, f)
    # No email - prepared only

    return root


@pytest.fixture
def scanner(temp_prospecting_root):
    """Create scanner with temp root."""
    return ArtifactScanner(root_path=temp_prospecting_root)


@pytest.fixture
def sample_artifacts(scanner):
    """Get scanned artifacts from temp root."""
    return scanner.scan_all()


# =============================================================================
# ARTIFACT SCANNER TESTS
# =============================================================================

class TestArtifactScanner:
    """Tests for ArtifactScanner core functionality."""

    def test_scan_all_finds_all_artifacts(self, scanner):
        """scan_all returns all artifacts."""
        artifacts = scanner.scan_all()
        assert len(artifacts) == 4

    def test_scan_all_sorted_by_date(self, scanner):
        """scan_all returns artifacts sorted by date (newest first)."""
        artifacts = scanner.scan_all()
        dates = [a.run_date for a in artifacts]
        assert dates == sorted(dates, reverse=True)

    def test_scan_by_date_filters_correctly(self, scanner):
        """scan_by_date returns only artifacts for that date."""
        today = date.today()
        artifacts = scanner.scan_by_date(today)

        # Should have 3 artifacts from today
        assert len(artifacts) == 3
        today_str = today.strftime("%Y-%m-%d")
        assert all(a.run_date == today_str for a in artifacts)

    def test_scan_actionable_excludes_approved(self, scanner, temp_prospecting_root):
        """scan_actionable excludes approved artifacts."""
        # Create an approval log
        # Note: company and contact names must match what scanner extracts
        # Scanner uses folder name for company and parses contact from filename
        log_path = temp_prospecting_root / "approval_log.json"
        log_entries = [
            {"company": "acme-corp", "contact": "John Smith", "timestamp": "2025-01-15T10:00:00"}
        ]
        with open(log_path, "w") as f:
            json.dump(log_entries, f)

        # Reload scanner to pick up approval log
        scanner = ArtifactScanner(root_path=temp_prospecting_root)
        actionable = scanner.scan_actionable()

        # Should exclude approved John Smith
        names = [a.contact_name for a in actionable]
        assert "John Smith" not in names

    def test_status_detection_approvable(self, sample_artifacts):
        """Artifacts with rendered email and no blockers are APPROVABLE."""
        john = next(a for a in sample_artifacts if a.contact_name == "John Smith")
        assert john.status == ProspectStatus.APPROVABLE
        assert john.approval_eligible is True

    def test_status_detection_rendered(self, sample_artifacts):
        """Artifacts with warnings are RENDERED but not approvable."""
        jane = next(a for a in sample_artifacts if a.contact_name == "Jane Doe")
        assert jane.status == ProspectStatus.RENDERED
        assert jane.rendered_validated is True
        assert jane.approval_eligible is False  # Due to THIN_RESEARCH warning

    def test_status_detection_review_required(self, sample_artifacts):
        """Artifacts with review_required are REVIEW_REQUIRED."""
        bob = next(a for a in sample_artifacts if a.contact_name == "Bob Jones")
        assert bob.status == ProspectStatus.REVIEW_REQUIRED
        assert bob.review_required is True

    def test_status_detection_prepared(self, sample_artifacts):
        """Artifacts without email are PREPARED."""
        alice = next(a for a in sample_artifacts if a.contact_name == "Alice Wong")
        assert alice.status == ProspectStatus.PREPARED
        assert alice.rendered_validated is False


# =============================================================================
# FILTER TESTS
# =============================================================================

class TestArtifactFiltering:
    """Tests for artifact filtering."""

    def test_filter_by_confidence(self, scanner, sample_artifacts):
        """Filter by confidence mode works."""
        filtered = scanner.filter_artifacts(sample_artifacts, confidence="HIGH")
        assert len(filtered) == 2
        assert all(a.confidence_mode == "HIGH" for a in filtered)

    def test_filter_by_persona(self, scanner, sample_artifacts):
        """Filter by persona works."""
        filtered = scanner.filter_artifacts(sample_artifacts, persona="quality")
        assert len(filtered) == 1
        assert filtered[0].persona == "quality"

    def test_filter_only_approvable(self, scanner, sample_artifacts):
        """Filter only_approvable returns only approvable items."""
        filtered = scanner.filter_artifacts(sample_artifacts, only_approvable=True)
        assert len(filtered) == 1
        assert filtered[0].contact_name == "John Smith"
        assert all(a.approval_eligible for a in filtered)

    def test_filter_only_renderable(self, scanner, sample_artifacts):
        """Filter only_renderable returns prepared items without review_required."""
        filtered = scanner.filter_artifacts(sample_artifacts, only_renderable=True)
        # Alice is prepared but GENERIC, Bob is review_required
        # Only Alice should match (prepared and not review_required)
        assert len(filtered) == 1
        assert filtered[0].contact_name == "Alice Wong"

    def test_filter_combined(self, scanner, sample_artifacts):
        """Multiple filters combine correctly."""
        filtered = scanner.filter_artifacts(
            sample_artifacts,
            confidence="HIGH",
            persona="regulatory"
        )
        assert len(filtered) == 1
        assert filtered[0].contact_name == "Bob Jones"


# =============================================================================
# GROUPING TESTS
# =============================================================================

class TestGrouping:
    """Tests for grouping utilities."""

    def test_group_by_company(self, sample_artifacts):
        """group_by_company groups correctly."""
        groups = group_by_company(sample_artifacts)

        # Company name comes from folder name (sanitized)
        assert "acme-corp" in groups
        assert len(groups["acme-corp"]) == 2

        assert "beta-inc" in groups
        assert len(groups["beta-inc"]) == 1

    def test_group_by_persona(self, sample_artifacts):
        """group_by_persona groups correctly."""
        groups = group_by_persona(sample_artifacts)

        assert "quality" in groups
        assert "manufacturing" in groups
        assert "regulatory" in groups
        assert "it" in groups

    def test_group_by_date(self, sample_artifacts):
        """group_by_date groups correctly."""
        groups = group_by_date(sample_artifacts)

        today = date.today().strftime("%Y-%m-%d")
        yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        assert today in groups
        assert len(groups[today]) == 3

        assert yesterday in groups
        assert len(groups[yesterday]) == 1

    def test_group_by_primary_account(self, sample_artifacts):
        """group_by_primary_account groups by primary account ID."""
        groups = group_by_primary_account(sample_artifacts)

        assert "acme-123" in groups
        assert len(groups["acme-123"]) == 2

        assert "beta-456" in groups
        assert len(groups["beta-456"]) == 1


# =============================================================================
# REVIEW QUEUE TESTS
# =============================================================================

class TestReviewQueue:
    """Tests for review_queue.py functionality."""

    def test_format_queue_header(self):
        """Queue header formats correctly."""
        from scripts.review_queue import format_queue_header

        today = date.today()
        header = format_queue_header(today, 5)

        assert "Daily Review Queue" in header
        assert today.strftime("%Y-%m-%d") in header
        assert "5 item(s)" in header

    def test_format_queue_header_empty(self):
        """Queue header handles empty queue."""
        from scripts.review_queue import format_queue_header

        header = format_queue_header(date.today(), 0)
        assert "No items to review" in header

    def test_status_icon_approvable(self):
        """Approvable items get checkmark icon."""
        from scripts.review_queue import get_status_icon

        artifact = ProspectArtifact(
            company_name="Test",
            contact_name="Test",
            run_date="2025-01-15",
            context_quality_path=Path("/tmp/test.json"),
            approval_eligible=True
        )

        assert get_status_icon(artifact) == "✓"

    def test_status_icon_review_required(self):
        """Review required items get warning icon."""
        from scripts.review_queue import get_status_icon

        artifact = ProspectArtifact(
            company_name="Test",
            contact_name="Test",
            run_date="2025-01-15",
            context_quality_path=Path("/tmp/test.json"),
            review_required=True
        )

        assert get_status_icon(artifact) == "⚠"

    def test_format_action_line_approvable(self):
        """Approvable items show 'Ready to approve'."""
        from scripts.review_queue import format_action_line

        artifact = ProspectArtifact(
            company_name="Test",
            contact_name="Test",
            run_date="2025-01-15",
            context_quality_path=Path("/tmp/test.json"),
            approval_eligible=True
        )

        action = format_action_line(artifact)
        assert "Ready to approve" in action

    def test_format_action_line_review_required(self):
        """Review required items show 'Manual decision only'."""
        from scripts.review_queue import format_action_line

        artifact = ProspectArtifact(
            company_name="Test",
            contact_name="Test",
            run_date="2025-01-15",
            context_quality_path=Path("/tmp/test.json"),
            review_required=True
        )

        action = format_action_line(artifact)
        assert "Manual decision only" in action


# =============================================================================
# INBOX VIEW TESTS
# =============================================================================

class TestInboxView:
    """Tests for inbox_view.py functionality."""

    def test_status_indicator_approvable(self):
        """Approvable items get '+' indicator."""
        from scripts.inbox_view import get_status_indicator

        artifact = ProspectArtifact(
            company_name="Test",
            contact_name="Test",
            run_date="2025-01-15",
            context_quality_path=Path("/tmp/test.json"),
            approval_eligible=True
        )

        assert get_status_indicator(artifact) == "+"

    def test_status_indicator_rendered(self):
        """Rendered items get 'R' indicator."""
        from scripts.inbox_view import get_status_indicator

        artifact = ProspectArtifact(
            company_name="Test",
            contact_name="Test",
            run_date="2025-01-15",
            context_quality_path=Path("/tmp/test.json"),
            rendered_validated=True,
            approval_eligible=False
        )

        assert get_status_indicator(artifact) == "R"

    def test_format_persona_short(self):
        """Personas format to 3-letter codes."""
        from scripts.inbox_view import format_persona_short

        assert format_persona_short("quality") == "QUA"
        assert format_persona_short("manufacturing") == "MFG"
        assert format_persona_short("regulatory") == "REG"
        assert format_persona_short("it") == "IT "

    def test_format_confidence_short(self):
        """Confidence modes format to 2-letter codes."""
        from scripts.inbox_view import format_confidence_short

        assert format_confidence_short("HIGH") == "HI"
        assert format_confidence_short("MEDIUM") == "MD"
        assert format_confidence_short("GENERIC") == "GN"

    def test_format_inbox_row(self):
        """Inbox row formats correctly."""
        from scripts.inbox_view import format_inbox_row

        artifact = ProspectArtifact(
            company_name="Acme Corp",
            contact_name="John Smith",
            run_date="2025-01-15",
            context_quality_path=Path("/tmp/test.json"),
            persona="quality",
            confidence_mode="HIGH",
            approval_eligible=True
        )

        row = format_inbox_row(artifact)

        assert "[+]" in row
        assert "2025-01-15" in row
        assert "Acme Corp" in row
        assert "John Smith" in row
        assert "QUA" in row
        assert "HI" in row
        assert "APPROVE!" in row

    def test_format_inbox_complete(self, sample_artifacts):
        """Complete inbox formats with header and footer."""
        from scripts.inbox_view import format_inbox

        output = format_inbox(sample_artifacts)

        assert "PROSPECTING INBOX" in output
        assert "Legend:" in output
        assert "Total:" in output
        assert "Approvable:" in output

    def test_format_inbox_with_limit(self, sample_artifacts):
        """Inbox respects limit parameter."""
        from scripts.inbox_view import format_inbox

        output = format_inbox(sample_artifacts, limit=2)

        assert "... and" in output
        assert "more items" in output


# =============================================================================
# STATS TESTS
# =============================================================================

class TestProspectingStats:
    """Tests for prospecting_stats.py functionality."""

    def test_calculate_stats_counts(self, sample_artifacts):
        """Stats calculation counts correctly."""
        from scripts.prospecting_stats import calculate_stats

        stats = calculate_stats(sample_artifacts, days=30)

        assert stats["total_prepared"] == 4
        assert stats["rendered"] == 3  # John, Jane, Bob have emails
        assert stats["prepared_only"] == 1  # Alice has no email

    def test_calculate_stats_persona_distribution(self, sample_artifacts):
        """Stats tracks persona distribution."""
        from scripts.prospecting_stats import calculate_stats

        stats = calculate_stats(sample_artifacts, days=30)

        assert "quality" in stats["persona_counts"]
        assert "manufacturing" in stats["persona_counts"]
        assert "regulatory" in stats["persona_counts"]
        assert "it" in stats["persona_counts"]

    def test_calculate_stats_confidence_distribution(self, sample_artifacts):
        """Stats tracks confidence distribution."""
        from scripts.prospecting_stats import calculate_stats

        stats = calculate_stats(sample_artifacts, days=30)

        assert "HIGH" in stats["confidence_counts"]
        assert stats["confidence_counts"]["HIGH"] == 2

    def test_calculate_stats_warning_counts(self, sample_artifacts):
        """Stats tracks warning distribution."""
        from scripts.prospecting_stats import calculate_stats

        stats = calculate_stats(sample_artifacts, days=30)

        # Jane has OLD_SIGNALS_PRESENT, Alice has NO_CITED_SIGNALS
        assert len(stats["warning_counts"]) >= 1

    def test_calculate_stats_stalled_percentage(self, sample_artifacts):
        """Stats calculates stalled percentage."""
        from scripts.prospecting_stats import calculate_stats

        stats = calculate_stats(sample_artifacts, days=30)

        # stalled_pct should be calculated
        assert "stalled_pct" in stats
        assert isinstance(stats["stalled_pct"], (int, float))

    def test_format_mini_stats(self, sample_artifacts):
        """Mini stats format is one line."""
        from scripts.prospecting_stats import calculate_stats, format_mini_stats

        stats = calculate_stats(sample_artifacts, days=30)
        mini = format_mini_stats(stats)

        assert "Prepared:" in mini
        assert "Rendered:" in mini
        assert "Approved:" in mini
        assert "Stalled:" in mini
        assert mini.count("\n") == 0  # Single line

    def test_format_stats_report_sections(self, sample_artifacts):
        """Full stats report contains all sections."""
        from scripts.prospecting_stats import calculate_stats, format_stats_report

        stats = calculate_stats(sample_artifacts, days=30)
        report = format_stats_report(stats)

        assert "PROSPECTING STATS" in report
        assert "SUMMARY" in report
        assert "STALLED ITEMS" in report
        assert "CONFIDENCE DISTRIBUTION" in report
        assert "PERSONA DISTRIBUTION" in report
        assert "DAILY BREAKDOWN" in report


# =============================================================================
# INTERACTIVE APPROVAL TESTS
# =============================================================================

class TestInteractiveApproval:
    """Tests for interactive approval mode."""

    def test_show_email_preview(self, temp_prospecting_root):
        """Email preview reads and formats correctly."""
        from scripts.approve_for_send import show_email_preview

        # Create test artifacts dict
        email_path = temp_prospecting_root / "acme-corp" / "drafts" / f"{date.today().strftime('%Y-%m-%d')}_john-smith_email.md"
        artifacts = {"email_md": email_path}

        preview = show_email_preview(artifacts)

        assert "Subject: Test" in preview
        assert "Hello John" in preview

    def test_show_email_preview_missing(self):
        """Email preview handles missing file."""
        from scripts.approve_for_send import show_email_preview

        artifacts = {}
        preview = show_email_preview(artifacts)

        assert "No email preview available" in preview

    def test_format_interactive_display(self):
        """Interactive display formats all sections."""
        from scripts.approve_for_send import format_interactive_display
        from src.approval_rules import ApprovalEligibilityResult

        context_quality = {
            "company": {"name": "Test Corp"},
            "contact": {"name": "John Smith", "persona": "quality"},
            "mode": {"confidence_mode": "HIGH", "tier": "A"},
            "signals": {
                "counts": {"total_cited": 5, "company_cited": 3, "person_cited": 2},
                "freshness": {},
                "warnings": []
            }
        }

        eligibility = ApprovalEligibilityResult(
            eligible=True,
            reasons=[],
            warnings_present=[],
            can_force=False
        )

        display = format_interactive_display(context_quality, {}, eligibility)

        assert "APPROVE FOR SEND" in display
        assert "Contact: John Smith" in display
        assert "Company: Test Corp" in display
        assert "CONTEXT QUALITY:" in display
        assert "ELIGIBILITY:" in display
        assert "EMAIL PREVIEW:" in display

    def test_interactive_mode_eligible_confirmed(self, temp_prospecting_root):
        """Interactive mode proceeds when confirmed."""
        from scripts.approve_for_send import run_interactive_mode
        from src.approval_rules import ApprovalEligibilityResult

        context_quality = {
            "company": {"name": "Test Corp"},
            "contact": {"name": "John Smith", "persona": "quality"},
            "mode": {"confidence_mode": "HIGH", "tier": "A"},
            "signals": {"counts": {"total_cited": 5}, "warnings": []}
        }

        eligibility = ApprovalEligibilityResult(
            eligible=True,
            reasons=[],
            warnings_present=[],
            can_force=False
        )

        approved_folder = temp_prospecting_root / "acme-corp" / "approved" / "john-smith"

        # Mock input to confirm
        with patch('builtins.input', side_effect=['y', '']):  # Confirm, no note
            result = run_interactive_mode(
                context_quality=context_quality,
                artifacts={},
                eligibility=eligibility,
                approved_folder=approved_folder,
                prospecting_root=str(temp_prospecting_root),
                persona_diagnostics=None,
                force=False
            )

        # Should execute approval - result has "success" key from execute_approval
        assert result["success"] is True

    def test_interactive_mode_declined(self, temp_prospecting_root):
        """Interactive mode aborts when declined."""
        from scripts.approve_for_send import run_interactive_mode
        from src.approval_rules import ApprovalEligibilityResult

        context_quality = {
            "company": {"name": "Test Corp"},
            "contact": {"name": "John Smith"},
            "mode": {"confidence_mode": "HIGH"},
            "signals": {"counts": {}, "warnings": []}
        }

        eligibility = ApprovalEligibilityResult(
            eligible=True,
            reasons=[],
            warnings_present=[],
            can_force=False
        )

        approved_folder = temp_prospecting_root / "acme-corp" / "approved" / "john-smith"

        # Mock input to decline
        with patch('builtins.input', return_value='n'):
            result = run_interactive_mode(
                context_quality=context_quality,
                artifacts={},
                eligibility=eligibility,
                approved_folder=approved_folder,
                prospecting_root=str(temp_prospecting_root),
                persona_diagnostics=None,
                force=False
            )

        assert result["success"] is False
        assert result["reason"] == "user_cancelled"

    def test_interactive_mode_not_eligible_no_force(self, temp_prospecting_root):
        """Interactive mode shows not eligible when ineligible and no force."""
        from scripts.approve_for_send import run_interactive_mode
        from src.approval_rules import ApprovalEligibilityResult

        context_quality = {
            "company": {"name": "Test Corp"},
            "contact": {"name": "John Smith"},
            "mode": {"confidence_mode": "GENERIC"},
            "signals": {"counts": {}, "warnings": []}
        }

        eligibility = ApprovalEligibilityResult(
            eligible=False,
            reasons=["GENERIC confidence not allowed"],
            warnings_present=[],
            can_force=False
        )

        approved_folder = temp_prospecting_root / "acme-corp" / "approved" / "john-smith"

        # Should not even ask for confirmation
        with patch('builtins.input', return_value='y') as mock_input:
            result = run_interactive_mode(
                context_quality=context_quality,
                artifacts={},
                eligibility=eligibility,
                approved_folder=approved_folder,
                prospecting_root=str(temp_prospecting_root),
                persona_diagnostics=None,
                force=False
            )

        assert result["success"] is False
        assert result["reason"] == "not_eligible"


# =============================================================================
# PROSPECT ARTIFACT DATA CLASS TESTS
# =============================================================================

class TestProspectArtifact:
    """Tests for ProspectArtifact dataclass."""

    def test_warning_codes_extraction(self):
        """warning_codes extracts codes from full strings."""
        artifact = ProspectArtifact(
            company_name="Test",
            contact_name="Test",
            run_date="2025-01-15",
            context_quality_path=Path("/tmp/test.json"),
            warnings=[
                "OLD_SIGNALS_PRESENT: signals are stale",
                "THIN_RESEARCH: only 2 signals"
            ]
        )

        codes = artifact.warning_codes
        assert "OLD_SIGNALS_PRESENT" in codes
        assert "THIN_RESEARCH" in codes

    def test_display_status_approvable(self):
        """display_status shows APPROVABLE for eligible items."""
        artifact = ProspectArtifact(
            company_name="Test",
            contact_name="Test",
            run_date="2025-01-15",
            context_quality_path=Path("/tmp/test.json"),
            approval_eligible=True
        )

        assert artifact.display_status == "APPROVABLE"

    def test_display_status_review(self):
        """display_status shows REVIEW for review_required items."""
        artifact = ProspectArtifact(
            company_name="Test",
            contact_name="Test",
            run_date="2025-01-15",
            context_quality_path=Path("/tmp/test.json"),
            review_required=True
        )

        assert artifact.display_status == "REVIEW"

    def test_is_actionable(self):
        """is_actionable returns True for non-approved/rejected items."""
        approvable = ProspectArtifact(
            company_name="Test",
            contact_name="Test",
            run_date="2025-01-15",
            context_quality_path=Path("/tmp/test.json"),
            status=ProspectStatus.APPROVABLE
        )
        assert approvable.is_actionable is True

        approved = ProspectArtifact(
            company_name="Test",
            contact_name="Test",
            run_date="2025-01-15",
            context_quality_path=Path("/tmp/test.json"),
            status=ProspectStatus.APPROVED_FOR_SEND
        )
        assert approved.is_actionable is False

    def test_to_dict(self):
        """to_dict serializes correctly."""
        artifact = ProspectArtifact(
            company_name="Test Corp",
            contact_name="John Smith",
            run_date="2025-01-15",
            context_quality_path=Path("/tmp/test.json"),
            confidence_mode="HIGH",
            persona="quality",
            status=ProspectStatus.APPROVABLE
        )

        d = artifact.to_dict()

        assert d["company_name"] == "Test Corp"
        assert d["contact_name"] == "John Smith"
        assert d["confidence_mode"] == "HIGH"
        assert d["status"] == "approvable"


# =============================================================================
# APPROVAL DESTINATION TESTS
# =============================================================================

class TestApprovalDestination:
    """Tests asserting approved artifacts stay in 02_Prospecting, NOT 01_Accounts.

    This is a critical semantic boundary: Prospecting ≠ Opportunity.
    Approved drafts are ready to send, but remain in the prospecting workspace
    until a human decides to manually promote to active accounts.
    """

    def test_get_approved_folder_stays_in_prospecting(self, tmp_path):
        """Approved folder path must stay within prospecting root, not accounts."""
        from scripts.approve_for_send import get_approved_folder

        prospecting_root = tmp_path / "02_Prospecting" / "agent-prospecting"
        prospecting_root.mkdir(parents=True)

        # Get the approved folder for a test company/contact
        approved_folder = get_approved_folder(
            company="Acme Corp",
            contact="John Smith",
            prospecting_root=prospecting_root
        )

        # Assert: path is within 02_Prospecting, NOT 01_Accounts
        path_str = str(approved_folder)
        assert "02_Prospecting" in path_str or "agent-prospecting" in path_str
        assert "01_Accounts" not in path_str
        assert "_Active" not in path_str

        # Assert: path structure is correct
        assert "approved" in path_str
        assert "acme-corp" in path_str.lower() or "acme_corp" in path_str.lower()

    def test_execute_approval_does_not_write_to_accounts(self, tmp_path):
        """Executing an approval must NOT create anything in 01_Accounts/_Active."""
        from scripts.approve_for_send import execute_approval
        from pathlib import Path

        # Set up directory structure
        prospecting_root = tmp_path / "02_Prospecting" / "agent-prospecting"
        accounts_root = tmp_path / "01_Accounts" / "_Active"
        prospecting_root.mkdir(parents=True)
        accounts_root.mkdir(parents=True)

        # Approved folder should be within prospecting
        approved_folder = prospecting_root / "acme-corp" / "approved" / "john-smith"

        context_quality = {
            "company": {"name": "Acme Corp"},
            "contact": {"name": "John Smith", "persona": "quality"},
            "mode": {"confidence_mode": "HIGH", "tier": "A"},
            "signals": {"counts": {"total_cited": 5}, "warnings": []}
        }

        # Execute approval
        result = execute_approval(
            artifacts={},
            context_quality=context_quality,
            persona_diagnostics=None,
            approved_folder=approved_folder,
            prospecting_root=str(prospecting_root),
            dry_run=False
        )

        assert result["success"] is True

        # CRITICAL ASSERTION: Nothing was created in 01_Accounts/_Active
        accounts_contents = list(accounts_root.rglob("*"))
        assert len(accounts_contents) == 0, (
            f"Approval should NOT write to 01_Accounts/_Active! "
            f"Found: {accounts_contents}"
        )

        # Verify artifacts were created in 02_Prospecting
        assert approved_folder.exists()
        assert (approved_folder / "approval_metadata.json").exists()

    def test_approval_log_stays_in_prospecting_root(self, tmp_path):
        """The approval_log.json must be created in prospecting root, not accounts."""
        from scripts.approve_for_send import execute_approval
        from pathlib import Path

        # Set up directory structure
        prospecting_root = tmp_path / "02_Prospecting" / "agent-prospecting"
        accounts_root = tmp_path / "01_Accounts" / "_Active"
        prospecting_root.mkdir(parents=True)
        accounts_root.mkdir(parents=True)

        approved_folder = prospecting_root / "acme-corp" / "approved" / "john-smith"

        context_quality = {
            "company": {"name": "Acme Corp"},
            "contact": {"name": "John Smith", "persona": "quality"},
            "mode": {"confidence_mode": "HIGH", "tier": "A"},
            "signals": {"counts": {"total_cited": 5}, "warnings": []}
        }

        # Execute approval (which also writes to approval_log.json)
        result = execute_approval(
            artifacts={},
            context_quality=context_quality,
            persona_diagnostics=None,
            approved_folder=approved_folder,
            prospecting_root=str(prospecting_root),
            dry_run=False
        )

        assert result["success"] is True

        # CRITICAL ASSERTION: Log is in prospecting, not accounts
        assert (prospecting_root / "approval_log.json").exists()

        # No files in accounts
        accounts_contents = list(accounts_root.rglob("*"))
        assert len(accounts_contents) == 0, (
            f"approval_log.json should NOT be in 01_Accounts! "
            f"Found: {accounts_contents}"
        )
