#!/usr/bin/env python3
"""
ZoomInfo API Client for Prospecting Module

This client provides methods to search for contacts and enrich company data
using the ZoomInfo API with PKI authentication (username + client_id + private key).

Example usage:
    from zoominfo_jwt_manager import ZoomInfoJWTManager

    jwt_manager = ZoomInfoJWTManager()
    client = ZoomInfoClient(jwt_manager)

    # Search for a contact
    contact = client.search_contact(
        name="John Smith",
        company_name="Acme Corp"
    )

    # Enrich company data
    if contact and contact.get('company_id'):
        company_data = client.enrich_company(contact['company_id'])
"""

import logging
import time
from typing import Optional, Dict, Any, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .zoominfo_jwt_manager import ZoomInfoJWTManager


# Configure module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add console handler if not already configured
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


class ZoomInfoAPIError(Exception):
    """Base exception for ZoomInfo API errors"""
    pass


class ZoomInfoRateLimitError(ZoomInfoAPIError):
    """Raised when API rate limit is exceeded"""
    pass


class ZoomInfoAuthenticationError(ZoomInfoAPIError):
    """Raised when authentication fails"""
    pass


class ZoomInfoClient:
    """
    Client for interacting with the ZoomInfo API using PKI authentication.

    This client provides methods to search for contacts and enrich company data.
    It handles JWT token authentication, rate limiting, retries, and error handling.

    Attributes:
        jwt_manager: ZoomInfoJWTManager instance for JWT token generation
        base_url: Base URL for ZoomInfo API (default: https://api.zoominfo.com)
        session: Configured requests session with retries
        timeout: Request timeout in seconds (default: 30)
    """

    def __init__(
        self,
        jwt_manager: Optional[ZoomInfoJWTManager] = None,
        base_url: str = "https://api.zoominfo.com",
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_delay: float = 0.6  # 100 req/min = 0.6s between calls
    ):
        """
        Initialize the ZoomInfo API client.

        Args:
            jwt_manager: ZoomInfoJWTManager instance (if None, will create new one)
            base_url: Base URL for ZoomInfo API (default: https://api.zoominfo.com)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for failed requests (default: 3)
            rate_limit_delay: Minimum seconds between API calls (default: 0.6)

        Raises:
            ValueError: If JWT manager cannot be initialized
        """
        # Initialize JWT manager
        if jwt_manager is None:
            try:
                self.jwt_manager = ZoomInfoJWTManager()
                logger.info("Initialized new ZoomInfoJWTManager")
            except Exception as e:
                logger.error(f"Failed to initialize JWT manager: {e}")
                raise ValueError(f"Cannot initialize ZoomInfo client: {e}")
        else:
            self.jwt_manager = jwt_manager

        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0

        # Configure session with retry logic
        self.session = requests.Session()

        # Retry strategy: retry on 500, 502, 503, 504
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,  # 1s, 2s, 4s delays
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        logger.info(f"ZoomInfo client initialized with base URL: {self.base_url}")

    def _wait_for_rate_limit(self):
        """Enforce rate limiting between API calls (100 req/min)."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - elapsed
            logger.debug(f"Rate limit: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _get_headers(self) -> Dict[str, str]:
        """
        Get request headers with JWT token.

        Returns:
            Headers dict with Authorization bearer token

        Raises:
            ZoomInfoAuthenticationError: If token generation fails
        """
        try:
            token = self.jwt_manager.get_token()
            return {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        except Exception as e:
            logger.error(f"Failed to get JWT token: {e}")
            raise ZoomInfoAuthenticationError(f"Authentication failed: {e}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request to ZoomInfo API with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/search/contact')
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object

        Raises:
            ZoomInfoRateLimitError: If rate limit exceeded
            ZoomInfoAuthenticationError: If authentication fails
            ZoomInfoAPIError: For other API errors
        """
        self._wait_for_rate_limit()

        url = f"{self.base_url}{endpoint}"

        try:
            # Get fresh headers with JWT token
            headers = self._get_headers()

            # Merge with any additional headers
            if 'headers' in kwargs:
                headers.update(kwargs['headers'])
            kwargs['headers'] = headers

            # Set timeout if not specified
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout

            logger.debug(f"Making {method} request to {url}")

            response = self.session.request(method, url, **kwargs)

            # Check for specific error codes
            if response.status_code == 429:
                logger.warning(f"Rate limit exceeded: {response.text}")
                raise ZoomInfoRateLimitError("API rate limit exceeded")

            elif response.status_code in [401, 403]:
                logger.error(f"Authentication failed: {response.text}")
                # Invalidate cached token and try again once
                self.jwt_manager.invalidate_token()
                raise ZoomInfoAuthenticationError(f"Authentication failed: {response.status_code}")

            elif response.status_code >= 400:
                logger.error(f"API error {response.status_code}: {response.text}")
                raise ZoomInfoAPIError(f"API error {response.status_code}: {response.text}")

            return response

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {self.timeout}s: {url}")
            return None

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return None

        except (ZoomInfoRateLimitError, ZoomInfoAuthenticationError, ZoomInfoAPIError):
            raise  # Re-raise our custom exceptions

        except Exception as e:
            logger.error(f"Unexpected error in API request: {e}", exc_info=True)
            raise ZoomInfoAPIError(f"Unexpected error: {e}")

    def search_contact(
        self,
        name: str,
        company_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Search for a contact by name and company.

        Args:
            name: Contact's full name (e.g., "John Smith")
            company_name: Company name (e.g., "Acme Corp")

        Returns:
            Contact information dict with keys:
                - contact_id: ZoomInfo contact ID
                - first_name: Contact's first name
                - last_name: Contact's last name
                - title: Job title
                - company_id: ZoomInfo company ID
                - company_name: Company name
            Or None if contact not found or request fails

            Note: Email and phone require premium ZoomInfo license

        Raises:
            ZoomInfoRateLimitError: If rate limit exceeded
            ZoomInfoAuthenticationError: If authentication fails
            ZoomInfoAPIError: For other API errors
        """
        # Parse name (handle "First Last" or "Last, First")
        first_name, last_name = self._parse_name(name)

        logger.info(f"Searching for contact: {first_name} {last_name} at {company_name}")

        # Step 1: First search for company to get company ID
        company_payload = {
            "companyName": company_name,
            "outputFields": ["id", "name"]
        }

        try:
            company_response = self._make_request('POST', '/search/company', json=company_payload)
            if not company_response or not company_response.json().get('data'):
                logger.warning(f"Company not found: {company_name}")
                return None

            company_id = str(company_response.json()['data'][0]['id'])
            logger.info(f"Found company ID: {company_id}")
        except Exception as e:
            logger.error(f"Error searching for company {company_name}: {e}")
            return None

        # Step 2: Search for contact using company ID
        # Note: Email and phone fields require premium license
        payload = {
            "firstName": first_name,
            "lastName": last_name,
            "companyId": company_id,
            "outputFields": [
                "id",
                "firstName",
                "lastName",
                "jobTitle",
                "companyId",
                "companyName"
            ]
        }

        try:
            response = self._make_request('POST', '/search/contact', json=payload)

            if not response:
                logger.warning(f"No response from contact search for {name} at {company_name}")
                return None

            data = response.json()

            # Extract first match if available
            if data.get('data') and len(data['data']) > 0:
                contact = data['data'][0]
                result = {
                    'contact_id': contact.get('id'),
                    'first_name': contact.get('firstName'),
                    'last_name': contact.get('lastName'),
                    'title': contact.get('jobTitle'),
                    'company_id': contact.get('companyId'),
                    'company_name': contact.get('companyName')
                }

                logger.info(f"Found contact: {result['first_name']} {result['last_name']}, {result['title']} at {result['company_name']}")
                return result
            else:
                logger.warning(f"No contact found for {name} at {company_name}")
                return None

        except Exception as e:
            logger.error(f"Error searching for contact {name}: {e}")
            return None

    def enrich_company(self, company_id: str) -> Dict[str, Any]:
        """
        Enrich company data with additional business intelligence.

        Args:
            company_id: ZoomInfo company ID

        Returns:
            Company data dict with keys:
                - revenue: Annual revenue range
                - employee_count: Number of employees
                - industry: Primary industry
                - tech_stack: List of technologies used
                - intent_signals: List of buying intent signals

        Raises:
            ZoomInfoRateLimitError: If rate limit exceeded
            ZoomInfoAuthenticationError: If authentication fails
            ZoomInfoAPIError: For other API errors
        """
        logger.info(f"Enriching company data for ID: {company_id}")

        payload = {
            "id": company_id,
            "outputFields": [
                "revenue",
                "employeeCount",
                "primaryIndustry",
                "techInstalledCategories",
                "recentNews"
            ]
        }

        try:
            response = self._make_request('POST', '/enrich/company', json=payload)

            if not response:
                logger.warning(f"No response from company enrichment for ID: {company_id}")
                return {}

            data = response.json()

            if data.get('data'):
                company = data['data']
                result = {
                    'revenue': company.get('revenue'),
                    'employee_count': company.get('employeeCount'),
                    'industry': company.get('primaryIndustry'),
                    'tech_stack': company.get('techInstalledCategories', []),
                    'intent_signals': []  # Placeholder for intent data
                }

                logger.info(f"Company enrichment complete: {result['industry']}, {result['employee_count']} employees")
                return result
            else:
                logger.warning(f"No company data found for ID: {company_id}")
                return {}

        except Exception as e:
            logger.error(f"Error enriching company {company_id}: {e}")
            return {}

    def search_contacts_by_role(
        self,
        role_keywords: str,
        company_name: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for contacts by job title/role at a company.

        Args:
            role_keywords: Job title keywords (e.g., "quality director", "vp operations")
            company_name: Company name (e.g., "Ultradent Products")
            limit: Max contacts to return (default: 5)

        Returns:
            List of contact dicts, each with:
                - contact_id: ZoomInfo contact ID
                - first_name, last_name: Contact name
                - title: Full job title
                - management_level: List of levels (["Director"], ["VP"], etc.)
                - job_function: List of dicts with name and department
                - location: String with "City, State"
                - company_id, company_name: Company identifiers

        Raises:
            ZoomInfoRateLimitError: If rate limit exceeded
            ZoomInfoAuthenticationError: If authentication fails
            ZoomInfoAPIError: For other API errors
        """
        logger.info(f"Searching for contacts with role '{role_keywords}' at {company_name}")

        # Step 1: Search for company to get company_id
        company_payload = {
            "companyName": company_name,
            "outputFields": ["id", "name"]
        }

        try:
            company_response = self._make_request('POST', '/search/company', json=company_payload)
            if not company_response or not company_response.json().get('data'):
                logger.warning(f"Company not found: {company_name}")
                return []

            company_id = str(company_response.json()['data'][0]['id'])
            logger.info(f"Found company ID: {company_id}")
        except Exception as e:
            logger.error(f"Error searching for company {company_name}: {e}")
            return []

        # Step 2: Search for contacts by role at this company
        # Note: Some fields require premium license (managementLevel, jobFunction, city, state)
        payload = {
            "companyId": company_id,
            "jobTitle": role_keywords,
            "outputFields": [
                "id",
                "firstName",
                "lastName",
                "jobTitle",
                "companyId",
                "companyName"
            ]
        }

        try:
            response = self._make_request('POST', '/search/contact', json=payload)

            if not response:
                logger.warning(f"No response from contact search for role '{role_keywords}' at {company_name}")
                return []

            data = response.json()

            # Extract contacts from results
            if data.get('data') and len(data['data']) > 0:
                contacts = []
                for contact in data['data'][:limit]:
                    result = {
                        'contact_id': contact.get('id'),
                        'first_name': contact.get('firstName'),
                        'last_name': contact.get('lastName'),
                        'title': contact.get('jobTitle'),
                        'management_level': contact.get('managementLevel', []),  # May be empty with basic license
                        'job_function': contact.get('jobFunction', []),  # May be empty with basic license
                        'location': 'N/A',  # Not available with basic license
                        'company_id': contact.get('companyId'),
                        'company_name': contact.get('companyName')
                    }
                    contacts.append(result)

                logger.info(f"Found {len(contacts)} contacts with role '{role_keywords}' at {company_name}")
                return contacts
            else:
                logger.warning(f"No contacts found for role '{role_keywords}' at {company_name}")
                return []

        except Exception as e:
            logger.error(f"Error searching for contacts by role '{role_keywords}': {e}")
            return []

    @staticmethod
    def _parse_name(name: str) -> tuple:
        """
        Parse a full name into first and last name.

        Args:
            name: Full name (e.g., "John Smith" or "Smith, John")

        Returns:
            Tuple of (first_name, last_name)
        """
        name = name.strip()

        if ',' in name:
            # Handle "Last, First" format
            parts = [p.strip() for p in name.split(',')]
            return parts[1] if len(parts) > 1 else '', parts[0]
        else:
            # Handle "First Last" format
            parts = name.split()
            if len(parts) >= 2:
                return parts[0], ' '.join(parts[1:])
            elif len(parts) == 1:
                return parts[0], ''
            else:
                return '', ''

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session."""
        self.session.close()
        return False
