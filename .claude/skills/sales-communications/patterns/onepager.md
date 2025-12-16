# Document: Deal One-Pager

**Pattern**: onepager
**Type**: Hybrid document (internal or customer-facing)
**Timing**: As needed for quick deal summaries
**Purpose**: Single-page deal snapshot for quick consumption (QBRs, handoffs, proposals)

---

## When to Use

Create this one-pager for various audiences:
- **Customer-facing**: Attached to proposals as executive summary
- **Internal**: Quick deal snapshot for forecast reviews, QBRs
- **Partner**: Deal summary for channel partners or implementation teams
- **Executive**: Board deck slide or investor update material

**Trigger Phrases**:
- "Create one-pager for {DEAL}"
- "Draft deal summary for {DEAL}"
- "Generate executive one-pager"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Deal basics (company, ACV, stage, close date)
   - Business case (customer pain, solution value)
   - Key stakeholders (Economic Buyer, Champion)
   - Current status and next steps
3. **Audience specification**: Customer-facing or internal (changes tone and content)
4. **NOTE**: Do NOT load email style corpus (not applicable for documents)

**OPTIONAL**:
- Brand guidelines (CRITICAL for customer-facing, formatting for internal)
- Methodology stage inventory (for qualification summary)

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract high-level summary from deal.md:
- **Deal snapshot**: Company, industry, ACV, stage, timeline
- **Business problem**: Customer pain point in 1-2 sentences
- **Solution value**: How we solve it, business outcomes
- **ROI/Metrics**: Financial impact (if available)
- **Stakeholders**: Key decision-makers (Economic Buyer, Champion)
- **Status**: Current stage, what's done, what's next
- **Competitive**: Who we're competing against (if customer-facing, subtle)

**One-pager is dense** - every sentence must add value

### 2. Load Brand Guidelines (Section 2 of _common.md)

**Customer-facing**: CRITICAL - Apply branding, logo, colors, formatting
**Internal**: Optional - Use if corporate template exists

### 3. Load Methodology Guidance (Section 4 of _common.md)

If MEDDPICC stage inventory available, use for qualification summary (internal version only)

---

## Document Structure

### Customer-Facing One-Pager

**Purpose**: Leave-behind document, proposal attachment, board presentation

**Structure**:
```
[Company Logo - Your Company]

# {Customer Company Name} - Executive Summary

**Prepared For**: {Customer contact name, title}
**Date**: {Date}

---

## The Challenge

{2-3 sentence customer pain point in their words}

**Business Impact**:
- {Quantified cost or inefficiency}
- {Strategic constraint or risk}
- {Operational pain}

---

## The Solution

{2-3 sentence solution overview focused on outcomes}

**Key Capabilities**:
- {Capability 1} - {Benefit to customer}
- {Capability 2} - {Benefit to customer}
- {Capability 3} - {Benefit to customer}

---

## Business Value

**Financial Impact**:
- {Savings or revenue impact}: {$X annually}
- {Efficiency gain}: {X% improvement}
- {ROI}: {X-month payback, X% return}

**Strategic Benefits**:
- {Strategic outcome 1}
- {Strategic outcome 2}

---

## Investment & Timeline

**Investment**: {$X annually / total contract value}
**Term**: {X months/years}
**Implementation**: {X weeks to go-live}
**Go-Live Date**: {Target date}

---

## Why {Your Company}

**Proven Results**:
- {Customer success stat or case study}
- {Industry credibility or awards}

**Implementation Confidence**:
- {Average implementation time}
- {Customer success support model}

---

## Next Steps

1. {Milestone 1} - {Date}
2. {Milestone 2} - {Date}
3. {Go-live} - {Date}

---

[Your Company Contact Info, Logo]
{AE Name, Title, Email, Phone}
```

