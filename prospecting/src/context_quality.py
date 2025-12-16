"""
Context Quality - Shared utilities for data freshness, completeness, and quality headers

This module makes data quality visible everywhere the system produces output.
It ensures polished outputs cannot hide thin, stale, or incomplete inputs.

Used by:
- Prospecting email generation (prospect_brief context quality)
- Deal analysis (folder freshness and completeness)
- Competitive intel (battle card age warnings)

Usage:
    from context_quality import (
        compute_prospect_context_quality,
        compute_deal_context_quality,
        get_battle_card_age_warning,
        format_prospect_context_header,
        format_deal_context_header
    )
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


# =============================================================================
# HELPERS
# =============================================================================

def _safe_dict(value: Any, default: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Safely get a dict value, handling None and non-dict types.

    This handles the case where dict.get("key", {}) returns None because
    the key exists with value None, rather than the key being missing.

    Args:
        value: The value to check (may be None, dict, or other)
        default: Default dict to return if value is None/invalid

    Returns:
        The value if it's a dict, otherwise default or empty dict
    """
    if value is None:
        return default if default is not None else {}
    if isinstance(value, dict):
        return value
    return default if default is not None else {}


def _safe_list(value: Any, default: Optional[List] = None) -> List[Any]:
    """
    Safely get a list value, handling None and non-list types.

    Args:
        value: The value to check (may be None, list, or other)
        default: Default list to return if value is None/invalid

    Returns:
        The value if it's a list, otherwise default or empty list
    """
    if value is None:
        return default if default is not None else []
    if isinstance(value, list):
        return value
    return default if default is not None else []


# =============================================================================
# CONFIGURATION
# =============================================================================

# Default staleness thresholds (in days)
STALENESS_THRESHOLDS = {
    'battle_card': 180,          # 6 months - battle cards older than this get warning
    'deal_folder_stale': 30,     # 30 days - deal folder not updated
    'deal_folder_cold': 90,      # 90 days - deal folder is cold
    'signal_stale': 90,          # 90 days - signal considered stale
    'transcript_recent': 30,     # 30 days - transcript considered recent
}

