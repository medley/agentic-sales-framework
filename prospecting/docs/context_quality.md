# Context Quality - Phase 1 Visibility Layer

## Overview

The Context Quality system makes data quality **visible** across all prospecting outputs. It surfaces:

- Signal counts by type (cited vs vendor, company vs person)
- Data freshness (newest/oldest signal ages)
- Source status (ZoomInfo, Perplexity, WebFetch, Company Intel)
- Warnings for quality issues

This is a **presentation/observability layer only** - it does NOT gate or block outputs.

## Canonical Schema

All context quality data follows this authoritative JSON schema:

```json
{
  "generated_at": "2025-12-11T10:30:00",
  "run_id": "abc123",
  "company": {
    "name": "Acme Corp",
    "primary_account_id": "001ABC123",
    "site_account_id": null,
    "domain": "acme.com"
  },
  "contact": {
    "name": "John Smith",
    "title": "VP Quality",
    "persona": "quality",
    "persona_confidence": "high",
    "ambiguity_detected": false,
    "review_required": false,
    "review_reasons": []
  },
  "mode": {
    "tier": "A",
    "confidence_mode": "HIGH",
    "confidence_notes": []
  },
  "sources": {
    "zoominfo": {
      "ran": true,
      "status": "ok",
      "found_contact": true,
      "found_email": true,
      "found_phone": false,
      "errors": []
    },
    "perplexity": {
      "ran": true,
      "status": "ok",
      "citations_count": 5,
      "cited_claims_count": 3,
      "errors": []
    },
    "webfetch": {
      "ran": false,
      "status": "skipped",
      "pages_fetched": 0,
      "errors": []
    },
    "company_intel": {
      "ran": true,
      "status": "ok",
      "cache_hit": true,
      "last_refreshed_at": "2025-12-10T10:30:00Z",
      "providers": {
        "sec": {
          "ran": true,
          "status": "ok",
          "cache_hit": true,
          "last_refreshed_at": "2025-12-10T10:30:00Z",
          "expires_at": "2026-01-09T10:30:00Z",
          "signals_public_url_count": 5,
          "signals_vendor_data_count": 0,
          "newest_as_of_date": "2024-12-31",
          "oldest_as_of_date": "2024-03-15",
          "errors": []
        }
      },
      "errors": []
    }
  },
  "signals": {
    "counts": {
      "company_cited": 5,
      "company_vendor": 0,
      "person_cited": 2,
      "person_vendor": 3,
      "total_cited": 7,
      "total_vendor": 3
    },
    "freshness": {
      "newest_cited_date": "2025-01-15",
      "oldest_cited_date": "2024-06-01",
      "newest_cited_age_days": 30,
      "oldest_cited_age_days": 200
    },
    "warnings": [
      "OLD_SIGNALS_PRESENT: oldest cited signal is 200 days old"
    ]
  },
  "artifacts": {
    "email_context": "/path/to/email_context.json",
    "email_md": "/path/to/email.md",
    "context_quality_json": "/path/to/context_quality.json"
  }
}
```

## Warning Codes

| Code | Meaning |
|------|---------|
| `OLD_SIGNALS_PRESENT` | Oldest cited signal > 365 days old |
| `COMPANY_INTEL_STALE` | Company intel provider data expired |
| `NO_CITED_SIGNALS` | No verifiable signals found |
| `VENDOR_DATA_ONLY` | Only vendor data available, cannot cite sources |
| `REVIEW_REQUIRED` | Persona or content requires manual review |
| `THIN_RESEARCH` | Few signals (<3) and oldest > 90 days |

## Signal Classification

Signals are classified by two dimensions:

### By Scope
- **Company-level**: From company intel (SEC filings, company news)
- **Person-level**: From contact research (LinkedIn, Perplexity)

### By Citability
- **Cited (public_url, user_provided)**: Can make explicit claims
- **Vendor (vendor_data)**: Guidance only, cannot cite in email

## Usage

### Building Context Quality

```python
from context_quality import ContextQualityBuilder

builder = ContextQualityBuilder()
context_quality = builder.build(
    research_data=research_data,
    prospect_brief=prospect_brief,
    company_intel=company_intel,  # Optional
    persona_result=persona_diagnostics,  # Optional
    confidence_result=confidence_diagnostics  # Optional
)
```

### Rendering Headers

```python
from context_quality import (
    render_context_quality_header,
    render_context_quality_header_markdown
)

# For CLI output
print(render_context_quality_header(context_quality))

# For saved deliverables
md_content = render_context_quality_header_markdown(context_quality)
```

### Writing Artifacts

```python
from context_quality import write_context_quality_artifacts

paths = write_context_quality_artifacts(
    context_quality,
    output_dir="/path/to/drafts"
)
# Returns: {"json": "/path/to/context_quality.json", "md": "/path/to/context_quality.md"}
```

### Path Resolution

```python
from path_resolver import (
    get_context_quality_json_path,
    get_context_quality_md_path,
    get_deliverables_paths
)

# Get individual paths
json_path = get_context_quality_json_path("Acme", "John Smith")
md_path = get_context_quality_md_path("Acme", "John Smith")

# Get all deliverable paths at once
paths = get_deliverables_paths("Acme", "John Smith")
# Returns dict with: drafts_folder, email_file, inmail_file, sequence_file,
#                    context_quality_json, context_quality_md
```

## Orchestrator Dashboard

The outbound orchestrator dashboard now includes:

| Column | Description |
|--------|-------------|
| Confidence | Confidence mode (HIGH/MEDIUM/LOW/GENERIC) |
| Cited | Total cited signals |
| Co. | Company-level cited signals |
| Fresh | Newest cited signal age in days |
| Warnings | Warning codes (first 2, plus count of additional) |

Example dashboard row:
```
| John Smith | VP Quality | prepared_for_rendering | HIGH | 7 | 5 | 30d | OLDSIGNALSPRESENT |
```

## Multi-Site Reuse

When processing multiple contacts at the same company:

1. First contact fetches company intel (cache_hit: false)
2. Subsequent contacts reuse cached intel (cache_hit: true)
3. All contacts see same company-level signals
4. Dashboard shows cache_hit status per provider

This is validated by the `TestMultiSiteCacheReuse` tests.

## File Structure

Deliverables are written to:
```
{PROSPECTING_OUTPUT_ROOT}/{company}/drafts/
├── {date}_{contact}_email_context.json  # Full context for Claude Code
├── {date}_{contact}_email.md            # Email plan
├── {date}_{contact}_inmail.md           # InMail draft (if applicable)
├── {date}_{contact}_sequence.md         # Cadence sequence (if applicable)
├── {date}_{contact}_context_quality.json # Canonical quality metadata
└── {date}_{contact}_context_quality.md   # Human-readable quality report
```

## Testing

Run context quality tests:
```bash
python -m pytest tests/test_context_quality.py -v
```

Test coverage includes:
- Canonical schema creation (`TestContextQualityBuilder`)
- Warning generation (`TestCanonicalWarnings`)
- Header rendering (`TestCanonicalHeaderRendering`)
- Artifact writing (`TestCanonicalArtifactWriting`)
- Multi-site cache reuse (`TestMultiSiteCacheReuse`)

## Design Constraints

This layer is **visibility only**:
- Does NOT modify confidence logic
- Does NOT modify persona detection
- Does NOT modify signal extraction
- Does NOT gate or block outputs

All warnings are surfaced for human review but do not automatically reject drafts.
