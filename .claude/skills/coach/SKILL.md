---
name: coach
description: Comprehensive AI sales coaching for individual deals. Analyzes deal health against methodology-specific stage criteria, identifies risks and gaps, recommends concrete D1/D7 actions, and suggests which skills to run next. Use for pre-call prep (discovery, demo, negotiation), weekly deal reviews, stage transitions, or when deal feels stuck or at risk.
allowed-tools: [Read, Write, Glob, Grep]
license: "MIT - See LICENSE.md"
metadata:
  version: "1.0"
---

# Coach

## Overview

Provides AI-powered sales coaching for individual deals by analyzing deal health, identifying risks, and recommending specific next actions. Adapts to methodology frameworks (Sandler, MEDDPICC, Generic) and generates concise, actionable coaching reports in 400-600 words.

## Core Principles

1. **Brevity First** - Entire coaching report MUST fit on one screen (400-600 words max)
2. **Methodology-Aware** - Loads methodology from deal frontmatter and applies framework-specific criteria
3. **Actionable** - Every recommendation includes What/Who/Why, no vague advice
4. **Evidence-Based** - Cite specific files and deal state, no generic templates
5. **Skill Orchestration** - Recommend which skills to execute with parameters
6. **Portable** - No hardcoded company logic, works with any deal structure

## When to Use This Skill

**Activate when:**
- Before any sales call (discovery, demo, negotiation, executive meeting)
- Weekly deal reviews or stage transitions
- Deal at risk or timeline slipping
- After significant customer interaction
- User asks: "Coach me on [deal]", "Is this deal on track?", "Prep me for [call type]"

**Do NOT use for:**
- Portfolio-level analysis across multiple deals (use `portfolio` skill instead)
- Generating specific artifacts like emails or agendas (use `sales-communications` or `prep-discovery`)
- Document conversion (use `convert-and-file` skill)
- Simple file reads (use Read tool directly)

## Workflow

### Step 1: Load Deal Context

1. **Locate deal note:**
   - Required path: `sample-data/Runtime/Sessions/{DEAL}/deal.md`
   - If not found → ERROR with template copy command

2. **Parse deal.md:**
   - **Frontmatter:** Extract `methodology`, `stage`, `generated_by`
   - **Body:** Parse stakeholders, timeline, history, existing artifacts, known risks

3. **Scan deal directory:**
   - Use Glob: `sample-data/Runtime/Sessions/{DEAL}/**/*.md`
   - Note discovery notes, agendas, emails, prior coaching reports

4. **Build deal_state object:**
   - Current stage and health status
   - Stakeholder map (Economic Buyer, Champion, Technical, Legal/Procurement)
   - Timeline and next milestone
   - Interaction history (last 3-5 touchpoints)
   - Existing artifacts generated
   - Known risks and gaps

**Error handling:**
- Deal note missing → `ERROR: Deal note not found at {path}. Create with: cp sample-data/Runtime/Sessions/_TEMPLATES/deal_template.md sample-data/Runtime/Sessions/{DEAL}/deal.md`
- Malformed frontmatter → Warn, attempt body parse
- Missing stage → Assume Stage 1 (Discover), flag as gap

### Step 2: Load Methodology Context

**Follow `Framework/System/methodology_loader.md` protocol:**

1. **Detect methodology:**
   - Check deal.md frontmatter for `methodology: {name}` (e.g., `MEDDPICC`, `Sandler`, `Generic`)
   - Default: `Generic` if not specified

2. **Load stage inventory (primary source):**
   - Path: `sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md`
   - Extract for current stage:
     - `exit_criteria` - What must be true to advance
     - `required_artifacts` - Documents/outputs needed
     - `risk_indicators` - Red flags to watch for
     - `question_frameworks` - Discovery/qualification questions

