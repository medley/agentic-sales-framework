"""
Company Cache - Separate cache for company-level data

Caches company research independently from contacts, allowing multiple
contacts at the same company to share cached company intel.

Cache Structure:
- Company data: 90-day TTL
- Indexed by company name (normalized)
- SQLite backend for faster lookups

Usage:
    from company_cache import CompanyCache

    cache = CompanyCache()
    cache.set_company("Acme Corp", company_data)
    data = cache.get_company("Acme Corp")
"""

import logging
import sqlite3
import json
from typing import Dict, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CompanyCache:
    """
    SQLite-based cache for company-level research data.
    """

    def __init__(
        self,
        cache_dir: str = ".cache",
        ttl_days: int = 90
    ):
        """
        Initialize company cache.

        Args:
            cache_dir: Directory for cache database
            ttl_days: Time-to-live in days (default 90)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        self.db_path = self.cache_dir / "company_cache.db"
        self.ttl_days = ttl_days

        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                company_key TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                data TEXT NOT NULL,
                cached_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                sources TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_company_name
            ON companies(company_name)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expires_at
            ON companies(expires_at)
        """)

        conn.commit()
        conn.close()

        logger.info(f"Company cache initialized at {self.db_path}")

    def get_company(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Get cached company data.

        Args:
            company_name: Company name (case-insensitive)

        Returns:
            Cached company data dict or None if not found/expired
        """
        company_key = self._normalize_company_name(company_name)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT data, expires_at, sources
            FROM companies
            WHERE company_key = ? AND expires_at > ?
        """, (company_key, datetime.utcnow().isoformat()))

        row = cursor.fetchone()
        conn.close()

        if row:
            data_json, expires_at, sources = row
            logger.info(f"Cache hit: {company_name} (sources: {sources})")
            return json.loads(data_json)

        logger.info(f"Cache miss: {company_name}")
        return None

    def set_company(
        self,
        company_name: str,
        data: Dict[str, Any],
        sources: list = None
    ):
        """
        Cache company data.

        Args:
            company_name: Company name
            data: Company research data dict
            sources: List of data sources (e.g., ['perplexity', 'webfetch'])
        """
        company_key = self._normalize_company_name(company_name)
        sources_str = ','.join(sources or [])

        cached_at = datetime.utcnow()
        expires_at = cached_at + timedelta(days=self.ttl_days)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO companies
            (company_key, company_name, data, cached_at, expires_at, sources)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            company_key,
            company_name,
            json.dumps(data),
            cached_at.isoformat(),
            expires_at.isoformat(),
            sources_str
        ))

        conn.commit()
        conn.close()

        logger.info(f"Cached company data: {company_name} (TTL: {self.ttl_days}d)")

    def invalidate_company(self, company_name: str) -> bool:
        """
        Invalidate cached data for a company.

        Args:
            company_name: Company name

        Returns:
            True if cache entry was deleted
        """
        company_key = self._normalize_company_name(company_name)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM companies WHERE company_key = ?
        """, (company_key,))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if deleted:
            logger.info(f"Invalidated cache: {company_name}")
        else:
            logger.info(f"No cache entry found: {company_name}")

        return deleted

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries deleted
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM companies WHERE expires_at <= ?
        """, (datetime.utcnow().isoformat(),))

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        if deleted > 0:
            logger.info(f"Cleaned up {deleted} expired cache entries")

        return deleted

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            {
                'total_companies': int,
                'expired_companies': int,
                'active_companies': int,
                'cache_size_mb': float
            }
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Total companies
        cursor.execute("SELECT COUNT(*) FROM companies")
        total = cursor.fetchone()[0]

        # Expired companies
        cursor.execute("""
            SELECT COUNT(*) FROM companies WHERE expires_at <= ?
        """, (datetime.utcnow().isoformat(),))
        expired = cursor.fetchone()[0]

        conn.close()

        # Cache file size
        cache_size_mb = self.db_path.stat().st_size / (1024 * 1024)

        return {
            'total_companies': total,
            'expired_companies': expired,
            'active_companies': total - expired,
            'cache_size_mb': round(cache_size_mb, 2)
        }

    def list_cached_companies(self) -> list:
        """
        List all cached companies (non-expired).

        Returns:
            List of company names
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT company_name, cached_at, expires_at, sources
            FROM companies
            WHERE expires_at > ?
            ORDER BY cached_at DESC
        """, (datetime.utcnow().isoformat(),))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                'company_name': row[0],
                'cached_at': row[1],
                'expires_at': row[2],
                'sources': row[3].split(',')
            }
            for row in rows
        ]

    def _normalize_company_name(self, company_name: str) -> str:
        """
        Normalize company name for cache key.

        Args:
            company_name: Raw company name

        Returns:
            Normalized key (lowercase, no spaces/punctuation)
        """
        # Remove common suffixes
        normalized = company_name.lower()
        for suffix in [' inc', ' inc.', ' llc', ' ltd', ' corp', ' corporation', ' company', ' co']:
            normalized = normalized.replace(suffix, '')

        # Remove special characters and extra spaces
        import re
        normalized = re.sub(r'[^a-z0-9]', '', normalized)

        return normalized


class CompanyCacheError(Exception):
    """Base exception for company cache errors."""
    pass
