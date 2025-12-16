#!/usr/bin/env python3
"""
Prospecting Stats - Lightweight analytics for visibility

Read-only aggregation of prospecting metrics. No ML, no scoring - just counts.

Usage:
    python scripts/prospecting_stats.py
    python scripts/prospecting_stats.py --days 7
    python scripts/prospecting_stats.py --json
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, date, timedelta
from collections import Counter
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.artifact_scanner import (
    ArtifactScanner,
    ProspectArtifact,
    ProspectStatus,
    group_by_date,
    group_by_persona
)


# =============================================================================
# STATISTICS CALCULATION
# =============================================================================

def calculate_stats(
    artifacts: List[ProspectArtifact],
    days: int = 7
) -> Dict[str, Any]:
    """
    Calculate statistics from artifacts.

    Args:
        artifacts: List of ProspectArtifact
        days: Number of days to analyze

    Returns:
        Stats dictionary
    """
    # Filter to date range
    cutoff = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")
    filtered = [a for a in artifacts if a.run_date >= cutoff]

    # Basic counts
    total = len(filtered)
    rendered = sum(1 for a in filtered if a.rendered_validated)
    approved = sum(1 for a in filtered if a.status == ProspectStatus.APPROVED_FOR_SEND)
    prepared_only = sum(
        1 for a in filtered
        if a.status == ProspectStatus.PREPARED and not a.rendered_validated
    )
    review_required = sum(1 for a in filtered if a.review_required)

    # Warning distribution
    all_warnings = []
    for a in filtered:
        all_warnings.extend(a.warning_codes)
    warning_counts = Counter(all_warnings)

    # Persona distribution
    persona_counts = Counter(a.persona for a in filtered)

    # Confidence distribution
    confidence_counts = Counter(a.confidence_mode for a in filtered)

    # Per-day breakdown
    by_date = group_by_date(filtered)
    daily_counts = {d: len(items) for d, items in by_date.items()}

    # Stalled percentage (prepared but not rendered after 1 day)
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    stalled = [
        a for a in filtered
        if a.run_date <= yesterday and a.status == ProspectStatus.PREPARED
    ]
    stalled_pct = (len(stalled) / total * 100) if total > 0 else 0

    # Best persona by confidence
    persona_confidence = {}
    by_persona = group_by_persona(filtered)
    for persona, items in by_persona.items():
        high_count = sum(1 for a in items if a.confidence_mode == "HIGH")
        total_count = len(items)
        if total_count > 0:
            persona_confidence[persona] = {
                "high_pct": high_count / total_count * 100,
                "high_count": high_count,
                "total": total_count
            }

    # Find highest confidence persona
    best_persona = None
    best_high_pct = 0
    for persona, data in persona_confidence.items():
        if data["high_pct"] > best_high_pct and data["total"] >= 3:
            best_high_pct = data["high_pct"]
            best_persona = persona

    return {
        "period_days": days,
        "total_prepared": total,
        "rendered": rendered,
        "approved": approved,
        "prepared_only": prepared_only,
        "review_required": review_required,
        "stalled_count": len(stalled),
        "stalled_pct": round(stalled_pct, 1),
        "warning_counts": dict(warning_counts.most_common(5)),
        "persona_counts": dict(persona_counts),
        "confidence_counts": dict(confidence_counts),
        "daily_counts": daily_counts,
        "persona_confidence": persona_confidence,
        "best_persona": best_persona,
        "best_persona_high_pct": round(best_high_pct, 1) if best_persona else None
    }


# =============================================================================
# DISPLAY FORMATTING
# =============================================================================

def format_stats_report(stats: Dict[str, Any]) -> str:
    """
    Format stats as human-readable report.

    Args:
        stats: Stats dictionary

    Returns:
        Formatted report string
    """
    lines = []

    days = stats["period_days"]
    lines.append("")
    lines.append("=" * 50)
    lines.append(f"  PROSPECTING STATS (Last {days} days)")
    lines.append("=" * 50)
    lines.append("")

    # Summary
    lines.append("SUMMARY")
    lines.append("-" * 30)
    lines.append(f"  Drafts prepared:     {stats['total_prepared']}")
    lines.append(f"  Rendered:            {stats['rendered']}")
    lines.append(f"  Approved:            {stats['approved']}")
    lines.append(f"  Awaiting render:     {stats['prepared_only']}")
    lines.append(f"  Needs review:        {stats['review_required']}")
    lines.append("")

    # Stalled
    lines.append("STALLED ITEMS")
    lines.append("-" * 30)
    lines.append(f"  Count:     {stats['stalled_count']}")
    lines.append(f"  Percent:   {stats['stalled_pct']}%")
    lines.append("")

    # Warnings
    if stats["warning_counts"]:
        lines.append("TOP WARNINGS")
        lines.append("-" * 30)
        for warning, count in stats["warning_counts"].items():
            lines.append(f"  {warning}: {count}")
        lines.append("")

    # Confidence distribution
    lines.append("CONFIDENCE DISTRIBUTION")
    lines.append("-" * 30)
    total = stats["total_prepared"]
    for conf, count in sorted(stats["confidence_counts"].items()):
        pct = (count / total * 100) if total > 0 else 0
        bar = "#" * int(pct / 5)
        lines.append(f"  {conf:8} {count:3}  {bar} ({pct:.0f}%)")
    lines.append("")

    # Persona distribution
    lines.append("PERSONA DISTRIBUTION")
    lines.append("-" * 30)
    for persona, count in sorted(
        stats["persona_counts"].items(),
        key=lambda x: x[1],
        reverse=True
    ):
        pct = (count / total * 100) if total > 0 else 0
        lines.append(f"  {persona:15} {count:3}  ({pct:.0f}%)")
    lines.append("")

    # Best performer
    if stats["best_persona"]:
        lines.append("BEST PERFORMER")
        lines.append("-" * 30)
        lines.append(f"  Persona: {stats['best_persona']}")
        lines.append(f"  HIGH confidence rate: {stats['best_persona_high_pct']}%")
        lines.append("")

    # Daily breakdown (last 7 days)
    lines.append("DAILY BREAKDOWN")
    lines.append("-" * 30)
    daily = stats["daily_counts"]
    dates_sorted = sorted(daily.keys(), reverse=True)[:7]
    for d in dates_sorted:
        count = daily[d]
        bar = "#" * count
        lines.append(f"  {d}: {count:3}  {bar}")
    lines.append("")

    lines.append("=" * 50)

    return "\n".join(lines)


def format_mini_stats(stats: Dict[str, Any]) -> str:
    """
    Format compact one-line stats summary.

    Args:
        stats: Stats dictionary

    Returns:
        One-line summary
    """
    return (
        f"Prepared: {stats['total_prepared']} | "
        f"Rendered: {stats['rendered']} | "
        f"Approved: {stats['approved']} | "
        f"Stalled: {stats['stalled_pct']}%"
    )


# =============================================================================
# MAIN CLI
# =============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lightweight prospecting analytics"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to analyze (default: 7)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--mini",
        action="store_true",
        help="Output compact one-line summary"
    )

    args = parser.parse_args()

    # Scan artifacts
    scanner = ArtifactScanner()
    artifacts = scanner.scan_all()

    # Calculate stats
    stats = calculate_stats(artifacts, days=args.days)

    # Output
    if args.json:
        import json
        print(json.dumps(stats, indent=2))
    elif args.mini:
        print(format_mini_stats(stats))
    else:
        print(format_stats_report(stats))


if __name__ == "__main__":
    main()
