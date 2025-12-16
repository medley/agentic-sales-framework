---
name: deal-intake
description: This skill should be used when the user says "process [deal]", "intake", "I just added [deal]", "create deal.md", or mentions processing transcripts/CRM/quotes/emails for a deal opportunity. Extracts facts from raw files into structured envelope with strict provenance (sourceFiles + sourceSnippets).
allowed-tools: [Read, Write, Glob, Bash]
---

# Deal Intake — Runtime Specification

**Version:** 1.2
**Purpose:** Initialize new deals or update existing deals through artifact ingestion, normalization, and deal state management
**Reference:** See `reference.md` for detailed examples, edge cases, and troubleshooting

---

## ⚠️ CRITICAL: Skill Invocation Validation

**Before proceeding, verify you are executing this skill correctly:**

✅ **Correct:** You are reading this from `.claude/skills/deal-intake/SKILL.md` and will follow ALL instructions below
❌ **Incorrect:** You are creating `deal.md` directly from `raw/` files without generating artifacts first

**If you are NOT reading this file, STOP immediately and invoke the skill properly:**
- Natural language: "process the [deal] deal" or "I just added [deal]"
- Explicit command: Use `/deal-intake` slash command

**Self-check:** Are you about to create deal.md WITHOUT first creating normalized artifacts in `artifacts/calls|quotes|emails|other/`?
→ If YES: You have skipped Phase 1. STOP and restart with proper skill invocation.

---

## When to Use This Skill

**Activate when:**
- User has call transcripts, CRM exports, quotes, slides, or emails for a specific deal
- User says "process {Company} deal files," "intake," "I just added {Deal}," or "create deal from files"
- Files are in `sample-data/Runtime/Sessions/{DEAL}/raw/**` or need to be organized
- Starting a NEW deal with existing files (auto-initializes folder structure + creates deal.md)
- Adding files to an EXISTING deal (generates new artifacts + updates deal.md)

**Do NOT use for:**
- Reusable knowledge (playbooks, methodologies, personas) → use `convert_and_file` skill
- Simple file reads without processing → use Read tool directly
- Portfolio-level analysis → use portfolio agent
- Creating empty deal from template with no files → manual template copy

---

## Core Principles

1. **Strictly Extractive:** Copy exact text from source files. Never invent dialogue, names, or details.
2. **Mandatory Provenance:** All facts require sourceFiles + sourceSnippets with exact quotes.
3. **Output Proportional to Input:** Short notes → short output. Don't expand minimal notes into elaborate stories.
4. **Use Fast Path for Simple Notes:** Files < 500 words with no structure skip artifact generation.
5. **Two-Phase Workflow:** Generate artifacts first (Phase 1), then create/update deal.md (Phase 2).

**See references/ for details:**
- `references/artifact-templates.md` - Extractive templates for all file types
- `references/data-precedence.md` - Rules for conflicting data (CRM > Quote > Transcript)
- `references/edge-cases.md` - Handling ambiguous inputs, troubleshooting
- `references/envelope-schema.md` - Complete JSON contract specification

---

## Input Contract

### Required
- **file_path** (string): Path to file(s) to process
  - Can be absolute: `/path/to/sample-data/Runtime/Sessions/AcmeCorp/raw/calls/transcript.txt`
  - Can be relative to deal: `raw/calls/transcript.txt` (if deal_name provided)
  - Can be glob pattern: `raw/calls/*.txt`

### Optional
- **deal_name** (string): Deal name (e.g., "AcmeCorp", "TechCoInc")
  - If omitted, infer from file_path (extract from `sample-data/Runtime/Sessions/{DEAL}/`)
  - If unclear, ERROR and ask user
- **directory_path** (string): Process all files in a directory
  - Example: `raw/` or `raw/Calls/`
  - Will recursively find all files and process them
  - Prioritizes CRM exports, then quotes, then transcripts, then emails

---

## Processing Algorithm

### Step 1: Determine Deal & Files

1. **Parse file_path:**
   - If contains `sample-data/Runtime/Sessions/{DEAL}/` → Extract deal name
   - If relative path and deal_name provided → Construct absolute path
   - If glob pattern → Expand with Glob tool

2. **Check if deal exists:**
   - Look for `sample-data/Runtime/Sessions/{DEAL}/deal.md`
   - If EXISTS → **Mode: UPDATE** (continue to Step 1.3)
   - If NOT FOUND → **Mode: INITIALIZE** (skip to Step 0.5)

