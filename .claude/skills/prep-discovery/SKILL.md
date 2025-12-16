---
license: "MIT - See LICENSE.md"
name: prep-discovery
description: Prepares comprehensive artifacts for discovery calls including internal prep agendas, customer meeting agendas, and confirmation emails. Use when the user is preparing for a discovery conversation, needs to plan pain discovery questions, or wants to align the team before a customer discovery meeting. This skill generates Sandler-aligned discovery materials focused on uncovering emotional pain and qualification criteria.
allowed-tools: [Read, Write, Glob]
---

# Discovery Prep — Runtime Specification

**Version:** 1.1
**Purpose:** Generate comprehensive discovery call prep packages aligned with sales methodology requirements
**Reference:** See `reference.md` for detailed examples, edge cases, and troubleshooting

---

# Discovery Prep Skill

## Purpose

This skill generates a complete discovery call prep package aligned with sales methodology requirements (especially Sandler's Pain stage). It creates internal alignment, customer-facing agendas, and confirmation communications that set the stage for effective qualification conversations.

## When to Use This Skill

**Activate this skill when:**
- User is preparing for an upcoming customer meeting (discovery, workshop, demo, executive meeting)
- User asks to "prep for discovery," "prepare for workshop," "prep next call," or "plan meeting"
- Deal is in any stage and has an upcoming meeting requiring preparation
- User needs to align internal team before customer meeting
- User wants to send meeting confirmation email to prospect
- Preparing questions, objectives, and agenda for upcoming customer interaction

**This skill is now stage-aware:**
- **Early stage (Discovery):** Generates pain discovery questions and qualification materials
- **Later stages (Workshop, Demo, Executive):** Adapts to meeting type and existing deal context
- Analyzes deal history to determine appropriate meeting prep focus

**Do NOT use this skill for:**
- Post-meeting follow-up (use `email-generator` skill instead)
- General internal planning unrelated to customer meetings
- Retrospective analysis (use `coach` skill for deal reviews)

## Core Principles

1. **Sandler Pain Focus:** Discovery is about uncovering emotional pain, not presenting solutions
2. **Up-Front Contracts:** Establish clear expectations before the meeting
3. **Internal Alignment First:** Team must be aligned on objectives, roles, and risks
4. **Question-Led Discovery:** Prepare specific questions, not product pitches
5. **Qualification Mindset:** Goal is to qualify or disqualify, not to "sell"

## Instructions

### Step 1: Read Deal Context

1. **Locate the deal file:**
   ```
   User should provide: sample-data/Runtime/Sessions/{deal_name}/deal.md
   Or ask: "Which deal is this discovery call for?"
   ```

2. **Read deal.md** using Read tool:
   - Current stage and health
   - Known stakeholders
   - Any prior interactions in History timeline
   - Existing artifacts or gaps
   - Risks & Gaps section

3. **Load methodology data:**
   - Follow the protocol in `Framework/System/methodology_loader.md`
   - Read `methodology` field from deal.md frontmatter (default: "Generic")
   - Load the appropriate stage inventory file:
     - Path: `sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md`
     - If missing, fall back to Generic (see methodology_loader.md §5 for fallback rules)
   - Extract from stage inventory:
     - `exit_criteria` for current stage
     - `question_frameworks` for discovery/pain questions
     - `required_artifacts` for follow-up artifacts
     - `risk_indicators` to include in prep

4. **Read relevant knowledge files:**
   - Any company-specific playbooks or guidelines
   - Prior meeting notes if this is follow-up discovery

### Step 1.5: Assess Deal Stage & Meeting Context

**CRITICAL: Determine if this is actually a first discovery call or a later-stage meeting.**

Before generating discovery materials, analyze the deal context to understand what type of meeting prep is needed:

1. **Reconcile stage information:**
   - Check `stage:` field in deal.md frontmatter
   - Check "Current Stage:" or "Stage Progress:" in deal body
   - **Priority:** If body contradicts frontmatter, trust the body (more detailed/recent)
   - Look for stage numbers (1-7) or names (Discovery, Qualify, Workshop, etc.)

2. **Check History for completed discovery:**
   - Scan History section for entries like:
     - "Initial discovery call"
     - "Discovery complete"
     - "Full team demo"
     - "Technical deep-dive"
   - If discovery already happened → this is NOT a first discovery call

3. **Check for upcoming scheduled meetings:**
   - Look for fields: `next_meeting_type`, `next_meeting_date`, "SCHEDULED" markers
   - Look for: "workshop", "on-site", "demo", "executive meeting", "technical review"
   - If specific meeting scheduled → prep for THAT meeting type, not generic discovery

4. **Determine meeting type and objectives:**

   **IF stage = "Discovery" (or Stage 1) AND no prior discovery in History:**
   - ✅ Generate **first discovery call prep** (standard behavior)
   - Focus: Uncovering pain, qualifying opportunity, establishing stakeholders

   **IF stage > Discovery (Stage 2+) OR History shows discovery complete:**
   - ⚠️ This is NOT a first discovery call
   - **Determine actual meeting type:**
     - Workshop scheduled? → Generate workshop prep
     - Demo scheduled? → Generate demo prep
     - Executive meeting? → Generate executive engagement prep
     - Technical deep-dive? → Generate technical validation prep

   **Meeting-specific prep focuses:**
   - **Workshop prep:** Validate solution fit, hands-on evaluation, stakeholder alignment
   - **Demo prep:** Product demonstration, feature validation, use case confirmation
   - **Executive prep:** Business case, ROI validation, decision authority engagement
   - **Technical prep:** Integration requirements, architecture review, security/compliance

5. **Adapt objectives and artifacts accordingly:**
   - **For first discovery:** Standard pain/qualification questions
   - **For later-stage meetings:**
     - Summarize what's ALREADY KNOWN (MEDDPICC gaps closed)
     - Identify REMAINING gaps specific to current stage
     - Generate agenda for the SPECIFIC upcoming meeting type
     - Focus questions on stage-appropriate objectives
     - Reference prior artifacts (discovery notes, demo feedback, etc.)

**Example stage-aware behavior:**

```
FOTE deal context:
- Frontmatter: stage: Discovery
- Body: "Current Stage: 2-Solutioning"
- History: "Oct 17: Initial discovery", "Oct 22: Full demo", "Oct 28: Tech deep-dive"
- Next meeting: "Nov 19: On-site workshop (15-17 attendees)"

→ CONCLUSION: This is Stage 2, discovery complete, workshop prep needed
→ GENERATE: Workshop prep artifacts (not discovery artifacts)
→ FOCUS: Validate solution fit, secure commitment, address competition
→ QUESTIONS: Workshop-specific (not pain discovery)
```

**If ambiguous:**
- Ask user: "I see discovery was completed Oct 17. Is the Nov 19 workshop the meeting you want to prep for?"
- Default to current stage + next scheduled meeting type

### Step 2: Identify Meeting Objectives (Stage-Aware)

**Use the loaded methodology context AND stage assessment from Step 1.5 to determine objectives:**

**For FIRST DISCOVERY calls (Stage 1, no prior discovery):**

1. **From stage inventory `exit_criteria`:**
   - What must be true to advance to next stage?
   - What knowledge gaps exist vs these criteria?
   - What evidence would confirm qualification?

2. **From stage inventory `question_frameworks`:**
   - Use methodology-specific question templates
   - Examples: Sandler Pain Funnel, MEDDPICC qualification questions, SPIN sequences
   - Adapt generic discovery questions if methodology has no specific frameworks

3. **From stage inventory `risk_indicators`:**
   - What red flags should we probe for?
   - What would cause us to disqualify?

4. **Key Questions to Answer:**
   - What are we trying to learn in this discovery call?
   - Who needs to be on the call (our side and their side)?
   - What qualification criteria are we testing?
   - What would cause us to disqualify based on methodology exit criteria?

**For LATER-STAGE meetings (Stage 2+, discovery complete):**

1. **Summarize what's ALREADY KNOWN:**
   - Review History section for completed discovery outcomes
   - Review MEDDPICC Snapshot for gaps already closed
   - List validated pain points, identified stakeholders, known requirements

2. **Identify REMAINING gaps for current stage:**
   - From stage inventory: What exit criteria are NOT yet met?
   - What information is still missing to advance?
   - What decisions need to be made?

3. **Define meeting-specific objectives:**
   - **Workshop:** Solution validation, hands-on evaluation, stakeholder alignment, commitment signals
   - **Demo:** Feature confirmation, use case validation, technical feasibility
   - **Executive:** Business case approval, budget authority, decision timeline, contract discussion
   - **Technical:** Integration requirements, architecture review, security/compliance validation

4. **Adapt questions to meeting type:**
   - NOT pain discovery questions (already done)
   - Focus on stage-appropriate questions:
     - Workshop: "How would this solve [known pain]?" "What concerns do stakeholders have?"
     - Demo: "Which features are most critical?" "What use cases to prioritize?"
     - Executive: "What ROI evidence do you need?" "What's your decision process?"
     - Technical: "What integration points?" "What security requirements?"

5. **Reference prior artifacts and context:**
   - Link to discovery call notes from History
   - Reference prior demo feedback
   - Build on previous conversations, don't start from scratch

**Note:** Methodology-specific objectives (e.g., Sandler pain intensity, MEDDPICC champion identification) come from the loaded stage inventory, not hardcoded here. For later-stage meetings, focus shifts from qualification to advancement.

### Step 3: Generate Internal Prep Agenda

**Goal:** Align internal team before customer meeting.

**Filename Convention:**
```
{YYYY-MM-DD}_stage{N}_agenda__internal_prep.md
Example: 2025-11-15_stage2_agenda__internal_prep.md
```

**Required Sections:**

1. **Meeting Context**
   - Deal name, stage, current health
   - Discovery call date/time
   - Attendees (customer side and our side)

2. **Discovery Objectives (3-5 specific goals)**
   - What we need to learn
   - Qualification criteria to test
   - Exit criteria to satisfy

3. **Roles & Responsibilities**
   - Who leads the meeting?
   - Who takes notes?
   - Who asks technical questions?
   - Who handles objections?

4. **Pain Discovery Question Plan (for Sandler)**
   - 3-5 pain hypotheses to explore
   - Pain Funnel questions prepared for each
   - Emotional language cues to listen for
   - Personal stakes questions

5. **Risks to Mitigate**
   - What could go wrong?
   - How do we handle objections?
   - Disqualification triggers to watch for

6. **Success Criteria**
   - What does a successful discovery look like?
   - What information do we need to advance stage?

7. **Next Steps & Owners**
   - Post-call debrief plan
   - Artifact creation assignments

**Use Template:** `Framework/Templates/agenda_internal.md` as starting point, then expand.

### Step 4: Generate Customer Meeting Agenda

**Goal:** Provide prospect with clear, professional agenda that establishes up-front contract.

**Filename Convention:**
```
{YYYY-MM-DD}_stage{N}_agenda__customer_discovery.md
Example: 2025-11-15_stage2_agenda__customer_discovery.md
```

**Required Sections:**

1. **Meeting Purpose (Up-Front Contract)**
   - Explicit statement of meeting purpose
   - What we hope to accomplish
   - What we need from them

2. **Attendees & Introductions**
   - Who from our team
   - Who we expect from their team
   - Brief intro plan

3. **Agenda Topics (with time allocations)**
   - Current state challenges (15 min)
   - Desired outcomes & success criteria (15 min)
   - Decision process & timeline (10 min)
   - Next steps (5 min)

4. **What We'll Need from You**
   - Be specific about what information you need
   - Set expectation for candid conversation
   - "It's okay to say this isn't a fit"

5. **Expected Outcomes**
   - By end of call, we'll both know...
   - Whether it makes sense to continue exploring
   - What next steps would be (if any)

**Tone:**
- Professional but collaborative
- Not vendor/customer hierarchy (equal business stature)
- Permission to say "no" built in
- No pressure language

**Use Template:** `Framework/Templates/agenda_customer.md` as starting point, then expand.

### Step 5: Generate Confirmation Email

**Goal:** Confirm discovery call, set expectations, share agenda.

**Filename Convention:**
```
{YYYY-MM-DD}_stage{N}_email__confirm_discovery.md
Example: 2025-11-15_stage2_email__confirm_discovery.md
```

**Required Elements:**

1. **Subject Line:**
   - Professional and clear
   - Example: "Discovery Call Confirmation - {Date} at {Time}"

2. **Meeting Logistics:**
   - Date, time, duration
   - Video/phone link
   - Attendees

3. **Purpose Reminder (Up-Front Contract):**
   - Brief reminder of what we'll cover
   - "Our goal is to understand..."
   - "By end of call, we'll both know whether..."

4. **Attached Agenda:**
   - Reference or embed customer agenda
   - "I've attached an agenda to help structure our conversation"

5. **Pre-Work (Optional but Recommended):**
   - "To make best use of our time, it would be helpful if you could..."
   - Example: Think about current challenges, desired outcomes, decision timeline

6. **Contact Info:**
   - "If timing doesn't work, let me know"
   - Phone number for day-of issues

**Tone:**
- Friendly but professional
- Helpful not pushy
- Sets expectations without overwhelming

**Email Block Format:**
```markdown
---
to: prospect@company.com
cc: [optional]
subject: {subject line}
---

```email
{email body in fenced block}
```
```

### Step 6: Add Provenance & Metadata

**To each artifact file, add footer:**

```markdown
---

## Provenance

source_deal: ../../deal.md
generated_by: prep_discovery
generated_at: {YYYY-MM-DD}
methodology: {loaded_methodology_name}
methodology_loader: Framework/System/methodology_loader.md
stage_ref: sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md
```

**Note:** Use the actual methodology name loaded from deal.md frontmatter (e.g., "Sandler", "MEDDPICC", "Generic"). The `stage_ref` path should point to the actual stage inventory file used.

### Step 7: Generate Chat Output

**Purpose:** Provide a concise prep summary for chat/UI display.

**Format:**
- Heading: `# Chat Output`
- Single markdown code fence containing brief prep summary (3-7 bullets)
- NO full agendas, NO detailed questions, NO frontmatter

**Content:**
- Meeting context (type, date, attendees)
- Top 2-3 objectives
- Top 1-2 risks to mitigate
- Top 2-3 prep actions (D1 priorities)

**Example:**
```markdown
# Chat Output

```markdown
**Workshop Prep - Northwind Manufacturing**
- Meeting: Nov 19 on-site workshop, 15-17 attendees including executives
- Objectives: Validate solution fit, demonstrate ROI, secure decision timeline
- Risks: Price sensitivity (InstantGMP competitor), champion departure potential
- D1 Actions:
  - Finalize custom demo on BG01980 batch record (Tom, Nov 18)
  - Brief Brian Curran on executive engagement strategy (Welf, Nov 18)
  - Prepare ROI one-pager with cost savings breakdown (Welf, Nov 18)
```
```

**Rules:**
- Keep under 100 words total
- Focus on actionable prep items, not detailed agendas
- No emoji in Chat Output

### Step 8: Generate Artifact Output (Full Prep Package)

**Purpose:** Create the complete prep package for storage and detailed review.

**Format:**
- Heading: `# Artifact Output`
- Single markdown code fence containing ALL THREE prep documents concatenated

**Content structure:**

1. **Document 1: Internal Prep Agenda**
   - YAML frontmatter
   - Full internal prep agenda (all sections from Step 3)
   - Separator: `---` between documents

2. **Document 2: Customer Meeting Agenda**
   - YAML frontmatter
   - Full customer agenda (all sections from Step 4)
   - Separator: `---` between documents

3. **Document 3: Confirmation Email**
   - YAML frontmatter
   - Full confirmation email (all sections from Step 5)

**Example structure:**
```markdown
# Artifact Output

```markdown
---
generated_by: prep_discovery
generated_on: 2025-11-15T10:00:00Z
deal_id: Northwind Manufacturing
sources: [...]
---

# Internal Prep Agenda - Workshop Nov 19

[Full internal prep content...]

---

---
generated_by: prep_discovery
generated_on: 2025-11-15T10:00:00Z
deal_id: Northwind Manufacturing
sources: [...]
---

# Customer Meeting Agenda - Workshop Nov 19

[Full customer agenda content...]

---

---
generated_by: prep_discovery
generated_on: 2025-11-15T10:00:00Z
deal_id: Northwind Manufacturing
sources: [...]
---

Subject: Looking Forward to Workshop on Tuesday

[Full confirmation email content...]
```
```

**File Output:**
- After generating the full Artifact Output, SPLIT it back into three separate files
- Write each document to its own file (with frontmatter) using Write tool
- Files go to: `sample-data/Runtime/Sessions/{deal_name}/`
  - `{date}_stage{N}_agenda__internal_prep.md`
  - `{date}_stage{N}_agenda__customer_discovery.md`
  - `{date}_stage{N}_email__confirm_discovery.md`

### Step 9: Write Artifacts to Deal Directory

**This step extracts the three documents from Artifact Output and writes them as separate files.**

1. **Determine output path:**
   ```
   sample-data/Runtime/Sessions/{deal_name}/
   ```

2. **Parse Artifact Output into three documents:**
   - Split on `---` separators
   - Extract each document with its frontmatter

3. **Write three files using Write tool:**
   - `{date}_stage{N}_agenda__internal_prep.md` (Document 1 content)
   - `{date}_stage{N}_agenda__customer_discovery.md` (Document 2 content)
   - `{date}_stage{N}_email__confirm_discovery.md` (Document 3 content)

4. **Verify all files created:**
   - Confirm paths
   - Report to user

### Step 10: Update Deal.md

1. **Append entries to "Generated Artifacts" section:**
   ```markdown
   ## Generated Artifacts
   - {YYYY-MM-DD} {date}_stage{N}_agenda__internal_prep.md (Internal discovery prep)
   - {YYYY-MM-DD} {date}_stage{N}_agenda__customer_discovery.md (Customer discovery agenda)
   - {YYYY-MM-DD} {date}_stage{N}_email__confirm_discovery.md (Discovery confirmation email)
   ```

2. **Use Edit tool** to append to deal.md

3. **Update "Artifacts (required per stage)" checklist if needed:**
   - Mark discovery prep artifacts as present [x]

### Step 11: Emit Structured JSON Summary

**Purpose:** Provide machine-readable summary for API/Next.js app consumption.

**Format:**
- Code fence with label: ` ```json summary `
- Valid JSON only - NO comments, NO trailing commas, NO explanatory text
- This is the THIRD and FINAL section of the three-section envelope
- Place after Chat Output (Step 7) and Artifact Output (Step 8) sections

**CRITICAL Output Order:**
1. `# Chat Output` (Step 7)
2. `# Artifact Output` (Step 8)
3. ` ```json summary` (Step 11 - this step)
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
- **summaryBullets**: 3-6 key meeting objectives or prep highlights
- **risks**: Risks or concerns to address during the meeting
- **missingInformation**: Information gaps that need to be filled
- **d1Actions**: Actions to complete before the meeting (prep tasks)
- **d7Actions**: Post-meeting follow-up actions

**Example Output:**
   ```json summary
   {
     "summaryBullets": [
       "Workshop scheduled for Nov 19 with 15-17 stakeholders including executives",
       "Discovery complete - focus on solution validation and commitment",
       "Main objective: Demonstrate ROI and secure decision timeline"
     ],
     "risks": [
       "Price sensitivity - InstantGMP cheaper alternative",
       "Champion (Victoria) potential departure",
       "Complex decision structure with multiple approvers"
     ],
     "missingInformation": [
       "CFO (Ryan) engagement level - needs 1:1 executive connection",
       "Exact decision timeline post-workshop",
       "Legal/procurement process details"
     ],
     "d1Actions": [
       {
         "label": "Finalize custom demo built on BG01980 batch record",
         "owner": "Tom Campbell",
         "deadline": "Nov 18 EOD",
         "rationale": "Workshop demo must reflect their actual process"
       },
       {
         "label": "Brief Brian Curran on executive engagement strategy",
         "owner": "Welf Ludwig",
         "deadline": "Nov 18",
         "rationale": "SVP needs context for peer-to-peer with Ray/Ryan/Tom"
       }
     ],
     "d7Actions": [
       {
         "label": "Same-day debrief with Victoria and John D'Andrea",
         "owner": "Welf Ludwig",
         "deadline": "Nov 19 post-workshop",
         "rationale": "Capture feedback while fresh, gauge decision readiness"
       },
       {
         "label": "Send executive summary with ROI one-pager",
         "owner": "Welf Ludwig",
         "deadline": "Nov 20",
         "rationale": "Provide materials for internal advocacy"
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
- ✅ All required fields present
- ✅ Action objects have all 4 fields (label, owner, deadline, rationale)
- ✅ Block ends with: ` ``` ` (backticks only, no text after)
- ✅ Nothing after the closing backticks - this is the LAST thing in your output

---

## See Also

**For detailed examples and troubleshooting:**
- See `reference.md` (full walkthroughs, edge cases, best practices)

**Methodology Loading:**
- `Framework/System/methodology_loader.md` - Protocol for loading and using sales methodologies

**Templates and Stage Data:**
- `templates/` - Discovery question banks and agenda templates
- Stage inventories: `sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md`
