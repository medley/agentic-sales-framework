"""
Path Resolver - Centralized path management for prospecting outputs

All output paths MUST come from this module. Never hardcode paths elsewhere.

Configuration:
    PROSPECTING_OUTPUT_ROOT: Base directory for all prospecting outputs
    Can be overridden via environment variable PROSPECTING_OUTPUT_ROOT
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# Default output root - prospecting execution folder (separate from CRM/deal history)
# Structure: {Company}/drafts/, {Company}/research/
# Override with PROSPECTING_OUTPUT_ROOT environment variable
DEFAULT_PROSPECTING_OUTPUT_ROOT = os.path.expanduser("~/prospecting-output")

# Temp directory for intermediate files (within prospecting system)
# Override with PROSPECTING_TEMP_ROOT environment variable
DEFAULT_TEMP_ROOT = os.path.expanduser("~/.prospecting/tmp")

def get_temp_root() -> Path:
    """
    Get the temp directory for intermediate pipeline files.

    Returns:
        Path object to the temp root

    Priority:
        1. PROSPECTING_TEMP_ROOT environment variable
        2. DEFAULT_TEMP_ROOT constant
    """
    root = os.environ.get('PROSPECTING_TEMP_ROOT', DEFAULT_TEMP_ROOT)
    path = Path(root)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_research_raw_path() -> Path:
    """Get path for raw research JSON (intermediate file)."""
    return get_temp_root() / "prospect_research_raw.json"


def get_email_context_path() -> Path:
    """Get path for email context JSON (intermediate file)."""
    return get_temp_root() / "email_context.json"


def get_prospect_status_path() -> Path:
    """Get path for prospect status JSON (intermediate file)."""
    return get_temp_root() / "prospect_status.json"


def get_prospecting_root() -> Path:
    """
    Get the root directory for all prospecting outputs.

    Returns:
        Path object to the prospecting output root

    Priority:
        1. PROSPECTING_OUTPUT_ROOT environment variable
        2. DEFAULT_PROSPECTING_OUTPUT_ROOT constant
    """
    root = os.environ.get('PROSPECTING_OUTPUT_ROOT', DEFAULT_PROSPECTING_OUTPUT_ROOT)
    return Path(root)


def get_company_folder(company: str) -> Path:
    """
    Get the folder path for a specific company.

    Args:
        company: Company name (will be sanitized for filesystem)

    Returns:
        Path to company folder: {root}/{company}/
    """
    sanitized = sanitize_name(company)
    return get_prospecting_root() / sanitized


def get_research_folder(company: str) -> Path:
    """
    Get the research subfolder for a company.

    Args:
        company: Company name

    Returns:
        Path to research folder: {root}/{company}/research/
    """
    return get_company_folder(company) / "research"


def get_drafts_folder(company: str) -> Path:
    """
    Get the drafts subfolder for a company.

    Args:
        company: Company name

    Returns:
        Path to drafts folder: {root}/{company}/drafts/
    """
    return get_company_folder(company) / "drafts"


def get_research_path(company: str, contact: str, date: Optional[str] = None) -> Path:
    """
    Get the full path for a research output file.

    Args:
        company: Company name
        contact: Contact name
        date: Date string (YYYY-MM-DD), defaults to today

    Returns:
        Path: {root}/{company}/research/{date}_{contact}_research.md
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    filename = f"{date}_{sanitize_name(contact)}_research.md"
    return get_research_folder(company) / filename


def get_email_draft_path(company: str, contact: str, date: Optional[str] = None) -> Path:
    """
    Get the full path for an email draft output file.

    Args:
        company: Company name
        contact: Contact name
        date: Date string (YYYY-MM-DD), defaults to today

    Returns:
        Path: {root}/{company}/drafts/{date}_{contact}_email.md
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    filename = f"{date}_{sanitize_name(contact)}_email.md"
    return get_drafts_folder(company) / filename


def get_inmail_draft_path(company: str, contact: str, date: Optional[str] = None) -> Path:
    """
    Get the full path for an InMail draft output file.

    Args:
        company: Company name
        contact: Contact name
        date: Date string (YYYY-MM-DD), defaults to today

    Returns:
        Path: {root}/{company}/drafts/{date}_{contact}_inmail.md
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    filename = f"{date}_{sanitize_name(contact)}_inmail.md"
    return get_drafts_folder(company) / filename