3. **Verify file(s) exist:**
   - Use Glob or direct path check
   - If not found → ERROR: "File not found: {file_path}. Check path."

4. **Check idempotency (UPDATE mode only):**
   - Read deal.md Generated Artifacts section
   - Extract filename from file_path
   - If filename already present:
     - Log warning: "⚠️ File {filename} was already processed on {date}. Reprocessing and updating deal.md..."
     - Proceed (overwrite previous artifact and update deal.md)
     - Note: Automatic reprocessing ensures SaaS UX remains non-interactive

---

### Step 0.5: Deal Initialization (INITIALIZE Mode Only)

**Trigger:** When deal.md does NOT exist (detected in Step 1.2)

**Goal:** Prepare for processing new deal files

**Note:** File organization is handled by the SaaS app. The framework processes files in their current locations under `sample-data/Runtime/Sessions/{DEAL}/raw/**`.

1. **Skip idempotency check** (all files are new in INITIALIZE mode)
2. **Continue to Step 1.5** (processing strategy)

---

### Step 1.5: Processing Strategy

**File count determines strategy:**
- 1-2 files → Process serially (continue to Step 2)
- 3+ files → Use parallel agents (one per file, max 5)

**For parallel processing:**
- Launch Task agents in parallel (one per file)
- Each agent processes independently and returns markdown
- Parent aggregates results, writes all files, updates deal.md once

**See reference.md § Performance Optimization for detailed orchestration patterns**

---

### Step 2: Detect Artifact Type

**Use two-stage detection for robustness:**

#### Stage 1: Pattern Matching (Primary - Fast)

Check folder path and filename patterns:

**Transcript indicators:**
- Path contains `/raw/calls/`
- OR filename matches `(transcript|call|recording|zoom|teams|meeting)`
- → **Type:** `transcript`

**Quote indicators:**
- Path contains `/raw/quotes/`
- OR filename matches `(quote|proposal|pricing|sow|statement.*work)`
- → **Type:** `quote`

**Slide indicators:**
- Path contains `/raw/slides/`
- OR extension is `.pptx|.key`
- OR filename matches `(deck|slides|presentation)`
- → **Type:** `slides`

**Email indicators:**
- Path contains `/raw/emails/`
- OR extension is `.eml|.msg`
- OR filename matches `(email|thread|correspondence)`
- → **Type:** `email`

**CRM/Deal Context indicators:**
- Filename matches `(salesforce|sfdc|crm|hubspot|opportunity|deal.*context)`
- OR content contains multiple: `ACV`, `Close Date`, `Economic Buyer`, `Stage`, `Opportunity`
- → **Type:** `crm_export`

**Other:**
- Path contains `/raw/other/` OR no pattern match
- → **Type:** `generic`

**Confidence levels:**
- **High:** Folder path + filename both match → Skip content scan
- **Medium:** Only one indicator matches → Quick content scan (50 lines)
- **Low:** No indicators match → Full content scan (100 lines)

#### Stage 2: Content Scanning (Fallback - Robust)

If confidence is Medium or Low, read file and count indicators:

**Read first 100 lines (or first 2 pages if PDF)**

**Transcript indicators (count these):**
- Speaker labels: `Speaker 1:`, `Speaker 1:`, patterns like `Name:`
- Timestamps: `[00:15:32]`, `15:32`
- Conversation markers: `Q:`, `A:`, multiple alternating speakers
- Zoom/Teams headers or watermarks

**Quote indicators (count these):**
- Currency amounts: `$`, `USD`, `EUR`, price tables
- Terms: `payment terms`, `subscription`, `annual contract value`, `ACV`
- Legal: `This proposal expires`, `terms and conditions`, `acceptance`
- Line items: SKU codes, quantity columns, unit price tables

**Email indicators (count these):**
- Headers: `From:`, `To:`, `Subject:`, `Date:`, `Cc:`
- Greetings: `Hi [name]`, `Hello`, `Dear`
- Signatures: `Best regards`, `Thanks`, `Sincerely`, `Sent from my`
- Thread markers: `On [date], [person] wrote:`, `>` quoting

**Slide indicators (count these):**
- Slide numbers: `Slide 1 of 20`, page numbering
- Title/body separation patterns
- Heavy use of bullet points
- Presenter notes sections

**Decision:**
- If 3+ transcript indicators → `transcript`
- If 3+ quote indicators → `quote`
- If 3+ email indicators → `email`
- If 2+ slide indicators → `slides`
- If still unclear → `generic` (file it, ask user if clarification needed)

---

### Step 2.5: Fast Path Check (Short Notes)

