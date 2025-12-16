#!/usr/bin/env python3
"""
Outbound Run CLI - Execute batch prospect email generation

This script consumes a ranked account list and generates draft emails
by calling the existing /prospect pipeline.

Usage:
    python3 scripts/outbound_run.py --accounts accounts.csv --top_n 10

    python3 scripts/outbound_run.py \
        --accounts accounts.json \
        --top_n 5 \
        --max_drafts_per_account 2 \
        --tier B \
        --mode hybrid \
        --dry_run

Example accounts.csv:
    company_name,score,tier,domain,tags
    Acme Corp,92,A,acme.com,"quality_focused,regulatory"
    Beta Inc,88,A,beta.com,operations_focused

Example accounts.json:
    {"accounts": [
        {"company_name": "Acme Corp", "score": 92, "tier": "A"},
        {"company_name": "Beta Inc", "score": 88, "tier": "B"}
    ]}
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print colored header."""
    print(f"\n{BLUE}{BOLD}{'=' * 60}{RESET}")
    print(f"{BLUE}{BOLD}{text}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 60}{RESET}\n")


def print_section(text):
    """Print section header."""
    print(f"\n{GREEN}{text}{RESET}")
    print("-" * 40)


def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}", file=sys.stderr)


def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_info(text):
    """Print info message."""
    print(f"{BLUE}ℹ {text}{RESET}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run batch prospect email generation from ranked account list",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic run:
    python3 scripts/outbound_run.py --accounts accounts.csv

  Limited run with tier B:
    python3 scripts/outbound_run.py --accounts accounts.csv --top_n 5 --tier B

  Dry run (show plan without execution):
    python3 scripts/outbound_run.py --accounts accounts.csv --dry_run
        """
    )

    # Required
    parser.add_argument(
        "--accounts",
        required=True,
        type=Path,
        help="Path to ranked accounts file (CSV or JSON)"
    )

    # Caps and limits
    parser.add_argument(
        "--top_n",
        type=int,
        default=10,
        help="Number of top accounts to process (default: 10)"
    )
    parser.add_argument(
        "--max_drafts_per_account",
        type=int,
        default=3,
        help="Maximum drafts per account (default: 3)"
    )
    parser.add_argument(
        "--max_total_drafts",
        type=int,
        default=20,
        help="Maximum total drafts for this run (default: 20)"
    )

    # Mode settings
    parser.add_argument(
        "--tier",
        choices=["A", "B"],
        default="A",
        help="Prospect tier (default: A)"
    )
    parser.add_argument(
        "--mode",
        choices=["hybrid", "legacy"],
        default="hybrid",
        help="Email generation mode (default: hybrid)"
    )
    parser.add_argument(
        "--exp",
        dest="experiment",
        help="Optional experiment name for A/B testing"
    )

    # Refresh behavior
    parser.add_argument(
        "--refresh",
        choices=["none", "company", "contact", "all"],
        default="none",
        help="Cache refresh behavior (default: none) - v1 is no-op except logging"
    )

    # Skip/filter settings
    parser.add_argument(
        "--since_days",
        type=int,
        default=7,
        help="Skip accounts with drafts within N days (default: 7)"
    )

    # Output settings
    parser.add_argument(
        "--output_root",
        type=Path,
        help="Override PROSPECTING_OUTPUT_ROOT for this run"
    )

    # Control flags
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Show plan without executing (no API calls, no file writes)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress non-essential output"
    )

    return parser.parse_args()


def setup_logging(verbose: bool, quiet: bool):
    """Configure logging based on verbosity."""
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def display_config(config):
    """Display run configuration."""
    print_section("Run Configuration")
    print(f"  Accounts file:        {config.accounts_path}")
    print(f"  Top N accounts:       {config.top_n}")
    print(f"  Max drafts/account:   {config.max_drafts_per_account}")
    print(f"  Max total drafts:     {config.max_total_drafts}")
    print(f"  Tier:                 {config.tier}")
    print(f"  Mode:                 {config.mode}")
    print(f"  Experiment:           {config.experiment or 'None'}")
    print(f"  Skip if drafted in:   {config.since_days} days")
    print(f"  Output root:          {config.output_root or 'default'}")
    print(f"  Dry run:              {config.dry_run}")


def display_summary(result):
    """Display run summary."""
    print_section("Run Summary")

    summary = result.summary
    print(f"  Accounts processed:   {summary.accounts_processed}")
    print(f"  Accounts skipped:     {summary.accounts_skipped}")
    print(f"  Prepared for render:  {summary.prepared_for_rendering}")
    print(f"  Rejected:             {summary.rejected}")

    # Calculate preparation rate
    total_attempts = summary.prepared_for_rendering + summary.rejected
    if total_attempts > 0:
        prep_rate = (summary.prepared_for_rendering / total_attempts) * 100
        print(f"  Preparation rate:     {prep_rate:.1f}%")


def display_accounts_detail(result, verbose: bool):
    """Display per-account details."""
    if not verbose:
        return

    print_section("Account Details")

    for account in result.accounts:
        status_color = GREEN if account.status == "processed" else YELLOW
        print(f"\n{status_color}{account.company_name}{RESET} (Score: {account.score})")

        for contact in account.contacts:
            if contact.status == "prepared_for_rendering":
                print(f"  {GREEN}✓{RESET} {contact.name} ({contact.title}) [PREPARED]")
                print(f"    Confidence: {contact.confidence_mode}, Signals: {contact.cited_signals}")
            elif contact.status == "rejected":
                print(f"  {RED}✗{RESET} {contact.name} ({contact.title}) [REJECTED]")
                print(f"    Reason: {contact.rejection_reason}")
            elif contact.status == "skipped":
                print(f"  {YELLOW}○{RESET} {contact.name} ({contact.title}) [SKIPPED]")
                if contact.rejection_reason:
                    print(f"    Reason: {contact.rejection_reason}")
            else:
                print(f"  {YELLOW}○{RESET} {contact.name} ({contact.title}) - {contact.status}")

    if result.skipped_accounts:
        print_section("Skipped Accounts")
        for skip in result.skipped_accounts:
            print(f"  {YELLOW}○{RESET} {skip['company_name']}: {skip['reason']}")


def main():
    """Main entry point."""
    args = parse_args()

    # Setup logging
    setup_logging(args.verbose, args.quiet)

    # Load environment variables
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        print_warning(f"No .env file found at {env_path}")

    print_header(f"Outbound Run - {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Import orchestrator (after setting up path)
    from src.outbound_orchestrator import OutboundOrchestrator, OutboundConfig

    # Validate accounts file exists
    if not args.accounts.exists():
        print_error(f"Accounts file not found: {args.accounts}")
        return 1

    # Build config
    config = OutboundConfig(
        accounts_path=args.accounts,
        top_n=args.top_n,
        max_drafts_per_account=args.max_drafts_per_account,
        max_total_drafts=args.max_total_drafts,
        tier=args.tier,
        mode=args.mode,
        experiment=args.experiment,
        refresh=args.refresh,
        dry_run=args.dry_run,
        since_days=args.since_days,
        output_root=args.output_root
    )

    # Display config
    if not args.quiet:
        display_config(config)

    # Refresh behavior logging (v1 no-op)
    if config.refresh != "none":
        print_info(f"Refresh mode '{config.refresh}' logged but not yet implemented (v1)")

    # Initialize orchestrator
    try:
        orchestrator = OutboundOrchestrator(config)
        print_success(f"Orchestrator initialized (output_root: {orchestrator.output_root})")
    except Exception as e:
        print_error(f"Failed to initialize orchestrator: {e}")
        return 1

    # Check ZoomInfo availability
    if orchestrator.zoominfo_available:
        print_success("ZoomInfo client available")
    else:
        print_warning("ZoomInfo unavailable - contact discovery will be skipped")

    # Dry run notice
    if args.dry_run:
        print_warning("DRY RUN MODE - No drafts will be prepared, no files written")

    # Run orchestration
    print_section("Executing Run")
    try:
        result = orchestrator.run()
    except Exception as e:
        print_error(f"Run failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    # Display results
    if not args.quiet:
        display_summary(result)
        display_accounts_detail(result, args.verbose)

    # Report dashboard location
    if not args.dry_run:
        runs_folder = orchestrator.output_root / "runs"
        print_section("Output Files")
        print(f"  Dashboard (MD):   {runs_folder / f'{result.run_date}_outbound_run.md'}")
        print(f"  Dashboard (JSON): {runs_folder / f'{result.run_date}_outbound_run.json'}")

    # Final status
    print_header("Run Complete")
    if result.summary.prepared_for_rendering > 0:
        print_success(f"Prepared {result.summary.prepared_for_rendering} draft(s) for rendering")
        return 0
    elif args.dry_run:
        print_info("Dry run completed - no drafts prepared")
        return 0
    else:
        print_warning("No drafts were prepared for rendering")
        return 2


if __name__ == "__main__":
    sys.exit(main())
