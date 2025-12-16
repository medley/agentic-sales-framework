#!/usr/bin/env python3
"""
Review Queue - Daily prospecting review queue

Answers: "What should I look at today?"

Usage:
    python scripts/review_queue.py
    python scripts/review_queue.py --date 2025-01-15
    python scripts/review_queue.py --confidence HIGH
    python scripts/review_queue.py --persona quality
    python scripts/review_queue.py --only_promotable
    python scripts/review_queue.py --only_renderable
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, date

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.artifact_scanner import (
    ArtifactScanner,
    ProspectArtifact,
    ProspectStatus,
    group_by_company,
    group_by_primary_account
)


# =============================================================================
# DISPLAY FORMATTING
# =============================================================================

def format_artifact_line(artifact: ProspectArtifact, indent: int = 3) -> str:
    """Format a single artifact as a line item."""
    prefix = " " * indent
    status_icon = get_status_icon(artifact)

    line = f"{prefix}{status_icon} {artifact.contact_name}"
    line += f" – {artifact.persona.upper()}"
    line += f" – {artifact.display_status}"
    line += f" – {artifact.confidence_mode}"

    return line


def format_warnings_line(artifact: ProspectArtifact, indent: int = 5) -> str:
    """Format warnings line."""
    prefix = " " * indent
    if artifact.warnings:
        codes = artifact.warning_codes
        return f"{prefix}Warnings: {', '.join(codes)}"
    return f"{prefix}Warnings: none"


def format_action_line(artifact: ProspectArtifact, indent: int = 5) -> str:
    """Format recommended action line."""
    prefix = " " * indent

    if artifact.review_required:
        return f"{prefix}→ Manual decision only"
    elif artifact.approval_eligible:
        return f"{prefix}→ Ready to approve"
    elif artifact.rendered_validated:
        return f"{prefix}→ Review before approve"
    elif artifact.status == ProspectStatus.PREPARED:
        if artifact.warning_codes:
            return f"{prefix}→ Review before render"
        else:
            return f"{prefix}→ Ready to render"
    else:
        return f"{prefix}→ Review needed"


def get_status_icon(artifact: ProspectArtifact) -> str:
    """Get status icon for artifact."""
    if artifact.review_required:
        return "⚠"
    elif artifact.approval_eligible:
        return "✓"
    elif artifact.rendered_validated:
        return "◐"
    elif artifact.status == ProspectStatus.PREPARED:
        return "○"
    else:
        return "·"


def format_queue_header(target_date: date, total: int) -> str:
    """Format the queue header."""
    date_str = target_date.strftime("%Y-%m-%d")
    weekday = target_date.strftime("%A")

    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append(f"  Daily Review Queue – {date_str} ({weekday})")
    lines.append("=" * 60)
    lines.append("")

    if total == 0:
        lines.append("  No items to review.")
    else:
        lines.append(f"  {total} item(s) to review")
        lines.append("")
        lines.append("  Legend: ✓ approvable  ◐ rendered  ○ prepared  ⚠ review")

    lines.append("")

    return "\n".join(lines)


def format_company_group(
    company_name: str,
    artifacts: list,
    index: int
) -> str:
    """Format a company group."""
    lines = []

    # Check if this is a primary account with multiple sites
    primary_ids = set(a.primary_account_id for a in artifacts if a.primary_account_id)
    suffix = " (Primary Account)" if len(primary_ids) == 1 else ""

    lines.append(f"{index}) {company_name}{suffix}")

    for artifact in artifacts:
        lines.append(format_artifact_line(artifact))
        lines.append(format_warnings_line(artifact))
        lines.append(format_action_line(artifact))
        lines.append("")

    return "\n".join(lines)


def format_queue(
    artifacts: list,
    target_date: date
) -> str:
    """Format the complete review queue."""
    lines = []

    # Header
    lines.append(format_queue_header(target_date, len(artifacts)))

    if not artifacts:
        return "\n".join(lines)

    # Group by company/primary account
    groups = group_by_primary_account(artifacts)

    # Sort groups: promotable first, then by company name
    def group_priority(items):
        promotable_count = sum(1 for a in items if a.promotion_eligible)
        return (-promotable_count, items[0].company_name)

    sorted_groups = sorted(groups.items(), key=lambda x: group_priority(x[1]))

    for i, (key, group_artifacts) in enumerate(sorted_groups, 1):
        # Use company name from first artifact
        company = group_artifacts[0].company_name
        lines.append(format_company_group(company, group_artifacts, i))

    # Footer
    lines.append("-" * 60)
    lines.append("")

    # Summary
    approvable = sum(1 for a in artifacts if a.approval_eligible)
    renderable = sum(
        1 for a in artifacts
        if a.status == ProspectStatus.PREPARED and not a.review_required
    )
    review_req = sum(1 for a in artifacts if a.review_required)

    lines.append("Summary:")
    lines.append(f"  Ready to approve: {approvable}")
    lines.append(f"  Ready to render:  {renderable}")
    lines.append(f"  Needs review:     {review_req}")
    lines.append("")

    return "\n".join(lines)


# =============================================================================
# MAIN CLI
# =============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Daily prospecting review queue"
    )
    parser.add_argument(
        "--date",
        help="Target date (YYYY-MM-DD, default: today)"
    )
    parser.add_argument(
        "--confidence",
        choices=["HIGH", "MEDIUM", "LOW", "GENERIC"],
        help="Filter by confidence mode"
    )
    parser.add_argument(
        "--persona",
        help="Filter by persona (quality, manufacturing, it, regulatory)"
    )
    parser.add_argument(
        "--only_approvable",
        action="store_true",
        help="Only show items ready for approval"
    )
    parser.add_argument(
        "--only_renderable",
        action="store_true",
        help="Only show items ready to render"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show all dates, not just target date"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Parse target date
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD.")
            sys.exit(1)
    else:
        target_date = date.today()

    # Scan artifacts
    scanner = ArtifactScanner()

    if args.all:
        artifacts = scanner.scan_actionable()
    else:
        artifacts = scanner.scan_by_date(target_date)
        # Also include older actionable items
        all_actionable = scanner.scan_actionable()
        # Add older items that haven't been addressed
        older = [a for a in all_actionable if a.run_date < target_date.strftime("%Y-%m-%d")]
        artifacts = artifacts + older

    # Filter
    artifacts = scanner.filter_artifacts(
        artifacts,
        confidence=args.confidence,
        persona=args.persona,
        only_approvable=args.only_approvable,
        only_renderable=args.only_renderable
    )

    # Output
    if args.json:
        import json
        output = {
            "date": target_date.strftime("%Y-%m-%d"),
            "count": len(artifacts),
            "artifacts": [a.to_dict() for a in artifacts]
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_queue(artifacts, target_date))


if __name__ == "__main__":
    main()
