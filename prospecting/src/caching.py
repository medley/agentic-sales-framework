"""
Caching Infrastructure for Prospecting Module

Adapted from site-signals caching system.
Provides multi-level caching for prospect enrichment data:
1. Contact Profiles: Individual enrichment data (90 days TTL)
2. API Responses: Raw API data (180 days TTL)

Features:
- Unified cache abstraction with TTL management
- Support for both file and GCS backends
- Performance tracking and statistics
- Automatic expiration handling
"""
import json
import hashlib
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Callable, Iterable
from dataclasses import dataclass
from functools import wraps
import logging

try:
    from google.cloud import storage as gcs_storage
except ImportError:
    gcs_storage = None

try:
    from google.api_core.exceptions import NotFound
except ImportError:
    NotFound = Exception  # type: ignore[assignment]

logger = logging.getLogger(__name__)


# ============================================================================
# STORAGE BACKENDS
# ============================================================================

class LocalCacheStorage:
    """Filesystem-backed cache storage."""

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _resolve(self, name: str) -> Path:
        path = self.base_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def read_json(self, name: str) -> Optional[Dict]:
        path = self.base_dir / name
        if not path.exists():
            return None
        with open(path, 'r') as f:
            return json.load(f)

    def write_json(self, name: str, data: Dict) -> None:
        path = self._resolve(name)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def read_bytes(self, name: str) -> Optional[bytes]:
        path = self.base_dir / name
        if not path.exists():
            return None
        with open(path, 'rb') as f:
            return f.read()

    def write_bytes(self, name: str, data: bytes) -> None:
        path = self._resolve(name)
        with open(path, 'wb') as f:
            f.write(data)

    def delete(self, name: str) -> None:
        path = self.base_dir / name
        if path.exists():
            path.unlink()

    def exists(self, name: str) -> bool:
        return (self.base_dir / name).exists()

    def iter_names(self, suffix: str = "") -> Iterable[str]:
        pattern = "**/*"
        for path in self.base_dir.glob(pattern):
            if not path.is_file():
                continue
            if suffix and not str(path).endswith(suffix):
                continue
            yield path.relative_to(self.base_dir).as_posix()


class GCSCacheStorage:
    """GCS-backed cache storage used in Cloud Run."""

    def __init__(self, bucket_name: str, prefix: str = ""):
        if not bucket_name:
            raise ValueError("CACHE_BUCKET is required for GCS cache backend")
        if gcs_storage is None:
            raise ImportError("google-cloud-storage is not installed")
        self.client = gcs_storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        self.prefix = prefix.strip('/')
        self.base_prefix = f"{self.prefix}/" if self.prefix else ""

    def _blob_name(self, name: str) -> str:
        return f"{self.base_prefix}{name}" if self.base_prefix else name

    def read_json(self, name: str) -> Optional[Dict]:
        blob = self.bucket.blob(self._blob_name(name))
        try:
            data = blob.download_as_text()
            return json.loads(data)
        except NotFound:
            return None
        except Exception as exc:
            logger.warning(f"GCS cache read_json error ({name}): {exc}")
            return None

    def write_json(self, name: str, data: Dict) -> None:
        blob = self.bucket.blob(self._blob_name(name))
        blob.upload_from_string(json.dumps(data, indent=2), content_type='application/json')

    def read_bytes(self, name: str) -> Optional[bytes]:
        blob = self.bucket.blob(self._blob_name(name))
        try:
            return blob.download_as_bytes()
        except NotFound:
            return None
        except Exception as exc:
            logger.warning(f"GCS cache read_bytes error ({name}): {exc}")
            return None

    def write_bytes(self, name: str, data: bytes) -> None:
        blob = self.bucket.blob(self._blob_name(name))
        blob.upload_from_string(data, content_type='application/octet-stream')

    def delete(self, name: str) -> None:
        blob = self.bucket.blob(self._blob_name(name))
        try:
            blob.delete()
        except NotFound:
            return
        except Exception as exc:
            logger.warning(f"GCS cache delete error ({name}): {exc}")

    def exists(self, name: str) -> bool:
        blob = self.bucket.blob(self._blob_name(name))
        try:
            return blob.exists()
        except Exception as exc:
            logger.warning(f"GCS cache exists error ({name}): {exc}")
            return False

    def iter_names(self, suffix: str = "") -> Iterable[str]:
        prefix = self.base_prefix or None
        try:
            for blob in self.client.list_blobs(self.bucket, prefix=prefix):
                if blob.name.endswith('/'):
                    continue
                if suffix and not blob.name.endswith(suffix):
                    continue
                if self.base_prefix:
                    yield blob.name[len(self.base_prefix):]
                else:
                    yield blob.name
        except Exception as exc:
            logger.warning(f"GCS cache listing error: {exc}")


