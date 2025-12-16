# Document: Executive Briefing

**Pattern**: briefing_exec
**Type**: Internal-facing document
**Timing**: When executive involvement needed (escalation, exec-to-exec outreach, strategic deals)
**Purpose**: Provide concise deal summary for VP/C-level with clear ask and context

---

## When to Use

Create this briefing when your executives need deal context:
- Exec-to-exec outreach (your VP calling their C-level)
- Strategic deal escalation (high-value, at-risk, politically complex)
- Quarterly business reviews (exec-level deal pipeline review)
- Customer success escalations (exec sponsor engagement)
- Board-level deals (requires C-suite awareness)

**Trigger Phrases**:
- "Draft executive briefing for {DEAL}"
- "Brief exec team on {DEAL}"
- "Create VP briefing document"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - High-level deal status (stage, value, timeline)
   - Business case and strategic value
   - Why exec involvement needed (blocker, escalation reason)
   - Key stakeholders (especially Economic Buyer)
3. **NOTE**: Do NOT load email style corpus (not applicable for documents)

**OPTIONAL**:
- Brand guidelines (for internal document formatting)
- Methodology stage inventory (for qualification assessment)

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract high-level information from deal.md:
- **Deal basics**: Company, ACV, stage, close date
- **Business value**: ROI, strategic importance, competitive significance
- **Why exec needed**: Specific blocker or escalation reason
- **Economic Buyer**: Name, title, priorities (who exec will engage)
- **Current status**: What's done, what's blocked, what's at risk
- **Ask**: What you need exec to do (call, meeting, decision, resources)

**Focus on signal, not noise** - Execs need 80/20 view, not full history

### 2. Load Brand Guidelines (Section 2 of _common.md)

If brand_guidelines.md exists with executive communication standards, apply

### 3. Load Methodology Guidance (Section 4 of _common.md)

If MEDDPICC stage inventory available, use for qualification summary

---

## Document Structure

### Header Section

**Structure**:
```
# Executive Briefing: {Customer Company Name}

**Prepared For**: {Exec name(s)}
**Prepared By**: {AE name}
**Date**: {Date}
**Read Time**: {1-2 minutes}

---

**TL;DR** (1 sentence):
{Deal value, status, ask}
```

**Example**:
```
# Executive Briefing: AcmeCorp

**Prepared For**: Mike Sullivan (VP Sales)
**Prepared By**: Sarah Chen (AE)
**Date**: November 20, 2025
**Read Time**: 90 seconds

---

**TL;DR**:
$144K AcmeCorp deal blocked on Economic Buyer (CFO) engagement - need your exec-to-exec
outreach to Carol Martinez (their CFO) by Nov 23 to save Dec 7 close.
```

### The Ask Section

**Purpose**: Lead with what you need from exec (respect their time)

**Structure**:
```
## The Ask

{Clear, specific request in 1-2 sentences}

**Why You**: {Why this requires exec-level involvement, not AE}

**Timeline**: {When action needed}

**Effort**: {Time commitment - 15 min call, 1 email, 30 min meeting}
```

**Example**:
```
## The Ask

Call or email Carol Martinez (AcmeCorp CFO) to request 30-minute executive business
review with her and me before Nov 25.

**Why You**: Carol is Economic Buyer (final approval >$100K) but hasn't responded to
my executive summary email. CFO-to-CFO or VP-to-CFO outreach will get her attention
where AE outreach hasn't.

**Timeline**: Outreach needed by Nov 23 to allow time for meeting before Dec 7 close.

**Effort**: 10-minute call or 5-minute email intro, then I'll drive the rest.
```

