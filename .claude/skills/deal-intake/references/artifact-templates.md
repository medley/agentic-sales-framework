# Artifact Templates - Extractive Mode Only

## Core Principle

Artifacts are **REFERENCE MATERIAL** containing verbatim quotes from source files.

**All intelligence and extraction logic belongs in the JSON envelope, NOT in artifacts.**

Artifacts serve one purpose: Organize verbatim quotes by category so the envelope generation step (Step 4.5) can reference exact source text.

---

## When to Generate Artifacts

### Generate Artifacts IF:
- Source file > 500 words AND has structure (speaker labels, sections, tables, headers)
- Multiple distinct topics/conversations that benefit from organization
- File type clearly indicates structured content (transcript, quote, CRM export)

### Skip Artifacts (Use Fast Path) IF:
- Source file < 500 words AND plain prose (no speaker labels, no sections)
- Simple meeting notes, brief email summaries, short updates
- No clear structure to organize

**Fast path behavior:** Extract facts directly from raw file into JSON envelope, skip artifact generation entirely.

---

## Universal Artifact Rules

🚨 **CRITICAL - APPLY TO ALL ARTIFACT TYPES:**

1. **Verbatim quotes only** - Copy exact text from source, character-for-character
2. **No paraphrasing** - If quote is too long, use "[...]" to truncate, never reword
3. **No interpretation** - Don't explain what quotes mean or add context
4. **No synthesis** - Don't combine multiple ideas into summary statements
5. **Omit empty sections** - If no quotes exist for a category, delete that section entirely
6. **No invented dialogue** - If source has no speaker labels, don't add them
7. **This is reference material** - The envelope (Step 4.5) extracts intelligence from these quotes

**If you're tempted to add content not in source → DELETE IT**

---

## Transcript Artifact Template (Extractive)

### Goal
Organize verbatim quotes by category for envelope generation reference.

### When to Use
- File has speaker labels (Speaker 1:, Name:, etc.)
- Clear conversational structure with Q&A or dialogue
- Discovery calls, demo recordings, meeting transcripts

### Artifact Path
`artifacts/calls/{DATE}_{call_type}_summary.md`

### Frontmatter
```yaml
---
generated_by: deal_intake
generated_on: {ISO_TIMESTAMP}
deal_id: {DEAL_NAME}
artifact_type: call_summary
call_type: {discovery|demo|negotiation|status|exec}
sources:
  - "{relative_path_to_raw_file}"
---
```

### Body Structure

```markdown
## Call Metadata
**Date:** [Only if explicitly stated in transcript, else "Not stated"]
**Type:** [Only if explicitly stated: discovery/demo/negotiation, else "Not stated"]
**Duration:** [Only if explicitly stated, else omit this line]

---

## Verbatim Quotes by Category

### Budget / Commercial Terms
[Exact quotes mentioning money, pricing, budget, contract value]

- **Speaker Name:** "exact quote from transcript..."
- **Speaker Name:** "another exact quote..."

[If no quotes found → DELETE this entire section]

---

### Timeline / Deadlines / Dates
[Exact quotes mentioning dates, deadlines, schedules, target timelines]

- **Speaker Name:** "exact quote..."
- **Speaker Name:** "exact quote..."

[If no quotes found → DELETE this entire section]

---

### Stakeholders Mentioned
[Names explicitly mentioned in transcript]

- **Name:** [exactly as written in transcript]
  - **Title:** [only if stated in transcript]
  - **Mentioned by:** Speaker Name
  - **Quote:** "exact quote where this person was mentioned..."

[If no stakeholders mentioned → DELETE this entire section]

---

### Pain Points / Challenges
[Exact quotes describing problems, frustrations, blockers, complaints]

- **Speaker Name:** "exact quote describing pain..."
- **Speaker Name:** "exact quote..."

[If no pain points mentioned → DELETE this entire section]

---

### Commitments / Next Steps
[Exact quotes about agreed actions, promises, follow-ups]

**Our commitments:**
- **Speaker Name:** "exact quote of what we agreed to..."

**Their commitments:**
- **Speaker Name:** "exact quote of what they agreed to..."

[If no commitments → DELETE this entire section]

---

### Competition / Alternatives
[Exact quotes mentioning other vendors, alternatives, current solutions]

- **Speaker Name:** "exact quote mentioning competitors..."

[If none mentioned → DELETE this entire section]
```

