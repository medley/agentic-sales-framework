# Email: Asking for Favor

**Pattern**: email_asking_for_favor
**Type**: Customer-facing email (existing customers)
**Timing**: When you need something from them
**Purpose**: Request reference, case study, testimonial, intro - make ask clear and easy to decline

---

## When to Use

Send this email to:
- Request reference call for an active prospect
- Ask for written case study or testimonial
- Seek LinkedIn recommendation or public endorsement
- Request introduction to another department/contact
- Invite customer to speak at event or webinar
- Request logo usage permission for marketing

**NOT for**:
- Cold outreach to prospects (use discovery patterns)
- Negotiation or closing asks (use deal advancement patterns)
- Upsell/cross-sell opportunities (use expansion patterns)
- Technical support requests (use internal channels)

**Trigger Phrases**:
- "Ask {NAME} for reference"
- "Request case study from {DEAL}"
- "Get testimonial from {CUSTOMER}"
- "Request intro to {PERSON} from {DEAL}"
- "Ask {CUSTOMER} to speak at event"
- "Get logo permission from {DEAL}"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Customer is live/implemented (not in sales cycle)
   - Relationship strength indicator (champion, satisfied user, etc.)
   - Recent positive outcomes or value delivered
3. **Relationship requirement**: Must be existing customer or strong champion
4. **Timing requirement**: Customer has experienced value (ideally 60+ days post-implementation)

**OPTIONAL**:
- Email style corpus (for tone matching)
- Brand guidelines (for signature formatting)
- Deal history showing positive interactions

**NOT NEEDED**:
- Methodology stage inventory (deal already closed)
- Qualification data
- Active sales cycle context

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Recipient name**: Customer contact (ideally champion)
- **Relationship quality**: Note any champion indicators, positive feedback, recent wins
- **Value delivered**: What results have they achieved?
- **Time since go-live**: When did they start seeing value?

**Example Deal Context to Parse**:
```markdown
## Stakeholders
- Jim Selby (Champion) - VP Quality, very satisfied with inspection automation results

## History
- 2025-09-15: Go-live, 40% reduction in inspection time achieved
- 2025-10-30: QBR - Jim mentioned team loves the new workflow
```

### 2. Define Your Ask

**Be specific about**:
- What you're asking for (reference call, case study, intro)
- Time commitment required (15-min call, 30-min interview, one email intro)
- When you need it by (if time-sensitive)
- Who benefits (prospect in similar industry, your marketing team, etc.)

### 3. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system for tone matching (keep genuine and humble)

### 4. Load Brand Guidelines (Section 2 of _common.md)

Apply signature formatting only

---

## Email Structure

### Subject Line
**Formula**: Clear ask, no mystery, under 8 words

**Options**:
- "Quick favor to ask"
- "Reference call request"
- "Would you be open to a case study?"
- "Customer story opportunity"
- "Quick intro request"

### Body Structure
**Purpose**: Context relationship, make specific ask, state time commitment, make it easy to decline

**Structure**: 100-140 words total

**Template**:
```
Hi {FIRST_NAME},

{Brief context: relationship/value delivered}. {Transition to ask}. {Specific ask with details: what, why, time required}. {Make it easy to decline gracefully}. {Express gratitude}.

{Closing},
{Signature}
```

### Example 1 (Reference Request)

```
Hi Jim,

I've been thinking about how well the inspection automation has been working for your team - the efficiency gains have been impressive. I'm working with a prospect in medical device manufacturing who's facing similar challenges, and I think hearing your experience would really help them understand the value.

Would you be open to a 15-minute reference call with their VP of Quality next week? Happy to send a brief on what they're evaluating. Totally understand if the timing doesn't work - no pressure at all.

Either way, thanks for being such a great partner.

Best,
Welf
```

### Example 2 (Case Study Request)

```
Hi Sarah,

The results your team has achieved with the new reporting system have been remarkable - I know you mentioned the executive team was thrilled with the visibility improvements. Our marketing team is looking to feature customer success stories, and I immediately thought of GlobalPharma.

Would you be open to a 30-minute interview for a written case study? We'd keep it focused on business outcomes and get your approval before publishing anything. If this isn't the right time or doesn't align with your communication plans, I completely understand.

Thanks for considering it.

Best regards,
Michael
```

### Example 3 (Introduction Request)

