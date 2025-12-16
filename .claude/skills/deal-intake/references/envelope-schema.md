# Deal Intake Envelope Schema v2

## Purpose

The JSON envelope is the **PRIMARY INTELLIGENT OUTPUT** of deal intake.

**Key Points:**
- Artifacts (if generated) are verbatim reference material
- **ALL extraction logic and intelligence belongs in the envelope**
- The envelope is consumed by the SaaS app to generate deal.md and update database
- Schema version v2 emphasizes strict extraction with mandatory sourceSnippets

---

## Schema Version

All new envelopes MUST include at the top level:
```json
{
  "schema_version": "v2",
  ...
}
```

**Version History:**
- **v1** (legacy): sourceSnippets optional for stakeholders/events/metrics
- **v2** (current): sourceSnippets mandatory for all facts, strict extraction rules

---

## Complete Schema

```json
{
  "schema_version": "v2",
  "dealId": "string",
  "mode": "INITIALIZE" | "UPDATE",
  "filesProcessed": [
    {
      "rawFilePath": "string",
      "artifactPaths": ["string"],
      "type": "call" | "email" | "quote" | "crm_export" | "notes" | "slides" | "other"
    }
  ],
  "artifactsCreated": ["string"],
  "artifactTypeCounts": {
    "call_summaries": number,
    "quote_snapshots": number,
    "email_summaries": number,
    "slide_decks": number,
    "crm_exports": number,
    "other": number
  },
  "stakeholders": [
    {
      "name": "string",
      "email": "string (optional)",
      "roleTitle": "string (optional)",
      "org": "string (optional)",
      "relationship": "champion" | "economic_buyer" | "technical" | "blocker" | "unknown" (optional)",
      "sourceFiles": ["string"],
      "sourceSnippets": ["string (MANDATORY in v2)"]
    }
  ],
  "painPoints": [
    {
      "description": "string",
      "category": "compliance" | "efficiency" | "cost" | "quality" | "other" (optional)",
      "sourceFiles": ["string"],
      "sourceSnippets": ["string (MANDATORY)"]
    }
  ],
  "metrics": [
    {
      "label": "string",
      "value": number (optional),
      "unit": "string (optional)",
      "rawText": "string (optional)",
      "sourceFiles": ["string"],
      "sourceSnippets": ["string (MANDATORY in v2)"]
    }
  ],
  "events": [
    {
      "description": "string",
      "dateText": "string (optional)",
      "normalizedDate": "string | null (optional)",
      "sourceFiles": ["string"],
      "sourceSnippets": ["string (MANDATORY in v2)"]
    }
  ],
  "suggestedUpdates": {
    "stage": {
      "value": "string",
      "confidence": "low" | "medium" | "high",
      "rationale": "string (optional)",
      "sourceFiles": ["string (optional)"],
      "sourceSnippets": ["string (optional)"]
    },
    "acv": {
      "value": number,
      "confidence": "low" | "medium" | "high",
      "rationale": "string (optional)",
      "sourceFiles": ["string (optional)"],
      "sourceSnippets": ["string (optional)"]
    },
    "closeDate": {
      "value": "string (YYYY-MM-DD format)",
      "confidence": "low" | "medium" | "high",
      "rationale": "string (optional)",
      "sourceFiles": ["string (optional)"],
      "sourceSnippets": ["string (optional)"]
    },
    "meddpicc": {
      "metrics": [
        {
          "value": "string",
          "confidence": "low" | "medium" | "high",
          "rationale": "string (optional)",
          "sourceFiles": ["string (optional)"],
          "sourceSnippets": ["string (optional)"]
        }
      ],
      "economicBuyer": { SuggestedValue<string> },
      "decisionCriteria": { SuggestedValue<string> },
      "decisionProcess": { SuggestedValue<string> },
      "paperProcess": { SuggestedValue<string> },
      "pain": { SuggestedValue<string> },
      "champion": { SuggestedValue<string> },
      "competition": { SuggestedValue<string> }
    }
  },
  "dealMdStatus": "created" | "updated",
  "dealSnapshot": {
    "stage": "string",
    "health": "GREEN" | "YELLOW" | "RED",
    "acv": "string",
    "closeDate": "string",
    "stakeholderCount": number
  },
  "summaryBullets": ["string"],
  "nextActions": ["string"]
}
```