**Example (Good - Extractive):**
```markdown
### Budget / Commercial Terms
- **Jane Smith:** "We have approximately $150,000 budgeted for this initiative"
- **John Doe:** "The CFO mentioned we might be able to go up to $175K if the ROI is clear"
```

**Example (Bad - Generative):**
```markdown
### Budget / Commercial Terms
The client has a budget of around $150K-$175K and is looking for clear ROI justification.

[DON'T DO THIS - this is synthesis, not extraction]
```

---

## Quote / Proposal Artifact Template (Extractive)

### Goal
Extract exact commercial terms, pricing, SKUs from quote document.

### When to Use
- Formal quotes, proposals, pricing documents
- SOWs (Statements of Work), pricing tables
- Contract drafts with commercial terms

### Artifact Path
`artifacts/quotes/{DATE}_quote_snapshot.md`

### Frontmatter
```yaml
---
generated_by: deal_intake
generated_on: {ISO_TIMESTAMP}
deal_id: {DEAL_NAME}
artifact_type: quote_snapshot
sources:
  - "{relative_path_to_raw_file}"
---
```

### Body Structure

```markdown
## Quote Metadata
**Date Sent:** [Extract from quote if present, else "Not stated"]
**Quote ID:** [Extract if present, else omit]
**Valid Through:** [Exact expiration date if stated, else "No expiration stated"]

---

## Commercial Terms (Verbatim)

### Total Contract Value
[Copy exact text from quote]

"Quote text: 'Total Contract Value: $144,000 USD'"

[If not found → omit this section]

---

### Pricing Breakdown
[Copy exact line items, SKUs, quantities, unit prices as written]

| SKU/Item | Description (exact from quote) | Quantity | Unit Price | Total |
|----------|-------------------------------|----------|------------|-------|
| [exact] | [exact text from quote] | [exact] | [exact] | [exact] |

[If no pricing table → list as bullet points with exact quotes]

---

### Payment Terms
[Exact text about payment schedule, terms]

"Quote text: 'Payment terms: Net 30 days from invoice date'"

[If not stated → omit this section]

---

### Contract Term / Duration
[Exact text about contract length, renewal terms]

"Quote text: '12-month initial term with automatic annual renewal'"

[If not stated → omit this section]

---

### Special Conditions / Notes
[Any exact text about discounts, conditions, expiration, negotiation notes]

- "Quote text: '10% discount applied for annual prepayment'"

[If none → omit this section]
```

**CRITICAL:**
- Copy numbers EXACTLY as written ("$144,000" not "$144K" or "144000")
- Include currency symbols as shown
- Preserve formatting (commas, decimals) exactly

---

## Email Artifact Template (Extractive)

### Goal
Organize verbatim email content by topic for envelope extraction.

### When to Use
- Email threads, correspondence
- Status updates via email
- Decisions/commitments sent via email

### Artifact Path
`artifacts/emails/{DATE}_email_summary.md`

### Frontmatter
```yaml
---
generated_by: deal_intake
generated_on: {ISO_TIMESTAMP}
deal_id: {DEAL_NAME}
artifact_type: email_summary
call_type: status
sources:
  - "{relative_path_to_raw_file}"
---
```

### Body Structure

```markdown
## Email Metadata
**Date:** [Extract from email header if present]
**From:** [Extract exact sender name/email]
**To:** [Extract exact recipient(s)]
**Subject:** [Extract exact subject line if present]

---

## Verbatim Email Content by Topic

### Decisions / Confirmations
[Exact quotes where decisions were stated or confirmed]

- "Email text: 'We've decided to proceed with Option B'"

[If none → omit section]

---

### Action Items / Commitments
[Exact quotes about who will do what, by when]

- "Email text: 'I'll send the updated proposal by Friday'"
- "Email text: 'Can you schedule the demo for next Tuesday?'"

[If none → omit section]

---

### Timeline / Dates Mentioned
[Exact quotes mentioning dates, deadlines]

- "Email text: 'We need to have this wrapped up by December 10th'"

[If none → omit section]

---

### Budget / Pricing Discussion
[Exact quotes about money, budget, pricing]

- "Email text: 'The $69 million budget was approved by the board'"

[If none → omit section]

---

### Blockers / Issues Raised
[Exact quotes describing problems, concerns, blockers]

- "Email text: 'We're concerned about the integration timeline'"

[If none → omit section]
```

