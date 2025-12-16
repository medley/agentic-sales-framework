# Email: Milestone Celebration

**Pattern**: email_milestone_celebration
**Type**: Customer-facing email
**Timing**: When customer hits significant milestone
**Purpose**: Celebrate their success, reinforce value, plant seeds for expansion

---

## When to Use

Send this email to:
- Celebrate product go-live completion
- Acknowledge ROI target achievement
- Recognize usage threshold milestones (10,000 users, 1M records, etc.)
- Mark time-based anniversaries (1 year customer)
- Celebrate expansion to new department/region
- Recognize successful completion of implementation phase

**NOT for**:
- Routine check-ins (use email_simple_followup)
- First meeting follow-ups (use email_discovery_recap)
- Demo follow-ups (use email_demo_followup)
- Renewal discussions (use appropriate sales pattern)

**Trigger Phrases**:
- "Celebrate {MILESTONE} with {CUSTOMER}"
- "Congrats on go-live"
- "Hit ROI target email"
- "Celebrate success with {DEAL}"
- "Milestone email for {CUSTOMER}"
- "Anniversary email to {CONTACT}"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Stakeholder name (recipient or champion)
   - Milestone data (what was achieved, when)
   - Original goals or success criteria (from discovery/proposal)
3. Milestone metrics:
   - Specific achievement data (users onboarded, ROI percentage, records processed, etc.)
   - Timeline context (days to go-live, time to ROI, etc.)
   - Comparison to original targets if available

**OPTIONAL**:
- Email style corpus (for tone matching)
- Brand guidelines (for signature formatting)
- Usage analytics or product data
- Customer success notes with detailed metrics

**NOT NEEDED**:
- Current stage gate criteria
- Detailed technical implementation notes
- Full deal qualification history

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Recipient name**: Champion or primary stakeholder
- **Milestone achieved**: What specific success occurred
- **Achievement data**: Concrete metrics (users, time, ROI %, volume, etc.)
- **Original goals**: What they told us they wanted to achieve (from discovery notes or proposal)
- **Timeline context**: When milestone was hit, how long it took

**Example History Entry to Parse**:
```markdown
## History
- 2025-11-12: GlobalPharma went live with 2,500 users across Quality and Regulatory departments. Hit projected 6-week go-live timeline.
- 2025-10-01: Proposal presented targeting 2,000 users, 8-week implementation.
```

**Example D1 Task to Parse**:
```markdown
## D1 Tasks (This Month)
- [ ] Celebrate go-live milestone with Jim - exceeded user target by 25%
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system for tone matching (keep celebratory but professional)

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply signature formatting only

---

## Email Structure

### Subject Line
**Formula**: Keep under 7 words, lead with celebration

**Options**:
- "Congratulations on {MILESTONE}" (e.g., "Congratulations on go-live")
- "{NUMBER} {METRIC} - amazing work" (e.g., "10,000 users - amazing work")
- "You hit your {TARGET}" (e.g., "You hit your ROI target")
- "One year together - thank you"

### Body (Single Paragraph)
**Purpose**: Celebrate their achievement, credit their team, reinforce value, plant expansion seed

**Structure**: 4-6 sentences, 90-130 words total

**Template**:
```
Hi {FIRST_NAME},

{Enthusiastic celebration of specific milestone with data}. {Credit to their team/leadership for the achievement}. {Connection to original goal or challenge they shared}. {Reinforcement of value being delivered}. {Subtle expansion seed or future opportunity}. {Forward-looking closing statement}.

{Closing},
{Signature}
```

**CRITICAL CONSTRAINTS**:
- Use ACTUAL metrics from the deal (not placeholders or generic numbers)
- Credit THEIR team explicitly (not just your product)
- Tie back to THEIR original goals or pain points from discovery
- Keep expansion seed subtle (no hard ask, just plant the idea)
- Make it about THEM, not you or your product

---

## Examples

### Example 1: Go-Live Milestone

```markdown
---
generated_by: sales-communications/email_milestone_celebration
generated_on: 2025-11-15T10:30:00Z
deal_id: GlobalPharma
sources:
  - sample-data/Runtime/Sessions/GlobalPharma/deal.md
  - sample-data/Runtime/Sessions/GlobalPharma/artifacts/discovery_notes_2025-09-15.md
