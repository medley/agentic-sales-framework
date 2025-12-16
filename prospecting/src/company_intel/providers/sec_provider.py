"""
SEC EDGAR Provider - Extract company intelligence from SEC filings

Provides:
- Company CIK lookup by name
- Filings index (10-K, 10-Q, 8-K)
- 10-K text extraction and caching
- Signal extraction from filing content

SEC EDGAR API Endpoints:
- Company search: https://efts.sec.gov/LATEST/search-index
- Submissions: https://data.sec.gov/submissions/CIK{cik}.json
- Filing documents: https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/
"""

import re
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from .base_provider import BaseIntelProvider, ProviderResult
from ..models import CompanySignal, SECMetadata, SECFiling

logger = logging.getLogger(__name__)


# Signal extraction patterns - safe, high-signal topics only
SEC_SIGNAL_PATTERNS = {
    'manufacturing_footprint': [
        (r'(?i)(?:we|the company|our company)\s+(?:operate|maintain|have|own)\s+(\d+)\s+(?:manufacturing|production)\s+(?:facilities|plants|sites)',
         'Company operates {0} manufacturing facilities'),
        (r'(?i)(?:manufacturing|production)\s+(?:facility|facilities|plant|plants|site|sites)\s+(?:located|in|at)\s+([A-Z][a-zA-Z\s,]+)',
         'Manufacturing facilities located in {0}'),
        (r'(?i)(?:opened|closed|acquired|expanded)\s+(?:a\s+)?(?:new\s+)?(?:manufacturing|production)\s+(?:facility|plant)',
         'Company has recently modified manufacturing footprint'),
    ],
    'restructuring': [
        (r'(?i)(?:restructuring|reorganization)\s+(?:plan|program|initiative|charges?)',
         'Company has restructuring/reorganization initiatives'),
        (r'(?i)workforce\s+reduction|headcount\s+reduction|reduction\s+in\s+force',
         'Company has workforce reduction initiatives'),
        (r'(?i)(?:consolidat(?:e|ing|ion))\s+(?:operations?|facilities?|manufacturing)',
         'Company is consolidating operations'),
    ],
    'quality_compliance': [
        (r'(?i)(?:FDA|Food and Drug Administration)\s+(?:warning\s+letter|form\s+483|483\s+observation|consent\s+decree)',
         'Company has FDA regulatory matters'),
        (r'(?i)(?:quality\s+system|GMP|cGMP|good\s+manufacturing\s+practice)\s+(?:remediation|improvement|enhancement|upgrade)',
         'Company has quality system improvement initiatives'),
        (r'(?i)(?:data\s+integrity|quality\s+assurance|quality\s+control)\s+(?:issue|concern|remediation|initiative)',
         'Company has data integrity/quality initiatives'),
        (r'(?i)(?:corrective\s+action|CAPA|deviation|non-?compliance)\s+(?:program|initiative|process)',
         'Company has corrective action programs'),
    ],
    'digital_transformation': [
        (r'(?i)(?:digital\s+transformation|digitalization|Industry\s+4\.0)',
         'Company has digital transformation initiatives'),
        (r'(?i)(?:ERP|enterprise\s+resource\s+planning)\s+(?:implementation|upgrade|modernization|system)',
         'Company has ERP initiatives'),
        (r'(?i)(?:MES|manufacturing\s+execution\s+system)\s+(?:implementation|upgrade|deployment)',
         'Company has MES initiatives'),
        (r'(?i)(?:QMS|quality\s+management\s+system)\s+(?:implementation|upgrade|modernization)',
         'Company has QMS initiatives'),
        (r'(?i)(?:automat(?:e|ion|ing))\s+(?:processes?|operations?|manufacturing|quality)',
         'Company has automation initiatives'),
    ],
    'supply_chain': [
        (r'(?i)(?:supply\s+chain)\s+(?:disruption|challenge|risk|constraint|issue)',
         'Company faces supply chain challenges'),
        (r'(?i)(?:single|sole)\s+source\s+(?:supplier|vendor|provider)',
         'Company has single-source supplier dependencies'),
        (r'(?i)(?:supplier|vendor)\s+(?:qualification|audit|management)\s+(?:program|process|initiative)',
         'Company has supplier management programs'),
    ],
}


