"""
Outbound Orchestrator - Control plane for batch prospect email generation

This module orchestrates the selection of accounts from a ranked list and
generates draft emails by calling the existing /prospect pipeline.

It is a CONTROL PLANE only:
- Select accounts (no new scoring logic)
- Execute prospect pipeline
- Verify artifacts meet quality gates
- Summarize results in dashboard

Usage:
    from outbound_orchestrator import OutboundOrchestrator, OutboundConfig

    config = OutboundConfig(
        accounts_path=Path("accounts.csv"),
        top_n=10,
        max_drafts_per_account=3,
        max_total_drafts=20
    )

    orchestrator = OutboundOrchestrator(config)
    result = orchestrator.run()
"""

import os
import sys
import csv
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .path_resolver import (
    get_prospecting_root,
    get_company_folder,
    get_drafts_folder,
    ensure_folders_exist,
    sanitize_name,
    get_context_quality_json_path,
    get_context_quality_md_path
)
from .context_quality import (
    ContextQualityBuilder,
    render_context_quality_header,
    render_context_quality_header_markdown,
    write_context_quality_artifacts
)
from .promotion_rules import (
    PromotionGate,
    BatchRenderGate,
    ProspectState
)

logger = logging.getLogger(__name__)


# =============================================================================
# COLUMN ALIAS MAPPINGS (Salesforce export compatibility)
# =============================================================================

COLUMN_ALIASES = {
    "company_name": ["company_name", "company", "acct name", "account_name"],
    "score": ["score", "rank", "priority_score"],
    "tier": ["tier", "priority_tier"],
    "account_id": ["account_id", "acct id", "primary_account_id", "sf_id"],
    "domain": ["domain", "website"],
    "tags": ["signal_tags", "tags"],
}


def _resolve_column(data: Dict[str, Any], field: str) -> Tuple[Optional[Any], Optional[str]]:
    """
    Resolve a field value from data using column aliases.

    Returns:
        (value, matched_column_name) or (None, None) if not found
    """
    aliases = COLUMN_ALIASES.get(field, [field])
    for alias in aliases:
        if alias in data and data[alias]:
            return data[alias], alias
    return None, None


def _normalize_tier(tier_val: Optional[str]) -> str:
    """Normalize tier values to A/B format."""
    if not tier_val:
        return "A"
    tier_lower = str(tier_val).lower()
    if "tier 1" in tier_lower or "hot" in tier_lower:
        return "A"
    elif "tier 2" in tier_lower or "warm" in tier_lower:
        return "B"
    elif tier_val.upper() in ("A", "B"):
        return tier_val.upper()
    return "A"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class AccountRecord:
    """Input record for an account from CSV/JSON."""
    company_name: str
    score: float = 0.0
    tier: str = "A"
    account_id: Optional[str] = None
    domain: Optional[str] = None
    notes: Optional[str] = None
    signal_tags: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["AccountRecord"]:
        """
        Create AccountRecord from dict (JSON or CSV row).

        Supports column aliases for Salesforce export compatibility:
          - acct name -> company_name
          - priority_score -> score
          - priority_tier -> tier
          - acct id -> account_id

        Returns:
            AccountRecord or None if company_name is missing
        """
        # Resolve company name (required)
        company, _ = _resolve_column(data, "company_name")
        if not company:
            return None  # Caller should log warning

        # Resolve score (default 0)
        score_val, _ = _resolve_column(data, "score")
        try:
            score = float(score_val) if score_val else 0.0
        except (ValueError, TypeError):
            score = 0.0

        # Resolve tier (normalize)
        tier_val, _ = _resolve_column(data, "tier")
        tier = _normalize_tier(tier_val)

        # Resolve account_id (optional)
        account_id, _ = _resolve_column(data, "account_id")

        # Resolve domain (optional)
        domain, _ = _resolve_column(data, "domain")

        # Resolve tags
        tags_val, _ = _resolve_column(data, "tags")
        tags = tags_val or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        return cls(
            company_name=str(company).strip(),
            score=score,
            tier=tier,
            account_id=str(account_id) if account_id else None,
            domain=domain,
            notes=data.get("notes"),
            signal_tags=tags
        )


@dataclass
class ContactResult:
    """Result for a single contact draft attempt."""
    name: str
    title: str
    status: str  # "prepared_for_rendering", "rendered_validated", "rejected", "skipped"
    draft_path: Optional[str] = None
    confidence_mode: Optional[str] = None
    cited_signals: int = 0
    company_cited: int = 0  # Company-level cited signals
    newest_cited_age_days: Optional[int] = None  # Age of newest cited signal
    warnings: List[str] = field(default_factory=list)  # Context quality warnings
    rejection_reason: Optional[str] = None
    error: Optional[str] = None
    # Phase 2 additions
    rendered_validated: bool = False  # Whether render_and_validate passed
    promotion_eligible: bool = False  # Whether eligible for promotion
    render_skipped_reason: Optional[str] = None  # Reason if render was skipped


@dataclass
class AccountResult:
    """Result for processing a single account."""
    company_name: str
    score: float
    status: str  # "processed", "skipped"
    skip_reason: Optional[str] = None
    contacts: List[ContactResult] = field(default_factory=list)


@dataclass
class RunSummary:
    """Summary statistics for the run."""
    accounts_processed: int = 0
    accounts_skipped: int = 0
    prepared_for_rendering: int = 0
    rendered_validated: int = 0  # Phase 2: count of successfully rendered
    rejected: int = 0
    render_skipped: int = 0  # Phase 2: count of render skips


