#!/usr/bin/env python3
"""
Promote Prospecting Artifacts - Move validated artifacts to Accounts folder

This script handles the intentional promotion of prospecting artifacts
from 02_Prospecting/agent-prospecting → 01_Accounts/_Active.

Promotion is gated and requires eligibility checks to pass.

Usage:
    python3 scripts/promote_prospecting_artifacts.py --company "Acme Corp" --contact "John Smith"
    python3 scripts/promote_prospecting_artifacts.py --company "Acme Corp" --contact "John Smith" --dry_run
    python3 scripts/promote_prospecting_artifacts.py --company "Acme Corp" --contact "John Smith" --force

CLI Flags:
    --company       Company name (required)
    --contact       Contact name (required)
    --run_id        Optional specific run ID to promote
    --dry_run       Show what would be promoted without copying
    --force         Override review_required after human review (regulatory and blocking warnings cannot be overridden)
    --target_root   Override default 01_Accounts/_Active path
    --interactive   Interactive mode with preview and confirmation
"""

import os
import sys
import json
import shutil
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.path_resolver import (
    get_prospecting_root,
    get_drafts_folder,
    get_research_folder,
    sanitize_name
)
from src.promotion_rules import (
    PromotionGate,
    ProspectState,
    format_eligibility_report
)
from src.context_quality import render_context_quality_header

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

# Default target root for promotions
# Configure via --target_root or update this path
DEFAULT_TARGET_ROOT = os.path.expanduser("~/prospecting-output/promoted")

# Files to promote (relative patterns)
PROMOTE_FILES = {
    "email_md": "*_email.md",
    "inmail_md": "*_inmail.md",
    "sequence_md": "*_sequence.md",
    "context_quality_json": "*_context_quality.json",
    "context_quality_md": "*_context_quality.md",
}

# Files to NOT promote (raw dumps, caches)
EXCLUDE_PATTERNS = [
    "*_research_raw.json",
    "*_cache.json",
    "*_debug.json",
    "*_email_context.json"  # Internal context, not for promotion
]


# =============================================================================
# ARTIFACT LOCATOR
# =============================================================================

def find_latest_artifacts(
    company: str,
    contact: str,
    run_id: Optional[str] = None
) -> Tuple[Optional[Path], Dict[str, Path]]:
    """
    Find the latest artifacts for a company/contact.

    Args:
        company: Company name
        contact: Contact name
        run_id: Optional specific run ID (date prefix)

    Returns:
        Tuple of (context_quality_json_path, dict of artifact paths)
    """
    drafts_folder = get_drafts_folder(company)

    if not drafts_folder.exists():
        logger.error(f"Drafts folder not found: {drafts_folder}")
        return None, {}

    sanitized_contact = sanitize_name(contact)

    # Find context_quality.json files
    pattern = f"*_{sanitized_contact}_context_quality.json"
    if run_id:
        pattern = f"{run_id}_{sanitized_contact}_context_quality.json"

    context_files = list(drafts_folder.glob(pattern))

    if not context_files:
        logger.error(f"No context_quality.json found for {contact} at {company}")
        return None, {}

    # Sort by modification time (newest first)
    context_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    latest_context = context_files[0]

    # Extract date prefix from filename
    date_prefix = latest_context.name.split("_")[0]
    logger.info(f"Found latest artifacts with date: {date_prefix}")

    # Find all related artifacts
    artifacts = {}
    for artifact_type, pattern in PROMOTE_FILES.items():
        full_pattern = pattern.replace("*", f"{date_prefix}_{sanitized_contact}")
        matches = list(drafts_folder.glob(full_pattern))
        if matches:
            artifacts[artifact_type] = matches[0]

    return latest_context, artifacts