def create_cache_storage(base_dir: Path, backend_hint: Optional[str] = None):
    """
    Helper to initialize cache storage respecting CACHE_BACKEND env overrides.

    Returns:
        (storage_impl, backend_name)
    """
    namespace = base_dir.as_posix().lstrip("./")
    env_backend = os.getenv('CACHE_BACKEND')
    backend = (env_backend or backend_hint or 'file').lower()
    if backend == 'auto':
        backend = 'gcs' if os.getenv('CACHE_BUCKET') and os.getenv('K_SERVICE') else 'file'

    if backend == 'gcs':
        bucket = os.getenv('CACHE_BUCKET')
        prefix_env = os.getenv('CACHE_PREFIX', '').strip('/')
        prefix = "/".join(filter(None, [prefix_env, namespace]))
        try:
            storage_impl = GCSCacheStorage(bucket_name=bucket, prefix=prefix)
            logger.info(f"[Cache] Using GCS backend for {namespace} (bucket={bucket}, prefix={prefix or '(root)'})")
            return storage_impl, 'gcs'
        except Exception as exc:
            logger.warning(f"[Cache] Falling back to local storage for {namespace}: {exc}")

    storage_impl = LocalCacheStorage(base_dir)
    return storage_impl, 'file'


# ============================================================================
# CACHE ENTRY
# ============================================================================

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    created_at: str  # ISO format timestamp
    ttl_days: int
    value: Any = None  # Not stored in metadata, only in pickle file
    size_bytes: int = 0

    @property
    def expires_at(self) -> datetime:
        """Calculate expiration timestamp"""
        created = datetime.fromisoformat(self.created_at)
        return created + timedelta(days=self.ttl_days)

    def is_expired(self) -> bool:
        """Check if entry has expired"""
        return datetime.now() > self.expires_at

    def age_days(self) -> float:
        """Get age in days"""
        created = datetime.fromisoformat(self.created_at)
        delta = datetime.now() - created
        return delta.total_seconds() / 86400  # Convert to days


# ============================================================================
# BASE CACHE
# ============================================================================

class BaseCache:
    """Base cache with TTL support"""

    def __init__(self, cache_dir: str, ttl_days: int, backend: str = 'file', redis_url: Optional[str] = None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_days = ttl_days
        self.ttl = timedelta(days=ttl_days)

        backend_override = os.getenv('CACHE_BACKEND')
        backend_choice = backend_override or backend

        # Performance tracking
        self.hits = 0
        self.misses = 0
        self.sets = 0

        # Redis client (if using Redis backend)
        self.redis_client = None
        if backend_choice == 'redis':
            try:
                import redis
                self.redis_client = redis.from_url(redis_url or 'redis://localhost:6379')
                logger.info("Connected to Redis cache")
            except ImportError:
                logger.warning("Redis not installed, falling back to file cache")
                backend_choice = 'file'

        self.storage, self.backend = create_cache_storage(self.cache_dir, backend_choice)

    def _get_cache_key(self, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, dict):
            # Sort keys for consistent hashing
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)

        return hashlib.md5(data_str.encode()).hexdigest()

    def _cache_filename(self, key: str) -> str:
        """Get cache file name"""
        return f"{key}.json"

    def _is_expired(self, cache_data: Dict) -> bool:
        """Check if cached data is expired"""
        if 'cached_at' not in cache_data:
            return True

        cached_at = datetime.fromisoformat(cache_data['cached_at'])
        age = datetime.now() - cached_at

        return age > self.ttl

    def get(self, key_data: Any) -> Optional[Dict]:
        """Get cached data (with performance tracking)"""
        key = self._get_cache_key(key_data)
        filename = self._cache_filename(key)
        cache_data = self.storage.read_json(filename)

        if cache_data is None:
            self.misses += 1
            return None

        # Check expiration
        if self._is_expired(cache_data):
            logger.debug(f"Cache expired for key {key[:8]}")
            self.storage.delete(filename)
            self.misses += 1
            return None

        logger.debug(f"Cache hit for key {key[:8]}")
        self.hits += 1
        return cache_data.get('data')

    def set(self, key_data: Any, data: Dict) -> None:
        """Set cached data (with performance tracking)"""
        key = self._get_cache_key(key_data)
        filename = self._cache_filename(key)

        cache_data = {
            'data': data,
            'cached_at': datetime.now().isoformat(),
            'ttl_days': self.ttl_days
        }

        try:
            self.storage.write_json(filename, cache_data)
            self.sets += 1
            logger.debug(f"Cache set for key {key[:8]}")
        except Exception as e:
            logger.warning(f"Cache write error for key {key[:8]}: {e}")

    def clear_expired(self) -> int:
        """Clear all expired cache entries"""
        expired_count = 0

        for name in self.storage.iter_names(suffix=".json"):
            try:
                cache_data = self.storage.read_json(name)
                if cache_data is None:
                    continue
                if self._is_expired(cache_data):
                    self.storage.delete(name)
                    expired_count += 1
            except Exception as e:
                logger.warning(f"Error checking cache file {name}: {e}")

        if expired_count > 0:
            logger.info(f"Cleared {expired_count} expired cache entries from {self.cache_dir.name}")

        return expired_count

    def count_entries(self, suffix: str = ".json") -> int:
        """Count cached objects (used for diagnostics)"""
        return sum(1 for _ in self.storage.iter_names(suffix=suffix))

    def get_stats(self) -> dict:
        """Get cache performance statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total) if total > 0 else 0

        return {
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'hit_rate': hit_rate,
            'total_requests': total
        }

    def cached(
        self,
        key_func: Optional[Callable] = None,
        ttl_days: Optional[int] = None,
        key_prefix: str = ""
    ):
        """
        Decorator for caching function results

        Args:
            key_func: Function to generate cache key from args
                     If None, uses function name + args hash
            ttl_days: TTL in days
            key_prefix: Prefix for cache key

        Example:
            @cache.cached(key_func=lambda company: f"sec_{company}", ttl_days=7)
            def fetch_sec_data(company):
                return api_call(company)

            # First call: cache miss, fetches from API
            data = fetch_sec_data("AAPL")

            # Second call: cache hit, returns cached data
            data = fetch_sec_data("AAPL")  # Instant!
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default: function name + hash of args
                    args_str = str(args) + str(kwargs)
                    args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
                    cache_key = f"{func.__name__}_{args_hash}"

                # Add prefix
                if key_prefix:
                    cache_key = f"{key_prefix}_{cache_key}"

                # Try cache (use cache_key as key_data since it's already a string)
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache HIT: {cache_key}")
                    return cached_value

                # Cache miss, call function
                logger.debug(f"Cache MISS: {cache_key}")
                result = func(*args, **kwargs)

                # Store in cache (use cache_key as key_data)
                # Note: ttl_days is ignored since set() uses instance ttl_days
                self.set(cache_key, result)

                return result

            return wrapper

        return decorator