**Best Practices**:
- Lead with the ask (don't bury it on page 2)
- Be specific (not "help with deal" - say exactly what)
- Explain why exec-level needed (justify expensive resource)
- Make it easy (draft email, talking points, minimal effort)

### Deal Summary Section

**Purpose**: Quick context on opportunity and why it matters

**Structure**:
```
## Deal Summary

**Customer**: {Company name, industry, size}
**Opportunity**: {ACV, term, products}
**Stage**: {Current stage}
**Close Date**: {Forecasted date}

**Strategic Value**:
{Why this deal matters beyond ARR - competitive win, market entry, reference customer, etc.}

**Business Case**:
{Customer's ROI or business driver in 1-2 sentences}
```

**Example**:
```
## Deal Summary

**Customer**: AcmeCorp Manufacturing, industrial sector, 5000 employees, $2B revenue
**Opportunity**: $144K ACV, 12-month term, Enterprise plan (50 users)
**Stage**: Proposal
**Close Date**: December 7, 2025

**Strategic Value**:
- First manufacturing logo in industrial sector (target vertical for 2026)
- Reference customer for automotive/aerospace market expansion
- Displaces Competitor X (they evaluated and rejected them on price)

**Business Case**:
AcmeCorp finance team spending $500K/year on manual reporting. Our solution delivers
$300K annual savings (60% reduction) with 9-month payback. New CFO chartered with
modernizing finance ops, board mandates real-time reporting by Q1 2026.
```

### Current Situation Section

**Purpose**: What's working, what's blocked, why exec help needed

**Structure**:
```
## Current Situation

**What's Working**:
- {Positive momentum indicator}
- {Validation or stakeholder support}

**The Blocker**:
{Specific obstacle preventing close - be direct}

**Why It Matters**:
{Business impact if deal slips or dies}
```

**Example**:
```
## Current Situation

**What's Working**:
- Technical validation complete - IT Director signed off on architecture (Nov 16)
- Champion (Jane Smith, VP Ops) enthusiastic, approved pricing
- Proposal sent and verbally accepted ($144K ACV, no pricing objection)
- Strong ROI ($300K savings, 9-month payback)
- Timeline urgent (Jan 15 go-live for Q1 board reporting)

**The Blocker**:
Carol Martinez (CFO) is Economic Buyer but not engaged. Jane (champion) has limited
authority ($100K threshold). I sent executive summary email to Carol on Nov 21 (CC'd
Jane) - no response after 48 hours. Cannot close without CFO approval.

**Why It Matters**:
- Dec 7 close at risk (need CFO meeting by Nov 25)
- $144K Q4 ARR slips to Q1 if we miss timeline
- Customer may revert to status quo if urgency fades (lose deal)
- Reference customer value lost (strategic target vertical)
```

### Stakeholder Context Section

**Purpose**: Who exec will engage, their priorities, political dynamics

**Structure**:
```
## Key Stakeholders

**Who You'll Engage**:
**{Name}, {Title}** - {Economic Buyer/Key Exec}
- **Priorities**: {What they care about}
- **Context**: {Relevant background}
- **Approach**: {How to engage - tone, topics, offer}

**Champion (Our Internal Advocate)**:
**{Name}, {Title}**
- {Why they're helping us, their limitations}

**Other Key Players**:
- {Name, Title, Role} - {1 sentence context}
```

**Example**:
```
## Key Stakeholders

**Who You'll Engage**:
**Carol Martinez, CFO** - Economic Buyer (final approval >$100K)
- **Priorities**: Cost reduction, ROI, financial risk mitigation (typical CFO concerns)
- **Context**: New CFO hired 6 months ago, chartered by CEO to modernize finance operations.
  She's data-driven, direct, skeptical of vendor claims (per Jane's description).
- **Approach**: Lead with ROI ($300K savings, 9-month payback), reference IT validation
  (de-risk implementation), tie to her mandate (board reporting modernization). Offer
  30-min business review to walk through financial case.

**Champion (Our Internal Advocate)**:
**Jane Smith, VP Operations**
- Reports to Carol (CFO), strong relationship with her
- Frustrated Jane can't close deal herself (limited authority), but supportive of us
- Has already briefed Carol on our solution (verbal), Carol just hasn't prioritized meeting

**Other Key Players**:
- Michael Chen, Director IT - Technical validation complete, supportive
- Sarah Park, Data Analyst - End-user, very positive on solution
```

### Suggested Talking Points Section

**Purpose**: Arm exec with key messages (make their job easy)

**Structure**:
```
## Suggested Talking Points

**Opening** (exec-to-exec rapport):
{How to introduce yourself and build credibility}

**The Business Case** (why Carol should care):
- {ROI/savings point}
- {Strategic value point}
- {Risk mitigation point}

**Social Proof** (reduce Carol's perceived risk):
- {Customer reference or case study}
- {Industry credibility}

**The Ask** (clear next step):
{What you want Carol to agree to}

**Objection Handling** (if Carol pushes back):
- **"Why should I prioritize this?"** → {Response}
- **"What's the risk?"** → {Response}
```

**Example**:
```
## Suggested Talking Points

**Opening**:
"Hi Carol, I'm Mike Sullivan, VP Sales at Example Corp. My AE Sarah has been working with
Jane and your team on the financial reporting automation initiative. Jane mentioned you're
driving finance modernization - I wanted to connect personally given the strategic nature
of this project for AcmeCorp."

**The Business Case**:
- $300K annual savings (60% reduction in manual processing costs) with 9-month payback
- Enables real-time board reporting (addresses your Q1 2026 mandate)
- Automated compliance controls address SOX audit findings from November

**Social Proof**:
- Fortune 500 healthcare company similar use case (15 FTEs → 5 FTEs, 67% cost reduction)
- 30-day average implementation (low risk, fast time-to-value)
- Your IT team (Michael Chen) already validated technical architecture

**The Ask**:
"Could we schedule 30 minutes next week - you, Jane, and Sarah - to walk through the
financial case and answer any questions? Jane's team has done great work validating
the operational fit, just want to ensure you're comfortable with the investment."

**Objection Handling**:
- **"Why should I prioritize this?"** → Jan 15 go-live required for Q1 board reporting
  (per CEO mandate). Delaying means another quarter of $125K manual processing costs.
- **"What's the risk?"** → IT validation complete (Michael signed off), 30-day
  implementation, money-back guarantee if we don't hit Jan 15 go-live.
- **"Why not wait until next budget cycle?"** → Budget approved this cycle ($500K
  allocation). Waiting means missing Q1 reporting deadline and continuing $500K/year cost.
```

### Background Section (Optional)

**Purpose**: Additional context if exec unfamiliar with customer

**Structure**:
```
## Background (Optional Detail)

**Deal History** (abbreviated):
- {Date}: {Key milestone}
- {Date}: {Key milestone}

**MEDDPICC Summary**:
- Metrics: {Business case status}
- Economic Buyer: {Engagement status}
- Champion: {Strength}
- Competition: {Landscape}
{Abbreviated, only if exec needs qualification context}
```

**Example**:
```
## Background (Optional Detail)

**Deal History**:
- Nov 12: Discovery call (identified $500K pain, budget approved)
- Nov 13: Demo (positive reception, IT and end-users)
- Nov 14: Proposal sent ($144K ACV, verbally approved by Jane)
- Nov 16: Technical validation complete (IT signoff)
- Nov 18: Blocker identified (Jane lacks authority, CFO approval needed)
- Nov 21: Executive summary sent to Carol (no response)

**MEDDPICC Summary**:
- Metrics: Green ($300K savings validated with champion)
- Economic Buyer: Red (identified but not engaged - PRIMARY BLOCKER)
- Decision Criteria: Green (IT validated)
- Decision Process: Yellow (timeline clear, approval path unclear)
- Champion: Yellow (strong but limited authority)
- Competition: Green (Competitor X rejected, status quo main risk)
```

### Success Metrics Section

**Purpose**: Define what "good" looks like after exec engagement

**Structure**:
```
## Success Metrics

**Ideal Outcome**:
{Best case scenario}

**Acceptable Outcome**:
{Minimum viable progress}

**Next Steps After Exec Engagement**:
1. {What AE does next}
2. {Timeline to close}
```

**Example**:
```
## Success Metrics

**Ideal Outcome**:
Carol agrees to 30-min business review by Nov 25, we present financial case, she
gives verbal approval, contract signed by Dec 7.

**Acceptable Outcome**:
Carol schedules meeting (even if after Nov 25), expresses interest, provides clear
path to approval (even if close date pushes to mid-December).

**Next Steps After Exec Engagement**:
1. Sarah schedules and leads CFO business review (Mike optional attendee)
2. CFO approves, contract sent within 24 hours
3. Legal review and negotiation (3-5 days)
4. Signature by Dec 7 (or Dec 15 if timeline slips)
```

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/briefing_exec
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
prepared_for: {exec_name}
escalation_reason: {blocker|strategic_deal|exec_sponsor|board_level}
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
  - sample-data/Runtime/_Shared/knowledge/methodologies/{METHOD}/stage_inventory__{METHOD}.md  # if loaded
---
```

### 2. Compose Document

Follow structure above with concise, exec-appropriate content from deal.md

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/briefing_exec_{DATE}.md`

**Filename format**: `briefing_exec_2025-11-20.md`

---

## Error Handling

**Missing Economic Buyer**:
- Flag prominently: "Economic Buyer not identified - qualification gap"
- Suggest exec help identifying the right stakeholder

**Missing business case (Metrics)**:
- Use deal size as proxy: "$144K opportunity"
- Note: "Customer ROI not documented"

**Unclear why exec needed**:
- Generic ask: "Strategic deal review and guidance"
- Suggest AE clarify escalation reason

**Missing stakeholder context**:
- Provide company-level info (industry, size)
- Note: "Stakeholder dynamics not documented, recommend discovery"

---

## Executive Briefing Best Practices

### Why Execs Are Different from Team Briefings

**Executives need**:
- 80/20 view (signal, not noise)
- The ask up front (respect their time)
- Strategic context (why this deal matters)
- Easy action (make their job simple)

**Team briefings include**:
- 100% view (comprehensive history)
- Full MEDDPICC assessment
- Detailed stakeholder dynamics
- Chronological narrative

### Length & Format

**Target**: 1-2 pages, <3 minutes read time

**Format**:
- Lead with "The Ask" (don't bury it)
- Use bullets (not paragraphs)
- Bold key points (skim-friendly)
- Include TL;DR at top

**Tone**: Direct, data-driven, action-oriented

### When to Brief Execs

**Good reasons**:
- Economic Buyer engagement (exec-to-exec required)
- Strategic deal (large ACV, competitive win, target vertical)
- Escalation (at-risk deal needing intervention)
- Executive sponsor (customer C-level wants to meet our C-level)

**Bad reasons**:
- Normal deal progression (don't cry wolf)
- AE wants to impress exec (use exec time wisely)
- Unclear ask (figure out what you need first)

### After Exec Engagement

**AE responsibility**:
1. Debrief exec after their outreach (what happened, next steps)
2. Update deal.md History with exec involvement
3. Drive post-engagement actions (don't drop ball after exec helps)
4. Close loop (tell exec outcome - "We closed, thank you")

**Why this matters**: Execs help when they see ROI on their time. If you waste their
time or don't close loop, they won't help next time.

---

## Example Output

```markdown
---
generated_by: sales-communications/briefing_exec
generated_on: 2025-11-20T16:00:00Z
deal_id: AcmeCorp
prepared_for: Mike Sullivan
escalation_reason: blocker
sources:
  - sample-data/Runtime/Sessions/AcmeCorp/deal.md
  - sample-data/Runtime/_Shared/knowledge/methodologies/MEDDPICC/stage_inventory__MEDDPICC.md
---

# Executive Briefing: AcmeCorp

**Prepared For**: Mike Sullivan (VP Sales)
**Prepared By**: Sarah Chen (AE)
**Date**: November 20, 2025
**Read Time**: 90 seconds

---

**TL;DR**:
$144K AcmeCorp deal blocked on Economic Buyer (CFO) engagement - need your exec-to-exec
outreach to Carol Martinez (their CFO) by Nov 23 to save Dec 7 close.

---

## The Ask

Call or email Carol Martinez (AcmeCorp CFO) to request 30-minute executive business
review with her and me before Nov 25.

**Why You**: Carol is Economic Buyer (final approval >$100K) but hasn't responded to
my executive summary email. CFO-to-CFO or VP-to-CFO outreach will get her attention
where AE outreach hasn't.

**Timeline**: Outreach needed by Nov 23 to allow time for meeting before Dec 7 close.

**Effort**: 10-minute call or 5-minute email intro, then I'll drive the rest.

---

## Deal Summary

**Customer**: AcmeCorp Manufacturing, industrial sector, 5000 employees, $2B revenue
**Opportunity**: $144K ACV, 12-month term, Enterprise plan (50 users)
**Stage**: Proposal
**Close Date**: December 7, 2025

**Strategic Value**:
- First manufacturing logo in industrial sector (target vertical for 2026)
- Reference customer for automotive/aerospace market expansion
- Displaces Competitor X (they evaluated and rejected them on price)

**Business Case**:
AcmeCorp finance team spending $500K/year on manual reporting. Our solution delivers
$300K annual savings (60% reduction) with 9-month payback. New CFO chartered with
modernizing finance ops, board mandates real-time reporting by Q1 2026.

---

## Current Situation

**What's Working**:
- Technical validation complete - IT Director signed off on architecture (Nov 16)
- Champion (Jane Smith, VP Ops) enthusiastic, approved pricing
- Proposal sent and verbally accepted ($144K ACV, no pricing objection)
- Strong ROI ($300K savings, 9-month payback)
- Timeline urgent (Jan 15 go-live for Q1 board reporting)

**The Blocker**:
Carol Martinez (CFO) is Economic Buyer but not engaged. Jane (champion) has limited
authority ($100K threshold). I sent executive summary email to Carol on Nov 21 (CC'd
Jane) - no response after 48 hours. Cannot close without CFO approval.

**Why It Matters**:
- Dec 7 close at risk (need CFO meeting by Nov 25)
- $144K Q4 ARR slips to Q1 if we miss timeline
- Customer may revert to status quo if urgency fades (lose deal)
- Reference customer value lost (strategic target vertical)

---

## Key Stakeholders

**Who You'll Engage**:
**Carol Martinez, CFO** - Economic Buyer (final approval >$100K)
- **Priorities**: Cost reduction, ROI, financial risk mitigation (typical CFO concerns)
- **Context**: New CFO hired 6 months ago, chartered by CEO to modernize finance operations.
  She's data-driven, direct, skeptical of vendor claims (per Jane's description).
- **Approach**: Lead with ROI ($300K savings, 9-month payback), reference IT validation
  (de-risk implementation), tie to her mandate (board reporting modernization). Offer
  30-min business review to walk through financial case.

**Champion (Our Internal Advocate)**:
**Jane Smith, VP Operations**
- Reports to Carol (CFO), strong relationship with her
- Frustrated Jane can't close deal herself (limited authority), but supportive of us
- Has already briefed Carol on our solution (verbal), Carol just hasn't prioritized meeting

**Other Key Players**:
- Michael Chen, Director IT - Technical validation complete, supportive
- Sarah Park, Data Analyst - End-user, very positive on solution

---

## Suggested Talking Points

**Opening**:
"Hi Carol, I'm Mike Sullivan, VP Sales at Example Corp. My AE Sarah has been working with
Jane and your team on the financial reporting automation initiative. Jane mentioned you're
driving finance modernization - I wanted to connect personally given the strategic nature
of this project for AcmeCorp."

**The Business Case**:
- $300K annual savings (60% reduction in manual processing costs) with 9-month payback
- Enables real-time board reporting (addresses your Q1 2026 mandate)
- Automated compliance controls address SOX audit findings from November

**Social Proof**:
- Fortune 500 healthcare company similar use case (15 FTEs → 5 FTEs, 67% cost reduction)
- 30-day average implementation (low risk, fast time-to-value)
- Your IT team (Michael Chen) already validated technical architecture

**The Ask**:
"Could we schedule 30 minutes next week - you, Jane, and Sarah - to walk through the
financial case and answer any questions? Jane's team has done great work validating
the operational fit, just want to ensure you're comfortable with the investment."

**Objection Handling**:
- **"Why should I prioritize this?"** → Jan 15 go-live required for Q1 board reporting
  (per CEO mandate). Delaying means another quarter of $125K manual processing costs.
- **"What's the risk?"** → IT validation complete (Michael signed off), 30-day
  implementation, money-back guarantee if we don't hit Jan 15 go-live.
- **"Why not wait until next budget cycle?"** → Budget approved this cycle ($500K
  allocation). Waiting means missing Q1 reporting deadline and continuing $500K/year cost.

---

## Success Metrics

**Ideal Outcome**:
Carol agrees to 30-min business review by Nov 25, we present financial case, she
gives verbal approval, contract signed by Dec 7.

**Acceptable Outcome**:
Carol schedules meeting (even if after Nov 25), expresses interest, provides clear
path to approval (even if close date pushes to mid-December).

**Next Steps After Exec Engagement**:
1. Sarah schedules and leads CFO business review (Mike optional attendee)
2. CFO approves, contract sent within 24 hours
3. Legal review and negotiation (3-5 days)
4. Signature by Dec 7 (or Dec 15 if timeline slips)

---

**Contact**: Sarah Chen | sarah.chen@example.com | (555) 123-4567
```

---

**End of Pattern: briefing_exec**
