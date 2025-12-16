---
name: roi-model
description: Generate customized ROI models for sales opportunities by populating Excel templates with deal-specific cost savings, investment data, and financial projections. Use when the user requests an ROI analysis, business case, or financial justification for a deal.
---

# ROI Model Generator

## Overview

Generates deal-specific ROI models in Excel by loading deal context (batch volumes, error rates, labor costs), calculating value creation using methodology-aligned savings assumptions, and populating a template with formulas for payback period, 3-year ROI, and net value calculations.

**Use this skill when:**
- User requests "ROI model", "business case", "financial justification"
- Preparing for economic buyer conversations or executive approval
- Quantifying value creation for a specific deal
- Building investment rationale for procurement review

## Workflow

### 1. Load Deal Context

Extract financial inputs from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:

**Required metrics:**
- **Annual batch volume**: Number of batches/year (e.g., 4,800)
- **Error rate**: Current documentation error rate (e.g., 5%)
- **QA reviewers**: Number of QA FTEs or hours spent on review
- **Deviations**: Planned deviations per month or year
- **Audit frequency**: Number of audits per year
- **ACV**: Annual Contract Value (solution cost)

**If missing:** Flag missing data and request from user before proceeding.

### 2. Calculate ROI Values

Use conservative savings assumptions from `Framework/Plays/value_realization.md`:

#### Current State Costs

```
QA Labor Inefficiency = QA_reviewers × avg_salary × % time on manual review
  Example: 2 FTEs × $100K × 80% = $160K

Documentation Error Cost = error_rate × batch_volume × rework_cost_per_error
  Example: 5% × 4,800 × $350 = $84K

Deviation Administrative Burden = deviation_count × hours_per_deviation × hourly_rate
  Example: 780/year × 3 hours × $30 = $70K

Audit Preparation Time = audit_count × prep_hours × hourly_rate
  Example: 26/year × 100 hours × $30 = $78K

Compliance Risk Exposure = potential_warning_letter_cost + shipment_hold_risk
  Example: $200K (conservative estimate)
```

#### Solution Value (Annual Savings)

```
QA Efficiency Savings = QA Labor Inefficiency × 80%
  (Review-by-exception vs line-by-line)

Error Elimination = Documentation Error Cost × 90%
  (Digital capture eliminates transcription errors)

Deviation Reduction = Deviation Admin Burden × 80%
  (Alternate BOM eliminates planned deviations)

Audit Efficiency = Audit Prep Time × 50%
  (Electronic records reduce prep time)

Vendor Consolidation = existing_tools_replaced × avg_cost
  (Optional: if replacing QMS/complaints tools)
```

#### Financial Summary

```
Investment (Year 1) = ACV + implementation_services
  (Implementation typically $50-75K)

Annual Value = Sum of all savings categories

Payback Period (months) = Investment ÷ (Annual Value / 12)

3-Year Net Value = (Annual Value × 3) - Investment

3-Year ROI Multiple = 3-Year Net Value ÷ Investment
```

**ROI Qualification Criteria:**
- ✅ ROI Multiple ≥ 3.0:1 (target)
- ✅ Payback Period < 12 months
- ⚠️ ROI Multiple 2.0-3.0:1 (acceptable with strong strategic value)
- ❌ ROI Multiple < 2.0:1 (challenge investment or find additional value)

### 3. Load Excel Template

Use pre-built template: `.claude/skills/roi-model/assets/roi_template.xlsx`

**Template structure (5 tabs):**
1. **Executive Summary**: Cross-sheet formulas pulling from Financial Summary
2. **Current State Costs**: Blue input cells for cost categories
3. **Solution Value**: Formulas referencing Current State × savings %
4. **Financial Summary**: Blue inputs (Investment) + black formulas (ROI calcs)
5. **Assumptions**: Documentation of methodology and color legend

