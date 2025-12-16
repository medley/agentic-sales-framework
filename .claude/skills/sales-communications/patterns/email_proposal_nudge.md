# Email: Proposal Nudge

**Pattern**: email_proposal_nudge
**Type**: Customer-facing email
**Timing**: 3-5 days after proposal delivery with no response
**Purpose**: Restart stalled conversation, uncover objections, create urgency

---

## When to Use

Send this email when a proposal has gone quiet to:
- Restart conversation without appearing desperate
- Uncover hidden objections or concerns
- Create urgency through business drivers (not arbitrary deadlines)
- Offer alternative paths forward (different scope, POC, call)
- Position for either close or graceful disqualification

**Trigger Phrases**:
- "Draft proposal nudge for {DEAL}"
- "Check in on {DEAL} proposal"
- "Follow up on stalled proposal"
- "Proposal follow-up email"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Recent proposal sent (in History or Generated Artifacts section)
   - Proposal date (to calculate days since sent)
   - Current stage should be "Proposal", "Negotiation", or "Pending Decision"
   - Economic Buyer identified (who needs to respond)
   - Decision Process timeline (their internal approval cycle)
3. Email style corpus (4-tier loading per _common.md section 3)

**OPTIONAL**:
- Brand guidelines (for formatting, tone)
- Methodology stage inventory (for Proposal/Negotiation best practices)

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Proposal sent date**: From History or Generated Artifacts
- **Days since proposal**: Calculate from sent date to today
- **Primary contact/Economic Buyer**: From MEDDPICC section
- **Proposed solution**: From proposal or MEDDPICC Metrics (what you proposed)
- **Business drivers**: From MEDDPICC Identify Pain (why they need this)
- **Decision timeline**: From MEDDPICC Decision Process (when they said they'd decide)
- **Competition**: From MEDDPICC (are they evaluating alternatives?)
- **Last interaction**: Most recent History entry (call, email response, etc.)

**Example History Entry to Parse**:
```markdown
### 2025-11-08 - Sent Proposal: Enterprise Plan + Professional Services
- Sent detailed proposal to Jane Smith (Economic Buyer) and Michael Chen (IT Director)
- Proposed: Enterprise plan ($144K ACV), 40-hour implementation package, 12-month term
- Business case: 80% reduction in reporting overhead = $180K annual savings (positive ROI)
- Decision timeline: They mentioned need to decide by Nov 30 for Q1 deployment
- Next: Follow up by Nov 13 if no response
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system. **Tone critical for nudge emails**:
- Professional but warm (not desperate)
- Create urgency through their business drivers (not yours)
- Offer help/alternatives (not pressure)

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply company email formatting if available

### 4. Load Methodology Guidance (Section 4 of _common.md)

If MEDDPICC stage inventory available:
- Check if all qualification criteria met before sent proposal
- Identify potential objections based on incomplete MEDDPICC fields
- Position follow-up to advance or disqualify cleanly

---

## Email Structure

### Subject Line
**Formula**: Balance urgency with value

**Options** (choose based on style corpus):
- Direct: "Re: {Company} Proposal - Quick Question"
- Value-focused: "Re: {Business Driver} - Timeline Question"
- Assumption close: "Re: Next Steps for {Project Name}"
- Humble: "Did I miss something on the proposal?"

**Avoid**:
- "Following up..." (sounds desperate)
- "Just checking in..." (no value)
- Arbitrary urgency ("Expires Friday!")

**Example**: "Re: AcmeCorp Reporting Platform - Timeline Question"

### Opening Paragraph
**Purpose**: Acknowledge silence, assume positive intent, ask for feedback

**Template**:
```
Hi {FIRST_NAME},

I know you and {other stakeholders} are busy, so I'll keep this brief. I wanted
to check in on the proposal I sent {number} days ago for {project name}.

{Humble question acknowledging you might have missed something}
```

**Example**:
```
Hi Jane,

I know you and Michael are busy with year-end planning, so I'll keep this brief.
I wanted to check in on the Enterprise platform proposal I sent last week.

I haven't heard back yet - did the proposal miss the mark on something? I'd rather
know now if there are concerns so we can address them or gracefully step aside if
it's not the right fit.
```

**Tone Notes**:
- Assume they're busy (not ignoring you)
- Give permission to say no (reduces pressure, increases honesty)
- Offer to address concerns (helpful, not pushy)

### Business Driver Reminder (1-2 sentences)
**Purpose**: Reconnect to why this matters to THEM (not you)

**Template**:
```
{Their business driver from discovery/demo} - {quantified impact if available} -
{their timeline if mentioned}.
```

**Example**:
```
We originally connected because your team was spending 50+ hours/month on manual
reporting, and you mentioned needing a solution operational by January 15 to
support your annual planning cycle. That date is coming up quickly.
```

**Avoid**:
- Your deadlines ("Our Q4 ends...")
- Generic value props ("Improve efficiency...")
- Anything about your quota/needs

### Direct Question Section
**Purpose**: Uncover the real objection or status

**Approach 1: Multiple Choice** (makes it easy to respond)
```
Where are you in the evaluation process?

a) Still reviewing internally - need more time
b) Comparing against other vendors - need differentiation help
c) Proposal looks good but [specific concern] - need to discuss
d) Not moving forward - can share why?
e) Ready to move forward - need next steps
```

**Approach 2: Direct Ask** (simpler)
```
I'd love a quick update on where things stand. If there are concerns with the
proposal - pricing, timeline, scope, technical fit - let's discuss. If you've
decided to go another direction, I completely understand and would appreciate
knowing so I can follow up at a better time.
```

**Approach 3: Offer Alternatives** (creates options)
```
A few options to move forward:

