# Document: Sales Team Briefing

**Pattern**: briefing_team
**Type**: Internal-facing document
**Timing**: Weekly or when team needs deal context
**Purpose**: Provide comprehensive deal overview for sales team collaboration

---

## When to Use

Create this briefing for internal sales team when:
- Handing off deal to another AE (territory change, account reassignment)
- Bringing in overlay specialist (enterprise AE, industry specialist)
- Manager needs detailed deal context for coaching or escalation
- Multi-threading requires multiple AEs coordinating on same account
- Deal review meetings where team needs full context

**Trigger Phrases**:
- "Draft team briefing for {DEAL}"
- "Create deal handoff document for {DEAL}"
- "Prepare sales team briefing"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Complete deal history and current status
   - Full MEDDPICC assessment (all fields)
   - Stakeholder landscape with roles and dynamics
   - D1/D7 tasks and current blockers
3. **NOTE**: Do NOT load email style corpus (not applicable for documents)

**OPTIONAL**:
- Brand guidelines (for internal document formatting)
- Methodology stage inventory (for methodology-specific assessment)

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract comprehensive information from deal.md:
- **Deal basics**: Company, industry, size, opportunity value, stage, forecasted close
- **Complete History**: All customer interactions chronologically
- **Full MEDDPICC assessment**: Every field with current status
- **Stakeholder map**: All contacts with roles, influence, sentiment
- **D1 tasks**: Strategic blockers and long-term initiatives
- **D7 tasks**: Tactical next steps and near-term actions
- **Competition**: Competitive landscape and positioning
- **Deal timeline**: Key milestones and decision dates

**This is the MOST comprehensive pattern** - includes everything from deal.md

### 2. Load Brand Guidelines (Section 2 of _common.md)

If brand_guidelines.md exists with internal document standards, apply formatting

### 3. Load Methodology Guidance (Section 4 of _common.md)

If MEDDPICC stage inventory available:
- Reference methodology framework throughout briefing
- Include stage-specific coaching and best practices
- Highlight methodology gaps or risks

---

## Document Structure

### Cover Section

**Structure**:
```
# Sales Team Briefing: {Customer Company Name}

**Deal ID**: {Customer name}
**Prepared By**: {AE name}
**Date**: {Date}
**Opportunity Value**: {ACV, term}
**Stage**: {Current stage}
**Forecast Category**: {Pipeline | Best Case | Commit | Closed}
**Close Date**: {Forecasted close date}

---

**Executive Summary** (2-3 sentences):
{High-level deal status - where it stands, what's needed to close, key risks}
```

**Example**:
```
# Sales Team Briefing: AcmeCorp

**Deal ID**: AcmeCorp
**Prepared By**: Sarah Chen
**Date**: November 20, 2025
**Opportunity Value**: $144K ACV, 12-month term, Enterprise plan
**Stage**: Proposal
**Forecast Category**: Best Case (downgraded from Commit due to Economic Buyer risk)
**Close Date**: December 7, 2025 (pushed from Nov 30)

---

**Executive Summary**:
AcmeCorp finance team needs real-time reporting to replace $500K/year manual process.
Technical validation complete, proposal sent and approved by champion (VP Ops), but
Economic Buyer (CFO) not yet engaged - this is primary blocker. Need CFO meeting by
Nov 25 to hit Dec 7 close.
```

### Customer Profile Section

**Purpose**: Provide context on company and business environment

**Structure**:
```
## Customer Profile

**Company**: {Name}
**Industry**: {Industry vertical}
**Size**: {Employees, revenue if known}
**Location**: {HQ and relevant offices}
**Website**: {URL}

**Business Context**:
{1-2 paragraphs on their business, market position, challenges}

**Why Now**:
{What's driving urgency - budget cycle, compliance deadline, competitive pressure, board mandate}
```

**Example**:
```
## Customer Profile

**Company**: AcmeCorp Manufacturing
**Industry**: Industrial Manufacturing
**Size**: 5000 employees, ~$2B annual revenue
**Location**: HQ in Chicago, IL; manufacturing plants in 6 US states
**Website**: www.acmecorp.com

**Business Context**:
AcmeCorp is a mid-market manufacturer serving automotive and aerospace sectors. They've
grown through acquisition (3 companies in last 5 years), resulting in fragmented systems
and manual reporting processes. Finance team struggling to consolidate data from legacy
systems across acquired entities. Board demanding better visibility into unit economics
and profitability by division.

**Why Now**:
- Board mandated real-time financial reporting for Q1 2026 (Jan 15 deadline)
- New CFO (Carol Martinez) hired 6 months ago, chartered with modernizing finance operations
- Budget approved for Q4 FY25 spend ($500K allocation for reporting/analytics)
- SOX audit findings (Nov 2025) flagged compliance risks in manual processes
```