def get_sequence_path(company: str, contact: str, date: Optional[str] = None) -> Path:
    """
    Get the full path for a cadence sequence output file.

    Args:
        company: Company name
        contact: Contact name
        date: Date string (YYYY-MM-DD), defaults to today

    Returns:
        Path: {root}/{company}/drafts/{date}_{contact}_sequence.md
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    filename = f"{date}_{sanitize_name(contact)}_sequence.md"
    return get_drafts_folder(company) / filename


def get_output_path(company: str, contact: str) -> dict:
    """
    Get all output paths for a prospect.

    Args:
        company: Company name
        contact: Contact name

    Returns:
        Dict with keys: root, company_folder, research_folder, drafts_folder,
                        research_file, email_file, inmail_file, sequence_file
    """
    return {
        'root': str(get_prospecting_root()),
        'company_folder': str(get_company_folder(company)),
        'research_folder': str(get_research_folder(company)),
        'drafts_folder': str(get_drafts_folder(company)),
        'research_file': str(get_research_path(company, contact)),
        'email_file': str(get_email_draft_path(company, contact)),
        'inmail_file': str(get_inmail_draft_path(company, contact)),
        'sequence_file': str(get_sequence_path(company, contact)),
    }


def ensure_folders_exist(company: str) -> dict:
    """
    Create all necessary folders for a company if they don't exist.

    Args:
        company: Company name

    Returns:
        Dict with created folder paths
    """
    research_folder = get_research_folder(company)
    drafts_folder = get_drafts_folder(company)

    research_folder.mkdir(parents=True, exist_ok=True)
    drafts_folder.mkdir(parents=True, exist_ok=True)

    return {
        'research_folder': str(research_folder),
        'drafts_folder': str(drafts_folder)
    }


def sanitize_name(name: str) -> str:
    """
    Sanitize a name for use in filesystem paths.

    - Replaces spaces with hyphens
    - Removes special characters except hyphens and underscores
    - Converts to title case

    Args:
        name: Raw name string

    Returns:
        Sanitized name safe for filesystem
    """
    # Replace spaces with hyphens
    sanitized = name.replace(' ', '-')

    # Remove characters that aren't alphanumeric, hyphen, or underscore
    sanitized = ''.join(c for c in sanitized if c.isalnum() or c in '-_')

    # Remove consecutive hyphens
    while '--' in sanitized:
        sanitized = sanitized.replace('--', '-')

    # Strip leading/trailing hyphens
    sanitized = sanitized.strip('-')

    return sanitized


# =============================================================================
# Company Intel Paths - Account-level intelligence storage
# =============================================================================

def get_accounts_root() -> Path:
    """
    Get the root directory for all account intel.

    Returns:
        Path: {PROSPECTING_OUTPUT_ROOT}/accounts/
    """
    return get_prospecting_root() / "accounts"


def get_account_folder(primary_account_id: str) -> Path:
    """
    Get the folder path for a specific account (by primary_account_id).

    Args:
        primary_account_id: Salesforce Primary Account ID (canonical key)

    Returns:
        Path: {accounts_root}/{primary_account_id}/
    """
    return get_accounts_root() / primary_account_id


def get_intel_folder(primary_account_id: str) -> Path:
    """
    Get the intel subfolder for an account.

    Args:
        primary_account_id: Salesforce Primary Account ID

    Returns:
        Path: {account_folder}/intel/
    """
    return get_account_folder(primary_account_id) / "intel"


def get_provider_folder(primary_account_id: str, provider: str) -> Path:
    """
    Get the provider-specific folder within intel.

    Args:
        primary_account_id: Salesforce Primary Account ID
        provider: Provider name (e.g., 'sec', 'fda', 'news')

    Returns:
        Path: {intel_folder}/{provider}/
    """
    return get_intel_folder(primary_account_id) / provider


def get_sites_folder(primary_account_id: str) -> Path:
    """
    Get the sites subfolder for an account (for site-specific data).

    Args:
        primary_account_id: Salesforce Primary Account ID

    Returns:
        Path: {account_folder}/sites/
    """
    return get_account_folder(primary_account_id) / "sites"


def get_site_folder(primary_account_id: str, site_account_id: str) -> Path:
    """
    Get a specific site's folder within the account.

    Args:
        primary_account_id: Salesforce Primary Account ID
        site_account_id: Salesforce Site Account ID

    Returns:
        Path: {sites_folder}/{site_account_id}/
    """
    return get_sites_folder(primary_account_id) / site_account_id


def ensure_intel_folders_exist(primary_account_id: str, providers: list = None) -> dict:
    """
    Create all necessary intel folders for an account.

    Args:
        primary_account_id: Salesforce Primary Account ID
        providers: Optional list of providers to create folders for

    Returns:
        Dict with created folder paths
    """
    intel_folder = get_intel_folder(primary_account_id)
    intel_folder.mkdir(parents=True, exist_ok=True)

    created = {
        'intel_folder': str(intel_folder)
    }

    # Create provider folders if specified
    if providers:
        for provider in providers:
            provider_folder = get_provider_folder(primary_account_id, provider)
            provider_folder.mkdir(parents=True, exist_ok=True)
            created[f'{provider}_folder'] = str(provider_folder)

    return created


# =============================================================================
# Context Quality Paths - Deliverable quality metadata
# =============================================================================

def get_context_quality_json_path(company: str, contact: str, date: Optional[str] = None) -> Path:
    """
    Get the path for context_quality.json deliverable.

    Args:
        company: Company name
        contact: Contact name
        date: Date string (YYYY-MM-DD), defaults to today

    Returns:
        Path: {drafts_folder}/{date}_{contact}_context_quality.json
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    filename = f"{date}_{sanitize_name(contact)}_context_quality.json"
    return get_drafts_folder(company) / filename