```
Hi David,

I hope the Salesforce integration is still going well for the sales team. Quick favor to ask: I'm working with your finance department on a separate project, and it would be helpful to connect with whoever leads financial systems on your side.

Would you be comfortable making a brief email introduction to that person? Just need to understand their current reporting setup - I can take it from there. No worries if this doesn't make sense or crosses organizational boundaries.

Appreciate you either way.

Cheers,
Tom
```

### Closing Options
**Casual** (use with champions):
- "Best,"
- "Thanks again,"
- "Appreciate you,"
- "Cheers,"

**Professional** (use with newer relationships):
- "Best regards,"
- "Thank you,"
- "Much appreciated,"

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_asking_for_favor
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - sample-data/Runtime/_Shared/style/{style_file}  # if loaded
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
---
```

### 2. Compose Email Body

**CRITICAL CONSTRAINTS**:
- Total body: 100-140 words (excluding subject and signature)
- Make the ask crystal clear (what + time commitment)
- Acknowledge the relationship/value first
- Make it easy to say no (give them an out)
- Express gratitude regardless of outcome
- No pressure language, no urgency unless genuinely time-sensitive

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_asking_for_favor_{DATE}.md`

**Filename format**: `email_asking_for_favor_2025-11-15.md`

---

## Error Handling

**Customer not live/implemented yet**:
- Warn user: "This pattern is for existing customers. {DEAL} appears to be in sales cycle. Consider waiting until they've experienced value."
- Ask: "Do you want to proceed anyway?"

**No relationship quality data**:
- Prompt user: "I don't see champion indicators or positive feedback. What's your relationship with {CONTACT}?"
- Suggest: Consider building more relationship equity before asking

**Missing value delivered data**:
- Prompt user: "What value has {DEAL} achieved? This context makes the ask feel less transactional."

**Ask unclear**:
- Prompt user: "What specifically are you asking for? (reference call, case study, intro, testimonial, event speaking, logo permission)"

---

## Asking for Favors Best Practices

**Relationship First**: Only ask customers who have experienced real value and have positive sentiment. Wait 60+ days post-go-live.

**Be Specific**: Don't make them guess. State exactly what you're asking for, time required, and when you need it.

**Easy Out**: Always give them graceful way to decline. Use phrases like:
- "Totally understand if the timing doesn't work"
- "No pressure at all"
- "No worries if this doesn't make sense"
- "I completely understand if..."

**Acknowledge Value Exchange**: Reference the value they've received, but don't make the ask feel transactional ("You owe me because we delivered results").

**Timing Matters**:
- Best: Right after they mention positive results or praise your solution
- Good: During QBR when discussing wins
- Risky: During renewal period (feels transactional)
- Bad: During implementation issues or support escalations

**Reciprocity**: When appropriate, offer something in return:
- "Happy to return the favor anytime"
- "I'll send you early access to our new feature"
- "Let me know how I can support your initiatives"

**Common Asks and Time Commitments**:
- Reference call: 15-30 minutes
- Written testimonial: 5-10 minutes (draft for them to edit)
- Case study interview: 30-45 minutes
- LinkedIn recommendation: 5 minutes
- Email introduction: 2 minutes
- Logo usage: 1 minute (legal approval may take longer)
- Event speaking: 1-2 hours (prep + presentation)

**When NOT to Use This Pattern**:
- Customer is having issues or recently escalated problem
- During active renewal negotiation (feels like leverage)
- Customer is new (< 60 days live)
- You haven't delivered measurable value yet
- Relationship is transactional, not strategic
- They've already done multiple favors recently (favor fatigue)

---

## Example Output

```markdown
---
generated_by: sales-communications/email_asking_for_favor
generated_on: 2025-11-15T16:45:00Z
deal_id: GlobalPharma
sources:
  - sample-data/Runtime/Sessions/GlobalPharma/deal.md
  - sample-data/Runtime/_Shared/style/ae_welf_corpus.md
---

**Subject**: Quick favor to ask

Hi Jim,

I've been thinking about how well the inspection automation has been working for your team - the efficiency gains have been impressive. I'm working with a prospect in medical device manufacturing who's facing similar challenges, and I think hearing your experience would really help them understand the value.

Would you be open to a 15-minute reference call with their VP of Quality next week? Happy to send a brief on what they're evaluating. Totally understand if the timing doesn't work - no pressure at all.

Either way, thanks for being such a great partner.

Best,
Welf Ludwig
Account Executive
rep@company.com
```

---

**End of Pattern: email_asking_for_favor**
