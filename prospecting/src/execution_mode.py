"""
Execution Mode Detection for Prospecting System

Determines whether the system is running in CLI mode (inside Claude Code)
or headless mode (background automation with API access).

In CLI mode:
- All Anthropic API calls are disabled
- LLM-based features fall back to deterministic alternatives
- System never fails due to missing API keys

In headless mode:
- Full API access is expected
- LLM-based features are enabled
- Missing API keys will cause failures

Usage:
    from execution_mode import get_execution_mode, is_cli_mode

    if is_cli_mode():
        # Use deterministic fallback
        pass
    else:
        # Use LLM-based approach
        pass
"""

import os
import logging
from typing import Literal

logger = logging.getLogger(__name__)

# Type alias for execution mode
ExecutionMode = Literal["cli", "headless"]

# Environment variable names
ENV_EXECUTION_MODE = "PROSPECTING_EXECUTION_MODE"

# Claude Code environment markers (checked in order)
CLAUDE_CODE_ENV_MARKERS = [
    "CLAUDE_CODE",           # Primary marker
    "CLAUDE_CODE_VERSION",   # Version marker
    "CLAUDE_CLI",            # Alternative marker
    "MCP_SERVER_NAME",       # MCP server context
]

# Cache for execution mode (computed once per process)
_cached_mode: ExecutionMode | None = None


def _detect_claude_code_environment() -> bool:
    """
    Detect if running inside Claude Code environment.

    Checks for known environment markers that indicate Claude Code context.

    Returns:
        True if Claude Code environment detected
    """
    for marker in CLAUDE_CODE_ENV_MARKERS:
        if os.getenv(marker):
            return True

    # Check for TTY as fallback heuristic (interactive terminal)
    # Claude Code typically runs in interactive context
    try:
        import sys
        if sys.stdin.isatty() and sys.stdout.isatty():
            # Interactive terminal - likely Claude Code
            return True
    except (AttributeError, OSError):
        pass

    return False


def get_execution_mode() -> ExecutionMode:
    """
    Get the current execution mode.

    Resolution order:
    1. Explicit PROSPECTING_EXECUTION_MODE environment variable
    2. Claude Code environment detection
    3. Default to 'headless'

    Returns:
        'cli' or 'headless'
    """
    global _cached_mode

    if _cached_mode is not None:
        return _cached_mode

    # 1. Check explicit environment variable
    explicit_mode = os.getenv(ENV_EXECUTION_MODE, "").lower().strip()
    if explicit_mode in ("cli", "headless"):
        _cached_mode = explicit_mode  # type: ignore
        logger.info(f"Execution mode from env var: {_cached_mode}")
        return _cached_mode

    # 2. Detect Claude Code environment
    if _detect_claude_code_environment():
        _cached_mode = "cli"
        logger.info("Execution mode: cli (Claude Code environment detected)")
        return _cached_mode

    # 3. Default to headless
    _cached_mode = "headless"
    logger.info("Execution mode: headless (default)")
    return _cached_mode


def is_cli_mode() -> bool:
    """
    Check if running in CLI mode.

    In CLI mode, all Anthropic API calls are disabled and the system
    falls back to deterministic alternatives.

    Returns:
        True if in CLI mode
    """
    return get_execution_mode() == "cli"


def is_headless_mode() -> bool:
    """
    Check if running in headless mode.

    In headless mode, full API access is available.

    Returns:
        True if in headless mode
    """
    return get_execution_mode() == "headless"


def reset_cached_mode() -> None:
    """
    Reset the cached execution mode.

    Useful for testing or when environment changes.
    """
    global _cached_mode
    _cached_mode = None


def set_execution_mode(mode: ExecutionMode) -> None:
    """
    Explicitly set the execution mode (for programmatic use).

    This bypasses environment detection. Use with caution.

    Args:
        mode: 'cli' or 'headless'
    """
    global _cached_mode
    if mode not in ("cli", "headless"):
        raise ValueError(f"Invalid execution mode: {mode}. Must be 'cli' or 'headless'")
    _cached_mode = mode
    logger.info(f"Execution mode set programmatically: {mode}")


# Context quality warning for CLI mode
WARNING_LLM_API_DISABLED_CLI_MODE = "LLM_API_DISABLED_CLI_MODE: LLM features disabled in CLI mode"
WARNING_RENDERED_DETERMINISTIC_NO_LLM = "RENDERED_DETERMINISTIC_NO_LLM: Email rendered without LLM"