**Example (Customer-Facing)**:
```
[Example Corp Solutions Logo]

# AcmeCorp Manufacturing - Executive Summary

**Prepared For**: Carol Martinez, Chief Financial Officer
**Date**: November 22, 2025

---

## The Challenge

AcmeCorp's finance team manually aggregates data from 15+ systems to produce board
reports, consuming 50+ hours per week and delivering results with a 7-day lag. This
manual process costs $500K annually and creates SOX compliance risks.

**Business Impact**:
- $500K/year operational cost (15 FTEs in manual processing)
- 7-day reporting lag prevents real-time decision-making
- SOX audit findings flagged manual process compliance risks
- Finance team turnover (40% attrition due to repetitive work)

---

## The Solution

Example Corp's automated financial reporting platform eliminates manual data aggregation
through real-time Salesforce integration and delivers board-ready dashboards on demand.

**Key Capabilities**:
- **Real-Time Integration** - Automated data sync from Salesforce and legacy systems (no manual exports)
- **Executive Dashboards** - Pre-built templates for board, C-suite, and department leaders
- **Drill-Down Analytics** - Click from summary metrics to underlying transactions without custom queries
- **Mobile Access** - iOS/Android apps for on-the-go reporting

---

## Business Value

**Financial Impact**:
- **$300K annual savings** (60% reduction in manual processing costs)
- **80% time reduction** (50 hours/week → 10 hours/week)
- **9-month payback**, 208% 3-year ROI

**Strategic Benefits**:
- Real-time board reporting (eliminates 7-day lag)
- Automated compliance controls (addresses SOX audit findings)
- Improved finance team retention (eliminate low-value manual work)

---

## Investment & Timeline

**Investment**: $144K annually (Enterprise plan, 50 users)
**Term**: 12 months (annual renewal)
**Implementation**: 4 weeks to go-live
**Go-Live Date**: January 15, 2026 (Q1 board reporting ready)

---

## Why Example Corp

**Proven Results**:
- Fortune 500 healthcare company: 67% cost reduction (15 FTEs → 5 FTEs)
- 4.8/5 G2 rating, Gartner Peer Insights Customers' Choice 2025
- 200+ enterprise customers in manufacturing, healthcare, financial services

**Implementation Confidence**:
- 30-day average implementation (industry-leading)
- Dedicated customer success manager and 24/7 support
- Money-back guarantee if Jan 15 go-live not achieved

---

## Next Steps

1. **Executive Business Review** - November 25, 2025 (30 minutes)
2. **Contract Execution** - November 30, 2025
3. **Implementation Kickoff** - December 2, 2025
4. **Go-Live** - January 15, 2026 (Q1 board reporting ready)

---

[Example Corp Solutions Logo]
**Sarah Chen**, Senior Account Executive
sarah.chen@example.com | (555) 123-4567
www.datacorpsolutions.com
```

---

### Internal One-Pager

**Purpose**: Forecast review, QBR, pipeline assessment, deal handoff

**Structure**:
```
# Deal One-Pager: {Customer Company Name}

**AE**: {AE name}
**Date**: {Date}
**Opportunity**: {ACV, term}
**Stage**: {Stage}
**Forecast**: {Pipeline/Best Case/Commit}
**Close Date**: {Date}

---

## Customer & Opportunity

**Company**: {Name, industry, size}
**Pain Point**: {Business problem in 1 sentence}
**Solution Value**: {How we solve it, business outcome}
**Strategic Importance**: {Why this deal matters - competitive win, vertical entry, reference}

---

## Qualification (MEDDPICC)

| Element | Status | Notes |
|---------|--------|-------|
| **Metrics** | {Red/Yellow/Green} | {ROI summary} |
| **Economic Buyer** | {Red/Yellow/Green} | {Who, engaged or not} |
| **Decision Criteria** | {Red/Yellow/Green} | {Requirements status} |
| **Decision Process** | {Red/Yellow/Green} | {Timeline, approvals} |
| **Champion** | {Red/Yellow/Green} | {Who, strength} |
| **Competition** | {Red/Yellow/Green} | {Competitive landscape} |

**Overall**: {Summary sentence on deal health}

---

## Status & Next Steps

**What's Complete**:
- {Milestone}
- {Milestone}

**Primary Blocker**: {Main obstacle if any}

**Next Steps**:
1. {Action} - {Owner}, {Date}
2. {Action} - {Owner}, {Date}

**Risks**:
- {Risk 1}
- {Risk 2}

---

**Prepared by**: {AE name}
```

**Example (Internal)**:
```
# Deal One-Pager: AcmeCorp

**AE**: Sarah Chen
**Date**: November 20, 2025
**Opportunity**: $144K ACV, 12-month term, Enterprise plan
**Stage**: Proposal
**Forecast**: Best Case (downgraded from Commit due to EB risk)
**Close Date**: December 7, 2025

---

## Customer & Opportunity

**Company**: AcmeCorp Manufacturing, industrial sector, 5000 employees, $2B revenue
**Pain Point**: Finance team spending $500K/year on manual reporting, board demands real-time dashboards
**Solution Value**: $300K annual savings (60% reduction), 9-month payback, enables Q1 2026 board reporting
**Strategic Importance**: First manufacturing logo in industrial sector (target vertical 2026), reference customer for automotive/aerospace, displaces Competitor X

---

## Qualification (MEDDPICC)

| Element | Status | Notes |
|---------|--------|-------|
| **Metrics** | Green | $300K savings, 9-month payback validated with champion |
| **Economic Buyer** | Red | Carol (CFO) identified but NOT engaged - PRIMARY BLOCKER |
| **Decision Criteria** | Green | Technical requirements validated by IT (Nov 16 signoff) |
| **Decision Process** | Yellow | Timeline clear (Jan 15 go-live), approval process unclear |
| **Champion** | Yellow | Jane (VP Ops) strong but limited authority ($100K threshold) |
| **Competition** | Yellow | Status quo main risk, Competitor X evaluated and rejected |

**Overall**: Deal qualified but at risk - Economic Buyer gap is critical blocker, need CFO engagement by Nov 25.

---

## Status & Next Steps

**What's Complete**:
- Discovery, demo, proposal sent (pricing approved by champion)
- Technical validation complete (IT Director signoff Nov 16)
- Strong business case ($300K savings, 9-month payback)

**Primary Blocker**: Carol Martinez (CFO) not engaged - she's Economic Buyer but hasn't responded to executive summary email

**Next Steps**:
1. VP Sales exec-to-exec outreach to Carol - Mike Sullivan, Nov 23
2. CFO business review scheduled - Sarah Chen, by Nov 25
3. Contract sent (if CFO approves) - Sarah Chen, Nov 30

**Risks**:
- CFO doesn't engage → deal slips to Q1 or dies (status quo)
- Timeline pressure fades → customer delays decision
- Champion lacks power → can't close without Economic Buyer

---

**Prepared by**: Sarah Chen | sarah.chen@company.com
```

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/onepager
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
audience: {customer|internal|partner}
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
  - sample-data/Runtime/_Shared/knowledge/methodologies/{METHOD}/stage_inventory__{METHOD}.md  # if loaded
