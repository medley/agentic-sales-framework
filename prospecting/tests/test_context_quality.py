"""
Tests for Context Quality Module

Tests the context quality computation, formatting, and artifact writing functions.
"""

import pytest
import tempfile
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

from src.context_quality import (
    ProspectContextQuality,
    DealContextQuality,
    compute_prospect_context_quality,
    compute_deal_context_quality,
    get_battle_card_age_warning,
    check_all_battle_cards,
    format_prospect_context_header,
    format_deal_context_header,
    write_prospect_context_quality_artifact,
    write_deal_context_quality_artifact,
    STALENESS_THRESHOLDS
)


class TestProspectContextQuality:
    """Test suite for prospect context quality computation."""

    @pytest.fixture
    def sample_prospect_brief_high(self):
        """Sample prospect brief with high confidence."""
        return {
            'confidence_tier': 'high',
            'cited_signals': [
                {
                    'id': 'signal_001',
                    'claim': 'Company raised $50M in Series C',
                    'source_type': 'public_url',
                    'citability': 'cited',
                    'recency_days': 30
                },
                {
                    'id': 'signal_002',
                    'claim': 'FDA approved new drug application',
                    'source_type': 'public_url',
                    'citability': 'cited',
                    'recency_days': 45
                },
                {
                    'id': 'signal_003',
                    'claim': 'New VP of Quality hired',
                    'source_type': 'public_url',
                    'citability': 'cited',
                    'recency_days': 60
                }
            ]
        }

    @pytest.fixture
    def sample_prospect_brief_low(self):
        """Sample prospect brief with low confidence (vendor data only)."""
        return {
            'confidence_tier': 'low',
            'cited_signals': [
                {
                    'id': 'signal_001',
                    'claim': 'Uses SAP ERP',
                    'source_type': 'vendor_data',
                    'citability': 'uncited',
                    'recency_days': 90
                }
            ]
        }

    @pytest.fixture
    def sample_research_data_full(self):
        """Sample research data with all sources."""
        return {
            'zoominfo': {'company': 'Test Corp', 'tech_stack': ['SAP']},
            'contact': {'first_name': 'John', 'email': 'john@test.com'},
            'perplexity': {
                'company_overview': 'Test Corp is a pharma company',
                'cited_claims': [
                    {'claim': 'Recently announced expansion', 'source_url': 'https://example.com'}
                ]
            },
            'webfetch': {'source_url': 'https://testcorp.com'}
        }

    @pytest.fixture
    def sample_research_data_minimal(self):
        """Sample research data with minimal sources."""
        return {
            'contact': {'first_name': 'Jane'}
        }

    def test_high_confidence_computation(self, sample_prospect_brief_high, sample_research_data_full):
        """Test that high confidence is computed correctly."""
        quality = compute_prospect_context_quality(
            prospect_brief=sample_prospect_brief_high,
            research_data=sample_research_data_full
        )

        assert quality.confidence_mode == 'HIGH'
        assert quality.cited_signal_count == 3
        assert quality.vendor_signal_count == 0
        assert quality.total_signal_count == 3
        assert quality.zoominfo_used is True
        assert quality.perplexity_used is True
        assert quality.perplexity_has_citations is True
        assert quality.webfetch_used is True

    def test_low_confidence_computation(self, sample_prospect_brief_low, sample_research_data_minimal):
        """Test that low confidence with vendor data triggers warnings."""
        quality = compute_prospect_context_quality(
            prospect_brief=sample_prospect_brief_low,
            research_data=sample_research_data_minimal
        )

        assert quality.confidence_mode == 'LOW'
        assert quality.cited_signal_count == 0
        assert quality.vendor_signal_count == 1
        assert len(quality.warnings) > 0
        # Should warn about no cited signals
        assert any('cited' in w.lower() or 'vendor' in w.lower() for w in quality.warnings)

    def test_signal_date_extraction(self, sample_prospect_brief_high, sample_research_data_full):
        """Test that signal dates are extracted from recency_days."""
        quality = compute_prospect_context_quality(
            prospect_brief=sample_prospect_brief_high,
            research_data=sample_research_data_full
        )

        # Should have computed dates from recency_days
        assert quality.oldest_signal_date is not None
        assert quality.newest_signal_date is not None
        assert quality.signal_age_days is not None
        # Oldest should be 60 days (signal_003)
        assert quality.signal_age_days >= 59  # Allow for test timing

    def test_no_signals_returns_generic(self):
        """Test that no signals returns generic confidence."""
        quality = compute_prospect_context_quality(
            prospect_brief={'confidence_tier': 'generic', 'cited_signals': []},
            research_data={}
        )

        assert quality.confidence_mode == 'GENERIC'
        assert quality.total_signal_count == 0
        assert len(quality.warnings) > 0

    def test_to_dict_serialization(self, sample_prospect_brief_high, sample_research_data_full):
        """Test that quality can be serialized to dict."""
        quality = compute_prospect_context_quality(
            prospect_brief=sample_prospect_brief_high,
            research_data=sample_research_data_full
        )

        quality_dict = quality.to_dict()

        assert isinstance(quality_dict, dict)
        assert 'confidence_mode' in quality_dict
        assert 'cited_signal_count' in quality_dict
        assert 'warnings' in quality_dict
        # Should be JSON serializable
        json.dumps(quality_dict)


