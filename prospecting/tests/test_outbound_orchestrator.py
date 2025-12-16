"""
Tests for Outbound Orchestrator

Tests cover:
1. Loading CSV and JSON accounts input
2. Skipping accounts with recent drafts
3. Respecting max_total_drafts and max_drafts_per_account caps
4. Behavior when ZoomInfo env missing (should not crash)
5. Output dashboard creation under output_root
"""

import os
import sys
import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.outbound_orchestrator import (
    OutboundOrchestrator,
    OutboundConfig,
    AccountRecord,
    ContactResult,
    AccountResult,
    RunSummary,
    get_personas_for_account,
    PERSONA_ROLE_KEYWORDS,
    DEFAULT_PERSONAS
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_csv_file(temp_dir):
    """Create a sample CSV accounts file."""
    csv_path = temp_dir / "accounts.csv"
    csv_content = """company_name,score,tier,domain,tags
Acme Corp,92,A,acme.com,"quality_focused,regulatory"
Beta Inc,88,A,beta.com,operations_focused
Gamma LLC,75,B,gamma.com,
Delta Co,95,A,delta.com,it_focused
Epsilon Ltd,60,B,epsilon.com,
"""
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON accounts file."""
    json_path = temp_dir / "accounts.json"
    json_data = {
        "accounts": [
            {"company_name": "Acme Corp", "score": 92, "tier": "A"},
            {"company_name": "Beta Inc", "score": 88, "tier": "A"},
            {"company_name": "Gamma LLC", "score": 75, "tier": "B"},
            {"company_name": "Delta Co", "score": 95, "tier": "A"},
            {"company_name": "Epsilon Ltd", "score": 60, "tier": "B"}
        ]
    }
    json_path.write_text(json.dumps(json_data))
    return json_path


@pytest.fixture
def json_list_format(temp_dir):
    """Create a JSON file with list format (not object with accounts key)."""
    json_path = temp_dir / "accounts_list.json"
    json_data = [
        {"company_name": "Company A", "score": 100},
        {"company_name": "Company B", "score": 90}
    ]
    json_path.write_text(json.dumps(json_data))
    return json_path


@pytest.fixture
def config_factory(temp_dir):
    """Factory to create OutboundConfig with temp output root."""
    def _create_config(accounts_path, **kwargs):
        defaults = {
            "accounts_path": accounts_path,
            "top_n": 10,
            "max_drafts_per_account": 3,
            "max_total_drafts": 20,
            "tier": "A",
            "mode": "hybrid",
            "output_root": temp_dir,
            "dry_run": True  # Default to dry run for tests
        }
        defaults.update(kwargs)
        return OutboundConfig(**defaults)
    return _create_config


# =============================================================================
# TEST: ACCOUNT LOADING
# =============================================================================

class TestAccountLoading:
    """Tests for loading accounts from CSV and JSON."""

    def test_load_csv_accounts(self, sample_csv_file, config_factory):
        """Test loading accounts from CSV file."""
        config = config_factory(sample_csv_file)

        # Set environment to avoid real path resolver
        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(config.output_root)}):
            orchestrator = OutboundOrchestrator(config)
            accounts = orchestrator.load_accounts(config.accounts_path)

        assert len(accounts) == 5
        assert accounts[0].company_name == "Acme Corp"
        assert accounts[0].score == 92
        assert accounts[0].tier == "A"
        assert "quality_focused" in accounts[0].signal_tags

    def test_load_json_accounts(self, sample_json_file, config_factory):
        """Test loading accounts from JSON file."""
        config = config_factory(sample_json_file)

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(config.output_root)}):
            orchestrator = OutboundOrchestrator(config)
            accounts = orchestrator.load_accounts(config.accounts_path)

        assert len(accounts) == 5
        assert accounts[0].company_name == "Acme Corp"
        assert accounts[0].score == 92

    def test_load_json_list_format(self, json_list_format, config_factory):
        """Test loading JSON in list format (not object with accounts key)."""
        config = config_factory(json_list_format)

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(config.output_root)}):
            orchestrator = OutboundOrchestrator(config)
            accounts = orchestrator.load_accounts(config.accounts_path)

        assert len(accounts) == 2
        assert accounts[0].company_name == "Company A"
        assert accounts[0].score == 100

    def test_load_nonexistent_file(self, temp_dir, config_factory):
        """Test that loading nonexistent file raises FileNotFoundError."""
        config = config_factory(temp_dir / "nonexistent.csv")

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(config.output_root)}):
            orchestrator = OutboundOrchestrator(config)

            with pytest.raises(FileNotFoundError):
                orchestrator.load_accounts(config.accounts_path)

    def test_load_unsupported_format(self, temp_dir, config_factory):
        """Test that unsupported file format raises ValueError."""
        txt_file = temp_dir / "accounts.txt"
        txt_file.write_text("some content")
        config = config_factory(txt_file)

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(config.output_root)}):
            orchestrator = OutboundOrchestrator(config)

            with pytest.raises(ValueError, match="Unsupported file format"):
                orchestrator.load_accounts(config.accounts_path)


# =============================================================================
# TEST: ACCOUNT SELECTION
# =============================================================================

class TestAccountSelection:
    """Tests for account selection and filtering."""

    def test_select_top_n(self, sample_csv_file, config_factory):
        """Test selecting top N accounts by score."""
        config = config_factory(sample_csv_file, top_n=3)

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(config.output_root)}):
            orchestrator = OutboundOrchestrator(config)
            accounts = orchestrator.load_accounts(config.accounts_path)
            selected = orchestrator.select_accounts(accounts, top_n=3)

        assert len(selected) == 3
        # Should be sorted by score descending
        assert selected[0].company_name == "Delta Co"  # Score 95
        assert selected[1].company_name == "Acme Corp"  # Score 92
        assert selected[2].company_name == "Beta Inc"  # Score 88

    def test_select_by_tier(self, sample_csv_file, config_factory):
        """Test filtering accounts by tier."""
        config = config_factory(sample_csv_file)

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(config.output_root)}):
            orchestrator = OutboundOrchestrator(config)
            accounts = orchestrator.load_accounts(config.accounts_path)

            # Select only tier A
            selected_a = orchestrator.select_accounts(accounts, top_n=10, tier_filter="A")
            assert len(selected_a) == 3
            assert all(a.tier == "A" for a in selected_a)

            # Select only tier B
            selected_b = orchestrator.select_accounts(accounts, top_n=10, tier_filter="B")
            assert len(selected_b) == 2
            assert all(a.tier == "B" for a in selected_b)


# =============================================================================
# TEST: SKIP RECENT DRAFTS
# =============================================================================

class TestSkipRecentDrafts:
    """Tests for skipping accounts with recent drafts."""

    def test_skip_account_with_recent_draft(self, temp_dir, config_factory):
        """Test that accounts with recent drafts are skipped."""
        # Create account folder with recent draft
        company_folder = temp_dir / "Acme-Corp" / "drafts"
        company_folder.mkdir(parents=True)
        draft_file = company_folder / "2024-01-15_john_smith_email.md"
        draft_file.write_text("draft content")

        # Create sample accounts file
        accounts_file = temp_dir / "accounts.csv"
        accounts_file.write_text("company_name,score\nAcme Corp,90\n")

        config = config_factory(accounts_file, since_days=7)

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(temp_dir)}):
            orchestrator = OutboundOrchestrator(config)
            account = AccountRecord(company_name="Acme Corp", score=90)

            should_skip, reason = orchestrator.should_skip_account(account, since_days=7)

        assert should_skip is True
        assert "Draft exists within 7 days" in reason

    def test_no_skip_without_recent_draft(self, temp_dir, config_factory):
        """Test that accounts without recent drafts are not skipped."""
        accounts_file = temp_dir / "accounts.csv"
        accounts_file.write_text("company_name,score\nNew Corp,90\n")

        config = config_factory(accounts_file)

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(temp_dir)}):
            orchestrator = OutboundOrchestrator(config)
            account = AccountRecord(company_name="New Corp", score=90)

            should_skip, reason = orchestrator.should_skip_account(account, since_days=7)

        assert should_skip is False
        assert reason is None


# =============================================================================
# TEST: CAPS AND LIMITS
# =============================================================================

class TestCapsAndLimits:
    """Tests for draft caps and limits."""

    def test_max_total_drafts_cap(self, temp_dir, config_factory):
        """Test that max_total_drafts cap is respected."""
        accounts_file = temp_dir / "accounts.csv"
        accounts_file.write_text("""company_name,score
Company1,100
Company2,90
Company3,80
""")

        config = config_factory(
            accounts_file,
            max_total_drafts=2,
            max_drafts_per_account=10,
            dry_run=False
        )

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(temp_dir)}):
            orchestrator = OutboundOrchestrator(config)

            # Mock the methods that do actual work
            with patch.object(orchestrator, 'find_contacts') as mock_find:
                with patch.object(orchestrator, 'run_prospect_pipeline') as mock_pipeline:
                    with patch.object(orchestrator, 'verify_draft_quality') as mock_verify:
                        # Return 3 contacts per company
                        mock_find.return_value = [
                            {"name": "John Doe", "title": "Quality Director", "first_name": "John", "last_name": "Doe"},
                            {"name": "Jane Smith", "title": "VP Ops", "first_name": "Jane", "last_name": "Smith"},
                            {"name": "Bob Wilson", "title": "IT Director", "first_name": "Bob", "last_name": "Wilson"}
                        ]

                        # Pipeline always succeeds
                        mock_pipeline.return_value = (
                            str(temp_dir / "draft.json"),
                            {"status": "success", "variants": [{"passed_validation": True}]}
                        )

                        # Quality always passes
                        mock_verify.return_value = (True, [])

                        # Mock ZoomInfo as available
                        orchestrator._zoominfo_available = True
                        orchestrator._zoominfo_client = MagicMock()

                        result = orchestrator.run()

        # Should have stopped at max_total_drafts=2
        assert orchestrator.total_drafts_generated <= 2
        assert result.summary.prepared_for_rendering <= 2

    def test_max_drafts_per_account_cap(self, temp_dir, config_factory):
        """Test that max_drafts_per_account cap is respected."""
        accounts_file = temp_dir / "accounts.csv"
        accounts_file.write_text("company_name,score\nSingle Corp,100\n")

        config = config_factory(
            accounts_file,
            top_n=1,
            max_drafts_per_account=2,
            max_total_drafts=100,
            dry_run=False
        )

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(temp_dir)}):
            orchestrator = OutboundOrchestrator(config)

            with patch.object(orchestrator, 'find_contacts') as mock_find:
                with patch.object(orchestrator, 'run_prospect_pipeline') as mock_pipeline:
                    with patch.object(orchestrator, 'verify_draft_quality') as mock_verify:
                        # Return 5 contacts
                        mock_find.return_value = [
                            {"name": f"Contact {i}", "title": "Title", "first_name": f"Contact{i}", "last_name": "Name"}
                            for i in range(5)
                        ]

                        mock_pipeline.return_value = (
                            str(temp_dir / "draft.json"),
                            {"status": "success", "variants": [{"passed_validation": True}]}
                        )
                        mock_verify.return_value = (True, [])

                        orchestrator._zoominfo_available = True
                        orchestrator._zoominfo_client = MagicMock()

                        result = orchestrator.run()

        # Should have stopped at 2 for this account
        if result.accounts:
            account = result.accounts[0]
            accepted_count = sum(1 for c in account.contacts if c.status == "prepared_for_rendering")
            assert accepted_count <= 2


# =============================================================================
# TEST: ZOOMINFO UNAVAILABILITY
# =============================================================================

class TestZoomInfoUnavailable:
    """Tests for behavior when ZoomInfo is unavailable."""

    def test_orchestrator_runs_without_zoominfo(self, sample_csv_file, config_factory):
        """Test that orchestrator runs (doesn't crash) when ZoomInfo is missing."""
        config = config_factory(sample_csv_file, dry_run=False)

        # Clear ZoomInfo env vars
        env_without_zoominfo = {
            k: v for k, v in os.environ.items()
            if not k.startswith("ZOOMINFO")
        }
        env_without_zoominfo["PROSPECTING_OUTPUT_ROOT"] = str(config.output_root)

        with patch.dict(os.environ, env_without_zoominfo, clear=True):
            orchestrator = OutboundOrchestrator(config)
            result = orchestrator.run()

        # Should not crash
        assert result is not None
        # All accounts should be skipped due to no ZoomInfo
        assert result.summary.accounts_skipped > 0

    def test_zoominfo_unavailable_logged_in_dashboard(self, sample_csv_file, config_factory):
        """Test that ZoomInfo unavailability is logged in dashboard."""
        config = config_factory(sample_csv_file, top_n=1, dry_run=False)

        env_without_zoominfo = {
            k: v for k, v in os.environ.items()
            if not k.startswith("ZOOMINFO")
        }
        env_without_zoominfo["PROSPECTING_OUTPUT_ROOT"] = str(config.output_root)

        with patch.dict(os.environ, env_without_zoominfo, clear=True):
            orchestrator = OutboundOrchestrator(config)
            result = orchestrator.run()

        # Should have skipped with reason about ZoomInfo
        assert any(
            "ZoomInfo" in skip.get("reason", "")
            for skip in result.skipped_accounts
        )


# =============================================================================
# TEST: DASHBOARD OUTPUT
# =============================================================================

class TestDashboardOutput:
    """Tests for dashboard output creation."""

    def test_dashboard_files_created(self, sample_csv_file, config_factory):
        """Test that dashboard MD and JSON files are created."""
        config = config_factory(sample_csv_file, dry_run=False)

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(config.output_root)}):
            orchestrator = OutboundOrchestrator(config)

            # Mock to avoid real processing
            orchestrator._zoominfo_available = False

            result = orchestrator.run()

        # Check files exist
        runs_folder = config.output_root / "runs"
        date_str = datetime.now().strftime("%Y-%m-%d")

        md_path = runs_folder / f"{date_str}_outbound_run.md"
        json_path = runs_folder / f"{date_str}_outbound_run.json"

        assert md_path.exists(), f"Markdown dashboard not found at {md_path}"
        assert json_path.exists(), f"JSON dashboard not found at {json_path}"

    def test_dashboard_json_structure(self, sample_csv_file, config_factory):
        """Test that dashboard JSON has expected structure."""
        config = config_factory(sample_csv_file, dry_run=False)

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(config.output_root)}):
            orchestrator = OutboundOrchestrator(config)
            orchestrator._zoominfo_available = False
            orchestrator.run()

        runs_folder = config.output_root / "runs"
        date_str = datetime.now().strftime("%Y-%m-%d")
        json_path = runs_folder / f"{date_str}_outbound_run.json"

        with open(json_path) as f:
            data = json.load(f)

        # Verify structure
        assert "run_date" in data
        assert "settings" in data
        assert "summary" in data
        assert "accounts" in data
        assert "skipped_accounts" in data

        # Verify summary fields
        summary = data["summary"]
        assert "accounts_processed" in summary
        assert "accounts_skipped" in summary
        assert "prepared_for_rendering" in summary
        assert "rejected" in summary

    def test_dashboard_under_output_root(self, sample_csv_file, temp_dir, config_factory):
        """Test that dashboard is created under PROSPECTING_OUTPUT_ROOT."""
        custom_root = temp_dir / "custom_output"
        custom_root.mkdir()

        config = config_factory(sample_csv_file, output_root=custom_root, dry_run=False)

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(custom_root)}):
            orchestrator = OutboundOrchestrator(config)
            orchestrator._zoominfo_available = False
            orchestrator.run()

        # Dashboard should be under custom root
        runs_folder = custom_root / "runs"
        assert runs_folder.exists()
        assert any(runs_folder.iterdir())