---

## Field Definitions

### Top-Level Fields

#### `schema_version` (required)
- **Type:** `"v1" | "v2"`
- **Required:** YES
- **Value:** Always `"v2"` for new envelopes
- **Purpose:** Allows SaaS app to handle schema evolution

#### `dealId` (required)
- **Type:** `string`
- **Required:** YES
- **Value:** Deal name/slug (e.g., "acme-corp", "santa-clause")
- **Source:** Inferred from file path or user input
- **Note:** Must match deal folder name in `Sessions/{dealId}/`

#### `mode` (required)
- **Type:** `"INITIALIZE" | "UPDATE"`
- **Required:** YES
- **Value:**
  - `"INITIALIZE"` - New deal, deal.md doesn't exist yet
  - `"UPDATE"` - Existing deal, merging new data into existing deal.md

#### `filesProcessed` (required)
- **Type:** Array of `FileExtractionSummary`
- **Required:** YES
- **Value:** List of all raw files examined during intake
- **Purpose:** Provenance tracking - what files contributed to this envelope

**FileExtractionSummary:**
```json
{
  "rawFilePath": "sample-data/Runtime/Sessions/acme-corp/raw/calls/discovery.md",
  "artifactPaths": [
    "sample-data/Runtime/Sessions/acme-corp/artifacts/calls/2025-01-15_discovery_summary.md"
  ],
  "type": "call"
}
```

**Fields:**
- `rawFilePath`: Exact path to raw file
- `artifactPaths`: Artifacts generated from this file (empty array if fast path)
- `type`: File classification (`"call" | "email" | "quote" | "crm_export" | "notes" | "slides" | "other"`)

#### `artifactsCreated` (required)
- **Type:** Array of strings
- **Required:** YES
- **Value:** Paths to all artifact files created (relative to deal root)
- **Example:** `["artifacts/calls/2025-01-15_discovery_summary.md"]`
- **Note:** Empty array if fast path was used

#### `artifactTypeCounts` (required)
- **Type:** Object with counts
- **Required:** YES
- **Value:** Count of each artifact type processed
- **Example:**
```json
{
  "call_summaries": 2,
  "quote_snapshots": 1,
  "email_summaries": 0,
  "slide_decks": 0,
  "crm_exports": 1,
  "other": 0
}
```

---

### Fact Arrays

#### `stakeholders` (required)
- **Type:** Array of `StakeholderFact`
- **Required:** YES (can be empty array `[]`)
- **Purpose:** Track people mentioned in source files
- **Extraction:** ONLY people explicitly named in source

**StakeholderFact:**
```json
{
  "name": "Jane Smith",
  "email": "jane@acme.com",
  "roleTitle": "VP Finance",
  "org": "AcmeCorp",
  "relationship": "economic_buyer",
  "sourceFiles": ["raw/calls/transcript.txt"],
  "sourceSnippets": ["Jane Smith (VP Finance) mentioned: 'We have $150K budgeted'"]
}
```

**Field Rules:**
- `name` (required): EXACTLY as written in source
  - ❌ DON'T normalize: "elf on the shelf" → "Elf"
  - ✅ DO copy exactly: "elf on the shelf"
