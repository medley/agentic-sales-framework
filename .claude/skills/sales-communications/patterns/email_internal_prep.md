# Email: Internal Team Prep

**Pattern**: email_internal_prep
**Type**: Internal-facing email
**Timing**: 24 hours before customer call
**Purpose**: Align internal team (SE, CSM, exec) on customer context and call objectives

---

## When to Use

Send this email to internal stakeholders before customer calls to:
- Brief team members joining customer calls (SEs, CSMs, executives, product specialists)
- Ensure everyone understands customer context and deal status
- Align on roles, talking points, and what NOT to say
- Surface potential landmines or objections to prepare for
- Coordinate handoffs and follow-up ownership

**Trigger Phrases**:
- "Draft internal prep for {DEAL} call"
- "Brief team for {meeting type}"
- "Create internal call prep email"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Upcoming customer meeting details (from D7 tasks or History)
   - Current deal status (stage, MEDDPICC fields, recent history)
   - Stakeholder landscape (who's on their side, dynamics)
   - Open questions, objections, or concerns
3. Email style corpus (4-tier loading per _common.md section 3) - internal style

**OPTIONAL**:
- Brand guidelines (for internal email formatting)
- Methodology stage inventory (for stage-specific coaching)

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Meeting details**: Date, time, type (discovery, demo, technical deep-dive, pricing, executive review)
- **Customer attendees**: From Stakeholders section (names, titles, roles, personalities)
- **Internal attendees**: Who from your team is joining (SE, CSM, exec, product)
- **Deal status**: Current stage, MEDDPICC completion, blockers
- **Recent history**: Last 2-3 customer interactions (what they know, what's been promised)
- **Stakeholder dynamics**: Champion, blockers, economic buyer, technical evaluators
- **Objections/concerns**: From History or MEDDPICC Competition field
- **D7 tasks**: What needs to happen after this call

**Example Context to Parse**:
```markdown
## Stakeholders
- **Jane Smith** (VP Operations) - Champion, budget owner, motivated by cost reduction
- **Michael Chen** (Director IT) - Technical gatekeeper, risk-averse, concerned about integration complexity
- **Carol Martinez** (CFO) - Economic Buyer, final approval, focused on ROI and payback period

## History
### 2025-11-13 - Demo Call
- Showed Salesforce integration to Jane and Michael
- Michael raised SSO concerns, asked about data retention policies
- Jane loved dashboard templates, wants to show CFO
- Next: Executive review call with Carol (CFO) scheduled Nov 22

## MEDDPICC
**Competition**: Current manual process (status quo), evaluated Competitor X (rejected - too expensive)
**Decision Process**: Carol must approve all investments >$100K, board review in December
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system for internal communications:
- More casual than customer-facing (use "we" not "I")
- Bullet-heavy format (skim-friendly)
- Direct language, no fluff
- Action-oriented

### 3. Load Brand Guidelines (Section 2 of _common.md)

If brand guidelines exist with internal communication standards, apply those

### 4. Load Methodology Guidance (Section 4 of _common.md)

If MEDDPICC stage inventory available:
- Include stage-specific coaching for team (what to validate, what to avoid)
- Reference methodology playbook sections if applicable

---

## Email Structure

### Subject Line
**Formula**: `INTERNAL: {Customer} {Meeting Type} Prep - {Date}`

**Examples**:
- "INTERNAL: AcmeCorp Executive Review Prep - Nov 22"
- "INTERNAL: TechCo Demo Call Brief - Tomorrow 2pm"
- "INTERNAL: HealthCorp Technical Deep-Dive - Nov 16"

**Best Practices**:
- Start with "INTERNAL:" to distinguish from customer emails
- Include customer name and meeting type
- Include date for urgency

### Opening Paragraph
**Purpose**: Set context, identify attendees, state purpose

**Template**:
```
Team,

Quick brief for our {meeting type} with {Customer} on {date/time}. {Who from our
team is attending}. This email covers customer context, call objectives, and roles.
```

**Example**:
```
Team,

Quick brief for our executive review call with AcmeCorp CFO on Thursday 11/22 at 10am.
Tom (SE) and I will be on the call, plus Mike (our VP Sales) joining for the first
15 minutes. This email covers customer context, call objectives, and roles.
```

### Deal Summary Section
**Purpose**: Give team members context if they haven't followed deal closely

**Template**:
```
## Deal Summary

**Customer**: {Company name, industry, size}
**Opportunity**: {ACV, term, product/plan}
**Stage**: {Current stage} (forecasted close: {date})

**Quick Context**:
- {1-2 sentence business problem}
- {Current status - validation done, pending items}
- {Key stakeholder we're meeting with and their role}
```

**Example**:
```
## Deal Summary

**Customer**: AcmeCorp, manufacturing, 5000 employees
**Opportunity**: $144K ACV, 12-month term, Enterprise plan (50 users)
**Stage**: Proposal (forecasted close: Nov 30)

**Quick Context**:
- Finance team spending $500K/year on manual reporting, board demanding real-time dashboards
- Technical validation complete (IT signoff), proposal sent, pricing approved by VP Ops
- Meeting with Carol Martinez (CFO) who has final budget approval >$100K
```

### Customer Attendee Profiles Section
**Purpose**: Brief team on who they're talking to (personalities, motivations, concerns)

**Template**:
```
## Customer Attendees

**{Name}, {Title}** - {Role in decision}
- {Motivation or priority}
- {Communication style or personality note}
- {Concerns or objections if any}

**{Name}, {Title}** - {Role in decision}
- {Motivation or priority}
- {Communication style or personality note}
```

**Example**:
```
## Customer Attendees

**Carol Martinez, CFO** - Economic Buyer (final approval)
- Priorities: ROI, payback period, financial risk mitigation
- Style: Data-driven, direct, skeptical of vendor claims
- Concerns: Likely to push on implementation risk and total cost of ownership

**Jane Smith, VP Operations** - Champion
- Motivation: Reduce team overhead, improve board reporting speed
- Style: Relationship-focused, enthusiastic about solution
- Role in call: Will advocate for us, expect her to reinforce business case
```

**Best Practices**:
- Flag champions (your advocates) vs blockers (skeptics)
- Note communication styles (data-driven vs relationship-focused)
- Surface known objections team should be ready to address

### Call Objectives Section
**Purpose**: Align team on what success looks like

**Template**:
```
## Call Objectives

1. **{Primary objective}** - {Success criteria}
2. **{Secondary objective}** - {Success criteria}
3. **{Tertiary objective if applicable}** - {Success criteria}

**What We NEED to Leave With**:
- {Must-have outcome - commitment, decision, next step}
```

**Example**:
```
## Call Objectives

1. **Get CFO approval** - Carol confirms budget approval and signs off on moving forward
2. **Address financial objections** - Answer ROI, payback, TCO questions confidently
3. **Set contract timeline** - Agree to contract send by Nov 23, close by Nov 30

**What We NEED to Leave With**:
- Carol's verbal commitment to proceed (or clear understanding of what's blocking her)
- Agreement on next steps: contract review timeline and signature date
```

### Talking Points & Strategy Section
**Purpose**: Coordinate messaging, assign roles, align on what to emphasize

**Template**:
```
## Talking Points & Strategy

**What to EMPHASIZE**:
- {Key value prop for this audience}
- {Proof point - customer story, data, validation}
- {Urgency driver - timeline, business event}

**What to AVOID**:
- {Topic that could derail - pricing, feature gaps, politics}
- {Landmine - something said in prior calls that caused concern}

**Roles**:
- {Name}: {What they'll cover}
- {Name}: {What they'll cover}
```

**Example**:
```
## Talking Points & Strategy

**What to EMPHASIZE**:
- 9-month payback period and $300K annual savings (Carol's priorities)
- IT validation complete (de-risk implementation concerns)
- Jan 15 go-live enables Q1 board reporting (ties to their timeline)
- Fortune 500 healthcare customer similar use case (social proof)

**What to AVOID**:
- Don't mention custom development (Carol doesn't care, could introduce risk perception)
- Don't get into technical weeds (Michael already validated, Carol trusts him)
- Don't negotiate pricing (already approved by Jane, don't reopen)

**Roles**:
- Sarah (AE): Lead call, business case recap, handle commercial discussion
- Mike (VP Sales): First 15 min - Executive intro, customer success commitment, then drop
- Tom (SE): On standby for technical questions (shouldn't need, but ready)
```

**Best Practices**:
- Preempt landmines (what NOT to say is as important as what to say)
- Assign clear roles (who speaks when, who stays quiet)
- Reference past interactions (what's been promised, what caused concern)

### Potential Objections & Responses Section
**Purpose**: Prepare team for pushback, align on handling

**Template**:
```
## Potential Objections & Responses

**Objection**: {Expected pushback}
**Response**: {How to handle - who addresses, key points}

**Objection**: {Expected pushback}
**Response**: {How to handle}
```

**Example**:
```
## Potential Objections & Responses

**Objection**: "What if implementation takes longer than promised?"
**Response**: (Sarah) Point to IT validation, reference implementation timeline in proposal.
(Tom) Offer to walk through technical plan if needed, cite 30-day avg implementation time.

**Objection**: "How do I know you'll deliver the projected savings?"
**Response**: (Sarah) Walk through ROI methodology with their specific inputs,
reference similar customer implementations. Offer to build detailed ROI model together.

**Objection**: "Why not wait until next budget cycle?"
**Response**: (Sarah) Jan 15 go-live requirement for Q1 board reporting (per Jane). Waiting
means another quarter of $125K manual processing costs. (Mike) Reinforce customer success
commitment to hit their timeline.
```

### Follow-Up Plan Section
**Purpose**: Coordinate post-call actions

**Template**:
```
## Follow-Up Plan

**If Carol approves**:
- {Action 1 - who owns, when}
- {Action 2 - who owns, when}

**If Carol has concerns**:
- {How to handle objections, who follows up}
```

**Example**:
```
## Follow-Up Plan

**If Carol approves**:
- Sarah sends contract by EOD Nov 22 (same day)
- Tom sends technical implementation plan to Michael by Nov 23
- Sarah schedules contract review call with legal for Nov 27

**If Carol has concerns**:
- Sarah captures specific objections, schedules 1:1 follow-up within 48 hours
- Tom prepares detailed ROI model or implementation risk mitigation plan as needed
- Mike offers to connect Carol with reference customer CFO
```

### Closing Paragraph
**Purpose**: Invite questions, confirm attendance

**Template**:
```
{Pre-call coordination ask}. {Question invitation}. {Confidence statement}.

{Closing},
{AE Name}
```

**Example**:
```
Let's connect 15 minutes before the call (9:45am) to align. Any questions or concerns,
reply all or Slack me. This should be straightforward - Jane's done great work building
internal support, we just need to get Carol comfortable with ROI and timeline.

Thanks,
Sarah
```

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_internal_prep
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
meeting_type: {discovery|demo|technical|pricing|executive}
meeting_date: {YYYY-MM-DD}
internal_recipients: [{team_member_names}]
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - sample-data/Runtime/_Shared/style/{style_file}  # if loaded
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
  - sample-data/Runtime/_Shared/knowledge/methodologies/{METHOD}/stage_inventory__{METHOD}.md  # if loaded
---
```

### 2. Compose Email Body

Follow structure above with actual content from deal.md

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_internal_prep_{MEETING_TYPE}_{DATE}.md`

**Filename format**: `email_internal_prep_executive_2025-11-22.md`

---

## Error Handling

**Missing meeting details**:
- Prompt user: "No upcoming meeting found. Add meeting details to D7 tasks?"
- Generate generic prep structure with placeholders

**Missing stakeholder info**:
- Use generic profiles: "Primary contact", "Technical evaluator"
- Suggest updating Stakeholders section

**Missing MEDDPICC fields**:
- Omit objections section if Competition not documented
- Generic objectives if Economic Buyer not identified

**Missing recent History**:
- Use stage-based assumptions for call objectives
- Suggest documenting recent customer interactions

---

## Internal Prep Best Practices

### Why Internal Alignment Matters

**Benefits**:
- Prevents contradictory messaging (team says different things)
- Surfaces landmines before customer sees them
- Ensures right person addresses right topics (don't let SE negotiate pricing)
- Builds team confidence (prepared = better performance)

### When to Send

**Timing**: 24 hours before customer call (not too early, not last-minute)

**Who to Include**:
- Anyone joining the customer call
- Manager/leadership if deal is strategic or at-risk
- Support teams if follow-up actions will need their help

### What NOT to Include

**Avoid**:
- Negative opinions about customer ("Jane is difficult")
- Sensitive internal pricing/margin discussions (use separate thread)
- Unvalidated assumptions presented as facts
- Lengthy narratives (bullets > paragraphs for skim-ability)

### Post-Call Debrief

After the call, send quick update:
- What happened (outcomes vs objectives)
- What changed (new info, surprises)
- Next steps and owners
- Update deal.md History accordingly

---

## Example Output

```markdown
---
generated_by: sales-communications/email_internal_prep
generated_on: 2025-11-20T16:00:00Z
deal_id: AcmeCorp
meeting_type: executive
meeting_date: 2025-11-22
internal_recipients: [Tom Rodriguez, Mike Sullivan]
sources:
  - sample-data/Runtime/Sessions/AcmeCorp/deal.md
  - sample-data/Runtime/_Shared/style/team_corpus.md
---

**Subject**: INTERNAL: AcmeCorp Executive Review Prep - Nov 22

Team,

Quick brief for our executive review call with AcmeCorp CFO on Thursday 11/22 at 10am.
Tom (SE) and I will be on the call, plus Mike (our VP Sales) joining for the first
15 minutes. This email covers customer context, call objectives, and roles.

## Deal Summary

**Customer**: AcmeCorp, manufacturing, 5000 employees
**Opportunity**: $144K ACV, 12-month term, Enterprise plan (50 users)
**Stage**: Proposal (forecasted close: Nov 30)

**Quick Context**:
- Finance team spending $500K/year on manual reporting, board demanding real-time dashboards
- Technical validation complete (IT signoff), proposal sent, pricing approved by VP Ops
- Meeting with Carol Martinez (CFO) who has final budget approval >$100K

## Customer Attendees

**Carol Martinez, CFO** - Economic Buyer (final approval)
- Priorities: ROI, payback period, financial risk mitigation
- Style: Data-driven, direct, skeptical of vendor claims
- Concerns: Likely to push on implementation risk and total cost of ownership

**Jane Smith, VP Operations** - Champion
- Motivation: Reduce team overhead, improve board reporting speed
- Style: Relationship-focused, enthusiastic about solution
- Role in call: Will advocate for us, expect her to reinforce business case

## Call Objectives

1. **Get CFO approval** - Carol confirms budget approval and signs off on moving forward
2. **Address financial objections** - Answer ROI, payback, TCO questions confidently
3. **Set contract timeline** - Agree to contract send by Nov 23, close by Nov 30

**What We NEED to Leave With**:
- Carol's verbal commitment to proceed (or clear understanding of what's blocking her)
- Agreement on next steps: contract review timeline and signature date

## Talking Points & Strategy

**What to EMPHASIZE**:
- 9-month payback period and $300K annual savings (Carol's priorities)
- IT validation complete (de-risk implementation concerns)
- Jan 15 go-live enables Q1 board reporting (ties to their timeline)
- Fortune 500 healthcare customer similar use case (social proof)

**What to AVOID**:
- Don't mention custom development (Carol doesn't care, could introduce risk perception)
- Don't get into technical weeds (Michael already validated, Carol trusts him)
- Don't negotiate pricing (already approved by Jane, don't reopen)

**Roles**:
- Sarah (AE): Lead call, business case recap, handle commercial discussion
- Mike (VP Sales): First 15 min - Executive intro, customer success commitment, then drop
- Tom (SE): On standby for technical questions (shouldn't need, but ready)

## Potential Objections & Responses

**Objection**: "What if implementation takes longer than promised?"
**Response**: (Sarah) Point to IT validation, reference implementation timeline in proposal.
(Tom) Offer to walk through technical plan if needed, cite 30-day avg implementation time.

**Objection**: "How do I know you'll deliver the projected savings?"
**Response**: (Sarah) Walk through ROI methodology with their specific inputs,
reference similar customer implementations. Offer to build detailed ROI model together.

**Objection**: "Why not wait until next budget cycle?"
**Response**: (Sarah) Jan 15 go-live requirement for Q1 board reporting (per Jane). Waiting
means another quarter of $125K manual processing costs. (Mike) Reinforce customer success
commitment to hit their timeline.

## Follow-Up Plan

**If Carol approves**:
- Sarah sends contract by EOD Nov 22 (same day)
- Tom sends technical implementation plan to Michael by Nov 23
- Sarah schedules contract review call with legal for Nov 27

**If Carol has concerns**:
- Sarah captures specific objections, schedules 1:1 follow-up within 48 hours
- Tom prepares detailed ROI model or implementation risk mitigation plan as needed
- Mike offers to connect Carol with reference customer CFO

Let's connect 15 minutes before the call (9:45am) to align. Any questions or concerns,
reply all or Slack me. This should be straightforward - Jane's done great work building
internal support, we just need to get Carol comfortable with ROI and timeline.

Thanks,
Sarah
```

---

**End of Pattern: email_internal_prep**