---
```

### 2. Compose Document

Follow structure above based on audience (customer vs internal)

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/onepager_{AUDIENCE}_{DATE}.md`

**Filename format**:
- `onepager_customer_2025-11-22.md` (customer-facing)
- `onepager_internal_2025-11-20.md` (internal)

---

## Error Handling

**Missing audience specification**:
- Default to internal version (safer - no branding required)
- Prompt user: "Should this be customer-facing or internal?"

**Missing business case (Metrics)**:
- Customer version: Omit Business Value section or use qualitative benefits
- Internal version: Flag "Metrics: Red - Not documented"

**Missing Economic Buyer**:
- Customer version: Omit stakeholder references (don't expose gaps)
- Internal version: Flag prominently "EB: Red - Not identified"

**Missing brand guidelines (customer-facing)**:
- Generate clean markdown format with placeholder for logo
- Warn user: "Add company logo and branding before sending to customer"

**Sparse deal.md**:
- Generate one-pager with available data
- Internal version: Flag data gaps
- Customer version: Use generic professional language

---

## One-Pager Best Practices

### Why One-Pagers Matter

**Benefits**:
- **Portable**: Easy to forward, attach, share (email-friendly)
- **Scannable**: Busy execs can digest in 60 seconds
- **Versatile**: Works for proposals, QBRs, handoffs, board decks
- **Memorable**: Visual format sticks better than long emails

### Customer-Facing vs Internal

**Customer-Facing One-Pager**:
- **Focus**: Their business outcomes (not our features)
- **Tone**: Confident, outcome-oriented, professional
- **Branding**: MUST include logo, colors, formatting
- **Avoid**: Internal jargon, MEDDPICC terminology, qualification gaps
- **Include**: Social proof, case studies, credibility markers
- **Format**: Polished, professional, ready to present to their C-suite

**Internal One-Pager**:
- **Focus**: Deal health and forecast accuracy
- **Tone**: Candid, data-driven, risk-aware
- **Branding**: Optional (lightweight formatting)
- **Include**: MEDDPICC assessment, blockers, risks, qualification gaps
- **Avoid**: Over-selling (be honest about deal status)
- **Format**: Functional, scannable, action-oriented

### When to Use Each Version

**Customer-Facing**:
- Proposal attachment (executive summary for C-level)
- Board presentation (customer presenting us to their board)
- Champion enablement (help them sell internally)
- Executive leave-behind (after exec business review)

**Internal**:
- Forecast review (pipeline qualification snapshot)
- QBR prep (deal health assessment)
- Deal handoff (territory transfer, AE change)
- Manager coaching (quick context for deal review)

### Design & Formatting

**Customer-Facing**:
- Professional design (use brand guidelines)
- Logo placement (header and footer)
- Visual hierarchy (headings, bullets, whitespace)
- Export as PDF (not editable markdown)
- Page limit: 1 page (2 pages max for complex deals)

**Internal**:
- Clean markdown or simple doc format
- Tables for MEDDPICC assessment (scannable)
- Bullet-heavy (skim-friendly)
- Color coding if available (Red/Yellow/Green status)
- Page limit: 1 page (strict)

### Common Mistakes

**Don't**:
- Exceed 1 page (2 pages destroys "one-pager" value)
- Use tiny font to cram content (defeats scannability)
- Include jargon audience won't understand
- Over-promise (customer version) or over-sell (internal version)
- Send customer version with qualification gaps visible
- Send internal version to customer (exposes MEDDPICC assessment)

**Do**:
- Use audience-appropriate language and detail level
- Include only high-signal information (no fluff)
- Make every sentence count (dense but readable)
- Update regularly (one-pagers go stale fast)
- Version control (date in filename, frontmatter)

---

## Example Output

{Full examples shown above in Document Structure section}

---

**End of Pattern: onepager**
