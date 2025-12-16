---
name: "frontmatter_specification"
type: "system_protocol"
owner: "Welf Ludwig"
version: "1.0.0"
license: "MIT - See LICENSE.md"
---

# Frontmatter Specification

Single source of truth for YAML frontmatter schemas used across the Agentic Sales Framework.

This file lives in:
`Framework/System/frontmatter_spec.md`

It is **documentation**, not code. Skills follow these schemas when generating or converting files.

---

## 1. Purpose

All markdown files in the framework must include YAML frontmatter for:
- **Provenance:** Trace outputs back to generating skill and source files
- **Filtering:** Enable downstream tools (Obsidian, scripts) to query by type/date/deal
- **Validation:** Ensure completeness and consistency across artifacts
- **Portability:** Files can be moved/shared while maintaining context

---

## 2. Generated Content Frontmatter

**Applies to:** Files created by skills (briefings, emails, agendas, summaries)

### Required Fields

```yaml
---
generated_by: {skill_name}
generated_on: {ISO_TIMESTAMP}
deal_id: {deal_name}
call_type: {discovery|demo|negotiation|handover|exec|status|other}
sources:
  - "{file_path_1}"
  - "{file_path_2}"
---
```

### Field Definitions

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `generated_by` | string | **Yes** | Name of skill that created this file | `coach`, `deal-intake`, `email_generator` |
| `generated_on` | ISO 8601 timestamp | **Yes** | When file was created (UTC) | `2025-11-13T14:30:00Z` |
| `deal_id` | string | **Yes** | Deal name (must match session folder) | `AcmeCorp`, `TechCoInc` |
| `call_type` | enum | **Yes** | Type of interaction or artifact | `discovery`, `demo`, `negotiation`, `status`, `other` |
| `sources` | array of strings | **Yes** | File paths consulted during generation (relative or absolute) | `sample-data/Runtime/Sessions/TechCoInc/deal.md` |

### Optional Extension Fields

Skills may add custom fields as needed, but MUST NOT omit the core required fields above.

Common extensions:
- `artifact_type` (string): Specific artifact subtype (e.g., `call_summary`, `email_summary`, `quote_snapshot`)
- `methodology` (string): Methodology applied (e.g., `Sandler`, `MEDDPICC`)
- `stage` (integer): Deal stage number
- `recipient` (string): For emails, the intended recipient
- `focus_areas` (array): Specific topics emphasized in this artifact

### Examples

#### Coach Skill Briefing
```yaml
---
generated_by: coach
generated_on: 2025-11-12T14:30:00Z
deal_id: TechCoInc
call_type: discovery
methodology: Sandler
stage: 2
sources:
  - sample-data/Runtime/Sessions/TechCoInc/deal.md
  - sample-data/Runtime/_Shared/knowledge/persona_cfo_pharma.md
  - sample-data/Runtime/_Shared/knowledge/methodologies/Sandler/stage_inventory__Sandler.md
---
```

#### Deal Intake Call Summary
```yaml
---
generated_by: deal_intake
generated_on: 2025-11-13T09:15:00Z
deal_id: AcmeCorp
call_type: demo
artifact_type: call_summary
sources:
  - sample-data/Runtime/Sessions/AcmeCorp/raw/calls/2025-11-12_demo_transcript.txt
---
```

#### Email Generator Output
```yaml
---
generated_by: email_generator
generated_on: 2025-11-13T16:45:00Z
deal_id: AcmePharma
call_type: status
artifact_type: follow_up_email
recipient: "Sarah Chen (VP Operations)"
sources:
  - sample-data/Runtime/Sessions/AcmePharma/deal.md
  - sample-data/Runtime/Sessions/AcmePharma/artifacts/calls/2025-11-10_discovery_summary.md
---
```

---

## 3. Converted Content Frontmatter

**Applies to:** Files created by `convert_and_file` skill from source materials

### Required Fields

```yaml
---
source_path: {original_file_path}
source_type: {pdf|docx|xlsx|txt|md}
converted_on: {ISO_DATE}
doc_type: {playbook|persona|battlecard|stage_guide|product|case_study|other}
confidence: {high|medium|low}
validation:
  freshness_hint: "{last_updated_info or empty}"
  findings: ["{issue1}", "{issue2}"]
augmentation:
  scope: "{brief_description}"
  additions: ["{topic1}", "{topic2}"]
gaps:
  questions: ["{question1}", "{question2}"]
  suggested_sources: ["{source1}", "{source2}"]
---
```

