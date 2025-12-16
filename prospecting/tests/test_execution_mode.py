"""
Tests for execution_mode module.

Tests CLI mode detection and enforcement of API-free operation.
"""

import os
import pytest
from unittest.mock import patch

# Add src to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from execution_mode import (
    get_execution_mode,
    is_cli_mode,
    is_headless_mode,
    reset_cached_mode,
    set_execution_mode,
    WARNING_LLM_API_DISABLED_CLI_MODE,
    WARNING_RENDERED_DETERMINISTIC_NO_LLM,
)


class TestExecutionModeDetection:
    """Test execution mode detection logic."""

    def setup_method(self):
        """Reset cached mode before each test."""
        reset_cached_mode()

    def teardown_method(self):
        """Clean up environment after each test."""
        reset_cached_mode()
        # Remove any test env vars
        for var in ["PROSPECTING_EXECUTION_MODE", "CLAUDE_CODE"]:
            if var in os.environ:
                del os.environ[var]

    def test_explicit_cli_mode_from_env(self):
        """Test that explicit env var sets CLI mode."""
        os.environ["PROSPECTING_EXECUTION_MODE"] = "cli"
        assert get_execution_mode() == "cli"
        assert is_cli_mode() is True
        assert is_headless_mode() is False

    def test_explicit_headless_mode_from_env(self):
        """Test that explicit env var sets headless mode."""
        os.environ["PROSPECTING_EXECUTION_MODE"] = "headless"
        assert get_execution_mode() == "headless"
        assert is_cli_mode() is False
        assert is_headless_mode() is True

    def test_claude_code_env_detection(self):
        """Test that CLAUDE_CODE env var triggers CLI mode."""
        os.environ["CLAUDE_CODE"] = "1"
        assert get_execution_mode() == "cli"
        assert is_cli_mode() is True

    def test_set_execution_mode_programmatic(self):
        """Test programmatic setting of execution mode."""
        set_execution_mode("cli")
        assert get_execution_mode() == "cli"

        set_execution_mode("headless")
        assert get_execution_mode() == "headless"

    def test_set_execution_mode_invalid(self):
        """Test that invalid mode raises error."""
        with pytest.raises(ValueError):
            set_execution_mode("invalid")

    def test_mode_is_cached(self):
        """Test that mode is cached after first detection."""
        os.environ["PROSPECTING_EXECUTION_MODE"] = "cli"
        first_call = get_execution_mode()

        # Change env var
        os.environ["PROSPECTING_EXECUTION_MODE"] = "headless"

        # Should still return cached value
        assert get_execution_mode() == first_call

    def test_reset_cached_mode(self):
        """Test that reset_cached_mode clears cache."""
        os.environ["PROSPECTING_EXECUTION_MODE"] = "cli"
        get_execution_mode()

        reset_cached_mode()

        os.environ["PROSPECTING_EXECUTION_MODE"] = "headless"
        assert get_execution_mode() == "headless"

    def test_warning_constants_exist(self):
        """Test that warning constants are defined."""
        assert "CLI_MODE" in WARNING_LLM_API_DISABLED_CLI_MODE
        assert "DETERMINISTIC" in WARNING_RENDERED_DETERMINISTIC_NO_LLM


