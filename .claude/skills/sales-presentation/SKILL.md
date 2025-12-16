---
name: sales-presentation
description: Generate branded PowerPoint executive briefings for customer sales meetings using company brand guidelines and deal context. Creates 3-slide presentations with current state cost analysis, solution value & ROI calculations, and decision framework options. Use when preparing for executive presentations, onsite customer visits, or business case discussions.
---

# Sales Presentation Generator

Generate professional, branded PowerPoint presentations for customer sales meetings using deal context and company brand guidelines.

## Overview

This skill creates executive briefing presentations (PPTX format) for sales meetings. It reads deal context from `deal.md`, applies company branding, and generates a 3-slide presentation ready for customer delivery.

**Use this skill when:**
- Preparing for onsite customer visits
- Creating executive business case presentations
- Generating ROI discussions for CFO/economic buyer meetings
- Need branded slide deck for decision-maker presentations

**Output:** PowerPoint file (PPTX) saved to `sample-data/Runtime/Sessions/{DEAL}/artifacts/exec_presentation_{DATE}.pptx`

---

## Workflow

### Step 1: Load Brand Guidelines

1. **Read company brand file:**
   ```
   Path: sample-data/Runtime/_Shared/knowledge/brand/brand_guidelines.md
   ```

2. **Extract brand elements:**
   - **Primary Colors:**
     - Teal: [Brand Primary Color] (primary brand color)
     - Purple: [Brand Secondary Color] (primary brand color)
     - Primary Gradient: Teal to Purple

   - **Secondary Colors (use sparingly):**
     - Dark Teal: #164A62
     - Dark Purple: #7B266C
     - Red: #D01E51
     - Orange: #E65B2B
     - Yellow: #FFCC67
     - Light Green: #C9DC5E
     - Green: #79B758

   - **Neutral Colors (for text):**
     - White: #FFFFFF
     - Light Gray: #C3C5C8
     - Mid Gray: #8A8B8C
     - Dark Gray: #4E4E50
     - Black: #000000

   - **Typography:**
     - Primary: Flama Semicondensed (fallback to Arial if not available)
     - Web-safe fallback: Arial, Helvetica
     - Weights: Ultra Light (large titles) → Black (small subheads)

   - **Logo Standards:**
     - Use horizontal lockup when possible
     - 2X clear space on all sides
     - Single-tone Teal or White logo acceptable

