---
license: "MIT - See LICENSE.md"
name: prep-demo
description: Prepares comprehensive artifacts for product demonstration calls including demo scripts, technical setup checklists, and customer demo agendas. Use when the user is preparing for a demo conversation, needs to plan feature validation, or wants to align the team before a customer demo. This skill generates methodology-aligned demo materials focused on validating solution fit and demonstrating value.
allowed-tools: [Read, Write, Glob, Grep, Bash]
---

# Purpose

Generate demo preparation artifacts that validate solution fit, demonstrate value, and advance deals through the sales cycle. This skill produces internal demo scripts with feature prioritization, technical setup checklists, and customer-facing demo agendas grounded in prior discovery work and deal context.

Unlike discovery (which qualifies opportunities by uncovering pain), demo prepares the team to validate the solution addresses known pain points and secures commitment to next steps.

# When to Use This Skill

Trigger this skill when:
- User says "prepare for demo", "demo prep", "getting ready to present", "product demonstration"
- Discovery phase is complete and moving to solution validation (typically Stage 2-3)
- Need to plan which features/use cases to demonstrate
- Technical team needs environment setup checklist
- Customer expects product walkthrough or proof-of-concept

**NOT for:**
- Initial discovery calls (use prep-discovery skill)
- Executive briefings without product focus (use sales-presentation skill)
- Deals where discovery gaps remain (run coach skill first)

# Core Principles

1. **Discovery-Informed** - Reference prior discovery notes to ground demo in known pain points and stakeholder priorities
2. **Stage-Aware** - Validate discovery is complete before generating demo prep; flag gaps if not ready
3. **Value-Led** - Lead with business outcomes and pain relief, not feature tours
4. **Interactive Focus** - Design for validation and confirmation, not one-way presentation
5. **Technical Readiness** - Ensure environment, data, and access are pre-validated before customer interaction
6. **Commitment-Oriented** - Every demo ends with clear next-step agreement
7. **Methodology-Aligned** - Load stage-specific validation questions and exit criteria from methodology inventory

# Instructions

Follow these steps to generate demo preparation artifacts:

## Step 1: Read Deal Context

Read the deal file at `sample-data/Runtime/Sessions/{DEAL_NAME}/deal.md`.

