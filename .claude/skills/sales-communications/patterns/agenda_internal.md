# Document: Internal Meeting Agenda

**Pattern**: agenda_internal
**Type**: Internal-facing document
**Timing**: Before internal strategy/planning meetings
**Purpose**: Structure internal deal reviews, account planning, forecast calls

---

## When to Use

Create this agenda for internal meetings about deals:
- Deal strategy sessions (how to advance stalled deals)
- Account planning (mapping stakeholders, identifying expansion)
- Forecast reviews (pipeline qualification, risk assessment)
- Post-mortem reviews (won/lost deal analysis)
- Team collaboration (multi-AE accounts, handoffs)

**Trigger Phrases**:
- "Draft internal agenda for {deal} strategy session"
- "Create deal review agenda"
- "Prepare account planning meeting agenda"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Current deal status (stage, MEDDPICC fields, history)
   - Blockers or open questions (from D1/D7 tasks)
   - Meeting purpose (strategy, forecast review, planning)
3. **NOTE**: Do NOT load email style corpus (not applicable for internal documents)

**OPTIONAL**:
- Brand guidelines (for internal document formatting)
- Methodology stage inventory (for methodology-specific deal review questions)

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Meeting purpose**: Why are we meeting? (Strategy session, forecast review, account planning)
- **Deal status**: Current stage, MEDDPICC completion, forecasted close date
- **Recent activity**: Last 2-3 History entries (what's happened, what's working/not working)
- **Blockers**: From D1 tasks (strategic issues preventing progress)
- **Open questions**: From MEDDPICC gaps or D7 tasks (what needs to be decided)
- **Stakeholder landscape**: From Stakeholders section (who's engaged, who's missing)
- **Competition**: From MEDDPICC Competition field (if applicable)

**Example D1 Task to Parse** (triggers need for strategy session):
```markdown
## D1 Tasks (Deal-Level)
- [ ] BLOCKER: Economic Buyer (CFO) not yet engaged, champion (VP Ops) doesn't have
      budget authority >$100K. Need strategy to get CFO meeting.
- [ ] Risk: Competitor X offering 20% discount, customer asked us to match
- [ ] Question: Customer wants custom SLA terms not in standard contract - legal review needed
```

### 2. Load Brand Guidelines (Section 2 of _common.md)

If brand_guidelines.md exists with internal document standards, apply formatting

### 3. Load Methodology Guidance (Section 4 of _common.md)

If MEDDPICC stage inventory available:
- Use methodology framework for deal review questions
- Reference stage exit criteria to assess readiness
- Apply qualification criteria to forecast assessment

---

## Document Structure

### Header Section

**Structure**:
```
# Internal Meeting Agenda: {Meeting Type}

**Deal**: {Customer Company Name}
**Meeting Type**: {Strategy Session | Forecast Review | Account Planning | Post-Mortem}
**Date**: {Date}
**Time**: {Time} {Timezone}
**Duration**: {Duration}
**Attendees**: {Internal team members}
```

**Example**:
```
# Internal Meeting Agenda: Deal Strategy Session

**Deal**: AcmeCorp
**Meeting Type**: Strategy Session
**Date**: Monday, November 20, 2025
**Time**: 2:00 PM ET
**Duration**: 60 minutes
**Attendees**: Sarah Chen (AE), Mike Sullivan (VP Sales), Tom Rodriguez (SE), Lisa Park (Sales Ops)
```

### Meeting Purpose Section

**Purpose**: Align on why we're meeting and what we need to decide

**Structure**:
```
## Meeting Purpose

{1-2 sentence problem statement or meeting trigger}

**Decisions Needed**:
1. {Decision or strategic question to resolve}
2. {Decision or strategic question to resolve}
3. {Decision or strategic question to resolve}
```