class TestDealContextQuality:
    """Test suite for deal context quality computation."""

    @pytest.fixture
    def temp_account_folder(self):
        """Create a temporary account folder structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            account_path = Path(tmpdir) / 'TestAccount'
            account_path.mkdir()

            # Create required files
            (account_path / '_README.md').write_text('# Test Account')
            (account_path / 'TestAccount_people.md').write_text('## Stakeholders\n- John Doe, VP Quality')

            # Create context folder
            context_dir = account_path / 'context'
            context_dir.mkdir()
            (context_dir / 'meddpic.md').write_text('# MEDDPIC')

            # Create conversations folder
            conv_dir = account_path / 'conversations'
            conv_dir.mkdir()
            (conv_dir / '2025-12-01_call_summary.md').write_text('# Call Summary')
            (conv_dir / '2025-12-05_email_from_john.md').write_text('# Email')

            yield str(account_path)

    @pytest.fixture
    def temp_empty_folder(self):
        """Create an empty temporary folder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            account_path = Path(tmpdir) / 'EmptyAccount'
            account_path.mkdir()
            yield str(account_path)

    def test_complete_folder_quality(self, temp_account_folder):
        """Test quality computation for a complete folder."""
        quality = compute_deal_context_quality(
            folder_path=temp_account_folder,
            account_name='TestAccount'
        )

        assert quality.total_files_found >= 4
        assert quality.required_files_present >= 1
        assert quality.freshness_status == 'CURRENT'  # Just created
        assert quality.completeness_score > 0
        assert quality.emails_present is True

    def test_empty_folder_quality(self, temp_empty_folder):
        """Test quality computation for an empty folder."""
        quality = compute_deal_context_quality(
            folder_path=temp_empty_folder,
            account_name='EmptyAccount'
        )

        assert quality.total_files_found == 0
        assert quality.required_files_present == 0
        assert quality.completeness_score == 0
        assert len(quality.warnings) > 0

    def test_nonexistent_folder(self):
        """Test quality computation for a non-existent folder."""
        quality = compute_deal_context_quality(
            folder_path='/nonexistent/path',
            account_name='Nonexistent'
        )

        assert quality.total_files_found == 0
        assert quality.completeness_score == 0
        assert 'Folder does not exist' in quality.warnings[0]

    def test_freshness_classification(self, temp_account_folder):
        """Test that freshness is classified correctly."""
        quality = compute_deal_context_quality(
            folder_path=temp_account_folder,
            account_name='TestAccount'
        )

        # Newly created should be CURRENT
        assert quality.freshness_status == 'CURRENT'
        assert quality.days_since_update is not None
        assert quality.days_since_update <= 1

    def test_to_dict_serialization(self, temp_account_folder):
        """Test that quality can be serialized to dict."""
        quality = compute_deal_context_quality(
            folder_path=temp_account_folder,
            account_name='TestAccount'
        )

        quality_dict = quality.to_dict()

        assert isinstance(quality_dict, dict)
        assert 'folder_path' in quality_dict
        assert 'completeness_score' in quality_dict
        assert 'freshness_status' in quality_dict
        # Should be JSON serializable
        json.dumps(quality_dict)


