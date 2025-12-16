# Promotion Rules and Batch Rendering - Phase 2

## Overview

Phase 2 adds lifecycle control and safe automation enablement:

1. **Promotion Rules** - Gates for moving artifacts from Prospecting → Accounts
2. **Batch Rendering** - Opt-in automated email rendering
3. **Multi-Site Validation** - Verification of company intel reuse

## Prospect Lifecycle States

| State | Description |
|-------|-------------|
| `prepared_for_rendering` | Hybrid system ran, draft context ready |
| `rendered_validated` | render_and_validate.py passed |
| `sent_manual` | Email manually sent (external action) |
| `replied` | Prospect replied (external action) |
| `promoted` | Artifacts moved to 01_Accounts/_Active |
| `rejected` | System or user rejected |
| `review_required` | Manual review needed before proceeding |

## Promotion Rules

### Eligibility Gates

Promotion from `02_Prospecting` → `01_Accounts/_Active` is allowed only if:

| Gate | Requirement |
|------|-------------|
| Status | `rendered_validated` |
| Validation | Passed |
| Confidence | Not `GENERIC` |
| Review | `review_required == false` (unless --force) |
| Forbidden Products | No violations |
| Warnings | No `THIN_RESEARCH` or `VENDOR_DATA_ONLY` |

### Blocking Warnings

These warnings **cannot** be overridden with `--force`:

- `THIN_RESEARCH` - Insufficient signals and stale data
- `VENDOR_DATA_ONLY` - No citable sources available

### What Gets Promoted

When promoting, the following files are copied:

```
01_Accounts/_Active/{company}/prospecting/{contact}/
├── {date}_{contact}_email.md          # Final rendered email
├── {date}_{contact}_context_quality.json
├── {date}_{contact}_context_quality.md
├── research_summary.md                 # Generated summary
└── promotion_metadata.json             # Run metadata
```

**NOT promoted**: Raw research dumps, caches, debug files

### CLI Usage

```bash
# Standard promotion
python scripts/promote_prospecting_artifacts.py \
    --company "Acme Corp" \
    --contact "John Smith"

# Dry run (preview only)
python scripts/promote_prospecting_artifacts.py \
    --company "Acme Corp" \
    --contact "John Smith" \
    --dry_run

# Force (override review_required after human review)
python scripts/promote_prospecting_artifacts.py \
    --company "Acme Corp" \
    --contact "John Smith" \
    --force

# Custom target
python scripts/promote_prospecting_artifacts.py \
    --company "Acme Corp" \
    --contact "John Smith" \
    --target_root "/path/to/accounts"
```

## Batch Rendering

### Eligibility Gates

Batch rendering is opt-in and allowed only if:

| Gate | Requirement |
|------|-------------|
| Review | `review_required == false` |
| Confidence | `HIGH` or `MEDIUM` |
| Signals | `total_cited >= 2` |
| Warnings | No `THIN_RESEARCH` or `OLD_SIGNALS_PRESENT` |
| Automation | `persona.automation_allowed == true` |

### Regulatory Persona

**Regulatory persona is NEVER batch rendered.** This is a hard safety constraint that cannot be overridden with `--force`.

Regulatory communications require individual human review before sending due to compliance requirements.

### Orchestrator Flags

```python
config = OutboundConfig(
    accounts_path=Path("accounts.csv"),
    render_emails=True,          # Enable batch rendering
    render_policy="strict"       # "strict" (default) or "permissive"
)
```

### CLI Usage

```bash
# Run orchestrator with batch rendering
python scripts/run_orchestrator.py \
    --accounts accounts.csv \
    --render_emails \
    --render_policy strict
```

### Dashboard Output

The orchestrator dashboard now includes:

| Column | Description |
|--------|-------------|
| Rend | Y/N/N* (rendered, not rendered, skip reason exists) |
| Promo | Y/N (promotion eligible) |

Example row:
```
| John Smith | VP Quality | prepared_for_rendering | HIGH | 5 | 3 | 30d | N* | N | - |
```

## Multi-Site Validation

### Purpose

Validates that company intel is fetched once and reused across contacts at different site accounts under the same Primary Account ID.

### What is Validated

1. **Cache Hit Behavior**
   - First contact: `cache_hit = false` (fresh fetch)
   - Subsequent contacts: `cache_hit = true` (reused)

2. **Signal Consistency**
   - Company cited signal counts are identical across contacts

3. **Persona Independence**
   - Different contacts can have different personas
   - Product motion varies per persona

4. **Review Rules**
   - Ambiguity → `review_required = true`
   - Regulatory persona → `review_required = true`, `automation_allowed = false`

### Test Fixtures

```python
from src.multisite_validator import MultisiteTestFixture

# Default fixture (two contacts, different personas)
fixture = MultisiteTestFixture.create_default()

# Same persona fixture
fixture = MultisiteTestFixture.create_same_persona()
```

### Running Validation

```python
from src.multisite_validator import MultisiteValidator, write_validation_report

validator = MultisiteValidator()
report = validator.validate_from_context_quality(fixture, context_qualities)

if report.all_passed:
    print("All validations passed")
else:
    for result in report.contact_results:
        if not result.passed:
            print(f"{result.contact_name}: {result.get_failures()}")

# Write report
report_path = write_validation_report(report)
```

### Report Output

Reports are written to:
```
runs/YYYY-MM-DD_multisite_validation.md
```

Report includes:
- Test fixture details
- Per-contact validation results
- Cache behavior summary
- Persona/product comparison table

## Testing

Run Phase 2 tests:
```bash
python -m pytest tests/test_phase2.py -v
```

Test coverage includes:
- `TestPromotionGate` - 8 tests for promotion eligibility
- `TestBatchRenderGate` - 8 tests for batch render eligibility
- `TestMultisiteValidator` - 5 tests for multi-site behavior
- `TestPromotionState` - 5 tests for state determination
- `TestEligibilityReport` - 2 tests for report formatting
- `TestForceOverrides` - 4 tests for --force behavior

## Design Constraints

This phase does NOT modify:
- Persona detection logic
- Product eligibility logic
- Confidence calculation logic
- Context quality schema or warnings
- Company intel providers

All changes are additive: behavior verification, lifecycle control, and automation enablement.