- `email` (optional): Only if explicitly stated
- `roleTitle` (optional): Only if explicitly stated (don't infer from context)
- `org` (optional): Only if explicitly stated
- `relationship` (optional): MUST be one of:
  - `"champion"` - Internal advocate
  - `"economic_buyer"` - Has budget authority
  - `"technical"` - Technical evaluator
  - `"blocker"` - Opposes deal
  - `"unknown"` - Unclear role
  - ❌ DON'T invent other values like "account_owner", "project_manager"
- `sourceFiles` (required): Raw file paths where mentioned
- `sourceSnippets` (MANDATORY in v2): Exact verbatim quotes from source

**Empty array if no stakeholders found:**
```json
{
  "stakeholders": []
}
```

#### `painPoints` (required)
- **Type:** Array of `PainFact`
- **Required:** YES (can be empty array)
- **Purpose:** Track customer problems/challenges mentioned
- **Extraction:** ONLY pains explicitly stated by customer

**PainFact:**
```json
{
  "description": "Manual batch record reviews delay every release by 3-4 days",
  "category": "efficiency",
  "sourceFiles": ["raw/calls/discovery_call.md"],
  "sourceSnippets": ["Our batch record reviews still take 3-4 days because everything is manual"]
}
```

**Field Rules:**
- `description` (required): Stay close to original phrasing
  - ❌ DON'T synthesize: "Inefficient manual processes"
  - ✅ DO copy: "Manual batch record reviews take 3-4 days"
- `category` (optional): MUST be one of:
  - `"compliance"` - Regulatory/legal issues
  - `"efficiency"` - Process/speed issues
  - `"cost"` - Budget/expense issues
  - `"quality"` - Quality control issues
  - `"other"` - Anything else
  - ❌ DON'T invent categories like "business_impact", "scalability"
- `sourceFiles` (required): Raw file paths
- `sourceSnippets` (MANDATORY): Exact quotes describing the pain

#### `metrics` (required)
- **Type:** Array of `MetricFact`
- **Required:** YES (can be empty array)
- **Purpose:** Track quantitative data points mentioned
- **Extraction:** ONLY metrics with numbers explicitly stated

**MetricFact:**
```json
{
  "label": "Batch record review time",
  "value": 4,
  "unit": "days",
  "rawText": "3-4 days",
  "sourceFiles": ["raw/calls/discovery_call.md"],
  "sourceSnippets": ["We spend 3 to 4 days on each review"]
}
```

**Field Rules:**
- `label` (required): Friendly description of metric
- `value` (optional): Numeric value - ONLY if explicit number in source
- `unit` (optional): Units (days, %, USD, etc.)
- `rawText` (optional): Original text containing the figure
  - ✅ Preserve format: "$69 million" not "$69M" or "69000000"
- `sourceFiles` (required): Raw file paths
- `sourceSnippets` (MANDATORY in v2): Exact quote containing the number

#### `events` (required)
- **Type:** Array of `EventFact`
- **Required:** YES (can be empty array)
- **Purpose:** Track activities, calls, meetings, milestones
- **Extraction:** ONLY events explicitly mentioned

**EventFact:**
```json
{
  "description": "Discovery call with finance team to discuss pain points",
  "dateText": "November 15, 2025",
  "normalizedDate": "2025-11-15",
  "sourceFiles": ["raw/calls/transcript.txt"],
  "sourceSnippets": ["Call started on November 15, 2025 at 2:00 PM"]
}
```

**Field Rules:**
- `description` (required): 1-2 sentences from source (no elaboration)
- `dateText` (optional): ONLY if date explicit in source
  - ❌ DON'T invent: "Today" → "2025-01-15"
  - ✅ DO preserve original: "November 15, 2025"
- `normalizedDate` (optional): ISO date (YYYY-MM-DD) or null if ambiguous
- `sourceFiles` (required): Raw file paths
- `sourceSnippets` (MANDATORY in v2): Exact text spans

---

### Suggested Updates

#### `suggestedUpdates` (optional)
- **Type:** Object with suggested values for deal.md frontmatter
- **Required:** NO (can be omitted or empty `{}`)
- **Purpose:** Hints for SaaS app to update deal.md canonical fields
- **Note:** SaaS may accept/reject based on apply options

**Structure:**
```json
{
  "suggestedUpdates": {
    "stage": { SuggestedValue<string> },
    "acv": { SuggestedValue<number> },
    "closeDate": { SuggestedValue<string> },
    "meddpicc": { Partial<MeddpiccSuggestedUpdate> }
  }
}
```

**SuggestedValue Schema:**
```typescript
{
  "value": T,  // The suggested value
  "confidence": "low" | "medium" | "high",
  "rationale": "string (optional)",
  "sourceFiles": ["string (optional)"],
  "sourceSnippets": ["string (optional)"]
}
```

**Example - ACV Suggestion:**
```json
{
  "acv": {
    "value": 144000,
    "confidence": "high",
    "rationale": "Quote explicitly lists $144,000 total in pricing table",
    "sourceFiles": ["raw/quotes/quote_2025-11-16.pdf"],
    "sourceSnippets": ["Total (USD): $144,000"]
  }
}
```

**🚨 CRITICAL - Suggested Values MUST Match Source:**
- If source says "$69 million" → `acv.value = 69000000`, `sourceSnippets = ["$69 million"]`
- If source says "december 10th 2025" → `closeDate.value = "2025-12-10"`, `sourceSnippets = ["december 10th 2025"]`
- If source lists "Toys R Us and Target" → include in `competition.value`

**Confidence Levels:**
- `"high"` - Explicit in source, no ambiguity (e.g., CRM field, quote line item)
- `"medium"` - Inferred from context but reasonably clear (e.g., quote expiration → close date)
- `"low"` - Weak signal or ambiguous (e.g., "around $100K" → ACV)

**MEDDPICC Suggested Updates:**
```json
{
  "meddpicc": {
    "metrics": [
      {
        "value": "Reduce review time from 4 days to < 1 day",
        "confidence": "high",
        "sourceSnippets": ["Current 4-day reviews need to drop to under 1 day"]
      }
    ],
    "economicBuyer": {
      "value": "Jane Smith (VP Finance)",
      "confidence": "high",
      "sourceSnippets": ["Jane has budget authority per transcript"]
    },
    "decisionCriteria": {
      "value": "ROI > 200%, compliance certified, < 6 month implementation",
      "confidence": "medium"
    },
    "competition": {
      "value": "Toys R Us, Target",
      "confidence": "high",
      "sourceSnippets": ["looking at Toys R Us and Target as alternatives"]
    }
  }
}
```

---

### Summary Fields

#### `dealMdStatus` (required)
- **Type:** `"created" | "updated"`
- **Required:** YES
- **Value:**
  - `"created"` - deal.md was created (INITIALIZE mode)
  - `"updated"` - deal.md was updated (UPDATE mode)

#### `dealSnapshot` (required)
- **Type:** Object with key deal metrics
- **Required:** YES
- **Purpose:** Quick summary for logging/monitoring

**Example:**
```json
{
  "dealSnapshot": {
    "stage": "2-Discovery",
    "health": "GREEN",
    "acv": "$144,000",
    "closeDate": "2025-12-31",
    "stakeholderCount": 4
  }
}
```

#### `summaryBullets` (required)
- **Type:** Array of strings
- **Required:** YES
- **Value:** 3-5 specific accomplishments from this intake run
- **Purpose:** User-facing summary of what was done

**Example:**
```json
{
  "summaryBullets": [
    "Processed 5 artifacts for AcmeCorp",
    "Updated deal.md with discovery call insights",
    "Identified economic buyer: Jane Smith (VP Finance)",
    "Added $144K quote to commercial terms",
    "Flagged 2 D1 tasks requiring immediate action"
  ]
}
```

#### `nextActions` (required)
- **Type:** Array of strings
- **Required:** YES
- **Value:** Recommended next steps for user
- **Note:** Always include "/coach" as one action

**Example:**
```json
{
  "nextActions": [
    "Run /coach to analyze deal health",
    "Review deal.md for accuracy",
    "Address D1 tasks within 24 hours"
  ]
}
```

---

## Extraction Rules (CRITICAL)

### Empty Arrays Are Valid

If no facts of a type are found in source:
```json
{
  "stakeholders": [],
  "painPoints": [],
  "metrics": [],
  "events": []
}
```

**NEVER populate arrays with invented/speculative data just to fill them.**

### sourceSnippets Are MANDATORY (v2)

Every fact MUST have at least one `sourceSnippet` showing exact text from source.

**If you cannot find an exact quote → DO NOT include that fact.**

### Verify Snippets Before Including

Before adding a sourceSnippet:
1. Re-read the source file
2. Confirm the exact text appears
3. Copy character-for-character (no paraphrasing)

### Numbers Must Match Source

```json
// Source says: "$69 million"
{
  "acv": {
    "value": 69000000,  // Normalized number
    "sourceSnippets": ["$69 million"]  // EXACT text from source
  }
}

// ❌ WRONG
{
  "acv": {
    "value": 69000000,
    "sourceSnippets": ["$69M"]  // Changed format - WRONG
  }
}

// ❌ WRONG
{
  "acv": {
    "value": 500000,  // Different number - HALLUCINATION
    "sourceSnippets": ["around $500K"]  // Fabricated quote
  }
}
```

### Names Must Match Source

```json
// Source says: "elf on the shelf"
{
  "stakeholders": [
    {
      "name": "elf on the shelf",  // EXACT match
      "sourceSnippets": ["other decision makers include elf on the shelf"]
    }
  ]
}

// ❌ WRONG - Normalized
{
  "name": "Elf",
  "roleTitle": "Production Manager"  // Invented title
}
```

---

## Complete Example Envelope

```json
{
  "schema_version": "v2",
  "dealId": "santa-clause",
  "mode": "INITIALIZE",
  "filesProcessed": [
    {
      "rawFilePath": "sample-data/Runtime/Sessions/santa-clause/raw/santa-test.md",
      "artifactPaths": [],
      "type": "notes"
    }
  ],
  "artifactsCreated": [],
  "artifactTypeCounts": {
    "call_summaries": 0,
    "quote_snapshots": 0,
    "email_summaries": 0,
    "slide_decks": 0,
    "crm_exports": 0,
    "other": 0
  },
  "stakeholders": [
    {
      "name": "santa clause",
      "sourceFiles": ["raw/santa-test.md"],
      "sourceSnippets": ["welf ludwig had a meeting with santa clause"]
    },
    {
      "name": "elf on the shelf",
      "relationship": "unknown",
      "sourceFiles": ["raw/santa-test.md"],
      "sourceSnippets": ["other decision makers include elf on the shelf"]
    },
    {
      "name": "rudolph the raindeer",
      "relationship": "unknown",
      "sourceFiles": ["raw/santa-test.md"],
      "sourceSnippets": ["other decision makers include ... rudolph the raindeer"]
    }
  ],
  "painPoints": [],
  "metrics": [],
  "events": [],
  "suggestedUpdates": {
    "acv": {
      "value": 69000000,
      "confidence": "high",
      "rationale": "Explicit budget mentioned in meeting notes",
      "sourceFiles": ["raw/santa-test.md"],
      "sourceSnippets": ["they have a budget of $69 million"]
    },
    "closeDate": {
      "value": "2025-12-10",
      "confidence": "high",
      "rationale": "Target purchase date explicitly stated",
      "sourceFiles": ["raw/santa-test.md"],
      "sourceSnippets": ["they would like to purchase by december 10th 2025"]
    },
    "meddpicc": {
      "competition": {
        "value": "Toys R Us, Target",
        "confidence": "high",
        "rationale": "Alternatives explicitly named",
        "sourceFiles": ["raw/santa-test.md"],
        "sourceSnippets": ["looking at Toys R Us and Target as alternatives solution providers"]
      }
    }
  },
  "dealMdStatus": "created",
  "dealSnapshot": {
    "stage": "1-Discovery",
    "health": "GREEN",
    "acv": "$69,000,000",
    "closeDate": "2025-12-10",
    "stakeholderCount": 3
  },
  "summaryBullets": [
    "Processed 1 file for santa-clause deal (fast path - no artifacts)",
    "Extracted 3 stakeholders: santa clause, elf on the shelf, rudolph the raindeer",
    "Budget identified: $69 million",
    "Target close date: December 10, 2025",
    "Competition: Toys R Us, Target"
  ],
  "nextActions": [
    "Run /coach to analyze deal health",
    "Schedule follow-up discovery call to understand pain points"
  ]
}
```

---

## Validation Checklist

Before finalizing envelope, verify:

- [ ] `schema_version` = "v2"
- [ ] Every stakeholder has `sourceSnippets` array with at least one quote
- [ ] Every painPoint has `sourceSnippets` with exact quote
- [ ] Every metric has `sourceSnippets` with exact number quote
- [ ] Every event has `sourceSnippets` with exact text
- [ ] Suggested ACV value matches sourceSnippets number
- [ ] Suggested closeDate value matches sourceSnippets date
- [ ] No names normalized ("elf on the shelf" not "Elf")
- [ ] No numbers changed ("$69 million" not "$500K")
- [ ] No competitors dropped (if source lists them, envelope includes them)
- [ ] Empty arrays for missing data (not invented facts)
- [ ] summaryBullets reflect actual extraction (not generic template text)
