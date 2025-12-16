"""
Perplexity API Client for Company Research

Standalone client for researching companies using Perplexity's AI-powered search.
Optimized for discovering quality, compliance, and business challenges relevant
to life sciences manufacturing companies.

IMPORTANT: This client extracts REAL citations from Perplexity responses.
- Citations are bracketed numbers like [1], [2] in the response text
- Source URLs are returned in the API response 'citations' field
- Only claims with real source URLs should be used for personalization

Usage:
    from perplexity_client import PerplexityClient

    client = PerplexityClient(api_key="your-api-key")
    research = client.research_company("Acme Corp", "VP of Quality")

    print(research['company_news'])
    print(research['cited_claims'])  # Claims with real source URLs
    print(research['citations'])      # Full citation list
"""
import os
import re
import time
import logging
from typing import Dict, Optional, List, Tuple
import requests

logger = logging.getLogger(__name__)


class PerplexityClient:
    """
    Client for Perplexity API focused on company research

    Features:
    - Company news and recent developments
    - Quality/compliance challenges
    - Role-specific pain points
    - Strategic initiatives
    - Automatic rate limiting
    - Error handling and retries
    """

    def __init__(self, api_key: Optional[str] = None, rate_limit_seconds: float = 0.2):
        """
        Initialize Perplexity API client

        Args:
            api_key: Perplexity API key (defaults to PERPLEXITY_API_KEY env var)
            rate_limit_seconds: Minimum seconds between API calls (default: 0.2)
        """
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("Perplexity API key must be provided or set in PERPLEXITY_API_KEY environment variable")

        self.base_url = 'https://api.perplexity.ai/chat/completions'
        self.model = 'sonar'  # Llama 3.3 70B-based, optimized for factuality
        self.temperature = 0.2  # Low temperature for factual accuracy

        # Rate limiting
        self.last_api_call = 0
        self.min_api_interval = rate_limit_seconds

        logger.info("PerplexityClient initialized")

    def research_company(
        self,
        company_name: str,
        contact_role: Optional[str] = None,
        max_retries: int = 2
    ) -> Dict:
        """
        Research a company for prospecting purposes

        Returns comprehensive research including:
        - Recent company news (last 3 months)
        - Business challenges (quality/manufacturing focus)
        - Role-specific pain points
        - Recent strategic initiatives

        Args:
            company_name: Name of the company to research
            contact_role: Job title/role of the prospect (optional, improves relevance)
            max_retries: Number of retries on failure (default: 2)

        Returns:
            Dict with keys:
                - company_news: Recent developments and news
                - business_challenges: Quality/compliance challenges
                - role_specific_pains: Pain points for the given role
                - recent_initiatives: Strategic initiatives and projects
                - summary: Brief summary for quick reference

        Example:
            >>> client = PerplexityClient()
            >>> research = client.research_company("Acme Corp", "VP of Quality")
            >>> print(research['business_challenges'])
        """
        logger.info(f"Researching company: {company_name} (role: {contact_role})")

        # Build comprehensive research query
        query = self._build_research_query(company_name, contact_role)

        # Execute search with retries
        for attempt in range(max_retries + 1):
            try:
                response_text, citations = self._search_perplexity(
                    query=query,
                    max_tokens=800,
                    system_prompt=self._get_system_prompt()
                )

                if response_text:
                    # Parse and structure the response
                    research_data = self._parse_research_response(
                        response_text, company_name, contact_role, citations
                    )
                    logger.info(f"Successfully researched {company_name}")
                    return research_data

            except Exception as e:
                logger.warning(f"Research attempt {attempt + 1} failed for {company_name}: {e}")
                if attempt < max_retries:
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    logger.error(f"All research attempts failed for {company_name}")
                    return self._get_fallback_research(company_name, contact_role)

        return self._get_fallback_research(company_name, contact_role)

    def get_pain_insights(
        self,
        company_name: str,
        contact_role: Optional[str] = None,
        focus_areas: Optional[list] = None
    ) -> str:
        """
        Get concise pain point insights for email personalization

        This is a simplified version of research_company() that returns
        a 1-2 sentence summary optimized for email use.

        Args:
            company_name: Name of the company
            contact_role: Job title/role of the prospect
            focus_areas: List of areas to focus on (e.g., ['FDA compliance', 'quality'])

        Returns:
            String with concise pain insight (1-2 sentences)

        Example:
            >>> client = PerplexityClient()
            >>> insight = client.get_pain_insights("Acme Corp", "Quality Director")
            >>> print(f"struggling with {insight}")
        """
        logger.info(f"Getting pain insights for {company_name}")

        # Build focused query for pain points
        query = self._build_pain_query(company_name, contact_role, focus_areas)

        try:
            response_text, citations = self._search_perplexity(
                query=query,
                max_tokens=150,
                system_prompt='You are a life sciences industry analyst. Provide concise, factual insights about quality and compliance challenges.'
            )

            if response_text:
                # Clean up the response
                pain_insight = response_text.strip()
                if len(pain_insight) > 200:
                    pain_insight = pain_insight[:197] + '...'

                logger.info(f"Got pain insight for {company_name}")
                return pain_insight

        except Exception as e:
            logger.error(f"Pain insight exception for {company_name}: {e}")

        return 'quality and compliance challenges'

    def _search_perplexity(
        self,
        query: str,
        max_tokens: int = 500,
        system_prompt: Optional[str] = None
    ) -> Tuple[Optional[str], List[str]]:
        """
        Execute a search query using Perplexity API

        Args:
            query: The search query
            max_tokens: Maximum tokens in response
            system_prompt: System prompt for the model (optional)

        Returns:
            Tuple of (response_text, citations_list) or (None, []) if failed
            Citations are real URLs extracted from Perplexity's response
        """
        # Rate limiting
        self._rate_limit()

        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        messages.append({
            'role': 'user',
            'content': query
        })

        try:
            response = requests.post(
                self.base_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': self.model,
                    'messages': messages,
                    'max_tokens': max_tokens,
                    'temperature': self.temperature
                },
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']

                # Extract citations from Perplexity response
                # Perplexity returns citations in response metadata
                citations = data.get('citations', [])

                # If citations not in top-level, check in message
                if not citations:
                    message = data['choices'][0].get('message', {})
                    citations = message.get('citations', [])

                logger.info(f"Received response with {len(citations)} citations")
                return content, citations

            elif response.status_code == 429:
                logger.warning("Perplexity API rate limit exceeded")
                raise Exception("Rate limit exceeded")

            elif response.status_code == 401:
                logger.error("Perplexity API authentication failed")
                raise Exception("Invalid API key")

            else:
                logger.warning(f"Perplexity API error: {response.status_code}")
                logger.debug(f"Response: {response.text}")
                return None, []

        except requests.exceptions.Timeout:
            logger.error("Perplexity API timeout")
            raise Exception("API timeout")

        except requests.exceptions.RequestException as e:
            logger.error(f"Perplexity API request exception: {e}")
            raise Exception(f"Request failed: {e}")

    def _extract_cited_claims(
        self,
        response_text: str,
        citations: List[str]
    ) -> List[Dict]:
        """
        Extract claims from response text that have citation references.

        Perplexity uses bracketed numbers like [1], [2] to reference citations.
        This method extracts sentences/bullet points that contain these references
        and maps them to the actual source URLs.

        Args:
            response_text: The full response text with citation markers
            citations: List of citation URLs (index 0 = [1], index 1 = [2], etc.)

        Returns:
            List of cited claims with structure:
            {
                'claim': str,           # The text of the claim
                'source_url': str,      # Real URL from citations
                'citation_number': int, # Which citation number was used
                'source_type': 'public_url'
            }
        """
        cited_claims = []

        if not citations:
            logger.warning("No citations available to extract claims")
            return cited_claims

        # Find all citation references in text [1], [2], etc.
        # and extract the surrounding sentence/bullet point

        # Split into lines/bullets for easier processing
        lines = response_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Find citation markers in this line
            citation_matches = re.findall(r'\[(\d+)\]', line)

            if citation_matches:
                # Get unique citation numbers
                citation_nums = list(set(int(m) for m in citation_matches))

                # Clean the claim text (remove citation markers for readability)
                claim_text = re.sub(r'\[\d+\]', '', line).strip()
                claim_text = claim_text.lstrip('-*•').strip()

                # Skip if claim is too short or just a header
                if len(claim_text) < 20 or claim_text.endswith(':'):
                    continue

                # Map to actual URLs (citation [1] = index 0)
                for cite_num in citation_nums:
                    url_index = cite_num - 1  # [1] maps to index 0
                    if 0 <= url_index < len(citations):
                        source_url = citations[url_index]

                        # Validate it's a real URL
                        if source_url and source_url.startswith('http'):
                            cited_claims.append({
                                'claim': claim_text,
                                'source_url': source_url,
                                'citation_number': cite_num,
                                'source_type': 'public_url'
                            })
                            logger.debug(f"Extracted cited claim: {claim_text[:50]}... -> {source_url}")
                        else:
                            logger.warning(f"Invalid URL for citation [{cite_num}]: {source_url}")

        logger.info(f"Extracted {len(cited_claims)} cited claims with real URLs")
        return cited_claims

    def _build_research_query(self, company_name: str, contact_role: Optional[str] = None) -> str:
        """Build comprehensive research query"""

        role_context = f" paying special attention to challenges relevant to a {contact_role}" if contact_role else ""

        query = f"""Research {company_name} for B2B prospecting{role_context}. Provide:

1. RECENT NEWS (last 3 months):
   - Major announcements, expansions, acquisitions
   - Leadership changes
   - Product launches or regulatory approvals
   - Financial results or funding

2. QUALITY & MANUFACTURING CHALLENGES:
   - FDA observations, warning letters, or recalls
   - Quality system modernization needs
   - Compliance or regulatory challenges
   - Manufacturing scale-up or capacity issues
   - Validation backlogs

3. ROLE-SPECIFIC PAIN POINTS{f' for {contact_role}' if contact_role else ''}:
   - Day-to-day operational challenges
   - Technology or process gaps
   - Resource constraints
   - Regulatory pressures

4. STRATEGIC INITIATIVES:
   - Digital transformation projects
   - Quality system upgrades
   - Process improvement programs
   - Geographic expansion plans

Format as clear sections with bullet points. Focus on factual, verifiable information."""

        return query

    def _build_pain_query(
        self,
        company_name: str,
        contact_role: Optional[str] = None,
        focus_areas: Optional[list] = None
    ) -> str:
        """Build focused query for pain points"""

        role_context = f" for a {contact_role}" if contact_role else ""

        focus_list = focus_areas or [
            'FDA observations',
            'recalls',
            'quality system modernization',
            'validation backlogs',
            'digital transformation in quality',
            'scaling challenges',
            'compliance issues'
        ]
        focus_text = ', '.join(focus_list)

        query = f"""What are the current quality, compliance, or regulatory challenges facing {company_name}{role_context}?

Focus on: {focus_text}

Provide a concise 1-2 sentence summary of their most pressing quality/compliance pain point."""

        return query

    def _get_system_prompt(self) -> str:
        """Get system prompt for research queries"""
        return """You are a B2B research analyst specializing in life sciences and manufacturing companies.

Your role is to provide accurate, factual, and actionable intelligence for sales prospecting.
Focus on recent developments, business challenges, and strategic initiatives.
Be specific and cite timeframes when available.
Organize information clearly with headers and bullet points."""

    def _parse_research_response(
        self,
        response_text: str,
        company_name: str,
        contact_role: Optional[str] = None,
        citations: Optional[List[str]] = None
    ) -> Dict:
        """
        Parse Perplexity response into structured research data

        Attempts to extract sections based on headers, falls back to full text.
        CRITICAL: Extracts cited claims with real source URLs for signal verification.

        Args:
            response_text: Raw response from Perplexity
            company_name: Company being researched
            contact_role: Role of prospect (optional)
            citations: List of citation URLs from Perplexity API response

        Returns:
            Research dict with cited_claims containing only verifiable data
        """
        citations = citations or []

        # Extract cited claims FIRST - these are the only claims with real sources
        cited_claims = self._extract_cited_claims(response_text, citations)

        # CITATION FORMAT VALIDATION (Fix #3)
        # Check if Perplexity returned content but no citations were extracted
        citation_warning = None
        confidence_downgrade = False

        if response_text and len(response_text) > 100:  # Substantial response
            if len(citations) == 0:
                citation_warning = (
                    "CITATION_FORMAT_WARNING: Perplexity returned content but no citations "
                    "were found in API response. API response format may have changed. "
                    "Confidence mode will be downgraded to 'generic'."
                )
                confidence_downgrade = True
                logger.warning(citation_warning)

            elif len(cited_claims) == 0 and len(citations) > 0:
                citation_warning = (
                    "CITATION_EXTRACTION_WARNING: Perplexity returned citations but no "
                    "claims could be mapped to them. Citation markers [1], [2] may not "
                    "be present in response text. Using generic confidence."
                )
                confidence_downgrade = True
                logger.warning(citation_warning)

            elif len(cited_claims) < len(citations) * 0.3:  # Less than 30% citation usage
                citation_warning = (
                    f"CITATION_COVERAGE_WARNING: Only {len(cited_claims)} claims extracted "
                    f"from {len(citations)} available citations. Response may not be "
                    f"well-cited. Consider lowering confidence."
                )
                logger.warning(citation_warning)

        research = {
            'company_name': company_name,
            'contact_role': contact_role,
            'company_news': '',
            'business_challenges': '',
            'role_specific_pains': '',
            'recent_initiatives': '',
            'summary': '',
            'raw_response': response_text,
            # Real citations and cited claims
            'citations': citations,  # Full list of source URLs
            'cited_claims': cited_claims,  # Claims with source_url and source_type
            'citation_count': len(citations),
            'cited_claim_count': len(cited_claims),
            # Citation validation status (Fix #3)
            'citation_warning': citation_warning,
            'citation_confidence_downgrade': confidence_downgrade,
            'citation_status': 'ok' if not citation_warning else 'warning'
        }

        # Try to extract sections
        text = response_text

        # Extract company news
        if 'recent news' in text.lower() or '1.' in text:
            research['company_news'] = self._extract_section(
                text,
                ['recent news', 'news', '1.'],
                ['quality', 'manufacturing', 'challenges', '2.', 'role-specific', '3.']
            )

        # Extract business challenges
        if 'quality' in text.lower() or 'manufacturing' in text.lower() or '2.' in text:
            research['business_challenges'] = self._extract_section(
                text,
                ['quality', 'manufacturing challenges', 'challenges', '2.'],
                ['role-specific', 'pain points', '3.', 'strategic', '4.']
            )

        # Extract role-specific pains
        if 'role-specific' in text.lower() or 'pain points' in text.lower() or '3.' in text:
            research['role_specific_pains'] = self._extract_section(
                text,
                ['role-specific', 'pain points', '3.'],
                ['strategic', 'initiatives', '4.']
            )

        # Extract strategic initiatives
        if 'strategic' in text.lower() or 'initiatives' in text.lower() or '4.' in text:
            research['recent_initiatives'] = self._extract_section(
                text,
                ['strategic', 'initiatives', '4.'],
                []
            )

        # Create summary (first 2-3 sentences)
        sentences = text.split('.')
        summary_sentences = [s.strip() for s in sentences[:3] if s.strip()]
        research['summary'] = '. '.join(summary_sentences) + '.'

        # If sections are empty, use the full response
        if not any([research['company_news'], research['business_challenges'],
                   research['role_specific_pains'], research['recent_initiatives']]):
            research['company_news'] = text
            research['summary'] = text[:200] + '...' if len(text) > 200 else text

        return research

    def _extract_section(self, text: str, start_markers: list, end_markers: list) -> str:
        """
        Extract a section of text between markers

        Args:
            text: Full text to search
            start_markers: List of possible section start markers (case-insensitive)
            end_markers: List of possible section end markers (case-insensitive)

        Returns:
            Extracted section text
        """
        text_lower = text.lower()

        # Find start position
        start_pos = -1
        for marker in start_markers:
            pos = text_lower.find(marker.lower())
            if pos != -1:
                start_pos = pos
                break

        if start_pos == -1:
            return ''

        # Find end position
        end_pos = len(text)
        if end_markers:
            for marker in end_markers:
                pos = text_lower.find(marker.lower(), start_pos + 1)
                if pos != -1 and pos < end_pos:
                    end_pos = pos
                    break

        # Extract and clean
        section = text[start_pos:end_pos].strip()

        # Remove the header line if it's there
        lines = section.split('\n')
        if len(lines) > 1 and any(marker.lower() in lines[0].lower() for marker in start_markers):
            section = '\n'.join(lines[1:]).strip()

        return section

    def _get_fallback_research(self, company_name: str, contact_role: Optional[str] = None) -> Dict:
        """
        Return fallback research data when API fails
        """
        return {
            'company_name': company_name,
            'contact_role': contact_role,
            'company_news': 'Unable to retrieve recent news at this time.',
            'business_challenges': 'Quality and compliance challenges common in life sciences manufacturing.',
            'role_specific_pains': 'Operational efficiency and regulatory compliance.',
            'recent_initiatives': 'Digital transformation and process improvement.',
            'summary': f'Research data for {company_name} is temporarily unavailable.',
            'raw_response': '',
            'error': True
        }

    def _rate_limit(self):
        """
        Enforce rate limiting between API calls

        Ensures minimum interval between requests to avoid hitting API limits
        """
        elapsed = time.time() - self.last_api_call
        if elapsed < self.min_api_interval:
            sleep_time = self.min_api_interval - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_api_call = time.time()