---

## CRM Export Artifact Template (Extractive)

### Goal
Field-by-field extraction with exact values from CRM system export.

### When to Use
- Salesforce opportunity exports
- HubSpot deal exports
- Any structured CRM data export

### Artifact Path
`artifacts/other/{DATE}_crm_context_summary.md`

### Frontmatter
```yaml
---
generated_by: deal_intake
generated_on: {ISO_TIMESTAMP}
deal_id: {DEAL_NAME}
artifact_type: crm_export
sources:
  - "{relative_path_to_raw_file}"
---
```

### Body Structure

```markdown
## CRM System
**System:** [Exact text: "Salesforce" / "HubSpot" / etc., only if stated]
**Export Date:** [Extract if present]

---

## Deal Fields (Exact Values)

### Opportunity / Deal Information
[Copy field names and values EXACTLY as shown in export]

- **Field Name (exact from CRM):** [Exact value from export]
- **ACV:** [Exact value with currency: "$144,781" not "144781" or "$144K"]
- **Close Date:** [Exact date format from export: "2025-12-31" or "12/31/2025"]
- **Stage:** [Exact stage name from export: "3-Validation" not "Validation"]

[Only include fields present in export - if field missing, omit]

---

### Stakeholder / Contact Information
[Copy contact fields exactly as shown]

- **Contact Name:** [Exact name from export]
  - **Title:** [Exact title if present]
  - **Role:** [Exact role field if present: "Economic Buyer" / "Champion" / etc.]
  - **Email:** [Exact email if present]

---

### Competition / Alternatives
[Exact text from competition fields]

- **Competitors:** [Exact list: "Toys R Us, Target" not "TRU and Target"]

[If field empty or missing → omit section]

---

### Next Steps / Action Items
[Exact text from next steps fields]

- **Next Step:** [Exact text from CRM field]
- **Due Date:** [Exact date if present]

[If field empty → omit section]
```

**CRITICAL - CRM Data Rules:**
- DO NOT normalize dates (keep format from export)
- DO NOT round numbers (keep exact values)
- DO NOT map stage names (use exact CRM stage)
- DO NOT expand abbreviations (if CRM says "EB" keep as "EB")
- Copy field names exactly as labeled in export

---

## Generic / Other Artifact Template (Extractive)

### Goal
Minimal processing for files that don't fit other types.

### When to Use
- Unstructured notes
- PDFs without clear format
- Mixed content documents
- When file type detection is unclear

### Artifact Path
`artifacts/other/{DATE}_{original_filename}.md`

### Frontmatter
```yaml
---
generated_by: deal_intake
generated_on: {ISO_TIMESTAMP}
deal_id: {DEAL_NAME}
artifact_type: generic
sources:
  - "{relative_path_to_raw_file}"
---
```

### Body Structure

```markdown
## File Information
**Original Filename:** [Exact filename]
**File Type:** [Extension: .pdf / .docx / .txt / etc.]

---

## Extracted Content

[IF file has clear structure (headers, sections, bullets):]
Copy structure verbatim with exact quotes.

[IF file is plain prose:]
Copy relevant excerpts verbatim, use "[...]" for skipped portions.

[IF file contains data/facts:]
List facts as bullet points with exact quotes:
- "Exact quote from file: '...'"

[IF file is mostly unstructured / unclear:]
Note: "Unable to extract structured information. File contains general discussion of [topic]."
```

**For generic files:** Extract any clear facts (names, dates, numbers, decisions) with exact quotes. If nothing clear → create minimal artifact noting file was reviewed.

---

## Summary: Extraction vs. Synthesis

### ✅ GOOD (Extraction)
```markdown
### Budget Discussion
- John: "We have $150K allocated for this project"
- Jane: "That might need CFO approval since it's over $100K"
```

### ❌ BAD (Synthesis)
```markdown
### Budget Discussion
The client has a budget of approximately $150K but may need CFO approval for amounts over $100K due to internal policies.

[This is SYNTHESIS - don't do this in artifacts]
```

**Remember:** Artifacts are VERBATIM REFERENCE MATERIAL. The envelope (Step 4.5) is where you apply extraction logic and intelligence.
