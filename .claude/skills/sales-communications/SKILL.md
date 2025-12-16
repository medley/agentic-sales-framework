---
name: sales-communications
description: Generate stage-specific sales artifacts using deal context and brand alignment
allowed-tools: [Read, Write]
---

# Sales Communications Generator

Generate customer-facing and internal sales artifacts with automatic brand alignment and deal context integration.

> **Note:** All company names, contact names, and scenarios in examples throughout this skill and its patterns are fictional, created for demonstration purposes.

## When to Use

User requests a sales artifact (email, agenda, briefing, one-pager) for an active deal or prospect.

## Pattern Routing

### Mode Detection (Generation vs Coaching)

**Step 1: Determine if user wants coaching or generation**

Route to **email_coach** (coaching mode) if:
- User message contains email-like text block with greeting + body + sign-off
- OR user uses coaching verbs:
  - "improve this email"
  - "review my draft"
  - "make this better"
  - "tighten this up"
  - "shorten this"
  - "lengthen this"
  - "make this more formal"
  - "make this more casual"

Route to **generation pattern** if:
- User says "draft", "write", "create" + email type
- No draft text provided in message

**Step 2: If generation mode, select appropriate pattern from table below**

---

### Generation Pattern Selection

| Pattern | Trigger Phrases | Use When |
|---------|----------------|----------|
| **Stage-Specific Emails** | | |
| email_discovery_recap | "discovery recap", "discovery follow-up" | After discovery call |
| email_demo_followup | "demo follow-up", "demo recap" | After product demo |
| email_proposal_nudge | "proposal nudge", "check in on proposal" | Advancing stalled proposal |
| email_poc_pilot_results | "POC results", "pilot results", "trial results" | After proof-of-concept completion |
| **Prospecting & Outreach** | | |
| email_cold_outbound | "cold email", "outbound email" | New prospect outreach |
| email_exec_summary | "exec summary email", "executive summary" | Escalating to exec sponsor |
| **Relationship & Follow-Up** | | |
| email_simple_followup | "looking forward", "see you", "quick follow-up" | Brief meeting confirmation (future event) |
| email_check_in | "check in", "haven't heard back", "gentle follow-up" | Re-engage after 1-2 weeks silence |
| email_touchbase | "quarterly check-in", "touch base", "long-cycle follow-up" | Reconnect after 3+ months |
| email_thank_you | "thank you email", "send thanks", "appreciate their time" | Pure gratitude, no next steps |
| email_congratulations | "congrats", "congratulate", "celebrate" | Acknowledge their achievement |
| email_article_share | "share article", "send resource", "thought of you" | Value-add content sharing |
| **Logistics & Coordination** | | |
| email_meeting_reminder | "meeting reminder", "day-of logistics", "confirm call details" | Day-of or day-before meeting |
| email_reschedule_request | "reschedule meeting", "need to move our call" | Request meeting time change |
| email_introduction | "intro {person} to {person}", "connect {name} with {name}" | Double opt-in connector |
| **Seasonal & Occasional** | | |
| email_holiday_greeting | "holiday greeting", "season's greetings", "end of year" | Seasonal touchpoint |
| **Customer Success** | | |
| email_post_signature | "post-signature email", "welcome {customer}" | Immediate post-close welcome |
| email_milestone_celebration | "celebrate {milestone}", "congrats on go-live" | Celebrate customer achievement |
| **Internal & Team** | | |
| email_internal_prep | "internal prep email", "team prep" | Prepping internal team |
| **Requests & Asks** | | |
| email_asking_for_favor | "ask for reference", "request case study", "get testimonial" | Customer reference/favor requests |
| **Agendas** | | |
| agenda_customer | "customer agenda", "call agenda" | External meeting prep |
| agenda_internal | "internal agenda", "team agenda" | Internal meeting prep |
| **Briefings** | | |
| briefing_team | "team briefing", "sales briefing" | Team context sharing |
| briefing_exec | "exec briefing", "executive briefing" | Executive stakeholder update |
| **Summaries** | | |
| onepager | "one-pager", "deal summary" | Deal summary artifact |
| **Email Coaching** | | |
| email_coach | "improve this", "review my draft", "make better" | Improve existing email draft while preserving voice |

All patterns load `patterns/_common.md` first for shared logic (deal context, brand guidelines, methodology).

**Note**: email_coach is universal (works for ANY email type). Other email patterns are for generation from scratch.

## Usage Examples

### Basic Invocation