**Color coding:**
- 🔵 Blue cells (#DDEEFF): User inputs (editable)
- ⚫ Black font (bold): Formulas (DO NOT EDIT)
- 🟢 Green font: Cross-sheet references (pulls from other tabs)

### 4. Populate Excel

**CRITICAL:** Only edit BLUE cells. Never modify formulas in black cells.

Use `document-skills:xlsx` skill to edit the template:

```python
# Current State Costs tab (edit blue cells only)
edit_cell('Current State Costs', 'B3', qa_labor_inefficiency)
edit_cell('Current State Costs', 'B4', documentation_error_cost)
edit_cell('Current State Costs', 'B5', deviation_admin_burden)
edit_cell('Current State Costs', 'B6', audit_prep_time)
edit_cell('Current State Costs', 'B7', compliance_risk_exposure)

# Solution Value tab (edit blue cell only - others are formulas)
edit_cell('Solution Value', 'B7', vendor_consolidation_savings)

# Financial Summary tab (edit blue cell only)
edit_cell('Financial Summary', 'B2', investment_year_1)
```

**DO NOT:**
- Edit cells with formulas (black font)
- Edit cells with cross-sheet references (green font)
- Modify tab names (will break cross-sheet formulas)
- Add/delete rows in formula ranges

### 5. Validate Formulas

Run formula validation using `scripts/recalc.py`:

```bash
python .claude/skills/roi-model/scripts/recalc.py <output_file.xlsx>
```

**Expected output:**
```
✅ Recalculated successfully
No formula errors found
```

**If errors found:**
- `#REF!`: Cross-sheet reference broken (tab renamed or cell moved)
- `#DIV/0!`: Division by zero (check Annual Value not zero)
- `#VALUE!`: Text in numeric cell (check all inputs are numbers)

**Fix strategy:** Regenerate from template rather than manual repair.

### 6. Generate Chat Output

**Purpose:** Provide a concise ROI summary for chat/UI display.

**Format:**
- Heading: `# Chat Output`
- Single markdown code fence containing ROI summary (4-6 bullets)
- NO full model details, NO frontmatter

**Content:**
- Key ROI metrics (payback, ROI multiple, net value)
- File generated notification
- Top 1-2 assumptions or caveats

**Example:**
```markdown
# Chat Output

```markdown
**ROI Model Generated - Northwind Manufacturing**
- **Excel file:** `roi_model__Fruit_of_the_Earth_2025-11-15.xlsx`
- **Payback:** 5.3 months | **3-Year ROI:** 5.8:1 ($1.27M net value)
- **Annual Value:** $495K | **Investment:** $220K
- **Assumptions:** Conservative 80% savings, $100K avg QA salary
- **Next:** Review with John D'Andrea (GM) and finance team
```
```

### 7. Generate Artifact Output (Full Model Summary)

**Purpose:** Create the complete model summary markdown for storage.

**Format:**
- Heading: `# Artifact Output`
- Single markdown code fence containing full model summary with frontmatter

**Content structure:**

```yaml
---
generated_by: roi-model
generated_on: 2025-11-15T10:30:00Z
deal_id: Northwind Manufacturing
sources:
  - sample-data/Runtime/Sessions/Northwind Manufacturing/deal.md
  - Framework/Plays/value_realization.md
  - .claude/skills/roi-model/assets/roi_template.xlsx
file_generated: roi_model__Fruit_of_the_Earth_2025-11-15.xlsx
---

# ROI Model: Northwind Manufacturing

## Executive Summary
- **Investment (Year 1):** $220,000
- **Annual Value:** $495,000
- **Payback Period:** 5.3 months
- **3-Year Net Value:** $1,265,000
- **3-Year ROI Multiple:** 5.8:1

## Current State Costs
- QA Labor Inefficiency: $250,000/year
- Documentation Error Cost: $81,000/year
- Deviation Administrative Burden: $70,000/year
- Audit Preparation Time: $78,000/year
- Compliance Risk Exposure: $200,000/year
- **TOTAL:** $679,000/year

## Solution Value
- QA Efficiency (80% savings): $200,000/year
- Error Elimination (90%): $72,900/year
- Deviation Reduction (80%): $56,000/year
- Audit Efficiency (50%): $39,000/year
- Vendor Consolidation: $40,000/year
- **TOTAL:** $495,000/year

## Assumptions
- Conservative savings estimates (80% vs potential 90%+)
- QA reviewer avg salary: $100K
- Implementation timeline: 4-5 months
- No ongoing maintenance costs (SaaS includes all)

## Next Steps
1. Review model with economic buyer (John D'Andrea, GM)
2. Validate assumptions with finance team
3. Present at onsite meeting next week
4. Use for procurement approval process
```

### 8. Emit Structured JSON Summary

**Purpose:** Provide machine-readable summary for API/Next.js app consumption.

**Format:**
- Code fence with label: ` ```json summary `
- This is the THIRD and FINAL section of the three-section envelope

**CRITICAL Output Order:**
1. `# Chat Output` (Step 6)
2. `# Artifact Output` (Step 7)
3. ` ```json summary` (Step 8 - this step)
4. Nothing else after the closing fence

**JSON Schema:**
```json
{
  "dealId": "Company Name",
  "fileGenerated": "roi_model__Company_2025-11-15.xlsx",
  "fileType": "xlsx",
  "summaryBullets": [
    "Payback: 5.3 months",
    "3-Year ROI: 5.8:1 ($1.27M net value)",
    "Annual Value: $495K | Investment: $220K"
  ],
  "nextActions": [
    "Review with economic buyer",
    "Validate assumptions with finance",
    "Present at onsite meeting"
  ]
}
```

**Validation:**
- ✅ Valid JSON - passes JSON.parse()
- ✅ All required fields: dealId, fileGenerated, fileType, summaryBullets, nextActions
- ✅ Nothing after closing fence

### 9. Save Output

Save Excel file and markdown companion to deal session directory:

**Excel Filename:** `sample-data/Runtime/Sessions/{DEAL}/roi_model__{DEAL}_{DATE}.xlsx`

**Markdown Filename:** `sample-data/Runtime/Sessions/{DEAL}/roi_model__{DEAL}_{DATE}.md`

Write ONLY the Artifact Output content (with frontmatter) to the markdown file.

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Missing deal.md | No deal context file found | Create deal note first with /deal-intake |
| Missing batch volume | Insufficient data in deal note | Request from customer or estimate conservatively |
| ROI < 2.0:1 | Low value or high cost | Find additional value drivers or challenge ACV |
| Formula errors after edit | Modified formula cells | Regenerate from template, only edit blue cells |
| Template not found | Missing roi_template.xlsx | Run `scripts/create_roi_template.py` to regenerate |

## Example Usage

**User request:** "Build ROI model for Northwind Manufacturing"

**Assistant workflow:**
1. Read `sample-data/Runtime/Sessions/Northwind Manufacturing/deal.md`
2. Extract: 4,800 batches/year, 5% error rate, 2 QA reviewers, 780 deviations/year, 26 audits/year, $144,781 ACV
3. Calculate current state costs: $679,000/year
4. Calculate solution value: $495,000/year (80-90% savings)
5. Load `roi_template.xlsx` using document-skills:xlsx
6. Populate blue cells with calculated values
7. Validate formulas with `recalc.py`
8. Save to `sample-data/Runtime/Sessions/Northwind Manufacturing/roi_model__Fruit_of_the_Earth_2025-11-15.xlsx`
9. Generate markdown summary with frontmatter
10. Report ROI results: 5.3 month payback, 5.8:1 ROI ✅

## Financial Model Standards

**Number Formats:**
- Currency: `$#,##0` (e.g., $250,000)
- Ratios: `0.0":1"` (e.g., 5.8:1)
- Decimals: `0.0` (e.g., 5.3 months)

**Cell Styling:**
- Blue fill (#DDEEFF) + Blue bold font: Input cells
- No fill + Black bold font: Formula cells
- No fill + Green font: Cross-sheet references
- Header fill (#4472C4) + White bold font: Column headers
- Double border: Total rows

**Formula Conventions:**
- Use explicit sheet names in cross-sheet refs: `='Current State Costs'!B3`
- Use SUM for totals: `=SUM(B3:B7)`
- Use division for ratios: `=B5/B2`
- Use multiplication for percentages: `=B3*0.80`

## References

- **ROI Methodology:** `Framework/Plays/value_realization.md` - Conservative savings assumptions, 3:1 ROI target
- **Excel Template:** `assets/roi_template.xlsx` - 5-tab workbook with formulas
- **Recalc Script:** `scripts/recalc.py` - Formula validation using LibreOffice
- **Template Generator:** `scripts/create_roi_template.py` - Regenerate template if corrupted

**Dependencies:**
- `openpyxl` (Python): Excel file manipulation
- `LibreOffice` (system): Formula recalculation via `recalc.py`
- `document-skills:xlsx` (skill): Cell editing interface