@dataclass
class OutboundConfig:
    """Configuration for an outbound run."""
    accounts_path: Path
    top_n: int = 10
    max_drafts_per_account: int = 3
    max_total_drafts: int = 20
    tier: str = "A"
    mode: str = "hybrid"
    experiment: Optional[str] = None
    refresh: str = "none"  # none, company, contact, all (no-op v1)
    dry_run: bool = False
    since_days: int = 7
    output_root: Optional[Path] = None
    # Phase 2 additions
    render_emails: bool = False  # Opt-in batch rendering
    render_policy: str = "strict"  # "strict" or "permissive"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "accounts_path": str(self.accounts_path),
            "top_n": self.top_n,
            "max_drafts_per_account": self.max_drafts_per_account,
            "max_total_drafts": self.max_total_drafts,
            "tier": self.tier,
            "mode": self.mode,
            "experiment": self.experiment,
            "refresh": self.refresh,
            "dry_run": self.dry_run,
            "since_days": self.since_days,
            "output_root": str(self.output_root) if self.output_root else None,
            "render_emails": self.render_emails,
            "render_policy": self.render_policy
        }


@dataclass
class RunResult:
    """Full result of an outbound run."""
    run_date: str
    settings: Dict[str, Any]
    summary: RunSummary
    accounts: List[AccountResult] = field(default_factory=list)
    skipped_accounts: List[Dict[str, str]] = field(default_factory=list)


# =============================================================================
# PERSONA MAPPING
# =============================================================================

# Default personas to search for
DEFAULT_PERSONAS = ["quality", "ops", "it"]

# Role keywords for each persona
PERSONA_ROLE_KEYWORDS = {
    "quality": ["quality director", "vp quality", "quality manager", "head of quality"],
    "ops": ["operations director", "vp operations", "operations manager", "head of operations"],
    "it": ["it director", "cio", "it manager", "head of it"]
}

# Priority order based on signal tags
PERSONA_PRIORITY_BY_TAG = {
    "quality_focused": ["quality", "ops", "it"],
    "operations_focused": ["ops", "quality", "it"],
    "it_focused": ["it", "ops", "quality"],
    "regulatory": ["quality", "ops", "it"],
    "manufacturing": ["ops", "quality", "it"],
    "digital": ["it", "ops", "quality"],
}


def get_personas_for_account(account: AccountRecord) -> List[str]:
    """
    Determine persona priority order for an account.

    Uses signal_tags to prioritize, falls back to default order.

    Args:
        account: AccountRecord with optional signal_tags

    Returns:
        List of personas in priority order
    """
    # Check tags for priority hints
    for tag in account.signal_tags:
        tag_lower = tag.lower().replace(" ", "_")
        if tag_lower in PERSONA_PRIORITY_BY_TAG:
            return PERSONA_PRIORITY_BY_TAG[tag_lower]

    return DEFAULT_PERSONAS.copy()


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