# Convenience function for quick usage
def research_company(company_name: str, contact_role: Optional[str] = None, api_key: Optional[str] = None) -> Dict:
    """
    Convenience function for one-off company research

    Args:
        company_name: Company to research
        contact_role: Role of the contact (optional)
        api_key: Perplexity API key (optional, uses env var if not provided)

    Returns:
        Research data dictionary

    Example:
        >>> research = research_company("Acme Corp", "VP Quality")
        >>> print(research['business_challenges'])
    """
    client = PerplexityClient(api_key=api_key)
    return client.research_company(company_name, contact_role)


if __name__ == '__main__':
    # Test the client
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "="*60)
    print("Perplexity Client Test")
    print("="*60 + "\n")

    try:
        client = PerplexityClient()
        print("✓ Client initialized successfully\n")

        # Test company research (use any public company for testing)
        test_company = "Acme Corp"
        test_role = "VP of Quality"

        print(f"Researching: {test_company}")
        print(f"Contact Role: {test_role}\n")

        research = client.research_company(test_company, test_role)

        print("\nRESEARCH RESULTS")
        print("-" * 60)

        print("\n📰 COMPANY NEWS:")
        print(research['company_news'][:300] + "..." if len(research['company_news']) > 300 else research['company_news'])

        print("\n⚠️  BUSINESS CHALLENGES:")
        print(research['business_challenges'][:300] + "..." if len(research['business_challenges']) > 300 else research['business_challenges'])

        print("\n🎯 ROLE-SPECIFIC PAINS:")
        print(research['role_specific_pains'][:300] + "..." if len(research['role_specific_pains']) > 300 else research['role_specific_pains'])

        print("\n🚀 RECENT INITIATIVES:")
        print(research['recent_initiatives'][:300] + "..." if len(research['recent_initiatives']) > 300 else research['recent_initiatives'])

        print("\n" + "="*60)
        print("✓ Test completed successfully!")
        print("="*60 + "\n")

        # Test pain insights
        print("\nTesting pain insights method...\n")
        pain_insight = client.get_pain_insights(test_company, test_role)
        print(f"Pain Insight: {pain_insight}\n")

    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease set PERPLEXITY_API_KEY environment variable:")
        print("  export PERPLEXITY_API_KEY='your-api-key'")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