**Example (Strategy Session)**:
```
## Meeting Purpose

AcmeCorp deal stalled at $144K ACV - champion (Jane, VP Ops) engaged but CFO (Carol)
not yet involved, and Jane doesn't have budget authority >$100K. We need a strategy
to engage the Economic Buyer before end of quarter.

**Decisions Needed**:
1. How do we get a meeting with Carol (CFO) - through Jane, direct outreach, or exec-to-exec?
2. Should we adjust deal size/structure to fit within Jane's authority ($100K threshold)?
3. Do we have enough MEDDPICC validation to forecast this deal accurately?
```

**Example (Forecast Review)**:
```
## Meeting Purpose

Q4 forecast review - AcmeCorp showing as "Commit" at $144K closing Nov 30.
Validate forecast accuracy and identify risks.

**Decisions Needed**:
1. Is this deal qualified to Commit category or should it be downgraded to Best Case?
2. What's our risk mitigation plan if CFO engagement doesn't happen this week?
3. Are there other stakeholders we should engage as fallback?
```

### Deal Summary Section

**Purpose**: Quick context for attendees who may not know deal intimately

**Structure**:
```
## Deal Summary

**Customer**: {Company name, industry, size}
**Opportunity**: {ACV, term, product/plan}
**Stage**: {Current stage}
**Forecast Category**: {Pipeline | Best Case | Commit | Closed}
**Close Date**: {Forecasted close date}

**Business Problem**: {1-2 sentence customer pain point}

**Recent Activity**:
- {Date}: {Event or interaction}
- {Date}: {Event or interaction}
- {Date}: {Event or interaction}
```

**Example**:
```
## Deal Summary

**Customer**: AcmeCorp, manufacturing, 5000 employees
**Opportunity**: $144K ACV, 12-month term, Enterprise plan (50 users)
**Stage**: Proposal
**Forecast Category**: Commit
**Close Date**: Nov 30, 2025

**Business Problem**: Finance team spending $500K/year on manual reporting, board
demanding real-time dashboards, need solution by Jan 15 for Q1 reporting cycle.

**Recent Activity**:
- Nov 12: Discovery call with Jane Smith (VP Ops) - identified pain, budget approved
- Nov 13: Demo with Jane + IT team - positive reception, technical validation underway
- Nov 14: Proposal sent ($144K ACV) - Jane verbally approved pricing
- Nov 18: Stalled - Jane revealed she needs CFO approval >$100K, CFO not yet engaged
```

### MEDDPICC Assessment Section

**Purpose**: Evaluate deal qualification and identify gaps

**Structure** (use if MEDDPICC methodology):
```
## MEDDPICC Assessment

| Element | Status | Notes | Risk |
|---------|--------|-------|------|
| **Metrics** | {Red/Yellow/Green} | {Business case summary} | {Gap or risk} |
| **Economic Buyer** | {Red/Yellow/Green} | {Who, engaged or not} | {Gap or risk} |
| **Decision Criteria** | {Red/Yellow/Green} | {Requirements status} | {Gap or risk} |
| **Decision Process** | {Red/Yellow/Green} | {Timeline, approvals} | {Gap or risk} |
| **Paper Process** | {Red/Yellow/Green} | {Legal, procurement} | {Gap or risk} |
| **Identify Pain** | {Red/Yellow/Green} | {Pain validation} | {Gap or risk} |
| **Champion** | {Red/Yellow/Green} | {Who, strength} | {Gap or risk} |
| **Competition** | {Red/Yellow/Green} | {Competitive landscape} | {Gap or risk} |
```

**Example**:
```
## MEDDPICC Assessment

| Element | Status | Notes | Risk |
|---------|--------|-------|------|
| **Metrics** | Green | $300K savings, 9-month payback validated | Low risk |
| **Economic Buyer** | Red | Carol (CFO) identified but NOT engaged | HIGH RISK - blocker |
| **Decision Criteria** | Green | Technical requirements validated by IT | Low risk |
| **Decision Process** | Yellow | Timeline clear (Nov 30), approval process unclear | Need CFO approval path |
| **Paper Process** | Yellow | Standard contract, no red flags raised | Unvalidated |
| **Identify Pain** | Green | $500K manual cost, board pressure confirmed | Low risk |
| **Champion** | Yellow | Jane (VP Ops) supportive but limited authority | Champion lacks power |
| **Competition** | Yellow | Status quo, evaluated Competitor X (rejected) | Could revert to status quo |

**Overall Assessment**: Deal at risk due to Economic Buyer gap. Champion strong but
lacks authority. Need CFO engagement within 5 days to hit Nov 30 close.
```