class TestCLIModeAPIBlocking:
    """Test that CLI mode blocks API calls."""

    def setup_method(self):
        """Set CLI mode for each test."""
        reset_cached_mode()
        set_execution_mode("cli")

    def teardown_method(self):
        """Reset after each test."""
        reset_cached_mode()

    def test_llm_angle_scorer_cli_mode_fallback(self):
        """Test that angle scorer falls back in CLI mode."""
        # Must set mode before importing the function
        reset_cached_mode()
        set_execution_mode("cli")

        # Import fresh
        import importlib
        import llm_angle_scorer
        importlib.reload(llm_angle_scorer)

        result = llm_angle_scorer.score_angles(
            persona="quality",
            company_name="Test Corp",
            verified_signals=[{"claim": "test", "source_url": "http://test.com"}],
            candidate_angles=[
                {"angle_id": "angle1", "name": "Angle 1", "description": "Test"}
            ],
            scoring_weights={"relevance": 0.45, "urgency": 0.35, "reply_likelihood": 0.20}
        )

        # Should return cli_fallback status, not error
        assert result["status"] == "cli_fallback"
        assert result["cli_mode"] is True
        assert len(result["scores"]) > 0

    def test_llm_angle_scorer_missing_api_key_ok_in_cli_mode(self):
        """Test that missing API key doesn't fail in CLI mode."""
        # Must set mode before importing the function
        reset_cached_mode()
        set_execution_mode("cli")

        # Remove API key
        original_key = os.environ.pop("ANTHROPIC_API_KEY", None)

        try:
            import importlib
            import llm_angle_scorer
            importlib.reload(llm_angle_scorer)

            result = llm_angle_scorer.score_angles(
                persona="quality",
                company_name="Test Corp",
                verified_signals=[],
                candidate_angles=[
                    {"angle_id": "angle1", "name": "Angle 1", "description": "Test"}
                ],
                scoring_weights={"relevance": 0.45, "urgency": 0.35, "reply_likelihood": 0.20}
            )

            # Should not raise, should use fallback
            assert result["status"] == "cli_fallback"

        finally:
            if original_key:
                os.environ["ANTHROPIC_API_KEY"] = original_key

    def test_llm_renderer_raises_in_cli_mode(self):
        """Test that LLMRenderer raises specific error in CLI mode."""
        # Must set mode before importing
        reset_cached_mode()
        set_execution_mode("cli")

        import importlib
        import llm_renderer
        importlib.reload(llm_renderer)

        with pytest.raises(llm_renderer.LLMRendererCLIModeError):
            llm_renderer.LLMRenderer()


class TestHeadlessModeAPIRequirement:
    """Test that headless mode requires API access."""

    def setup_method(self):
        """Set headless mode for each test."""
        reset_cached_mode()
        set_execution_mode("headless")

    def teardown_method(self):
        """Reset after each test."""
        reset_cached_mode()

    def test_llm_angle_scorer_fails_without_api_key_headless(self):
        """Test that angle scorer fails in headless mode without API key."""
        # Must set mode before importing
        reset_cached_mode()
        set_execution_mode("headless")

        # Remove API key
        original_key = os.environ.pop("ANTHROPIC_API_KEY", None)

        try:
            import importlib
            import llm_angle_scorer
            importlib.reload(llm_angle_scorer)

            result = llm_angle_scorer.score_angles(
                persona="quality",
                company_name="Test Corp",
                verified_signals=[],
                candidate_angles=[
                    {"angle_id": "angle1", "name": "Angle 1", "description": "Test"}
                ],
                scoring_weights={"relevance": 0.45, "urgency": 0.35, "reply_likelihood": 0.20}
            )

            # Should fail with error status
            assert result["status"] == "error"
            assert "ANTHROPIC_API_KEY" in result.get("error", "")

        finally:
            if original_key:
                os.environ["ANTHROPIC_API_KEY"] = original_key

    def test_llm_renderer_fails_without_api_key_headless(self):
        """Test that LLMRenderer fails in headless mode without API key."""
        # Must set mode before importing
        reset_cached_mode()
        set_execution_mode("headless")

        # Remove API key
        original_key = os.environ.pop("ANTHROPIC_API_KEY", None)

        try:
            import importlib
            import llm_renderer
            importlib.reload(llm_renderer)

            with pytest.raises(ValueError) as exc_info:
                llm_renderer.LLMRenderer()

            assert "ANTHROPIC_API_KEY" in str(exc_info.value)

        finally:
            if original_key:
                os.environ["ANTHROPIC_API_KEY"] = original_key


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
