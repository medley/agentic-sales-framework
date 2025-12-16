---
name: deal-review-panel
description: Multi-agent deal review simulating team collaboration. Launches 4 specialized reviewers (Qualification, Competitive, Executive Alignment, Deal Mechanics) who independently analyze a deal, debate with each other, then synthesize findings into prioritized recommendations. Use for complex deals, stage gates, deals stuck over 30 days, or high-value opportunities requiring multiple perspectives. NOT for quick pre-call prep (use coach skill instead).
allowed-tools: [Read, Write, Glob, Grep, Task]
license: "MIT - See LICENSE.md"
metadata:
  version: "1.0"
---

# Deal Review Panel

## Overview

Provides multi-agent AI deal review by orchestrating 4 specialized reviewers who independently analyze deal health, debate their findings, and synthesize a unified coaching report. Simulates a team deal review meeting with diverse perspectives (methodology compliance, competitive positioning, executive alignment, deal mechanics).

Each reviewer brings a distinct lens:
- **Qualification Analyst** - Methodology compliance, disqualification specialist
- **Competitive Strategist** - Win/loss analysis, positioning expert
- **Executive Alignment Coach** - Stakeholder dynamics, Economic Buyer engagement
- **Deal Mechanics Reviewer** - Timeline, legal, procurement specialist

The multi-agent debate surfaces blind spots, contradictions, and alternative strategies that single-perspective analysis might miss.

## Core Principles

1. **Dialectic Over Monologue** - Multiple perspectives reveal hidden risks and opportunities
2. **Evidence-Based Debate** - Reviewers cite deal.md, not opinions
3. **Conflict Surfacing** - Disagreements are documented, not hidden (let user decide)
4. **Attribution Clarity** - "Panel Consensus (4/4)" vs. "Per Competitive Strategist"
5. **Actionable Synthesis** - Final report is 400-600 words with specific D1/D7 actions
6. **Methodology-Aware** - All reviewers adapt to deal's methodology (MEDDPICC, Sandler, Generic)

## When to Use This Skill

**Activate when:**
- Complex or high-value deals requiring multiple perspectives
- Stage gate reviews (advancing from Qualify → Propose, etc.)
- Deal stuck for >30 days with unclear path forward
- Conflicting internal opinions on deal health
- Formal deal reviews with leadership
- User asks: "Review this deal", "Is this deal winnable?", "Give me multiple perspectives on [deal]"

**Do NOT use for:**
- Quick pre-call prep (use `coach` skill instead - faster, single perspective)
- Portfolio-level analysis (use `portfolio` skill instead)
- Simple status checks (use `next-steps` skill)
- Generating specific artifacts like emails (use `sales_communications`)

## Workflow

### Step 1: Load Deal Context

1. **Identify deal:**
   - If user provides deal name → `sample-data/Runtime/Sessions/{DEAL}/deal.md`
   - If ambiguous → Ask user: "Which deal? (e.g., 'Acme Corp', 'TechCo')"

2. **Validate deal note exists:**
   - Path: `sample-data/Runtime/Sessions/{DEAL}/deal.md`
   - If not found → ERROR: `Deal note not found. Create with: cp Framework/Templates/deal_template.md sample-data/Runtime/Sessions/{DEAL}/deal.md`

3. **Parse deal.md:**
   - **Frontmatter:** Extract `methodology`, `stage`, `deal_id`, `generated_by`
   - **Body:** Parse stakeholders, timeline, interaction history, known risks

4. **Scan deal directory for artifacts:**
   - Use Glob: `sample-data/Runtime/Sessions/{DEAL}/**/*.md`
   - Identify: Discovery notes, agendas, emails, prior coaching reports, competitive intel

5. **Build deal_state summary (for reviewers):**
   - Current stage, methodology, health status
   - Stakeholder map (Economic Buyer, Champion, Technical, Legal/Procurement)
   - Timeline and next milestone
   - Last 3-5 interactions
   - Known risks and gaps
   - Existing artifacts

**Error handling:**
- Deal note missing → HALT with error message
- Malformed frontmatter → Warn, attempt body parse
- Missing methodology → Default to Generic
- Empty deal directory → Proceed (note "No artifacts found")

### Step 2: Load Methodology Context

**Follow `Framework/System/methodology_loader.md` protocol:**

