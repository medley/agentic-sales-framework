# Edge Cases & Troubleshooting

This document covers ambiguous inputs, tricky scenarios, and how to handle them correctly.

---

## Edge Case 1: Short Notes (< 500 words, No Structure)

### Problem
Simple meeting notes or brief updates are being misclassified as transcripts, leading to hallucinated dialogue and fabricated structure.

### Example Input
```
Welf ludwig had a meeting with santa clause. santa is interested in buying parts to make toys. other decision makers include elf on the shelf and rudolph the raindeer. they would like to purchase by december 10th 2025. they have a budget of $69 million. They are also looking at Toys R Us and Target as alternatives solution providers.
```

### Solution: Use Fast Path

**Trigger:** File < 500 words AND no speaker labels AND no structure

**Behavior:**
1. **Skip artifact generation entirely** (don't create files in artifacts/)
2. **Extract facts directly into JSON envelope**
3. **Generate minimal deal.md** from envelope only

**Expected Envelope:**
```json
{
  "schema_version": "v2",
  "dealId": "santa-clause",
  "filesProcessed": [{
    "rawFilePath": "raw/santa-test.md",
    "artifactPaths": [],
    "type": "notes"
  }],
  "stakeholders": [
    {
      "name": "santa clause",
      "sourceFiles": ["raw/santa-test.md"],
      "sourceSnippets": ["welf ludwig had a meeting with santa clause"]
    },
    {
      "name": "elf on the shelf",
      "relationship": "technical",
      "sourceFiles": ["raw/santa-test.md"],
      "sourceSnippets": ["other decision makers include elf on the shelf"]
    },
    {
      "name": "rudolph the raindeer",
      "sourceFiles": ["raw/santa-test.md"],
      "sourceSnippets": ["other decision makers include ... rudolph the raindeer"]
    }
  ],
  "suggestedUpdates": {
    "acv": {
      "value": 69000000,
      "sourceFiles": ["raw/santa-test.md"],
      "sourceSnippets": ["they have a budget of $69 million"]
    },
    "closeDate": {
      "value": "2025-12-10",
      "sourceFiles": ["raw/santa-test.md"],
      "sourceSnippets": ["they would like to purchase by december 10th 2025"]
    },
    "meddpicc": {
      "competition": {
        "value": "Toys R Us, Target",
        "sourceFiles": ["raw/santa-test.md"],
        "sourceSnippets": ["looking at Toys R Us and Target as alternatives solution providers"]
      }
    }
  }
}
```

**Expected deal.md:**
Minimal structure (frontmatter + History + Stakeholders + facts from envelope), ~100-200 lines total.

**DO NOT:**
- ❌ Create call summary artifacts
- ❌ Invent speaker labels ("Santa:", "Elf:")
- ❌ Generate dialogue not in source
- ❌ Expand to 500+ line deal.md with invented narrative

---

## Edge Case 2: Files with No Structure (Plain Prose)

### Problem
PDFs or documents with continuous prose (no sections, no bullets, no clear organization) are difficult to organize.

### Example Input
Long-form email or document that's all paragraphs, no clear breaks.

### Solution: Minimal Artifact or Fast Path

**If < 500 words:** Use fast path (skip artifacts)

**If > 500 words:**
1. Create generic artifact in `artifacts/other/`
2. Copy relevant excerpts verbatim with "[...]" for skipped portions
3. Extract facts into envelope with sourceSnippets pointing to specific paragraphs

**Artifact Format:**
```markdown
## Extracted Content

### Paragraph 1
"Verbatim text from first relevant paragraph..."

[...skipped paragraphs with no actionable content...]

### Paragraph 5
"Verbatim text from paragraph mentioning budget: 'We have approximately $150K allocated for this initiative.'"
```

**Envelope:** Extract facts with paragraph-level sourceSnippets.

---

## Edge Case 3: Multiple Files with Conflicting Data

### Problem
Quote says $100K ACV, transcript says $120K, CRM says $144K.

### Solution: Apply Data Precedence + Note Discrepancy

**Reference:** `data-precedence.md`

**Steps:**
1. Apply hierarchy: CRM > Quote > Transcript
2. Use CRM value ($144K) in suggestedUpdates
3. Include ALL sources in sourceSnippets for transparency
4. Note discrepancy in envelope summaryBullets or deal.md Risks section

**Envelope:**
```json
{
  "suggestedUpdates": {
    "acv": {
      "value": 144000,
      "confidence": "high",
      "rationale": "CRM authoritative ($144K), conflicts with Quote ($100K) and Transcript ($120K)",
      "sourceFiles": [
        "raw/other/crm_export.csv",
        "raw/quotes/quote.pdf",
        "raw/calls/transcript.md"
      ],
      "sourceSnippets": [
        "CRM ACV: $144,000",
        "Quote Total: $100,000",
        "Transcript: 'budget around $120K'"
      ]
    }
  }
}
```

**deal.md Risks section:**
```markdown
## Risks
- **Pricing Discrepancy:** CRM shows $144K ACV, but quote is $100K and transcript mentioned $120K - verify with AE which is correct
```

---

## Edge Case 4: Files with Ambiguous Type

### Problem
File `meeting_notes_2025-01-15.md` could be transcript, email thread, or just notes.

### Solution: Two-Stage Detection

**Stage 1: Pattern Matching**
- Check folder path (`raw/calls/` suggests transcript)
- Check filename patterns (`meeting_notes` is ambiguous)
- Check extension (`.md` is neutral)

**Stage 2: Content Scanning**
Read first 100 lines and count indicators:

| Indicator Type | Count | Classification |
|----------------|-------|----------------|
| Speaker labels (Name:, Speaker 1:) | 5+ | Transcript |
| Email headers (From:, To:, Subject:) | 3+ | Email |
| Currency/pricing ($, USD, terms) | 5+ | Quote |
| CRM fields (ACV:, Stage:, Close Date:) | 3+ | CRM Export |
| None of above | 0-2 | Generic |

**If still unclear after scanning:**
- Classify as "generic"
- Create minimal artifact
- Ask user in output: "File type unclear - classified as generic. Is this a transcript, quote, or something else?"

---

## Edge Case 5: Binary Files (PDFs, DOCX)

### Problem
Can't directly read content from PDFs or Word docs.

### Solution: Use Appropriate Tools

**For PDFs:**
```bash
pdftotext input.pdf output.txt
```
Then process output.txt as text file.

**For DOCX:**
Use Read tool (supports DOCX natively in framework).

**For other binary formats:**
- Skip with note: "Binary format not supported - manual review required"
- Create placeholder artifact noting file exists but wasn't processed

---

## Edge Case 6: Large Files (> 10,000 words)

### Problem
Very long transcripts or documents exceed token limits.

### Solution: Chunk Processing

**Approach 1: Extract by Section**
If file has clear sections/chapters, process each section as separate artifact.

**Approach 2: Time-based Chunking (for transcripts)**
Split by timestamp ranges:
- 00:00 - 30:00
- 30:00 - 60:00
- etc.

**Approach 3: Sampling**
For very long files (>20K words):
- Extract first 2000 words
- Extract last 2000 words
- Note in artifact: "File excerpted due to length - full file at {path}"

**Envelope:** Combine facts from all chunks, note if file was sampled.

---

## Edge Case 7: No Facts Extractable

### Problem
File contains general discussion with no concrete facts (names, dates, numbers, decisions).

### Example Input
"We had a great conversation about the industry trends and potential collaboration opportunities. Looking forward to staying in touch."

### Solution: Minimal Envelope with Empty Arrays

**Envelope:**
```json
{
  "schema_version": "v2",
  "dealId": "acme-corp",
  "filesProcessed": [{
    "rawFilePath": "raw/general_discussion.md",
    "artifactPaths": [],
    "type": "notes"
  }],
  "stakeholders": [],
  "painPoints": [],
  "metrics": [],
  "events": [{
    "description": "General discussion about industry trends",
    "dateText": "Not specified",
    "sourceFiles": ["raw/general_discussion.md"],
    "sourceSnippets": ["We had a great conversation about the industry trends"]
  }],
  "suggestedUpdates": {}
}
```

**deal.md:** Add minimal history entry, note file was reviewed but contained no actionable facts.

**DO NOT invent facts to fill empty arrays.**

---

## Edge Case 8: Stakeholder Names Not in Source

### Problem
Transcript has speaker labels "Speaker 1:", "Speaker 2:" but no actual names mentioned.

### Example Input
```
Speaker 1: We're interested in your solution.
Speaker 2: What's the pricing?
```

### Solution: Use Generic Labels, Do NOT Invent

**Artifact:**
```markdown
## Stakeholders Present
- Speaker 1 (role unknown)
- Speaker 2 (role unknown)
```

**Envelope:**
```json
{
  "stakeholders": [
    {
      "name": "Speaker 1",
      "sourceFiles": ["raw/calls/transcript.md"],
      "sourceSnippets": ["Speaker 1: We're interested in your solution"]
    },
    {
      "name": "Speaker 2",
      "sourceFiles": ["raw/calls/transcript.md"],
      "sourceSnippets": ["Speaker 2: What's the pricing?"]
    }
  ]
}
```

**DO NOT:**
- ❌ Invent names ("John Smith", "Jane Doe")
- ❌ Infer roles ("Project Manager", "CTO")
- ❌ Use world knowledge to guess who speakers are

**If user provides actual names later, update stakeholders with correct names.**

---

## Edge Case 9: Dates in Ambiguous Format

### Problem
Source says "12/10/2025" - could be December 10 or October 12.

### Solution: Prefer US Format, Note Ambiguity

**If context suggests US date format (USD currency, US company):**
- Interpret as MM/DD/YYYY (December 10, 2025)
- Note in envelope: `"dateText": "12/10/2025"` (preserve original)
- Normalize: `"normalizedDate": "2025-12-10"`

**If unclear:**
- Keep original: `"dateText": "12/10/2025"`
- Set `"normalizedDate": null` (ambiguous)
- Note in envelope confidence: "low" due to date ambiguity

**DO NOT guess if truly ambiguous.**

---

## Edge Case 10: Numbers in Different Formats

### Problem
Source mentions "$69 million", "69M", "$69000000" - all the same number.

### Solution: Preserve Original Format in sourceSnippets

**Envelope:**
```json
{
  "suggestedUpdates": {
    "acv": {
      "value": 69000000,
      "sourceSnippets": ["$69 million"]
    }
  }
}
```

**Rules:**
- `value`: Normalized number (69000000)
- `sourceSnippets`: EXACT text from source ("$69 million")
- `rawText`: Optional field for original format ("$69 million")

**DO NOT:**
- ❌ Change snippet to match value ("$69000000")
- ❌ Normalize snippet ("$69M")
- ❌ Round value to make it cleaner (69000000 is correct, not 70000000)

---

## Edge Case 11: Empty or Near-Empty Files

### Problem
File uploaded but contains only whitespace or "TBD" placeholders.

### Solution: Skip Processing, Note in Envelope

**Envelope:**
```json
{
  "filesProcessed": [{
    "rawFilePath": "raw/empty_file.md",
    "artifactPaths": [],
    "type": "other"
  }],
  "stakeholders": [],
  "events": [],
  "painPoints": [],
  "metrics": []
}
```

**summaryBullets:**
- "Processed 1 file (empty - no content to extract)"

**DO NOT invent placeholder content.**

---

## Edge Case 12: Seasonal/Time-Sensitive Deals

### Problem
Deal has explicit seasonal deadline (e.g., "Christmas", "end of quarter").

### Example Input
"We need to have this sorted by Christmas."

### Solution: Extract Exact Text, Normalize If Possible

**sourceSnippets:**
```json
"sourceSnippets": ["We need to have this sorted by Christmas"]
```

**dateText:**
```json
"dateText": "Christmas"
```

**normalizedDate:**
If current context provides year (2025):
```json
"normalizedDate": "2025-12-25"
```

Otherwise:
```json
"normalizedDate": null
```

**Note in envelope:** "Seasonal deadline 'Christmas' - assuming 2025-12-25 based on context"

---

## Edge Case 13: Multiple Contacts with Same Name

### Problem
Transcript mentions "John" multiple times, unclear if same person.

### Example Input
```
John from Finance: We have budget.
John from IT: We need technical validation.
```

### Solution: Create Separate Stakeholders with Distinguishing Info

**Envelope:**
```json
{
  "stakeholders": [
    {
      "name": "John",
      "org": "Finance",
      "sourceSnippets": ["John from Finance: We have budget"]
    },
    {
      "name": "John",
      "org": "IT",
      "sourceSnippets": ["John from IT: We need technical validation"]
    }
  ]
}
```

**Deduplication (later step):** SaaS apply logic will handle merging if they're actually the same person.

---

## Troubleshooting Common Issues

### Issue: Hallucinated Dialogue

**Symptom:** Envelope contains sourceSnippets like "Santa: I'm the owner..." but source file has no dialogue.

**Cause:** Artifact generation invented dialogue, which then got extracted as "quotes."

**Fix:** Use fast path (skip artifacts) OR ensure artifact templates are purely extractive.

**Prevention:** Check Step 2.5 (fast path) triggers correctly for short notes.

---

### Issue: Dropped Explicit Information

**Symptom:** Source says "Toys R Us and Target" but envelope has competition = "UNKNOWN"

**Cause:** Artifact template or envelope generation logic dropped explicit facts.

**Fix:** Re-read source file in Step 4.5 before generating envelope. Don't rely solely on artifacts.

**Prevention:** Envelope MUST re-read raw files, not just artifacts.

---

### Issue: Changed Numbers

**Symptom:** Source says "$69 million" but envelope has value = 500000

**Cause:** Template example number polluted extraction, or normalization error.

**Fix:** Copy exact numbers from source. Double-check `value` matches `sourceSnippets`.

**Prevention:** Include explicit check in Step 4.5: "If source says '$69 million', value MUST be 69000000"

---

### Issue: Over-Normalized Names

**Symptom:** Source says "elf on the shelf" but envelope has "Elf" or "Production Manager"

**Cause:** Name normalization or role inference from artifacts.

**Fix:** Copy names EXACTLY as written. Do not normalize, expand, or infer titles.

**Prevention:** Explicit instruction in Step 4.5: "name: EXACTLY as written ('elf on the shelf' not 'Elf')"

---

## Summary: Handling Edge Cases

### Key Principles

1. **When in doubt, use fast path** (skip artifacts, extract directly)
2. **Preserve original text** in sourceSnippets (don't normalize, paraphrase, or clean up)
3. **Empty is better than wrong** (empty arrays better than invented facts)
4. **Note ambiguity** (use confidence levels, note in risks section)
5. **Apply data precedence** when conflicts exist

### Decision Tree

```
Is file < 500 words AND no structure?
├─ YES → Fast path (skip artifacts)
└─ NO → Continue to type detection

Can you clearly identify file type?
├─ YES → Use appropriate artifact template
└─ NO → Classify as generic

Are there extractable facts?
├─ YES → Extract with exact sourceSnippets
└─ NO → Empty arrays (don't invent)

Do multiple sources conflict?
├─ YES → Apply data precedence + note discrepancy
└─ NO → Use single source

Is anything ambiguous (dates, names, numbers)?
├─ YES → Preserve original, note in confidence/rationale
└─ NO → Extract with high confidence
```