1. **Full proposal as sent**: If it looks good, I can send contract and kickoff
   plan for Jan 15 deployment
2. **Pilot/POC first**: If there's uncertainty, we could do a 30-day proof of
   concept before full commitment
3. **Scope adjustment**: If budget is a concern, I can propose a phased approach
   starting with core reporting features
4. **More time**: If timing is off, I'm happy to reconnect in {month}

What makes most sense for your team?
```

**Choose Based On**:
- **Multiple choice**: When you're unsure what the blocker is
- **Direct ask**: When you have strong relationship, can handle direct feedback
- **Offer alternatives**: When you suspect pricing/scope is the issue

### Urgency Creation (Optional)
**Purpose**: Create urgency through THEIR drivers, not yours

**Only include if TRUE**:
- Their stated decision timeline is approaching
- Business driver has time sensitivity (budget cycle, compliance deadline)
- Market condition creates urgency (price increase, competitor action)

**Template**:
```
{Their timeline reminder}: {Consequence of delay}.
```

**Good Examples**:
```
Your mentioned timeline: Need to decide by Nov 30 for Q1 deployment. If we kick
off by mid-December, we can still hit your Jan 15 go-live date. Much later than
that and we're pushed into Q2.
```

```
Budget cycle: You mentioned Q4 budget is approved and available. If we don't move
by month-end, that budget may need to be re-justified in the new fiscal year.
```

**Bad Examples** (avoid):
```
❌ "Our Q4 promotion ends Friday" (your urgency, not theirs)
❌ "This price is only good until..." (feels manipulative unless true regulatory/cost change)
❌ "Other companies are buying" (social proof = pressure)
```

### Closing Paragraph
**Purpose**: Make it easy to respond, remain professional

**Template**:
```
{Easy response ask}. {Gratitude}. {Open door}.

{Closing},
{Signature}
```

**Example**:
```
Even a quick "still reviewing" or "went another direction" reply would be hugely
helpful. Thanks for your time, and let me know if any questions come up.

Best regards,
Sarah Chen
```

**Tone**: Professional, not needy. Make responding easy (yes/no/update all acceptable).

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_proposal_nudge
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
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

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_proposal_nudge_{DATE}.md`

**Filename format**: `email_proposal_nudge_2025-11-14.md`

---

## Error Handling

**No proposal found in History or Generated Artifacts**:
- BLOCK: Prompt user "I don't see a proposal in the deal history. Add proposal details first?"