### Field Definitions

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `source_path` | string | **Yes** | Original file path before conversion | `sample-data/input/playbooks/sales_playbook_2024.pdf` |
| `source_type` | enum | **Yes** | File type of original | `pdf`, `docx`, `xlsx`, `txt`, `md` |
| `converted_on` | ISO 8601 date | **Yes** | When conversion occurred | `2025-11-13` |
| `doc_type` | enum | **Yes** | Category of content | `playbook`, `persona`, `battlecard`, `stage_guide`, `product`, `case_study`, `other` |
| `confidence` | enum | **Yes** | Quality assessment | `high`, `medium`, `low` |
| `validation` | object | **Yes** | Quality checks and findings | See below |
| `augmentation` | object | **Yes** | LLM-added content tracking | See below |
| `gaps` | object | **Yes** | Missing information | See below |

#### Validation Object

```yaml
validation:
  freshness_hint: "Last updated Q3 2024"  # or "" if unknown
  findings:
    - "Source refers to DISC profiles but doesn't define DISC types"
    - "Page 23 shows 7 stages; page 45 shows 6 stages (discrepancy)"
```

#### Augmentation Object

```yaml
augmentation:
  scope: "Added generic discovery best practices and stage mapping"
  additions:
    - "Multi-threading importance"
    - "Champion criteria"
    - "Crosswalk to Generic stage inventory"
```

#### Gaps Object

```yaml
gaps:
  questions:
    - "What's the typical sales cycle length?"
    - "Who are key competitors?"
  suggested_sources:
    - "Product roadmap document"
    - "Competitive analysis deck"
```

### Confidence Levels

- **high**: Source is official, recent (< 6 months), and complete
- **medium**: Source is older (6-18 months) or incomplete but usable
- **low**: Source is outdated (> 18 months), fragmented, or questionable

### Example

#### Converted Methodology Document
```yaml
---
source_path: sample-data/input/methodologies/sandler_selling_system.pdf
source_type: pdf
converted_on: 2025-11-12
doc_type: stage_guide
confidence: high
validation:
  freshness_hint: "Published 2023, no updates mentioned"
  findings:
    - "Budget discussion techniques reference 'Monkey's Paw' without full explanation"
augmentation:
  scope: "Added general B2B sales context and question framework examples"
  additions:
    - "Generic stage mapping for non-Sandler deals"
    - "Exit criteria best practices"
gaps:
  questions:
    - "Are there industry-specific variations of Sandler stages?"
  suggested_sources:
    - "Advanced Sandler training materials"
---
```

---

## 4. Extension Guidelines

When skills need to add custom frontmatter fields:

### Do's
- Add fields that enhance filtering/querying (e.g., `artifact_type`, `recipient`)
- Use snake_case for field names
- Use standard types (string, integer, boolean, array, object)
- Document custom fields in skill spec
- Preserve all core required fields

### Don'ts
- Omit or rename core required fields
- Use camelCase or PascalCase (use snake_case)
- Embed large objects (keep frontmatter concise)
- Duplicate information already in core fields
- Add sensitive data (passwords, API keys)

### Example Custom Extensions

#### prep_discovery skill adds:
```yaml
attendees:
  - "Alex Johnson (VP Sales)"
  - "Sarah Chen (CFO)"
focus_areas:
  - "budget_qualification"
  - "decision_process"
```

#### portfolio skill adds:
```yaml
deals_analyzed: 12
risk_threshold: "high"
generated_for: "weekly_pipeline_review"
```

---

## 5. Validation Rules

Tools and scripts can validate frontmatter using these rules:

### Generated Content
1. All 5 core fields must be present: `generated_by`, `generated_on`, `deal_id`, `call_type`, `sources`
2. `generated_on` must be valid ISO 8601 timestamp
3. `call_type` must be one of: discovery, demo, negotiation, handover, exec, status, other
4. `sources` must be non-empty array
5. `deal_id` should match existing deal folder under `sample-data/Runtime/Sessions/`

### Converted Content
1. All 7 core fields must be present: `source_path`, `source_type`, `converted_on`, `doc_type`, `confidence`, `validation`, `augmentation`, `gaps`
2. `converted_on` must be valid ISO 8601 date (YYYY-MM-DD)
3. `confidence` must be one of: high, medium, low
4. `validation`, `augmentation`, and `gaps` must be objects (not null)

---

## 6. Cross-References

This spec is referenced by:
- `CLAUDE.md` (bootstrap spec)
- `Framework/System/DEVELOPER_GUIDE.md` (development protocols)
- `.claude/skills/*/SKILL.md` (skill specifications)

When updating this spec, ensure all cross-references remain consistent.

---

## 7. Version History

- **1.0.0** (2025-11-13): Initial specification created as single source of truth for frontmatter schemas