def load_context_quality(path: Path) -> Dict[str, Any]:
    """Load context_quality.json file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# PROMOTION EXECUTION
# =============================================================================

def create_research_summary(
    context_quality: Dict[str, Any],
    persona_diagnostics: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a short research summary markdown for promotion.

    Args:
        context_quality: Context quality data
        persona_diagnostics: Optional persona data

    Returns:
        Markdown string
    """
    lines = []

    company = context_quality.get("company", {})
    contact = context_quality.get("contact", {})
    mode = context_quality.get("mode", {})
    signals = context_quality.get("signals", {})
    counts = signals.get("counts", {})
    freshness = signals.get("freshness", {})

    lines.append(f"# Research Summary: {contact.get('name', 'Unknown')}")
    lines.append("")
    lines.append(f"**Company:** {company.get('name', 'Unknown')}")
    lines.append(f"**Title:** {contact.get('title', 'Unknown')}")
    lines.append(f"**Persona:** {contact.get('persona', 'Unknown')}")
    lines.append("")

    lines.append("## Confidence")
    lines.append(f"- **Mode:** {mode.get('confidence_mode', 'Unknown')}")
    lines.append(f"- **Tier:** {mode.get('tier', 'Unknown')}")
    lines.append("")

    lines.append("## Signal Coverage")
    lines.append(f"- **Total Cited:** {counts.get('total_cited', 0)}")
    lines.append(f"- **Company Cited:** {counts.get('company_cited', 0)}")
    lines.append(f"- **Person Cited:** {counts.get('person_cited', 0)}")
    lines.append(f"- **Vendor (guidance):** {counts.get('total_vendor', 0)}")
    lines.append("")

    if freshness.get("newest_cited_date"):
        lines.append("## Freshness")
        lines.append(f"- **Newest:** {freshness.get('newest_cited_date')} ({freshness.get('newest_cited_age_days')}d)")
        lines.append(f"- **Oldest:** {freshness.get('oldest_cited_date')} ({freshness.get('oldest_cited_age_days')}d)")
        lines.append("")

    warnings = signals.get("warnings", [])
    if warnings:
        lines.append("## Warnings")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    lines.append("---")
    lines.append(f"*Promoted: {datetime.now().isoformat()}*")

    return "\n".join(lines)


def create_promotion_metadata(
    context_quality: Dict[str, Any],
    persona_diagnostics: Optional[Dict[str, Any]],
    source_path: Path,
    target_path: Path
) -> Dict[str, Any]:
    """
    Create promotion metadata JSON.

    Args:
        context_quality: Context quality data
        persona_diagnostics: Optional persona data
        source_path: Source artifacts path
        target_path: Target promotion path

    Returns:
        Metadata dict
    """
    mode = context_quality.get("mode", {})
    signals = context_quality.get("signals", {})
    counts = signals.get("counts", {})
    freshness = signals.get("freshness", {})
    contact = context_quality.get("contact", {})

    return {
        "promoted_at": datetime.now().isoformat(),
        "run_id": context_quality.get("run_id"),
        "source_path": str(source_path),
        "target_path": str(target_path),
        "persona": contact.get("persona"),
        "product_motion": persona_diagnostics.get("primary_product_motion") if persona_diagnostics else None,
        "confidence_mode": mode.get("confidence_mode"),
        "tier": mode.get("tier"),
        "cited_signals": {
            "total": counts.get("total_cited", 0),
            "company": counts.get("company_cited", 0),
            "person": counts.get("person_cited", 0)
        },
        "freshness": {
            "newest_date": freshness.get("newest_cited_date"),
            "newest_age_days": freshness.get("newest_cited_age_days"),
            "oldest_date": freshness.get("oldest_cited_date"),
            "oldest_age_days": freshness.get("oldest_cited_age_days")
        },
        "warnings": signals.get("warnings", [])
    }


def get_target_folder(
    company: str,
    contact: str,
    target_root: str
) -> Path:
    """
    Get the target folder path for promotion.

    Structure: {target_root}/{company}/prospecting/{contact}/

    Args:
        company: Company name
        contact: Contact name
        target_root: Root path for accounts

    Returns:
        Path to target folder
    """
    sanitized_company = sanitize_name(company)
    sanitized_contact = sanitize_name(contact)

    return Path(target_root) / sanitized_company / "prospecting" / sanitized_contact