### Stakeholder Map Section

**Purpose**: Comprehensive view of buying committee with relationships and dynamics

**Structure**:
```
## Stakeholder Map

### Economic Buyer
**{Name}, {Title}**
- **Authority**: {Budget level, decision scope}
- **Priorities**: {What they care about}
- **Engagement Status**: {Engaged/Not Engaged, last contact}
- **Sentiment**: {Supportive/Neutral/Skeptical}
- **Strategy**: {How we're engaging or plan to engage}

### Champion
**{Name}, {Title}**
- **Relationship Strength**: {Strong/Medium/Weak}
- **Influence**: {High/Medium/Low with Economic Buyer}
- **Motivation**: {Why they're advocating for us}
- **Engagement**: {Frequency and quality of interactions}
- **Risk**: {Could they become blocker or lose political capital}

### Technical Evaluators
**{Name}, {Title}**
- **Role in Decision**: {Technical validation, security review, etc.}
- **Sentiment**: {Supportive/Neutral/Skeptical}
- **Concerns**: {Technical objections or requirements}
- **Status**: {Validation complete, in progress, blocked}

### Influencers
**{Name}, {Title}**
- **Role**: {Advisor, end-user, consultant}
- **Influence**: {How they impact decision}
- **Sentiment**: {Supportive/Neutral/Opposed}

### Blockers (if any)
**{Name}, {Title}**
- **Opposition Reason**: {Why they're blocking}
- **Mitigation Strategy**: {How we're addressing}
```

**Example**:
```
## Stakeholder Map

### Economic Buyer
**Carol Martinez, CFO**
- **Authority**: Final approval on all investments >$100K, reports to CEO
- **Priorities**: Cost reduction, ROI, risk mitigation, operational efficiency
- **Engagement Status**: NOT ENGAGED - Identified but no contact yet (PRIMARY RISK)
- **Sentiment**: Unknown (no interaction)
- **Strategy**: Exec summary email Nov 21, exec-to-exec outreach from our VP Sales if needed

### Champion
**Jane Smith, VP of Operations**
- **Relationship Strength**: Strong - 5 interactions, responsive, advocates internally
- **Influence**: Medium with CFO - reports to CFO, but new in role (6 months), limited authority
- **Motivation**: Reduce team overhead (her team does manual work), improve board reporting
- **Engagement**: Weekly contact, last call Nov 18, next call Nov 22
- **Risk**: Limited budget authority ($100K threshold) weakens her champion power

### Technical Evaluators
**Michael Chen, Director of IT**
- **Role in Decision**: Technical architecture approval, security/compliance validation
- **Sentiment**: Cautiously Supportive - Initially skeptical, now signed off on architecture
- **Concerns**: SSO integration (resolved), data retention policies (addressed)
- **Status**: Technical validation COMPLETE - Green light to proceed (Nov 16)

**Sarah Park, Senior Data Analyst**
- **Role in Decision**: End-user validation, ease-of-use assessment
- **Sentiment**: Very Supportive - Excited about dashboard features
- **Concerns**: Training requirements (addressed - 30min onboarding)
- **Status**: Actively testing trial environment, positive feedback

### Influencers
**David Kumar, Finance Manager**
- **Role**: Reports to Jane, manages team doing manual work (key beneficiary)
- **Influence**: Jane trusts his operational input
- **Sentiment**: Supportive - Frustrated with current manual process
```

### MEDDPICC Assessment Section

**Purpose**: Detailed methodology evaluation with evidence

**Structure**:
```
## MEDDPICC Assessment

### Metrics
**Status**: {Green/Yellow/Red}

**Business Case**:
- Current cost: {$}
- Target savings: {$}
- ROI: {%}, Payback: {months}

**Evidence**:
{Where metrics came from - customer shared, AE calculated, inferred}

**Validation**:
{Has customer confirmed these numbers? Economic Buyer bought in?}

**Risk**: {Gaps or concerns}

---

{Repeat for each MEDDPICC element: Economic Buyer, Decision Criteria, Decision Process,
Paper Process, Identify Pain, Champion, Competition}
```

