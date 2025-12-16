#!/usr/bin/env python3
"""
Approve for Send - Mark validated prospecting artifacts as approved for outbound

This script handles the intentional approval of prospecting artifacts.
Approved artifacts STAY in 02_Prospecting (not moved to 01_Accounts).

Approval means: Human reviewed and approved to send outbound.
Approval does NOT imply an opportunity exists.

Usage:
    python3 scripts/approve_for_send.py --company "Acme Corp" --contact "John Smith"
    python3 scripts/approve_for_send.py --company "Acme Corp" --contact "John Smith" --dry_run
    python3 scripts/approve_for_send.py --company "Acme Corp" --contact "John Smith" --force
    python3 scripts/approve_for_send.py --company "Acme Corp" --contact "John Smith" --interactive

CLI Flags:
    --company       Company name (required)
    --contact       Contact name (required)
    --run_id        Optional specific run ID to approve
    --dry_run       Show what would be approved without changes
    --force         Override review_required gate after human review (some checks cannot be overridden)
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
from src.approval_rules import (
    ApprovalGate,
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

# Approved artifacts stay in the prospecting folder
# Structure: prospecting-output/{Company}/approved/
DEFAULT_PROSPECTING_ROOT = os.path.expanduser(
    os.environ.get("PROSPECTING_OUTPUT_ROOT", "~/prospecting-output")
)

# Files to copy to approved folder (relative patterns)
APPROVE_FILES = {
    "email_md": "*_email.md",
    "inmail_md": "*_inmail.md",
    "sequence_md": "*_sequence.md",
    "context_quality_json": "*_context_quality.json",
    "context_quality_md": "*_context_quality.md",
}

# Files to NOT copy (raw dumps, caches)
EXCLUDE_PATTERNS = [
    "*_research_raw.json",
    "*_cache.json",
    "*_debug.json",
    "*_email_context.json"  # Internal context, not needed in approved
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
    for artifact_type, pattern in APPROVE_FILES.items():
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
# APPROVAL EXECUTION
# =============================================================================

def create_approval_summary(
    context_quality: Dict[str, Any],
    persona_diagnostics: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a short approval summary markdown.

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

    lines.append(f"# Approval Summary: {contact.get('name', 'Unknown')}")
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
    lines.append(f"*Approved for send: {datetime.now().isoformat()}*")

    return "\n".join(lines)


def create_approval_metadata(
    context_quality: Dict[str, Any],
    persona_diagnostics: Optional[Dict[str, Any]],
    source_path: Path,
    target_path: Path
) -> Dict[str, Any]:
    """
    Create approval metadata JSON.

    Args:
        context_quality: Context quality data
        persona_diagnostics: Optional persona data
        source_path: Source artifacts path
        target_path: Target approval path

    Returns:
        Metadata dict
    """
    mode = context_quality.get("mode", {})
    signals = context_quality.get("signals", {})
    counts = signals.get("counts", {})
    freshness = signals.get("freshness", {})
    contact = context_quality.get("contact", {})

    return {
        "approved_at": datetime.now().isoformat(),
        "run_id": context_quality.get("run_id"),
        "source_path": str(source_path),
        "approved_path": str(target_path),
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


def get_approved_folder(
    company: str,
    contact: str,
    prospecting_root: str = DEFAULT_PROSPECTING_ROOT
) -> Path:
    """
    Get the approved folder path within 02_Prospecting.

    Structure: {prospecting_root}/{company}/approved/{contact}/

    Approved artifacts stay in the prospecting workspace.
    Nothing moves to 01_Accounts/_Active during prospecting.

    Args:
        company: Company name
        contact: Contact name
        prospecting_root: Root path for prospecting

    Returns:
        Path to approved folder
    """
    sanitized_company = sanitize_name(company)
    sanitized_contact = sanitize_name(contact)

    return Path(prospecting_root) / sanitized_company / "approved" / sanitized_contact


def execute_approval(
    artifacts: Dict[str, Path],
    context_quality: Dict[str, Any],
    persona_diagnostics: Optional[Dict[str, Any]],
    approved_folder: Path,
    prospecting_root: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Execute the approval by copying files to approved folder.

    Approved artifacts stay in 02_Prospecting - NOT moved to 01_Accounts.

    Args:
        artifacts: Dict of artifact type -> source path
        context_quality: Context quality data
        persona_diagnostics: Optional persona data
        approved_folder: Target approved folder path
        prospecting_root: Root path for prospecting
        dry_run: If True, don't actually copy

    Returns:
        Approval result dict
    """
    result = {
        "success": True,
        "files_copied": [],
        "files_created": [],
        "errors": []
    }

    if dry_run:
        logger.info(f"[DRY RUN] Would create folder: {approved_folder}")
    else:
        approved_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created approved folder: {approved_folder}")

    # Copy artifact files
    for artifact_type, source_path in artifacts.items():
        if not source_path.exists():
            continue

        target_path = approved_folder / source_path.name

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

    # Create approval summary
    summary_path = approved_folder / "approval_summary.md"
    summary_content = create_approval_summary(context_quality, persona_diagnostics)

    if dry_run:
        logger.info("[DRY RUN] Would create: approval_summary.md")
        result["files_created"].append(str(summary_path))
    else:
        try:
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(summary_content)
            logger.info("Created: approval_summary.md")
            result["files_created"].append(str(summary_path))
        except Exception as e:
            logger.error(f"Failed to create approval_summary.md: {e}")
            result["errors"].append(str(e))

    # Create approval metadata
    source_path = artifacts.get("context_quality_json", Path("."))
    metadata = create_approval_metadata(
        context_quality,
        persona_diagnostics,
        source_path.parent,
        approved_folder
    )

    metadata_path = approved_folder / "approval_metadata.json"

    if dry_run:
        logger.info("[DRY RUN] Would create: approval_metadata.json")
        result["files_created"].append(str(metadata_path))
    else:
        try:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            logger.info("Created: approval_metadata.json")
            result["files_created"].append(str(metadata_path))
        except Exception as e:
            logger.error(f"Failed to create approval_metadata.json: {e}")
            result["errors"].append(str(e))

    # Write to approval log (stays in prospecting root)
    log_path = Path(prospecting_root) / "approval_log.json"
    company_name = context_quality.get("company", {}).get("name")
    contact_name = context_quality.get("contact", {}).get("name")

    # Use folder-based company name for consistent lookup
    sanitized_company = sanitize_name(company_name) if company_name else "unknown"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "contact": contact_name,
        "company": sanitized_company,  # Use folder-based name for lookup
        "approved_folder": str(approved_folder),
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

            logger.info(f"Updated approval log: {log_path}")
        except Exception as e:
            logger.warning(f"Could not update approval log: {e}")

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
    lines.append("  APPROVE FOR SEND")
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
    approved_folder: Path,
    prospecting_root: str,
    persona_diagnostics: Optional[Dict[str, Any]],
    force: bool = False
) -> Dict[str, Any]:
    """
    Run interactive approval mode.

    Shows preview, asks for confirmation, optionally adds note.

    Args:
        context_quality: Context quality data
        artifacts: Artifact paths
        eligibility: Eligibility result
        approved_folder: Target approved folder path
        prospecting_root: Root path for prospecting
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
        print("\nApproval is NOT eligible. Use --force to override (if allowed).")
        return {"success": False, "reason": "not_eligible"}

    if not eligibility.eligible and force:
        if not eligibility.can_force:
            print("\nCannot force approval - blocking warnings present.")
            return {"success": False, "reason": "cannot_force"}
        print("\n[FORCE MODE] Proceeding despite eligibility failure.")

    # Ask for confirmation
    print("\nApprove for send? [y/N]: ", end="")
    try:
        response = input().strip().lower()
    except EOFError:
        response = "n"

    if response not in ("y", "yes"):
        print("Approval cancelled.")
        return {"success": False, "reason": "user_cancelled"}

    # Optional note
    print("Add a note (optional, press Enter to skip): ", end="")
    try:
        note = input().strip()
    except EOFError:
        note = ""

    # Execute approval
    result = execute_approval(
        artifacts=artifacts,
        context_quality=context_quality,
        persona_diagnostics=persona_diagnostics,
        approved_folder=approved_folder,
        prospecting_root=prospecting_root,
        dry_run=False
    )

    # Add note to approval metadata if provided
    if note and result["success"]:
        add_approval_note(approved_folder, note)

    return result


def add_approval_note(approved_folder: Path, note: str):
    """
    Add a note to the approval metadata.

    Args:
        approved_folder: Approved folder path
        note: Note to add
    """
    metadata_path = approved_folder / "approval_metadata.json"

    if metadata_path.exists():
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            metadata["approval_note"] = note
            metadata["note_added_at"] = datetime.now().isoformat()

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Added approval note")
        except Exception as e:
            logger.warning(f"Could not add note: {e}")


# =============================================================================
# MAIN CLI
# =============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Approve prospecting artifacts for sending (stays in 02_Prospecting)"
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
        help="Show what would be approved without changes"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Override review_required after human review (regulatory and blocking warnings cannot be overridden)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode with preview and confirmation"
    )

    args = parser.parse_args()

    logger.info(f"Approving artifacts for {args.contact} at {args.company}")

    # Get prospecting root
    prospecting_root = os.environ.get("PROSPECTING_OUTPUT_ROOT", DEFAULT_PROSPECTING_ROOT)

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

    # Step 3: Evaluate approval eligibility
    gate = ApprovalGate()

    # Determine current status
    # For now, assume rendered_validated if we have artifacts
    status = ProspectState.RENDERED_VALIDATED.value

    eligibility = gate.evaluate(
        context_quality=context_quality,
        persona_diagnostics=persona_diagnostics,
        status=status,
        validation_passed=True,
        force=args.force
    )

    # Step 4: Get approved folder (stays in 02_Prospecting)
    approved_folder = get_approved_folder(
        args.company,
        args.contact,
        prospecting_root
    )

    # Interactive mode - show preview and ask for confirmation
    if args.interactive:
        result = run_interactive_mode(
            context_quality=context_quality,
            artifacts=artifacts,
            eligibility=eligibility,
            approved_folder=approved_folder,
            prospecting_root=prospecting_root,
            persona_diagnostics=persona_diagnostics,
            force=args.force
        )

        if result.get("success"):
            print("\nApproval completed successfully!")
            print(f"Approved folder: {approved_folder}")
            print("(Artifacts remain in 02_Prospecting, not moved to 01_Accounts)")
        else:
            reason = result.get("reason", "unknown")
            print(f"\nApproval not completed: {reason}")

        sys.exit(0 if result.get("success") else 1)

    # Non-interactive mode
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
            logger.error("Cannot force approval - blocking warnings present")
            print(json.dumps({
                "success": False,
                "eligible": False,
                "reasons": eligibility.reasons,
                "can_force": False,
                "message": "Force not allowed due to blocking warnings"
            }, indent=2))
            sys.exit(1)
        logger.warning("Forcing approval despite eligibility failure")

    # Execute approval
    result = execute_approval(
        artifacts=artifacts,
        context_quality=context_quality,
        persona_diagnostics=persona_diagnostics,
        approved_folder=approved_folder,
        prospecting_root=prospecting_root,
        dry_run=args.dry_run
    )

    # Output result
    output = {
        "success": result["success"],
        "dry_run": args.dry_run,
        "approved_folder": str(approved_folder),
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