# Expected files for deal folder completeness
EXPECTED_DEAL_FILES = {
    'required': [
        '_README.md',
        '{account}_people.md',
    ],
    'recommended': [
        'context/meddpic.md',
        'context/stakeholders.md',
    ],
    'valuable': [
        'conversations/',  # directory with emails/transcripts
        'research/',       # directory with analysis
    ]
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ProspectContextQuality:
    """Context quality assessment for prospecting emails."""

    # Confidence mode (from existing logic)
    confidence_mode: str  # HIGH | MEDIUM | LOW | GENERIC

    # Signal counts
    cited_signal_count: int      # Signals with real URLs (public_url, user_provided)
    vendor_signal_count: int     # Signals from ZoomInfo etc (vendor_data)
    inferred_signal_count: int   # Signals without sources (inferred)
    total_signal_count: int

    # Signal dates
    oldest_signal_date: Optional[str]   # ISO format or None
    newest_signal_date: Optional[str]   # ISO format or None
    signal_age_days: Optional[int]      # Age of oldest signal

    # Research sources used
    zoominfo_used: bool
    perplexity_used: bool
    perplexity_has_citations: bool
    webfetch_used: bool
    user_context_provided: bool

    # Warnings
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class DealContextQuality:
    """Context quality assessment for deal analysis."""

    # Folder freshness
    folder_path: str
    folder_last_modified: Optional[str]  # ISO format
    oldest_file_date: Optional[str]      # ISO format
    newest_file_date: Optional[str]      # ISO format
    days_since_update: Optional[int]

    # File coverage
    total_files_found: int
    required_files_present: int
    required_files_total: int
    recommended_files_present: int
    recommended_files_total: int

    # Conversation coverage
    transcripts_last_30_days: int
    emails_present: bool

    # Stakeholder coverage
    named_stakeholders: int
    stakeholder_roles_unknown: int

    # Completeness score (0-100)
    completeness_score: int

    # Freshness classification
    freshness_status: str  # CURRENT | STALE | COLD

    # Warnings
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


# =============================================================================
# PROSPECTING CONTEXT QUALITY
# =============================================================================

def compute_prospect_context_quality(
    prospect_brief: Dict[str, Any],
    research_data: Dict[str, Any]
) -> ProspectContextQuality:
    """
    Compute context quality for a prospecting email generation run.

    Args:
        prospect_brief: The prospect brief from relevance_engine
        research_data: Raw research data from orchestrator

    Returns:
        ProspectContextQuality with all computed fields
    """
    # Safely handle None values
    prospect_brief = _safe_dict(prospect_brief)
    research_data = _safe_dict(research_data)

    warnings = []

    # Get signals (support both old and new terminology)
    signals = _safe_list(prospect_brief.get('cited_signals') or prospect_brief.get('verified_signals'))

    # Count signals by type
    cited_count = 0
    vendor_count = 0
    inferred_count = 0
    signal_dates = []

    for signal in signals:
        source_type = signal.get('source_type', 'inferred')

        if source_type in ('public_url', 'user_provided'):
            cited_count += 1
        elif source_type == 'vendor_data':
            vendor_count += 1
        else:
            inferred_count += 1

        # Extract signal date if available
        signal_date = _extract_signal_date(signal)
        if signal_date:
            signal_dates.append(signal_date)

    # Compute date ranges
    oldest_date = None
    newest_date = None
    signal_age_days = None

    if signal_dates:
        signal_dates.sort()
        oldest_date = signal_dates[0].isoformat()
        newest_date = signal_dates[-1].isoformat()
        signal_age_days = (datetime.now() - signal_dates[0]).days

        if signal_age_days > STALENESS_THRESHOLDS['signal_stale']:
            warnings.append(f"Oldest signal is {signal_age_days} days old - may be outdated")

    # Check research sources
    zoominfo_used = bool(research_data.get('zoominfo') or research_data.get('contact'))
    perplexity_data = _safe_dict(research_data.get('perplexity'))
    perplexity_used = bool(perplexity_data)
    perplexity_has_citations = bool(_safe_list(perplexity_data.get('cited_claims')))
    webfetch_used = bool(research_data.get('webfetch'))
    user_context_provided = bool(research_data.get('user_context'))

    # Add warnings for thin research
    if not perplexity_has_citations and cited_count == 0:
        warnings.append("No cited signals - claims cannot be verified")

    if cited_count == 0 and vendor_count > 0:
        warnings.append("Only vendor data available - cannot make explicit claims")

    if not zoominfo_used and not perplexity_used:
        warnings.append("No external research sources used")

    # Get confidence mode
    confidence_mode = prospect_brief.get('confidence_tier', 'generic').upper()

    return ProspectContextQuality(
        confidence_mode=confidence_mode,
        cited_signal_count=cited_count,
        vendor_signal_count=vendor_count,
        inferred_signal_count=inferred_count,
        total_signal_count=len(signals),
        oldest_signal_date=oldest_date,
        newest_signal_date=newest_date,
        signal_age_days=signal_age_days,
        zoominfo_used=zoominfo_used,
        perplexity_used=perplexity_used,
        perplexity_has_citations=perplexity_has_citations,
        webfetch_used=webfetch_used,
        user_context_provided=user_context_provided,
        warnings=warnings
    )


def _extract_signal_date(signal: Dict[str, Any]) -> Optional[datetime]:
    """
    Extract date from a signal, estimating from recency_days if needed.

    Args:
        signal: Signal dict with potential date fields

    Returns:
        datetime or None
    """
    # Try explicit date field
    date_str = signal.get('date') or signal.get('published') or signal.get('timestamp')
    if date_str:
        try:
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%Y-%m-%dT%H:%M:%S']:
                try:
                    return datetime.strptime(str(date_str)[:19], fmt)
                except ValueError:
                    continue
        except Exception:
            pass

    # Fall back to recency_days
    recency_days = signal.get('recency_days')
    if recency_days is not None:
        return datetime.now() - timedelta(days=int(recency_days))

    return None


# =============================================================================
# DEAL CONTEXT QUALITY
# =============================================================================

def compute_deal_context_quality(
    folder_path: str,
    account_name: str,
    files_read: Optional[List[str]] = None
) -> DealContextQuality:
    """
    Compute context quality for a deal analysis.

    Args:
        folder_path: Path to account folder
        account_name: Account name (for file pattern matching)
        files_read: Optional list of files that were read (for validation)

    Returns:
        DealContextQuality with all computed fields
    """
    warnings = []
    folder = Path(folder_path)

    if not folder.exists():
        return DealContextQuality(
            folder_path=folder_path,
            folder_last_modified=None,
            oldest_file_date=None,
            newest_file_date=None,
            days_since_update=None,
            total_files_found=0,
            required_files_present=0,
            required_files_total=len(EXPECTED_DEAL_FILES['required']),
            recommended_files_present=0,
            recommended_files_total=len(EXPECTED_DEAL_FILES['recommended']),
            transcripts_last_30_days=0,
            emails_present=False,
            named_stakeholders=0,
            stakeholder_roles_unknown=0,
            completeness_score=0,
            freshness_status='COLD',
            warnings=['Folder does not exist']
        )

    # Get all files recursively
    all_files = list(folder.rglob('*'))
    all_files = [f for f in all_files if f.is_file()]

    # Compute file dates
    file_dates = []
    for f in all_files:
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            file_dates.append(mtime)
        except Exception:
            pass

    oldest_file_date = None
    newest_file_date = None
    days_since_update = None

    if file_dates:
        file_dates.sort()
        oldest_file_date = file_dates[0].isoformat()
        newest_file_date = file_dates[-1].isoformat()
        days_since_update = (datetime.now() - file_dates[-1]).days

    # Folder last modified (newest file)
    folder_last_modified = newest_file_date

    # Check required files
    required_present = 0
    for pattern in EXPECTED_DEAL_FILES['required']:
        # Replace {account} with actual name
        check_pattern = pattern.replace('{account}', account_name)
        if (folder / check_pattern).exists():
            required_present += 1
        else:
            # Try case-insensitive match
            matches = list(folder.glob(check_pattern.replace(account_name, '*')))
            if matches:
                required_present += 1

    # Check recommended files
    recommended_present = 0
    for pattern in EXPECTED_DEAL_FILES['recommended']:
        check_path = folder / pattern
        if check_path.exists():
            recommended_present += 1

    # Check conversations directory
    conversations_dir = folder / 'conversations'
    transcripts_recent = 0
    emails_present = False

    if conversations_dir.exists():
        for f in conversations_dir.iterdir():
            if f.is_file():
                if 'email' in f.name.lower():
                    emails_present = True

                # Check if file is recent (last 30 days)
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if (datetime.now() - mtime).days <= STALENESS_THRESHOLDS['transcript_recent']:
                        if 'call' in f.name.lower() or 'transcript' in f.name.lower() or 'summary' in f.name.lower():
                            transcripts_recent += 1
                except Exception:
                    pass

    # Count stakeholders (simple heuristic - look in people files)
    named_stakeholders = 0
    stakeholder_roles_unknown = 0

    people_files = list(folder.glob('*people*.md')) + list(folder.glob('*stakeholder*.md'))
    for pf in people_files:
        try:
            content = pf.read_text()
            # Count lines that look like person entries (contain @ or title keywords)
            for line in content.split('\n'):
                if '@' in line or any(kw in line.lower() for kw in ['vp', 'director', 'manager', 'head of', 'chief']):
                    named_stakeholders += 1
                if 'unknown' in line.lower() or 'tbd' in line.lower():
                    stakeholder_roles_unknown += 1
        except Exception:
            pass

    # Compute completeness score
    completeness_score = _compute_completeness_score(
        required_present=required_present,
        required_total=len(EXPECTED_DEAL_FILES['required']),
        recommended_present=recommended_present,
        recommended_total=len(EXPECTED_DEAL_FILES['recommended']),
        has_transcripts=transcripts_recent > 0,
        has_emails=emails_present,
        stakeholder_count=named_stakeholders
    )

    # Determine freshness status
    if days_since_update is None:
        freshness_status = 'COLD'
    elif days_since_update <= STALENESS_THRESHOLDS['deal_folder_stale']:
        freshness_status = 'CURRENT'
    elif days_since_update <= STALENESS_THRESHOLDS['deal_folder_cold']:
        freshness_status = 'STALE'
    else:
        freshness_status = 'COLD'

    # Generate warnings
    if freshness_status == 'COLD':
        warnings.append(f"Folder not updated in {days_since_update or 'unknown'} days - data may be outdated")
    elif freshness_status == 'STALE':
        warnings.append(f"Folder last updated {days_since_update} days ago")

    if transcripts_recent == 0:
        warnings.append("No recent call transcripts (last 30 days)")

    if not emails_present:
        warnings.append("No email history found")

    if named_stakeholders == 0:
        warnings.append("No stakeholders documented")

    if completeness_score < 50:
        warnings.append(f"Low completeness score ({completeness_score}%) - analysis may be limited")

    return DealContextQuality(
        folder_path=folder_path,
        folder_last_modified=folder_last_modified,
        oldest_file_date=oldest_file_date,
        newest_file_date=newest_file_date,
        days_since_update=days_since_update,
        total_files_found=len(all_files),
        required_files_present=required_present,
        required_files_total=len(EXPECTED_DEAL_FILES['required']),
        recommended_files_present=recommended_present,
        recommended_files_total=len(EXPECTED_DEAL_FILES['recommended']),
        transcripts_last_30_days=transcripts_recent,
        emails_present=emails_present,
        named_stakeholders=named_stakeholders,
        stakeholder_roles_unknown=stakeholder_roles_unknown,
        completeness_score=completeness_score,
        freshness_status=freshness_status,
        warnings=warnings
    )


def _compute_completeness_score(
    required_present: int,
    required_total: int,
    recommended_present: int,
    recommended_total: int,
    has_transcripts: bool,
    has_emails: bool,
    stakeholder_count: int
) -> int:
    """
    Compute completeness score (0-100).

    Weights:
    - Required files: 40%
    - Recommended files: 20%
    - Conversation coverage: 25% (transcripts + emails)
    - Stakeholder coverage: 15%
    """
    score = 0

    # Required files (40%)
    if required_total > 0:
        score += int(40 * (required_present / required_total))

    # Recommended files (20%)
    if recommended_total > 0:
        score += int(20 * (recommended_present / recommended_total))

    # Conversation coverage (25%)
    if has_transcripts:
        score += 15
    if has_emails:
        score += 10

    # Stakeholder coverage (15%)
    if stakeholder_count >= 3:
        score += 15
    elif stakeholder_count >= 1:
        score += int(15 * (stakeholder_count / 3))

    return min(100, score)


# =============================================================================
# COMPETITIVE INTEL AGE WARNINGS
# =============================================================================

def get_battle_card_age_warning(
    file_path: str,
    threshold_days: int = STALENESS_THRESHOLDS['battle_card']
) -> Tuple[Optional[str], Optional[str]]:
    """
    Check if a battle card file is stale and return warning if needed.

    Args:
        file_path: Path to battle card file
        threshold_days: Days after which to warn (default 180)

    Returns:
        Tuple of (last_updated_date, warning_message or None)
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return (None, f"Battle card not found: {file_path}")

        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        age_days = (datetime.now() - mtime).days
        last_updated = mtime.strftime('%Y-%m-%d')

        if age_days > threshold_days:
            return (
                last_updated,
                f"Battle card last updated {last_updated} ({age_days} days ago) - may be outdated"
            )

        return (last_updated, None)

    except Exception as e:
        logger.error(f"Error checking battle card age: {e}")
        return (None, f"Error checking file: {e}")


def check_all_battle_cards(
    intel_dir: str = None,
    threshold_days: int = STALENESS_THRESHOLDS['battle_card']
) -> Dict[str, Dict[str, Any]]:
    """
    Check all battle cards for staleness.

    Args:
        intel_dir: Path to intel/competitors directory
        threshold_days: Days after which to warn

    Returns:
        Dict mapping competitor name to {last_updated, warning, is_stale}
    """
    if intel_dir is None:
        # Default path (relative to prospecting module)
        intel_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'data', 'competitors'
        )

    results = {}
    intel_path = Path(intel_dir)

    if not intel_path.exists():
        return {'_error': {'warning': f'Intel directory not found: {intel_dir}'}}

    for card_file in intel_path.glob('competitor_*.md'):
        competitor = card_file.stem.replace('competitor_', '')
        last_updated, warning = get_battle_card_age_warning(str(card_file), threshold_days)

        results[competitor] = {
            'last_updated': last_updated,
            'warning': warning,
            'is_stale': warning is not None
        }

    return results


# =============================================================================
# FORMAT HEADERS
# =============================================================================

def format_prospect_context_header(quality: ProspectContextQuality) -> str:
    """
    Format context quality header for prospecting output.

    Returns both terminal-friendly and markdown-compatible format.
    """
    lines = []

    lines.append("=" * 60)
    lines.append("CONTEXT QUALITY")
    lines.append("=" * 60)

    # Confidence mode with visual indicator
    confidence_indicator = {
        'HIGH': '[====]',
        'MEDIUM': '[=== ]',
        'LOW': '[==  ]',
        'GENERIC': '[=   ]'
    }.get(quality.confidence_mode, '[    ]')

    lines.append(f"Confidence: {quality.confidence_mode} {confidence_indicator}")
    lines.append("")

    # Signal counts
    lines.append("Signals:")
    lines.append(f"  Cited (verifiable):    {quality.cited_signal_count}")
    lines.append(f"  Vendor data:           {quality.vendor_signal_count}")
    lines.append(f"  Inferred:              {quality.inferred_signal_count}")
    lines.append(f"  Total:                 {quality.total_signal_count}")
    lines.append("")

    # Signal dates
    if quality.oldest_signal_date:
        lines.append("Signal Freshness:")
        lines.append(f"  Oldest: {quality.oldest_signal_date}")
        lines.append(f"  Newest: {quality.newest_signal_date}")
        if quality.signal_age_days is not None:
            lines.append(f"  Age:    {quality.signal_age_days} days")
    else:
        lines.append("Signal Freshness: No dated signals")
    lines.append("")

    # Research sources
    lines.append("Research Sources:")
    lines.append(f"  ZoomInfo:              {'Yes' if quality.zoominfo_used else 'No'}")
    lines.append(f"  Perplexity:            {'Yes' if quality.perplexity_used else 'No'}")
    lines.append(f"  Perplexity citations:  {'Yes' if quality.perplexity_has_citations else 'No'}")
    lines.append(f"  WebFetch:              {'Yes' if quality.webfetch_used else 'No'}")
    lines.append(f"  User-provided context: {'Yes' if quality.user_context_provided else 'No'}")
    lines.append("")

    # Warnings
    if quality.warnings:
        lines.append("Warnings:")
        for warning in quality.warnings:
            lines.append(f"  ! {warning}")
        lines.append("")

    lines.append("=" * 60)

    return '\n'.join(lines)


def format_deal_context_header(quality: DealContextQuality) -> str:
    """
    Format context quality header for deal analysis output.
    """
    lines = []

    lines.append("=" * 60)
    lines.append("CONTEXT QUALITY - Deal Analysis")
    lines.append("=" * 60)

    # Freshness status with visual indicator
    freshness_indicator = {
        'CURRENT': '[CURRENT]',
        'STALE': '[STALE]  ',
        'COLD': '[COLD]   '
    }.get(quality.freshness_status, '[??????]')

    lines.append(f"Freshness: {freshness_indicator}")
    lines.append("")

    # Folder dates
    lines.append("Folder Activity:")
    lines.append(f"  Last modified: {quality.folder_last_modified or 'Unknown'}")
    lines.append(f"  Oldest file:   {quality.oldest_file_date or 'Unknown'}")
    lines.append(f"  Newest file:   {quality.newest_file_date or 'Unknown'}")
    if quality.days_since_update is not None:
        lines.append(f"  Days since update: {quality.days_since_update}")
    lines.append("")

    # Completeness
    completeness_bar = _render_progress_bar(quality.completeness_score)
    lines.append(f"Completeness: {completeness_bar} {quality.completeness_score}%")
    lines.append("")

    # File coverage
    lines.append("File Coverage:")
    lines.append(f"  Required files:    {quality.required_files_present}/{quality.required_files_total}")
    lines.append(f"  Recommended files: {quality.recommended_files_present}/{quality.recommended_files_total}")
    lines.append(f"  Total files:       {quality.total_files_found}")
    lines.append("")

    # Conversation coverage
    lines.append("Conversation Coverage:")
    lines.append(f"  Transcripts (last 30 days): {quality.transcripts_last_30_days}")
    lines.append(f"  Email history:              {'Present' if quality.emails_present else 'Missing'}")
    lines.append("")

    # Stakeholder coverage
    lines.append("Stakeholder Coverage:")
    lines.append(f"  Named stakeholders: {quality.named_stakeholders}")
    if quality.stakeholder_roles_unknown > 0:
        lines.append(f"  Roles unknown:      {quality.stakeholder_roles_unknown}")
    lines.append("")

    # Warnings
    if quality.warnings:
        lines.append("Warnings:")
        for warning in quality.warnings:
            lines.append(f"  ! {warning}")
        lines.append("")

    lines.append("=" * 60)

    return '\n'.join(lines)


def _render_progress_bar(percentage: int, width: int = 10) -> str:
    """Render a text progress bar."""
    filled = int(width * percentage / 100)
    empty = width - filled
    return f"[{'=' * filled}{' ' * empty}]"


# =============================================================================
# JSON ARTIFACT WRITERS
# =============================================================================

def write_prospect_context_quality_artifact(
    quality: ProspectContextQuality,
    output_dir: str
) -> str:
    """
    Write context quality to JSON artifact.

    Args:
        quality: ProspectContextQuality dataclass
        output_dir: Directory to write to

    Returns:
        Path to written file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    artifact_path = output_path / 'context_quality.json'

    data = {
        'type': 'prospect_context_quality',
        'generated_at': datetime.now().isoformat(),
        **quality.to_dict()
    }

    with open(artifact_path, 'w') as f:
        json.dump(data, f, indent=2)

    logger.info(f"Wrote context quality artifact to {artifact_path}")
    return str(artifact_path)


def write_deal_context_quality_artifact(
    quality: DealContextQuality,
    output_dir: str
) -> str:
    """
    Write deal context quality to JSON artifact.

    Args:
        quality: DealContextQuality dataclass
        output_dir: Directory to write to

    Returns:
        Path to written file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    artifact_path = output_path / 'deal_context_quality.json'

    data = {
        'type': 'deal_context_quality',
        'generated_at': datetime.now().isoformat(),
        **quality.to_dict()
    }

    with open(artifact_path, 'w') as f:
        json.dump(data, f, indent=2)

    logger.info(f"Wrote deal context quality artifact to {artifact_path}")
    return str(artifact_path)


# =============================================================================
# MARKDOWN FORMATTERS (for saved deliverables)
# =============================================================================

def format_prospect_context_header_markdown(quality: ProspectContextQuality) -> str:
    """
    Format context quality header as markdown for saved files.
    """
    lines = []

    lines.append("## Context Quality")
    lines.append("")
    lines.append(f"**Confidence Mode:** {quality.confidence_mode}")
    lines.append("")
    lines.append("### Signal Summary")
    lines.append(f"| Type | Count |")
    lines.append(f"|------|-------|")
    lines.append(f"| Cited (verifiable) | {quality.cited_signal_count} |")
    lines.append(f"| Vendor data | {quality.vendor_signal_count} |")
    lines.append(f"| Inferred | {quality.inferred_signal_count} |")
    lines.append(f"| **Total** | {quality.total_signal_count} |")
    lines.append("")

    if quality.oldest_signal_date:
        lines.append("### Signal Freshness")
        lines.append(f"- Oldest signal: {quality.oldest_signal_date}")
        lines.append(f"- Newest signal: {quality.newest_signal_date}")
        if quality.signal_age_days:
            lines.append(f"- Signal age: {quality.signal_age_days} days")
        lines.append("")

    lines.append("### Research Sources")
    sources = []
    if quality.zoominfo_used:
        sources.append("ZoomInfo")
    if quality.perplexity_used:
        sources.append("Perplexity" + (" (with citations)" if quality.perplexity_has_citations else ""))
    if quality.webfetch_used:
        sources.append("WebFetch")
    if quality.user_context_provided:
        sources.append("User-provided context")

    lines.append(f"- Sources used: {', '.join(sources) if sources else 'None'}")
    lines.append("")

    if quality.warnings:
        lines.append("### Warnings")
        for warning in quality.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    lines.append("---")
    lines.append("")

    return '\n'.join(lines)


def format_deal_context_header_markdown(quality: DealContextQuality) -> str:
    """
    Format deal context quality header as markdown.
    """
    lines = []

    lines.append("## Context Quality - Deal Analysis")
    lines.append("")
    lines.append(f"**Freshness:** {quality.freshness_status}")
    lines.append(f"**Completeness:** {quality.completeness_score}%")
    lines.append("")

    lines.append("### Folder Activity")
    lines.append(f"- Last modified: {quality.folder_last_modified or 'Unknown'}")
    lines.append(f"- Days since update: {quality.days_since_update or 'Unknown'}")
    lines.append("")

    lines.append("### Coverage")
    lines.append(f"| Category | Status |")
    lines.append(f"|----------|--------|")
    lines.append(f"| Required files | {quality.required_files_present}/{quality.required_files_total} |")
    lines.append(f"| Recent transcripts | {quality.transcripts_last_30_days} |")
    lines.append(f"| Email history | {'Present' if quality.emails_present else 'Missing'} |")
    lines.append(f"| Named stakeholders | {quality.named_stakeholders} |")
    lines.append("")

    if quality.warnings:
        lines.append("### Warnings")
        for warning in quality.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    lines.append("---")
    lines.append("")

    return '\n'.join(lines)


# =============================================================================
# CANONICAL CONTEXT QUALITY SCHEMA (Phase 1)
# =============================================================================

import uuid

# Warning codes
WARNING_OLD_SIGNALS = "OLD_SIGNALS_PRESENT"
WARNING_COMPANY_INTEL_STALE = "COMPANY_INTEL_STALE"
WARNING_NO_CITED_SIGNALS = "NO_CITED_SIGNALS"
WARNING_VENDOR_ONLY = "VENDOR_DATA_ONLY"
WARNING_REVIEW_REQUIRED = "REVIEW_REQUIRED"
WARNING_THIN_RESEARCH = "THIN_RESEARCH"


class ContextQualityBuilder:
    """
    Builder for canonical context_quality.json schema.

    Produces the authoritative schema that all consumers rely on:
    - /prospect CLI output
    - Saved deliverables
    - Orchestrator dashboards
    """

    # Threshold for old signals warning (days)
    OLD_SIGNAL_THRESHOLD_DAYS = 365

    def __init__(self):
        self._data = {}

    def build(
        self,
        research_data: Dict[str, Any],
        prospect_brief: Dict[str, Any],
        company_intel: Optional[Dict[str, Any]] = None,
        persona_result: Optional[Dict[str, Any]] = None,
        confidence_result: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
        artifact_paths: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Build the canonical context_quality.json structure.

        Args:
            research_data: Raw research from orchestrator
            prospect_brief: Processed brief from relevance_engine
            company_intel: Company intel result (if available)
            persona_result: Persona detection diagnostics (if available)
            confidence_result: Confidence assessment (if available)
            run_id: Optional run identifier
            artifact_paths: Paths to generated artifacts

        Returns:
            Dict matching canonical schema
        """
        now = datetime.now()

        # Build each section
        result = {
            "generated_at": now.isoformat(),
            "run_id": run_id or str(uuid.uuid4())[:8],
            "company": self._build_company_section(research_data, prospect_brief, company_intel),
            "contact": self._build_contact_section(research_data, prospect_brief, persona_result),
            "mode": self._build_mode_section(prospect_brief, confidence_result),
            "sources": self._build_sources_section(research_data, company_intel),
            "signals": self._build_signals_section(prospect_brief, company_intel),
            "artifacts": artifact_paths or {}
        }

        return result

    def _build_company_section(
        self,
        research_data: Dict[str, Any],
        prospect_brief: Dict[str, Any],
        company_intel: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build company section of schema."""
        # Safely get nested dicts (handles None values)
        research_data = _safe_dict(research_data)
        prospect_brief = _safe_dict(prospect_brief)
        company_intel = _safe_dict(company_intel)
        company_data = _safe_dict(research_data.get("company"))

        # Try to get company info from various sources
        company_name = (
            prospect_brief.get("company_name") or
            research_data.get("company_name") or
            company_data.get("name", "")
        )

        primary_account_id = None
        site_account_id = None
        domain = None

        if company_intel:
            primary_account_id = company_intel.get("primary_account_id")
            aliases = _safe_dict(company_intel.get("aliases"))
            domains = aliases.get("domains")
            if domains:
                domain = domains[0] if isinstance(domains, list) else domains

        # Try to get domain from research
        if not domain:
            domain = company_data.get("website") or company_data.get("domain")

        return {
            "name": company_name,
            "primary_account_id": primary_account_id,
            "site_account_id": site_account_id,
            "domain": domain
        }

    def _build_contact_section(
        self,
        research_data: Dict[str, Any],
        prospect_brief: Dict[str, Any],
        persona_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build contact section of schema."""
        # Safely get nested dicts (handles None values)
        research_data = _safe_dict(research_data)
        prospect_brief = _safe_dict(prospect_brief)
        persona_result = _safe_dict(persona_result)
        contact_data = _safe_dict(research_data.get("contact"))

        # Get persona info
        persona = prospect_brief.get("persona", "unknown")

        # Determine persona confidence
        persona_confidence = "medium"
        ambiguity_detected = False
        review_required = False
        review_reasons = []

        if persona_result:
            ambiguity_detected = persona_result.get("ambiguity_detected", False)
            if ambiguity_detected:
                persona_confidence = "low"
                review_reasons.append("Multiple personas detected for title")

            if persona_result.get("confidence_downgrade"):
                review_required = True
                review_reasons.append("Persona requires manual review")

            if persona_result.get("safe_angle_only"):
                review_reasons.append("Limited to safe angles only")

        # Check for manual review flags in prospect_brief
        if prospect_brief.get("review_required") or prospect_brief.get("manual_review"):
            review_required = True
            if prospect_brief.get("review_reason"):
                review_reasons.append(prospect_brief["review_reason"])

        if not ambiguity_detected and persona != "unknown":
            persona_confidence = "high"

        return {
            "name": contact_data.get("name") or prospect_brief.get("contact_name", ""),
            "title": contact_data.get("title") or contact_data.get("job_title", ""),
            "persona": persona,
            "persona_confidence": persona_confidence,
            "ambiguity_detected": ambiguity_detected,
            "review_required": review_required,
            "review_reasons": review_reasons
        }

    def _build_mode_section(
        self,
        prospect_brief: Dict[str, Any],
        confidence_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build mode section of schema."""
        # Safely handle None values
        prospect_brief = _safe_dict(prospect_brief)
        confidence_result = _safe_dict(confidence_result)

        # Get confidence tier
        confidence_mode = prospect_brief.get("confidence_tier", "GENERIC").upper()

        # Get tier (A/B)
        tier = prospect_brief.get("tier", "B").upper()

        # Collect confidence notes
        confidence_notes = []

        if confidence_result:
            notes = confidence_result.get("notes")
            if notes:
                confidence_notes.extend(_safe_list(notes))

        # Add notes based on brief status
        status = prospect_brief.get("status", "")
        if status == "needs_more_research":
            confidence_notes.append("Insufficient signals for confident outreach")
        elif status == "generic_only":
            confidence_notes.append("Using generic messaging due to low context")

        return {
            "tier": tier,
            "confidence_mode": confidence_mode,
            "confidence_notes": confidence_notes
        }

    def _build_sources_section(
        self,
        research_data: Dict[str, Any],
        company_intel: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build sources section of schema."""
        # Safely get nested dicts (handles None values)
        research_data = _safe_dict(research_data)
        sources = {}

        # ZoomInfo source
        zoominfo_data = _safe_dict(research_data.get("zoominfo")) or _safe_dict(research_data.get("contact"))
        sources["zoominfo"] = self._build_zoominfo_source(zoominfo_data, research_data)

        # Perplexity source
        perplexity_data = _safe_dict(research_data.get("perplexity"))
        sources["perplexity"] = self._build_perplexity_source(perplexity_data)

        # WebFetch source
        webfetch_data = _safe_dict(research_data.get("webfetch"))
        sources["webfetch"] = self._build_webfetch_source(webfetch_data)

        # Company Intel source
        sources["company_intel"] = self._build_company_intel_source(company_intel)

        return sources

    def _build_zoominfo_source(
        self,
        zoominfo_data: Dict[str, Any],
        research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build ZoomInfo source entry."""
        # Safely handle None values
        zoominfo_data = _safe_dict(zoominfo_data)
        research_data = _safe_dict(research_data)

        ran = bool(zoominfo_data)
        found_contact = bool(zoominfo_data.get("name") or zoominfo_data.get("id"))

        # Check for email/phone
        found_email = bool(zoominfo_data.get("email"))
        found_phone = bool(zoominfo_data.get("phone") or zoominfo_data.get("directPhone"))

        errors_dict = _safe_dict(research_data.get("errors"))
        errors = _safe_list(errors_dict.get("zoominfo"))
        if isinstance(errors, str):
            errors = [errors] if errors else []

        status = "ok" if ran and not errors else ("error" if errors else "skipped")

        return {
            "ran": ran,
            "status": status,
            "found_contact": found_contact,
            "found_email": found_email,
            "found_phone": found_phone,
            "errors": errors
        }

    def _build_perplexity_source(self, perplexity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build Perplexity source entry."""
        # Safely handle None values
        perplexity_data = _safe_dict(perplexity_data)

        ran = bool(perplexity_data)

        # Count citations
        citations = _safe_list(perplexity_data.get("citations"))
        citations_count = len(citations)

        # Count cited claims
        cited_claims = _safe_list(perplexity_data.get("cited_claims"))
        cited_claims_count = len(cited_claims)

        errors = _safe_list(perplexity_data.get("errors"))
        if isinstance(errors, str):
            errors = [errors] if errors else []

        status = "ok" if ran and not errors else ("error" if errors else "skipped")

        return {
            "ran": ran,
            "status": status,
            "citations_count": citations_count,
            "cited_claims_count": cited_claims_count,
            "errors": errors
        }

    def _build_webfetch_source(self, webfetch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build WebFetch source entry."""
        # Safely handle None values
        webfetch_data = _safe_dict(webfetch_data)

        ran = bool(webfetch_data)

        # Count pages fetched
        pages = _safe_list(webfetch_data.get("pages"))
        pages_fetched = len(pages) if pages else (1 if webfetch_data.get("content") else 0)

        errors = _safe_list(webfetch_data.get("errors"))
        if isinstance(errors, str):
            errors = [errors] if errors else []

        status = "ok" if ran and not errors else ("error" if errors else "skipped")

        return {
            "ran": ran,
            "status": status,
            "pages_fetched": pages_fetched,
            "errors": errors
        }

    def _build_company_intel_source(
        self,
        company_intel: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build company intel source entry."""
        # Safely handle None values
        company_intel = _safe_dict(company_intel)

        if not company_intel:
            return {
                "ran": False,
                "status": "skipped",
                "cache_hit": False,
                "last_refreshed_at": None,
                "providers": {},
                "errors": []
            }

        # Determine overall status
        sources = _safe_dict(company_intel.get("sources"))
        errors = _safe_list(company_intel.get("errors"))

        # Check cache hit (if last_refreshed matches session start, it's fresh)
        last_refreshed = company_intel.get("last_refreshed")
        cache_hit = company_intel.get("_cache_hit", True)  # Default to True if not specified

        # Determine status
        all_stale = True
        any_error = bool(errors)

        providers_section = {}
        for provider_name, provider_status in sources.items():
            if isinstance(provider_status, dict):
                prov_status = provider_status.get("status", "ok")
                if prov_status == "success" or prov_status == "ok":
                    all_stale = False

                # Build provider entry
                providers_section[provider_name] = self._build_provider_entry(
                    provider_name, provider_status, company_intel
                )

        overall_status = "error" if any_error else ("stale" if all_stale else "ok")

        return {
            "ran": True,
            "status": overall_status,
            "cache_hit": cache_hit,
            "last_refreshed_at": last_refreshed,
            "providers": providers_section,
            "errors": errors if isinstance(errors, list) else [errors] if errors else []
        }

    def _build_provider_entry(
        self,
        provider_name: str,
        provider_status: Dict[str, Any],
        company_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build individual provider entry."""
        # Safely handle None values
        provider_status = _safe_dict(provider_status)
        company_intel = _safe_dict(company_intel)

        status = provider_status.get("status", "ok")
        if status == "success":
            status = "ok"

        last_run = provider_status.get("last_run")
        expires_at = provider_status.get("expires_at")

        # Count signals from this provider
        signals_public = 0
        signals_vendor = 0
        newest_date = None
        oldest_date = None

        all_signals = _safe_dict(company_intel.get("signals"))

        # Count public_url signals from this provider
        for signal in _safe_list(all_signals.get("public_url")):
            if isinstance(signal, dict):
                if signal.get("provider") == provider_name or signal.get("_provider") == provider_name:
                    signals_public += 1
                    as_of = signal.get("as_of_date")
                    if as_of:
                        if not oldest_date or as_of < oldest_date:
                            oldest_date = as_of
                        if not newest_date or as_of > newest_date:
                            newest_date = as_of

        # Count vendor_data signals
        for signal in _safe_list(all_signals.get("vendor_data")):
            if isinstance(signal, dict):
                if signal.get("provider") == provider_name or signal.get("_provider") == provider_name:
                    signals_vendor += 1

        # Check for stale status
        is_stale = False
        if expires_at:
            try:
                expires = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                if datetime.now(expires.tzinfo) > expires:
                    is_stale = True
                    status = "stale"
            except (ValueError, TypeError):
                pass

        return {
            "ran": True,
            "status": status,
            "cache_hit": True,  # If we have data, it was either cached or just fetched
            "last_refreshed_at": last_run,
            "expires_at": expires_at,
            "signals_public_url_count": signals_public,
            "signals_vendor_data_count": signals_vendor,
            "newest_as_of_date": newest_date,
            "oldest_as_of_date": oldest_date,
            "errors": _safe_list(provider_status.get("errors"))
        }

    def _build_signals_section(
        self,
        prospect_brief: Dict[str, Any],
        company_intel: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build signals section of schema."""
        # Safely handle None values
        prospect_brief = _safe_dict(prospect_brief)
        company_intel = _safe_dict(company_intel)

        # Get all signals from prospect_brief
        all_signals = _safe_list(
            prospect_brief.get("cited_signals") or prospect_brief.get("verified_signals")
        )

        # Initialize counters
        company_cited = 0
        company_vendor = 0
        person_cited = 0
        person_vendor = 0

        cited_dates = []

        for signal in all_signals:
            if not isinstance(signal, dict):
                continue

            source_type = signal.get("source_type", "inferred")
            scope = signal.get("scope", "person_level")
            origin = signal.get("_origin", "")

            # Determine if company-level
            is_company = (
                scope == "company_level" or
                scope == "company_specific" or
                origin == "company_intel"
            )

            # Determine if cited
            is_cited = source_type in ("public_url", "user_provided")

            # Count
            if is_company:
                if is_cited:
                    company_cited += 1
                else:
                    company_vendor += 1
            else:
                if is_cited:
                    person_cited += 1
                else:
                    person_vendor += 1

            # Track dates for cited signals
            if is_cited:
                signal_date = _extract_signal_date(signal)
                if signal_date:
                    cited_dates.append(signal_date)

        # Add company intel signals not in prospect_brief
        if company_intel:
            intel_signals = _safe_dict(company_intel.get("signals"))
            for signal in _safe_list(intel_signals.get("public_url")):
                if isinstance(signal, dict):
                    # Don't double-count if already in all_signals
                    signal_id = signal.get("signal_id")
                    if signal_id and not any(s.get("signal_id") == signal_id for s in all_signals):
                        company_cited += 1
                        as_of = signal.get("as_of_date")
                        if as_of:
                            try:
                                cited_dates.append(datetime.strptime(as_of, "%Y-%m-%d"))
                            except ValueError:
                                pass

        # Calculate freshness
        newest_cited_date = None
        oldest_cited_date = None
        newest_age = None
        oldest_age = None

        if cited_dates:
            cited_dates.sort()
            oldest_cited_date = cited_dates[0].strftime("%Y-%m-%d")
            newest_cited_date = cited_dates[-1].strftime("%Y-%m-%d")
            oldest_age = (datetime.now() - cited_dates[0]).days
            newest_age = (datetime.now() - cited_dates[-1]).days

        # Generate warnings
        warnings = self._generate_signal_warnings(
            company_cited=company_cited,
            company_vendor=company_vendor,
            person_cited=person_cited,
            person_vendor=person_vendor,
            oldest_age=oldest_age,
            company_intel=company_intel
        )

        return {
            "counts": {
                "company_cited": company_cited,
                "company_vendor": company_vendor,
                "person_cited": person_cited,
                "person_vendor": person_vendor,
                "total_cited": company_cited + person_cited,
                "total_vendor": company_vendor + person_vendor
            },
            "freshness": {
                "newest_cited_date": newest_cited_date,
                "oldest_cited_date": oldest_cited_date,
                "newest_cited_age_days": newest_age,
                "oldest_cited_age_days": oldest_age
            },
            "warnings": warnings
        }

    def _generate_signal_warnings(
        self,
        company_cited: int,
        company_vendor: int,
        person_cited: int,
        person_vendor: int,
        oldest_age: Optional[int],
        company_intel: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate warnings based on signal analysis."""
        warnings = []

        total_cited = company_cited + person_cited
        total_vendor = company_vendor + person_vendor

        # Warning: Old signals present
        if oldest_age and oldest_age > self.OLD_SIGNAL_THRESHOLD_DAYS:
            warnings.append(f"{WARNING_OLD_SIGNALS}: oldest cited signal is {oldest_age} days old")

        # Warning: No cited signals
        if total_cited == 0:
            if total_vendor > 0:
                warnings.append(f"{WARNING_VENDOR_ONLY}: only vendor data available, cannot cite sources")
            else:
                warnings.append(f"{WARNING_NO_CITED_SIGNALS}: no verifiable signals found")

        # Warning: Company intel stale
        if company_intel:
            sources = _safe_dict(company_intel.get("sources"))
            for provider_name, provider_status in sources.items():
                if isinstance(provider_status, dict):
                    expires_at = provider_status.get("expires_at")
                    if expires_at:
                        try:
                            expires = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                            if datetime.now(expires.tzinfo) > expires:
                                warnings.append(f"{WARNING_COMPANY_INTEL_STALE}: {provider_name} data expired")
                        except (ValueError, TypeError):
                            pass

        # Warning: Thin research (few signals with old data)
        if total_cited > 0 and total_cited < 3 and oldest_age and oldest_age > 90:
            warnings.append(f"{WARNING_THIN_RESEARCH}: few signals and oldest is {oldest_age} days old")

        return warnings


def render_context_quality_header(context_quality: Dict[str, Any]) -> str:
    """
    Render compact, human-readable context quality header.

    Used in:
    - /prospect CLI output
    - email.md / inmail.md headers
    - sequence.md headers
    - orchestrator dashboard rows

    Args:
        context_quality: Dict from ContextQualityBuilder.build()

    Returns:
        Formatted header string
    """
    # Safely handle None values
    context_quality = _safe_dict(context_quality)

    lines = []
    lines.append("Context Quality")

    # Confidence
    mode = _safe_dict(context_quality.get("mode"))
    confidence = mode.get("confidence_mode", "UNKNOWN")
    lines.append(f"- Confidence: {confidence}")

    # Signal counts
    signals = _safe_dict(context_quality.get("signals"))
    counts = _safe_dict(signals.get("counts"))

    total_cited = counts.get("total_cited", 0)
    company_cited = counts.get("company_cited", 0)
    person_cited = counts.get("person_cited", 0)
    total_vendor = counts.get("total_vendor", 0)

    lines.append(f"- Cited signals: {total_cited} (company {company_cited}, person {person_cited})")
    lines.append(f"- Vendor signals: {total_vendor}")

    # Freshness
    freshness = _safe_dict(signals.get("freshness"))
    newest_date = freshness.get("newest_cited_date")
    oldest_date = freshness.get("oldest_cited_date")
    newest_age = freshness.get("newest_cited_age_days")
    oldest_age = freshness.get("oldest_cited_age_days")

    if newest_date:
        lines.append(f"- Newest cited: {newest_date} ({newest_age}d)")
    if oldest_date:
        lines.append(f"- Oldest cited: {oldest_date} ({oldest_age}d)")

    # Company intel status
    sources = _safe_dict(context_quality.get("sources"))
    company_intel = _safe_dict(sources.get("company_intel"))

    if company_intel.get("ran"):
        providers = _safe_dict(company_intel.get("providers"))
        provider_statuses = []
        for prov_name, prov_data in providers.items():
            prov_data = _safe_dict(prov_data)
            status = prov_data.get("status", "unknown")
            cache_note = "cached" if prov_data.get("cache_hit") else "fresh"

            # Calculate cache age
            last_refreshed = prov_data.get("last_refreshed_at")
            if last_refreshed:
                try:
                    refreshed_dt = datetime.fromisoformat(last_refreshed.replace('Z', '+00:00'))
                    age_days = (datetime.now(refreshed_dt.tzinfo) - refreshed_dt).days
                    cache_note = f"cached {age_days}d ago" if age_days > 0 else "fresh"
                except (ValueError, TypeError):
                    pass

            status_icon = "ok" if status == "ok" else status
            provider_statuses.append(f"{prov_name.upper()} {status_icon} ({cache_note})")

        if provider_statuses:
            lines.append(f"- Company intel: {', '.join(provider_statuses)}")

    # Other sources
    source_items = []

    zoominfo = _safe_dict(sources.get("zoominfo"))
    if zoominfo.get("ran"):
        icon = "✓" if zoominfo.get("status") == "ok" else "✗"
        source_items.append(f"ZoomInfo {icon}")

    perplexity = _safe_dict(sources.get("perplexity"))
    if perplexity.get("ran"):
        icon = "✓" if perplexity.get("status") == "ok" else "✗"
        citations = perplexity.get("citations_count", 0)
        source_items.append(f"Perplexity {icon} ({citations} citations)")

    webfetch = _safe_dict(sources.get("webfetch"))
    if webfetch.get("ran"):
        icon = "✓" if webfetch.get("status") == "ok" else "✗"
        source_items.append(f"WebFetch {icon}")

    if source_items:
        lines.append(f"- Sources: {', '.join(source_items)}")

    # Warnings
    warnings = _safe_list(signals.get("warnings"))
    for warning in warnings:
        # Extract warning code for display
        if ":" in warning:
            code = warning.split(":")[0]
            lines.append(f"⚠ {code}")
        else:
            lines.append(f"⚠ {warning}")

    # Review required
    contact = _safe_dict(context_quality.get("contact"))
    if contact.get("review_required"):
        lines.append(f"⚠ {WARNING_REVIEW_REQUIRED}")

    return "\n".join(lines)


def render_context_quality_header_markdown(context_quality: Dict[str, Any]) -> str:
    """
    Render context quality header as markdown for saved deliverables.

    Args:
        context_quality: Dict from ContextQualityBuilder.build()

    Returns:
        Markdown formatted header
    """
    # Safely handle None values
    context_quality = _safe_dict(context_quality)

    lines = []
    lines.append("## Context Quality")
    lines.append("")

    # Mode section
    mode = _safe_dict(context_quality.get("mode"))
    lines.append(f"**Confidence:** {mode.get('confidence_mode', 'UNKNOWN')} | **Tier:** {mode.get('tier', 'B')}")
    lines.append("")

    # Signals table
    signals = _safe_dict(context_quality.get("signals"))
    counts = _safe_dict(signals.get("counts"))

    lines.append("### Signals")
    lines.append("| Type | Company | Person | Total |")
    lines.append("|------|---------|--------|-------|")
    lines.append(f"| Cited | {counts.get('company_cited', 0)} | {counts.get('person_cited', 0)} | {counts.get('total_cited', 0)} |")
    lines.append(f"| Vendor | {counts.get('company_vendor', 0)} | {counts.get('person_vendor', 0)} | {counts.get('total_vendor', 0)} |")
    lines.append("")

    # Freshness
    freshness = _safe_dict(signals.get("freshness"))
    if freshness.get("newest_cited_date"):
        lines.append("### Freshness")
        lines.append(f"- **Newest cited:** {freshness.get('newest_cited_date')} ({freshness.get('newest_cited_age_days')} days ago)")
        lines.append(f"- **Oldest cited:** {freshness.get('oldest_cited_date')} ({freshness.get('oldest_cited_age_days')} days ago)")
        lines.append("")

    # Sources table
    sources = _safe_dict(context_quality.get("sources"))
    lines.append("### Sources")
    lines.append("| Source | Status | Details |")
    lines.append("|--------|--------|---------|")

    zoominfo = _safe_dict(sources.get("zoominfo"))
    if zoominfo.get("ran"):
        details = []
        if zoominfo.get("found_contact"):
            details.append("contact found")
        if zoominfo.get("found_email"):
            details.append("email")
        if zoominfo.get("found_phone"):
            details.append("phone")
        lines.append(f"| ZoomInfo | {zoominfo.get('status', 'unknown')} | {', '.join(details) if details else '-'} |")

    perplexity = _safe_dict(sources.get("perplexity"))
    if perplexity.get("ran"):
        lines.append(f"| Perplexity | {perplexity.get('status', 'unknown')} | {perplexity.get('citations_count', 0)} citations, {perplexity.get('cited_claims_count', 0)} claims |")

    webfetch = _safe_dict(sources.get("webfetch"))
    if webfetch.get("ran"):
        lines.append(f"| WebFetch | {webfetch.get('status', 'unknown')} | {webfetch.get('pages_fetched', 0)} pages |")

    company_intel = _safe_dict(sources.get("company_intel"))
    if company_intel.get("ran"):
        providers = _safe_dict(company_intel.get("providers"))
        for prov_name, prov_data in providers.items():
            prov_data = _safe_dict(prov_data)
            cache_status = "cached" if prov_data.get("cache_hit") else "fresh"
            signals_count = prov_data.get("signals_public_url_count", 0)
            lines.append(f"| {prov_name.upper()} | {prov_data.get('status', 'unknown')} ({cache_status}) | {signals_count} signals |")

    lines.append("")

    # Warnings
    warnings = _safe_list(signals.get("warnings"))
    contact = _safe_dict(context_quality.get("contact"))

    if warnings or contact.get("review_required"):
        lines.append("### Warnings")
        for warning in warnings:
            lines.append(f"- ⚠️ {warning}")
        if contact.get("review_required"):
            reasons = _safe_list(contact.get("review_reasons"))
            lines.append(f"- ⚠️ **Review Required**: {', '.join(reasons) if reasons else 'Manual review needed'}")
        lines.append("")

    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def write_context_quality_artifacts(
    context_quality: Dict[str, Any],
    output_dir: str
) -> Dict[str, str]:
    """
    Write context_quality.json and context_quality.md to output directory.

    Args:
        context_quality: Dict from ContextQualityBuilder.build()
        output_dir: Directory to write artifacts

    Returns:
        Dict with paths to written files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    paths = {}

    # Write JSON
    json_path = output_path / "context_quality.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(context_quality, f, indent=2, ensure_ascii=False)
    paths["json"] = str(json_path)
    logger.info(f"Wrote context_quality.json to {json_path}")

    # Write Markdown
    md_content = render_context_quality_header_markdown(context_quality)
    md_path = output_path / "context_quality.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    paths["md"] = str(md_path)
    logger.info(f"Wrote context_quality.md to {md_path}")

    return paths