3. **Brand application rules:**
   - **DO:** Use Primary Colors (Teal, Purple) for headers, banners, accents
   - **DO:** Use Neutral Colors (Dark Gray #4E4E50) for body text
   - **DO NOT:** Use Primary Colors for body text (reduces readability)
   - **DO:** Apply gradient (Teal→Purple) for visual impact
   - **DO:** Maintain 2X logo clear space

---

### Step 2: Load Deal Context

1. **Parse deal.md file:**
   ```
   Path: sample-data/Runtime/Sessions/{DEAL}/deal.md
   ```

2. **Extract required fields:**
   - `deal_name` - Company name
   - `industry` - Customer industry
   - `acv` - Annual contract value
   - `pain` - Current state pain points
   - `metrics` - Quantified business metrics (batches/year, error rates, FTE counts)
   - `economic_buyer` - CFO or budget approver name/title
   - `champion` - Internal advocate name/title
   - `competition` - Competing vendors

3. **Calculate ROI values** (reference `Framework/Plays/value_realization.md`)

:

   **Current State Costs:**
   - Labor cost: Extract FTE counts × $100K average salary
   - Error cost: Extract error rates × batch volumes
   - Deviation cost: Deviation counts × $50/hour admin time
   - Audit cost: Audit counts × prep hours × hourly rate
   - Risk cost: Compliance risk exposure

   **Solution Value:**
   - QA efficiency: 80% time reduction (from deal metrics)
   - Error elimination: 90% error reduction
   - Deviation reduction: 80% reduction (alternate BOM capability)
   - Audit efficiency: 50% faster prep
   - Vendor consolidation: Replace existing tool costs

   **Financial Summary:**
   - Investment: ACV Year 1 + implementation (~$50-75K)
   - Annual value: Sum of all savings categories
   - Payback: Investment ÷ Annual value (in months)
   - 3-year ROI: (3-year net value) ÷ Investment

4. **Handle missing data gracefully:**
   - If metrics missing, use conservative estimates
   - If pain points vague, use generic B2B quality system pain
   - If ACV missing, note "[Investment TBD]" in slides

---

### Step 3: Generate HTML Slides

Create HTML file for each slide following `html2pptx.md` syntax.

**CRITICAL html2pptx rules:**
- ALL text must be in `<p>`, `<h1>`-`<h6>`, `<ul>`, `<ol>` tags
- Slide dimensions: `width: 720pt; height: 405pt` (16:9 aspect ratio)
- Use web-safe fonts only: Arial, Helvetica, Times New Roman, Georgia
- Backgrounds/borders/shadows only work on `<div>` elements
- Never use CSS gradients - rasterize to PNG first
- Use `display: flex` on body to prevent margin collapse

---

#### Slide 1: Current State Cost

**Purpose:** Show the cost of their current manual/inefficient processes

**Layout:**
- Full-width header bar (Teal [Brand Primary Color], white text)
- Two-column content (40% text / 60% cost breakdown table)
- Footer with [YourCompany] branding

**HTML structure:**
```html
<!DOCTYPE html>
<html>
<head>
<style>
body {
  width: 720pt;
  height: 405pt;
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
  display: flex;
  flex-direction: column;
  background: #FFFFFF;
}
.header {
  background: [Brand Primary Color]; /* Teal */
  color: #FFFFFF;
  padding: 20pt;
  flex-shrink: 0;
}
.content {
  display: flex;
  flex: 1;
  padding: 20pt;
  gap: 20pt;
}
.left-column {
  flex: 0 0 40%;
}
.right-column {
  flex: 0 0 55%;
}
.footer {
  background: #F4F6F6;
  color: #8A8B8C;
  padding: 10pt 20pt;
  flex-shrink: 0;
  text-align: right;
}
</style>
</head>
<body>
<div class="header">
  <h1 style="margin: 0; font-size: 32pt; font-weight: bold;">Current State Cost</h1>
</div>
<div class="content">
  <div class="left-column">
    <p style="font-size: 14pt; color: #4E4E50; line-height: 1.5;">
      {DEAL_NAME} is currently spending <strong style="color: #D01E51;">${TOTAL_COST}/year</strong> on manual quality processes:
    </p>
    <ul style="font-size: 12pt; color: #4E4E50; line-height: 1.8;">
      <li>{PAIN_POINT_1}</li>
      <li>{PAIN_POINT_2}</li>
      <li>{PAIN_POINT_3}</li>
    </ul>
  </div>
  <div class="right-column">
    <!-- Cost breakdown table (use PptxGenJS table API) -->
    <div class="placeholder" style="width: 100%; height: 100%; background: #E8E6DC;"></div>
  </div>
</div>
<div class="footer">
  <p style="margin: 0; font-size: 10pt;">[Company Name]</p>
</div>
</body>
</html>
```

**Variables to populate:**
- `{DEAL_NAME}` - From deal.md `deal_name`
- `{TOTAL_COST}` - Sum of current state costs (formatted as currency)
- `{PAIN_POINT_1-3}` - From deal.md `pain` field

**Table data** (add via PptxGenJS after html2pptx):
```javascript
[
  ["Cost Category", "Annual Cost"],
  ["QA Labor Inefficiency", "$250,000"],
  ["Documentation Errors", "$81,000"],
  ["Deviation Burden", "$70,000"],
  ["Audit Prep Time", "$78,000"],
  ["Compliance Risk", "$200,000+"],
  ["TOTAL", "$679,000"]
]
```

---

#### Slide 2: Solution Value & ROI

**Purpose:** Show the value [YourCompany] delivers and financial return

**Layout:**
- Full-width header bar (Purple [Brand Secondary Color], white text)
- Three-column value drivers (left 60%) + financial summary box (right 35%)
- Footer with branding

**HTML structure:**
```html
<!DOCTYPE html>
<html>
<head>
<style>
body {
  width: 720pt;
  height: 405pt;
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
  display: flex;
  flex-direction: column;
  background: #FFFFFF;
}
.header {
  background: [Brand Secondary Color]; /* Purple */
  color: #FFFFFF;
  padding: 20pt;
  flex-shrink: 0;
}
.content {
  display: flex;
  flex: 1;
  padding: 20pt;
  gap: 20pt;
}
.value-drivers {
  flex: 0 0 58%;
}
.roi-box {
  flex: 0 0 37%;
  background: #F4F6F6;
  border: 3pt solid [Brand Primary Color];
  border-radius: 8pt;
  padding: 15pt;
}
.footer {
  background: #F4F6F6;
  color: #8A8B8C;
  padding: 10pt 20pt;
  flex-shrink: 0;
  text-align: right;
}
</style>
</head>
<body>
<div class="header">
  <h1 style="margin: 0; font-size: 32pt; font-weight: bold;">Solution Value & ROI</h1>
</div>
<div class="content">
  <div class="value-drivers">
    <h2 style="font-size: 16pt; color: [Brand Primary Color]; margin: 0 0 10pt 0;">Annual Value Creation: ${ANNUAL_VALUE}</h2>
    <ul style="font-size: 11pt; color: #4E4E50; line-height: 1.8;">
      <li><strong>80% faster QA review</strong> – Redeploy 1.5 FTE = ${QA_SAVINGS}</li>
      <li><strong>Eliminate 90% of documentation errors</strong> = ${ERROR_SAVINGS}</li>
      <li><strong>Prevent shipment holds</strong> (legibility solved) = ${HOLD_SAVINGS}</li>
      <li><strong>Reduce 80% of planned deviations</strong> = ${DEVIATION_SAVINGS}</li>
      <li><strong>50% faster audit prep</strong> = ${AUDIT_SAVINGS}</li>
      <li><strong>Real-time inventory accuracy</strong> = ${INVENTORY_SAVINGS}</li>
      <li><strong>Replace existing QMS tool</strong> = ${VENDOR_SAVINGS}</li>
    </ul>
  </div>
  <div class="roi-box">
    <h3 style="font-size: 14pt; color: [Brand Secondary Color]; margin: 0 0 10pt 0; text-align: center;">Financial Summary</h3>
    <p style="font-size: 12pt; color: #4E4E50; margin: 5pt 0;">
      <strong>Investment (Year 1):</strong> ${INVESTMENT}
    </p>
    <p style="font-size: 12pt; color: #4E4E50; margin: 5pt 0;">
      <strong>Annual Value:</strong> ${ANNUAL_VALUE}
    </p>
    <p style="font-size: 12pt; color: #4E4E50; margin: 5pt 0;">
      <strong>Payback Period:</strong> {PAYBACK_MONTHS} months
    </p>
    <p style="font-size: 18pt; color: #79B758; margin: 15pt 0 0 0; text-align: center; font-weight: bold;">
      3-Year ROI: {ROI_MULTIPLE}:1
    </p>
  </div>
</div>
<div class="footer">
  <p style="margin: 0; font-size: 10pt;">[Company Name]</p>
</div>
</body>
</html>
```

**Variables to populate:**
- `{ANNUAL_VALUE}` - Sum of all savings (formatted currency)
- `{QA_SAVINGS}` through `{VENDOR_SAVINGS}` - Individual savings categories
- `{INVESTMENT}` - ACV + implementation cost
- `{PAYBACK_MONTHS}` - Investment ÷ (Annual Value / 12)
- `{ROI_MULTIPLE}` - 3-year net value ÷ Investment (e.g., "3.2")

---

#### Slide 3: Decision Framework

**Purpose:** Present clear options for next steps (go/pilot/defer)

**Layout:**
- Full-width header bar (Teal-to-Purple gradient background)
- Three option boxes side-by-side
- Footer with branding

**HTML structure:**
```html
<!DOCTYPE html>
<html>
<head>
<style>
body {
  width: 720pt;
  height: 405pt;
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
  display: flex;
  flex-direction: column;
  background: #FFFFFF;
}
.header {
  background: linear-gradient(90deg, [Brand Primary Color] 0%, [Brand Secondary Color] 100%);
  color: #FFFFFF;
  padding: 20pt;
  flex-shrink: 0;
}
.content {
  display: flex;
  flex: 1;
  padding: 20pt;
  gap: 15pt;
}
.option-box {
  flex: 1;
  border: 2pt solid #C3C5C8;
  border-radius: 8pt;
  padding: 15pt;
  background: #FAFAFA;
}
.option-box h3 {
  font-size: 16pt;
  color: [Brand Primary Color];
  margin: 0 0 10pt 0;
  text-align: center;
}
.footer {
  background: #F4F6F6;
  color: #8A8B8C;
  padding: 10pt 20pt;
  flex-shrink: 0;
  text-align: right;
}
</style>
</head>
<body>
<div class="header">
  <h1 style="margin: 0; font-size: 32pt; font-weight: bold;">Decision Framework</h1>
</div>
<div class="content">
  <div class="option-box">
    <h3>Option A: Full Implementation</h3>
    <p style="font-size: 10pt; color: #4E4E50; line-height: 1.6;">
      <strong>Timeline:</strong> Contract {CONTRACT_DATE}, Go-live {GOLIVE_DATE}
    </p>
    <p style="font-size: 10pt; color: #4E4E50; line-height: 1.6;">
      <strong>Investment:</strong> ${INVESTMENT} Year 1
    </p>
    <p style="font-size: 10pt; color: #4E4E50; line-height: 1.6;">
      <strong>Value:</strong> ${ANNUAL_VALUE}/year (full value)
    </p>
  </div>
  <div class="option-box">
    <h3>Option B: Phased Pilot</h3>
    <p style="font-size: 10pt; color: #4E4E50; line-height: 1.6;">
      <strong>Timeline:</strong> 90-day pilot, then decide
    </p>
    <p style="font-size: 10pt; color: #4E4E50; line-height: 1.6;">
      <strong>Investment:</strong> $50K pilot (credited if proceed)
    </p>
    <p style="font-size: 10pt; color: #4E4E50; line-height: 1.6;">
      <strong>Value:</strong> Validate ROI before full commitment
    </p>
  </div>
  <div class="option-box">
    <h3>Option C: Defer to Q2 {NEXT_YEAR}</h3>
    <p style="font-size: 10pt; color: #4E4E50; line-height: 1.6;">
      <strong>Cost of delay:</strong> ${MONTHLY_COST}/month in continued inefficiency
    </p>
    <p style="font-size: 10pt; color: #4E4E50; line-height: 1.6;">
      <strong>Risk:</strong> {URGENT_DEADLINE} deadline ({TIMELINE_PRESSURE})
    </p>
    <p style="font-size: 10pt; color: #4E4E50; line-height: 1.6;">
      <strong>Recommendation:</strong> Revisit when priority returns
    </p>
  </div>
</div>
<div class="footer">
  <p style="margin: 0; font-size: 10pt;">[Company Name]</p>
</div>
</body>
</html>
```

**Variables to populate:**
- `{CONTRACT_DATE}` - Target contract signature (e.g., "Dec 2025")
- `{GOLIVE_DATE}` - Target implementation completion (e.g., "May 2026")
- `{INVESTMENT}` - Year 1 total cost
- `{ANNUAL_VALUE}` - Annual savings value
- `{MONTHLY_COST}` - Annual value ÷ 12
- `{URGENT_DEADLINE}` - From deal.md (e.g., "JDE upgrade Q1 2026")
- `{TIMELINE_PRESSURE}` - Urgency description
- `{NEXT_YEAR}` - Current year + 1

**Note:** Gradient background will need to be rasterized to PNG first using Sharp, then applied as background-image.

---

### Step 4: Convert HTML to PowerPoint

Use `scripts/html2pptx.js` to convert HTML slides to PowerPoint format.

**JavaScript conversion script:**

```javascript
const fs = require('fs');
const html2pptx = require('./scripts/html2pptx.js');
const PptxGenJS = require('pptxgenjs');

async function generatePresentation(dealName, outputPath) {
  const pptx = new PptxGenJS();

  // Slide 1: Current State Cost
  const slide1Html = fs.readFileSync('slide1_current_state.html', 'utf-8');
  const slide1 = pptx.addSlide();
  const placeholders1 = await html2pptx(slide1Html, slide1);

  // Add cost breakdown table to placeholder
  if (placeholders1.length > 0) {
    const ph = placeholders1[0];
    slide1.addTable(
      [
        [{ text: "Cost Category", options: { bold: true } }, { text: "Annual Cost", options: { bold: true } }],
        ["QA Labor Inefficiency", "$250,000"],
        ["Documentation Errors", "$81,000"],
        ["Deviation Burden", "$70,000"],
        ["Audit Prep Time", "$78,000"],
        ["Compliance Risk", "$200,000+"],
        [{ text: "TOTAL", options: { bold: true } }, { text: "$679,000", options: { bold: true, color: "D01E51" } }]
      ],
      {
        x: ph.x, y: ph.y, w: ph.w, h: ph.h,
        border: { pt: 1, color: "C3C5C8" },
        fill: { color: "FFFFFF" },
        color: "4E4E50",
        fontSize: 11,
        align: "left"
      }
    );
  }

  // Slide 2: Solution Value & ROI
  const slide2Html = fs.readFileSync('slide2_solution_value.html', 'utf-8');
  const slide2 = pptx.addSlide();
  await html2pptx(slide2Html, slide2);

  // Slide 3: Decision Framework
  const slide3Html = fs.readFileSync('slide3_decision_framework.html', 'utf-8');
  const slide3 = pptx.addSlide();
  await html2pptx(slide3Html, slide3);

  // Save presentation
  await pptx.writeFile({ fileName: outputPath });
  console.log(`✅ Presentation saved to: ${outputPath}`);
}

// Run conversion
const dealName = process.argv[2] || "Customer";
const outputPath = process.argv[3] || "exec_presentation.pptx";
generatePresentation(dealName, outputPath);
```

---

### Step 5: Generate Thumbnails & Validate

Create thumbnail grid to visually inspect slides for layout issues.

**Command:**
```bash
python scripts/thumbnail.py {OUTPUT_FILE}.pptx workspace/thumbnails --cols 3
```

**Visual validation checklist:**
- ✅ Text not cut off by header bars or slide edges
- ✅ No text overlap with shapes or other text
- ✅ Sufficient contrast (text readable on backgrounds)
- ✅ Brand colors applied correctly (Teal, Purple, neutrals)
- ✅ Tables/data visible and aligned
- ✅ Footer branding present on all slides

**If issues found:**
1. Adjust HTML margins, padding, font sizes
2. Re-run html2pptx conversion
3. Re-generate thumbnails
4. Repeat until visually correct

---

### Step 6: Generate Chat Output

**Purpose:** Provide a concise presentation summary for chat/UI display.

**Format:**
- Heading: `# Chat Output`
- Single markdown code fence containing presentation summary (4-6 bullets)
- NO full presentation details, NO frontmatter

**Content:**
- File generated notification
- Slide count and topics
- Key metrics highlighted (cost savings, ROI)
- Under 100 words total

**Example:**
```markdown
# Chat Output

```markdown
**Executive Briefing Created - Northwind Manufacturing**
- **File:** `exec_presentation_Fruit_of_the_Earth_2025-11-15.pptx`
- **Slides:** 3 slides (Current State Cost, Solution Value & ROI, Decision Framework)
- **Highlights:** $679K current state cost, $495K annual value, 5.3 month payback
- **Brand:** [YourCompany] (Teal/Purple, 16:9 format)
- **Next:** Review in PowerPoint, customize for {ECONOMIC_BUYER}
```
```

---

### Step 7: Generate Artifact Output

**Purpose:** Create the complete presentation summary markdown for storage.

**Format:**
- Heading: `# Artifact Output`
- Single markdown code fence containing full presentation summary with frontmatter

**Content structure:**

```yaml
---
generated_by: sales-presentation
generated_on: 2025-11-15T10:30:00Z
deal_id: Northwind Manufacturing
sources:
  - sample-data/Runtime/Sessions/Northwind Manufacturing/deal.md
  - sample-data/Runtime/_Shared/knowledge/brand/brand_guidelines.md
  - Framework/Plays/value_realization.md
file_generated: exec_presentation_Fruit_of_the_Earth_2025-11-15.pptx
---

# Executive Briefing: Northwind Manufacturing

## Presentation Summary
- **File:** exec_presentation_Fruit_of_the_Earth_2025-11-15.pptx
- **Format:** PowerPoint (PPTX), 16:9 aspect ratio
- **Slides:** 3
- **Brand:** [YourCompany] (Teal [Brand Primary Color], Purple [Brand Secondary Color])

## Slide Outline

### Slide 1: Current State Cost
- **Purpose:** Quantify cost of current manual/inefficient processes
- **Layout:** Full-width Teal header, two-column (pain points + cost breakdown table)
- **Key Message:** $679,000/year in quality system inefficiency
- **Data Points:**
  - QA Labor Inefficiency: $250,000
  - Documentation Errors: $81,000
  - Deviation Burden: $70,000
  - Audit Prep Time: $78,000
  - Compliance Risk: $200,000+

### Slide 2: Solution Value & ROI
- **Purpose:** Show [YourCompany] value creation and financial return
- **Layout:** Purple header, value drivers (60%) + ROI summary box (35%)
- **Key Message:** $495K annual value, 5.3 month payback, 5.8:1 ROI
- **Value Drivers:**
  - 80% faster QA review → $200K savings
  - Eliminate 90% of errors → $73K savings
  - Reduce 80% of deviations → $56K savings
  - 50% faster audit prep → $39K savings
  - Replace existing QMS → $40K savings

### Slide 3: Decision Framework
- **Purpose:** Present clear next-step options (full/pilot/defer)
- **Layout:** Gradient header (Teal→Purple), three option boxes side-by-side
- **Options:**
  - **A: Full Implementation** - Contract Dec 2025, Go-live May 2026, $220K Year 1, $495K/year value
  - **B: Phased Pilot** - 90-day pilot, $50K (credited if proceed), validate ROI first
  - **C: Defer to Q2 2026** - Cost of delay: $41K/month, Risk: JDE upgrade deadline

## Talking Points

**For Economic Buyer (John D'Andrea, GM):**
- "You're spending $679K/year on quality inefficiency. We can eliminate $495K of that."
- "Payback in 5.3 months. 5.8:1 return over three years."
- "JDE upgrade deadline creates urgency—delaying costs $41K/month in continued inefficiency."

**For Champion (Amy Cantor, QA Manager):**
- "Review-by-exception will free up 1.5 QA FTEs for higher-value work."
- "Digital capture eliminates 90% of documentation errors at root cause."
- "Audit prep time cut in half—no more all-hands prep weeks."

## Next Steps
1. Open in PowerPoint for final review and customization
2. Add [YourCompany] logo from approved artwork
3. Validate metrics with champion (Amy Cantor)
4. Present at onsite meeting with John D'Andrea (GM)
5. Share with procurement for approval process
```

---

### Step 8: Emit Structured JSON Summary

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
  "dealId": "Northwind Manufacturing",
  "fileGenerated": "exec_presentation_Fruit_of_the_Earth_2025-11-15.pptx",
  "fileType": "pptx",
  "summaryBullets": [
    "Created 3-slide executive briefing with [YourCompany] branding",
    "Slide 1: $679K current state cost breakdown",
    "Slide 2: $495K annual value, 5.3 month payback, 5.8:1 ROI",
    "Slide 3: Decision framework (Full/Pilot/Defer options)"
  ],
  "nextActions": [
    "Open in PowerPoint for final review",
    "Validate metrics with champion",
    "Present to economic buyer at onsite meeting",
    "Share with procurement for approval"
  ]
}
```

**Validation:**
- ✅ Valid JSON - passes JSON.parse()
- ✅ All required fields: dealId, fileGenerated, fileType, summaryBullets, nextActions
- ✅ Nothing after closing fence

---

### Step 9: Save Output & Update deal.md

1. **Save presentation:**
   ```
   Path: sample-data/Runtime/Sessions/{DEAL}/artifacts/exec_presentation_{ISO_DATE}.pptx
   ```

2. **Save markdown companion:**
   ```
   Path: sample-data/Runtime/Sessions/{DEAL}/exec_presentation_{ISO_DATE}.md
   ```

   Write ONLY the Artifact Output content (with frontmatter) to the markdown file.

3. **Update deal.md Generated Artifacts section:**
   ```markdown
   ## Generated Artifacts
   - **{DATE}** - `artifacts/exec_presentation_{DATE}.pptx` - Executive briefing presentation (3 slides: Current State Cost, Solution Value & ROI, Decision Framework) with [YourCompany] branding
   ```

---

## Error Handling

| Error | Severity | Behavior | Fallback |
|-------|----------|----------|----------|
| deal.md missing | CRITICAL | HALT | Return error with path expected |
| Brand guidelines missing | WARNING | Proceed | Use [YourCompany] defaults (Teal [Brand Primary Color], Purple [Brand Secondary Color], Arial font) |
| Metrics missing from deal.md | WARNING | Proceed | Use conservative ROI estimates, note "[Estimated]" in slides |
| ACV missing | WARNING | Proceed | Show "[Investment TBD]" in financial summary |
| html2pptx script not found | CRITICAL | HALT | Return error: "Missing scripts/html2pptx.js" |

---

## Example Usage

**User request:**
```
"Create sales presentation for Northwind Manufacturing"
```

**Skill execution:**
1. Loads `sample-data/Runtime/Sessions/Northwind Manufacturing/deal.md`
2. Extracts: ACV $144,781, 4,800 batches/year, 5% error rate, 2 QA reviewers, JDE upgrade crisis
3. Calculates: Current cost $528K/year, Solution value $392K/year, Payback 6.7 months, ROI 3.0:1
4. Applies [YourCompany] brand (Teal, Purple, Arial, logo standards)
5. Generates 3 slides with deal-specific data
6. Emits Chat Output (concise summary)
7. Emits Artifact Output (full presentation summary with frontmatter)
8. Emits JSON Summary (machine-readable)
9. Saves PPTX to `artifacts/exec_presentation_2025-11-15.pptx` and markdown companion

---

## References

See `references/` directory for:
- `pptx-syntax.md` - Complete html2pptx HTML syntax reference
- `exec-briefing-examples.md` - Sample slide layouts and design patterns