# ============================================================================
# SPECIALIZED CACHE TYPES FOR PROSPECTING
# ============================================================================

class ContactCache(BaseCache):
    """Cache for individual contact enrichment data

    TTL: 90 days (prospects don't change frequently)
    Storage: Prospecting/.cache/prospects/contact_profiles/
    """

    def __init__(self, ttl_days: int = 90):
        super().__init__('Prospecting/.cache/prospects/contact_profiles', ttl_days)

    def get_profile(self, name: str, company: str) -> Optional[Dict]:
        """Get cached contact profile"""
        key_data = {'name': name.lower(), 'company': company.lower()}
        return self.get(key_data)

    def set_profile(self, name: str, company: str, profile: Dict) -> None:
        """Cache contact profile"""
        key_data = {'name': name.lower(), 'company': company.lower()}
        self.set(key_data, profile)


class APIResponseCache(BaseCache):
    """Cache for API responses (Google, LinkedIn, etc.)

    TTL: 180 days (API data is stable)
    Storage: Prospecting/.cache/prospects/api_responses/
    """

    def __init__(self, ttl_days: int = 180):
        super().__init__('Prospecting/.cache/prospects/api_responses', ttl_days)

    def get_response(self, query: str, source: str) -> Optional[Dict]:
        """Get cached API response"""
        key_data = {'query': query.lower(), 'source': source}
        return self.get(key_data)

    def set_response(self, query: str, source: str, response: Dict) -> None:
        """Cache API response"""
        key_data = {'query': query.lower(), 'source': source}
        self.set(key_data, response)


class CacheManager:
    """Manage all Prospecting module caches"""

    def __init__(self):
        self.contact_cache = ContactCache(ttl_days=90)
        self.api_cache = APIResponseCache(ttl_days=180)

    def clear_all_expired(self) -> Dict[str, int]:
        """Clear expired entries from all caches"""
        return {
            'contact_profiles': self.contact_cache.clear_expired(),
            'api_responses': self.api_cache.clear_expired()
        }

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics

        Returns:
            Dict with file counts and hit rates for each cache type
        """
        stats = {
            'contact_profiles': {
                'count': self.contact_cache.count_entries(".json"),
                'performance': self.contact_cache.get_stats()
            },
            'api_responses': {
                'count': self.api_cache.count_entries(".json"),
                'performance': self.api_cache.get_stats()
            }
        }
        return stats


# Global cache manager instance
cache_manager = CacheManager()


if __name__ == '__main__':
    # Test caching
    print("Testing Prospecting cache infrastructure...")

    # Test contact cache
    contact_cache = ContactCache()
    contact_cache.set_profile(
        "John Doe",
        "Example Corp",
        {"title": "VP Sales", "email": "john@example.com", "test": True}
    )

    result = contact_cache.get_profile("John Doe", "Example Corp")
    print(f"Contact cache test: {'PASS' if result else 'FAIL'}")
    if result:
        print(f"  Retrieved: {result}")

    # Test API cache
    api_cache = APIResponseCache()
    api_cache.set_response("John Doe Example Corp", "linkedin", {"profile": "test_profile_url"})

    result = api_cache.get_response("John Doe Example Corp", "linkedin")
    print(f"API cache test: {'PASS' if result else 'FAIL'}")
    if result:
        print(f"  Retrieved: {result}")

    # Get cache stats
    manager = CacheManager()
    stats = manager.get_cache_stats()
    print(f"\nCache stats:")
    print(json.dumps(stats, indent=2))

    print("\nCache infrastructure ready!")