---

**Subject**: Congratulations on go-live

Hi Jim,

Congratulations to you and the team on successfully going live with 2,500 users across Quality and Regulatory this week. You not only hit your 6-week timeline but exceeded your initial 2,000-user target by 25%. This is a testament to how well your team executed the implementation and how committed everyone was to solving those audit readiness challenges you shared back in September. You're already seeing the efficiency gains we discussed, and I know this is just the beginning. As your Manufacturing team sees what Quality accomplished, I imagine they'll be excited about the possibilities. Looking forward to seeing the impact continue to grow.

Best,
Welf
```

**Word count**: 118 words

### Example 2: ROI Achievement

```markdown
---
generated_by: sales-communications/email_milestone_celebration
generated_on: 2025-11-15T14:20:00Z
deal_id: MedDevice_Inc
sources:
  - sample-data/Runtime/Sessions/MedDevice_Inc/deal.md
  - sample-data/Runtime/Sessions/MedDevice_Inc/artifacts/proposal_2025-07-22.md
---

**Subject**: You hit your ROI target

Hi Sarah,

I just saw that you've already hit your 18-month ROI target in only 9 months - that's incredible. Your team's ability to reduce manual data entry by 70% and cut audit prep time from weeks to days is exactly the transformation you envisioned when we first talked. The hard work your Quality team put into adoption and process refinement really shows in these results. You mentioned back in July that the VP of Operations was watching this closely - I bet these numbers are making an impression. Excited to see what the next quarter brings as usage continues to mature.

Congratulations,
Michael
```

**Word count**: 114 words

### Example 3: Usage Milestone

```markdown
---
generated_by: sales-communications/email_milestone_celebration
generated_on: 2025-11-15T16:45:00Z
deal_id: BioTech_Solutions
sources:
  - sample-data/Runtime/Sessions/BioTech_Solutions/deal.md
  - sample-data/Runtime/_Shared/knowledge/customer_success/biotech_usage_report_Q4.md
---

**Subject**: 1 million records processed

Hi David,

Your team just crossed 1 million records processed through the system, and I wanted to take a moment to recognize this milestone. When we started this journey, you were struggling with data silos across three legacy systems and spending weeks on compliance reporting. Now you're processing 50,000+ records weekly with full traceability. Your data governance team deserves real credit for how thoughtfully they structured the migration and adoption plan. As you continue to scale, I know your European sites are going through similar challenges - happy to explore how this success could translate there when the timing is right.

Great work,
Anna
```

**Word count**: 115 words

---

## Closing Options

**Celebratory**:
- "Congratulations,"
- "Great work,"
- "Well done,"
- "Cheers to your success,"

**Professional**:
- "Best,"
- "Best regards,"
- "Thank you,"
- "Looking forward,"

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_milestone_celebration
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - sample-data/Runtime/Sessions/{DEAL}/artifacts/{discovery_or_proposal_file}
  - sample-data/Runtime/_Shared/style/{style_file}  # if loaded
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
---
```

### 2. Compose Email Body

