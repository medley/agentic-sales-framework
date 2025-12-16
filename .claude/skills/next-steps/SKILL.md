---
license: "MIT - See LICENSE.md"
name: next-steps
description: Analyzes deal state (stage + methodology) to recommend 3-5 specific, calendar-worthy next actions. Flags missing information and suggests which skills to run next. Use when the user needs tactical action recommendations to drive deal momentum forward.
allowed-tools: [Read, Write, Glob]
---

# Next Steps — Runtime Specification

**Version:** 1.0
**Purpose:** Generate concise, actionable next-step recommendations to maintain deal momentum
**Reference:** See `reference.md` for detailed examples, methodology-specific guidance, and edge cases

---

## When to Use This Skill

**Activate when:**
- User asks "What's next?" or "Next steps for [deal]?"
- After deal_intake (automatic follow-up recommendations)
- Before weekly deal reviews (refresh D1/D7 tasks)
- When deal feels stuck or unclear on priorities
- After stage transitions (what's needed to advance)
- User requests: "What should I do next on [deal]?"

**Do NOT use for:**
- Full strategic coaching (use `coach` skill instead)
- Generating artifacts like emails/agendas (use `sales_communications` or `prep-discovery`)
- Portfolio-level analysis (use `portfolio` skill)
- Deep deal health assessment (use `coach` skill)

---

## Core Principles

1. **Brevity First:** Output MUST fit on one page (400-600 words max)
2. **Calendar-Worthy:** Every action gets a date/deadline and owner
3. **Methodology-Aware:** Recommendations based on stage exit criteria
4. **Skill Orchestration:** Suggest which skills help execute the actions
5. **Specific Not Generic:** "Schedule tech validation with VP Ops" not "follow up"
6. **Gap-Focused:** Highlight what's blocking stage advancement

---

## Processing Algorithm

### Step 1: Load Deal Context

1. **Locate deal file:**
   - User provides: `sample-data/Runtime/Sessions/{deal_name}/deal.md`
   - Or extract from current context
   - If unclear → ERROR and ask user

2. **Read deal.md:**
   - Current stage and health
   - Recent history (last 3-5 entries)
   - Existing D1/D7 tasks
   - Stakeholder map
   - MEDDPICC/qualification status
   - Risks & gaps

3. **Scan deal directory:**
   - Recent artifacts (what's been done)
   - Missing artifacts (what's needed but not created)

4. **Error handling:**
   - File not found → "deal.md not found at Sessions/{DEAL}/. Run setup first."
   - No recent activity → Note in output ("Last update: [date], deal may be stale")

---

### Step 2: Load Methodology Context

**Follow `Framework/System/methodology_loader.md` protocol:**

1. **Read methodology from deal frontmatter** (default: "Generic")

2. **Load stage inventory:**
   - Path: `sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md`
   - If missing → use Generic fallback (per methodology_loader.md)

3. **Extract for current stage:**
   - `exit_criteria` - What must be true to advance?
   - `required_artifacts` - What documents/outputs are needed?
   - `risk_indicators` - What red flags should we watch for?
   - `question_frameworks` - What discovery/qualification questions remain?

4. **Optional:** Read `Framework/Methodologies/{Methodology}.md` for background context

---

### Step 3: Analyze Gaps & Priorities

**Identify what's missing or blocking progress:**

1. **Exit Criteria Gaps:**
   - Compare current deal state vs stage exit criteria
   - Example: "Champion identified? NO" → Action: Identify and cultivate champion

2. **Information Gaps:**
   - Missing stakeholder info (no Economic Buyer name/title)
   - Unknown decision process (no timeline, approval steps unclear)
   - Budget not qualified (no ACV, no budget authority confirmed)

3. **Artifact Gaps:**
   - Required but missing: discovery agenda, proposal, ROI analysis
   - Check `required_artifacts` from stage inventory

4. **Time-Sensitive Items:**
   - Upcoming calls/meetings without prep
   - Commitments due soon (from History)
   - Close date approaching with gaps

5. **Stale Tasks:**
   - D1 tasks older than 2 days → escalate or re-assess
   - D7 tasks older than 10 days → remove or update

---

### Step 4: Generate Recommendations

**Create 3-5 specific, prioritized next actions:**

**Priority Rules:**
1. **D1 (Next 24 Hours):** Urgent items (1-2 actions max)
   - Commitments due tomorrow
   - Calls tomorrow needing prep
   - Critical blockers

2. **D7 (This Week):** Important items (2-3 actions max)
   - Advance stage exit criteria
   - Fill information gaps
   - Create required artifacts

**Action Format:**
Each action must include:
- **Specific task** (not "follow up")
- **Owner** (You, SE, Manager, etc.)
- **Deadline** (date or "by when")
- **Rationale** (why this matters, tied to deal objective)

**Example:**
```markdown
### D1 Actions (Next 24 Hours)
1. **Send technical validation questions to VP Operations**
   - Owner: You
   - Deadline: Nov 15 by 2 PM
   - Why: Economic Buyer needs technical sign-off before Nov 30 board meeting
   - How: Use sales_communications/email_cold_outbound pattern
```

---

### Step 5: Identify Missing Exit Criteria

**Map unmet stage exit criteria to actions:**

For each unmet criterion:
- State what's missing
- Recommend how to get it
- Link to methodology reasoning

**Example:**
```markdown
### Missing Exit Criteria (MEDDPICC - Discovery Stage)
❌ **Champion:** Not identified or cultivated
   → Action: Review stakeholder map, identify who has power + pain + willingness to sell internally

❌ **Paper Process:** Decision timeline unknown
   → Action: In next call, ask "What does the approval process look like after we submit a proposal?"
```

---

### Step 6: Suggest Skills to Run Next

**Recommend which skills would help execute the actions:**

**Skill Recommendation Logic:**
- Missing discovery agenda → `prep-discovery`
- Need follow-up email → `sales_communications/{pattern}`
- New files to process → `deal_intake`
- Need full coaching → `coach`
- Multiple deals to review → `portfolio`

**Format:**
```markdown
### Suggested Skills to Run Next
1. **prep-discovery** - Discovery call on Nov 20 but no agenda created yet
2. **sales_communications/email_internal_prep** - Technical deep-dive needs team alignment
```

---

### Step 7: Format Output (ONE-PAGE CONSTRAINT)

**CRITICAL: Output must fit on single screen (400-600 words max)**

**Required Sections:**
1. **Header** (deal name, stage, date)
2. **D1 Actions** (1-2 items)
3. **D7 Actions** (2-3 items)
4. **Missing Exit Criteria** (2-3 gaps)
5. **Suggested Skills** (1-3 skills)

**Optional Sections (only if space allows):**
- **Missing Information** (critical gaps only)
- **Stale Tasks** (cleanup recommendations)

**Formatting Rules:**
- Tight bullet points (no paragraph walls)
- One-line rationales (not essays)
- Use emoji sparingly (❌, ✅ for criteria status)
- Reference file paths for sources

**Template:**
```markdown
# Next Steps - [Deal Name]

**Generated:** YYYY-MM-DD | **Stage:** [Stage Name] | **Health:** [Health Status]

## D1 Actions (Next 24 Hours)
- [ ] **[Date/Time]** - [Specific task] (Owner: [Name])
  Why: [One-line rationale]

## D7 Actions (This Week)
- [ ] **[Deadline]** - [Specific task] (Owner: [Name])
  Why: [One-line rationale]

## Missing Exit Criteria ([Methodology] - [Stage])
❌ **[Criterion]:** [What's missing]
   → Action: [How to get it]

## Suggested Skills to Run Next
1. **[skill-name]** - [Why you should run this skill]

---
## Provenance
source_deal: ../../deal.md
generated_by: next-steps
generated_at: YYYY-MM-DD
methodology_ref: sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md
```

---

### Step 8: Generate Chat Output

**Purpose:** Provide concise next-steps summary for chat/UI display.

**Format:**
- Heading: `# Chat Output`
- Single markdown code fence containing 3-5 action bullets
- NO full report, NO detailed sections, NO frontmatter

**Content:**
- Top 2-3 D1 actions (urgent, next 24 hours)
- Top 1-2 D7 actions (this week)

**Example:**
```markdown
# Chat Output

```markdown
**Next Steps - Acme Corp**

**D1 (Next 24 Hours):**
- Send technical validation questions to VP Operations (Nov 15 by 2pm)
- Request warm intro to CFO from champion John (EOD today)

**D7 (This Week):**
- Schedule multi-threading session with Ops + Security (by Friday)
- Create ROI model for Economic Buyer presentation (by Wed)
```
```

**Rules:**
- Keep under 80 words total
- Focus on actions only, minimal context
- No emoji in Chat Output

### Step 9: Generate Artifact Output (Full Next-Steps Report)

**Purpose:** Create the complete next-steps report for storage.

**Format:**
- Heading: `# Artifact Output`
- Single markdown code fence containing full report with frontmatter

**Content:** Full next-steps report (400-600 words) with all sections from Step 7

**Example structure:**
```markdown
# Artifact Output

```markdown
---
generated_by: next-steps
generated_on: 2025-11-15T10:00:00Z
deal_id: Acme Corp
methodology: MEDDPICC
stage: 2
sources:
  - sample-data/Runtime/Sessions/Acme Corp/deal.md
  - sample-data/Runtime/_Shared/knowledge/methodologies/MEDDPICC/stage_inventory__MEDDPICC.md
---

# Next Steps - Acme Corp

**Stage:** 2 (Qualify) | **Date:** Nov 15, 2025

## D1 Actions (Next 24 Hours)
1. **Send technical validation questions to VP Operations**
   - Owner: You
   - Deadline: Nov 15 by 2 PM
   - Why: Economic Buyer needs technical sign-off before Nov 30 board meeting
   - How: Use sales_communications/email_cold_outbound pattern

2. **Request warm intro to CFO from champion John**
   - Owner: You
   - Deadline: EOD Today
   - Why: No Economic Buyer identified - critical Stage 2 gap

## D7 Actions (This Week)
[...]

## Missing Exit Criteria (MEDDPICC - Qualify Stage)
[...]

## Suggested Skills to Run Next
[...]
```
```

### Step 10: Emit Structured JSON Summary

**Purpose:** Provide machine-readable summary for API/Next.js app consumption.

**Format:**
- Code fence with label: ` ```json summary `
- This is the THIRD and FINAL section of the three-section envelope

**CRITICAL Output Order:**
1. `# Chat Output` (Step 8)
2. `# Artifact Output` (Step 9)
3. ` ```json summary` (Step 10 - this step)
4. Nothing else after the closing fence

**JSON Schema:** Use coaching schema (summaryBullets, risks, missingInformation, d1Actions, d7Actions)

```json
{
  "summaryBullets": ["Stage 2 next actions", "Focus on Economic Buyer engagement"],
  "risks": ["No Economic Buyer", "Single-threaded"],
  "missingInformation": ["Budget authority", "Decision process"],
  "d1Actions": [
    {
      "label": "Send technical validation questions to VP Operations",
      "owner": "You",
      "deadline": "Nov 15 by 2 PM",
      "rationale": "Economic Buyer needs technical sign-off before Nov 30 board meeting"
    }
  ],
  "d7Actions": [
    {
      "label": "Schedule multi-threading session with Ops + Security",
      "owner": "You + SE",
      "deadline": "This Friday",
      "rationale": "Single-threaded risk - expand stakeholder map"
    }
  ]
}
```

**Validation:**
- ✅ Valid JSON - passes JSON.parse()
- ✅ All required fields present
- ✅ Nothing after closing fence

### Step 11: Write Output File

1. **Determine output path:**
   ```
   sample-data/Runtime/Sessions/{DEAL_NAME}/next_steps_{YYYY-MM-DD}.md
   ```

2. **Use Write tool** to save ONLY Artifact Output content (with frontmatter)

3. **Verify brevity:**
   - Count words (must be 400-600 range)
   - If over 600 → cut optional sections or condense rationales

---

### Step 12: Update deal.md (Optional)

**Ask user first:** "Update deal.md D1/D7 tasks with these recommendations? (Y/n)"

**If Yes:**
1. **Replace D1 Tasks section:**
   - Clear old tasks (if stale)
   - Insert new D1 actions

2. **Replace D7 Tasks section:**
   - Clear old tasks (if stale)
   - Insert new D7 actions

3. **Update History:**
   - Append: `- {DATE}: Generated next-steps recommendations`

4. **Use Edit tool** for updates

**Power User Option:** Support `--auto` flag to skip confirmation

---

## Error Handling

**deal.md not found:**
```
Error: deal.md not found at sample-data/Runtime/Sessions/{DEAL}/.
Run setup workflow first to create deal structure.
```

**Deal name unclear:**
```
Error: Cannot determine deal name.
Which deal do you want next-step recommendations for?
```

**No methodology found:**
```
Warning: Methodology not specified in deal.md frontmatter.
Using Generic best practices for recommendations.
```

**Stale deal (no activity > 30 days):**
```
⚠️ Last activity: {DATE} ({days_ago} days ago)
This deal may be stale. Consider archiving or re-engaging.
```

**No gaps found:**
```
✅ All exit criteria met for current stage.
Consider advancing to next stage or running coach skill for strategic review.
```

---

## Quick Reference

### Trigger Phrases
- "What's next for [deal]?"
- "Next steps for [deal]"
- "What should I do next on [deal]?"
- "Update my next actions for [deal]"

### Output Path
```
sample-data/Runtime/Sessions/{DEAL_NAME}/next_steps_{YYYY-MM-DD}.md
```

### Word Count Constraint
**Target:** 400-600 words
**Maximum:** 600 words (hard limit)

### Priority Logic
- **D1:** Urgent (< 24 hours), critical blockers
- **D7:** Important (< 7 days), stage advancement

### Skill Recommendations
Always suggest 1-3 skills that help execute the recommended actions

---

## Integration Points

### With Other Skills
- **After deal_intake:** Automatically suggest next-steps
- **Before prep-discovery:** Run next-steps to identify prep priorities
- **With coach skill:** Coach provides strategy, next-steps provides tactics

### With Methodology System
- Loads stage inventory via `methodology_loader.md`
- Uses exit criteria to identify gaps
- Methodology-agnostic (works with Sandler, MEDDPICC, Generic, etc.)

### Power User Workflows
```bash
# Quick recommendation
"What's next for TechCoInc?"

# Auto-update deal.md
"Next steps for TechCoInc --auto"

# After intake workflow
"Ingest transcript for TechCoInc" → deal_intake runs
"What's next?" → next-steps runs
```

---

## Additional Resources

**For detailed examples:**
- See `reference.md` (methodology walkthroughs, edge cases, advanced patterns)

**Related Skills:**
- `coach` - Strategic deal coaching
- `prep-discovery` - Discovery call preparation
- `sales_communications` - Artifact generation
- `deal_intake` - Process deal artifacts

**Methodology Handling:**
- `Framework/System/methodology_loader.md` - Protocol for loading sales methodologies

---

**Version History:**
- **1.0** (2025-11-14): Initial skill created for tactical next-action recommendations