1. **Detect methodology:**
   - Check deal.md frontmatter for `methodology: {name}`
   - Default: `Generic` if not specified

2. **Load stage inventory (primary source):**
   - Path: `sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md`
   - Extract for current stage:
     - `exit_criteria` - What must be true to advance
     - `required_artifacts` - Documents/outputs needed
     - `risk_indicators` - Red flags
     - `question_frameworks` - Discovery/qualification questions

3. **Optional background:**
   - Path: `Framework/Methodologies/{Methodology}.md`
   - Provides philosophy and principles (read-only)

4. **Fallback if missing:**
   - Use Generic methodology or hardcoded B2B stages
   - Note in output: "Using generic B2B model (no custom methodology found)"

### Step 3: Launch 4 Reviewer Agents (Parallel)

**Load reviewer personas:**
- Read: `.claude/skills/deal-review-panel/references/reviewer_personas.md`
- Extract 4 persona definitions (analysis frameworks, principles, typical stance)

**Launch 4 Task agents in parallel (single message, 4 tool calls):**

For each reviewer:
1. **Use Task tool with:**
   - `subagent_type: "general-purpose"`
   - `model: "sonnet"` (balance quality/cost)
   - `description: "{Reviewer Role} analysis of {DEAL}"`

2. **Provide prompt with:**
   - Full deal_state summary (from Step 1)
   - Methodology stage inventory (from Step 2)
   - Reviewer persona definition (from reviewer_personas.md)
   - Analysis constraints:
     - **Output limit:** 200 words max
     - **Required sections:** Top 3 Risks, D1 Actions (next 24h), D7 Actions (next 7d), Key Gaps, Overall Sentiment
     - **Evidence requirement:** Cite deal.md sections, not assumptions
   - Instruction: "Analyze this deal from the {Persona} perspective. Focus on your domain expertise. Be specific, not generic."

3. **Collect outputs:**
   - Save each reviewer's analysis to structured object:
     ```
     reviewer_analyses = {
       "Qualification Analyst": {...},
       "Competitive Strategist": {...},
       "Executive Alignment Coach": {...},
       "Deal Mechanics Reviewer": {...}
     }
     ```

**Example Task prompt for Qualification Analyst:**

```
You are the Qualification Analyst reviewing a B2B SaaS deal. Your role is to scrutinize methodology compliance and identify disqualification signals.

**Deal State:**
{deal_state_summary}

**Methodology Stage Inventory:**
{stage_exit_criteria}

**Your Analysis Framework:**
{persona_definition_from_reviewer_personas.md}

**Task:**
Analyze this deal from the Qualification Analyst perspective. Output exactly:

1. **Top 3 Risks** (qualification gaps, disqualification signals)
2. **D1 Actions** (next 24 hours - what to do immediately)
3. **D7 Actions** (next 7 days - qualification tests, artifact creation)
4. **Key Gaps** (missing information blocking qualification)
5. **Overall Sentiment** (Optimistic | Neutral | Pessimistic)

**Constraints:**
- 200 words max
- Cite specific deal.md sections
- No vague advice ("improve relationships" → "Schedule 1:1 with CFO by Friday")
- Focus on disqualification opportunities (disqualifying bad deals = success)

Output format:
## Top 3 Risks
1. ...

## D1 Actions
- ...

## D7 Actions
- ...

## Key Gaps
- ...

## Overall Sentiment
{Optimistic | Neutral | Pessimistic}
```

### Step 4: Run Debate Round (Sequential)

**For each reviewer (4 sequential Task calls):**

1. **Provide prompt with:**
   - Original deal_state summary
   - **All 4 reviewer analyses from Step 3** (not just their own)
   - Persona definition (same as Step 3)
   - Debate constraints:
     - **Output limit:** 100 words max
     - **Required:** Agreements (with which reviewers, on what), Disagreements (with which reviewers, why), New insights

2. **Instruction:**
   "Review the analyses from all 4 reviewers. From your {Persona} perspective:
   - What do you AGREE with from other reviewers?
   - What do you DISAGREE with and why?
   - Any new insights after seeing other perspectives?

   100 words max. Be specific about which reviewer and which point."

3. **Collect debate outputs:**
   ```
   reviewer_debates = {
     "Qualification Analyst": "...",
     "Competitive Strategist": "...",
     "Executive Alignment Coach": "...",
     "Deal Mechanics Reviewer": "..."
   }
   ```

