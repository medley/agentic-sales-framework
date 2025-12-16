# Email: Check-In

**Pattern**: email_check_in
**Type**: Customer-facing email
**Timing**: After 1-2 weeks of no response
**Purpose**: Gentle re-engagement, give them an out, keep door open

---

## When to Use

Send this email when a deal has gone silent to:
- Acknowledge the silence without creating pressure
- Give the prospect permission to say "not now"
- Preserve the relationship for future engagement
- Gracefully accept that the deal may be dead
- Offer a specific reconnect timeframe (next quarter, next year)

**NOT for**:
- Active deals with recent contact (use email_simple_followup)
- Proposals that need urgency (use email_proposal_nudge)
- Scheduled follow-ups (use email_simple_followup)
- Deals where you have a specific reason to re-engage (use pattern with new value)

**Trigger Phrases**:
- "Check in with {DEAL}"
- "Haven't heard back from {NAME}"
- "Gentle follow-up on {DEAL}"
- "{DEAL} went quiet"
- "Re-engage {DEAL}"
- "Soft touch with {COMPANY}"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Primary contact name (who to email)
   - Last contact date (to reference timing)
   - What you were following up on (proposal, demo, discovery call, etc.)

**OPTIONAL**:
- Email style corpus (for tone matching)
- Brand guidelines (for signature formatting)

**NOT NEEDED**:
- Methodology stage inventory
- Detailed qualification data
- Business drivers or pain points (this is relationship preservation, not advancement)

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Recipient name**: Primary contact or last person you spoke with
- **Last contact date**: From History section (most recent interaction)
- **Last interaction type**: What you were following up on (proposal sent, demo scheduled, discovery call held, etc.)
- **Time elapsed**: Calculate days/weeks since last contact

**Example History Entry to Parse**:
```markdown
### 2025-10-28 - Sent Proposal: Standard Plan + Implementation
- Sent proposal to David Martinez (VP Operations)
- Proposed: Standard plan ($48K ACV), 20-hour implementation, 12-month term
- Next: Follow up by Nov 4 if no response
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system for tone matching. Keep output brief and warm, not formal.

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply signature formatting only

---

## Email Structure

### Subject Line
**Formula**: Keep under 8 words, acknowledge the gap, no pressure

**Options**:
- "Checking in - {Company}"
- "Re: {Company} - Still Interested?"
- "Quick question about {Company}"
- "Is this still on your radar?"
- "Touching base - {Project/Topic}"

**Avoid**:
- Urgency ("Time sensitive...")
- Multiple question marks ("Still interested???")
- Desperate language ("One more try...")
- Generic subject ("Following up")

**Example**: "Checking in - AcmeCorp"

### Body (Single Paragraph)
**Purpose**: Acknowledge silence, assume timing changed, offer easy out, keep door open

**Structure**: 4-6 sentences, 70-110 words total

**Template**:
```
Hi {FIRST_NAME},

{Acknowledge the silence and last interaction}. {Assume timing or priorities changed}.
{Explicitly give permission to say "not now"}. {Offer specific reconnect timeframe}.
{Make it easy to opt out completely}. {Warm closing}.

{Closing},
{Signature}
```

**Example 1 (Post-Proposal Silence)**:
```
Hi David,

I haven't heard back since sending the proposal a few weeks ago, so I'm guessing
timing or priorities shifted on your end. That happens - no worries at all.

If this isn't a focus right now, just let me know and I'm happy to reconnect next
quarter when things might be different. Or if you'd prefer I close the file
completely, that's perfectly fine too.

Either way, thanks for your time earlier this year.

Best,
Sarah
```

**Example 2 (Post-Discovery No-Show)**:
```
Hi Jennifer,

We had a discovery call scheduled a couple weeks back, but I never heard from you
after you couldn't make it. I'm assuming things got busy or priorities changed.

Totally understand if this isn't the right time. Should I check back in Q1, or
would you prefer I take you off my follow-up list?

No hard feelings either way - just want to respect your time.