**Example** (abbreviated):
```
## MEDDPICC Assessment

### Metrics
**Status**: Green

**Business Case**:
- Current cost: $500K/year (15 FTEs x 50 hrs/month x $40/hr loaded)
- Target savings: $300K/year (60% reduction)
- ROI: 208% over 3 years, Payback: 9 months

**Evidence**:
Jane (VP Ops) shared FTE count and time allocation in discovery call (Nov 12).
Sarah (Data Analyst) confirmed hours/month in demo (Nov 13). AE calculated loaded
cost using industry standard.

**Validation**:
Champion (Jane) confirmed savings calculation. Economic Buyer (Carol CFO) NOT yet
validated - this is a risk.

**Risk**: CFO may challenge savings assumptions. Need to validate with Carol before
final approval.

---

### Economic Buyer
**Status**: Red

**Identified**: Carol Martinez, CFO - Final authority on investments >$100K

**Engagement**: NOT ENGAGED - Zero contact to date

**Authority Validation**: Jane confirmed Carol must approve (Nov 18 call)

**Priorities**: Unknown (not engaged), assume CFO priorities: ROI, cost reduction, risk

**Risk**: HIGH RISK - Cannot close without Economic Buyer engagement. No relationship,
no validation of business case from decision-maker.

**Mitigation Plan**:
- Nov 21: Sarah sends executive summary email to Carol (with Jane's permission)
- Nov 23: If no response, our VP Sales (Mike) does exec-to-exec outreach
- Target: CFO call scheduled by Nov 25

---

{Continue for all 8 MEDDPICC elements...}
```

### Deal History Section

**Purpose**: Chronological narrative of all customer interactions

**Structure**:
```
## Deal History

### {Date} - {Event Type}
**Attendees**: {Who from customer, who from our team}
**Topics**: {What was discussed}
**Outcomes**: {Decisions, next steps, key takeaways}
**Sentiment**: {How customer reacted - positive, neutral, concerns}

{Repeat chronologically for all History entries}
```

**Example**:
```
## Deal History

### 2025-11-12 - Discovery Call
**Attendees**: Jane Smith (VP Ops), Sarah Chen (our AE)
**Topics**: Current manual reporting process, pain points, requirements, timeline
**Outcomes**:
- Identified $500K annual cost in manual work (15 FTEs)
- Confirmed budget approved ($500K allocation Q4 FY25)
- Timeline: Need solution operational by Jan 15, 2026 for Q1 board reporting
- Next: Product demo scheduled Nov 13
**Sentiment**: Very positive - Jane frustrated with status quo, motivated to change

### 2025-11-13 - Product Demo
**Attendees**: Jane Smith, Michael Chen (Dir IT), Sarah Park (Data Analyst), Sarah Chen, Tom Rodriguez (our SE)
**Topics**: Salesforce integration, dashboard templates, mobile access, drill-down analytics
**Outcomes**:
- Showed 5-minute API setup (addressed Jane's "easy integration" requirement)
- Michael raised SSO concerns (we addressed with SAML 2.0 support)
- Sarah (analyst) excited about dashboard templates
- Next: Technical deep-dive, proposal
**Sentiment**: Positive overall, Michael cautious (IT gatekeeper), Jane and Sarah enthusiastic

### 2025-11-14 - Proposal Sent
**Attendees**: Email to Jane
**Topics**: Pricing, terms, SOW
**Outcomes**:
- Sent Enterprise plan proposal: $144K ACV, 12-month term, 50 users
- Jane verbally approved pricing same day (email reply)
- Next: Technical validation, then exec approval
**Sentiment**: Positive - "Pricing works for our budget" (Jane quote)

### 2025-11-16 - Technical Deep-Dive
**Attendees**: Michael Chen, Sarah Park, Tom Rodriguez (our SE), Sarah Chen
**Topics**: SSO integration, custom field mapping, data security, retention policies
**Outcomes**:
- Michael validated SSO approach (SAML 2.0 with Azure AD)
- Reviewed custom field mapping (10 custom objects to sync)
- Confirmed data encryption and retention (meets compliance requirements)
- Michael gave technical signoff: "Architecture meets our requirements"
**Sentiment**: Positive - Michael's concerns resolved, gave green light

### 2025-11-18 - Check-In Call with Jane
**Attendees**: Jane Smith, Sarah Chen
**Topics**: Status update, next steps
**Outcomes**:
- Jane revealed she needs CFO (Carol) approval for >$100K investments
- Carol not yet engaged (Jane hasn't briefed her)
- Jane committed to intro us to Carol, but timeline unclear
- Decision: Sarah will send exec summary directly to Carol (with Jane's permission)
**Sentiment**: Still positive but revealed blocker - Jane's authority limitation
```