**Color Coding**:
- **Green**: Fully validated, low risk
- **Yellow**: Partially validated, medium risk, needs attention
- **Red**: Not validated or identified as blocker, high risk

### Discussion Topics Section

**Purpose**: Structured agenda for meeting flow

**Structure**:
```
## Discussion Topics

| Time | Topic | Owner | Outcome Needed |
|------|-------|-------|----------------|
| {time} | {topic} | {who leads} | {decision or action} |
| {time} | {topic} | {who leads} | {decision or action} |
```

**Example (Strategy Session)**:
```
## Discussion Topics

| Time | Duration | Topic | Owner | Outcome Needed |
|------|----------|-------|-------|----------------|
| 2:00 | 10 min | Deal summary & MEDDPICC review | Sarah | Alignment on current status |
| 2:10 | 15 min | CFO engagement strategy | All | Decide: Jane intro, direct outreach, or exec-to-exec |
| 2:25 | 10 min | Deal sizing options | Lisa | Evaluate: Can we restructure to fit Jane's authority? |
| 2:35 | 10 min | Competitive positioning | Tom | Assess: Are we at risk of losing to status quo? |
| 2:45 | 10 min | Forecast accuracy assessment | Mike | Decide: Commit vs Best Case categorization |
| 2:55 | 5 min | Action items & next steps | Sarah | Clear owners and deadlines |
```

**Best Practices**:
- Timebox discussions (prevents rambling)
- Assign topic owners (who drives that segment)
- Define outcomes (decision, action plan, or assessment)
- Put critical topics early (highest energy/focus)

### Strategic Questions Section

**Purpose**: Frame key questions to answer during meeting

**Structure**:
```
## Strategic Questions

**Deal Advancement**:
- {Question about moving deal forward}
- {Question about stakeholder engagement}

**Risk Mitigation**:
- {Question about deal risks}
- {Question about competitive threats}

**Forecast Accuracy**:
- {Question about qualification}
- {Question about timeline}
```

**Example**:
```
## Strategic Questions

**Deal Advancement**:
- How do we get Carol (CFO) engaged without undermining Jane (our champion)?
- Should Mike (our VP Sales) reach out exec-to-exec to Carol, or does that signal desperation?
- Is there a different Economic Buyer we should target (CEO, COO)?

**Risk Mitigation**:
- What's our fallback if Carol doesn't engage before Nov 30?
- Could we lose this deal to status quo if timeline slips?
- Is Competitor X still in play, or have they definitively chosen us?

**Forecast Accuracy**:
- Do we have enough MEDDPICC validation to keep this as "Commit" forecast?
- Should we push close date to December to allow time for CFO engagement?
- What would need to happen in next 5 days to confidently forecast Nov 30 close?
```

### Options & Recommendations Section

**Purpose**: Present strategic options with pros/cons for decision

**Structure**:
```
## Options & Recommendations

### Option 1: {Strategy name}
**Approach**: {What we'd do}
**Pros**: {Benefits}
**Cons**: {Risks or downsides}

### Option 2: {Strategy name}
**Approach**: {What we'd do}
**Pros**: {Benefits}
**Cons**: {Risks or downsides}

### Recommendation
{Which option, why, what success looks like}
```

