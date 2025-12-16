"""
WebFetch Client - Fast website research for company intel

Fetches company websites in parallel to extract:
- Products/services
- Industries served
- Recent news
- Regulatory context
- Tech stack hints

Usage:
    from webfetch_client import WebFetchClient

    client = WebFetchClient()
    data = client.research_company("Acme Corp", "acme.com")
"""

import logging
import requests
from typing import Dict, Optional, Any
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebFetchClient:
    """
    Fast website data extraction for company research.
    """

    def __init__(self, timeout_seconds: int = 5):
        """
        Initialize WebFetch client.

        Args:
            timeout_seconds: HTTP request timeout
        """
        self.timeout = timeout_seconds
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def research_company(
        self,
        company_name: str,
        website: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Research company via website data extraction.

        Args:
            company_name: Company name
            website: Company website URL (if known)

        Returns:
            {
                'company_description': str,
                'industries': [str],
                'products': [str],
                'recent_news': [str],
                'regulatory_keywords': [str],
                'tech_stack_hints': [str]
            }
            or None if fetch fails
        """
        if not website:
            website = self._guess_website(company_name)

        try:
            logger.info(f"Fetching website: {website}")
            response = requests.get(
                website,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            result = {
                'company_description': self._extract_description(soup),
                'industries': self._extract_industries(soup),
                'products': self._extract_products(soup),
                'recent_news': self._extract_news(soup),
                'regulatory_keywords': self._extract_regulatory_keywords(soup),
                'tech_stack_hints': self._extract_tech_hints(soup),
                'source_url': website
            }

            logger.info(f"Successfully fetched data from {website}")
            return result

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {website}")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch {website}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {website}: {str(e)}")
            return None

    def _guess_website(self, company_name: str) -> str:
        """
        Guess company website from name.

        Args:
            company_name: Company name

        Returns:
            Guessed URL (e.g., https://www.acme.com)
        """
        # Remove common suffixes
        clean_name = company_name.lower()
        for suffix in [' inc', ' inc.', ' llc', ' ltd', ' corp', ' corporation', ' company', ' co']:
            clean_name = clean_name.replace(suffix, '')

        # Remove special characters
        clean_name = re.sub(r'[^a-z0-9]', '', clean_name)

        return f"https://www.{clean_name}.com"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract company description from meta tags or about section."""
        # Try meta description
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta['content']

        # Try og:description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content']

        # Try first paragraph in about/company section
        about_section = soup.find(['section', 'div'], class_=re.compile(r'about|company', re.I))
        if about_section:
            p = about_section.find('p')
            if p:
                return p.get_text(strip=True)

        return "No description found"

    def _extract_industries(self, soup: BeautifulSoup) -> list:
        """Extract industries served from page content."""
        industries = []
        text = soup.get_text().lower()

        # Common industry keywords
        industry_keywords = {
            'pharmaceutical': ['pharma', 'pharmaceutical', 'drug'],
            'biotech': ['biotech', 'biotechnology'],
            'medical device': ['medical device', 'medtech'],
            'aerospace': ['aerospace', 'aviation', 'defense'],
            'automotive': ['automotive', 'auto'],
            'manufacturing': ['manufacturing', 'factory'],
            'healthcare': ['healthcare', 'hospital'],
            'life sciences': ['life science']
        }

        for industry, keywords in industry_keywords.items():
            if any(keyword in text for keyword in keywords):
                industries.append(industry)

        return industries[:5]  # Limit to top 5

    def _extract_products(self, soup: BeautifulSoup) -> list:
        """Extract products/services from page."""
        products = []

        # Look for product sections
        product_sections = soup.find_all(['section', 'div'], class_=re.compile(r'product|solution|service', re.I))

        for section in product_sections[:3]:  # Limit to first 3 sections
            # Extract headings
            headings = section.find_all(['h2', 'h3', 'h4'])
            for h in headings:
                text = h.get_text(strip=True)
                if text and len(text) < 100:
                    products.append(text)

        return products[:5]  # Limit to top 5

    def _extract_news(self, soup: BeautifulSoup) -> list:
        """Extract recent news or announcements."""
        news = []

        # Look for news/press sections
        news_sections = soup.find_all(['section', 'div'], class_=re.compile(r'news|press|announcement', re.I))

        for section in news_sections[:2]:
            # Extract article titles or links
            articles = section.find_all(['article', 'a', 'h3'])
            for article in articles[:5]:
                text = article.get_text(strip=True)
                if text and 10 < len(text) < 200:
                    news.append(text)

        return news[:5]  # Limit to top 5

    def _extract_regulatory_keywords(self, soup: BeautifulSoup) -> list:
        """Extract regulatory/compliance keywords."""
        keywords = []
        text = soup.get_text().lower()

        regulatory_terms = [
            'fda', '21 cfr', 'iso 13485', 'iso 9001', 'as9100',
            'gmp', 'cgmp', 'quality management', 'compliance',
            'audit', 'regulatory', 'validation', 'traceability'
        ]

        for term in regulatory_terms:
            if term in text:
                keywords.append(term.upper())

        return list(set(keywords))  # Remove duplicates

    def _extract_tech_hints(self, soup: BeautifulSoup) -> list:
        """Extract technology stack hints from page source."""
        hints = []

        # Check for common platforms/tools
        html = str(soup)

        tech_patterns = {
            'Salesforce': r'salesforce',
            'HubSpot': r'hubspot',
            'Google Analytics': r'google-analytics|gtag',
            'WordPress': r'wp-content|wordpress',
            'Shopify': r'shopify',
            'React': r'react',
            'Angular': r'angular',
            'Vue': r'vue\.js'
        }

        for tech, pattern in tech_patterns.items():
            if re.search(pattern, html, re.I):
                hints.append(tech)

        return hints


class WebFetchError(Exception):
    """Base exception for WebFetch errors."""
    pass