3. **Optional background (read-only):**
   - Path: `Framework/Methodologies/{Methodology}.md`
   - Provides philosophy, principles, and context (don't modify)

4. **Fallback if missing:**
   - Use Generic methodology from `sample-data/Runtime/_Shared/knowledge/methodologies/Generic/stage_inventory__Generic.md`
   - If still missing → Use hardcoded generic B2B stages: Discover → Qualify → Propose → Select → Negotiate → Close → Won
   - Note in output: "Using generic B2B model (no custom methodology found)"

5. **Load relevant knowledge base files:**
   - Personas matching deal's industry/roles: `persona_*.md`
   - Battlecards for competitors mentioned: `battlecard_{competitor}.md`
   - Stage guides for current stage: `stage_guide_*.md`
   - Do NOT load entire knowledge base - be selective

### Step 3: Analyze Deal State

1. **Map current stage to methodology:**
   - Translate stage number/name to methodology-specific stage
   - Example: Stage 2 → "Qualify" (Generic) or "Pain/Budget Discovery" (Sandler)

2. **Assess stakeholder coverage:**
   - **Critical:** Economic Buyer identified and engaged?
   - **Critical:** Champion present and strong?
   - **Important:** Technical evaluator involved?
   - **Important:** Legal/Procurement engaged if needed?
   - Flag gaps by severity

3. **Evaluate timeline and urgency:**
   - Next milestone defined and realistic?
   - Compelling event driving decision?
   - Days in stage vs. typical duration
   - Close date pressure

4. **Review interaction history:**
   - Last touchpoint date (fresh vs. stale)
   - Frequency of engagement
   - Types of interactions (discovery, demo, follow-up)
   - Forward momentum indicators

5. **Compare current state vs. exit criteria:**
   - For each criterion → ✅ Met | ⚠️ Partial | ❌ Not Met | ❓ Unknown
   - Identify blocking gaps

6. **Detect risk indicators:**
   - Load from stage inventory or methodology adapter
   - Examples: Champion departure risk, budget authority unclear, competition active, timeline compressed
   - Rank by severity: 🔴 Critical | 🟡 High | 🟠 Medium | 🟢 Low

7. **Assess deal velocity:**
   - Days in stage vs. expected duration
   - Status: 🟢 On track | 🟡 Slow | 🔴 Stalled

### Step 3.5: Identify Relevant Plays

**Plays are reusable sales tactics (reference, executive engagement, champion building, etc.) stored in `Framework/Plays/`**

1. **Discover available plays:**
   - Use Glob: `Framework/Plays/*.md`
   - Expected plays: reference, executive_engagement, champion_building, multi_threading, poc, mutual_action_plan, contract_negotiation, value_realization, deal_rescue, committee_selling, budget_creation, security_compliance

2. **Match deal state to play triggers:**
   - Read each play's `<triggers>` section
   - Match triggers against deal state from Step 3:
     - **no_economic_buyer** → executive_engagement play
     - **no_champion** or **weak_champion** → champion_building play
     - **single_contact** → multi_threading play
     - **customer_validation_request** → reference play
     - **technical_validation_needed** → poc play
     - **complex_buying_process** → mutual_action_plan play
     - **contract_redlines** or **legal_review** → contract_negotiation play
     - **pricing_objection** or **cfo_approval_needed** → value_realization play
     - **no_activity_30_days** or **ghosting** → deal_rescue play
     - **committee_decision** → committee_selling play
     - **no_budget** → budget_creation play
     - **security_questionnaire** or **infosec_review** → security_compliance play

3. **Load matched plays** (limit to 2-3 most relevant):
   - Read full play content for matched plays
   - Extract:
     - `<principles>` - Core tenets of the play
     - `<steps>` - Tactical execution steps
     - `<examples>` - Real-world scenarios (for pattern matching to deal)
     - `<pitfalls>` - Common mistakes to avoid

4. **Synthesize play-specific recommendations:**
   - Map play steps to D1/D7 actions (see Step 4)
   - Cite play name in action rationale: "Per executive_engagement play: Get warm intro from champion to CFO"
   - Include 1-2 play principles in coaching narrative (brevity constraint: don't copy entire play)
   - Reference play in "See Also" section of coaching report

5. **Play selection guidelines:**
   - **High priority plays** (match these first):
     - executive_engagement (if no Economic Buyer)
     - champion_building (if weak/no champion)
     - deal_rescue (if stalled >30 days)
     - value_realization (if pricing objection or CFO approval needed)
   - **Situational plays** (load if specific trigger matches):
     - reference (if validation request)
     - poc (if pilot needed)
     - mutual_action_plan (if complex buying process)
     - contract_negotiation (if legal review in progress)
     - committee_selling (if committee decision)
     - budget_creation (if no budget)
     - security_compliance (if security review)
   - **Always consider**: multi_threading (most deals benefit from stakeholder expansion)

6. **Fallback:**
   - If no plays match triggers → Proceed with standard methodology-based coaching (no play synthesis)
   - If Framework/Plays/ empty → Note in output "No plays available" and proceed with methodology only

**Example play synthesis:**

Deal state triggers: `no_economic_buyer`, `weak_champion`, `30_days_in_stage`

Matched plays:
1. executive_engagement (no Economic Buyer)
2. champion_building (weak champion)
3. deal_rescue (not quite 30 days, but velocity slow)

Synthesized D1 actions (from plays):
- [ ] **EOD Today** - Ask champion (Dir IT) for warm intro to CFO (Economic Buyer) for 15-min business review (Per executive_engagement play)
  - Why: No Economic Buyer identified yet (Stage 3 risk)
- [ ] **Tomorrow** - Test champion strength: Request champion to share last quarter's budget data (Per champion_building play)
  - Why: Champion seems lukewarm (hasn't driven internal meetings)

Coaching narrative excerpt:
"This deal lacks Economic Buyer engagement (CFO not identified). Per executive_engagement play, request warm intro from champion rather than cold outreach. Prepare 3-slide exec briefing (problem/solution/proof) for 15-min CFO meeting."

### Step 4: Generate Recommendations

1. **Prioritize gaps into action buckets:**
   - **D1 (next 24 hours):** Critical blockers requiring immediate action (3-5 max)
   - **D7 (next 7 days):** Important but not urgent, stage advancement work (5-7 max)
   - **Backlog:** Optimization opportunities (mention briefly)

2. **Create D1 actions:**
   - Format: `[Action] with [Who] to [Outcome]`
   - Must include: Specific task, Owner, Deadline, Why it matters
   - ✅ Good: "Schedule 1:1 with CFO (Jane Smith) by EOD tomorrow to validate budget authority and decision process"
   - ❌ Bad: "Follow up with stakeholders", "Improve relationships"

3. **Create D7 actions:**
   - Artifact creation, stakeholder mapping, research tasks
   - Same specificity as D1: What/Who/When/Why

4. **Apply methodology-specific principles:**
   - **Sandler:** No free consulting, qualify pain/budget/decision before presenting, disqualification = success
   - **MEDDPICC:** Checklist-driven (M-E-D-D-P-I-C), metrics focus, Economic Buyer critical, paper process visibility
   - **Generic:** Standard B2B qualification (stakeholders, pain, budget, decision, timeline)

5. **Map actions to skills:**
   - Identify which skills help execute recommendations
   - Specify parameters: `deal_path`, `call_type`, `focus_areas`, `recipient`
   - Prioritize 2-4 skills max with rationale

**Common skill recommendations:**
- `prep-discovery` - Discovery call upcoming, pain/budget gaps exist
- `sales_communications` - Outreach email needed (Economic Buyer, follow-up, check-in)
- `next-steps` - User needs quick tactical actions without full coaching
- `convert_and_file` - Need to import methodology docs, playbooks, or competitive intel

### Step 5: Generate Chat Output

**Purpose:** Provide a concise coaching summary for chat/UI display (3-7 bullets).

**Format:**
- Heading: `# Chat Output`
- Single markdown code fence containing 3-7 bullet points
- NO full report, NO detailed sections, NO frontmatter

**Content:**
- Quick deal snapshot (stage, health, key players)
- Top 1-2 risks
- Top 2-3 recommended actions (D1 priorities)

**Example:**
```markdown
# Chat Output

```markdown
**Deal Snapshot:**
- Stage 2 (Qualify) - Moderate health, 30 days in stage
- Champion: John Doe (Dir IT) | Economic Buyer: NOT IDENTIFIED
- ACV: $250K | Close: Dec 15 | Probability: 60%

**Top Risks:**
- No Economic Buyer engaged (CFO not identified)
- Single-threaded with one contact

**D1 Actions:**
- Request warm intro to CFO from John (EOD today)
- Send competitive battlecard before competitor meeting (tomorrow)
- Schedule multi-threading session with Ops/Security (this week)
```
```

**Rules:**
- Keep under 100 words total
- Focus on actionable insights, not analysis
- No emoji in Chat Output (use in Artifact Output only)

### Step 6: Generate Artifact Output (Full Coaching Report)

**Purpose:** Create the complete coaching report for storage and detailed review.

**Format:**
- Heading: `# Artifact Output`
- Single markdown code fence containing the full report

**Content structure:**

1. **YAML frontmatter:**
   ```yaml
   ---
   generated_by: coach
   generated_on: {ISO_TIMESTAMP}  # YYYY-MM-DDTHH:MM:SSZ
   deal_id: {DEAL_NAME}
   call_type: {discovery|demo|negotiation|status}
   methodology: {METHODOLOGY}
   stage: {STAGE_NUMBER}
   sources:
     - sample-data/Runtime/Sessions/{DEAL}/deal.md
     - [other files consulted]
     - [Framework/Plays/*.md if plays used]
   ---
   ```

2. **Body (400-600 words total, CRITICAL constraint):**

   ```markdown
   # Deal Coaching Report - {Company Name}

   **Generated:** {DATE} | **Stage:** {STAGE} | **Methodology:** {METHODOLOGY} | **Health:** {STATUS}

   ## Deal Snapshot (5-6 bullets)
   - Stage {X} - {one_line_health_summary}
   - ACV: ${amount} | Close Date: {date} | Probability: {X}%
   - Last Activity: {date} ({days_ago} days ago) - {activity_type}
   - Champion: {Name/Title} | Economic Buyer: {Name/Title or "NOT IDENTIFIED"}
   - Competition: {Primary competitor or "None known"}
   - Timeline: {next_milestone} by {date}

   ## Stage Health (2-3 bullets)
   - Exit Criteria: {X/Y} met - {brief_gap_summary}
   - Required Artifacts: {X/Y} completed - Missing: {list}
   - Readiness: {Ready to Advance | Gaps Exist | Blocked}

   ## Top 3 Risks (3 bullets, one line each)
   1. 🔴 **{Risk Name}** - {brief impact} → {mitigation}
   2. 🟡 **{Risk Name}** - {brief impact} → {mitigation}
   3. 🟠 **{Risk Name}** - {brief impact} → {mitigation}

   ## Recommended Actions

   ### D1 (Next 24 Hours)
   - [ ] **{Deadline}** - {Specific action with Who} (Owner: {Name})
     - Why: {One-line rationale tied to exit criteria or risk}

   ### D7 (This Week)
   - [ ] **{Deadline}** - {Specific action with Who} (Owner: {Name})
     - Why: {One-line rationale}

   ## Missing Information (3-5 bullets)
   - [ ] {Specific gap} → {How to get it / Who to ask}

   ## Suggested Skills to Run Next (1-3 bullets)
   1. **{skill-name}** - {Why run this skill, expected output}
      - Parameters: `deal_path`, `call_type: {type}`, `focus_areas: [{areas}]`

   ## See Also
   - {Link to relevant deal artifacts}
   - {Link to stage inventory or methodology reference}
   - {Link to relevant plays (e.g., Framework/Plays/executive_engagement.md)}
   ```

**File Output:**
- Write ONLY the Artifact Output content (with frontmatter) to:
  - Path: `sample-data/Runtime/Sessions/{DEAL}/coaching_report_{call_type}_{ISO_DATE}.md`
- Update deal.md "Generated Artifacts" section:
  ```
  - coaching_report_{call_type}_{ISO_DATE}.md (generated on {date})
  ```

**Quality checks before writing:**
- ✅ All 6 required sections present
- ✅ Executive summary ≤ 6 bullets
- ✅ D1 actions: 3-5 items with What/Who/Why
- ✅ D7 actions: 5-7 items with What/Who/Why
- ✅ Risks: 3-5 ranked with severity/impact/mitigation
- ✅ Skills: 1-3 recommended with parameters
- ✅ Total word count: 400-600 words (CRITICAL)
- ✅ No vague advice ("improve relationships", "follow up")
- ✅ Methodology principles applied
- ✅ All sources cited in frontmatter

### Step 7: Emit Structured JSON Summary

**Purpose:** Provide machine-readable summary for API/Next.js app consumption.

**Format:**
- Code fence with label: ` ```json summary `
- Valid JSON only - NO comments, NO trailing commas, NO explanatory text
- This is the THIRD and FINAL section of the three-section envelope
- Place after Chat Output and Artifact Output sections

**CRITICAL Output Order:**
1. `# Chat Output` (Step 5)
2. `# Artifact Output` (Step 6)
3. ` ```json summary` (Step 7 - this step)
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
- **summaryBullets**: 3-6 key insights from "Deal Snapshot" section (remove emoji/formatting)
- **risks**: Top 3-5 risks from "Top 3 Risks" section (remove emoji/severity markers)
- **missingInformation**: Items from "Missing Information" section (remove checkbox syntax)
- **d1Actions**: All D1 actions with exact label/owner/deadline/rationale (remove checkbox/markdown)
- **d7Actions**: All D7 actions with exact label/owner/deadline/rationale (remove checkbox/markdown)

**Example Output:**
   ```json summary
   {
     "summaryBullets": [
       "Stage 2 - Qualified, moderate health, 30 days in stage",
       "ACV: $250K | Close Date: 2025-12-15 | Probability: 60%",
       "Champion: John Doe (Dir IT) | Economic Buyer: NOT IDENTIFIED",
       "Competition: Competitor X actively engaged",
       "Timeline: Technical evaluation by 2025-11-30"
     ],
     "risks": [
       "No Economic Buyer identified - CFO not engaged yet",
       "Single-threaded - only one contact (John Doe)",
       "Competition actively presenting to CTO"
     ],
     "missingInformation": [
       "Budget authority unclear - ask John who controls IT budget",
       "Decision process unknown - request RACI chart",
       "Technical requirements incomplete - schedule deep-dive with Ops team"
     ],
     "d1Actions": [
       {
         "label": "Request warm intro to CFO from John Doe by EOD today",
         "owner": "AE",
         "deadline": "EOD Today",
         "rationale": "No Economic Buyer identified - critical Stage 2 gap"
       },
       {
         "label": "Send competitive battlecard prep to John before competitor meeting",
         "owner": "AE",
         "deadline": "Tomorrow 9am",
         "rationale": "Competitor X presenting to CTO - need to arm champion"
       }
     ],
     "d7Actions": [
       {
         "label": "Schedule multi-threading session with Ops team and Security",
         "owner": "AE + SE",
         "deadline": "This Friday",
         "rationale": "Single-threaded risk - expand stakeholder map"
       },
       {
         "label": "Create executive briefing deck for CFO intro meeting",
         "owner": "AE",
         "deadline": "Wed EOD",
         "rationale": "Prepare for Economic Buyer engagement"
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

## Error Handling

| Error | Severity | Behavior | Fallback | Output Note |
|-------|----------|----------|----------|-------------|
| Deal note missing | CRITICAL | HALT | None - return error with template copy cmd | N/A |
| Methodology not found | WARNING | Proceed | Generic B2B practices | "Methodology {name} not found, using Generic" |
| Stage inventory missing | WARNING | Proceed | Hardcoded generic 7-stage model | "Using generic stage model" |
| No stakeholders in deal | WARNING | Proceed | Flag as critical risk | "Risk #1: No stakeholders identified" |
| Empty knowledge base | WARNING | Proceed | Generic B2B | "Limited context - no knowledge base" |
| Malformed deal note | WARNING | Partial parse | Extract readable sections, defaults | "Data quality issues detected" |
| Deal artifacts missing | INFO | Proceed | Note in output | "No prior artifacts found" |
| Unclear stage number | WARNING | Assume Stage 1 | Use Discover criteria | "Stage unclear, assumed Stage 1" |

## Resources

### references/

This skill includes reference files for detailed examples and methodology-specific guidance:

- **risk_indicators.md** - Champion departure risk patterns, Economic Buyer disengagement signals, competition displacement indicators, timeline compression risks, budget authority warning signs
- **coaching_examples.md** - Example coaching sessions for different stages and methodologies (MEDDPICC, Sandler, Generic B2B)
- **methodology_guidance.md** - Deep-dive on how to coach MEDDPICC, Sandler, and Generic deals, when to recommend methodology adoption

Load these references when:
- User asks for detailed examples
- Need deep methodology guidance
- Otherwise, keep out of context (progressive disclosure)