**Missing proposal date**:
- Can't calculate days since sent
- Use generic "last week" or "recently"

**Missing Economic Buyer**:
- Send to primary contact from Stakeholders
- Generic salutation if no stakeholders

**Missing Decision Timeline**:
- Omit urgency section
- Focus on uncovering objections only

**Missing Business Drivers**:
- Generic "original conversation" reference
- Weaker email without specific pain points

---

## Proposal Nudge Best Practices

### Timing
- **First nudge**: 3-5 business days after proposal sent
- **Second nudge**: 7-10 days after first nudge
- **Third nudge**: Breakup email (different pattern - offer to close file)

### Tone
- **Helpful, not desperate**: Offer to solve their problem, not yours
- **Give permission to say no**: Reduces pressure, increases honesty
- **Assume positive intent**: They're busy, not ignoring you

### What to Avoid
- Appearing desperate ("Just following up again...")
- Creating fake urgency (arbitrary deadlines)
- Talking about your needs (quota, quarter-end)
- Long emails (keep under 150 words)
- Multiple follow-ups without new information

### Advanced Techniques
- **Offer alternatives**: Full deal, pilot, phased approach (gives them options)
- **Ask for referral**: "If this isn't priority, is there someone else at {company} who might benefit?"
- **Provide new value**: "Saw this case study and thought of your {pain point}" (attach resource)

---

## Example Output

```markdown
---
generated_by: sales-communications/email_proposal_nudge
generated_on: 2025-11-14T09:15:00Z
deal_id: AcmeCorp
sources:
  - sample-data/Runtime/Sessions/AcmeCorp/deal.md
  - sample-data/Runtime/_Shared/style/ae_sarahchen_corpus.md
---

**Subject**: Re: AcmeCorp Reporting Platform - Timeline Question

Hi Jane,

I know you and Michael are busy with year-end planning, so I'll keep this brief.
I wanted to check in on the Enterprise platform proposal I sent last week.

I haven't heard back yet - did the proposal miss the mark on something? I'd rather
know now if there are concerns so we can address them or gracefully step aside if
it's not the right fit.

We originally connected because your team was spending 50+ hours/month on manual
reporting, and you mentioned needing a solution operational by January 15 to
support your annual planning cycle. That date is coming up quickly.

Where are you in the evaluation process?

a) Still reviewing internally - need more time
b) Comparing against other vendors - need differentiation help
c) Proposal looks good but [specific concern] - let's discuss
d) Not moving forward - can share why?
e) Ready to move forward - need next steps

Your mentioned timeline: Decide by Nov 30 for Q1 deployment. If we kick off by
mid-December, we can still hit your Jan 15 go-live date. Much later than that
and we're pushed into Q2.

Even a quick "still reviewing" or "went another direction" reply would be hugely
helpful. Thanks for your time, and let me know if any questions come up.

Best regards,
Sarah Chen
Senior Account Executive
Example Corp Solutions
sarah.chen@example.com | (555) 123-4567
```

---

**Example Output (Alternative Approach - Offering Options)**

```markdown
---
generated_by: sales-communications/email_proposal_nudge
generated_on: 2025-11-14T09:15:00Z
deal_id: AcmeCorp
sources:
  - sample-data/Runtime/Sessions/AcmeCorp/deal.md
  - sample-data/Runtime/_Shared/style/ae_sarahchen_corpus.md
---

**Subject**: Re: AcmeCorp Proposal - A Few Options

Hi Jane,

Following up on the proposal I sent last week for the Enterprise reporting
platform. I haven't heard back, which usually means one of three things:

1. **Still evaluating** - Happy to give you more time or answer questions
2. **Concerns about scope/pricing** - I can propose alternatives (pilot, phased approach)
3. **Decided to go another direction** - Totally understand, just let me know

Your team mentioned needing this operational by Jan 15 for annual planning. If
that's still the target, we're getting close to the decision point.

What makes most sense for you?

Thanks,
Sarah
```

---

**End of Pattern: email_proposal_nudge**
