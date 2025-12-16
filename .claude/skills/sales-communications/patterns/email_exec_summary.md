# Email: Executive Summary

**Pattern**: email_exec_summary
**Type**: Customer-facing email
**Timing**: When escalating to executive sponsor or providing C-level update
**Purpose**: Deliver concise business-focused summary for executive decision-maker

---

## When to Use

Send this email to executive stakeholders (VP, C-level) to:
- Escalate from mid-level contacts to economic buyer
- Provide concise deal summary for busy executives
- Accelerate decision-making by removing information overload
- Position solution in business terms (ROI, risk, strategic value)
- Request executive engagement or final approval

**Trigger Phrases**:
- "Draft executive summary for {DEAL}"
- "Send C-level update to {DEAL}"
- "Create exec summary email for {economic buyer}"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Economic Buyer identified in MEDDPICC section
   - Business metrics and ROI from MEDDPICC "Metrics" field
   - Current deal status (stage, timeline, blockers)
   - Stakeholder names and titles
3. Email style corpus (4-tier loading per _common.md section 3)

**OPTIONAL**:
- Brand guidelines (for formatting, tone)
- Methodology stage inventory (for executive engagement best practices)

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Economic Buyer**: From MEDDPICC "Economic Buyer" section (name, title, authority level)
- **Business metrics**: From MEDDPICC "Metrics" (ROI, cost savings, revenue impact)
- **Strategic pain points**: From MEDDPICC "Identify Pain" (business problems, not technical issues)
- **Decision timeline**: From MEDDPICC "Decision Process" (urgency, budget cycle)
- **Current status**: From stage and recent History (where deal stands)
- **Key blockers**: From D1 tasks or History (what's preventing progress)
- **Champion**: From MEDDPICC (who's advocating internally)

**Example MEDDPICC Fields to Parse**:
```markdown
## MEDDPICC

**Economic Buyer**: Carol Martinez, CFO
- Authority: Final budget approval for investments >$100K
- Priorities: Cost reduction, operational efficiency, risk mitigation

**Metrics**:
- Current cost: $500K/year in manual processing overhead
- Target savings: 60% reduction = $300K annual savings
- ROI timeline: 9-month payback period
- Strategic value: Enable real-time financial reporting for board

**Identify Pain**:
- Board demands real-time reporting, current system delivers weekly (7-day lag)
- Manual processes create compliance risk (SOX audit findings)
- Finance team turnover due to repetitive low-value work
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system, BUT adjust for executive audience:
- Shorter paragraphs than discovery/demo emails
- More business language, less technical detail
- Direct subject lines, no fluff
- Crisp CTAs (ask for meeting, decision, or escalation)

### 3. Load Brand Guidelines (Section 2 of _common.md)

If brand_guidelines.md exists:
- Apply executive communication tone (professional, strategic)
- Include company signature and contact info

### 4. Load Methodology Guidance (Section 4 of _common.md)

If MEDDPICC stage inventory available:
- Ensure email engages Economic Buyer per methodology
- Frame in terms of business outcomes (not features)
- Address executive priorities (revenue, cost, risk, strategy)

---

## Email Structure

### Subject Line
**Formula**: `[Company Name] - [Business Outcome]: Executive Summary`

**Options** (choose based on urgency and relationship):
- Direct: "{Company} Investment Summary - $300K Annual Savings"
- Strategic: "Board Reporting Initiative - Executive Summary"
- Urgent: "Decision Needed: {Initiative} Timeline"

**Examples**:
- "AcmeCorp Financial Automation - Executive Summary"
- "Q1 Reporting Initiative: $300K Savings Opportunity"
- "Real-Time Board Reporting - Investment Decision"

### Opening Paragraph
**Purpose**: Establish relevance, respect their time, state purpose

**Template** (2-3 sentences max):
```
{FIRST_NAME},

{Introduction/context - how you got their contact or why you're reaching out}.
I'm sending a brief summary of {initiative/solution} that {primary business outcome}
for {their company}. {Time commitment ask - 5 min read, 15 min call, etc.}.
```

**Example**:
```
Carol,

Jane Smith suggested I reach out to you regarding our financial automation initiative.
I'm sending a brief summary of the solution we've been evaluating that could reduce
AcmeCorp's processing overhead by $300K annually while addressing the board's real-time
reporting requirements. This should take less than 5 minutes to review.
```

**Style Variations**:
- Warm intro (if champion made introduction): "{Champion} thought you should see this..."
- Cold escalation: "I've been working with {mid-level contact} on {initiative}..."
- Follow-up: "Following up on {previous brief interaction}..."

### Business Challenge Section
**Purpose**: Frame the problem in executive terms (money, risk, strategy)

**Template**:
```
## Current Challenge

{1-2 sentence business problem statement}

**Impact**:
- {Quantified cost or risk}
- {Strategic constraint or competitive disadvantage}
- {Organizational pain - retention, compliance, board pressure}
```

**Example**:
```
## Current Challenge

AcmeCorp's finance team currently spends $500K annually on manual data processing,
delivering board reports weekly instead of in real-time.

**Impact**:
- $500K/year operational cost in manual work (15 FTEs)
- 7-day reporting lag prevents agile decision-making
- SOX audit findings flagged manual process compliance risks
- Finance team turnover (40% annual attrition due to low-value work)
```

**Best Practices**:
- Lead with dollars or strategic risk (what execs care about)
- Quantify everything possible (FTEs, $, %, timeline)
- Connect to their stated priorities (board demands, compliance, competition)
- Avoid technical jargon (no "API integration" - say "automated data sync")

### Proposed Solution Section
**Purpose**: High-level solution overview focused on business outcomes

**Template**:
```
## Proposed Solution

{1 sentence solution description in business terms}

**Business Outcomes**:
- {Primary financial benefit with timeline}
- {Secondary strategic benefit}
- {Risk mitigation or compliance benefit if applicable}

**Investment**: {Total cost} over {term}
**ROI**: {Payback period} payback, {ROI %} return
```

**Example**:
```
## Proposed Solution

Automated financial reporting platform that eliminates manual processing and delivers
real-time board-ready dashboards.

**Business Outcomes**:
- $300K annual savings (60% reduction in processing costs)
- Real-time reporting replaces 7-day lag, enabling faster decisions
- Automated compliance controls address SOX audit findings
- Improved finance team satisfaction and retention

**Investment**: $144K annually (Enterprise plan, 50 users)
**ROI**: 9-month payback, 208% 3-year ROI
```

**Tone**: Confidence, not salesmanship. Facts, not hype.

### Status & Next Steps Section
**Purpose**: Transparent deal status, clear ask, simple decision path

**Template**:
```
## Current Status

{Where evaluation stands - stage, stakeholder engagement, timeline}

**Next Steps**:
1. {Clear ask - meeting, decision, approval}
2. {What happens after - implementation timeline, onboarding, go-live}

**Decision Timeline**: {When decision needed and why}
```

**Example**:
```
## Current Status

Your team has completed technical validation (IT signoff from Michael Chen) and
evaluated our platform against {competitor if applicable}. Jane Smith (VP Operations)
has confirmed this addresses AcmeCorp's requirements and supports moving forward.

**Next Steps**:
1. **30-minute executive review call** (proposed: Nov 22 at 10am) - Review business
   case, answer any questions, discuss contract terms
2. **Contract execution by Nov 30** - Enables Jan 15 go-live to support Q1 board
   reporting cycle

**Decision Timeline**: Jan 15 go-live requires contract by Nov 30 for onboarding and
data migration ahead of year-end close.
```

**Best Practices**:
- Acknowledge work already done (technical validation, stakeholder buy-in)
- Make ask simple and time-bounded (30 min call, yes/no decision)
- Tie timeline to their business driver (board meeting, budget cycle, compliance deadline)
- Remove friction (you drive next steps, not them)

### Closing Paragraph
**Purpose**: Open door, express confidence, respect their time

**Template**:
```
{Confidence statement}. {Question invitation}. {Appreciation}.

{Closing},
{Signature}
```

**Example**:
```
I'm confident this solution delivers the cost savings and real-time visibility
your board requires. Happy to answer any questions or schedule time to discuss
in more detail. I appreciate your consideration.

Best regards,
Sarah Chen
```

**Style Variations**:
- Formal: "I look forward to your feedback and next steps."
- Direct: "Let me know if you'd like to schedule the review call."
- Deferential: "I appreciate your time reviewing this summary."

### Signature
Apply brand guidelines signature format if available, otherwise:

```
[AE Name]
[Title]
[Company Name]
[Email] | [Phone]
```

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_exec_summary
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
recipient_role: Economic Buyer
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

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_exec_summary_{DATE}.md`

**Filename format**: `email_exec_summary_2025-11-14.md`

---

## Error Handling

**Missing Economic Buyer in MEDDPICC**:
- Prompt user: "No Economic Buyer identified. Who should receive this summary?"
- Generate generic exec summary and ask user to specify recipient

**Missing Metrics (ROI, savings)**:
- Generate summary without financial quantification
- Suggest updating MEDDPICC Metrics field with business case

**Missing stage/status**:
- Assume "Proposal" or "Negotiation" stage (when exec summaries are most common)
- Generic status: "Your team is evaluating our solution..."

**Missing stakeholders/champion**:
- Use generic intro: "I'm reaching out regarding {initiative}..."
- Suggest identifying champion for warm introduction

**Missing methodology**:
- Use generic B2B executive engagement best practices
- Focus on ROI, risk, and strategic value

---

## Executive Email Best Practices

### Why Executives Are Different

**Executives care about**:
- Financial impact (revenue, cost, margins)
- Strategic value (competitive advantage, market positioning)
- Risk (compliance, reputation, operational)
- Speed to value (time to ROI, implementation risk)

**Executives don't care about**:
- Feature lists (they delegate technical evaluation)
- Long narratives (respect their time)
- Your company's story (make it about THEM)

### Tone & Length

**Tone**: Confident, concise, business-focused
- Use "I recommend" not "I think maybe"
- Lead with outcomes, not activities
- Respect hierarchy (acknowledge champion, don't undercut them)

**Length**: <300 words ideal
- Execs skim, not read
- Bullets > paragraphs
- One ask per email

### When to Send

**Right time**:
- After technical validation complete (de-risk for exec)
- When champion suggests ("You should talk to Carol")
- When deal stalled at mid-level (escalation play)
- Before major decision point (budget approval, board meeting)

**Wrong time**:
- Too early (no mid-level validation = waste of exec time)
- Too late (decision already made without them)
- Too often (one exec summary per deal, max two)

---

## Example Output

```markdown
---
generated_by: sales-communications/email_exec_summary
generated_on: 2025-11-14T14:00:00Z
deal_id: AcmeCorp
recipient_role: Economic Buyer
sources:
  - sample-data/Runtime/Sessions/AcmeCorp/deal.md
  - sample-data/Runtime/_Shared/style/team_corpus.md
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md
---

**Subject**: AcmeCorp Financial Automation - Executive Summary

Carol,

Jane Smith suggested I reach out to you regarding our financial automation initiative.
I'm sending a brief summary of the solution we've been evaluating that could reduce
AcmeCorp's processing overhead by $300K annually while addressing the board's real-time
reporting requirements. This should take less than 5 minutes to review.

## Current Challenge

AcmeCorp's finance team currently spends $500K annually on manual data processing,
delivering board reports weekly instead of in real-time.

**Impact**:
- $500K/year operational cost in manual work (15 FTEs)
- 7-day reporting lag prevents agile decision-making
- SOX audit findings flagged manual process compliance risks
- Finance team turnover (40% annual attrition due to low-value work)

## Proposed Solution

Automated financial reporting platform that eliminates manual processing and delivers
real-time board-ready dashboards.

**Business Outcomes**:
- $300K annual savings (60% reduction in processing costs)
- Real-time reporting replaces 7-day lag, enabling faster decisions
- Automated compliance controls address SOX audit findings
- Improved finance team satisfaction and retention

**Investment**: $144K annually (Enterprise plan, 50 users)
**ROI**: 9-month payback, 208% 3-year ROI

## Current Status

Your team has completed technical validation (IT signoff from Michael Chen) and
evaluated our platform against current manual processes. Jane Smith (VP Operations)
has confirmed this addresses AcmeCorp's requirements and supports moving forward.

**Next Steps**:
1. **30-minute executive review call** (proposed: Nov 22 at 10am) - Review business
   case, answer any questions, discuss contract terms
2. **Contract execution by Nov 30** - Enables Jan 15 go-live to support Q1 board
   reporting cycle

**Decision Timeline**: Jan 15 go-live requires contract by Nov 30 for onboarding and
data migration ahead of year-end close.

I'm confident this solution delivers the cost savings and real-time visibility
your board requires. Happy to answer any questions or schedule time to discuss
in more detail. I appreciate your consideration.

Best regards,
Sarah Chen
Senior Account Executive
Example Corp Solutions
sarah.chen@example.com | (555) 123-4567
```

---

**End of Pattern: email_exec_summary**