def execute_promotion(
    artifacts: Dict[str, Path],
    context_quality: Dict[str, Any],
    persona_diagnostics: Optional[Dict[str, Any]],
    target_folder: Path,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Execute the promotion by copying files to target.

    Args:
        artifacts: Dict of artifact type → source path
        context_quality: Context quality data
        persona_diagnostics: Optional persona data
        target_folder: Target folder path
        dry_run: If True, don't actually copy

    Returns:
        Promotion result dict
    """
    result = {
        "success": True,
        "files_copied": [],
        "files_created": [],
        "errors": []
    }

    if dry_run:
        logger.info(f"[DRY RUN] Would create folder: {target_folder}")
    else:
        target_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created target folder: {target_folder}")

    # Copy artifact files
    for artifact_type, source_path in artifacts.items():
        if not source_path.exists():
            continue

        target_path = target_folder / source_path.name

        if dry_run:
            logger.info(f"[DRY RUN] Would copy: {source_path.name}")
            result["files_copied"].append(str(target_path))
        else:
            try:
                shutil.copy2(source_path, target_path)
                logger.info(f"Copied: {source_path.name}")
                result["files_copied"].append(str(target_path))
            except Exception as e:
                logger.error(f"Failed to copy {source_path.name}: {e}")
                result["errors"].append(str(e))
                result["success"] = False

    # Create research summary
    summary_path = target_folder / "research_summary.md"
    summary_content = create_research_summary(context_quality, persona_diagnostics)

    if dry_run:
        logger.info("[DRY RUN] Would create: research_summary.md")
        result["files_created"].append(str(summary_path))
    else:
        try:
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(summary_content)
            logger.info("Created: research_summary.md")
            result["files_created"].append(str(summary_path))
        except Exception as e:
            logger.error(f"Failed to create research_summary.md: {e}")
            result["errors"].append(str(e))

    # Create promotion metadata
    source_path = artifacts.get("context_quality_json", Path("."))
    metadata = create_promotion_metadata(
        context_quality,
        persona_diagnostics,
        source_path.parent,
        target_folder
    )

    metadata_path = target_folder / "promotion_metadata.json"

    if dry_run:
        logger.info("[DRY RUN] Would create: promotion_metadata.json")
        result["files_created"].append(str(metadata_path))
    else:
        try:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            logger.info("Created: promotion_metadata.json")
            result["files_created"].append(str(metadata_path))
        except Exception as e:
            logger.error(f"Failed to create promotion_metadata.json: {e}")
            result["errors"].append(str(e))

    # Write to promotion log
    log_path = Path(target_folder).parent.parent / "promotion_log.json"
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "contact": context_quality.get("contact", {}).get("name"),
        "company": context_quality.get("company", {}).get("name"),
        "target_folder": str(target_folder),
        "success": result["success"]
    }

    if not dry_run:
        try:
            # Append to log
            existing_log = []
            if log_path.exists():
                with open(log_path, "r") as f:
                    existing_log = json.load(f)

            existing_log.append(log_entry)

            with open(log_path, "w") as f:
                json.dump(existing_log, f, indent=2)

            logger.info(f"Updated promotion log: {log_path}")
        except Exception as e:
            logger.warning(f"Could not update promotion log: {e}")

    return result


# =============================================================================
# INTERACTIVE MODE
# =============================================================================

def show_email_preview(artifacts: Dict[str, Path], max_lines: int = 30) -> str:
    """
    Show email preview from email.md file.

    Args:
        artifacts: Dict of artifact paths
        max_lines: Maximum lines to show

    Returns:
        Preview string
    """
    email_path = artifacts.get("email_md")
    if not email_path or not email_path.exists():
        return "[No email preview available]"

    try:
        with open(email_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        if len(lines) > max_lines:
            preview = "\n".join(lines[:max_lines])
            preview += f"\n\n... ({len(lines) - max_lines} more lines)"
        else:
            preview = content

        return preview
    except Exception as e:
        return f"[Error reading email: {e}]"


def format_interactive_display(
    context_quality: Dict[str, Any],
    artifacts: Dict[str, Path],
    eligibility
) -> str:
    """
    Format the interactive display with all relevant info.

    Args:
        context_quality: Context quality data
        artifacts: Artifact paths
        eligibility: Eligibility result

    Returns:
        Formatted display string
    """
    lines = []

    # Header
    lines.append("")
    lines.append("=" * 70)
    lines.append("  PROMOTION REVIEW")
    lines.append("=" * 70)
    lines.append("")

    # Contact info
    contact = context_quality.get("contact", {})
    company = context_quality.get("company", {})

    lines.append(f"Contact: {contact.get('name', 'Unknown')}")
    lines.append(f"Company: {company.get('name', 'Unknown')}")
    lines.append(f"Persona: {contact.get('persona', 'unknown')}")
    lines.append("")

    # Context quality header
    lines.append("-" * 70)
    lines.append("CONTEXT QUALITY:")
    lines.append("-" * 70)
    cq_header = render_context_quality_header(context_quality)
    lines.append(cq_header)
    lines.append("")

    # Warnings
    signals = context_quality.get("signals", {})
    warnings = signals.get("warnings", [])

    if warnings:
        lines.append("-" * 70)
        lines.append("WARNINGS:")
        lines.append("-" * 70)
        for w in warnings:
            lines.append(f"  - {w}")
        lines.append("")

    # Eligibility status
    lines.append("-" * 70)
    lines.append("ELIGIBILITY:")
    lines.append("-" * 70)
    status = "ELIGIBLE" if eligibility.eligible else "NOT ELIGIBLE"
    lines.append(f"  Status: {status}")
    if not eligibility.eligible:
        lines.append("  Reasons:")
        for r in eligibility.reasons:
            lines.append(f"    - {r}")
    lines.append(f"  Can force: {'Yes' if eligibility.can_force else 'No'}")
    lines.append("")

    # Email preview
    lines.append("-" * 70)
    lines.append("EMAIL PREVIEW:")
    lines.append("-" * 70)
    preview = show_email_preview(artifacts)
    lines.append(preview)
    lines.append("")
    lines.append("=" * 70)

    return "\n".join(lines)


def run_interactive_mode(
    context_quality: Dict[str, Any],
    artifacts: Dict[str, Path],
    eligibility,
    target_folder: Path,
    persona_diagnostics: Optional[Dict[str, Any]],
    force: bool = False
) -> Dict[str, Any]:
    """
    Run interactive promotion mode.

    Shows preview, asks for confirmation, optionally adds note.

    Args:
        context_quality: Context quality data
        artifacts: Artifact paths
        eligibility: Eligibility result
        target_folder: Target folder path
        persona_diagnostics: Optional persona data
        force: Whether force flag was passed

    Returns:
        Result dict
    """
    # Show display
    display = format_interactive_display(context_quality, artifacts, eligibility)
    print(display)

    # Check eligibility
    if not eligibility.eligible and not force:
        print("\nPromotion is NOT eligible. Use --force to override (if allowed).")
        return {"success": False, "reason": "not_eligible"}

    if not eligibility.eligible and force:
        if not eligibility.can_force:
            print("\nCannot force promotion - blocking warnings present.")
            return {"success": False, "reason": "cannot_force"}
        print("\n[FORCE MODE] Proceeding despite eligibility failure.")

    # Ask for confirmation
    print("\nPromote this artifact? [y/N]: ", end="")
    try:
        response = input().strip().lower()
    except EOFError:
        response = "n"

    if response not in ("y", "yes"):
        print("Promotion cancelled.")
        return {"success": False, "reason": "user_cancelled"}

    # Optional note
    print("Add a note (optional, press Enter to skip): ", end="")
    try:
        note = input().strip()
    except EOFError:
        note = ""

    # Execute promotion
    result = execute_promotion(
        artifacts=artifacts,
        context_quality=context_quality,
        persona_diagnostics=persona_diagnostics,
        target_folder=target_folder,
        dry_run=False
    )

    # Add note to promotion log if provided
    if note and result["success"]:
        add_promotion_note(target_folder, note)

    return result


def add_promotion_note(target_folder: Path, note: str):
    """
    Add a note to the promotion metadata.

    Args:
        target_folder: Target folder path
        note: Note to add
    """
    metadata_path = target_folder / "promotion_metadata.json"

    if metadata_path.exists():
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            metadata["promotion_note"] = note
            metadata["note_added_at"] = datetime.now().isoformat()

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Added promotion note")
        except Exception as e:
            logger.warning(f"Could not add note: {e}")


# =============================================================================
# MAIN CLI
# =============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Promote prospecting artifacts to Accounts folder"
    )
    parser.add_argument(
        "--company",
        required=True,
        help="Company name"
    )
    parser.add_argument(
        "--contact",
        required=True,
        help="Contact name"
    )
    parser.add_argument(
        "--run_id",
        help="Optional specific run ID (date prefix, e.g., 2025-01-15)"
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Show what would be promoted without copying"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Override review_required after human review (regulatory and blocking warnings cannot be overridden)"
    )
    parser.add_argument(
        "--target_root",
        default=DEFAULT_TARGET_ROOT,
        help=f"Target root folder (default: {DEFAULT_TARGET_ROOT})"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode with preview and confirmation"
    )

    args = parser.parse_args()

    logger.info(f"Promoting artifacts for {args.contact} at {args.company}")

    # Step 1: Find artifacts
    context_path, artifacts = find_latest_artifacts(
        args.company,
        args.contact,
        args.run_id
    )

    if not context_path:
        print(json.dumps({
            "success": False,
            "error": f"No artifacts found for {args.contact} at {args.company}"
        }, indent=2))
        sys.exit(1)

    logger.info(f"Found {len(artifacts)} artifact files")

    # Step 2: Load context quality
    context_quality = load_context_quality(context_path)

    # Try to load persona diagnostics from email_context.json
    persona_diagnostics = None
    email_context_path = context_path.parent / context_path.name.replace(
        "_context_quality.json", "_email_context.json"
    )
    if email_context_path.exists():
        try:
            with open(email_context_path, "r") as f:
                email_context = json.load(f)
            persona_diagnostics = email_context.get("persona_diagnostics")
        except Exception:
            pass

    # Step 3: Evaluate promotion eligibility
    gate = PromotionGate()

    # Determine current status
    # For now, assume rendered_validated if we have artifacts
    # In production, this would come from a status field
    status = ProspectState.RENDERED_VALIDATED.value

    eligibility = gate.evaluate(
        context_quality=context_quality,
        persona_diagnostics=persona_diagnostics,
        status=status,
        validation_passed=True,
        force=args.force
    )

    # Step 4: Get target folder
    target_folder = get_target_folder(
        args.company,
        args.contact,
        args.target_root
    )

    # Interactive mode - show preview and ask for confirmation
    if args.interactive:
        result = run_interactive_mode(
            context_quality=context_quality,
            artifacts=artifacts,
            eligibility=eligibility,
            target_folder=target_folder,
            persona_diagnostics=persona_diagnostics,
            force=args.force
        )

        if result.get("success"):
            print("\nPromotion completed successfully!")
            print(f"Target: {target_folder}")
        else:
            reason = result.get("reason", "unknown")
            print(f"\nPromotion not completed: {reason}")

        sys.exit(0 if result.get("success") else 1)

    # Non-interactive mode (original behavior)
    # Print eligibility report
    print(format_eligibility_report(eligibility))

    if not eligibility.eligible and not args.force:
        print(json.dumps({
            "success": False,
            "eligible": False,
            "reasons": eligibility.reasons,
            "can_force": eligibility.can_force
        }, indent=2))
        sys.exit(1)

    if not eligibility.eligible and args.force:
        if not eligibility.can_force:
            logger.error("Cannot force promotion - blocking warnings present")
            print(json.dumps({
                "success": False,
                "eligible": False,
                "reasons": eligibility.reasons,
                "can_force": False,
                "message": "Force not allowed due to blocking warnings"
            }, indent=2))
            sys.exit(1)
        logger.warning("Forcing promotion despite eligibility failure")

    # Execute promotion
    result = execute_promotion(
        artifacts=artifacts,
        context_quality=context_quality,
        persona_diagnostics=persona_diagnostics,
        target_folder=target_folder,
        dry_run=args.dry_run
    )

    # Output result
    output = {
        "success": result["success"],
        "dry_run": args.dry_run,
        "target_folder": str(target_folder),
        "files_copied": result["files_copied"],
        "files_created": result["files_created"],
        "errors": result["errors"],
        "eligibility": eligibility.to_dict()
    }

    print(json.dumps(output, indent=2))

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
