---
license: "MIT - See LICENSE.md"
name: deal_intake_reference
description: Reference documentation for deal_intake skill with detailed examples, edge cases, and troubleshooting. This is the comprehensive guide - for day-to-day execution, use SKILL.md instead.
---

# Deal Intake — Reference Documentation

**Purpose:** Comprehensive guide with full examples, edge cases, and troubleshooting for the deal_intake skill
**Runtime Spec:** See `SKILL.md` for concise execution instructions

---

## Overview

This skill manages intake of deal-specific artifacts (call transcripts, quotes, slide decks, email threads) into the framework. It automatically detects file types, generates normalized summaries, and updates deal.md with history, tasks, and MEDDPICC fields.

**Key principles:**
- All artifacts trace back to files in `raw/`
- Every intake updates deal.md
- Type-specific processing for different artifacts
- Idempotent (won't re-process same file twice)
- Methodology-neutral extraction (agents handle interpretation)

---

## Detailed Examples

### Example 1: Ingest Discovery Call Transcript

**User Request:**
> "Ingest the new discovery call for AcmeCorp"

**File Location:**
`sample-data/Runtime/Sessions/AcmeCorp/raw/calls/2025-11-13_discovery_zoom_transcript.txt`

**Skill Execution:**

#### Step 1: Determine Deal & Files
```
Parsed path: Sessions/AcmeCorp/raw/calls/2025-11-13_discovery_zoom_transcript.txt
Deal name: AcmeCorp
Verified: deal.md exists at Sessions/AcmeCorp/deal.md
Verified: File exists
Idempotency check: "2025-11-13_discovery_zoom_transcript.txt" not in Generated Artifacts → Proceed
```

#### Step 2: Detect Type
```
Pattern matching:
- Path contains "/raw/calls/" ✅
- Filename contains "transcript" ✅
Confidence: HIGH
Type: transcript (skip content scan)
```

#### Step 3: Process as Transcript
```
Read transcript (850 lines)

Extracted:
- Objective: Discovery call to understand pain points and current process
- What we learned:
  * CFO frustrated with manual month-end close (takes 5 days)
  * VP Ops concerned about audit trail gaps
  * Currently using Excel + email for reconciliation
  * Pain level: CFO rated it "8 out of 10" unprompted
- Stakeholders:
  * Sarah Chen - CFO (champion signals: engaged, asked about timeline)
  * Mike Torres - VP Operations (neutral: listening, few questions)
  * Lisa Park - Controller (blocker risk: mentioned "happy with current process")
- Pain notes: Manual close = 5 days, audit gaps, compliance risk
- Budget notes: CFO mentioned "we budgeted for process improvements this quarter"
- Commitments:
  * Our side: Send ROI calculator by Friday, schedule demo for next week
  * Their side: CFO will review with team, provide current process doc
- Next steps:
  * Send ROI calc (by 2025-11-15) - ASSIGNED TO US
  * Schedule demo (week of 2025-11-18)
  * Get current process doc from them
```

#### Step 4: Write Artifacts & Update deal.md

**Generated artifact:**
`artifacts/calls/2025-11-13_discovery_summary.md`

```markdown
---
generated_by: deal_intake
generated_on: 2025-11-13T14:30:00Z
deal_id: AcmeCorp
artifact_type: call_summary
sources:
  - "raw/calls/2025-11-13_discovery_zoom_transcript.txt"
---

## Call Summary
**Date:** 2025-11-13
**Type:** discovery
**Duration:** 45 minutes

## Objective
Discovery call to understand current month-end close pain points and process gaps.

## What We Learned
- CFO frustrated with manual month-end close taking 5 days
- VP Ops concerned about audit trail gaps for compliance
- Currently using Excel + email for reconciliation (no centralized system)
- Pain level: CFO unprompted rated it "8 out of 10"
- Budget: CFO mentioned "we budgeted for process improvements this quarter"

## Stakeholders Present
- Sarah Chen - CFO (champion signals: very engaged, asked about timeline multiple times)
- Mike Torres - VP Operations (neutral: listening mode, asked few questions)
- Lisa Park - Controller (blocker risk: mentioned "happy with current process" twice)

## Pain/Budget/Decision Notes
**Pain:**
- Manual close process takes 5 days vs industry standard 2-3 days
- Audit trail gaps creating compliance risk
- CFO personally involved in reconciliation (not scalable)

**Budget:**
- CFO confirmed budget allocated this quarter for process improvements
- No specific amount mentioned yet

**Decision:**
- CFO appears to be decision maker (mentioned "I'll review with team")
- Unclear if Lisa (Controller) has veto power

## Commitments
**Our commitments:**
- Send ROI calculator by Friday 2025-11-15
- Schedule demo for week of 2025-11-18

**Their commitments:**
- CFO will review with team after receiving ROI calc
- Will provide current process documentation

## Next Steps
- Send ROI calculator (by 2025-11-15) - URGENT
- Schedule demo (target week of 2025-11-18)
- Follow up on current process doc request
```

**Updates to deal.md:**

```markdown
## History
- 2025-11-13: Discovery call with CFO Sarah Chen, VP Ops Mike Torres, Controller Lisa Park

## Generated Artifacts
- 2025-11-13 2025-11-13_discovery_summary.md (Discovery call - pain at 8/10, budget confirmed)

## D1 Tasks
- [ ] Send ROI calculator to Sarah Chen (due: 2025-11-15)

## D7 Tasks
- [ ] Schedule demo for week of 2025-11-18
- [ ] Follow up on current process documentation request

## Metrics / MEDDPICC
### Pain
- Manual month-end close: 5 days (vs 2-3 day industry standard)
- Audit trail gaps creating compliance risk
- CFO involvement not scalable
- Pain intensity: 8/10 (CFO self-rated)

### Budget
- Confirmed: Budget allocated this quarter for process improvements
- Amount: Not yet disclosed

### Decision Process
- CFO Sarah Chen appears to be decision maker
- Risk: Controller Lisa Park mentioned "happy with current process" - potential blocker

## Risks
- Controller (Lisa Park) may block - expressed satisfaction with current process
- Need to understand her veto power in decision
```

**User confirmation:**
```
✅ Created artifacts/calls/2025-11-13_discovery_summary.md
✅ Updated deal.md (History, D1/D7, MEDDPICC, Risks)
📄 Summary: 3 stakeholders, pain at 8/10, budget confirmed, 2 urgent tasks
```

---

### Example 2: Ingest Quote Document

**User Request:**
> "File the quote I just sent to TechCoInc"

**File Location:**
`sample-data/Runtime/Sessions/TechCoInc/raw/quotes/TechCoInc_Proposal_2025-11-13_v2.pdf`

**Skill Execution:**

#### Step 1-2: Determine Deal & Detect Type
```
Deal: TechCoInc
Type: quote (path contains "/raw/quotes/", filename contains "Proposal")
Confidence: HIGH
```

#### Step 3: Process as Quote
```
Read quote PDF (12 pages)

Extracted:
- ACV: $240,000
- Term: 12 months
- Total Contract Value: $240,000 (same as ACV for 1-year term)
- Payment terms: Net 30, invoiced quarterly
- Key SKUs:
  * Enterprise License: $180,000
  * Professional Services (setup): $40,000
  * Training (2 sessions): $20,000
- Special conditions: 15% discount applied (from $282k list price)
- Expiration: Valid until 2025-11-30
```

#### Step 4: Write Artifacts & Update deal.md

**Generated artifact:**
`artifacts/quotes/2025-11-13_quote_snapshot.md`

```markdown
---
generated_by: deal_intake
generated_on: 2025-11-13T15:45:00Z
deal_id: TechCoInc
artifact_type: quote_snapshot
sources:
  - "raw/quotes/TechCoInc_Proposal_2025-11-13_v2.pdf"
---

## Quote Snapshot
**Date Sent:** 2025-11-13
**Quote ID:** Q-2025-1113-ACMECORP-02
**Expires:** 2025-11-30

## Commercial Terms
- **ACV:** $240,000
- **Term:** 12 months
- **Total Contract Value:** $240,000
- **Payment Terms:** Net 30, invoiced quarterly ($60k per quarter)

## Key SKUs / Options
- Enterprise License: $180,000 (15% discount applied)
- Professional Services (setup & implementation): $40,000
- Training (2 sessions, up to 20 users): $20,000

## Notes
- 15% discount applied (from $282k list price)
- Quote valid until 2025-11-30 (17 days)
- Includes standard warranty and 12-month support
```

**Updates to deal.md:**

```markdown
## History
- 2025-11-13: Sent revised quote v2 ($240k ACV, 12-month term, expires 2025-11-30)

## Generated Artifacts
- 2025-11-13 2025-11-13_quote_snapshot.md (Quote v2: $240k ACV, expires 2025-11-30)

## Metrics / MEDDPICC
### ACV
$240,000

### Expected Close Date
2025-11-30 (aligned with quote expiration)

## Stage
Propose (moved from Discover - quote sent)
```

**User confirmation:**
```
✅ Created artifacts/quotes/2025-11-13_quote_snapshot.md
✅ Updated deal.md (ACV: $240k, expected_close: 2025-11-30, stage: Propose)
```

---

### Example 3: Ingest Email Thread

**User Request:**
> "Process the email thread with PharmaCo champion"

**File Location:**
`sample-data/Runtime/Sessions/PharmaCo/raw/emails/2025-11-13_champion_legal_approval.eml`

**Skill Execution:**

#### Step 1-2: Determine Deal & Detect Type
```
Deal: PharmaCo
Type: email (extension is .eml, path contains "/raw/emails/")
Confidence: HIGH
```

#### Step 3: Process as Email
```
Read email thread (7 messages)

Extracted:
- Participants: Jennifer Wu (champion), Alex Johnson (us), Legal team (cc'd)
- Subject: "Legal Review Complete - Ready to Move Forward"
- Key decisions:
  * Legal approved contract terms
  * Security review passed
  * Procurement will issue PO this week
- Tone: Positive and urgent ("let's get this wrapped up by month end")
- Asks from us: Need final MSA signature and W-9 form by Friday
- Asks from them: None (they're ready on their side)
- Commitments:
  * Our side: Provide signed MSA and W-9 by 2025-11-15
  * Their side: Issue PO by end of week (2025-11-15)
```

#### Step 4: Write Artifacts & Update deal.md

**Generated artifact:**
`artifacts/emails/2025-11-13_champion_legal_approval_summary.md`

```markdown
---
generated_by: deal_intake
generated_on: 2025-11-13T16:20:00Z
deal_id: PharmaCo
artifact_type: email_summary
sources:
  - "raw/emails/2025-11-13_champion_legal_approval.eml"
---

## Email Thread Summary
**Date:** 2025-11-13
**Participants:** Jennifer Wu (champion), Alex Johnson (AE), Legal team (cc'd)
**Subject:** Legal Review Complete - Ready to Move Forward

## Key Decisions
- Legal review complete and approved
- Security review passed
- Procurement will issue PO this week

## Tone/Urgency
**Tone:** Positive, enthusiastic
**Urgency:** High - Jennifer mentioned "let's get this wrapped up by month end" multiple times

## Asks & Blockers
**They need from us:**
- Signed MSA (by Friday 2025-11-15)
- W-9 form (by Friday 2025-11-15)

**We need from them:**
- PO issuance (committed by end of week)

**Blockers:** None identified

## Commitments
**Our commitments:**
- Provide signed MSA by 2025-11-15
- Provide W-9 form by 2025-11-15

**Their commitments:**
- Issue PO by end of week (2025-11-15)
- Jennifer will expedite any remaining approvals
```

**Updates to deal.md:**

```markdown
## History
- 2025-11-13: Email from champion Jennifer Wu - legal approved, PO coming this week

## Generated Artifacts
- 2025-11-13 2025-11-13_champion_legal_approval_summary.md (Legal approved, PO this week)

## D1 Tasks
- [ ] Get MSA signed and send to Jennifer (due: 2025-11-15)
- [ ] Send W-9 form to Jennifer (due: 2025-11-15)

## Champion Strength
- Strong: Jennifer actively pushing for month-end close, expediting approvals
```

**User confirmation:**
```
✅ Created artifacts/emails/2025-11-13_champion_legal_approval_summary.md
✅ Updated deal.md (History, D1 tasks, Champion strength)
⚡ High urgency detected - 2 tasks due Friday
```

---

## Edge Cases & Troubleshooting

### Problem: File already processed (idempotency)

**Symptom:**
User tries to ingest same transcript twice

**Behavior:**
```
File "2025-11-13_discovery_zoom_transcript.txt" already processed on 2025-11-13.
Existing artifact: artifacts/calls/2025-11-13_discovery_summary.md
Re-run and overwrite? (Y/n)
```

**User response options:**
- **Y / yes:** Overwrite existing artifact, update deal.md again (useful if new insights)
- **N / no:** Skip processing, exit gracefully

**Implementation note:**
Check deal.md `## Generated Artifacts` section for filename presence before processing.

---

### Problem: deal.md doesn't exist

**Symptom:**
User tries to ingest file for deal that hasn't been set up yet

**Behavior:**
```
Error: deal.md not found at sample-data/Runtime/Sessions/NewDeal/.
Run setup workflow first to create deal structure.
```

**Solution:**
User must run deal setup first (create deal.md, folder structure).

**Do NOT auto-create deal.md** - setup requires user input (deal name, stage, methodology, etc.)

---

### Problem: Cannot detect file type (ambiguous)

**Symptom:**
- File in `raw/` root (not in subfolder)
- Generic filename: `meeting_notes.txt`
- No clear indicators in filename
- Content scan returns mixed signals

**Behavior:**
```
⚠️ Could not auto-detect file type for "meeting_notes.txt"
Pattern matching: No clear indicators
Content scan: 2 transcript indicators, 2 email indicators (ambiguous)

Filed in artifacts/other/2025-11-13_meeting_notes.md with basic summary.

Is this a transcript, quote, slide deck, or email thread?
Please clarify and I can re-process with correct type-specific flow.
```

**Solution:**
1. File as generic artifact in `artifacts/other/`
2. Generate basic summary (what is it, why does it matter)
3. Update deal.md with generic entry
4. Ask user to clarify type
5. If user clarifies, re-run with correct type

---

### Problem: Multiple files in one command

**Symptom:**
User says "ingest all the files in raw/calls/"

**Behavior:**
```
Found 3 files in Sessions/AcmeCorp/raw/calls/:
- 2025-11-10_intro_call.txt
- 2025-11-12_demo.txt
- 2025-11-13_discovery.txt

Processing each file:
1/3: Processing 2025-11-10_intro_call.txt... ✅
2/3: Processing 2025-11-12_demo.txt... ✅
3/3: Processing 2025-11-13_discovery.txt... ⚠️ Already processed (skip)

Summary:
✅ Processed 2 new files
⚠️ Skipped 1 duplicate
📄 Updated deal.md with 2 new history entries, 4 new tasks
```

**Implementation:**
- Use Glob to expand pattern
- Process each file sequentially
- Check idempotency for each
- Batch update deal.md once at end (not after each file)

---

### Problem: Transcript with poor formatting / no speaker labels

**Symptom:**
Zoom auto-transcript with no speaker identification, just wall of text

**Behavior:**
```
⚠️ Transcript detected but no clear speaker labels found
Generated summary may be less detailed than usual

Proceeding with best-effort extraction:
- Objective: [extracted from context]
- Key points: [bullet list of topics discussed]
- Stakeholders: Unable to identify (no speaker labels)
- Next steps: [action items if mentioned]
```

**Solution:**
1. Note in artifact frontmatter: `transcript_quality: poor_formatting`
2. Extract what's possible (topics, action items)
3. Note in summary: "Speaker identification unavailable - review raw transcript"
4. Still update deal.md with what was extracted

---

### Problem: Quote PDF is image-based (scanned), not text

**Symptom:**
Quote is scanned image, Read tool returns gibberish or minimal text

**Behavior:**
```
⚠️ Quote document appears to be scanned image with poor OCR quality
Extracted partial information:
- ACV: Unable to extract
- Term: Possibly 12 months (unclear)

Filed quote snapshot with [OCR QUALITY ISSUE] markers.
Recommend user provide text-based PDF or manual entry for key terms.
```

**Solution:**
1. Extract whatever is readable
2. Flag sections as `[OCR QUALITY ISSUE - verify manually]`
3. Ask user to confirm ACV, term, key terms
4. Still create artifact and update deal.md with what's available

---

### Problem: Deal name ambiguous / multiple deals

**Symptom:**
File path doesn't contain `Sessions/{DEAL}/` and no deal_name provided

**Behavior:**
```
Error: Cannot determine deal name from path: "/path/to/Downloads/transcript.txt"

Available deals:
- AcmeCorp
- TechCoInc
- PharmaCo

Specify deal_name parameter or move file to Sessions/{DEAL}/raw/ before ingesting.
```

**Solution:**
1. List available deals (scan `Sessions/` directory)
2. Ask user to specify
3. Do NOT guess

---

### Problem: File in wrong subfolder (transcript in quotes/)

**Symptom:**
User put transcript file in `raw/quotes/` folder

**Behavior:**
```
Pattern detection: Path says "quotes" but content scan detects transcript (8 indicators)
Confidence: MEDIUM (mixed signals)

Detected as: transcript (content overrides path)

Processing as transcript...
✅ Created artifacts/calls/2025-11-13_discovery_summary.md

💡 Tip: File was in raw/quotes/ but appears to be a transcript.
Consider organizing files in correct subfolders for faster processing.
```

**Solution:**
- Use content scan as tiebreaker when path and content disagree
- Proceed with content-based type
- Give gentle reminder to user about folder organization
- Still process successfully (be forgiving)

---

## Tips for Effective Intake

### 1. Organize raw/ Files by Type

**Best practice folder structure:**
```
Sessions/AcmeCorp/raw/
├── calls/           ← All transcripts, recordings
├── quotes/          ← Proposals, pricing docs
├── slides/          ← Presentation decks
├── emails/          ← Email threads (.eml exports)
└── other/           ← Misc (contracts, legal, SOWs)
```

**Why:** Faster type detection, clearer organization, easier to find files later

---

### 2. Use Descriptive Filenames

**Good:**
- `2025-11-13_discovery_call_zoom_transcript.txt`
- `2025-11-13_proposal_v2_final.pdf`
- `2025-11-13_demo_deck_exec_overview.pptx`

**Bad:**
- `transcript.txt` (no date, unclear which call)
- `proposal.pdf` (no version, no date)
- `deck.pptx` (no context)

**Why:** Easier to track artifacts over time, clearer in deal.md history

---

### 3. Ingest Files Promptly After Events

**Workflow:**
```
Discovery call ends → Export Zoom transcript → Drop in raw/calls/ → Run deal_intake
```

**Benefits:**
- deal.md always current
- D1/D7 tasks captured while fresh
- Easier to remember context for review

---

### 4. Review Generated Artifacts

**After intake, always:**
1. Open generated artifact (e.g., `artifacts/calls/2025-11-13_discovery_summary.md`)
2. Verify key info extracted correctly
3. Add manual notes if needed (use Edit tool)
4. Check deal.md updates are accurate

**Why:** LLM extraction is good but not perfect - human review catches gaps

---

### 5. Batch Process When Possible

**Instead of:**
```
"Ingest 2025-11-10_call.txt"
"Ingest 2025-11-12_demo.txt"
"Ingest 2025-11-13_discovery.txt"
```

**Do:**
```
"Ingest all files in raw/calls/"
```

**Why:** More efficient, single deal.md update, better for you

---

## Version History

- **1.0** (2025-11-13): Initial skill created as part of two-lane intake model
  - Type detection with pattern matching + content scanning
  - Five artifact types: transcript, quote, slides, email, generic
  - deal.md update protocol for History, D1/D7, MEDDPICC, Risks
  - Idempotency handling
  - Methodology-neutral extraction

---

## Performance Optimization

This section provides detailed guidance on parallel agent execution for multi-file operations.

### When to Use Parallel Agents

**Recommended by Claude Code documentation:** "Launch multiple agents concurrently whenever possible to maximize performance"

**Decision matrix:**

| File Count | Strategy | Agent Count | Rationale |
|------------|----------|-------------|-----------|
| 1-2 files | Serial | 0 (process directly) | Overhead not worth it |
| 3-5 files | Parallel | N (one per file) | Maximum isolation, manageable coordination |
| 6-10 files | Parallel | 5 agents | Batch files to avoid overhead |
| 10+ files | Parallel | 5 agents | Strategic batching (CRM first, then by type) |

### Why Cap at 5 Agents?

1. **Proven pattern** from `convert-and-file` skill (processed 58 PDFs with 5 agents)
2. **Orchestration overhead** increases non-linearly beyond 5
3. **API rate limit safety** margin
4. **Diminishing returns** (5 concurrent is already very fast)

### File Batching Strategy (6+ Files)

**Priority order for batching:**

1. **CRM exports** (Agent 1 dedicated - most authoritative data)
2. **Quotes** (Agent 2 - contains ACV, terms)
3. **Transcripts** (Agents 3-5 - divide evenly)
4. **Emails** (Agent 5 if space, otherwise batch with Agent 4)

**Example: 12 files (1 CRM + 8 transcripts + 2 quotes + 1 email)**

```
Agent 1: CRM export (priority)
Agent 2: Quote 1, Quote 2
Agent 3: Transcripts 1-3
Agent 4: Transcripts 4-6
Agent 5: Transcripts 7-8, Email 1
```

### Performance Benchmarks

| Scenario | Serial Time | Parallel (5 agents) | Speedup |
|----------|-------------|---------------------|---------|
| 5 files (AcmeCorp) | ~15 min | ~3 min | **5× faster** |
| 12 files (large deal) | ~30 min | ~6 min | **5× faster** |
| 50 files (massive import) | ~2 hours | ~25 min | **~5× faster** |

**Note:** Speedup plateaus at ~5× due to orchestration overhead and sequential aggregation step.

### Token Budget Comparison

| Approach | Total Tokens | Quality | Notes |
|----------|--------------|---------|-------|
| Serial (4 files) | 80-100K | Degrades after file 2 | Token pressure causes shortcuts |
| Parallel (4 agents) | 4 × 20-25K = 80-100K | Consistent | Each agent has fresh 200K budget |

**Key advantage:** Token isolation prevents quality degradation in later files.

### Implementation Pattern

**For 5 files (4 transcripts + 1 CRM export):**

1. Launch 5 agents in parallel:
   ```
   Agent 1: Process salesforce_notes.md (CRM export)
   Agent 2: Process transcript_1.txt
   Agent 3: Process transcript_2.txt
   Agent 4: Process transcript_3.txt
   Agent 5: Process transcript_4.txt
   ```

2. Each agent receives prompt:
   ```markdown
   Process this file for deal_intake:
   - Deal: AcmeCorp
   - File: {file_path}
   - Auto-detect type (transcript/quote/email/slides/crm_export)
   - Generate summary with full frontmatter
   - Return markdown content (don't write to disk)
   ```

3. Wait for all agents to complete (blocking)

4. Aggregate:
   - Write all 5 artifact files
   - Merge data using precedence rules (CRM > Quote > Transcript)
   - Update deal.md once with consolidated changes

5. Report to user:
   ```
   ✅ Processed 5 files in parallel (~3 min vs ~15 min serial)
   ✅ Created 5 artifacts
   ✅ Updated deal.md (ACV: $144K from CRM, Close: Oct 2026, EB: Jane Smith)
   ```

### Alternative: Batch Processing (Small Files Only)

**For files < 5K tokens each:**

You can process multiple files in one prompt:
```
Process these 4 transcripts:
1. file1.txt
2. file2.txt
3. file3.txt
4. file4.txt

Generate summaries for all 4.
```

**Pros:** Single API call, faster latency
**Cons:** Still faces token pressure, all-or-nothing (one failure = redo everything)

**Recommendation:** Use parallel agents for quality and fault tolerance.

---

## Data Precedence

Detailed field-by-field precedence rules and conflict resolution examples.

### Precedence Hierarchy

**When multiple sources provide conflicting data, use this priority:**

1. **ACV:**
   - CRM export > Quote document > Transcript (explicit mention) > TBD
   - Example: If CRM says "$144K" and transcript says "awaiting quote", use "$144K"

2. **Close Date:**
   - CRM export > Quote expiration date > Transcript discussion > TBD
   - Example: If CRM says "Oct 2026" and transcript says "budget decision Sept", note both (budget gate ≠ close date)

3. **Economic Buyer:**
   - CRM export field > Transcript identification > Inference from stakeholders
   - Example: If CRM says "Jane Smith (CFO)" use that, not "multiple EBs"

4. **Competitors:**
   - CRM export list > Transcript mention > TBD
   - Example: If CRM says "AssurX, Instant GMP" use that, not "Shurex, ETQ" from transcript

5. **Stage:**
   - CRM export stage (map to framework stages) > deal.md current stage
   - Only update if CRM stage is more advanced

### Conflict Resolution

**General rules:**
- Log conflicts in artifact's "Notes" section
- Use higher-priority source in deal.md
- Keep both values if they represent different things (e.g., budget decision date vs. close date)

**Example conflict:**
```
Transcript says: "They mentioned $150K budget"
CRM export says: "ACV: $144,781"
Quote doc says: "Total: $144,781"

Resolution: Use $144,781 (CRM + Quote agree, transcript was estimate)
```

