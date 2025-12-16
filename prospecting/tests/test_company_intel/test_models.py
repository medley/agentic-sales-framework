"""Tests for company_intel.models."""

import pytest
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from company_intel.models import (
    CompanySignal,
    CompanyAliases,
    ProviderStatus,
    CompanyIntelResult,
    SECMetadata,
    SECFiling,
)


class TestCompanySignal:
    """Tests for CompanySignal dataclass."""

    def test_create_signal(self):
        """Test creating a basic signal."""
        signal = CompanySignal(
            signal_id="sec_10k_mfg_001",
            claim="Company operates 5 manufacturing facilities",
            source_url="https://www.sec.gov/...",
            source_type="public_url",
            citability="cited",
            provider="sec",
            filing_type="10-K"
        )

        assert signal.signal_id == "sec_10k_mfg_001"
        assert signal.source_type == "public_url"
        assert signal.citability == "cited"
        assert signal.scope == "company_level"

    def test_signal_to_dict(self):
        """Test signal serialization."""
        signal = CompanySignal(
            signal_id="test_001",
            claim="Test claim",
            source_url="https://example.com",
            source_type="public_url",
            citability="cited",
            key_terms=["test", "claim"]
        )

        data = signal.to_dict()
        assert data['signal_id'] == "test_001"
        assert data['key_terms'] == ["test", "claim"]

    def test_signal_from_dict(self):
        """Test signal deserialization."""
        data = {
            'signal_id': 'test_002',
            'claim': 'Test claim 2',
            'source_url': 'https://example.com',
            'source_type': 'public_url',
            'citability': 'cited'
        }

        signal = CompanySignal.from_dict(data)
        assert signal.signal_id == 'test_002'
        assert signal.citability == 'cited'


class TestCompanyAliases:
    """Tests for CompanyAliases dataclass."""

    def test_create_aliases(self):
        """Test creating aliases."""
        aliases = CompanyAliases(
            site_account_ids=["001ABC", "001DEF"],
            domains=["example.com"],
            sec_cik="0001234567"
        )

        assert len(aliases.site_account_ids) == 2
        assert aliases.sec_cik == "0001234567"

    def test_add_alias(self):
        """Test adding aliases."""
        aliases = CompanyAliases()

        aliases.add_alias('domain', 'example.com')
        assert 'example.com' in aliases.domains

        aliases.add_alias('sec_cik', '0001234567')
        assert aliases.sec_cik == '0001234567'

        # No duplicates
        aliases.add_alias('domain', 'example.com')
        assert len(aliases.domains) == 1


class TestProviderStatus:
    """Tests for ProviderStatus dataclass."""

    def test_is_expired_true(self):
        """Test expired status detection."""
        past = datetime.utcnow() - timedelta(days=1)
        status = ProviderStatus(
            status="success",
            expires_at=past.isoformat() + 'Z'
        )

        assert status.is_expired() is True

    def test_is_expired_false(self):
        """Test non-expired status detection."""
        future = datetime.utcnow() + timedelta(days=30)
        status = ProviderStatus(
            status="success",
            expires_at=future.isoformat() + 'Z'
        )

        assert status.is_expired() is False

    def test_is_expired_no_expiry(self):
        """Test status without expiry is considered expired."""
        status = ProviderStatus(status="success")
        assert status.is_expired() is True


class TestCompanyIntelResult:
    """Tests for CompanyIntelResult dataclass."""

    def test_add_signal(self):
        """Test adding signals to result."""
        result = CompanyIntelResult(
            company_name="Test Corp",
            primary_account_id="001ABC"
        )

        signal = CompanySignal(
            signal_id="test_001",
            claim="Test claim",
            source_url="https://example.com",
            source_type="public_url",
            citability="cited"
        )

        result.add_signal(signal)

        assert len(result.signals['public_url']) == 1
        assert result.total_signals['public_url'] == 1

    def test_get_cited_signals(self):
        """Test getting cited signals only."""
        result = CompanyIntelResult(
            company_name="Test Corp",
            primary_account_id="001ABC"
        )

        # Add public_url signal (cited)
        result.add_signal(CompanySignal(
            signal_id="test_001",
            claim="Public claim",
            source_url="https://example.com",
            source_type="public_url",
            citability="cited"
        ))

        # Add vendor_data signal (uncited)
        result.add_signal(CompanySignal(
            signal_id="test_002",
            claim="Vendor claim",
            source_url="",
            source_type="vendor_data",
            citability="uncited"
        ))

        cited = result.get_cited_signals()
        assert len(cited) == 1
        assert cited[0].source_type == "public_url"

    def test_to_dict_from_dict(self):
        """Test serialization round-trip."""
        result = CompanyIntelResult(
            company_name="Test Corp",
            primary_account_id="001ABC",
            aliases=CompanyAliases(domains=["test.com"])
        )

        result.add_signal(CompanySignal(
            signal_id="test_001",
            claim="Test claim",
            source_url="https://example.com",
            source_type="public_url",
            citability="cited"
        ))

        data = result.to_dict()
        restored = CompanyIntelResult.from_dict(data)

        assert restored.company_name == "Test Corp"
        assert len(restored.signals['public_url']) == 1
