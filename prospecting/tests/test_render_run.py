"""
Tests for render_run.py batch renderer.

Tests gate enforcement and rendering logic.
"""

import os
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import after path setup
from execution_mode import reset_cached_mode, set_execution_mode


class TestRenderGates:
    """Test render gate enforcement."""

    def setup_method(self):
        """Set up test fixtures."""
        reset_cached_mode()
        set_execution_mode("cli")

        # Import here to pick up mocked execution mode
        from render_run import check_render_gates

        self.check_gates = check_render_gates

    def teardown_method(self):
        """Clean up."""
        reset_cached_mode()

    def test_blocks_low_confidence(self):
        """Test that LOW confidence mode is blocked."""
        contact = {"confidence_mode": "LOW", "warnings": []}
        context = {"prospect_brief": {}}

        eligible, reason = self.check_gates(contact, context, force=False)

        assert eligible is False
        assert "confidence_mode_LOW" in reason

    def test_blocks_generic_confidence(self):
        """Test that GENERIC confidence mode is blocked."""
        contact = {"confidence_mode": "GENERIC", "warnings": []}
        context = {"prospect_brief": {}}

        eligible, reason = self.check_gates(contact, context, force=False)

        assert eligible is False
        assert "confidence_mode_GENERIC" in reason

    def test_allows_high_confidence(self):
        """Test that HIGH confidence mode is allowed."""
        contact = {"confidence_mode": "HIGH", "warnings": []}
        context = {"prospect_brief": {"automation_allowed": True}}

        eligible, reason = self.check_gates(contact, context, force=False)

        assert eligible is True
        assert reason is None

    def test_allows_medium_confidence(self):
        """Test that MEDIUM confidence mode is allowed."""
        contact = {"confidence_mode": "MEDIUM", "warnings": []}
        context = {"prospect_brief": {"automation_allowed": True}}

        eligible, reason = self.check_gates(contact, context, force=False)

        assert eligible is True
        assert reason is None

    def test_blocks_thin_research_warning(self):
        """Test that THIN_RESEARCH warning is blocked."""
        contact = {"confidence_mode": "HIGH", "warnings": ["THIN_RESEARCH: Only 1 signal"]}
        context = {"prospect_brief": {}}

        eligible, reason = self.check_gates(contact, context, force=False)

        assert eligible is False
        assert "THIN_RESEARCH" in reason

    def test_blocks_vendor_data_only_warning(self):
        """Test that VENDOR_DATA_ONLY warning is blocked."""
        contact = {"confidence_mode": "HIGH", "warnings": ["VENDOR_DATA_ONLY"]}
        context = {"prospect_brief": {}}

        eligible, reason = self.check_gates(contact, context, force=False)

        assert eligible is False
        assert "VENDOR_DATA_ONLY" in reason

    def test_blocks_review_required(self):
        """Test that review_required is blocked without force."""
        contact = {"confidence_mode": "HIGH", "warnings": []}
        context = {"prospect_brief": {"review_required": True, "automation_allowed": True}}

        eligible, reason = self.check_gates(contact, context, force=False)

        assert eligible is False
        assert reason == "review_required"

    def test_force_bypasses_review_required(self):
        """Test that --force bypasses review_required."""
        contact = {"confidence_mode": "HIGH", "warnings": []}
        context = {"prospect_brief": {"review_required": True, "automation_allowed": True}}

        eligible, reason = self.check_gates(contact, context, force=True)

        assert eligible is True
        assert reason is None

    def test_blocks_automation_not_allowed(self):
        """Test that automation_allowed=False is blocked."""
        contact = {"confidence_mode": "HIGH", "warnings": []}
        context = {"prospect_brief": {"automation_allowed": False}}

        eligible, reason = self.check_gates(contact, context, force=False)

        assert eligible is False
        assert reason == "automation_not_allowed_regulatory"

    def test_force_does_not_bypass_regulatory(self):
        """Test that --force does NOT bypass regulatory block (Phase 2 policy)."""
        contact = {"confidence_mode": "HIGH", "warnings": []}
        context = {"prospect_brief": {"automation_allowed": False}}

        eligible, reason = self.check_gates(contact, context, force=True)

        assert eligible is False
        assert reason == "automation_not_allowed_regulatory"


class TestRenderRunDashboard:
    """Test dashboard loading and processing."""

    def setup_method(self):
        """Set up test fixtures."""
        reset_cached_mode()
        set_execution_mode("cli")

        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up."""
        reset_cached_mode()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_finds_run_dashboard(self):
        """Test that dashboard is found by date."""
        from render_run import find_run_dashboard

        # Create runs directory and dashboard
        runs_dir = Path(self.temp_dir) / "runs"
        runs_dir.mkdir(parents=True)

        dashboard_path = runs_dir / "2025-12-11_outbound_run.json"
        with open(dashboard_path, 'w') as f:
            json.dump({"run_date": "2025-12-11"}, f)

        found = find_run_dashboard("2025-12-11", self.temp_dir)

        assert found is not None
        assert found.name == "2025-12-11_outbound_run.json"

    def test_returns_none_for_missing_dashboard(self):
        """Test that None is returned for missing dashboard."""
        from render_run import find_run_dashboard

        found = find_run_dashboard("2099-01-01", self.temp_dir)

        assert found is None

    def test_loads_run_dashboard(self):
        """Test that dashboard JSON is loaded correctly."""
        from render_run import load_run_dashboard

        # Create dashboard
        dashboard_path = Path(self.temp_dir) / "test_dashboard.json"
        with open(dashboard_path, 'w') as f:
            json.dump({
                "run_date": "2025-12-11",
                "accounts": [{"company_name": "Test Corp"}]
            }, f)

        dashboard = load_run_dashboard(dashboard_path)

        assert dashboard["run_date"] == "2025-12-11"
        assert len(dashboard["accounts"]) == 1


class TestRenderOutput:
    """Test render output and status files."""

    def setup_method(self):
        """Set up test fixtures."""
        reset_cached_mode()
        set_execution_mode("cli")

        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up."""
        reset_cached_mode()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_saves_render_status(self):
        """Test that render status file is saved."""
        from render_run import save_render_status

        context_path = str(Path(self.temp_dir) / "test_email_context.json")
        result = {"best_variant": {"subject": "Test"}, "variants": [{}]}

        save_render_status(context_path, True, result, None)

        status_path = Path(self.temp_dir) / "test_render_status.json"
        assert status_path.exists()

        with open(status_path) as f:
            status = json.load(f)

        assert status["success"] is True
        assert status["execution_mode"] == "cli"
        assert "DETERMINISTIC" in status.get("warning", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