def get_context_quality_md_path(company: str, contact: str, date: Optional[str] = None) -> Path:
    """
    Get the path for context_quality.md deliverable.

    Args:
        company: Company name
        contact: Contact name
        date: Date string (YYYY-MM-DD), defaults to today

    Returns:
        Path: {drafts_folder}/{date}_{contact}_context_quality.md
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    filename = f"{date}_{sanitize_name(contact)}_context_quality.md"
    return get_drafts_folder(company) / filename


def get_deliverables_paths(company: str, contact: str, date: Optional[str] = None) -> dict:
    """
    Get all deliverable paths for a prospect including context quality.

    Args:
        company: Company name
        contact: Contact name
        date: Date string (YYYY-MM-DD), defaults to today

    Returns:
        Dict with all deliverable paths
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    return {
        'drafts_folder': str(get_drafts_folder(company)),
        'email_file': str(get_email_draft_path(company, contact, date)),
        'inmail_file': str(get_inmail_draft_path(company, contact, date)),
        'sequence_file': str(get_sequence_path(company, contact, date)),
        'context_quality_json': str(get_context_quality_json_path(company, contact, date)),
        'context_quality_md': str(get_context_quality_md_path(company, contact, date)),
    }


# CLI interface for testing
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python path_resolver.py <command> [args]")
        print("Commands:")
        print("  root                      - Print prospecting root path")
        print("  temp                      - Print temp root path")
        print("  research-raw              - Print research raw JSON path")
        print("  email-context             - Print email context JSON path")
        print("  prospect-status           - Print prospect status JSON path")
        print("  paths <company> <contact> - Print all paths for prospect")
        print("  ensure <company>          - Create folders for company")
        sys.exit(1)

    command = sys.argv[1]

    if command == "root":
        print(get_prospecting_root())

    elif command == "temp":
        print(get_temp_root())

    elif command == "research-raw":
        print(get_research_raw_path())

    elif command == "email-context":
        print(get_email_context_path())

    elif command == "prospect-status":
        print(get_prospect_status_path())

    elif command == "paths":
        if len(sys.argv) < 4:
            print("Usage: python path_resolver.py paths <company> <contact>")
            sys.exit(1)
        company = sys.argv[2]
        contact = sys.argv[3]
        paths = get_output_path(company, contact)
        print(json.dumps(paths, indent=2))

    elif command == "ensure":
        if len(sys.argv) < 3:
            print("Usage: python path_resolver.py ensure <company>")
            sys.exit(1)
        company = sys.argv[2]
        folders = ensure_folders_exist(company)
        print(json.dumps(folders, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