**Example**:
```
## Options & Recommendations

### Option 1: Champion-Led CFO Introduction
**Approach**: Ask Jane to introduce us to Carol, position as "final approval conversation"
**Pros**: Respects Jane's relationship, doesn't bypass her, builds on champion strength
**Cons**: Jane may delay (protects her turf), we lose control of messaging, slower

### Option 2: Direct Executive Summary Email
**Approach**: Sarah sends executive summary email directly to Carol, CC Jane
**Pros**: Faster, we control messaging, demonstrates urgency
**Cons**: Could undercut Jane's authority, Carol may ignore cold email, political risk

### Option 3: Executive-to-Executive Outreach
**Approach**: Mike (VP Sales) reaches out to Carol (CFO) peer-to-peer
**Pros**: Executive-level engagement signals strategic importance, hard to ignore
**Cons**: Could signal desperation, may annoy Jane, expensive exec time for uncertain outcome

### Recommendation
**Hybrid approach**: Sarah sends executive summary email to Carol (Option 2) WITH Jane's
explicit permission and framing ("Jane suggested I send you a summary..."). This respects
Jane while creating urgency. If no response in 48 hours, Mike does exec-to-exec outreach
(Option 3) as escalation. Target: CFO call scheduled by Nov 23.
```

### Action Items Section

**Purpose**: Document decisions and next steps with owners

**Structure**:
```
## Action Items

{To be completed during meeting - leave blank template}

**Decisions Made**:
- {Decision 1}
- {Decision 2}

**Next Steps**:
1. {Action item} - Owner: {name}, Due: {date}
2. {Action item} - Owner: {name}, Due: {date}
3. {Action item} - Owner: {name}, Due: {date}

**Follow-Up Meeting**: {If needed, when}
```

**Example** (filled in after meeting):
```
## Action Items

**Decisions Made**:
- Proceed with hybrid CFO engagement strategy (champion intro + direct email)
- Keep deal at "Commit" forecast but flag high risk due to Economic Buyer gap
- Push close date to Dec 7 if Carol meeting doesn't happen by Nov 23

**Next Steps**:
1. Sarah gets Jane's permission to email Carol, drafts executive summary - Due: Nov 20 EOD
2. Sarah sends executive summary to Carol (CC Jane) - Due: Nov 21 morning
3. If no Carol response by Nov 23, Mike does exec-to-exec outreach - Due: Nov 23
4. Tom prepares detailed ROI model for CFO conversation - Due: Nov 22
5. Lisa researches deal sizing options <$100K if CFO strategy fails - Due: Nov 25

**Follow-Up Meeting**: Monday Nov 27 - Assess CFO engagement results, finalize forecast
```

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/agenda_internal
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
meeting_type: {strategy|forecast|account_planning|post_mortem}
meeting_date: {YYYY-MM-DD}
internal_attendees: [{team_member_names}]
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
  - sample-data/Runtime/_Shared/knowledge/methodologies/{METHOD}/stage_inventory__{METHOD}.md  # if loaded
---
```

### 2. Compose Document

Follow structure above with actual content from deal.md

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/agenda_internal_{MEETING_TYPE}_{DATE}.md`

**Filename format**: `agenda_internal_strategy_2025-11-20.md`

---

## Error Handling

**Missing MEDDPICC fields**:
- Omit MEDDPICC Assessment section
- Use generic deal qualification questions

**Missing recent History**:
- Use stage as proxy for status
- Flag in meeting purpose: "Need to document recent activity"

**Missing D1/D7 tasks**:
- Generic strategic questions based on stage
- Prompt team to identify blockers during meeting

**Missing methodology**:
- Use generic B2B deal review framework
- Focus on stakeholders, timeline, competition, risks

---

## Internal Agenda Best Practices

### When to Hold Internal Strategy Sessions

**Right time**:
- Deal stalled >2 weeks with no clear path forward
- Major blocker identified (Economic Buyer gap, competitive threat)
- Forecast accuracy questioned (upgrade to Commit or downgrade to Best Case)
- Complex stakeholder dynamics need mapping
- Lost deal post-mortem (learn from failures)

