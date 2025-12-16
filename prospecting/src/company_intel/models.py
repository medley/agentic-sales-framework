"""
Data Models for Company Intelligence

These dataclasses define the structure for company intel storage and API responses.
All models are JSON-serializable and used across cache, providers, and service layers.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    """Signal source type classification."""
    PUBLIC_URL = "public_url"       # Cited, sayable for explicit claims
    VENDOR_DATA = "vendor_data"     # Uncited, guidance only
    USER_PROVIDED = "user_provided" # Cited, sayable
    INFERRED = "inferred"           # Generic, guidance only


class Citability(str, Enum):
    """Signal citability classification."""
    CITED = "cited"       # Can be used for explicit claims
    UNCITED = "uncited"   # Cannot be cited, angle guidance only
    GENERIC = "generic"   # Industry-level only


class ProviderStatusCode(str, Enum):
    """Provider execution status."""
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"
    NOT_FOUND = "not_found"
    STALE = "stale"


@dataclass
class CompanySignal:
    """
    A company-level signal extracted from an intel provider.

    Signals are the core output of the company intel system.
    They are merged into the prospect brief and used for email personalization.
    """
    signal_id: str                      # Unique ID: "{provider}_{topic}_{seq}"
    claim: str                          # The factual claim text
    source_url: str                     # Real URL (SEC filing, FDA letter, etc.)
    source_type: str                    # 'public_url' | 'vendor_data' | 'user_provided' | 'inferred'
    citability: str                     # 'cited' | 'uncited' | 'generic'
    scope: str = "company_level"        # Always 'company_level' for company intel

    # Temporal metadata
    as_of_date: Optional[str] = None    # Filing/source date (YYYY-MM-DD)
    recency_days: int = 180             # Days since as_of_date

    # Extraction metadata
    key_terms: List[str] = field(default_factory=list)  # For semantic validation
    provider: str = ""                  # 'sec', 'fda', 'news', etc.
    filing_type: Optional[str] = None   # '10-K', '10-Q', 'warning_letter', etc.
    confidence: str = "medium"          # 'high', 'medium', 'low' (extraction confidence)

    # Topic categorization
    topic: Optional[str] = None         # 'manufacturing_footprint', 'restructuring', etc.

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanySignal':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class CompanyAliases:
    """
    All known identifiers for a company.

    Used for alias resolution: given any identifier, find the primary_account_id.
    """
    site_account_ids: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    zoominfo_company_ids: List[str] = field(default_factory=list)
    sec_cik: Optional[str] = None
    normalized_names: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanyAliases':
        """Create from dictionary."""
        return cls(**data)

    def add_alias(self, alias_type: str, alias_value: str) -> None:
        """Add an alias of the specified type."""
        if alias_type == 'site_account_id':
            if alias_value not in self.site_account_ids:
                self.site_account_ids.append(alias_value)
        elif alias_type == 'domain':
            if alias_value not in self.domains:
                self.domains.append(alias_value)
        elif alias_type == 'zoominfo_id':
            if alias_value not in self.zoominfo_company_ids:
                self.zoominfo_company_ids.append(alias_value)
        elif alias_type == 'sec_cik':
            self.sec_cik = alias_value
        elif alias_type == 'name':
            if alias_value not in self.normalized_names:
                self.normalized_names.append(alias_value)


@dataclass
class ProviderStatus:
    """
    Status of a single provider's execution.

    Stored in index.json for each provider that has run.
    """
    status: str                         # 'success', 'error', 'skipped', 'not_found', 'stale'
    ran: bool = True                    # Whether provider was executed
    last_run: Optional[str] = None      # ISO timestamp of last run
    expires_at: Optional[str] = None    # ISO timestamp when data expires
    signal_count: int = 0               # Number of signals extracted
    error: Optional[str] = None         # Error message if status='error'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProviderStatus':
        """Create from dictionary."""
        return cls(**data)

    def is_expired(self) -> bool:
        """Check if the provider data has expired."""
        if not self.expires_at:
            return True
        try:
            expires = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
            return datetime.now(expires.tzinfo) > expires
        except (ValueError, TypeError):
            return True


@dataclass
class CompanyIntelResult:
    """
    Complete company intelligence result.

    Returned by CompanyIntelService.get_company_intel().
    Contains all signals, provider status, and aliases.
    """
    company_name: str
    primary_account_id: str
    aliases: CompanyAliases = field(default_factory=CompanyAliases)

    # Timestamps
    created_at: Optional[str] = None
    last_refreshed: Optional[str] = None

    # Provider status
    sources: Dict[str, ProviderStatus] = field(default_factory=dict)

    # Signals grouped by source_type
    signals: Dict[str, List[CompanySignal]] = field(default_factory=lambda: {
        'public_url': [],
        'vendor_data': [],
        'user_provided': [],
        'inferred': []
    })

    # Aggregated counts
    total_signals: Dict[str, int] = field(default_factory=lambda: {
        'public_url': 0,
        'vendor_data': 0,
        'user_provided': 0,
        'inferred': 0
    })

    # Errors during fetch
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'company_name': self.company_name,
            'primary_account_id': self.primary_account_id,
            'aliases': self.aliases.to_dict() if isinstance(self.aliases, CompanyAliases) else self.aliases,
            'created_at': self.created_at,
            'last_refreshed': self.last_refreshed,
            'sources': {
                k: v.to_dict() if isinstance(v, ProviderStatus) else v
                for k, v in self.sources.items()
            },
            'signals': {
                source_type: [
                    s.to_dict() if isinstance(s, CompanySignal) else s
                    for s in signals
                ]
                for source_type, signals in self.signals.items()
            },
            'total_signals': self.total_signals,
            'errors': self.errors
        }
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanyIntelResult':
        """Create from dictionary (e.g., loaded from JSON)."""
        aliases_data = data.get('aliases', {})
        aliases = CompanyAliases.from_dict(aliases_data) if isinstance(aliases_data, dict) else aliases_data

        sources_data = data.get('sources', {})
        sources = {
            k: ProviderStatus.from_dict(v) if isinstance(v, dict) else v
            for k, v in sources_data.items()
        }

        signals_data = data.get('signals', {})
        signals = {
            source_type: [
                CompanySignal.from_dict(s) if isinstance(s, dict) else s
                for s in signal_list
            ]
            for source_type, signal_list in signals_data.items()
        }

        return cls(
            company_name=data.get('company_name', ''),
            primary_account_id=data.get('primary_account_id', ''),
            aliases=aliases,
            created_at=data.get('created_at'),
            last_refreshed=data.get('last_refreshed'),
            sources=sources,
            signals=signals,
            total_signals=data.get('total_signals', {}),
            errors=data.get('errors', [])
        )

    def add_signal(self, signal: CompanySignal) -> None:
        """Add a signal to the appropriate source_type bucket."""
        source_type = signal.source_type
        if source_type not in self.signals:
            self.signals[source_type] = []
        self.signals[source_type].append(signal)

        # Update counts
        if source_type not in self.total_signals:
            self.total_signals[source_type] = 0
        self.total_signals[source_type] += 1

    def get_all_signals(self) -> List[CompanySignal]:
        """Get all signals flattened into a single list."""
        all_signals = []
        for signal_list in self.signals.values():
            all_signals.extend(signal_list)
        return all_signals

    def get_cited_signals(self) -> List[CompanySignal]:
        """Get only signals that can be cited (public_url, user_provided)."""
        cited = []
        for source_type in ['public_url', 'user_provided']:
            cited.extend(self.signals.get(source_type, []))
        return cited


@dataclass
class SECMetadata:
    """
    SEC EDGAR company metadata.

    Stored in intel/sec/metadata.json.
    """
    sec_cik: str                        # 10-digit CIK (zero-padded)
    company_name: str                   # SEC-registered company name
    ticker: Optional[str] = None        # Stock ticker if public
    sic_code: Optional[str] = None      # SIC industry code
    sic_description: Optional[str] = None

    # Filing counts
    filing_counts: Dict[str, int] = field(default_factory=dict)  # {'10-K': 10, '10-Q': 40, ...}

    # Latest filing dates
    latest_10k_date: Optional[str] = None
    latest_10q_date: Optional[str] = None
    latest_8k_date: Optional[str] = None

    # Fetch metadata
    fetched_at: Optional[str] = None
    expires_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SECMetadata':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class SECFiling:
    """
    A single SEC filing entry.

    Stored in intel/sec/filings_index.json as a list.
    """
    accession_number: str               # Unique filing ID
    form_type: str                      # '10-K', '10-Q', '8-K', etc.
    filing_date: str                    # YYYY-MM-DD
    report_date: Optional[str] = None   # Period end date

    # Document info
    primary_document: Optional[str] = None  # Main document filename
    primary_doc_description: Optional[str] = None

    # URLs
    filing_url: Optional[str] = None    # URL to filing index
    document_url: Optional[str] = None  # URL to primary document

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SECFiling':
        """Create from dictionary."""
        return cls(**data)