### Step 5: Synthesize Panel Report

**Load synthesis protocol:**
- Read: `.claude/skills/deal-review-panel/references/debate_synthesis.md`
- Apply conflict resolution framework

**Execute synthesis:**

1. **Identify consensus vs. conflicts:**
   - **Panel Consensus (3-4 reviewers agree):** High confidence → D1 actions
   - **Split decision (2 vs. 2):** Surface tension, resolve with evidence or sequence
   - **Specialist insight (1 reviewer):** Defer to domain expert (e.g., Deal Mechanics on legal timeline)

2. **Resolve conflicts:**
   - **Timing disagreement** (now vs. later) → Resolve based on urgency
   - **Priority disagreement** (focus A vs. B) → Resolve based on stage exit criteria
   - **Approach disagreement** (aggressive vs. conservative) → Resolve based on deal health
   - Apply heuristics from debate_synthesis.md:
     - Stage 1-2: Favor Qualification Analyst (disqualification is success early)
     - Stage 3-4: Favor Competitive Strategist (positioning critical mid-stage)
     - Stage 5-6: Favor Deal Mechanics (execution risk highest)
     - All stages: Executive Alignment Coach wins on Economic Buyer questions

3. **Prioritize actions:**
   - **D1 (Next 24 Hours):** 3-5 actions max
     - Blockers to stage advancement (consensus)
     - Economic Buyer engagement (if missing)
     - Disqualification-level risks (if time-sensitive)
     - Competitive displacement threats (if imminent)
   - **D7 (Next 7 Days):** 5-7 actions max
     - Artifact creation (per methodology)
     - Stakeholder expansion
     - Competitive positioning
     - Legal/procurement process mapping

4. **Generate unified coaching report:**
   - Structure per debate_synthesis.md (Panel Snapshot, Panel Consensus, Debate Highlights, D1/D7 Actions, Unresolved Tensions, Missing Info, Suggested Skills)
   - **Word count:** 400-600 words (CRITICAL constraint)
   - **Attribution:** "Panel Consensus (4/4)" or "Per {Reviewer Name}"
   - **Surface conflicts:** Don't hide disagreements, let user decide

### Step 6: Generate Chat Output

**Purpose:** Provide a concise panel summary for chat/UI display (3-7 bullets).

**Format:**
- Heading: `# Chat Output`
- Single markdown code fence containing 3-7 bullet points
- NO full report, NO detailed sections, NO frontmatter

**Content:**
- Panel verdict and consensus
- Top 1-3 priorities from panel review
- Critical D1 actions

**Example:**
```markdown
# Chat Output

```markdown
**Panel Verdict:** AT RISK (3/4 reviewers pessimistic)

**Panel Consensus:**
- No Economic Buyer engaged after 45 days (Qualification + Exec Alignment + Competitive flagged)
- Competitor has inside track with CTO (Competitive Strategist)
- 7-day test: CFO meeting must be scheduled by next Friday or disqualify

**D1 Panel Priority:**
- Champion must secure CFO intro by EOD tomorrow (Panel Consensus 4/4)
- Map legal/procurement process with champion (Deal Mechanics)
```
```

**Rules:**
- Keep under 100 words total
- Focus on consensus and top priorities
- No emoji in Chat Output (use in Artifact Output only)

### Step 7: Generate Artifact Output (Full Panel Report)

**Purpose:** Create the complete panel review report for storage and detailed review.

**Format:**
- Heading: `# Artifact Output`
- Single markdown code fence containing the full report

**Content structure:**

1. **YAML frontmatter:**
   ```yaml
   ---
   generated_by: deal-review-panel
   generated_on: {ISO_TIMESTAMP}  # YYYY-MM-DDTHH:MM:SSZ
   deal_id: {DEAL_NAME}
   review_type: {stage_gate|weekly_review|deal_stuck|status}
   methodology: {METHODOLOGY}
   stage: {STAGE_NUMBER}
   panel_verdict: {STRONG|QUALIFIED|AT_RISK|DISQUALIFY}
   sources:
     - sample-data/Runtime/Sessions/{DEAL}/deal.md
     - [other artifacts reviewed]
   reviewers:
     - Qualification Analyst
     - Competitive Strategist
     - Executive Alignment Coach
     - Deal Mechanics Reviewer
   ---
   ```

