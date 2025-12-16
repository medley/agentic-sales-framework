#!/usr/bin/env python3
"""
Inbox View - Compact inbox-style view of prospecting artifacts

Displays a compact, scrollable list of all prospecting items.

Usage:
    python scripts/inbox_view.py
    python scripts/inbox_view.py --limit 20
    python scripts/inbox_view.py --show_warnings
    python scripts/inbox_view.py --group_by company
    python scripts/inbox_view.py --group_by persona
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.artifact_scanner import (
    ArtifactScanner,
    ProspectArtifact,
    ProspectStatus,
    group_by_company,
    group_by_persona
)


# =============================================================================
# DISPLAY FORMATTING
# =============================================================================

def get_status_indicator(artifact: ProspectArtifact) -> str:
    """Get status indicator character."""
    if artifact.status == ProspectStatus.APPROVED_FOR_SEND:
        return "A"
    elif artifact.review_required:
        return "!"
    elif artifact.approval_eligible:
        return "+"
    elif artifact.rendered_validated:
        return "R"
    elif artifact.status == ProspectStatus.PREPARED:
        return "."
    else:
        return "-"


def get_status_color_marker(artifact: ProspectArtifact) -> str:
    """Get status marker with visual indicator."""
    indicator = get_status_indicator(artifact)

    if artifact.status == ProspectStatus.APPROVED_FOR_SEND:
        return f"[{indicator}]"  # Approved
    elif artifact.review_required:
        return f"[{indicator}]"  # Attention needed
    elif artifact.approval_eligible:
        return f"[{indicator}]"  # Ready for approval
    elif artifact.rendered_validated:
        return f"[{indicator}]"  # In progress
    else:
        return f"[{indicator}]"  # Pending


def format_persona_short(persona: str) -> str:
    """Format persona as short 3-letter code."""
    mapping = {
        "quality": "QUA",
        "manufacturing": "MFG",
        "it": "IT ",
        "regulatory": "REG",
        "operations": "OPS",
        "supply_chain": "SCM",
        "executive": "EXC",
        "unknown": "UNK"
    }
    return mapping.get(persona.lower(), persona[:3].upper())


def format_confidence_short(confidence: str) -> str:
    """Format confidence mode as short code."""
    mapping = {
        "HIGH": "HI",
        "MEDIUM": "MD",
        "LOW": "LO",
        "GENERIC": "GN",
        "UNKNOWN": "--"
    }
    return mapping.get(confidence.upper(), confidence[:2].upper())


def format_state_short(artifact: ProspectArtifact) -> str:
    """Format state as short string."""
    if artifact.status == ProspectStatus.APPROVED_FOR_SEND:
        return "APPROVED"
    elif artifact.review_required:
        return "REVIEW  "
    elif artifact.approval_eligible:
        return "APPROVE!"
    elif artifact.rendered_validated:
        return "RENDERED"
    else:
        return "PREPARED"


def format_warnings_short(artifact: ProspectArtifact, max_chars: int = 20) -> str:
    """Format warnings as short string."""
    if not artifact.warnings:
        return "-"

    codes = []
    for w in artifact.warning_codes[:2]:
        # Shorten common warnings
        short = w.replace("_", "").replace("SIGNALS", "SIG").replace("PRESENT", "")
        if len(short) > 10:
            short = short[:8] + ".."
        codes.append(short)

    result = ",".join(codes)
    if len(artifact.warnings) > 2:
        result += f"+{len(artifact.warnings) - 2}"

    if len(result) > max_chars:
        result = result[:max_chars - 2] + ".."

    return result


def format_inbox_row(artifact: ProspectArtifact, show_warnings: bool = False) -> str:
    """
    Format a single inbox row.

    Format:
    [S] DATE       COMPANY          CONTACT          PER  CNF  STATE     WARN
    """
    marker = get_status_color_marker(artifact)
    date = artifact.run_date[:10]  # YYYY-MM-DD
    company = artifact.company_name[:16].ljust(16)
    contact = artifact.contact_name[:16].ljust(16)
    persona = format_persona_short(artifact.persona)
    conf = format_confidence_short(artifact.confidence_mode)
    state = format_state_short(artifact)

    row = f"{marker} {date}  {company}  {contact}  {persona}  {conf}   {state}"

    if show_warnings:
        warn = format_warnings_short(artifact)
        row += f"  {warn}"

    return row


def format_inbox_header(show_warnings: bool = False) -> str:
    """Format the inbox header row."""
    header = "[S] DATE        COMPANY           CONTACT           PER  CNF  STATE    "
    if show_warnings:
        header += " WARNINGS"
    separator = "-" * len(header)

    return f"{header}\n{separator}"


def format_inbox(
    artifacts: list,
    show_warnings: bool = False,
    limit: int = 0
) -> str:
    """
    Format the complete inbox view.

    Args:
        artifacts: List of ProspectArtifact
        show_warnings: Whether to show warnings column
        limit: Max items to show (0 = unlimited)

    Returns:
        Formatted inbox string
    """
    lines = []

    # Title
    lines.append("")
    lines.append("  PROSPECTING INBOX")
    lines.append("")

    # Legend
    lines.append("  Legend: [+] approvable  [R] rendered  [.] prepared  [!] review  [A] approved")
    lines.append("")

    # Header
    lines.append(format_inbox_header(show_warnings))

    # Rows
    display_artifacts = artifacts[:limit] if limit > 0 else artifacts

    for artifact in display_artifacts:
        lines.append(format_inbox_row(artifact, show_warnings))

    # Footer
    if limit > 0 and len(artifacts) > limit:
        lines.append(f"\n  ... and {len(artifacts) - limit} more items")

    lines.append("")

    # Stats
    approvable = sum(1 for a in artifacts if a.approval_eligible)
    rendered = sum(1 for a in artifacts if a.rendered_validated and not a.approval_eligible)
    prepared = sum(1 for a in artifacts if a.status == ProspectStatus.PREPARED)
    review = sum(1 for a in artifacts if a.review_required)

    lines.append(f"  Total: {len(artifacts)} | Approvable: {approvable} | Rendered: {rendered} | Prepared: {prepared} | Review: {review}")
    lines.append("")

    return "\n".join(lines)


def format_grouped_inbox(
    artifacts: list,
    group_by: str,
    show_warnings: bool = False
) -> str:
    """
    Format inbox grouped by company or persona.

    Args:
        artifacts: List of ProspectArtifact
        group_by: "company" or "persona"
        show_warnings: Whether to show warnings

    Returns:
        Formatted grouped inbox
    """
    lines = []

    # Title
    lines.append("")
    lines.append(f"  PROSPECTING INBOX (grouped by {group_by})")
    lines.append("")

    # Legend
    lines.append("  Legend: [+] approvable  [R] rendered  [.] prepared  [!] review  [A] approved")
    lines.append("")

    # Group
    if group_by == "company":
        groups = group_by_company(artifacts)
    else:
        groups = group_by_persona(artifacts)

    # Sort groups by size (largest first)
    sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)

    for group_name, group_artifacts in sorted_groups:
        lines.append(f"  === {group_name.upper()} ({len(group_artifacts)}) ===")
        lines.append(format_inbox_header(show_warnings))

        for artifact in group_artifacts:
            lines.append(format_inbox_row(artifact, show_warnings))

        lines.append("")

    # Stats
    approvable = sum(1 for a in artifacts if a.approval_eligible)
    total = len(artifacts)
    lines.append(f"  Total: {total} | Approvable: {approvable}")
    lines.append("")

    return "\n".join(lines)


# =============================================================================
# MAIN CLI
# =============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Compact inbox view of prospecting artifacts"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of items shown (0 = unlimited)"
    )
    parser.add_argument(
        "--show_warnings",
        action="store_true",
        help="Show warnings column"
    )
    parser.add_argument(
        "--group_by",
        choices=["company", "persona"],
        help="Group items by company or persona"
    )
    parser.add_argument(
        "--actionable_only",
        action="store_true",
        help="Only show actionable items (not promoted)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Scan artifacts
    scanner = ArtifactScanner()

    if args.actionable_only:
        artifacts = scanner.scan_actionable()
    else:
        artifacts = scanner.scan_all()

    # Output
    if args.json:
        import json
        output = {
            "count": len(artifacts),
            "artifacts": [a.to_dict() for a in artifacts]
        }
        print(json.dumps(output, indent=2))
    elif args.group_by:
        print(format_grouped_inbox(artifacts, args.group_by, args.show_warnings))
    else:
        print(format_inbox(artifacts, args.show_warnings, args.limit))


if __name__ == "__main__":
    main()
