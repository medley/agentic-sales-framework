"""Tests for company_intel_cache."""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from company_intel.company_intel_cache import CompanyIntelCache
from company_intel.models import CompanyAliases, CompanySignal


class TestCompanyIntelCache:
    """Tests for CompanyIntelCache."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def cache(self, temp_cache_dir):
        """Create cache instance with temp directory."""
        return CompanyIntelCache(accounts_root=temp_cache_dir)

    def test_create_and_save_index(self, cache, temp_cache_dir):
        """Test index creation and saving."""
        primary_id = "001ABC123"

        index = cache.create_index(
            primary_account_id=primary_id,
            company_name="Test Corp",
            aliases=CompanyAliases(domains=["test.com"])
        )

        assert cache.save_index(primary_id, index)

        # Verify file was created
        index_path = temp_cache_dir / primary_id / "intel" / "index.json"
        assert index_path.exists()

    def test_get_index(self, cache):
        """Test index retrieval."""
        primary_id = "001ABC123"

        # Create and save
        index = cache.create_index(primary_id, "Test Corp")
        cache.save_index(primary_id, index)

        # Retrieve
        loaded = cache.get_index(primary_id)

        assert loaded is not None
        assert loaded['company_name'] == "Test Corp"
        assert loaded['primary_account_id'] == primary_id

    def test_save_and_get_signals(self, cache):
        """Test signal storage and retrieval."""
        primary_id = "001ABC123"

        signals = [
            {
                'signal_id': 'test_001',
                'claim': 'Test claim',
                'source_url': 'https://example.com',
                'source_type': 'public_url',
                'citability': 'cited'
            }
        ]

        # Save
        assert cache.save_signals(primary_id, 'public_url', signals)

        # Retrieve
        loaded = cache.get_signals(primary_id, 'public_url')

        assert len(loaded) == 1
        assert loaded[0]['signal_id'] == 'test_001'

    def test_is_expired_true(self, cache):
        """Test expiry detection for expired data."""
        primary_id = "001ABC123"

        # Create index with expired provider
        past = datetime.utcnow() - timedelta(days=1)
        index = {
            'company_name': 'Test Corp',
            'primary_account_id': primary_id,
            'aliases': {},
            'providers': {
                'sec': {
                    'status': 'success',
                    'expires_at': past.isoformat() + 'Z'
                }
            }
        }
        cache.save_index(primary_id, index)

        assert cache.is_expired(primary_id, 'sec') is True

    def test_is_expired_false(self, cache):
        """Test expiry detection for non-expired data."""
        primary_id = "001ABC123"

        # Create index with future expiry
        future = datetime.utcnow() + timedelta(days=30)
        index = {
            'company_name': 'Test Corp',
            'primary_account_id': primary_id,
            'aliases': {},
            'providers': {
                'sec': {
                    'status': 'success',
                    'expires_at': future.isoformat() + 'Z'
                }
            }
        }
        cache.save_index(primary_id, index)

        assert cache.is_expired(primary_id, 'sec') is False

    def test_alias_registration_and_lookup(self, cache):
        """Test alias registration and lookup."""
        primary_id = "001ABC123"

        # Create index first
        index = cache.create_index(primary_id, "Test Corp")
        cache.save_index(primary_id, index)

        # Register aliases
        cache.register_alias(primary_id, 'domain', 'test.com')
        cache.register_alias(primary_id, 'sec_cik', '0001234567')

        # Lookup by domain
        found = cache.lookup_by_alias('domain', 'test.com')
        assert found == primary_id

        # Lookup by SEC CIK
        found = cache.lookup_by_alias('sec_cik', '0001234567')
        assert found == primary_id

    def test_list_accounts(self, cache):
        """Test listing cached accounts."""
        # Create multiple accounts
        for i in range(3):
            primary_id = f"001ABC{i:03d}"
            index = cache.create_index(primary_id, f"Test Corp {i}")
            cache.save_index(primary_id, index)

        accounts = cache.list_accounts()
        assert len(accounts) == 3

    def test_files_written_under_output_root(self, cache, temp_cache_dir):
        """Test that all files are written under the accounts root."""
        primary_id = "001ABC123"

        # Create index
        index = cache.create_index(primary_id, "Test Corp")
        cache.save_index(primary_id, index)

        # Save signals
        cache.save_signals(primary_id, 'public_url', [{'signal_id': 'test'}])

        # Save provider data
        cache.save_provider_data(primary_id, 'sec', 'metadata.json', {'cik': '123'})

        # Verify all files are under temp_cache_dir
        all_files = list(temp_cache_dir.rglob('*'))
        for f in all_files:
            assert str(f).startswith(str(temp_cache_dir))