### Current Status & Next Steps Section

**Purpose**: Clear snapshot of where deal stands and what happens next

**Structure**:
```
## Current Status

**Stage**: {Current stage}
**Forecast Category**: {Pipeline/Best Case/Commit}
**Close Date**: {Date}

**What's Complete**:
- {Milestone or validation}
- {Milestone or validation}

**What's Pending**:
- {Open item or blocker}
- {Open item or blocker}

**Primary Blocker**: {Biggest obstacle to closing}

---

## Next Steps

### D1 Tasks (Strategic)
- [ ] {Strategic task} - Owner: {name}, Due: {date}
- [ ] {Strategic task} - Owner: {name}, Due: {date}

### D7 Tasks (Tactical)
- [ ] {Tactical task} - Owner: {name}, Due: {date}
- [ ] {Tactical task} - Owner: {name}, Due: {date}

**Critical Path to Close**:
1. {Milestone 1} by {date}
2. {Milestone 2} by {date}
3. {Milestone 3 (close)} by {date}
```

**Example**:
```
## Current Status

**Stage**: Proposal
**Forecast Category**: Best Case (downgraded from Commit on Nov 19 due to EB risk)
**Close Date**: December 7, 2025

**What's Complete**:
- Discovery (Nov 12) - Pain, requirements, budget validated
- Demo (Nov 13) - Solution fit confirmed
- Proposal sent (Nov 14) - Pricing approved by champion
- Technical validation (Nov 16) - IT signoff received

**What's Pending**:
- Economic Buyer (CFO) engagement - NOT STARTED
- Legal/procurement review - NOT STARTED (waiting for EB approval)
- Contract negotiation - NOT STARTED

**Primary Blocker**: Carol Martinez (CFO) not engaged. Cannot close without her approval.

---

## Next Steps

### D1 Tasks (Strategic)
- [ ] Get CFO (Carol) meeting scheduled - Owner: Sarah, Due: Nov 25
- [ ] Validate business case with Economic Buyer - Owner: Sarah, Due: Nov 30
- [ ] Identify backup Economic Buyer if Carol blocks - Owner: Sarah + Mike, Due: Nov 27

### D7 Tasks (Tactical)
- [ ] Send executive summary email to Carol - Owner: Sarah, Due: Nov 21
- [ ] Prep detailed ROI model for CFO conversation - Owner: Tom, Due: Nov 22
- [ ] Follow up with Jane on Carol intro - Owner: Sarah, Due: Nov 22
- [ ] If no Carol response, exec-to-exec outreach (Mike to Carol) - Owner: Mike, Due: Nov 23

**Critical Path to Close**:
1. CFO call scheduled by Nov 25
2. CFO approval received by Nov 30
3. Contract sent and negotiated by Dec 5
4. Signature by Dec 7
```

### Competitive Landscape Section

**Purpose**: Understand competitive dynamics and positioning

**Structure**:
```
## Competitive Landscape

**Primary Competition**: {Vendor, status quo, build in-house}

**Competitive Situation**:
{What customer is evaluating, who's in/out, where we stand}

**Our Differentiation**:
- {Key differentiator 1}
- {Key differentiator 2}

**Competitor Weaknesses**:
- {Weakness we can exploit}
- {Weakness we can exploit}

**Risks**:
{Competitive threats or customer reverting to status quo}
```

**Example**:
```
## Competitive Landscape

**Primary Competition**: Status quo (manual process), Competitor X (evaluated, rejected)

**Competitive Situation**:
- Customer evaluated Competitor X in Oct 2025 (before we engaged)
- Competitor X rejected due to price ($250K ACV, too expensive per Jane)
- Current competition is STATUS QUO (do nothing, keep manual process)
- Risk: If timeline slips or CFO doesn't approve, they may delay to next budget cycle

**Our Differentiation vs Status Quo**:
- $300K annual savings (compelling ROI vs manual process cost)
- Jan 15 deadline creates urgency (board mandate for real-time reporting)
- Low implementation risk (30-day setup vs months to hire/build team)

**Our Differentiation vs Competitor X**:
- 42% lower price ($144K vs $250K ACV)
- Faster implementation (30 days vs 90 days per their proposal)
- Better Salesforce integration (native vs middleware)

**Risks**:
- Status quo bias if urgency fades (board mandate could be pushed)
- CFO may delay decision to next budget cycle (risk if we don't engage her soon)
- Competitor X could come back with discount if we stall
```

### Handoff Notes Section (if applicable)

**Purpose**: Specific guidance for AE taking over deal