**Simple Meeting Confirmation:**
```
"Write a follow-up email to Jim, looking forward to meeting him next week at the onsite"
```
→ Routes to `email_simple_followup` pattern
→ Loads deal context for recipient name and event details
→ Generates brief 80-120 word confirmation email

**Email Coaching (Improve Draft):**
```
User pastes draft:
"Hi Jim, I hope this email finds you well. We had a great conversation last week
about your reporting challenges and I wanted to follow up with some resources
and next steps to keep the momentum going. Let me know if you have any questions."

User: "Make this shorter"
```
→ Routes to `email_coach` pattern (detects draft text + "make this shorter")
→ Loads AE style corpus for voice preservation
→ Improves draft: reduces word count, strengthens CTA, matches AE voice
→ Returns improved version with change log

**Customer Follow-Up Email (Post-Demo):**
```
"Draft a demo follow-up for AcmeCorp"
```
→ Routes to `email_demo_followup` pattern
→ Loads deal context from `sample-data/Runtime/Sessions/AcmeCorp/deal.md`
→ Generates comprehensive email with demo recap, Q&A, resources, next steps

**Prospecting Email:**
```
"Write a cold email to Jane Smith at GlobalPharma about reporting automation"
```
→ Routes to `email_cold_outbound` pattern
→ Creates brief, personalized outreach (50-100 words)
→ Saves to `sample-data/Runtime/Sessions/_Prospects/`

**Internal Team Prep:**
```
"Send team prep email before tomorrow's technical call with AcmePharma"
```
→ Routes to `email_internal_prep` pattern
→ Loads stakeholder profiles, objection handling, role assignments
→ Generates comprehensive prep brief for internal team

**Customer Meeting Agenda:**
```
"Create agenda for discovery call with Example Pharma on Nov 20"
```
→ Routes to `agenda_customer` pattern
→ Generates professional agenda with time-boxed topics
→ Includes background, objectives, next steps

**Team Briefing:**
```
"Generate sales briefing for the AcmeCorp deal"
```
→ Routes to `briefing_team` pattern
→ Full MEDDPICC assessment, stakeholder map, deal history
→ Used for handoffs, collaboration, manager updates

**Deal Summary:**
```
"Create a one-pager for the OurProduct opportunity"
```
→ Routes to `onepager` pattern
→ Dense 1-page snapshot (customer or internal version)
→ Includes key facts, timeline, status, next steps

### Deal Context Integration

**Discovery Recap (with methodology):**
```
"Draft discovery recap for AcmeCorp"
```
→ Loads `deal.md`: MEDDPICC fields, stakeholder names, recent history
→ Loads methodology: `MEDDPICC/stage_inventory_MEDDPICC.md` for Discovery stage exit criteria
→ Generates email addressing qualification gaps, confirming understanding

**Proposal Nudge (with timeline urgency):**
```
"Check in on the AcmeCorp proposal"
```
→ Loads `deal.md`: Proposal sent date (calculates days since), Economic Buyer, Decision Timeline
→ Creates urgency from THEIR timeline (not yours): "You mentioned need to decide by Nov 30..."
→ Offers alternatives: Full deal, pilot, phased approach

**Executive Briefing (with strategic context):**
```
"Create exec briefing for my VP about AcmeCorp"
```
→ Loads `deal.md`: D1 tasks (strategic initiatives), Risk Register, MEDDPICC assessment
→ Generates concise 1-2 page brief with "The Ask" first
→ Includes talking points for exec involvement

### Framework Workflow Integration

**After deal_intake (intake → artifact):**
1. Run: `"Ingest the discovery transcript for AcmeCorp"`
   → `deal_intake` skill processes transcript, updates `deal.md`
2. Then: `"Draft discovery recap for AcmeCorp"`
   → `sales_communications` loads updated `deal.md`, generates follow-up email

**Before customer call (prep workflow):**
1. Verify `deal.md` is current (update History, D7 tasks if needed)
2. Run: `"Send internal prep email for tomorrow's AcmeCorp demo"`
   → Generates team brief with stakeholder profiles, demo goals, objection handling
3. Run: `"Create customer agenda for AcmeCorp demo"`
   → Generates professional agenda to send to customer

**After deal close (handoff workflow):**
1. Mark deal as "Closed-Won" in `deal.md`
2. Run: `"Generate handover one-pager for AcmeCorp"`
   → Creates comprehensive deal summary for CS/implementation team
   → Includes account history, stakeholders, commercial terms, success criteria

## Pattern Selection Rules

When choosing between similar patterns, apply these priority rules:

### Email Pattern Priority

**For forward-looking communications (upcoming events)**:
1. **email_simple_followup** - Use when request contains:
   - "looking forward to"
   - "see you {timeframe}"
   - "quick follow-up" or "simple reminder"
   - "confirm meeting/onsite/demo"
   - "wish {name} a nice weekend/holiday"
   - User wants brief confirmation without detailed content

2. **agenda_customer** - Use when request needs:
   - Structured time-boxed agenda
   - Multiple topics/sections
   - Formal meeting preparation

**For backward-looking communications (past events)**:
1. **email_discovery_recap** - After discovery call with qualification data
2. **email_demo_followup** - After product demo with Q&A, resources, POC discussion

**Avoid email_demo_followup unless**:
- Request explicitly mentions "demo recap" or "demo follow-up"
- Message needs to recap workshop/presentation that already occurred
- Technical resources or Q&A sections required
- POC/trial next steps need detailed explanation

**Avoid email_simple_followup unless**:
- Message is about upcoming event (not past event)
- User wants brief, casual tone (<120 words)
- No technical details, resources, or detailed next steps required

### JSON Output Requirements (if using structured output)

**For mode = "simple_followup"**:
```json
{
  "mode": "simple_followup",
  "subject": "{max 7 words}",
  "toPersona": "{recipient name/role}",
  "bodyMarkdown": "{max 120 words, single paragraph, no headers}"
}
```

**For mode = "demo_followup"**:
```json
{
  "mode": "demo_followup",
  "subject": "{max 10 words}",
  "toPersona": "{recipient name/role}",
  "bodyMarkdown": "{multiple sections: opening, recap bullets, Q&A, resources, next steps}"
}
```

---

## Error Handling

- **Ambiguous request**: Check deal.md stage → suggest most relevant pattern
- **Missing pattern file**: List available patterns + suggest closest match
- **Missing brand guidelines**: Use generic defaults (no error)
- **Missing deal.md**: Prompt user to run deal_intake first
- **Multiple pattern matches**: Apply Pattern Selection Rules above, prioritize most specific match
- **Malformed pattern**: Log error + use fallback template

## Output Format (CRITICAL)

ALL sales_communications outputs MUST follow this three-section envelope structure:

### Section 1: Chat Output

A `# Chat Output` heading followed by a single markdown code fence containing ONLY the final email ready to send.

**Rules:**
- NO analysis, NO pattern selection notes, NO voice verification details
- NO duplicate emails
- Email format: Subject line, optional To line, body paragraphs, closing, signature
- For coaching mode: show ONLY the improved version (not original + improved)
- For generation mode: show ONLY the final email

**Example:**
```markdown
# Chat Output

```markdown
Subject: Looking Forward to Tuesday's Workshop

Hi Jim,

Looking forward to our workshop on Tuesday at 2pm. I'll bring the technical deep-dive materials we discussed.

See you then,
Welf
```
```

### Section 2: Artifact Output

A `# Artifact Output` heading followed by a single markdown code fence containing the complete artifact for storage.

**Contents (in order):**
1. **YAML frontmatter** (generated_by, generated_on, deal_id, sources, plus optional: mode, pattern, voice_verification, etc.)
2. **Email body** (full email with subject, greeting, body, closing, signature)
3. **Email Analysis** section (ONLY if coaching mode or complex generation):
   - Pattern used and why
   - Key deal context incorporated
   - Brand alignment notes
4. **Voice Verification** section (ONLY if voice corpus loaded):
   - Voice match score
   - Corrections applied
   - Style notes
5. **Notes** section (optional):
   - Missing information flagged
   - Assumptions made
   - Suggested follow-up actions

**Example:**
```markdown
# Artifact Output

```markdown
---
generated_by: sales-communications/email_simple_followup
generated_on: 2025-01-15T14:30:00Z
deal_id: Northwind Manufacturing
sources:
  - sample-data/Runtime/Sessions/Northwind Manufacturing/deal.md
  - sample-data/Runtime/_Shared/knowledge/brand_guidelines.md
mode: simple_followup
pattern: email_simple_followup
---

Subject: Looking Forward to Tuesday's Workshop

Hi Jim,

Looking forward to our workshop on Tuesday at 2pm. I'll bring the technical deep-dive materials we discussed.

See you then,
Welf

---

## Email Analysis

**Pattern Used:** email_simple_followup
**Rationale:** User requested brief confirmation for upcoming onsite workshop (forward-looking event, no detailed recap needed)