**Wrong time**:
- Deal progressing normally (don't over-meet)
- Simple questions that can be answered via Slack/email
- No new information since last review

### Meeting Formats by Type

**Strategy Session (60 min)**:
- Purpose: Unblock stalled deal, align on approach
- Attendees: AE, manager, SE if technical blocker, Sales Ops if process issue
- Outcome: Decision on strategy, action plan with owners

**Forecast Review (30 min)**:
- Purpose: Validate forecast accuracy, assess risk
- Attendees: AE, manager, Sales Ops
- Outcome: Forecast category (Pipeline/Best Case/Commit), risk mitigation plan

**Account Planning (90 min)**:
- Purpose: Map complex account, identify expansion opportunities
- Attendees: AE, CSM, manager, SE
- Outcome: Account map, expansion plan, stakeholder engagement strategy

**Post-Mortem (45 min)**:
- Purpose: Learn from won/lost deals
- Attendees: AE, manager, SE, anyone involved in deal
- Outcome: Lessons learned, process improvements

### Documentation & Follow-Up

**During meeting**:
- Designate note-taker (not AE leading discussion)
- Document decisions in real-time
- Assign owners and deadlines for every action

**After meeting**:
- AE updates deal.md with decisions and action items
- Send meeting summary email within 24 hours
- Schedule follow-up if needed

---

## Example Output

```markdown
---
generated_by: sales-communications/agenda_internal
generated_on: 2025-11-19T14:00:00Z
deal_id: AcmeCorp
meeting_type: strategy
meeting_date: 2025-11-20
internal_attendees: [Sarah Chen, Mike Sullivan, Tom Rodriguez, Lisa Park]
sources:
  - sample-data/Runtime/Sessions/AcmeCorp/deal.md
  - sample-data/Runtime/_Shared/knowledge/methodologies/MEDDPICC/stage_inventory__MEDDPICC.md
---

# Internal Meeting Agenda: Deal Strategy Session

**Deal**: AcmeCorp
**Meeting Type**: Strategy Session
**Date**: Monday, November 20, 2025
**Time**: 2:00 PM ET
**Duration**: 60 minutes
**Attendees**: Sarah Chen (AE), Mike Sullivan (VP Sales), Tom Rodriguez (SE), Lisa Park (Sales Ops)

---

## Meeting Purpose

AcmeCorp deal stalled at $144K ACV - champion (Jane, VP Ops) engaged but CFO (Carol)
not yet involved, and Jane doesn't have budget authority >$100K. We need a strategy
to engage the Economic Buyer before end of quarter.

**Decisions Needed**:
1. How do we get a meeting with Carol (CFO) - through Jane, direct outreach, or exec-to-exec?
2. Should we adjust deal size/structure to fit within Jane's authority ($100K threshold)?
3. Do we have enough MEDDPICC validation to forecast this deal accurately?

---

## Deal Summary

**Customer**: AcmeCorp, manufacturing, 5000 employees
**Opportunity**: $144K ACV, 12-month term, Enterprise plan (50 users)
**Stage**: Proposal
**Forecast Category**: Commit
**Close Date**: Nov 30, 2025

**Business Problem**: Finance team spending $500K/year on manual reporting, board
demanding real-time dashboards, need solution by Jan 15 for Q1 reporting cycle.

**Recent Activity**:
- Nov 12: Discovery call with Jane Smith (VP Ops) - identified pain, budget approved
- Nov 13: Demo with Jane + IT team - positive reception, technical validation underway
- Nov 14: Proposal sent ($144K ACV) - Jane verbally approved pricing
- Nov 18: Stalled - Jane revealed she needs CFO approval >$100K, CFO not yet engaged

---

## MEDDPICC Assessment

| Element | Status | Notes | Risk |
|---------|--------|-------|------|
| **Metrics** | Green | $300K savings, 9-month payback validated | Low risk |
| **Economic Buyer** | Red | Carol (CFO) identified but NOT engaged | HIGH RISK - blocker |
| **Decision Criteria** | Green | Technical requirements validated by IT | Low risk |
| **Decision Process** | Yellow | Timeline clear (Nov 30), approval process unclear | Need CFO approval path |
| **Paper Process** | Yellow | Standard contract, no red flags raised | Unvalidated |
| **Identify Pain** | Green | $500K manual cost, board pressure confirmed | Low risk |
| **Champion** | Yellow | Jane (VP Ops) supportive but limited authority | Champion lacks power |
| **Competition** | Yellow | Status quo, evaluated Competitor X (rejected) | Could revert to status quo |

**Overall Assessment**: Deal at risk due to Economic Buyer gap. Champion strong but
lacks authority. Need CFO engagement within 5 days to hit Nov 30 close.

---

## Discussion Topics

| Time | Duration | Topic | Owner | Outcome Needed |
|------|----------|-------|-------|----------------|
| 2:00 | 10 min | Deal summary & MEDDPICC review | Sarah | Alignment on current status |
| 2:10 | 15 min | CFO engagement strategy | All | Decide: Jane intro, direct outreach, or exec-to-exec |
| 2:25 | 10 min | Deal sizing options | Lisa | Evaluate: Can we restructure to fit Jane's authority? |
| 2:35 | 10 min | Competitive positioning | Tom | Assess: Are we at risk of losing to status quo? |
| 2:45 | 10 min | Forecast accuracy assessment | Mike | Decide: Commit vs Best Case categorization |
| 2:55 | 5 min | Action items & next steps | Sarah | Clear owners and deadlines |

---

## Strategic Questions

**Deal Advancement**:
- How do we get Carol (CFO) engaged without undermining Jane (our champion)?
- Should Mike (our VP Sales) reach out exec-to-exec to Carol, or does that signal desperation?
- Is there a different Economic Buyer we should target (CEO, COO)?

**Risk Mitigation**:
- What's our fallback if Carol doesn't engage before Nov 30?
- Could we lose this deal to status quo if timeline slips?
- Is Competitor X still in play, or have they definitively chosen us?

**Forecast Accuracy**:
- Do we have enough MEDDPICC validation to keep this as "Commit" forecast?
- Should we push close date to December to allow time for CFO engagement?
- What would need to happen in next 5 days to confidently forecast Nov 30 close?

---

## Options & Recommendations

### Option 1: Champion-Led CFO Introduction
**Approach**: Ask Jane to introduce us to Carol, position as "final approval conversation"
**Pros**: Respects Jane's relationship, doesn't bypass her, builds on champion strength
**Cons**: Jane may delay (protects her turf), we lose control of messaging, slower

### Option 2: Direct Executive Summary Email
**Approach**: Sarah sends executive summary email directly to Carol, CC Jane
**Pros**: Faster, we control messaging, demonstrates urgency
**Cons**: Could undercut Jane's authority, Carol may ignore cold email, political risk

### Option 3: Executive-to-Executive Outreach
**Approach**: Mike (VP Sales) reaches out to Carol (CFO) peer-to-peer
**Pros**: Executive-level engagement signals strategic importance, hard to ignore
**Cons**: Could signal desperation, may annoy Jane, expensive exec time for uncertain outcome

### Recommendation
**Hybrid approach**: Sarah sends executive summary email to Carol (Option 2) WITH Jane's
explicit permission and framing ("Jane suggested I send you a summary..."). This respects
Jane while creating urgency. If no response in 48 hours, Mike does exec-to-exec outreach
(Option 3) as escalation. Target: CFO call scheduled by Nov 23.

---

## Action Items

{To be completed during meeting}

**Decisions Made**:
-
-

**Next Steps**:
1. {Action} - Owner: {Name}, Due: {Date}
2. {Action} - Owner: {Name}, Due: {Date}

**Follow-Up Meeting**: {If needed}

---

**Prepared by**: Sarah Chen
**Document Date**: November 19, 2025
```

---

**End of Pattern: agenda_internal**