# =============================================================================
# TEST: PERSONA MAPPING
# =============================================================================

class TestPersonaMapping:
    """Tests for deterministic persona mapping."""

    def test_default_persona_order(self):
        """Test default persona order when no tags."""
        account = AccountRecord(company_name="Test Corp", score=90)
        personas = get_personas_for_account(account)

        assert personas == ["quality", "ops", "it"]

    def test_quality_focused_tag(self):
        """Test persona order with quality_focused tag."""
        account = AccountRecord(
            company_name="Test Corp",
            score=90,
            signal_tags=["quality_focused"]
        )
        personas = get_personas_for_account(account)

        assert personas[0] == "quality"

    def test_operations_focused_tag(self):
        """Test persona order with operations_focused tag."""
        account = AccountRecord(
            company_name="Test Corp",
            score=90,
            signal_tags=["operations_focused"]
        )
        personas = get_personas_for_account(account)

        assert personas[0] == "ops"

    def test_it_focused_tag(self):
        """Test persona order with it_focused tag."""
        account = AccountRecord(
            company_name="Test Corp",
            score=90,
            signal_tags=["it_focused", "other_tag"]
        )
        personas = get_personas_for_account(account)

        assert personas[0] == "it"


# =============================================================================
# TEST: QUALITY GATES
# =============================================================================

