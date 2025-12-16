#!/usr/bin/env python3
"""
Batch Render Script - Renders prepared drafts from orchestrator runs

This script processes drafts prepared by the outbound orchestrator and renders
them using the deterministic render_and_validate pipeline. It does NOT use
Anthropic API calls - all rendering is done locally via Claude CLI.

Respects all Phase 2 gates:
- review_required: Skip unless --force (human review override)
- confidence_mode: Skip LOW/GENERIC (cannot be overridden)
- warnings: Skip THIN_RESEARCH, VENDOR_DATA_ONLY (cannot be overridden)
- automation_allowed: Skip if False (regulatory block - CANNOT be overridden)

Usage:
    # Render today's run
    python3 scripts/render_run.py

    # Render specific date
    python3 scripts/render_run.py --run_date 2025-12-11

    # Dry run (show what would be rendered)
    python3 scripts/render_run.py --dry_run

    # Force rendering (override review_required after human review)
    python3 scripts/render_run.py --force

    # Only render promotable items
    python3 scripts/render_run.py --only_promotable

Output:
    - Renders each eligible email_context.json
    - Updates status to rendered_validated
    - Writes rendered email artifacts
    - Prints summary of rendered/skipped/failed
"""

import sys
import os
import json
import argparse
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from execution_mode import (
    get_execution_mode,
    is_cli_mode,
    set_execution_mode,
    WARNING_RENDERED_DETERMINISTIC_NO_LLM
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Gates - reasons to skip rendering
BLOCKED_CONFIDENCE_MODES = {"LOW", "GENERIC"}
BLOCKED_WARNINGS = {"THIN_RESEARCH", "VENDOR_DATA_ONLY"}


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Batch render prepared drafts from orchestrator run"
    )
    parser.add_argument(
        "--run_date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Run date (YYYY-MM-DD format, default: today)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum items to render (default: 20)"
    )
    parser.add_argument(
        "--only_promotable",
        action="store_true",
        help="Only render items marked as promotion_eligible"
    )
    parser.add_argument(
        "--include_prepared",
        action="store_true",
        default=True,
        help="Include items with status=prepared_for_rendering (default: True)"
    )
    parser.add_argument(
        "--execution_mode",
        choices=["cli", "headless"],
        default=None,
        help="Execution mode: cli (no API) or headless (with API). Default: auto-detect"
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Show what would be rendered without actually rendering"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Override review_required after human review (regulatory personas cannot be overridden)"
    )
    parser.add_argument(
        "--output_root",
        default=None,
        help="Output root directory (default: from env or standard location)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    return parser.parse_args()


def find_run_dashboard(run_date: str, output_root: Optional[str] = None) -> Optional[Path]:
    """
    Find the run dashboard JSON for a given date.

    Args:
        run_date: Date string (YYYY-MM-DD)
        output_root: Optional output root directory

    Returns:
        Path to run dashboard JSON or None if not found
    """
    # Determine output root
    if output_root:
        root = Path(output_root)
    else:
        root = Path(os.getenv(
            "PROSPECTING_OUTPUT_ROOT",
            Path.home() / "prospecting-output"
        ))

    # Look for run dashboard
    runs_dir = root / "runs"
    dashboard_path = runs_dir / f"{run_date}_outbound_run.json"

    if dashboard_path.exists():
        return dashboard_path

    # Try to find any dashboard for this date
    if runs_dir.exists():
        for f in runs_dir.glob(f"{run_date}*.json"):
            return f

    logger.warning(f"No run dashboard found for {run_date} in {runs_dir}")
    return None


def load_run_dashboard(path: Path) -> Dict[str, Any]:
    """Load run dashboard JSON."""
    with open(path, 'r') as f:
        return json.load(f)


def load_email_context(path: str) -> Optional[Dict[str, Any]]:
    """Load email context JSON."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load email context: {e}")
        return None


def check_render_gates(
    contact: Dict[str, Any],
    context: Dict[str, Any],
    force: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Check if contact passes all render gates.

    Args:
        contact: Contact dict from run dashboard
        context: Email context loaded from draft_path
        force: If True, bypasses review_required gate (cannot bypass regulatory)

    Returns:
        (eligible, skip_reason) - eligible=True if can render
    """
    # Gate 1: Confidence mode
    confidence_mode = contact.get("confidence_mode", "UNKNOWN").upper()
    if confidence_mode in BLOCKED_CONFIDENCE_MODES:
        return False, f"confidence_mode_{confidence_mode}"

    # Gate 2: Warnings
    warnings = contact.get("warnings", [])
    for warning in warnings:
        for blocked in BLOCKED_WARNINGS:
            if blocked in warning.upper():
                return False, f"warning_{blocked}"

    # Gate 3: Review required (can be overridden with --force after human review)
    prospect_brief = context.get("prospect_brief", {})
    if prospect_brief.get("review_required", False):
        if not force:
            return False, "review_required"
        logger.info("Overriding review_required with --force (human review completed)")

    # Gate 4: Automation allowed (regulatory block - CANNOT be overridden)
    if not prospect_brief.get("automation_allowed", True):
        return False, "automation_not_allowed_regulatory"

    return True, None


def render_single_item(
    context_path: str,
    dry_run: bool = False
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Render a single email context using render_and_validate.py.

    Args:
        context_path: Path to email_context.json
        dry_run: If True, don't actually render

    Returns:
        (success, error_message, render_result)
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would render: {context_path}")
        return True, None, {"dry_run": True}

    # Build command
    script_path = Path(__file__).parent / "render_and_validate.py"
    cmd = [
        sys.executable,
        str(script_path),
        "--context", context_path,
        "--output", "json"
    ]

    logger.info(f"Rendering: {context_path}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            try:
                output = json.loads(result.stdout)
                return True, None, output
            except json.JSONDecodeError:
                logger.warning("Could not parse render output as JSON")
                return True, None, {"raw_output": result.stdout}
        else:
            error = result.stderr or result.stdout or "Unknown error"
            logger.error(f"Render failed: {error[:200]}")
            return False, error[:500], None

    except subprocess.TimeoutExpired:
        return False, "Render timeout (120s)", None
    except Exception as e:
        return False, str(e), None


def save_render_status(
    context_path: str,
    success: bool,
    result: Optional[Dict[str, Any]],
    error: Optional[str]
) -> None:
    """
    Save render status file alongside email context.

    Args:
        context_path: Path to email_context.json
        success: Whether render succeeded
        result: Render result dict
        error: Error message if failed
    """
    context_dir = Path(context_path).parent
    status_path = context_dir / Path(context_path).stem.replace(
        "_email_context", "_render_status"
    )
    status_path = status_path.with_suffix(".json")

    status = {
        "rendered_at": datetime.now().isoformat(),
        "success": success,
        "execution_mode": get_execution_mode(),
        "warning": WARNING_RENDERED_DETERMINISTIC_NO_LLM if success else None,
        "error": error
    }

    if result and not result.get("dry_run"):
        status["best_variant"] = result.get("best_variant", {})
        status["variants_count"] = len(result.get("variants", []))

    with open(status_path, 'w') as f:
        json.dump(status, f, indent=2)

    logger.debug(f"Saved render status: {status_path}")


def update_dashboard_status(
    dashboard_path: Path,
    company_name: str,
    contact_name: str,
    success: bool,
    skip_reason: Optional[str] = None
) -> None:
    """
    Update run dashboard with render status.

    Args:
        dashboard_path: Path to run dashboard JSON
        company_name: Company name
        contact_name: Contact name
        success: Whether render succeeded
        skip_reason: Reason for skipping (if applicable)
    """
    try:
        with open(dashboard_path, 'r') as f:
            dashboard = json.load(f)

        # Find and update contact
        for account in dashboard.get("accounts", []):
            if account["company_name"] == company_name:
                for contact in account.get("contacts", []):
                    if contact["name"] == contact_name:
                        if success:
                            contact["status"] = "rendered_validated"
                            contact["rendered_validated"] = True
                            contact["render_skipped_reason"] = None
                        elif skip_reason:
                            contact["render_skipped_reason"] = skip_reason
                        break
                break

        # Update summary
        summary = dashboard.get("summary", {})
        if success:
            summary["rendered_validated"] = summary.get("rendered_validated", 0) + 1
        elif skip_reason:
            summary["render_skipped"] = summary.get("render_skipped", 0) + 1

        with open(dashboard_path, 'w') as f:
            json.dump(dashboard, f, indent=2)

    except Exception as e:
        logger.warning(f"Failed to update dashboard: {e}")


def main():
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Set execution mode if specified
    if args.execution_mode:
        set_execution_mode(args.execution_mode)

    logger.info(f"Execution mode: {get_execution_mode()}")
    logger.info(f"Render run for date: {args.run_date}")

    # Find run dashboard
    dashboard_path = find_run_dashboard(args.run_date, args.output_root)
    if not dashboard_path:
        logger.error(f"No run dashboard found for {args.run_date}")
        sys.exit(1)

    logger.info(f"Using dashboard: {dashboard_path}")

    # Load dashboard
    dashboard = load_run_dashboard(dashboard_path)

    # Collect eligible items
    eligible_items = []
    skipped_items = []

    for account in dashboard.get("accounts", []):
        company_name = account["company_name"]

        for contact in account.get("contacts", []):
            contact_name = contact["name"]
            status = contact.get("status", "")
            draft_path = contact.get("draft_path")

            # Skip if already rendered
            if contact.get("rendered_validated"):
                skipped_items.append({
                    "company": company_name,
                    "contact": contact_name,
                    "reason": "already_rendered"
                })
                continue

            # Skip if not prepared for rendering
            if status != "prepared_for_rendering" and args.include_prepared:
                skipped_items.append({
                    "company": company_name,
                    "contact": contact_name,
                    "reason": f"status_{status}"
                })
                continue

            # Skip if only_promotable and not eligible
            if args.only_promotable and not contact.get("promotion_eligible"):
                skipped_items.append({
                    "company": company_name,
                    "contact": contact_name,
                    "reason": "not_promotion_eligible"
                })
                continue

            # Check draft path exists
            if not draft_path or not Path(draft_path).exists():
                skipped_items.append({
                    "company": company_name,
                    "contact": contact_name,
                    "reason": "missing_draft_path"
                })
                continue

            # Load context and check gates
            context = load_email_context(draft_path)
            if not context:
                skipped_items.append({
                    "company": company_name,
                    "contact": contact_name,
                    "reason": "failed_to_load_context"
                })
                continue

            eligible, skip_reason = check_render_gates(contact, context, args.force)
            if not eligible:
                skipped_items.append({
                    "company": company_name,
                    "contact": contact_name,
                    "reason": skip_reason
                })
                continue

            eligible_items.append({
                "company": company_name,
                "contact": contact_name,
                "draft_path": draft_path,
                "context": context
            })

    # Apply limit
    if len(eligible_items) > args.limit:
        logger.info(f"Limiting to {args.limit} items (found {len(eligible_items)})")
        eligible_items = eligible_items[:args.limit]

    logger.info(f"Found {len(eligible_items)} eligible items, {len(skipped_items)} skipped")

    if args.dry_run:
        print("\n=== DRY RUN ===")
        print(f"Would render {len(eligible_items)} items:\n")
        for item in eligible_items:
            print(f"  - {item['company']}: {item['contact']}")
        print(f"\nSkipped {len(skipped_items)} items")
        for skip in skipped_items[:10]:
            print(f"  - {skip['company']}: {skip['contact']} ({skip['reason']})")
        if len(skipped_items) > 10:
            print(f"  ... and {len(skipped_items) - 10} more")
        return

    # Render eligible items
    rendered = 0
    failed = 0

    for item in eligible_items:
        success, error, result = render_single_item(
            item["draft_path"],
            dry_run=args.dry_run
        )

        if success:
            rendered += 1
            save_render_status(item["draft_path"], True, result, None)
            update_dashboard_status(
                dashboard_path,
                item["company"],
                item["contact"],
                True
            )
            logger.info(f"Rendered: {item['company']} - {item['contact']}")
        else:
            failed += 1
            save_render_status(item["draft_path"], False, None, error)
            logger.error(f"Failed: {item['company']} - {item['contact']}: {error[:100]}")

    # Print summary
    print("\n" + "=" * 50)
    print("RENDER RUN SUMMARY")
    print("=" * 50)
    print(f"Date: {args.run_date}")
    print(f"Execution mode: {get_execution_mode()}")
    print(f"Rendered: {rendered}")
    print(f"Failed: {failed}")
    print(f"Skipped: {len(skipped_items)}")
    print("")

    if skipped_items:
        print("Skipped reasons:")
        reasons = {}
        for skip in skipped_items:
            reason = skip["reason"]
            reasons[reason] = reasons.get(reason, 0) + 1
        for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"  {reason}: {count}")

    print("=" * 50)


if __name__ == "__main__":
    main()
