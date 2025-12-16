# Outbound Orchestrator Implementation Plan

## Overview

Build an outbound orchestrator that consumes ranked account lists and generates bounded draft emails by calling the existing `/prospect` pipeline.

## Module Boundaries

### 1. `src/outbound_orchestrator.py` - Core Logic

**Classes:**
- `OutboundOrchestrator`: Main orchestrator class
- `AccountRecord`: Data class for account input records
- `RunResult`: Data class for run dashboard data
- `DraftResult`: Data class for individual draft results

**Key Methods:**
- `load_accounts(filepath: Path) -> List[AccountRecord]`: Load CSV or JSON
- `select_accounts(accounts, top_n, tier) -> List[AccountRecord]`: Filter/sort by score/tier
- `should_skip_account(account, since_days) -> Tuple[bool, str]`: Check recent drafts
- `get_personas_for_account(account) -> List[str]`: Deterministic persona mapping
- `find_contacts(company_name, personas) -> List[dict]`: ZoomInfo role search
- `run_prospect_pipeline(company, contact, tier, mode, exp) -> DraftResult`: Core pipeline call
- `verify_draft_quality(draft_path) -> Tuple[bool, List[str]]`: Quality gate checks
- `run(config) -> RunResult`: Main orchestration loop

**Dependencies (existing):**
- `src.path_resolver`: For all paths (`get_prospecting_root`, `get_company_folder`, `get_drafts_folder`)
- `src.zoominfo_client`: For `search_contacts_by_role` (graceful degradation if unavailable)
- `src.hybrid_email_generator`: For running the prospect pipeline
- `src.validators`: For deterministic validation
- `src.context_quality`: For quality header validation

### 2. `scripts/outbound_run.py` - CLI Entrypoint

**CLI Flags:**
```
--accounts <path>           Required: Path to accounts CSV/JSON
--top_n <n>                 Default 10: Number of accounts to process
--max_drafts_per_account <n> Default 3: Cap per account
--max_total_drafts <n>      Default 20: Global cap
--tier A|B                  Default A: Prospect tier
--mode hybrid|legacy        Default hybrid: Generation mode
--exp <name>                Optional: Experiment name
--refresh none|company|contact|all  Default none: Refresh behavior (no-op v1)
--dry_run                   Flag: Show plan without execution
--since_days <n>            Default 7: Skip accounts drafted within N days
--output_root <path>        Optional: Override PROSPECTING_OUTPUT_ROOT
```

### 3. `tests/test_outbound_orchestrator.py` - Test Suite

**Test Cases:**
1. `test_load_csv_accounts`: Parse CSV format
2. `test_load_json_accounts`: Parse JSON format
3. `test_skip_recent_drafts`: Honor `--since_days`
4. `test_max_total_drafts_cap`: Stop at global limit
5. `test_max_drafts_per_account_cap`: Stop at per-account limit
6. `test_zoominfo_unavailable`: Graceful degradation, dashboard shows reason
7. `test_dashboard_creation`: Verify MD and JSON outputs in correct location

## Pipeline Integration

### How `/prospect` pipeline is called

The orchestrator will **NOT** simulate the slash command. Instead, it calls Python entrypoints directly:

```python
# 1. Research (if not using cached data)
from src.research_orchestrator import ResearchOrchestrator
research = orchestrator.research_prospect(name, company)

# 2. Email generation
from src.hybrid_email_generator import HybridEmailGenerator
generator = HybridEmailGenerator(mode=mode, tier=tier, experiment=exp)
result = generator.generate(research_data=research, n_variants=1)

# 3. Validation
from src.validators import validate_all
validation = validate_all(variant, cited_signals, constraints, confidence_mode)
```

### Artifact Locations

All outputs under `PROSPECTING_OUTPUT_ROOT`:

```
{PROSPECTING_OUTPUT_ROOT}/
├── {company_sanitized}/
│   ├── research/
│   │   └── {date}_{contact}_research.md
│   └── drafts/
│       └── {date}_{contact}_email.md
│       └── {date}_{contact}_variants.json  <-- NEW: structured output
└── runs/
    ├── YYYY-MM-DD_outbound_run.md      <-- Dashboard markdown
    └── YYYY-MM-DD_outbound_run.json    <-- Structured data
```

## Quality Gates

A draft is **accepted** only if ALL pass:

1. **Artifact exists**: `variants.json` or `variants.md` in drafts folder
2. **Context quality present**: `context_quality.json` exists with `confidence_mode` field
3. **Validation passed**: Deterministic validator status is "PASSED"
4. **Correct location**: Output is under `PROSPECTING_OUTPUT_ROOT`

Rejected drafts:
- Marked in dashboard with rejection reason
- Do NOT count toward `max_total_drafts`

## Hard Guardrails

1. Never exceed `max_total_drafts`
2. Never exceed `max_drafts_per_account`
3. Never generate drafts without contact name AND title
4. Never bypass validators
5. Never write outside `output_root`

## Persona Mapping (Deterministic)

Default personas (in priority order):
- `quality` → "quality director", "vp quality", "quality manager"
- `ops` → "operations director", "vp operations", "ops manager"
- `it` → "it director", "cio", "it manager"

If account record has `tags`, use them to reorder:
```python
PERSONA_PRIORITY = {
    'quality_focused': ['quality', 'ops', 'it'],
    'operations_focused': ['ops', 'quality', 'it'],
    'it_focused': ['it', 'ops', 'quality'],
    'default': ['quality', 'ops', 'it']
}
```

## Dashboard Format

### Markdown (`YYYY-MM-DD_outbound_run.md`)

```markdown
# Outbound Run Dashboard
**Date:** 2024-01-15
**Settings:**
- top_n: 10
- max_drafts_per_account: 3
- max_total_drafts: 20
- tier: A
- mode: hybrid
- experiment: null

## Summary
- Accounts processed: 8
- Accounts skipped: 2
- Total drafts accepted: 15
- Total drafts rejected: 3

## Accounts Processed

### 1. Acme Corp (Score: 92)
**Contacts:**
| Name | Title | Status | Draft Path | Confidence | Signals |
|------|-------|--------|------------|------------|---------|
| John Smith | Quality Director | accepted | /path/to/draft.md | HIGH | 3 |
| Jane Doe | VP Ops | rejected | - | - | reason: validation failed |

### 2. Beta Inc (Score: 88)
...

## Accounts Skipped
| Account | Reason |
|---------|--------|
| Old Corp | Draft exists within 7 days |
| No Contact Inc | ZoomInfo unavailable |
```

### JSON (`YYYY-MM-DD_outbound_run.json`)

```json
{
  "run_date": "2024-01-15",
  "settings": {
    "top_n": 10,
    "max_drafts_per_account": 3,
    "max_total_drafts": 20,
    "tier": "A",
    "mode": "hybrid",
    "experiment": null
  },
  "summary": {
    "accounts_processed": 8,
    "accounts_skipped": 2,
    "drafts_accepted": 15,
    "drafts_rejected": 3
  },
  "accounts": [
    {
      "company_name": "Acme Corp",
      "score": 92,
      "status": "processed",
      "contacts": [
        {
          "name": "John Smith",
          "title": "Quality Director",
          "status": "accepted",
          "draft_path": "/path/to/draft.md",
          "confidence_mode": "HIGH",
          "cited_signals": 3
        }
      ]
    }
  ],
  "skipped_accounts": [
    {"company_name": "Old Corp", "reason": "Draft exists within 7 days"}
  ]
}
```

## Implementation Order

1. Create `src/outbound_orchestrator.py` with core logic
2. Create `scripts/outbound_run.py` CLI
3. Create `tests/test_outbound_orchestrator.py`
4. Run tests, iterate