**Structure**:
```
## Handoff Notes

**Reason for Handoff**: {Territory change, specialty overlay, escalation}

**Key Relationships**:
- {Stakeholder name}: {Relationship strength, communication tips}
- {Stakeholder name}: {Relationship strength, communication tips}

**What's Been Promised**:
- {Commitment made to customer}
- {Timeline or deliverable promised}

**Landmines to Avoid**:
- {Topic or approach that caused issues}
- {Stakeholder sensitivity or political issue}

**Recommended Next Steps**:
{Specific advice on how to advance deal}
```

**Example**:
```
## Handoff Notes

**Reason for Handoff**: Sarah (current AE) moving to Enterprise segment, deal reassigned
to Jordan (Mid-Market AE) effective Nov 25.

**Key Relationships**:
- Jane Smith (Champion): Strong relationship, very responsive, casual communication style.
  She prefers brief emails and Zoom calls over phone. Usually replies within 2 hours.
- Michael Chen (IT): Was skeptical initially, took time to build trust. Appreciate his
  risk-averse nature, provide detailed technical docs, don't overpromise.
- Carol Martinez (CFO): Not yet engaged - this is your top priority.

**What's Been Promised**:
- 30-day implementation timeline (Nov 16 tech validation)
- $300K annual savings (validated with Jane, NOT yet with Carol)
- Jan 15 go-live date (committed to support their Q1 board reporting)
- Tom (our SE) will lead implementation (Jane specifically requested him)

**Landmines to Avoid**:
- Don't bypass Jane to get to Carol (tried this Oct with another deal, damaged relationship)
- Don't mention "custom development" (Michael hates custom work, sees as risk)
- Don't negotiate price (Jane already approved $144K, reopening could kill deal)

**Recommended Next Steps**:
1. Intro call with Jane (you + Sarah) to transfer relationship - Nov 26
2. Send exec summary to Carol immediately after Jane intro - Nov 27
3. Push for CFO call by Dec 2 (gives you time to build rapport)
4. Close by Dec 15 (safer than Dec 7 given handoff)
```

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/briefing_team
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
briefing_type: {handoff|collaboration|review}
prepared_for: [{recipient_names}]
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
  - sample-data/Runtime/_Shared/knowledge/methodologies/{METHOD}/stage_inventory__{METHOD}.md  # if loaded
---
```

### 2. Compose Document

Follow structure above with comprehensive content from deal.md

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/briefing_team_{DATE}.md`

**Filename format**: `briefing_team_2025-11-20.md`

---

## Error Handling

**Missing MEDDPICC fields**:
- Include section with "Status: Unknown" or "Not Documented"
- Flag as gap for receiving AE to investigate

**Missing stakeholder details**:
- List known stakeholders with limited info
- Note "Relationship dynamics not documented"

**Missing History**:
- Use stage as proxy: "Deal in Proposal stage, history not documented"
- Encourage receiving AE to document going forward

**Sparse deal.md**:
- Generate briefing with available data, flag gaps prominently
- Include "Data Quality" section noting what's missing

---

## Team Briefing Best Practices

### When to Create Team Briefings

**Essential for**:
- Deal handoffs (AE changes, territory realignment)
- Complex deals requiring specialist overlay
- Manager coaching or escalation support
- Multi-AE collaboration on strategic accounts

**Not needed for**:
- Simple, straightforward deals (low ACV, single stakeholder)
- Deals you're handling solo with no handoff expected

### Briefing vs Other Documents

**Team Briefing**: Comprehensive deal overview (this pattern)
- Audience: Internal AEs, managers, specialists
- Depth: Complete history, full MEDDPICC, stakeholder dynamics
- Length: 5-10 pages

**Internal Prep Email**: Tactical call prep (email_internal_prep pattern)
- Audience: Team members joining specific customer call
- Depth: Call-specific context and strategy
- Length: 1-2 pages

**Executive Briefing**: Strategic summary for execs (briefing_exec pattern)
- Audience: VPs, C-level executives
- Depth: High-level status, key risks, ask
- Length: 1-2 pages

### Maintaining Team Briefings

**When to update**:
- Major deal milestones (stage changes, new stakeholders)
- After handoffs (receiving AE adds their notes)
- Quarterly for strategic accounts

**Version control**:
- Include date in filename
- Use frontmatter to track updates
- Archive old versions (don't overwrite)

---

## Example Output

{Full example omitted for brevity - would include all sections above populated with
AcmeCorp deal data from previous examples}

---

**End of Pattern: briefing_team**