class OutboundOrchestrator:
    """
    Orchestrates batch prospect email generation.

    This is a CONTROL PLANE that:
    1. Loads ranked accounts
    2. Selects top N by score/tier
    3. For each account, finds contacts and runs prospect pipeline
    4. Verifies quality gates
    5. Produces dashboard output
    """

    def __init__(self, config: OutboundConfig):
        """
        Initialize orchestrator with config.

        Args:
            config: OutboundConfig with all settings
        """
        self.config = config

        # Set output root (can be overridden via config)
        if config.output_root:
            os.environ["PROSPECTING_OUTPUT_ROOT"] = str(config.output_root)

        self.output_root = get_prospecting_root()

        # Initialize clients lazily
        self._zoominfo_client = None
        self._zoominfo_available = None  # None = not checked yet

        # Track totals for caps
        self.total_drafts_generated = 0

        logger.info(f"Initialized OutboundOrchestrator with output_root={self.output_root}")

    @property
    def zoominfo_client(self):
        """Lazily initialize ZoomInfo client."""
        if self._zoominfo_available is None:
            self._check_zoominfo_availability()
        return self._zoominfo_client

    @property
    def zoominfo_available(self) -> bool:
        """Check if ZoomInfo is available."""
        if self._zoominfo_available is None:
            self._check_zoominfo_availability()
        return self._zoominfo_available

    def _check_zoominfo_availability(self):
        """Check if ZoomInfo credentials are configured."""
        try:
            from .zoominfo_client import ZoomInfoClient
            from .zoominfo_jwt_manager import ZoomInfoJWTManager

            # ZoomInfoJWTManager will raise if credentials missing
            # It reads ZOOMINFO_USERNAME, ZOOMINFO_CLIENT_ID from env
            # and loads private key from ZOOMINFO_PRIVATE_KEY_FILE
            jwt_manager = ZoomInfoJWTManager()
            self._zoominfo_client = ZoomInfoClient(jwt_manager)
            self._zoominfo_available = True
            logger.info("ZoomInfo client initialized successfully")

        except Exception as e:
            logger.warning(f"ZoomInfo unavailable: {e}")
            self._zoominfo_available = False

    def load_accounts(self, filepath: Path) -> List[AccountRecord]:
        """
        Load accounts from CSV or JSON file.

        Args:
            filepath: Path to accounts file

        Returns:
            List of AccountRecord objects

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is unsupported
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Accounts file not found: {filepath}")

        suffix = filepath.suffix.lower()

        if suffix == ".csv":
            return self._load_csv(filepath)
        elif suffix == ".json":
            return self._load_json(filepath)
        else:
            raise ValueError(f"Unsupported file format: {suffix}. Use .csv or .json")

    def _load_csv(self, filepath: Path) -> List[AccountRecord]:
        """Load accounts from CSV file."""
        accounts = []
        skipped_no_company = 0
        column_mappings_logged = False

        with open(filepath, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            # Log detected column mappings once
            if reader.fieldnames:
                detected = {}
                for field, aliases in COLUMN_ALIASES.items():
                    for alias in aliases:
                        if alias in reader.fieldnames:
                            detected[field] = alias
                            break
                if detected:
                    logger.info(f"CSV column mappings: {detected}")
                    column_mappings_logged = True

            for row in reader:
                try:
                    account = AccountRecord.from_dict(row)
                    if account:
                        accounts.append(account)
                    else:
                        skipped_no_company += 1
                except Exception as e:
                    logger.warning(f"Skipping invalid row: {e}")

        if skipped_no_company > 0:
            logger.warning(f"Skipped {skipped_no_company} rows with missing company name")

        logger.info(f"Loaded {len(accounts)} accounts from CSV")
        return accounts

    def _load_json(self, filepath: Path) -> List[AccountRecord]:
        """Load accounts from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Support both list and {"accounts": [...]} format
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict) and "accounts" in data:
            records = data["accounts"]
        else:
            raise ValueError("JSON must be a list or have 'accounts' key")

        accounts = []
        skipped_no_company = 0
        for record in records:
            try:
                account = AccountRecord.from_dict(record)
                if account:
                    accounts.append(account)
                else:
                    skipped_no_company += 1
            except Exception as e:
                logger.warning(f"Skipping invalid record: {e}")

        if skipped_no_company > 0:
            logger.warning(f"Skipped {skipped_no_company} records with missing company name")

        logger.info(f"Loaded {len(accounts)} accounts from JSON")
        return accounts

    def select_accounts(
        self,
        accounts: List[AccountRecord],
        top_n: int,
        tier_filter: Optional[str] = None
    ) -> List[AccountRecord]:
        """
        Select top N accounts by score, optionally filtered by account tier.

        Note: tier_filter filters by account's tier field in the input file,
        NOT the generation tier (which is set separately via config.tier).

        Args:
            accounts: All loaded accounts
            top_n: Number to select
            tier_filter: Optional account tier to filter by (A or B)

        Returns:
            Top N accounts sorted by score descending
        """
        filtered = accounts

        # Filter by account tier if specified
        # Note: This is separate from generation tier (config.tier)
        if tier_filter:
            filtered = [a for a in accounts if a.tier.upper() == tier_filter.upper()]
            logger.info(f"Filtered to {len(filtered)} accounts with account_tier={tier_filter}")

        # Sort by score descending
        sorted_accounts = sorted(filtered, key=lambda a: a.score, reverse=True)

        # Take top N
        selected = sorted_accounts[:top_n]
        logger.info(f"Selected top {len(selected)} accounts by score")

        return selected

    def should_skip_account(
        self,
        account: AccountRecord,
        since_days: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if account should be skipped due to recent drafts.

        Args:
            account: Account to check
            since_days: Skip if draft exists within this many days

        Returns:
            (should_skip, reason) tuple
        """
        drafts_folder = get_drafts_folder(account.company_name)

        if not drafts_folder.exists():
            return False, None

        cutoff = datetime.now() - timedelta(days=since_days)

        # Check for any draft files modified within since_days
        for draft_file in drafts_folder.iterdir():
            if draft_file.is_file():
                mtime = datetime.fromtimestamp(draft_file.stat().st_mtime)
                if mtime > cutoff:
                    return True, f"Draft exists within {since_days} days ({draft_file.name})"

        return False, None

    def find_contacts(
        self,
        company_name: str,
        personas: List[str],
        max_per_persona: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Find contacts for personas at a company using ZoomInfo.

        Args:
            company_name: Company to search
            personas: List of persona keys to search
            max_per_persona: Max contacts per persona

        Returns:
            List of contact dicts with name, title, persona
        """
        if not self.zoominfo_available:
            logger.warning(f"ZoomInfo unavailable, cannot find contacts for {company_name}")
            return []

        contacts = []

        for persona in personas:
            role_keywords = PERSONA_ROLE_KEYWORDS.get(persona, [persona])

            for keyword in role_keywords:
                try:
                    results = self.zoominfo_client.search_contacts_by_role(
                        role_keywords=keyword,
                        company_name=company_name,
                        limit=max_per_persona
                    )

                    for contact in results:
                        # Ensure we have name and title
                        first_name = contact.get("first_name", "")
                        last_name = contact.get("last_name", "")
                        title = contact.get("title", "")

                        if first_name and title:
                            contacts.append({
                                "name": f"{first_name} {last_name}".strip(),
                                "first_name": first_name,
                                "last_name": last_name,
                                "title": title,
                                "persona": persona,
                                "company_name": company_name
                            })

                    # Stop after finding contacts for this persona
                    if len([c for c in contacts if c["persona"] == persona]) >= max_per_persona:
                        break

                except Exception as e:
                    logger.error(f"Error searching for {keyword} at {company_name}: {e}")

        # Dedupe by name
        seen_names = set()
        unique_contacts = []
        for contact in contacts:
            if contact["name"] not in seen_names:
                seen_names.add(contact["name"])
                unique_contacts.append(contact)

        logger.info(f"Found {len(unique_contacts)} unique contacts at {company_name}")
        return unique_contacts

    def run_prospect_pipeline(
        self,
        company_name: str,
        contact: Dict[str, Any],
        tier: str,
        mode: str,
        experiment: Optional[str]
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Run the prospect pipeline for a single contact.

        This follows the same pattern as /prospect command:
        1. Run research via ResearchOrchestrator
        2. Run rules engine via prepare_email_context logic
        3. Save the email context/plan for Claude Code to render

        Args:
            company_name: Company name
            contact: Contact dict with name, title
            tier: Prospect tier (A or B)
            mode: Generation mode (hybrid or legacy)
            experiment: Optional experiment name

        Returns:
            (draft_path, result_dict) where draft_path is None if failed
        """
        from .research_orchestrator import ResearchOrchestrator
        from .perplexity_client import PerplexityClient
        from .caching import ContactCache
        from .rules_loader import load_rules
        from .relevance_engine import build_prospect_brief
        from .email_assembler import EmailAssembler

        contact_name = contact["name"]
        logger.info(f"Running prospect pipeline for {contact_name} at {company_name}")

        try:
            # Ensure folders exist
            ensure_folders_exist(company_name)

            # Initialize research clients
            perplexity_key = os.getenv("PERPLEXITY_API_KEY")
            if not perplexity_key:
                logger.warning("Perplexity API key not configured")
                perplexity = None
            else:
                perplexity = PerplexityClient(api_key=perplexity_key)

            cache = ContactCache()

            # Research orchestrator takes positional args: zoominfo_client, perplexity_client, cache
            research_orchestrator = ResearchOrchestrator(
                self._zoominfo_client if self.zoominfo_available else None,
                perplexity,
                cache
            )

            # Step 1: Run research (same as /prospect Step 1)
            research_data = research_orchestrator.research_prospect(
                name=contact_name,
                company=company_name,
                force_refresh=False
            )

            # Step 2: Run rules engine (same as /prospect Step 2)
            rules_config = load_rules(experiment=experiment, tier=tier)

            prospect_brief = build_prospect_brief(
                research_data=research_data,
                context=research_data,
                tier=tier,
                rules_config=rules_config
            )

            logger.info(f"Prospect brief status: {prospect_brief.get('status')}")

            # Check if we have enough signals
            if prospect_brief.get("status") == "needs_more_research":
                signals_found = prospect_brief.get("signals_found", prospect_brief.get("signal_count", 0))
                signals_required = prospect_brief.get("signals_required", 3 if tier == "A" else 2)

                # Build context_quality even for rejections (required for dashboard metrics)
                context_quality_builder = ContextQualityBuilder()
                context_quality = context_quality_builder.build(
                    research_data=research_data,
                    prospect_brief=prospect_brief,
                    company_intel=research_data.get("company_intel"),
                    persona_result=prospect_brief.get("persona_diagnostics"),
                    confidence_result=prospect_brief.get("confidence_diagnostics")
                )

                return None, {
                    "status": "rejected",
                    "rejection_reason": f"Insufficient signals ({signals_found}/{signals_required} for tier {tier})",
                    "context_quality": context_quality
                }

            # Step 3: Build email plan (draft sentences using rules)
            assembler = EmailAssembler()
            email_plan = assembler.build_email_plan(
                prospect_brief=prospect_brief,
                rules_config=rules_config
            )

            # Build canonical context quality using ContextQualityBuilder
            context_quality_builder = ContextQualityBuilder()
            context_quality = context_quality_builder.build(
                research_data=research_data,
                prospect_brief=prospect_brief,
                company_intel=research_data.get("company_intel"),
                persona_result=prospect_brief.get("persona_diagnostics"),
                confidence_result=prospect_brief.get("confidence_diagnostics")
            )

            # Build result with all context for Claude Code to render
            result = {
                "status": "ready_for_rendering",
                "mode": mode,
                "tier": tier,
                "research_data": research_data,
                "prospect_brief": prospect_brief,
                "email_plan": email_plan,
                "contact": contact,
                "company_name": company_name,
                "context_quality": context_quality
            }

            # Save draft context to correct location
            draft_path = self._save_draft(company_name, contact_name, result)

            return draft_path, result

        except Exception as e:
            logger.error(f"Pipeline failed for {contact_name}: {e}", exc_info=True)
            return None, {"status": "error", "error": str(e)}

    def _save_draft(
        self,
        company_name: str,
        contact_name: str,
        result: Dict[str, Any]
    ) -> Optional[str]:
        """
        Save draft artifacts to the correct location.

        Canonical artifact contract (handoff to Claude Code):
        1. {date}_{contact}_email_context.json - Full context for rendering
        2. {date}_{contact}_email.md - Human-readable email plan (NOT final copy)
        3. {date}_{contact}_context_quality.json - Quality metadata

        These files are the handoff point to Claude Code for final rendering.
        """
        drafts_folder = get_drafts_folder(company_name)
        drafts_folder.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        sanitized_contact = sanitize_name(contact_name)

        # ARTIFACT 1: email_context.json - Full context for Claude Code to render
        context_path = drafts_folder / f"{date_str}_{sanitized_contact}_email_context.json"
        with open(context_path, "w") as f:
            json.dump(result, f, indent=2, default=str)

        # Extract data for readable artifacts
        email_plan = result.get("email_plan", {})
        prospect_brief = result.get("prospect_brief", {})
        contact_data = result.get("contact", {})

        # Get draft sentences from email plan
        sentences = [
            email_plan.get("sentence_1_draft", ""),
            email_plan.get("sentence_2_draft", ""),
            email_plan.get("sentence_3_draft", ""),
            email_plan.get("sentence_4_draft", "")
        ]
        draft_body = " ".join(s for s in sentences if s)

        # Get subject candidates
        subject_candidates = email_plan.get("subject_candidates", ["[Subject needed]"])

        # Get cited signals
        cited_signals = prospect_brief.get("cited_signals", prospect_brief.get("verified_signals", []))

        # ARTIFACT 2: email.md - Human-readable email PLAN (not final copy)
        email_path = drafts_folder / f"{date_str}_{sanitized_contact}_email.md"
        content = f"""# Email Plan: {contact_name}

> **This is an EMAIL PLAN, not final copy.**
> Run `/prospect {contact_name} at {company_name}` to render final email.

## Metadata
| Field | Value |
|-------|-------|
| Company | {company_name} |
| Date | {date_str} |
| Status | {result.get('status', 'unknown')} |
| Mode | {result.get('mode', 'unknown')} |
| Tier | {result.get('tier', 'unknown')} |

## Context Quality
| Metric | Value |
|--------|-------|
| Confidence Mode | {prospect_brief.get('confidence_tier', 'unknown')} |
| Persona | {prospect_brief.get('persona', 'unknown')} |
| Angle | {prospect_brief.get('angle_id', 'unknown')} |
| Offer | {prospect_brief.get('offer_id', 'unknown')} |
| Cited Signals | {len(cited_signals)} |

## Subject Candidates
{chr(10).join(f'- {s}' for s in subject_candidates)}

## Draft Sentences (from email_plan)
{draft_body}

## Cited Signals (from relevance_engine)
{chr(10).join(f"- **[{s.get('signal_id', 'N/A')}]** {s.get('claim', s.get('description', 'N/A'))}" for s in cited_signals) if cited_signals else "*No cited signals*"}

## Contact Info
- **Name:** {contact_data.get('name', contact_name)}
- **Title:** {contact_data.get('title', 'Unknown')}

---
## Artifacts
- `{date_str}_{sanitized_contact}_email_context.json` - Full context for rendering
- `{date_str}_{sanitized_contact}_email.md` - This file (email plan)
- `{date_str}_{sanitized_contact}_context_quality.json` - Quality metadata
"""
        with open(email_path, "w") as f:
            f.write(content)

        # ARTIFACT 3: context_quality.json - Canonical quality metadata (always written)
        # Use the canonical context_quality from ContextQualityBuilder
        context_quality = result.get("context_quality", {})
        quality_path = drafts_folder / f"{date_str}_{sanitized_contact}_context_quality.json"

        if isinstance(context_quality, dict) and "signals" in context_quality:
            # Already canonical format from ContextQualityBuilder
            quality_data = context_quality
            # Add artifact paths if not present
            if "artifacts" not in quality_data or not quality_data["artifacts"]:
                quality_data["artifacts"] = {
                    "email_context": str(context_path),
                    "email_md": str(email_path),
                    "context_quality_json": str(quality_path)
                }
        else:
            # Fallback for legacy format - convert to canonical-like structure
            signals = prospect_brief.get("cited_signals", prospect_brief.get("verified_signals", []))

            # Extract confidence_mode from canonical or flat structure
            conf_mode = "unknown"
            if isinstance(context_quality, dict):
                mode_section = context_quality.get("mode") or {}
                conf_mode = mode_section.get("confidence_mode") if isinstance(mode_section, dict) else None
                if not conf_mode:
                    conf_mode = context_quality.get("confidence_mode") or "unknown"

            quality_data = {
                "generated_at": datetime.now().isoformat(),
                "run_id": context_quality.get("run_id") if isinstance(context_quality, dict) else None,
                "company": {"name": company_name},
                "contact": {"name": contact_name},
                "mode": {
                    "tier": result.get("tier"),
                    "confidence_mode": conf_mode
                },
                "sources": {},
                "signals": {
                    "counts": {
                        "total_cited": len(signals),
                        "company_cited": 0,
                        "person_cited": len(signals),
                        "total_vendor": 0
                    },
                    "freshness": {},
                    "warnings": []
                },
                "artifacts": {
                    "email_context": str(context_path),
                    "email_md": str(email_path),
                    "context_quality_json": str(quality_path)
                }
            }

        with open(quality_path, "w", encoding="utf-8") as f:
            json.dump(quality_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved draft artifacts to {drafts_folder}")
        return str(context_path)

    def verify_draft_quality(
        self,
        draft_path: Optional[str],
        result: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Verify that a draft meets all quality gates.

        Quality gates:
        1. Artifact exists (email_context.json)
        2. Context quality header present with confidence_mode
        3. Status is ready_for_rendering
        4. Output is under PROSPECTING_OUTPUT_ROOT

        Args:
            draft_path: Path to draft file
            result: Result dict from pipeline

        Returns:
            (passed, rejection_reasons) tuple
        """
        reasons = []

        # Gate 1: Artifact exists
        if not draft_path or not Path(draft_path).exists():
            reasons.append("Draft artifact does not exist")
            return False, reasons

        # Gate 2: Check location is under output_root
        draft_path_obj = Path(draft_path).resolve()
        output_root_resolved = self.output_root.resolve()
        try:
            draft_path_obj.relative_to(output_root_resolved)
        except ValueError:
            reasons.append(f"Draft not under output_root ({output_root_resolved})")

        # Gate 3: Context quality with confidence_mode
        # Support both canonical schema (mode.confidence_mode) and legacy flat structure
        context_quality = result.get("context_quality")
        if context_quality:
            if hasattr(context_quality, "confidence_mode"):
                # ProspectContextQuality dataclass
                confidence = context_quality.confidence_mode
            elif isinstance(context_quality, dict):
                # Check canonical schema first (mode.confidence_mode)
                mode_section = context_quality.get("mode") or {}
                confidence = mode_section.get("confidence_mode") if isinstance(mode_section, dict) else None
                # Fall back to flat structure for legacy compatibility
                if not confidence:
                    confidence = context_quality.get("confidence_mode")
            else:
                confidence = None

            if not confidence:
                reasons.append("Missing confidence_mode in context quality")
        else:
            reasons.append("Missing context quality header")

        # Gate 4: Status is ready_for_rendering (replaced validation check)
        status = result.get("status")
        if status != "ready_for_rendering":
            reasons.append(f"Status is '{status}', expected 'ready_for_rendering'")

        passed = len(reasons) == 0
        return passed, reasons

    def _execute_batch_render(
        self,
        company_name: str,
        contact_name: str,
        draft_path: str
    ) -> bool:
        """
        Execute batch rendering via render_and_validate.py.

        Args:
            company_name: Company name
            contact_name: Contact name
            draft_path: Path to draft email_context.json

        Returns:
            True if rendering and validation passed, False otherwise
        """
        import subprocess

        logger.info(f"Executing batch render for {contact_name} at {company_name}")

        try:
            # Get the scripts directory
            scripts_dir = Path(__file__).parent.parent / "scripts"
            render_script = scripts_dir / "render_and_validate.py"

            if not render_script.exists():
                logger.error(f"Render script not found: {render_script}")
                return False

            # Run render_and_validate.py with --output json
            result = subprocess.run(
                [
                    sys.executable,
                    str(render_script),
                    "--output", "json"
                ],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                cwd=str(scripts_dir.parent)
            )

            if result.returncode != 0:
                logger.error(f"Render script failed: {result.stderr}")
                return False

            # Parse output to check validation status
            try:
                output = json.loads(result.stdout)
                status = output.get("status", "")

                if status == "success":
                    logger.info(f"Render succeeded for {contact_name}")
                    return True
                else:
                    logger.warning(f"Render validation failed for {contact_name}: {output.get('error', 'unknown')}")
                    return False

            except json.JSONDecodeError:
                # Check for PASSED in raw output
                if "PASSED" in result.stdout:
                    logger.info(f"Render succeeded for {contact_name} (raw output)")
                    return True
                else:
                    logger.warning(f"Could not parse render output for {contact_name}")
                    return False

        except subprocess.TimeoutExpired:
            logger.error(f"Render timeout for {contact_name}")
            return False
        except Exception as e:
            logger.error(f"Render error for {contact_name}: {e}")
            return False

    def run(self) -> RunResult:
        """
        Execute the full outbound run.

        Returns:
            RunResult with all data for dashboard
        """
        run_date = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"Starting outbound run for {run_date}")

        # Initialize result
        result = RunResult(
            run_date=run_date,
            settings=self.config.to_dict(),
            summary=RunSummary()
        )

        # Load accounts
        accounts = self.load_accounts(self.config.accounts_path)

        # Select top N (no tier filtering - tier is for generation, not selection)
        selected = self.select_accounts(
            accounts,
            top_n=self.config.top_n,
            tier_filter=None  # Don't filter by tier; config.tier is for email generation
        )

        # Process each account
        for account in selected:
            # Check global cap
            if self.total_drafts_generated >= self.config.max_total_drafts:
                logger.info(f"Reached max_total_drafts cap ({self.config.max_total_drafts})")
                break

            # Check if should skip
            should_skip, skip_reason = self.should_skip_account(
                account,
                self.config.since_days
            )

            if should_skip:
                result.skipped_accounts.append({
                    "company_name": account.company_name,
                    "reason": skip_reason
                })
                result.summary.accounts_skipped += 1
                logger.info(f"Skipping {account.company_name}: {skip_reason}")
                continue

            # Dry run mode - just show plan
            if self.config.dry_run:
                logger.info(f"[DRY RUN] Would process {account.company_name}")
                account_result = AccountResult(
                    company_name=account.company_name,
                    score=account.score,
                    status="dry_run"
                )
                result.accounts.append(account_result)
                continue

            # Get personas and find contacts
            personas = get_personas_for_account(account)

            if not self.zoominfo_available:
                # Can't find contacts without ZoomInfo
                result.skipped_accounts.append({
                    "company_name": account.company_name,
                    "reason": "ZoomInfo unavailable - cannot discover contacts"
                })
                result.summary.accounts_skipped += 1
                continue

            contacts = self.find_contacts(
                account.company_name,
                personas,
                max_per_persona=2
            )

            if not contacts:
                result.skipped_accounts.append({
                    "company_name": account.company_name,
                    "reason": "No contacts found via ZoomInfo"
                })
                result.summary.accounts_skipped += 1
                continue

            # Process contacts for this account
            account_result = AccountResult(
                company_name=account.company_name,
                score=account.score,
                status="processed"
            )

            drafts_for_account = 0

            for contact in contacts:
                # Check per-account cap
                if drafts_for_account >= self.config.max_drafts_per_account:
                    logger.info(f"Reached max_drafts_per_account for {account.company_name}")
                    break

                # Check global cap
                if self.total_drafts_generated >= self.config.max_total_drafts:
                    logger.info(f"Reached max_total_drafts cap")
                    break

                # GUARDRAIL: Never generate without name and title
                if not contact.get("name") or not contact.get("title"):
                    account_result.contacts.append(ContactResult(
                        name=contact.get("name", "Unknown"),
                        title=contact.get("title", "Unknown"),
                        status="skipped",
                        rejection_reason="Missing name or title"
                    ))
                    continue

                # Run pipeline
                draft_path, pipeline_result = self.run_prospect_pipeline(
                    company_name=account.company_name,
                    contact=contact,
                    tier=self.config.tier,
                    mode=self.config.mode,
                    experiment=self.config.experiment
                )

                # Check for pipeline-level rejection first (before quality gates)
                if pipeline_result.get("status") in ("rejected", "error"):
                    reason = pipeline_result.get("rejection_reason") or pipeline_result.get("error") or "Pipeline failed"
                    account_result.contacts.append(ContactResult(
                        name=contact["name"],
                        title=contact["title"],
                        status="rejected",
                        rejection_reason=reason
                    ))
                    result.summary.rejected += 1
                    continue

                # Verify quality gates (only if pipeline succeeded)
                passed, rejection_reasons = self.verify_draft_quality(
                    draft_path,
                    pipeline_result
                )

                # Extract metrics for dashboard from canonical context_quality
                confidence_mode = None
                cited_signals = 0
                company_cited = 0
                newest_cited_age_days = None
                cq_warnings = []

                if pipeline_result.get("context_quality"):
                    cq = pipeline_result["context_quality"]
                    if isinstance(cq, dict):
                        # Canonical format: signals.counts.total_cited
                        mode_section = cq.get("mode", {})
                        confidence_mode = mode_section.get("confidence_mode")

                        signals_section = cq.get("signals", {})
                        counts = signals_section.get("counts", {})
                        cited_signals = counts.get("total_cited", 0)
                        company_cited = counts.get("company_cited", 0)

                        # Freshness
                        freshness = signals_section.get("freshness", {})
                        newest_cited_age_days = freshness.get("newest_cited_age_days")

                        # Warnings
                        cq_warnings = signals_section.get("warnings", [])

                        # Fallback for legacy format
                        if not confidence_mode:
                            confidence_mode = cq.get("confidence_mode")
                        if not cited_signals:
                            cited_signals = cq.get("cited_signal_count", 0)

                if passed:
                    # Phase 2: Check batch render eligibility
                    render_gate = BatchRenderGate()
                    persona_diag = pipeline_result.get("prospect_brief", {}).get("persona_diagnostics")
                    if not persona_diag:
                        # Try to get from pipeline result directly
                        persona_diag = pipeline_result.get("persona_diagnostics")

                    render_eligibility = render_gate.evaluate(
                        context_quality=pipeline_result.get("context_quality", {}),
                        persona_diagnostics=persona_diag,
                        force=False,
                        policy=self.config.render_policy
                    )

                    # Phase 2: Check promotion eligibility
                    promo_gate = PromotionGate()
                    promo_eligibility = promo_gate.evaluate(
                        context_quality=pipeline_result.get("context_quality", {}),
                        persona_diagnostics=persona_diag,
                        status=ProspectState.PREPARED_FOR_RENDERING.value,
                        validation_passed=False,  # Not yet rendered
                        force=False
                    )

                    # Determine status and render outcome
                    contact_status = "prepared_for_rendering"
                    rendered_validated = False
                    render_skipped_reason = None

                    # Phase 2: Batch rendering (if enabled and eligible)
                    if self.config.render_emails:
                        if render_eligibility.eligible:
                            # Execute batch render
                            render_success = self._execute_batch_render(
                                account.company_name,
                                contact["name"],
                                draft_path
                            )
                            if render_success:
                                contact_status = "rendered_validated"
                                rendered_validated = True
                                result.summary.rendered_validated += 1

                                # Re-check promotion eligibility with rendered status
                                promo_eligibility = promo_gate.evaluate(
                                    context_quality=pipeline_result.get("context_quality", {}),
                                    persona_diagnostics=persona_diag,
                                    status=ProspectState.RENDERED_VALIDATED.value,
                                    validation_passed=True,
                                    force=False
                                )
                            else:
                                render_skipped_reason = "Render validation failed"
                                result.summary.render_skipped += 1
                        else:
                            render_skipped_reason = "; ".join(render_eligibility.reasons)
                            result.summary.render_skipped += 1
                            logger.info(f"Render skipped for {contact['name']}: {render_skipped_reason}")

                    account_result.contacts.append(ContactResult(
                        name=contact["name"],
                        title=contact["title"],
                        status=contact_status,
                        draft_path=draft_path,
                        confidence_mode=confidence_mode,
                        cited_signals=cited_signals,
                        company_cited=company_cited,
                        newest_cited_age_days=newest_cited_age_days,
                        warnings=cq_warnings,
                        rendered_validated=rendered_validated,
                        promotion_eligible=promo_eligibility.eligible,
                        render_skipped_reason=render_skipped_reason
                    ))
                    result.summary.prepared_for_rendering += 1
                    self.total_drafts_generated += 1
                    drafts_for_account += 1
                else:
                    account_result.contacts.append(ContactResult(
                        name=contact["name"],
                        title=contact["title"],
                        status="rejected",
                        rejection_reason="; ".join(rejection_reasons),
                        confidence_mode=confidence_mode,
                        cited_signals=cited_signals,
                        company_cited=company_cited,
                        newest_cited_age_days=newest_cited_age_days,
                        warnings=cq_warnings
                    ))
                    result.summary.rejected += 1
                    # Note: rejected drafts do NOT count toward max_total_drafts

            result.accounts.append(account_result)
            result.summary.accounts_processed += 1

        # Write dashboard outputs
        self._write_dashboard(result)

        logger.info(
            f"Run complete: {result.summary.accounts_processed} processed, "
            f"{result.summary.prepared_for_rendering} prepared, "
            f"{result.summary.rejected} rejected"
        )

        return result

    def _write_dashboard(self, result: RunResult):
        """Write dashboard outputs (MD and JSON) to runs folder."""
        runs_folder = self.output_root / "runs"
        runs_folder.mkdir(parents=True, exist_ok=True)

        date_str = result.run_date
        md_path = runs_folder / f"{date_str}_outbound_run.md"
        json_path = runs_folder / f"{date_str}_outbound_run.json"

        # Write JSON
        json_data = {
            "run_date": result.run_date,
            "settings": result.settings,
            "summary": asdict(result.summary),
            "accounts": [
                {
                    "company_name": a.company_name,
                    "score": a.score,
                    "status": a.status,
                    "contacts": [
                        {
                            "name": c.name,
                            "title": c.title,
                            "status": c.status,
                            "draft_path": c.draft_path,
                            "confidence_mode": c.confidence_mode,
                            "cited_signals": c.cited_signals,
                            "company_cited": c.company_cited,
                            "newest_cited_age_days": c.newest_cited_age_days,
                            "warnings": c.warnings,
                            "rejection_reason": c.rejection_reason,
                            # Phase 2 fields
                            "rendered_validated": c.rendered_validated,
                            "promotion_eligible": c.promotion_eligible,
                            "render_skipped_reason": c.render_skipped_reason
                        }
                        for c in a.contacts
                    ]
                }
                for a in result.accounts
            ],
            "skipped_accounts": result.skipped_accounts
        }

        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=2)

        logger.info(f"Wrote JSON dashboard to {json_path}")

        # Write Markdown
        md_content = self._format_markdown_dashboard(result)
        with open(md_path, "w") as f:
            f.write(md_content)

        logger.info(f"Wrote Markdown dashboard to {md_path}")

    def _format_markdown_dashboard(self, result: RunResult) -> str:
        """Format dashboard as markdown."""
        lines = []

        lines.append("# Outbound Run Dashboard")
        lines.append(f"**Date:** {result.run_date}")
        lines.append("")
        lines.append("## Settings")
        for key, value in result.settings.items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")

        lines.append("## Summary")
        lines.append(f"- Accounts processed: {result.summary.accounts_processed}")
        lines.append(f"- Accounts skipped: {result.summary.accounts_skipped}")
        lines.append(f"- Prepared for rendering: {result.summary.prepared_for_rendering}")
        lines.append(f"- Rendered & validated: {result.summary.rendered_validated}")
        lines.append(f"- Render skipped: {result.summary.render_skipped}")
        lines.append(f"- Rejected: {result.summary.rejected}")
        lines.append("")

        lines.append("## Accounts Processed")
        lines.append("")

        for i, account in enumerate(result.accounts, 1):
            lines.append(f"### {i}. {account.company_name} (Score: {account.score})")
            lines.append("")

            if account.contacts:
                lines.append("**Contacts:**")
                lines.append("")
                lines.append("| Name | Title | Status | Conf | Cited | Co. | Fresh | Rend | Promo | Warnings |")
                lines.append("|------|-------|--------|------|-------|-----|-------|------|-------|----------|")

                for contact in account.contacts:
                    conf = contact.confidence_mode or "-"
                    if contact.status == "rejected":
                        reason = contact.rejection_reason or "unknown"
                        if len(reason) > 15:
                            reason = reason[:12] + "..."
                        conf = f"REJ:{reason}"

                    # Format freshness
                    fresh = "-"
                    if contact.newest_cited_age_days is not None:
                        fresh = f"{contact.newest_cited_age_days}d"

                    # Format warnings
                    warn_str = "-"
                    if contact.warnings:
                        # Extract just warning codes
                        codes = []
                        for w in contact.warnings[:2]:  # Max 2 warnings shown
                            if ":" in w:
                                codes.append(w.split(":")[0].replace("_", ""))
                            else:
                                codes.append(w[:8])
                        warn_str = ",".join(codes)
                        if len(contact.warnings) > 2:
                            warn_str += f"+{len(contact.warnings)-2}"

                    # Phase 2 columns
                    rendered = "Y" if contact.rendered_validated else "N"
                    promo = "Y" if contact.promotion_eligible else "N"

                    # Add render skip reason hint
                    if contact.render_skipped_reason and not contact.rendered_validated:
                        rendered = f"N*"  # asterisk indicates reason exists

                    lines.append(
                        f"| {contact.name} | {contact.title} | {contact.status} | "
                        f"{conf} | {contact.cited_signals} | {contact.company_cited} | "
                        f"{fresh} | {rendered} | {promo} | {warn_str} |"
                    )

                lines.append("")
            else:
                lines.append("*No contacts processed*")
                lines.append("")

        if result.skipped_accounts:
            lines.append("## Accounts Skipped")
            lines.append("")
            lines.append("| Account | Reason |")
            lines.append("|---------|--------|")
            for skip in result.skipped_accounts:
                lines.append(f"| {skip['company_name']} | {skip['reason']} |")
            lines.append("")

        return "\n".join(lines)