class TestQualityGates:
    """Tests for draft quality gate verification."""

    def test_verify_quality_passes_valid_draft(self, temp_dir, config_factory):
        """Test that valid draft passes quality gates."""
        accounts_file = temp_dir / "accounts.csv"
        accounts_file.write_text("company_name,score\nTest,90\n")

        config = config_factory(accounts_file)

        # Create a valid draft file
        draft_path = temp_dir / "draft.json"
        draft_path.write_text("{}")

        # Result with status=ready_for_rendering passes quality gates
        result = {
            "status": "ready_for_rendering",
            "context_quality": {
                "confidence_mode": "HIGH",
                "cited_signal_count": 3
            }
        }

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(temp_dir)}):
            orchestrator = OutboundOrchestrator(config)
            passed, reasons = orchestrator.verify_draft_quality(str(draft_path), result)

        assert passed is True
        assert len(reasons) == 0

    def test_verify_quality_fails_missing_artifact(self, temp_dir, config_factory):
        """Test that missing artifact fails quality gates."""
        accounts_file = temp_dir / "accounts.csv"
        accounts_file.write_text("company_name,score\nTest,90\n")

        config = config_factory(accounts_file)

        result = {"status": "success"}

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(temp_dir)}):
            orchestrator = OutboundOrchestrator(config)
            passed, reasons = orchestrator.verify_draft_quality(None, result)

        assert passed is False
        assert any("does not exist" in r for r in reasons)

    def test_verify_quality_fails_no_confidence_mode(self, temp_dir, config_factory):
        """Test that missing confidence_mode fails quality gates."""
        accounts_file = temp_dir / "accounts.csv"
        accounts_file.write_text("company_name,score\nTest,90\n")

        config = config_factory(accounts_file)

        draft_path = temp_dir / "draft.json"
        draft_path.write_text("{}")

        # Test with context_quality present but missing confidence_mode
        result = {
            "status": "success",
            "context_quality": {"cited_signal_count": 0},  # Missing confidence_mode
            "variants": [{"passed_validation": True}]
        }

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(temp_dir)}):
            orchestrator = OutboundOrchestrator(config)
            passed, reasons = orchestrator.verify_draft_quality(str(draft_path), result)

        assert passed is False
        assert any("confidence_mode" in r for r in reasons)

    def test_verify_quality_fails_empty_context(self, temp_dir, config_factory):
        """Test that empty context quality dict fails quality gates."""
        accounts_file = temp_dir / "accounts.csv"
        accounts_file.write_text("company_name,score\nTest,90\n")

        config = config_factory(accounts_file)

        draft_path = temp_dir / "draft.json"
        draft_path.write_text("{}")

        # Empty context_quality dict is treated as missing
        result = {
            "status": "success",
            "context_quality": {},
            "variants": [{"passed_validation": True}]
        }

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(temp_dir)}):
            orchestrator = OutboundOrchestrator(config)
            passed, reasons = orchestrator.verify_draft_quality(str(draft_path), result)

        assert passed is False
        assert any("context quality" in r.lower() for r in reasons)

    def test_verify_quality_fails_wrong_status(self, temp_dir, config_factory):
        """Test that wrong status fails quality gates."""
        accounts_file = temp_dir / "accounts.csv"
        accounts_file.write_text("company_name,score\nTest,90\n")

        config = config_factory(accounts_file)

        draft_path = temp_dir / "draft.json"
        draft_path.write_text("{}")

        # Status is not "ready_for_rendering"
        result = {
            "status": "needs_more_research",
            "context_quality": {"confidence_mode": "HIGH"}
        }

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(temp_dir)}):
            orchestrator = OutboundOrchestrator(config)
            passed, reasons = orchestrator.verify_draft_quality(str(draft_path), result)

        assert passed is False
        assert any("ready_for_rendering" in r for r in reasons)


# =============================================================================
# TEST: DRY RUN MODE
# =============================================================================

class TestDryRunMode:
    """Tests for dry run mode."""

    def test_dry_run_no_pipeline_calls(self, sample_csv_file, config_factory):
        """Test that dry run doesn't call pipeline."""
        config = config_factory(sample_csv_file, dry_run=True)

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(config.output_root)}):
            orchestrator = OutboundOrchestrator(config)

            with patch.object(orchestrator, 'run_prospect_pipeline') as mock_pipeline:
                orchestrator._zoominfo_available = True
                result = orchestrator.run()

                # Pipeline should not be called in dry run
                mock_pipeline.assert_not_called()

    def test_dry_run_accounts_listed(self, sample_csv_file, config_factory):
        """Test that dry run lists accounts that would be processed."""
        config = config_factory(sample_csv_file, top_n=3, dry_run=True)

        with patch.dict(os.environ, {"PROSPECTING_OUTPUT_ROOT": str(config.output_root)}):
            orchestrator = OutboundOrchestrator(config)
            result = orchestrator.run()

        # Should have accounts with dry_run status
        assert len(result.accounts) == 3
        assert all(a.status == "dry_run" for a in result.accounts)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