**Trigger:** File < 500 words AND no clear structure

**Check indicators:**
- Word count < 500
- No speaker labels (no "Speaker 1:", no "Name:")
- No section headers
- No tables or structured data
- Plain prose or minimal bullet points

**If triggered:**
1. **Skip artifact generation** (don't create files in artifacts/)
2. **Extract facts directly** into JSON envelope (Step 4.5)
3. **Generate minimal deal.md** from envelope only

**If NOT triggered:**
- Continue to Step 3 (Process by Type)

**See:** `references/edge-cases.md` Edge Case 1 for detailed behavior.

---

### Step 3: Generate Artifacts (If NOT Fast Path)

**Goal:** Create verbatim reference material organized by category.

**Rule:** Artifacts contain ONLY exact quotes from source. NO paraphrasing, NO synthesis, NO interpretation.

**Templates:** See `references/artifact-templates.md` for complete templates:
- **Transcript artifacts** - Organize quotes by category (Budget, Timeline, Pain, etc.)
- **Quote artifacts** - Extract exact commercial terms verbatim
- **Email artifacts** - Organize email content by topic
- **CRM Export artifacts** - Field-by-field extraction with exact values
- **Generic artifacts** - Minimal processing for unclear file types

**Artifact Path Format:**
- Transcripts → `artifacts/calls/{DATE}_{call_type}_summary.md`
- Quotes → `artifacts/quotes/{DATE}_quote_snapshot.md`
- Emails → `artifacts/emails/{DATE}_email_summary.md`
- CRM Exports → `artifacts/other/{DATE}_crm_context_summary.md`
- Generic → `artifacts/other/{DATE}_{original_filename}.md`

**Frontmatter (ALL artifacts):**
```yaml
---
generated_by: deal_intake
generated_on: {ISO_TIMESTAMP}
deal_id: {DEAL_NAME}
artifact_type: {call_summary|quote_snapshot|email_summary|crm_export|generic}
sources:
  - "{relative_path_to_raw_file}"
---
```

**Output:** Write artifact to appropriate path with frontmatter.

**Data Precedence:** See `references/data-precedence.md` for rules when multiple sources conflict (CRM > Quote > Transcript > Email).

**Edge Cases:** See `references/edge-cases.md` for handling ambiguous files, missing structure, binary formats, etc.

---

### Step 4: Write Artifacts & Update deal.md

**Phase 1:** Write artifact files to appropriate paths (using templates from Step 3)
- Include frontmatter with all required fields
- Write to `artifacts/{type}/{DATE}_{filename}.md`

**Phase 2:** Generate JSON envelope (see Step 4.5)

**Phase 3:** Create or update deal.md
- **INITIALIZE mode (new deal):** Create deal.md from envelope data
  - Use SaaS app conventions for structure
  - Populate all sections from envelope facts
  - Add entry to Generated Artifacts section
  - Add entry to History section
- **UPDATE mode (existing deal):** Append new data to existing deal.md
  - Add entries to Generated Artifacts section (artifact paths + timestamps)
  - Add entries to History section (date + brief description)
  - Update relevant sections if new information present (Stakeholders, MEDDPICC, Risks, Tasks)
  - Apply data precedence rules (see `references/data-precedence.md`)

**Note:** deal.md structure and formatting follow SaaS app conventions. The skill provides structured data (envelope); detailed formatting is handled by SaaS apply logic.

---

### Step 4.5: JSON Output (Single Section Only)

**CRITICAL:** After completing Phase 2 (deal.md creation/update), you MUST output ONLY a single JSON object.

⚠️ **OUTPUT REQUIREMENTS:**

1. **Output ONLY JSON** - No prose, no explanations, no markdown headings, no multiple sections
2. **Do NOT include "Chat Output" or "Artifact Output"** - These are not needed
3. **The ENTIRE response must be a single JSON object** - Nothing else
4. **Optional: Wrap in code fences** - You may use ```json ... ``` fences (will be stripped during parsing)

**CRITICAL - Extractive Envelope:**

⚠️ **STRICT EXTRACTION REQUIREMENTS:**

Before generating this JSON, you MUST:
1. Re-read all generated artifacts AND the original raw files
2. Extract stakeholders, pain points, metrics, events ONLY from source text
3. NEVER invent names, titles, companies, dialogue, or any other details
4. **EVERY fact MUST include sourceSnippets with EXACT text from source files**
5. sourceSnippets must be verbatim quotes - no paraphrasing, no summarization
6. If you cannot find an exact quote for a fact → DO NOT include that fact in the envelope
7. **Verify each sourceSnippet actually appears in the source file before including it**
8. If source says "$69 million" → snippet says "$69 million", NOT "$500,000" or any other number
9. If source mentions "elf on the shelf" → use "elf on the shelf", NOT "Elf" or "Production Manager"
10. If source lists competitors → include exact company names, NOT "UNKNOWN"

**Schema Version:**
All new envelopes MUST include `"schema_version": "v2"` at the top level.

**Intake-specific schema:**

```json
{
  "schema_version": "v2",
  "dealId": "Company Name",
  "mode": "INITIALIZE|UPDATE",
  "filesProcessed": [
    {
      "rawFilePath": "sample-data/Runtime/Sessions/AcmeCorp/raw/calls/discovery_call.md",
      "artifactPaths": [
        "sample-data/Runtime/Sessions/AcmeCorp/artifacts/calls/2025-01-10_discovery.md"
      ],
      "type": "call"
    }
  ],
  "artifactsCreated": [
    "artifacts/calls/2025-11-15_discovery_summary.md",
    "artifacts/quotes/2025-11-16_quote_snapshot.md",
    "artifacts/emails/2025-11-14_email_summary.md"
  ],
  "artifactTypeCounts": {
    "call_summaries": 2,
    "quote_snapshots": 1,
    "email_summaries": 2,
    "slide_decks": 0,
    "crm_exports": 0,
    "other": 0
  },
  "stakeholders": [
    {
      "name": "Jane Smith",
      "roleTitle": "VP Finance",
      "org": "AcmeCorp",
      "relationship": "economic_buyer",
      "sourceFiles": ["sample-data/Runtime/Sessions/AcmeCorp/raw/calls/transcript.txt"],
      "sourceSnippets": ["Jane Smith (VP Finance) mentioned: 'We have $150K budgeted for this initiative'"]
    }
  ],
  "painPoints": [
    {
      "description": "Manual batch record reviews delay every release by 3-4 days",
      "category": "efficiency",
      "sourceFiles": [
        "sample-data/Runtime/Sessions/AcmeCorp/raw/calls/discovery_call.md"
      ],
      "sourceSnippets": [
        "\"Our batch record reviews still take 3-4 days because everything is manual\""
      ]
    }
  ],
  "metrics": [
    {
      "label": "Batch record review time",
      "value": 4,
      "unit": "days",
      "rawText": "\"review cycles are still 3-4 days\"",
      "sourceFiles": [
        "sample-data/Runtime/Sessions/AcmeCorp/raw/calls/discovery_call.md"
      ],
      "sourceSnippets": [
        "\"We spend 3 to 4 days on each review\""
      ]
    }
  ],
  "events": [
    {
      "description": "Discovery call with finance team to discuss pain points",
      "dateText": "November 15, 2025",
      "normalizedDate": "2025-11-15",
      "sourceFiles": ["sample-data/Runtime/Sessions/AcmeCorp/raw/calls/transcript.txt"],
      "sourceSnippets": ["Call started on November 15, 2025 at 2:00 PM"]
    }
  ],
  "suggestedUpdates": {
    "stage": {
      "value": "3-Validation",
      "confidence": "medium",
      "rationale": "Team confirmed technical validation underway after the demo",
      "sourceFiles": ["sample-data/Runtime/Sessions/AcmeCorp/raw/emails/demo_recap.md"],
      "sourceSnippets": [
        "\"Following the technical validation meeting, we're aligned on next procurement steps\""
      ]
    },
    "acv": {
      "value": 144000,
      "confidence": "high",
      "rationale": "Quote explicitly lists $144,000 total in the pricing table",
      "sourceFiles": ["sample-data/Runtime/Sessions/AcmeCorp/raw/quotes/quote_2025-11-16.pdf"],
      "sourceSnippets": [
        "\"Total (USD): $144,000\""
      ]
    },
    "closeDate": {
      "value": "2025-12-31",
      "confidence": "medium",
      "rationale": "Quote expiration date is December 31, 2025",
      "sourceFiles": ["sample-data/Runtime/Sessions/AcmeCorp/raw/quotes/quote_2025-11-16.pdf"],
      "sourceSnippets": [
        "\"Valid through 31 December 2025\""
      ]
    }
  },
  "dealMdStatus": "created|updated",
  "dealSnapshot": {
    "stage": "2-Discovery",
    "health": "GREEN",
    "acv": "$144,000",
    "closeDate": "2025-12-31",
    "stakeholderCount": 4
  },
  "summaryBullets": [
    "Processed 5 artifacts for AcmeCorp",
    "Updated deal.md with discovery call insights",
    "Identified economic buyer: Jane Smith (VP Finance)",
    "Added $144K quote to commercial terms",
    "Flagged 2 D1 tasks requiring immediate action"
  ],
  "nextActions": [
    "Run /coach to analyze deal health",
    "Review deal.md for accuracy",
    "Address D1 tasks within 24 hours"
  ]
}
```

**Required Fields:** See `references/envelope-schema.md` for complete specification.

**Critical Extraction Rules:**
1. Set `"schema_version": "v2"` (mandatory)
2. ALL facts require sourceFiles + sourceSnippets
3. sourceSnippets = EXACT verbatim quotes (no paraphrasing)
4. Names EXACTLY as written ("elf on the shelf" not "Elf")
5. Numbers EXACTLY as written (if source says "$69 million", snippet = "$69 million")
6. NEVER invent names, numbers, dialogue, or details
7. Empty arrays better than invented data

**Validation Checklist Before Finalizing:**
- Every stakeholder has sourceSnippets with exact quote
- Every number matches source exactly (no rounding)
- Every name matches source exactly (no normalization)
- No world knowledge applied
- Fast path used for files < 500 words
- All relationship values are valid enums (champion|economic_buyer|technical|blocker|unknown)
- All category values are valid enums (compliance|efficiency|cost|quality|other)

**See:** `references/envelope-schema.md` for field definitions, examples, and complete validation rules.

**Basic Extraction Rules:**
- If NO stakeholders found in source files → `"stakeholders": []`
- If NO events found in source files → `"events": []`
- If NO pains or metrics are grounded → `"painPoints": []`, `"metrics": []`
- NEVER populate these arrays with speculative or invented data
- Each fact MUST have at least one sourceSnippet showing exact text from source

---

## Performance Optimization

**For multi-file operations (3+ files), this skill uses parallel agent execution for maximum performance.**

**Quick guide:**
- 1-2 files → Process serially (no overhead)
- 3-5 files → Launch N parallel agents (one per file)
- 6+ files → Launch 5 agents max (batch files strategically)

**Benefits:** 5× speedup, token isolation, consistent quality

**See reference.md § Performance Optimization for:**
- Detailed decision matrices
- File batching strategies
- Performance benchmarks
- Token budget analysis
- Implementation examples

---

## Error Handling

**File not found:**
```
Error: File not found: {file_path}
Check path and try again.
```

**Deal name unclear:**
```
Error: Cannot determine deal name from path.
Specify deal_name parameter or put file in sample-data/Runtime/Sessions/{DEAL}/raw/.
```

**Already processed:**
```
File {filename} already processed on {date} ({existing_artifact}).
Re-run and overwrite? (Y/n)
```

**Type detection failed:**
```
⚠️ Could not auto-detect file type for {filename}.
Filed in artifacts/other/. Is this a transcript, quote, slide, or email?
```

---

## Quick Reference

### Artifact Output Paths

| Type       | Path                                    |
|------------|-----------------------------------------|
| Transcript | `artifacts/calls/{DATE}_{type}_summary.md` |
| Quote      | `artifacts/quotes/{DATE}_quote_snapshot.md` |
| Slides     | `artifacts/slides/{DATE}_deck_summary.md` |
| Email      | `artifacts/emails/{DATE}_email_summary.md` |
| Generic    | `artifacts/other/{DATE}_{filename}.md` |

### deal.md Sections Always Updated

- `## History` - Chronological event log
- `## Generated Artifacts` - File inventory with dates and descriptions

### deal.md Sections Conditionally Updated

- `## D1 Tasks` - If urgent action items found
- `## D7 Tasks` - If near-term action items found
- `## Metrics / MEDDPICC` - If Pain/Budget/Decision info found
- `## Risks` - If red flags or blockers found

---

## Additional Resources

**For detailed examples and troubleshooting:**
- See `reference.md` (full walkthroughs, edge cases, tips)

**Related Skills:**
- `convert_and_file` - For reusable knowledge (playbooks, methodologies)
- `coach_agent` - For deal analysis and coaching recommendations

---

**Version History:**
- **1.1** (2025-11-14): Added auto-initialization mode - skill now handles both new and existing deals. Creates folder structure + artifacts + deal.md for new deals; updates artifacts + deal.md for existing deals. Added two-phase workflow enforcement (artifacts first, then deal.md).
- **1.0** (2025-11-13): Initial skill created as part of two-lane intake model