Thanks,
Michael
```

**Example 3 (Ghosted After Demo)**:
```
Hi Lisa,

I followed up a few times after our demo last month but haven't heard back, so
I'm guessing the project got deprioritized or you went another direction.

If it makes sense to reconnect later this year, I'm happy to reach out in the
fall. Otherwise, no worries at all - I'll close the file on my end.

Appreciate the time you spent with us.

Cheers,
Tom
```

**Example 4 (Multiple Failed Attempts)**:
```
Hi Kevin,

I've reached out a few times over the past few weeks but haven't been able to
connect. I know inboxes get overwhelming, so no worries if this just isn't a
priority right now.

Should I follow up in a few months when bandwidth might be better? Or would you
prefer I don't reach out again?

Either way, thanks for considering us.

Best regards,
Anna
```

### Closing Options
**Casual**:
- "Best,"
- "Thanks,"
- "Cheers,"
- "Talk later,"

**Professional**:
- "Best regards,"
- "Thank you,"
- "All the best,"

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_check_in
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
- Total body: 70-110 words (excluding subject and signature)
- Single paragraph only (no bullet lists, no sections, no multiple choice options)
- NO urgency language, NO pressure tactics, NO business driver reminders
- Explicitly give permission to opt out
- Assume deal may be dead (not just delayed)
- Warm but professional tone (not desperate or needy)

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_check_in_{DATE}.md`

**Filename format**: `email_check_in_2025-11-15.md`

---

## Error Handling

**Missing last contact date**:
- Use vague timeframe: "a few weeks ago", "last month", "earlier this year"

**Missing last interaction type**:
- Use generic reference: "our last conversation", "when we connected", "after we spoke"

**Missing recipient name**:
- Use generic salutation: "Hi there," or "Hi team,"

**No clear what you were following up on**:
- Generic: "I followed up a couple times but haven't heard back..."

---

## Check-In Email Best Practices

**Acknowledge Reality**: Don't pretend everything is fine. Address the silence directly.

**Give Permission to Exit**: Make it easy to say "not interested" or "not now". This reduces guilt and increases honest responses.

**No Pressure**: This email is the opposite of a sales push. You're preserving the relationship, not forcing a decision.

**Offer Specific Timeframes**: "Check back in Q1" is better than "let me know when timing is better" (too vague).

**Make Opt-Out Easy**: "Should I close the file?" or "Would you prefer I don't follow up again?" - direct and respectful.

**Timing**:
- After 1-2 weeks of no response to previous follow-ups
- After 3+ unanswered emails/calls
- When deal stage shows no activity for 2+ weeks
- Before giving up completely (last attempt to keep door open)

**When NOT to use this pattern**:
- Active deals with recent contact (use email_simple_followup instead)
- Proposals where you have legitimate urgency (use email_proposal_nudge)
- When you have new value to offer (lead with value, not "checking in")
- After only 1 unanswered email (too soon)

**Why This Works**:
- Low pressure increases response rate
- Permission to exit reduces guilt that causes ghosting
- Respectful tone preserves relationship for future
- Many "dead" deals come back months/years later if you stay professional

---

## Example Output

```markdown
---
generated_by: sales-communications/email_check_in
generated_on: 2025-11-15T14:20:00Z
deal_id: AcmeCorp
sources:
  - sample-data/Runtime/Sessions/AcmeCorp/deal.md
  - sample-data/Runtime/_Shared/style/ae_sarahchen_corpus.md
---

**Subject**: Checking in - AcmeCorp

Hi David,

I haven't heard back since sending the proposal a few weeks ago, so I'm guessing
timing or priorities shifted on your end. That happens - no worries at all.

If this isn't a focus right now, just let me know and I'm happy to reconnect next
quarter when things might be different. Or if you'd prefer I close the file
completely, that's perfectly fine too.

Either way, thanks for your time earlier this year.

Best,
Sarah Chen
Senior Account Executive
Example Corp Solutions
sarah.chen@example.com | (555) 123-4567
```

---

**End of Pattern: email_check_in**