2. **Body (400-600 words total, CRITICAL constraint):**

   ```markdown
   # Deal Review Panel Report - {Company Name}

   **Generated:** {DATE} | **Stage:** {STAGE} | **Methodology:** {METHODOLOGY} | **Panel Verdict:** {STRONG|QUALIFIED|AT_RISK|DISQUALIFY}

   ## Panel Snapshot (6 bullets)
   - Stage {X} - {one_line_health_summary}
   - ACV: ${amount} | Close Date: {date} | Probability: {X}%
   - Last Activity: {date} ({days_ago} days ago)
   - Champion: {Name/Title} | Economic Buyer: {Name/Title or "NOT IDENTIFIED"}
   - Competition: {Primary competitor or "None known"}
   - Panel Verdict: {STRONG|QUALIFIED|AT_RISK|DISQUALIFY}

   ## Panel Consensus (Top 3 Risks)
   1. 🔴 **{Risk Name}** - {brief impact} → {mitigation}
      - **Flagged by:** {Reviewer names}
   2. 🟡 **{Risk Name}** - {brief impact} → {mitigation}
      - **Flagged by:** {Reviewer names}
   3. 🟠 **{Risk Name}** - {brief impact} → {mitigation}
      - **Flagged by:** {Reviewer names}

   ## Panel Debate Highlights
   - **{Conflict Topic}:** {Reviewer A} says {position}. {Reviewer B} counters: {counterpoint}. **Resolution:** {synthesized recommendation}

   ## Recommended Actions

   ### D1 (Next 24 Hours) - Panel Priority
   - [ ] **{Deadline}** - {Specific action with Who} (Owner: {Name})
     - Why: {Rationale} - **Panel Consensus (4/4)** or **Per {Reviewer}**

   ### D7 (This Week) - Panel Priority
   - [ ] **{Deadline}** - {Specific action with Who} (Owner: {Name})
     - Why: {Rationale} - **Per {Reviewer} + {Reviewer}**

   ## Unresolved Panel Tensions
   - **{Tension Topic}:** {Disagreement summary - let user decide}

   ## Missing Information (Panel Gaps)
   - [ ] {Specific gap} → {How to get it / Who to ask}

   ## Suggested Skills to Run Next
   1. **{skill-name}** - {Why, expected output}
      - Parameters: `{param_name}`, `{param_name}`, ...

   ## Panel Composition
   - **Qualification Analyst** - Methodology compliance, disqualification specialist
   - **Competitive Strategist** - Win/loss analyst, positioning expert
   - **Executive Alignment Coach** - Stakeholder dynamics, Economic Buyer engagement
   - **Deal Mechanics Reviewer** - Timeline, legal, procurement specialist
   ```