**CRITICAL CONSTRAINTS**:
- Total body: 90-130 words (excluding subject and signature)
- Single paragraph only (no bullet lists, no sections)
- Use ACTUAL data from the deal (specific numbers, dates, metrics)
- Credit their team explicitly by name or role
- Reference their original goals/pain points from discovery or proposal
- Expansion seed should be ONE sentence maximum and feel natural
- Celebratory but professional tone (avoid excessive exclamation marks or emojis)

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_milestone_celebration_{DATE}.md`

**Filename format**: `email_milestone_celebration_2025-11-15.md`

---

## Error Handling

**Missing milestone data**:
- Prompt user: "What specific milestone should I celebrate? Include metrics if available."
- Cannot generate without concrete achievement to reference

**Missing original goals**:
- Review discovery notes or proposal for success criteria
- If unavailable, acknowledge achievement without comparing to original targets

**Missing recipient**:
- Default to primary contact from deal.md
- Use "Hi team," if multiple stakeholders should receive

**Vague metrics**:
- Ask user for specific numbers (users, records, time savings, ROI %, etc.)
- Generic celebration email has no impact - needs data

---

## Milestone Celebration Best Practices

**Use Their Data**: Every metric should come from actual deal history or usage data. No placeholders, no "XX users" or "significant improvement."

**Make It About Them**: Credit their team by name/role. Reference their specific challenges. Highlight their execution, not just your product.

**Tie to Original Goals**: Connect achievement back to what THEY said they wanted during discovery. This shows you listened and reinforces value alignment.

**Expansion Seeds Are Subtle**: One sentence maximum. Natural mention of other teams/regions/use cases that might benefit. No hard ask, no "let's set up a call."

**Timing Matters**:
- Send within 24-48 hours of milestone achievement
- Don't wait for formal QBR or check-in meeting
- Strike while success is fresh and visible

**Who to CC**: Consider copying their manager or executive sponsor if the milestone was significant and visibility helps your champion.

**When NOT to use this pattern**:
- Routine product usage (not every login is a milestone)
- Internal team milestones that don't impact customer (your company hit a goal, not theirs)
- Milestones the customer doesn't care about (you think it's impressive but they don't)
- When renewal negotiation is active (don't mix celebration with commercial pressure)

**Authenticity Check**: Would you send this email even if there was no expansion opportunity? If not, rewrite to be genuinely celebratory.

---

## Common Milestones Reference

**Go-Live Milestones**:
- User count targets (exceeded expected adoption)
- Timeline achievements (faster than projected)
- Department/site rollouts (expanded beyond initial scope)
- Integration completions (connected to other systems)

**ROI Milestones**:
- Payback period hit early
- Cost savings targets exceeded
- Efficiency gains (time savings, error reduction)
- Revenue impact (if product drives revenue)

**Usage Milestones**:
- Volume thresholds (records processed, transactions, users active)
- Feature adoption (advanced capabilities now in use)
- API/integration volume (system-to-system activity)
- Compliance/audit events (clean audits, zero findings)

**Time-Based Milestones**:
- 6-month mark (early proof of value)
- 1-year anniversary (established partnership)
- Multi-year renewals (long-term commitment)

**Expansion Milestones**:
- New department adoption
- Geographic expansion (new sites/regions)
- New use case implementation
- Executive sponsorship elevation

---

## Example Output

```markdown
---
generated_by: sales-communications/email_milestone_celebration
generated_on: 2025-11-15T10:30:00Z
deal_id: GlobalPharma
sources:
  - sample-data/Runtime/Sessions/GlobalPharma/deal.md
  - sample-data/Runtime/Sessions/GlobalPharma/artifacts/discovery_notes_2025-09-15.md
  - sample-data/Runtime/_Shared/style/ae_welf_corpus.md
---

**Subject**: Congratulations on go-live

Hi Jim,

Congratulations to you and the team on successfully going live with 2,500 users across Quality and Regulatory this week. You not only hit your 6-week timeline but exceeded your initial 2,000-user target by 25%. This is a testament to how well your team executed the implementation and how committed everyone was to solving those audit readiness challenges you shared back in September. You're already seeing the efficiency gains we discussed, and I know this is just the beginning. As your Manufacturing team sees what Quality accomplished, I imagine they'll be excited about the possibilities. Looking forward to seeing the impact continue to grow.

Best,
Welf Ludwig
Account Executive
rep@company.com
```

---

**End of Pattern: email_milestone_celebration**