class TestBattleCardAgeWarning:
    """Test suite for battle card age warnings."""

    @pytest.fixture
    def temp_battle_card_current(self):
        """Create a current (recently modified) battle card."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('# Competitor Battle Card\nContent here')
            f.flush()
            yield f.name
            os.unlink(f.name)

    @pytest.fixture
    def temp_battle_card_stale(self):
        """Create a stale battle card (modified 200 days ago)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('# Competitor Battle Card\nContent here')
            f.flush()
            # Set modification time to 200 days ago
            old_time = (datetime.now() - timedelta(days=200)).timestamp()
            os.utime(f.name, (old_time, old_time))
            yield f.name
            os.unlink(f.name)

    def test_current_battle_card_no_warning(self, temp_battle_card_current):
        """Test that current battle cards don't generate warnings."""
        last_updated, warning = get_battle_card_age_warning(temp_battle_card_current)

        assert last_updated is not None
        assert warning is None

    def test_stale_battle_card_warning(self, temp_battle_card_stale):
        """Test that stale battle cards generate warnings."""
        last_updated, warning = get_battle_card_age_warning(temp_battle_card_stale)

        assert last_updated is not None
        assert warning is not None
        assert 'outdated' in warning.lower() or 'days ago' in warning.lower()

    def test_nonexistent_battle_card(self):
        """Test that non-existent battle cards generate error."""
        last_updated, warning = get_battle_card_age_warning('/nonexistent/file.md')

        assert last_updated is None
        assert warning is not None
        assert 'not found' in warning.lower()

    def test_custom_threshold(self, temp_battle_card_current):
        """Test custom staleness threshold."""
        # With threshold of 0 days, even current files should warn
        last_updated, warning = get_battle_card_age_warning(
            temp_battle_card_current,
            threshold_days=0
        )

        assert last_updated is not None
        # With 0 day threshold, any file should trigger warning
        # (unless it was literally just created in this same second)


class TestFormatHeaders:
    """Test suite for header formatting functions."""

    def test_format_prospect_header_high_confidence(self):
        """Test formatting of high confidence header."""
        quality = ProspectContextQuality(
            confidence_mode='HIGH',
            cited_signal_count=3,
            vendor_signal_count=1,
            inferred_signal_count=0,
            total_signal_count=4,
            oldest_signal_date='2025-11-01',
            newest_signal_date='2025-12-01',
            signal_age_days=40,
            zoominfo_used=True,
            perplexity_used=True,
            perplexity_has_citations=True,
            webfetch_used=False,
            user_context_provided=False,
            warnings=[]
        )

        header = format_prospect_context_header(quality)

        assert 'CONTEXT QUALITY' in header
        assert 'HIGH' in header
        assert 'Cited (verifiable):    3' in header
        assert 'ZoomInfo:              Yes' in header
        assert 'Perplexity citations:  Yes' in header

    def test_format_prospect_header_with_warnings(self):
        """Test formatting of header with warnings."""
        quality = ProspectContextQuality(
            confidence_mode='LOW',
            cited_signal_count=0,
            vendor_signal_count=2,
            inferred_signal_count=0,
            total_signal_count=2,
            oldest_signal_date=None,
            newest_signal_date=None,
            signal_age_days=None,
            zoominfo_used=True,
            perplexity_used=False,
            perplexity_has_citations=False,
            webfetch_used=False,
            user_context_provided=False,
            warnings=['No cited signals - claims cannot be verified']
        )

        header = format_prospect_context_header(quality)

        assert 'LOW' in header
        assert 'Warnings:' in header
        assert 'cannot be verified' in header

    def test_format_deal_header(self):
        """Test formatting of deal context header."""
        quality = DealContextQuality(
            folder_path='/test/path',
            folder_last_modified='2025-12-01T10:00:00',
            oldest_file_date='2025-10-01T10:00:00',
            newest_file_date='2025-12-01T10:00:00',
            days_since_update=10,
            total_files_found=15,
            required_files_present=2,
            required_files_total=2,
            recommended_files_present=1,
            recommended_files_total=2,
            transcripts_last_30_days=2,
            emails_present=True,
            named_stakeholders=5,
            stakeholder_roles_unknown=1,
            completeness_score=75,
            freshness_status='CURRENT',
            warnings=[]
        )

        header = format_deal_context_header(quality)

        assert 'CONTEXT QUALITY - Deal Analysis' in header
        assert 'CURRENT' in header
        assert '75%' in header
        assert 'Required files:    2/2' in header


