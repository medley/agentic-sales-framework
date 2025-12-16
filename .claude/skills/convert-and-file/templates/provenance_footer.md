
# Provenance Footer Template

Use this template at the end of all converted knowledge files.

## Standard Format

```markdown
---

## Provenance

source_paths:
  - "sample-data/input/path/to/source1.pdf"
  - "sample-data/input/path/to/source2.docx"

converted_by: convert_and_file
converted_at: {{YYYY-MM-DD}}
stage_ref: ../../_Shared/knowledge/stage_inventory.md
augmentation_notice: >
  Sections under **Augmentation (LLM-inferred)** contain general guidance not
  explicitly present in source documents. Review before adoption.
```

## Field Definitions

### Required Fields

**source_paths:**
- List ALL source files used in conversion
- Use relative paths from project root or absolute paths
- Include page numbers if specific pages used: `"file.pdf (pp. 15-23)"`
- For web sources, use full URL

**converted_by:**
- Always: `convert_and_file`
- For parallel processing: `convert_and_file (parallel agent analysis)`

**converted_at:**
- ISO 8601 date format: YYYY-MM-DD
- Use actual conversion date, not placeholder

### Optional Fields

**stage_ref:**
- Relative path to relevant stage inventory
- Default: `../../_Shared/knowledge/stage_inventory.md`
- Methodology-specific: `../../_Shared/knowledge/methodologies/{name}/stage_inventory__{name}.md`

**augmentation_notice:**
- Standard notice about LLM-inferred content
- Customize if specific augmentation types need highlighting

**Additional Custom Fields:**
- `methodology: "Sandler Selling System"` - For methodology-specific files
- `version: "1.0"` - For versioned documents
- `reviewed_by: "user@company.com"` - If user has validated output
- `validation_notes: "Pricing data from 2023, confirm current"` - Important caveats
- `agents_used: 5` - For parallel agent processing
- `deal_ref: "../../deal.md"` - For deal-specific conversions

## Examples

### Example 1: Single Source File
```markdown
---

## Provenance

source_paths:
  - "sample-data/input/playbooks/acme_sales_playbook.pdf"

converted_by: convert_and_file
converted_at: 2025-11-11
stage_ref: ../../_Shared/knowledge/stage_inventory.md
augmentation_notice: >
  Sections under **Augmentation (LLM-inferred)** contain general guidance not
  explicitly present in source documents. Review before adoption.
validation_notes: "Pricing data from 2023, confirm current before use"
```

### Example 2: Multiple Sources, Parallel Processing
```markdown
---

## Provenance

source_paths:
  - "sample-data/input/playbooks/methodologies/Sandler/Sales Mastery Workbook-20190722/2019_sandler_01_why_have_a_system_sales_mastery.pdf"
  - "sample-data/input/playbooks/methodologies/Sandler/Sales Mastery Workbook-20190722/2019_sandler_03_up_front_contracts_sales_mastery.pdf"
  - "sample-data/input/playbooks/methodologies/Sandler/Sales Mastery Workbook-20190722/2019_sandler_05_pain_sales_mastery.pdf"
  - "sample-data/input/playbooks/methodologies/Sandler/Sales Mastery Workbook-20190722/2019_sandler_06_budget_sales_mastery.pdf"
  - "sample-data/input/playbooks/methodologies/Sandler/Sales Mastery Workbook-20190722/2019_sandler_07_decision_sales_mastery.pdf"
  - [... 14 more source files ...]

converted_by: convert_and_file (parallel agent analysis)
converted_at: 2025-11-11
agents_used: 5
methodology: "Sandler Selling System"
stage_ref: ../../stage_inventory.md
augmentation_notice: >
  Sections under **Augmentation (LLM-inferred)** contain general guidance and
  crosswalk mapping not explicitly present in source documents. The core stage
  definitions, exit criteria, artifacts, and indicators are extracted directly
  from Sandler source materials. Review crosswalk mapping before applying to
  deals, as it represents interpretation of how Sandler maps to default inventory.
```

### Example 3: Deal-Specific Conversion
```markdown
---

## Provenance

source_paths:
  - "sample-data/input/deals/acmepharma/discovery_notes_2025-11-08.txt"
  - "sample-data/input/deals/acmepharma/stakeholder_email_thread.pdf"

converted_by: convert_and_file
converted_at: 2025-11-11
deal_ref: ../../deal.md
stage_ref: ../../_Shared/knowledge/stage_inventory.md
augmentation_notice: >
  "Recommended Follow-Up" section contains LLM-inferred suggestions based on
  Sandler Pain stage criteria. Validate with actual customer context before use.
```

### Example 4: Web Source
```markdown
---

## Provenance

source_paths:
  - "https://example.com/sales-methodology-guide"
  - "sample-data/input/playbooks/internal_notes.md"

converted_by: convert_and_file
converted_at: 2025-11-11
stage_ref: ../../_Shared/knowledge/stage_inventory.md
augmentation_notice: >
  Sections under **Augmentation (LLM-inferred)** contain general guidance not
  explicitly present in source documents. Review before adoption.
last_web_fetch: 2025-11-11
```

## Troubleshooting

**Problem:** Relative path to stage_ref doesn't work
**Solution:** Count directory levels from output file to target
```
Output: sample-data/Runtime/_Shared/knowledge/methodologies/Sandler/stage_inventory__Sandler.md
Target: sample-data/Runtime/_Shared/knowledge/stage_inventory.md
Path: ../../stage_inventory.md (up 2 levels: methodologies/ and Sandler/)
```

**Problem:** Too many source files to list
**Solution:** Group by directory with wildcard notation
```yaml
source_paths:
  - "sample-data/input/playbooks/methodologies/Sandler/Sales Mastery Workbook-20190722/*.pdf (19 files)"
  - "sample-data/input/playbooks/methodologies/Sandler/Sales Mastery Tool Kit-20190722/*.pdf (8 files)"
```

**Problem:** Source no longer exists
**Solution:** Note in validation or add field
```yaml
validation_notes: "Source file was in input/ but has been archived/deleted since conversion"
```