**Deal Context:**
- Jim Selby = Primary Champion (per deal.md)
- Workshop scheduled for 2025-01-18 at 2pm (per History section)
- Technical deep-dive requested in last call notes

**Brand Alignment:**
- Tone: Professional, casual (matches AE voice corpus)
- Length: 42 words (within 80-120 word target for simple_followup)
- No marketing jargon (per brand guidelines)

---

## Notes

**Next Actions:**
- Prepare technical deep-dive materials for workshop
- Confirm Jim received calendar invite
```
```

### Section 3: JSON Summary

A ` ```json summary` code fence containing valid JSON with email metadata.

**Required schema for sales_communications:**
```json
{
  "mode": "simple_followup|demo_followup|cold_outbound|discovery_recap|...",
  "pattern": "email_simple_followup|email_demo_followup|...",
  "subject": "Email subject line",
  "toPersona": "Recipient name or role",
  "fromPersona": "Sender name (usually AE)",
  "summaryBullets": [
    "Brief description of email purpose",
    "Key point or context"
  ],
  "nextActions": [
    "Prepare materials for workshop",
    "Confirm calendar invite received"
  ]
}
```

**Example:**
```markdown
```json summary
{
  "mode": "simple_followup",
  "pattern": "email_simple_followup",
  "subject": "Looking Forward to Tuesday's Workshop",
  "toPersona": "Jim Selby",
  "fromPersona": "Welf Ludwig",
  "summaryBullets": [
    "Confirming attendance at Tuesday workshop",
    "Bringing technical materials as discussed"
  ],
  "nextActions": [
    "Prepare technical deep-dive materials",
    "Verify calendar invite sent"
  ]
}
```
```

### Complete Output Example

```markdown
# Chat Output

```markdown
Subject: Looking Forward to Tuesday's Workshop

Hi Jim,

Looking forward to our workshop on Tuesday at 2pm. I'll bring the technical deep-dive materials we discussed.

See you then,
Welf
```

# Artifact Output

```markdown
---
generated_by: sales-communications/email_simple_followup
generated_on: 2025-01-15T14:30:00Z
deal_id: Northwind Manufacturing
sources:
  - sample-data/Runtime/Sessions/Northwind Manufacturing/deal.md
mode: simple_followup
pattern: email_simple_followup
---

Subject: Looking Forward to Tuesday's Workshop

Hi Jim,

Looking forward to our workshop on Tuesday at 2pm. I'll bring the technical deep-dive materials we discussed.

See you then,
Welf

---

## Email Analysis

**Pattern Used:** email_simple_followup
**Rationale:** Brief confirmation for upcoming workshop

**Deal Context:**
- Jim Selby = Primary Champion
- Workshop: 2025-01-18 at 2pm
- Technical deep-dive requested

**Brand Alignment:**
- Professional, casual tone
- 42 words (target: 80-120)
```

```json summary
{
  "mode": "simple_followup",
  "pattern": "email_simple_followup",
  "subject": "Looking Forward to Tuesday's Workshop",
  "toPersona": "Jim Selby",
  "fromPersona": "Welf Ludwig",
  "summaryBullets": [
    "Confirming Tuesday workshop attendance",
    "Bringing technical materials"
  ],
  "nextActions": [
    "Prepare technical materials",
    "Verify calendar invite"
  ]
}
```
```

### Output Validation Rules

**CRITICAL - Enforce these rules:**

1. **Always emit all three sections** in this order: Chat Output → Artifact Output → JSON Summary
2. **Never emit more than one Chat Output** section (no duplicates, no before/after comparisons in Chat Output)
3. **Chat Output must be clean** - ONLY the final email, no meta-commentary
4. **All analysis goes in Artifact Output** - Pattern selection, voice notes, Email Analysis, all metadata
5. **JSON must be valid** - parseable JSON with all required keys (mode, pattern, subject, toPersona, fromPersona, summaryBullets, nextActions)
6. **Code fences must be properly closed** - Each section has exactly one opening ` ```markdown` and one closing ` ``` `
7. **JSON fence label is "summary"** - Must be ` ```json summary` not ` ```json`

### File Output

After generating the three-section output, save ONLY the Artifact Output content (including frontmatter) to:
- Deal sessions: `sample-data/Runtime/Sessions/{DEAL_NAME}/{artifact_type}_{timestamp}.md`
- Prospects: `sample-data/Runtime/Sessions/_Prospects/{artifact_type}_{timestamp}.md`

The Chat Output and JSON Summary are for chat/API consumption only (not saved to separate files).