class SECProvider(BaseIntelProvider):
    """
    SEC EDGAR provider for public company filings.

    Fetches 10-K, 10-Q, 8-K filings and extracts business signals
    about manufacturing, compliance, restructuring, and technology initiatives.
    """

    provider_name = "sec"
    metadata_ttl_days = 30      # Metadata cached for 30 days
    data_ttl_days = 14          # Filings index cached for 14 days

    # SEC API configuration
    SEC_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
    SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
    SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}"

    # User agent required by SEC (customize with your contact email)
    USER_AGENT = "Prospecting-Research-Bot/1.0 (your-email@example.com)"

    # Character limit for 10-K text
    TEXT_CHAR_LIMIT = 250000

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.USER_AGENT,
            'Accept': 'application/json'
        })

    def lookup_company(
        self,
        company_name: str,
        hints: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Look up company in SEC EDGAR by name or CIK.

        Args:
            company_name: Company name to search
            hints: Optional hints with 'sec_cik' if known

        Returns:
            SECMetadata dict or None if not found
        """
        hints = hints or {}

        # If we have a CIK hint, use it directly
        if hints.get('sec_cik'):
            cik = hints['sec_cik'].lstrip('0').zfill(10)
            return self._fetch_submissions_metadata(cik)

        # Search by company name
        return self._search_company_by_name(company_name)

    def _search_company_by_name(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Search SEC for company by name.

        Uses the SEC full-text search API to find company CIK.
        """
        # Clean company name for search
        search_name = re.sub(r'[^\w\s]', '', company_name)

        # Try direct company search via SEC company search
        search_url = f"https://www.sec.gov/cgi-bin/browse-edgar"
        params = {
            'company': search_name,
            'type': '10-K',
            'dateb': '',
            'owner': 'include',
            'count': '10',
            'action': 'getcompany',
            'output': 'atom'
        }

        try:
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()

            # Parse Atom feed to extract CIK
            soup = BeautifulSoup(response.text, 'xml')

            # Find first entry with company info
            entries = soup.find_all('entry')
            if not entries:
                self.logger.info(f"No SEC filings found for {company_name}")
                return None

            # Extract CIK from the entry link
            for entry in entries:
                link = entry.find('link', rel='alternate')
                if link and link.get('href'):
                    href = link.get('href')
                    # Extract CIK from URL pattern
                    cik_match = re.search(r'/cgi-bin/browse-edgar\?action=getcompany&CIK=(\d+)', href)
                    if cik_match:
                        cik = cik_match.group(1).zfill(10)
                        return self._fetch_submissions_metadata(cik)

            # Fallback: Try to get CIK from title
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                cik_match = re.search(r'CIK[:\s]*(\d+)', title_text)
                if cik_match:
                    cik = cik_match.group(1).zfill(10)
                    return self._fetch_submissions_metadata(cik)

            self.logger.info(f"Could not extract CIK for {company_name}")
            return None

        except requests.RequestException as e:
            self.logger.error(f"SEC company search failed: {e}")
            return None

    def _fetch_submissions_metadata(self, cik: str) -> Optional[Dict[str, Any]]:
        """
        Fetch company metadata from SEC submissions API.

        Args:
            cik: 10-digit CIK (zero-padded)

        Returns:
            SECMetadata dict
        """
        url = self.SEC_SUBMISSIONS_URL.format(cik=cik)

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Extract filing counts by type
            filings = data.get('filings', {}).get('recent', {})
            forms = filings.get('form', [])

            filing_counts = {}
            for form in forms:
                filing_counts[form] = filing_counts.get(form, 0) + 1

            # Find latest filing dates by type
            filing_dates = filings.get('filingDate', [])
            latest_10k_date = None
            latest_10q_date = None
            latest_8k_date = None

            for i, form in enumerate(forms):
                if i < len(filing_dates):
                    date = filing_dates[i]
                    if form == '10-K' and not latest_10k_date:
                        latest_10k_date = date
                    elif form == '10-Q' and not latest_10q_date:
                        latest_10q_date = date
                    elif form == '8-K' and not latest_8k_date:
                        latest_8k_date = date

            metadata = {
                'sec_cik': cik,
                'company_name': data.get('name', ''),
                'ticker': data.get('tickers', [''])[0] if data.get('tickers') else None,
                'sic_code': data.get('sic'),
                'sic_description': data.get('sicDescription'),
                'filing_counts': filing_counts,
                'latest_10k_date': latest_10k_date,
                'latest_10q_date': latest_10q_date,
                'latest_8k_date': latest_8k_date,
                'fetched_at': datetime.utcnow().isoformat() + 'Z',
                '_raw_filings': filings  # Keep for fetch_data
            }

            self.logger.info(f"Found SEC metadata for CIK {cik}: {data.get('name')}")
            return metadata

        except requests.RequestException as e:
            self.logger.error(f"SEC submissions fetch failed for CIK {cik}: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"SEC submissions JSON parse failed: {e}")
            return None

    def fetch_data(
        self,
        metadata: Dict[str, Any],
        cache: Any = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch 10-K filing text.

        Args:
            metadata: Metadata from lookup_company()
            cache: Optional cache to check for existing 10-K text

        Returns:
            Dict with filings_index and 10k_text
        """
        cik = metadata.get('sec_cik')
        if not cik:
            return None

        # Build filings index
        filings_index = self._build_filings_index(metadata)

        # Find latest 10-K
        latest_10k = None
        for filing in filings_index:
            if filing['form_type'] == '10-K':
                latest_10k = filing
                break

        if not latest_10k:
            self.logger.warning(f"No 10-K filing found for CIK {cik}")
            return {
                'filings_index': filings_index,
                '10k_text': None,
                '10k_filing': None
            }

        # Fetch 10-K text
        tenk_text = self._fetch_10k_text(cik, latest_10k)

        return {
            'filings_index': filings_index,
            '10k_text': tenk_text,
            '10k_filing': latest_10k
        }

    def _build_filings_index(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build filings index from metadata.

        Returns list of filing dicts sorted by date (most recent first).
        """
        raw_filings = metadata.get('_raw_filings', {})

        forms = raw_filings.get('form', [])
        dates = raw_filings.get('filingDate', [])
        accessions = raw_filings.get('accessionNumber', [])
        primary_docs = raw_filings.get('primaryDocument', [])
        descriptions = raw_filings.get('primaryDocDescription', [])

        filings = []
        cik = metadata.get('sec_cik', '').lstrip('0')

        for i in range(min(len(forms), len(dates), len(accessions))):
            form_type = forms[i]

            # Only include relevant filing types
            if form_type not in ['10-K', '10-Q', '8-K', '10-K/A', '10-Q/A']:
                continue

            accession = accessions[i].replace('-', '')
            primary_doc = primary_docs[i] if i < len(primary_docs) else None

            filing = {
                'accession_number': accessions[i],
                'form_type': form_type,
                'filing_date': dates[i],
                'primary_document': primary_doc,
                'primary_doc_description': descriptions[i] if i < len(descriptions) else None,
                'filing_url': f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/",
                'document_url': f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{primary_doc}" if primary_doc else None
            }
            filings.append(filing)

        # Sort by date descending
        filings.sort(key=lambda x: x['filing_date'], reverse=True)

        return filings[:50]  # Limit to 50 most recent

    def _fetch_10k_text(
        self,
        cik: str,
        filing: Dict[str, Any]
    ) -> Optional[str]:
        """
        Fetch and extract text from 10-K filing.

        Args:
            cik: Company CIK
            filing: Filing dict with accession_number and document info

        Returns:
            Plain text content (capped at TEXT_CHAR_LIMIT)
        """
        document_url = filing.get('document_url')
        if not document_url:
            # Try to construct from filing URL
            filing_url = filing.get('filing_url')
            primary_doc = filing.get('primary_document')
            if filing_url and primary_doc:
                document_url = f"{filing_url.rstrip('/')}/{primary_doc}"
            else:
                return None

        try:
            self.logger.info(f"Fetching 10-K from {document_url}")
            response = self.session.get(document_url, timeout=30)
            response.raise_for_status()

            # Parse HTML and extract text
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            text = soup.get_text(separator=' ')

            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()

            # Cap at limit
            if len(text) > self.TEXT_CHAR_LIMIT:
                text = text[:self.TEXT_CHAR_LIMIT]
                self.logger.info(f"10-K text truncated to {self.TEXT_CHAR_LIMIT} chars")

            return text

        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch 10-K: {e}")
            return None

    def extract_signals(
        self,
        data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[CompanySignal]:
        """
        Extract signals from 10-K text using regex patterns.

        Args:
            data: Data from fetch_data() with 10k_text
            metadata: Company metadata

        Returns:
            List of CompanySignal objects
        """
        signals = []
        signal_counter = 1

        tenk_text = data.get('10k_text')
        if not tenk_text:
            return signals

        tenk_filing = data.get('10k_filing', {})
        cik = metadata.get('sec_cik', '').lstrip('0')
        company_name = metadata.get('company_name', '')
        filing_date = tenk_filing.get('filing_date', '')
        filing_url = tenk_filing.get('filing_url', '')

        # Calculate recency
        recency_days = 180
        if filing_date:
            try:
                filing_dt = datetime.strptime(filing_date, '%Y-%m-%d')
                recency_days = (datetime.now() - filing_dt).days
            except ValueError:
                pass

        # Apply each pattern category
        for topic, patterns in SEC_SIGNAL_PATTERNS.items():
            for pattern_tuple in patterns:
                pattern = pattern_tuple[0]
                claim_template = pattern_tuple[1]

                matches = re.findall(pattern, tenk_text[:100000])  # Limit search scope
                if matches:
                    # Deduplicate matches
                    unique_matches = list(set(matches[:3]))  # Max 3 per pattern

                    for match in unique_matches:
                        # Format claim with match
                        if '{0}' in claim_template:
                            if isinstance(match, tuple):
                                claim = claim_template.format(*match)
                            else:
                                claim = claim_template.format(match)
                        else:
                            claim = claim_template

                        # Extract key terms from claim
                        key_terms = self._extract_key_terms(claim)

                        signal = CompanySignal(
                            signal_id=f"sec_10k_{topic}_{signal_counter:03d}",
                            claim=claim,
                            source_url=filing_url,
                            source_type='public_url',
                            citability='cited',
                            scope='company_level',
                            as_of_date=filing_date,
                            recency_days=recency_days,
                            key_terms=key_terms,
                            provider='sec',
                            filing_type='10-K',
                            confidence='medium',
                            topic=topic
                        )
                        signals.append(signal)
                        signal_counter += 1

                        # Limit signals per topic
                        if signal_counter > 20:
                            break

        # Deduplicate by claim
        seen_claims = set()
        unique_signals = []
        for signal in signals:
            claim_normalized = signal.claim.lower().strip()
            if claim_normalized not in seen_claims:
                seen_claims.add(claim_normalized)
                unique_signals.append(signal)

        self.logger.info(f"Extracted {len(unique_signals)} unique signals from 10-K")
        return unique_signals

    def _extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key terms from a claim for semantic validation.

        Args:
            text: Claim text

        Returns:
            List of key terms
        """
        # Split into words
        words = text.split()
        key_terms = []

        for word in words:
            # Clean punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            if not clean_word:
                continue

            # Keep significant words
            if (clean_word[0].isupper() and len(clean_word) > 2) or \
               clean_word.isdigit() or \
               (len(clean_word) > 6 and clean_word.isalpha()):
                key_terms.append(clean_word.lower())

        # Deduplicate and limit
        seen = set()
        unique_terms = []
        for term in key_terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)

        return unique_terms[:10]

    def get_filing_url(self, cik: str, form_type: str = '10-K') -> str:
        """
        Get URL to company's filing page on SEC website.

        Args:
            cik: Company CIK
            form_type: Filing type

        Returns:
            URL string
        """
        cik_clean = cik.lstrip('0')
        return f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik_clean}&type={form_type}"