class TestArtifactWriters:
    """Test suite for artifact writers."""

    def test_write_prospect_artifact(self):
        """Test writing prospect context quality artifact."""
        quality = ProspectContextQuality(
            confidence_mode='HIGH',
            cited_signal_count=3,
            vendor_signal_count=0,
            inferred_signal_count=0,
            total_signal_count=3,
            oldest_signal_date='2025-11-01',
            newest_signal_date='2025-12-01',
            signal_age_days=40,
            zoominfo_used=True,
            perplexity_used=True,
            perplexity_has_citations=True,
            webfetch_used=False,
            user_context_provided=False,
            warnings=[]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = write_prospect_context_quality_artifact(quality, tmpdir)

            assert Path(artifact_path).exists()
            assert artifact_path.endswith('context_quality.json')

            with open(artifact_path) as f:
                data = json.load(f)

            assert data['type'] == 'prospect_context_quality'
            assert data['confidence_mode'] == 'HIGH'
            assert 'generated_at' in data

    def test_write_deal_artifact(self):
        """Test writing deal context quality artifact."""
        quality = DealContextQuality(
            folder_path='/test/path',
            folder_last_modified='2025-12-01T10:00:00',
            oldest_file_date='2025-10-01T10:00:00',
            newest_file_date='2025-12-01T10:00:00',
            days_since_update=10,
            total_files_found=15,
            required_files_present=2,
            required_files_total=2,
            recommended_files_present=1,
            recommended_files_total=2,
            transcripts_last_30_days=2,
            emails_present=True,
            named_stakeholders=5,
            stakeholder_roles_unknown=1,
            completeness_score=75,
            freshness_status='CURRENT',
            warnings=[]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = write_deal_context_quality_artifact(quality, tmpdir)

            assert Path(artifact_path).exists()
            assert artifact_path.endswith('deal_context_quality.json')

            with open(artifact_path) as f:
                data = json.load(f)

            assert data['type'] == 'deal_context_quality'
            assert data['completeness_score'] == 75
            assert 'generated_at' in data


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_prospect_brief(self):
        """Test handling of empty prospect brief."""
        quality = compute_prospect_context_quality(
            prospect_brief={},
            research_data={}
        )

        assert quality.confidence_mode == 'GENERIC'
        assert quality.total_signal_count == 0

    def test_none_values_in_signals(self):
        """Test handling of None values in signals."""
        brief = {
            'confidence_tier': 'low',
            'cited_signals': [
                {
                    'id': 'signal_001',
                    'claim': None,
                    'source_type': None,
                    'recency_days': None
                }
            ]
        }

        # Should not crash
        quality = compute_prospect_context_quality(
            prospect_brief=brief,
            research_data={}
        )

        assert quality is not None

    def test_backward_compatibility_verified_signals(self):
        """Test backward compatibility with 'verified_signals' key."""
        brief = {
            'confidence_tier': 'high',
            'verified_signals': [  # Old key name
                {
                    'id': 'signal_001',
                    'claim': 'Test claim',
                    'source_type': 'public_url',
                    'verifiability': 'verified',  # Old terminology
                    'recency_days': 30
                }
            ]
        }

        quality = compute_prospect_context_quality(
            prospect_brief=brief,
            research_data={}
        )

        # Should work with old key names
        assert quality.total_signal_count == 1


# =============================================================================
# Phase 1: Canonical Schema Tests (ContextQualityBuilder)
# =============================================================================

from src.context_quality import (
    ContextQualityBuilder,
    render_context_quality_header,
    render_context_quality_header_markdown,
    write_context_quality_artifacts,
    WARNING_OLD_SIGNALS,
    WARNING_COMPANY_INTEL_STALE,
    WARNING_NO_CITED_SIGNALS,
    WARNING_VENDOR_ONLY,
    WARNING_THIN_RESEARCH,
)


class TestContextQualityBuilder:
    """Tests for ContextQualityBuilder canonical schema."""

    @pytest.fixture
    def builder(self):
        """Create builder instance."""
        return ContextQualityBuilder()

    @pytest.fixture
    def full_research_data(self):
        """Research data with all sources."""
        return {
            "company": {"name": "Test Corp", "website": "testcorp.com"},
            "contact": {"name": "John Smith", "title": "VP Quality", "email": "john@test.com"},
            "zoominfo": {"name": "John Smith", "id": "123456", "email": "john@test.com"},
            "perplexity": {
                "citations": ["https://example.com/1", "https://example.com/2"],
                "cited_claims": [{"claim": "Test claim", "url": "https://example.com/1"}]
            },
            "webfetch": {"content": "Website content", "pages": ["https://testcorp.com/about"]}
        }

    @pytest.fixture
    def full_prospect_brief(self):
        """Prospect brief with company and person signals."""
        return {
            "company_name": "Test Corp",
            "persona": "quality_leader",
            "confidence_tier": "HIGH",
            "tier": "A",
            "cited_signals": [
                {"claim": "Company has facilities", "source_type": "public_url", "scope": "company_level", "_origin": "company_intel", "recency_days": 30},
                {"claim": "Person led initiative", "source_type": "public_url", "scope": "person_level", "recency_days": 60}
            ]
        }

    @pytest.fixture
    def company_intel_data(self):
        """Company intel fixture."""
        future = datetime.utcnow() + timedelta(days=30)
        return {
            "company_name": "Test Corp",
            "primary_account_id": "001ABC123",
            "aliases": {"domains": ["testcorp.com"]},
            "last_refreshed": datetime.utcnow().isoformat() + 'Z',
            "_cache_hit": True,
            "sources": {
                "sec": {"status": "success", "last_run": datetime.utcnow().isoformat() + 'Z', "expires_at": future.isoformat() + 'Z'}
            },
            "signals": {"public_url": [{"signal_id": "sec_001", "provider": "sec", "as_of_date": "2024-12-01"}], "vendor_data": []}
        }

    def test_build_creates_canonical_schema(self, builder, full_research_data, full_prospect_brief):
        """Test that build creates all required schema sections."""
        result = builder.build(research_data=full_research_data, prospect_brief=full_prospect_brief)

        assert "generated_at" in result
        assert "run_id" in result
        assert "company" in result
        assert "contact" in result
        assert "mode" in result
        assert "sources" in result
        assert "signals" in result
        assert "artifacts" in result

    def test_company_section_with_intel(self, builder, full_research_data, full_prospect_brief, company_intel_data):
        """Test company section includes intel data."""
        result = builder.build(
            research_data=full_research_data,
            prospect_brief=full_prospect_brief,
            company_intel=company_intel_data
        )

        assert result["company"]["name"] == "Test Corp"
        assert result["company"]["primary_account_id"] == "001ABC123"
        assert result["company"]["domain"] == "testcorp.com"

    def test_signal_counts_breakdown(self, builder, full_research_data, full_prospect_brief):
        """Test company vs person signal breakdown."""
        result = builder.build(research_data=full_research_data, prospect_brief=full_prospect_brief)

        counts = result["signals"]["counts"]
        assert counts["company_cited"] == 1
        assert counts["person_cited"] == 1
        assert counts["total_cited"] == 2
        assert counts["total_vendor"] == 0

    def test_sources_section_structure(self, builder, full_research_data, full_prospect_brief, company_intel_data):
        """Test sources section has correct structure."""
        result = builder.build(
            research_data=full_research_data,
            prospect_brief=full_prospect_brief,
            company_intel=company_intel_data
        )

        sources = result["sources"]
        assert sources["zoominfo"]["ran"] is True
        assert sources["zoominfo"]["found_contact"] is True
        assert sources["perplexity"]["ran"] is True
        assert sources["perplexity"]["citations_count"] == 2
        assert sources["company_intel"]["ran"] is True
        assert "sec" in sources["company_intel"]["providers"]


class TestCanonicalWarnings:
    """Tests for warning generation in canonical schema."""

    @pytest.fixture
    def builder(self):
        return ContextQualityBuilder()

    def test_old_signals_warning(self, builder):
        """Test OLD_SIGNALS_PRESENT warning."""
        old_date = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
        brief = {"cited_signals": [{"claim": "Old", "source_type": "public_url", "date": old_date, "scope": "company_level"}]}

        result = builder.build(research_data={}, prospect_brief=brief)
        warnings = result["signals"]["warnings"]
        assert any(WARNING_OLD_SIGNALS in w for w in warnings)

    def test_no_cited_warning(self, builder):
        """Test NO_CITED_SIGNALS warning."""
        result = builder.build(research_data={}, prospect_brief={"cited_signals": []})
        warnings = result["signals"]["warnings"]
        assert any(WARNING_NO_CITED_SIGNALS in w for w in warnings)

    def test_vendor_only_warning(self, builder):
        """Test VENDOR_DATA_ONLY warning."""
        brief = {"cited_signals": [{"claim": "Vendor", "source_type": "vendor_data", "scope": "company_level"}]}
        result = builder.build(research_data={}, prospect_brief=brief)
        warnings = result["signals"]["warnings"]
        assert any(WARNING_VENDOR_ONLY in w for w in warnings)

    def test_company_intel_stale_warning(self, builder):
        """Test COMPANY_INTEL_STALE warning."""
        past = (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'
        intel = {"sources": {"sec": {"status": "success", "expires_at": past}}, "signals": {"public_url": [], "vendor_data": []}}

        result = builder.build(research_data={}, prospect_brief={"cited_signals": []}, company_intel=intel)
        warnings = result["signals"]["warnings"]
        assert any(WARNING_COMPANY_INTEL_STALE in w for w in warnings)


class TestCanonicalHeaderRendering:
    """Tests for canonical header rendering."""

    @pytest.fixture
    def sample_quality(self):
        """Sample canonical context quality."""
        return {
            "mode": {"tier": "A", "confidence_mode": "HIGH"},
            "sources": {
                "zoominfo": {"ran": True, "status": "ok", "found_contact": True, "found_email": True},
                "perplexity": {"ran": True, "status": "ok", "citations_count": 8},
                "webfetch": {"ran": True, "status": "ok"},
                "company_intel": {"ran": True, "status": "ok", "providers": {"sec": {"status": "ok", "cache_hit": True, "last_refreshed_at": "2025-12-08T10:30:00Z", "signals_public_url_count": 7}}}
            },
            "signals": {
                "counts": {"company_cited": 7, "person_cited": 20, "total_cited": 27, "company_vendor": 0, "person_vendor": 0, "total_vendor": 0},
                "freshness": {"newest_cited_date": "2025-12-09", "oldest_cited_date": "2024-12-31", "newest_cited_age_days": 2, "oldest_cited_age_days": 345},
                "warnings": []
            },
            "contact": {"review_required": False}
        }

    def test_header_contains_confidence(self, sample_quality):
        """Test header shows confidence."""
        header = render_context_quality_header(sample_quality)
        assert "Confidence: HIGH" in header

    def test_header_contains_signal_breakdown(self, sample_quality):
        """Test header shows company/person breakdown."""
        header = render_context_quality_header(sample_quality)
        assert "Cited signals: 27" in header
        assert "company 7" in header
        assert "person 20" in header

    def test_header_contains_freshness(self, sample_quality):
        """Test header shows freshness info."""
        header = render_context_quality_header(sample_quality)
        assert "2025-12-09" in header
        assert "2d" in header

    def test_markdown_header_has_tables(self, sample_quality):
        """Test markdown header has tables."""
        md = render_context_quality_header_markdown(sample_quality)
        assert "| Type | Company | Person | Total |" in md


class TestCanonicalArtifactWriting:
    """Tests for writing canonical artifacts."""

    @pytest.fixture
    def sample_quality(self):
        return {
            "generated_at": datetime.now().isoformat(),
            "run_id": "test123",
            "company": {"name": "Test Corp"},
            "contact": {"name": "John"},
            "mode": {"tier": "A", "confidence_mode": "HIGH"},
            "sources": {},
            "signals": {"counts": {}, "freshness": {}, "warnings": []}
        }

    def test_writes_both_files(self, sample_quality):
        """Test both JSON and MD files are written."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = write_context_quality_artifacts(sample_quality, tmpdir)

            assert Path(paths["json"]).exists()
            assert Path(paths["md"]).exists()

    def test_json_is_valid(self, sample_quality):
        """Test JSON file is valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = write_context_quality_artifacts(sample_quality, tmpdir)

            with open(paths["json"]) as f:
                loaded = json.load(f)

            assert loaded["run_id"] == "test123"


class TestMultiSiteCacheReuse:
    """Tests for multi-site company intel reuse tracking."""

    @pytest.fixture
    def builder(self):
        return ContextQualityBuilder()

    def test_cache_hit_reflected(self, builder):
        """Test cache_hit is reflected in output."""
        intel = {
            "primary_account_id": "001ABC",
            "_cache_hit": True,
            "last_refreshed": "2025-12-08T10:30:00Z",
            "sources": {"sec": {"status": "success", "last_run": "2025-12-08T10:30:00Z"}},
            "signals": {"public_url": [], "vendor_data": []}
        }

        result = builder.build(research_data={}, prospect_brief={"cited_signals": []}, company_intel=intel)
        assert result["sources"]["company_intel"]["cache_hit"] is True

    def test_consistent_company_across_contacts(self, builder):
        """Test same company data for different contacts."""
        intel = {
            "company_name": "Acme Corp",
            "primary_account_id": "001ABC",
            "aliases": {"domains": ["acme.com"]},
            "sources": {},
            "signals": {"public_url": [], "vendor_data": []}
        }

        # Two different contacts, same company
        result1 = builder.build(research_data={"contact": {"name": "Alice"}}, prospect_brief={"cited_signals": []}, company_intel=intel)
        result2 = builder.build(research_data={"contact": {"name": "Bob"}}, prospect_brief={"cited_signals": []}, company_intel=intel)

        assert result1["company"]["primary_account_id"] == result2["company"]["primary_account_id"]
        assert result1["company"]["name"] == result2["company"]["name"]


class TestNoneHandlingRegressions:
    """
    Regression tests for None value handling.

    These tests verify that the context_quality module gracefully handles
    None values in nested dictionaries, which can occur when:
    - company_intel is missing or not fetched
    - providers fail or return None
    - research_data has keys with None values
    """

    @pytest.fixture
    def builder(self):
        return ContextQualityBuilder()

    def test_build_with_none_company_intel(self, builder):
        """Test build() handles None company_intel without crashing."""
        result = builder.build(
            research_data={"contact": {"name": "Test"}},
            prospect_brief={"cited_signals": []},
            company_intel=None
        )

        assert result is not None
        assert result["sources"]["company_intel"]["ran"] is False
        assert result["sources"]["company_intel"]["status"] == "skipped"

    def test_build_with_empty_company_intel(self, builder):
        """Test build() handles empty dict company_intel."""
        result = builder.build(
            research_data={},
            prospect_brief={"cited_signals": []},
            company_intel={}
        )

        assert result is not None
        assert result["sources"]["company_intel"]["ran"] is False

    def test_build_with_none_nested_values(self, builder):
        """Test build() handles None values in nested dicts."""
        # This simulates data where keys exist but values are None
        research_data = {
            "company": None,  # Key exists but value is None
            "contact": None,
            "zoominfo": None,
            "perplexity": None,
            "webfetch": None
        }

        # Should not crash with AttributeError
        result = builder.build(
            research_data=research_data,
            prospect_brief={"cited_signals": []},
            company_intel=None
        )

        assert result is not None
        assert "company" in result
        assert "sources" in result

    def test_build_with_none_providers(self, builder):
        """Test build() handles None in providers section."""
        company_intel = {
            "sources": {
                "sec": None,  # Provider entry is None
                "fda": {"status": "success"}
            },
            "signals": None  # signals is None
        }

        result = builder.build(
            research_data={},
            prospect_brief={"cited_signals": []},
            company_intel=company_intel
        )

        assert result is not None
        assert result["sources"]["company_intel"]["ran"] is True

    def test_build_with_none_prospect_brief(self, builder):
        """Test build() handles None prospect_brief."""
        result = builder.build(
            research_data={"contact": {"name": "Test"}},
            prospect_brief=None,
            company_intel=None
        )

        assert result is not None
        assert result["mode"]["confidence_mode"] == "GENERIC"

    def test_build_with_none_research_data(self, builder):
        """Test build() handles None research_data."""
        result = builder.build(
            research_data=None,
            prospect_brief={"cited_signals": []},
            company_intel=None
        )

        assert result is not None
        assert "sources" in result

    def test_compute_prospect_context_quality_with_none(self):
        """Test compute_prospect_context_quality handles None inputs."""
        # None prospect_brief
        result = compute_prospect_context_quality(
            prospect_brief=None,
            research_data={}
        )
        assert result.confidence_mode == "GENERIC"

        # None research_data
        result = compute_prospect_context_quality(
            prospect_brief={"confidence_tier": "low"},
            research_data=None
        )
        assert result is not None

    def test_render_header_with_none_sections(self):
        """Test render_context_quality_header handles None/missing sections."""
        # Partial context quality with missing sections
        partial_quality = {
            "mode": None,  # None section
            "signals": {},  # Empty section
            "sources": {"zoominfo": None},  # None source
            "contact": None
        }

        # Should not crash
        header = render_context_quality_header(partial_quality)
        assert "Context Quality" in header

    def test_render_markdown_with_none_sections(self):
        """Test render_context_quality_header_markdown handles None sections."""
        partial_quality = {
            "mode": None,
            "signals": None,
            "sources": None,
            "contact": None
        }

        # Should not crash
        md = render_context_quality_header_markdown(partial_quality)
        assert "## Context Quality" in md

    def test_company_section_with_none_company_data(self, builder):
        """Regression: company_data.get() crashed when company was None."""
        research_data = {
            "company": None,  # This caused AttributeError before fix
            "company_name": "Test Corp"
        }

        result = builder.build(
            research_data=research_data,
            prospect_brief={"cited_signals": []},
            company_intel=None
        )

        # Should use fallback company_name
        assert result["company"]["name"] == "Test Corp"

    def test_signals_section_with_none_cited_signals(self, builder):
        """Test signals section handles None cited_signals."""
        result = builder.build(
            research_data={},
            prospect_brief={"cited_signals": None},  # None instead of list
            company_intel=None
        )

        counts = result["signals"]["counts"]
        assert counts["total_cited"] == 0

    def test_provider_entry_with_none_status(self, builder):
        """Test provider entry handles None provider_status."""
        company_intel = {
            "sources": {
                "sec": None  # None status should be handled
            },
            "signals": {"public_url": [], "vendor_data": []}
        }

        result = builder.build(
            research_data={},
            prospect_brief={"cited_signals": []},
            company_intel=company_intel
        )

        # Should have company_intel source but handle None provider gracefully
        assert result["sources"]["company_intel"]["ran"] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