Extract:
- **Current stage** (from frontmatter and Stage section)
- **Stakeholders** (Economic Buyer, Champion, Technical contacts with roles)
- **History** (last 3-5 interactions, especially discovery call notes)
- **Known pain points** (from Pain section and prior artifacts)
- **Technical requirements** (integration points, security requirements, user volumes)
- **D1/D7 tasks** (what's been committed)
- **Existing artifacts** (reference any prior agendas, call summaries)

If deal.md does not exist or is incomplete, emit error message:
```
ERROR: Cannot prepare demo without deal context.
Run `deal-intake` skill first to create deal.md.
```

## Step 1.5: Validate Discovery Complete (Stage-Aware Logic)

**CRITICAL: Assess whether discovery is complete before proceeding with demo prep.**

Check for evidence of completed discovery:
- **History section** contains discovery call notes or pain qualification interactions
- **Pain section** has specific, quantified pain points (not generic placeholders)
- **Budget section** shows qualification status (allocated, authorized, or clear timeline)
- **Decision section** identifies decision makers and process
- **Stage** is 2 or higher (not stuck in Stage 1)

**If discovery appears incomplete:**
- Surface gaps explicitly in Chat Output (e.g., "Missing: quantified pain impact, budget authority")
- Recommend running `coach` skill to assess deal health
- Ask user: "Should I proceed with demo prep despite these gaps, or run discovery prep first?"

**If user confirms to proceed despite gaps:**
- Flag missing context in generated artifacts with `[DISCOVERY GAP: ...]` markers
- Recommend discovery validation questions to include in demo call

## Step 2: Load Methodology Context

Follow `Framework/System/methodology_loader.md` protocol:

1. Read `methodology` field from deal.md frontmatter (default to "Generic" if absent)
2. Load stage inventory file:
   ```
   sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md
   ```
3. Extract for **current stage** (or Stage 2 if unclear):
   - `exit_criteria` - What must be validated in demo to advance
   - `required_artifacts` - Documents needed (demo script, technical validation)
   - `risk_indicators` - Red flags during demo (lack of engagement, missing stakeholders)
   - `question_frameworks` - Validation questions for demo phase

4. Optional: Read `Framework/Methodologies/{Methodology}.md` for background on demo phase philosophy

5. Fallback: If methodology files missing, use Generic best practices (solution validation, feature confirmation, next-step commitment)

## Step 3: Analyze Prior Discovery Notes

Search deal History for discovery-related artifacts:
- Call summaries with pain discovery
- Internal prep agendas listing pain hypotheses
- Email confirmations mentioning priorities

Extract:
- **Confirmed pain points** (emotional + quantified impact)
- **Stakeholder priorities** (what each role cares about most)
- **Use cases mentioned** (workflows, processes, scenarios)
- **Open questions** (anything unresolved from discovery)

If no discovery notes found, document this gap and recommend validation questions to recover.

## Step 4: Identify Demo Focus Areas

Based on pain points, stakeholder priorities, and methodology exit criteria, determine:

1. **Primary use cases** (3-5 max) - Which workflows/scenarios to demonstrate
2. **Feature priority** (must-show vs. nice-to-have) - Map features to pain relief
3. **Stakeholder customization** - What matters to each attendee role
4. **Technical validation points** - Integration, security, scalability topics to address
5. **Success criteria** - What "good" looks like for this specific demo

Prioritize ruthlessly: Show less, demonstrate value more deeply.

## Step 5: Design Demo Flow

Create a logical demo script structure:

1. **Opening** (5 min) - Recap pain points, set demo objectives, confirm attendees
2. **Use Case 1** (10-15 min) - Lead with highest-value pain relief, show don't tell
3. **Use Case 2** (10-15 min) - Address second priority, interactive validation
4. **Use Case 3** (optional, 10 min) - Third priority if time allows
5. **Technical Deep-Dive** (10 min) - Integration points, security, architecture as needed
6. **Q&A** (10 min) - Address concerns, validate fit
7. **Next Steps** (5 min) - Secure commitment (POC, trial, proposal, next meeting)

Total: 60-75 minutes typical

**Demo Design Principles:**
- Lead with value and pain relief, not features
- Interactive validation ("How would this solve your X problem?")
- Show real workflows, not disconnected features
- Leave time for questions and exploration
- End with clear next-step agreement

## Step 6: Create Technical Setup Checklist

List pre-demo technical requirements:

1. **Environment setup** - Demo instance, data loaded, configurations set
2. **Access provisioning** - User accounts, permissions, SSO if needed
3. **Integration prep** - API endpoints, test connections, sample data flows
4. **Backup plan** - Screenshots, video walkthrough if live demo fails
5. **Screen sharing logistics** - Platform (Zoom, Teams), screenshare permissions, dual monitors
6. **Performance validation** - Load times acceptable, no test data visible, branding correct

Assign owners and deadlines (typically D1 tasks for SE/technical team).

## Step 7: Generate Customer Demo Agenda

Create external-facing agenda for customer attendees:

**Format:**
```
Subject: [Company Name] Product Demo - [Date]

Agenda:
- Recap: Your priorities and pain points [5 min]
- Demo: [Use Case 1 description] [15 min]
- Demo: [Use Case 2 description] [15 min]
- Technical Q&A: Integration, security, implementation [10 min]
- Next Steps: [POC/Trial/Proposal] timeline [5 min]

Please confirm attendees and any specific topics to prioritize.
```

**Tone:** Collaborative, value-focused, not product-centric

## Step 8: Generate Internal Demo Script

Create detailed internal run sheet for demo team:

**Include:**
- Minute-by-minute flow with presenter assignments
- Feature callouts mapped to pain points
- Validation questions to ask during demo
- Technical FAQs with prepared answers
- Transition language between sections
- Next-step close script

**Format:** Bulleted, scannable, ready to present from

**Length:** 600-800 words (2-3 pages)

## Step 9: Identify Validation Questions

Based on methodology question_frameworks, generate 5-10 validation questions to ask during demo:

**Categories:**
- **Use case confirmation**: "Is this how you'd use it for [workflow]?"
- **Feature validation**: "Does this address your concern about [pain point]?"
- **Stakeholder alignment**: "What do you think, [name]?" (engage silent attendees)
- **Objection surfacing**: "What concerns do you have about [topic]?"
- **Next-step readiness**: "If this solves [pain], what would be the next step?"

These keep demo interactive and validate fit in real-time.

## Step 10: Generate Artifacts with Frontmatter

Create three artifacts with proper YAML frontmatter:

### Artifact 1: Demo Script (Internal)
```yaml
---
generated_by: prep-demo
generated_on: {ISO_TIMESTAMP}
deal_id: {Company Name}
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - {prior_discovery_artifacts}
  - sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md
artifact_type: demo_script
---
```

### Artifact 2: Technical Setup Checklist
```yaml
---
generated_by: prep-demo
generated_on: {ISO_TIMESTAMP}
deal_id: {Company Name}
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
artifact_type: technical_checklist
---
```

### Artifact 3: Customer Demo Agenda
```yaml
---
generated_by: prep-demo
generated_on: {ISO_TIMESTAMP}
deal_id: {Company Name}
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
artifact_type: demo_agenda
---
```

## Step 11: Write Artifacts to Deal Directory

Use Write tool to save files to:
```
sample-data/Runtime/Sessions/{DEAL_NAME}/{YYYY-MM-DD}_stage{N}_demo__{type}.md
```

**Naming examples:**
- `2025-11-17_stage2_demo__script.md` (internal demo script)
- `2025-11-17_stage2_demo__technical_checklist.md`
- `2025-11-17_stage2_demo__customer_agenda.md`

## Step 12: Update deal.md

Append to **Generated Artifacts** section in deal.md:
```
- 2025-11-17: Demo preparation artifacts (script, technical checklist, customer agenda)
```

Do NOT modify other sections of deal.md.

## Step 13: Emit Three-Section Output

Generate output in standardized envelope format:

### Section 1: Chat Output
```markdown
# Chat Output

```markdown
- Demo script created: 3 use cases prioritized by pain relief
- Technical checklist: 6 setup items assigned to [SE name]
- Customer agenda ready to send
- Validation questions embedded for interactive demo
- [Any critical gaps or recommendations]
```
```

**Constraints:**
- Under 100 words
- Concise, scannable bullets
- Ready-to-use deliverable summary only
- NO analysis, NO methodology jargon

### Section 2: Artifact Output
```markdown
# Artifact Output

```markdown
{Full content of all three artifacts with frontmatter, concatenated with --- separators}
```
```

### Section 3: JSON Summary
```json summary
{
  "summaryBullets": [
    "Demo script generated with 3 use cases mapped to pain points",
    "Technical setup checklist with 6 pre-demo tasks",
    "Customer agenda ready for confirmation email"
  ],
  "risks": [
    "Missing discovery validation on budget authority",
    "Technical Buyer not confirmed as attendee"
  ],
  "missingInformation": [
    "Specific integration requirements for CRM system",
    "Decision timeline for POC approval"
  ],
  "d1Actions": [
    {
      "label": "Validate demo environment with sample data loaded",
      "owner": "SE",
      "deadline": "Day before demo",
      "rationale": "Ensure no technical failures during customer demo"
    }
  ],
  "d7Actions": [
    {
      "label": "Send customer demo agenda for confirmation",
      "owner": "AE",
      "deadline": "3 days before demo",
      "rationale": "Allow time for attendee changes and topic additions"
    }
  ]
}
```

**CRITICAL:** Nothing after the closing JSON fence.

## Step 14: Recommend Next Skills

Based on demo prep, suggest related skills:

- **sales_communications** - If customer demo agenda needs to be sent as email
- **coach** - If discovery gaps detected, run deal health assessment first
- **roi-model** - If demo will include financial justification, prepare ROI model
- **sales-presentation** - If executive attendees need business case slides

## Step 15: Error Handling

If errors occur, emit specific messages:

**Missing deal.md:**
```
ERROR: Deal file not found at sample-data/Runtime/Sessions/{DEAL}/deal.md
ACTION: Run deal-intake skill to create deal context first
```

**Discovery incomplete:**
```
WARNING: Discovery appears incomplete (missing pain quantification, budget status, or decision process)
RECOMMENDATION: Run coach skill to assess deal health, or run prep-discovery to complete qualification
QUESTION: Proceed with demo prep despite gaps?
```

**No stakeholders identified:**
```
ERROR: Cannot prepare demo without stakeholder information
ACTION: Update deal.md Stakeholders section with Economic Buyer, Champion, and Technical contacts
```

**Missing methodology stage inventory:**
```
WARNING: Methodology stage inventory not found at sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/
FALLBACK: Using Generic demo best practices (solution validation, feature confirmation, next-step commitment)
```

# Quick Reference

**File Locations:**
- Deal context: `sample-data/Runtime/Sessions/{DEAL}/deal.md`
- Stage inventory: `sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md`
- Output artifacts: `sample-data/Runtime/Sessions/{DEAL}/{DATE}_stage{N}_demo__*.md`

**Artifact Constraints:**
- Demo script: 600-800 words, bulleted, minute-by-minute flow
- Technical checklist: 5-10 items, owners assigned, D1 deadline
- Customer agenda: Under 200 words, collaborative tone, value-focused

**Output Format:**
1. Chat Output (under 100 words, bullets only)
2. Artifact Output (full content with frontmatter)
3. JSON Summary (summaryBullets, risks, missingInformation, d1Actions, d7Actions)

**Demo Best Practices:**
- Focus on 3-5 use cases max (avoid feature tours)
- Lead with value/pain relief, not features
- Interactive validation ("show don't tell")
- Technical environment pre-validated
- Clear next-step commitment at end
- Stakeholder-specific customization

**Stage Context:**
- Typically Stage 2-3 (after discovery complete)
- Discovery must validate pain, budget, decision process
- Demo advances by validating solution fit and securing next step

# See Also

- **prep-discovery** - For initial discovery call preparation (run before demo)
- **coach** - For deal health assessment if discovery gaps detected
- **sales_communications** - To generate confirmation email with demo agenda
- **roi-model** - To prepare financial justification for demo discussion
- **next-steps** - For post-demo action recommendations
- **reference.md** - Detailed demo script examples and troubleshooting
- **templates/demo_question_bank.md** - Validation question library by vertical