**Quality checks before writing:**
- ✅ All 8 required sections present
- ✅ Panel Snapshot ≤ 6 bullets
- ✅ D1 actions: 3-5 items with What/Who/Why + attribution
- ✅ D7 actions: 5-7 items with What/Who/Why + attribution
- ✅ Top 3 Risks: Ranked with severity/impact/mitigation + reviewers who flagged
- ✅ Debate Highlights: At least 1 major conflict surfaced + resolution
- ✅ Unresolved Tensions: Documented if exist (don't hide disagreements)
- ✅ Total word count: 400-600 words (CRITICAL)
- ✅ No vague advice ("improve relationships", "follow up")
- ✅ All sources cited in frontmatter
- ✅ Attribution clarity (Panel Consensus vs. specific reviewer)

### Step 8: Emit Structured JSON Summary

**Purpose:** Provide machine-readable summary for API/Next.js app consumption.

**Format:**
- Code fence with label: ` ```json summary `
- Valid JSON only - NO comments, NO trailing commas, NO explanatory text
- This is the THIRD and FINAL section of the three-section envelope
- Place after Chat Output and Artifact Output sections

**CRITICAL Output Order:**
1. `# Chat Output` (Step 6)
2. `# Artifact Output` (Step 7)
3. ` ```json summary` (Step 8 - this step)
4. Nothing else after the closing fence

**JSON Format Requirements:**
- Use ONLY a fenced code block with language identifier: ` ```json summary `
- Valid JSON only - NO comments, NO trailing commas, NO explanatory text
- Nothing else after this block - no explanation, no commentary

**JSON Schema:**
   ```json
   {
     "summaryBullets": ["string"],
     "risks": ["string"],
     "missingInformation": ["string"],
     "d1Actions": [
       {
         "label": "string",
         "owner": "string",
         "deadline": "string",
         "rationale": "string"
       }
     ],
     "d7Actions": [
       {
         "label": "string",
         "owner": "string",
         "deadline": "string",
         "rationale": "string"
       }
     ]
   }
   ```

**Field Extraction Rules:**
- **summaryBullets**: 3-6 key insights from "Panel Snapshot" section (remove emoji/formatting)
- **risks**: Top 3-5 risks from "Panel Consensus (Top 3 Risks)" section (remove emoji/severity markers, include reviewer attribution)
- **missingInformation**: Items from "Missing Information (Panel Gaps)" section (remove checkbox syntax)
- **d1Actions**: All D1 actions with exact label/owner/deadline/rationale (remove checkbox/markdown, include attribution)
- **d7Actions**: All D7 actions with exact label/owner/deadline/rationale (remove checkbox/markdown, include attribution)

**Example Output:**
   ```json summary
   {
     "summaryBullets": [
       "Stage 3 - AT RISK, 45 days in stage",
       "ACV: $500K | Close Date: 2025-12-31 | Probability: 40%",
       "Champion: John Doe (Dir IT) | Economic Buyer: NOT IDENTIFIED",
       "Competition: Competitor X has inside track with CTO",
       "Panel Verdict: AT RISK (3/4 reviewers pessimistic)"
     ],
     "risks": [
       "No Economic Buyer engaged after 45 days - Flagged by: Qualification Analyst, Executive Alignment Coach, Competitive Strategist",
       "Competitor has inside track with CTO - Flagged by: Competitive Strategist",
       "Legal/procurement process unmapped, timeline unrealistic - Flagged by: Deal Mechanics Reviewer"
     ],
     "missingInformation": [
       "CFO budget authority unclear - Request org chart from champion",
       "Decision criteria unknown - Schedule qualification call with Economic Buyer",
       "Legal timeline unmapped - Ask champion for procurement contact"
     ],
     "d1Actions": [
       {
         "label": "Champion must secure CFO intro by EOD tomorrow",
         "owner": "AE",
         "deadline": "EOD Tomorrow",
         "rationale": "No Economic Buyer identified - Panel Consensus (4/4)"
       },
       {
         "label": "Map legal/procurement process with champion",
         "owner": "AE",
         "deadline": "Tomorrow",
         "rationale": "Timeline unrealistic without process visibility - Per Deal Mechanics"
       }
     ],
     "d7Actions": [
       {
         "label": "7-day test: CFO meeting must be scheduled by next Friday or disqualify",
         "owner": "AE + Manager",
         "deadline": "Next Friday",
         "rationale": "45 days with no Economic Buyer = disqualification signal - Panel Consensus (3/4)"
       },
       {
         "label": "Prepare competitive positioning deck for CTO meeting",
         "owner": "AE + SE",
         "deadline": "This Week",
         "rationale": "Competitor displacement threat - Per Competitive Strategist"
       }
     ]
   }
   ```

**Validation Checklist:**
- ✅ Block starts with exactly: ` ```json summary ` (with newline after)
- ✅ Valid JSON - passes JSON.parse()
- ✅ No comments (e.g., `// this is...`)
- ✅ No trailing commas
- ✅ All string values properly escaped
- ✅ All required fields present (summaryBullets, risks, missingInformation, d1Actions, d7Actions)
- ✅ Action objects have all 4 fields (label, owner, deadline, rationale)
- ✅ Block ends with: ` ``` ` (backticks only, no text after)
- ✅ Nothing after the closing backticks - this is the LAST thing in your output

### Step 9: Write Panel Report to File

**Write ONLY Artifact Output content to file.**

1. **Generate filename:**
   - Format: `panel_review_{review_type}_{ISO_DATE}.md`
   - Examples: `panel_review_stage_gate_2025-11-15.md`, `panel_review_weekly_2025-11-15.md`
   - Default review_type: `status` if not specified

2. **Write to:**
   - Path: `sample-data/Runtime/Sessions/{DEAL}/panel_review_{review_type}_{ISO_DATE}.md`
   - Content: ONLY the Artifact Output content (with frontmatter) from Step 7

3. **Update deal.md:**
   - Append to "Generated Artifacts" section:
     ```
     - panel_review_{review_type}_{ISO_DATE}.md (generated on {date})
     ```

## Error Handling

| Error | Severity | Behavior | Fallback | Output Note |
|-------|----------|----------|----------|-------------|
| Deal note missing | CRITICAL | HALT | None - return error with template copy cmd | N/A |
| Methodology not found | WARNING | Proceed | Generic B2B practices | "Methodology {name} not found, using Generic" |
| Stage inventory missing | WARNING | Proceed | Hardcoded generic stages | "Using generic stage model" |
| Reviewer agent fails | WARNING | Proceed with 3 reviewers | Note missing perspective | "Qualification Analyst unavailable (3/4 panel)" |
| All reviewers fail | CRITICAL | HALT | Fall back to single-agent `coach` skill | "Panel unavailable, try /coach" |
| No stakeholders in deal | WARNING | Proceed | Flag as critical risk | "Risk #1: No stakeholders identified" |
| Empty deal directory | WARNING | Proceed | Note in output | "No artifacts found for review" |
| Synthesis timeout | WARNING | Generate partial report | Skip debate, use first-round analyses | "Partial panel report (no debate round)" |

## Advanced Usage

### Custom Reviewer Configuration

To adjust reviewer focus areas:
1. Edit `.claude/skills/deal-review-panel/references/reviewer_personas.md`
2. Modify analysis frameworks or principles for specific reviewers
3. No code changes needed - personas are loaded dynamically

### Panel Verdict Calibration

**Panel Verdict determination:**
- **STRONG:** 0-1 critical risks, all exit criteria met, panel consensus optimistic
- **QUALIFIED:** 2-3 medium risks, most exit criteria met, mixed panel sentiment
- **AT RISK:** 3+ high risks, exit criteria gaps, panel consensus pessimistic
- **DISQUALIFY:** Qualification Analyst + 1 other reviewer recommend disqualification

### Integration with Other Skills

**Typical skill sequence:**
1. **deal-review-panel** (this skill) → Get multi-agent coaching
2. **prep-discovery** → Prepare for Economic Buyer call (if panel flagged EB gap)
3. **sales_communications** → Draft outreach email (per panel recommendation)
4. **sales-presentation** → Create executive briefing (if panel recommends business case)

## Resources

### references/

This skill includes reference files for detailed reviewer definitions and synthesis protocols:

- **reviewer_personas.md** - 4 specialized reviewer definitions (Qualification Analyst, Competitive Strategist, Executive Alignment Coach, Deal Mechanics Reviewer). Each persona includes role, perspective, core principles, analysis framework, output focus, and typical stance.
- **debate_synthesis.md** - Protocol for combining reviewer outputs, resolving conflicts, prioritizing actions, and generating unified coaching reports. Includes conflict resolution heuristics, synthesis patterns, and quality checks.

Load these references:
- Always load reviewer_personas.md in Step 3 (launch reviewers)
- Always load debate_synthesis.md in Step 5 (synthesis)
- Not loaded for other skills (progressive disclosure)

## Example Usage

**User:** "Review the Acme Corp deal - it's been stuck for 45 days and I'm not sure if we should keep pursuing it."

**Skill executes:**
1. Loads Acme Corp deal.md + artifacts
2. Launches 4 reviewers in parallel
3. Collects independent analyses
4. Runs debate round
5. Synthesizes findings:
   - **Qualification Analyst:** Recommends disqualify (no Economic Buyer after 45 days, weak champion)
   - **Executive Alignment Coach:** Counters: Champion securing CFO intro next week, don't bail yet
   - **Competitive Strategist:** Agrees with QA (competitor has inside track, displacement risk high)
   - **Deal Mechanics:** Notes legal process unmapped, timeline unrealistic
6. **Panel Verdict:** AT RISK (3/4 reviewers pessimistic)
7. **Resolution:** 7-day test - if no CFO meeting scheduled by next Friday, disqualify

**Output:** `panel_review_deal_stuck_2025-11-15.md` with specific D1/D7 actions, unresolved tensions documented, and skill recommendations.
