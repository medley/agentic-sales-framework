# Email: Reschedule Request

**Pattern**: email_reschedule_request
**Type**: Customer-facing email
**Timing**: As soon as conflict discovered
**Purpose**: Request meeting time change, minimize inconvenience, maintain professionalism

---

## When to Use

Send this email to:
- Notify customer of scheduling conflict requiring meeting change
- Respond to customer's request to reschedule
- Address technical issues preventing original meeting time
- Handle travel delays or emergencies affecting availability
- Proactively move a meeting due to higher-priority customer conflict

**NOT for**:
- Canceling without rescheduling (requires phone call)
- Postponing indefinitely (suggests lack of commitment)
- Moving meetings more than once (damages credibility)
- Routine calendar adjustments made days/weeks in advance

**Trigger Phrases**:
- "Reschedule meeting with {DEAL}"
- "Need to move our call with {NAME}"
- "Conflict with {MEETING}"
- "Can we move our {EVENT}"
- "Change meeting time for {DEAL}"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Stakeholder name (recipient)
   - Current scheduled meeting (date, time, type)
3. Alternative meeting times (2-3 specific options with dates/times)
4. Reason for reschedule (keep brief, don't over-explain)

**OPTIONAL**:
- Email style corpus (for tone matching)
- Brand guidelines (for signature formatting)
- Calendar booking link (for convenience)

**NOT NEEDED**:
- Methodology stage inventory
- Detailed deal qualification data
- Meeting agenda or objectives

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Recipient name**: Primary contact for scheduled meeting
- **Original meeting**: Date, time, and type from D7 tasks or History
- **Meeting purpose**: Discovery, demo, technical review, etc.

**Example D7 Task to Parse**:
```markdown
## D7 Tasks (This Week)
- [ ] Discovery call with Sarah Chen - Wednesday 11/20 at 2:00pm ET
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system for tone matching (maintain apologetic but professional tone)

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply signature formatting only

---

## Email Structure

### Subject Line
**Formula**: Clear, specific, no ambiguity about purpose

**Options**:
- "Need to reschedule {DAY}" (e.g., "Need to reschedule Wednesday")
- "Moving our {EVENT}" (e.g., "Moving our discovery call")
- "Schedule change for {DAY} meeting"
- "Quick schedule update"

**AVOID**:
- Vague subjects like "Quick question" or "Following up"
- Apologetic subjects like "So sorry but..."

### Body Structure
**Purpose**: Apologize briefly, explain if necessary, offer alternatives immediately, maintain momentum

**Structure**: 60-100 words total, 4-6 sentences

**Template**:
```
Hi {FIRST_NAME},

{Brief apology for schedule change}. {Optional: One-sentence reason if appropriate}. {Propose 2-3 specific alternative times}. {Optional: Offer calendar link for convenience}. {Reassure commitment/maintain momentum}.

{Closing},
{Signature}
```

---

## Examples

### Example 1: Internal Conflict (Customer Priority)
```markdown
---
generated_by: sales-communications/email_reschedule_request
generated_on: 2025-11-15T09:45:00Z
deal_id: TechCorp
sources:
  - sample-data/Runtime/Sessions/TechCorp/deal.md
---

**Subject**: Need to reschedule Wednesday

Hi Sarah,

I need to reschedule our discovery call scheduled for Wednesday at 2pm - an urgent customer issue came up that I need to handle. Could we move to Thursday at 10am, Thursday at 3pm, or Friday at 11am instead? I apologize for the late notice and really appreciate your flexibility. Still very much looking forward to learning about your reporting challenges.

Best regards,
Michael
```

### Example 2: Customer-Requested Reschedule
```markdown
---
generated_by: sales-communications/email_reschedule_request
generated_on: 2025-11-15T14:20:00Z
deal_id: GlobalPharma
sources:
  - sample-data/Runtime/Sessions/GlobalPharma/deal.md
---

**Subject**: Moving our demo to next week

Hi Jim,

No problem at all on moving Tuesday's demo - I completely understand. How about Monday 11/25 at 2pm, Tuesday 11/26 at 10am, or Wednesday 11/27 at 1pm? Here's my calendar link if those don't work and you want to pick a time that works best for you: [calendar link]. Looking forward to showing you the Salesforce integration examples we prepared.

Best,
Welf
```

### Example 3: Technical Issue
```markdown
---
generated_by: sales-communications/email_reschedule_request
generated_on: 2025-11-15T10:05:00Z
deal_id: MedDevice_Inc
sources:
  - sample-data/Runtime/Sessions/MedDevice_Inc/deal.md
---

**Subject**: Quick schedule update for today

Hi David,

I'm having technical issues with Zoom this morning and want to make sure we have a solid connection for our technical review. Can we push to this afternoon at 2pm or 4pm, or would tomorrow morning at 9am work better? I apologize for the inconvenience and want to ensure you get the full value from this session.

Talk soon,
Anna
```

### Example 4: Travel Delay
```markdown
---
generated_by: sales-communications/email_reschedule_request
generated_on: 2025-11-15T06:30:00Z
deal_id: RetailCo
sources:
  - sample-data/Runtime/Sessions/RetailCo/deal.md
---

**Subject**: Moving our 10am call

Hi Lisa,

My flight was delayed this morning and I won't be able to make our 10am call from a quiet location. Could we move to 1pm today, 9am tomorrow, or 3pm tomorrow? I really appreciate your understanding and want to make sure I can give you my full attention when we connect.

Best regards,
Tom
```

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_reschedule_request
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
- Total body: 60-100 words (excluding subject and signature)
- Single paragraph preferred (maximum 2 short paragraphs)
- Apologize once, don't grovel or over-explain
- Provide 2-3 specific alternative times (exact dates/times)
- Maintain forward momentum (still interested, still prepared)
- No excuses or lengthy explanations

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_reschedule_request_{DATE}.md`

**Filename format**: `email_reschedule_request_2025-11-15.md`

---

## Error Handling

**Missing original meeting details**:
- Prompt user: "Which meeting are you rescheduling? I need the original date/time."

**No alternative times provided**:
- Suggest: "Please provide 2-3 specific alternative times you're available."

**Missing recipient name**:
- Use generic salutation: "Hi there," or reference company: "Hi {COMPANY} team,"

**Vague reason for reschedule**:
- Default to professional: "Something came up that requires my attention"
- Don't invent specific reasons

---

## Reschedule Request Best Practices

**Timing**: Send as soon as you know about the conflict, ideally 24+ hours before original meeting

**Brevity**: Keep it short. They don't need a long explanation, they need new options.

**Specificity**: Provide exact dates and times, not "sometime next week"

**Quantity**: Offer 2-3 alternatives. More than 3 creates decision paralysis.

**Tone**: Apologetic but not groveling. Professional but warm.

**Accountability**: Own the change without excessive excuses

**Momentum**: Remind them you're still prepared and interested

**Options**: Include calendar link if available to reduce back-and-forth

**Frequency**: Never reschedule the same meeting twice - damages credibility

**Explanation Guidelines**:
- Customer conflict: "An urgent customer issue came up" (shows priorities)
- Internal issue: "Something came up that requires my attention" (professional, vague)
- Their request: "No problem at all" (gracious, accommodating)
- Technical: "Having technical issues with [tool]" (specific, valid)
- Travel: "Flight delayed" or "Travel issue" (brief, factual)

**AVOID**:
- Over-apologizing: "I'm so incredibly sorry, this is completely my fault..."
- Over-explaining: "My boss scheduled a meeting and then my car broke down and..."
- Vague alternatives: "Maybe sometime next week?"
- Indefinite postponement: "Let's reconnect when things calm down"
- Multiple reschedules of the same meeting

**When to call instead of email**:
- Rescheduling within 2 hours of meeting time
- Second time rescheduling same meeting
- Very senior stakeholder (VP+)
- Critical deal milestone meeting

---

## Example Output

```markdown
---
generated_by: sales-communications/email_reschedule_request
generated_on: 2025-11-15T09:45:00Z
deal_id: TechCorp
sources:
  - sample-data/Runtime/Sessions/TechCorp/deal.md
  - sample-data/Runtime/_Shared/style/ae_michael_corpus.md
---

**Subject**: Need to reschedule Wednesday

Hi Sarah,

I need to reschedule our discovery call scheduled for Wednesday at 2pm - an urgent customer issue came up that I need to handle. Could we move to Thursday at 10am, Thursday at 3pm, or Friday at 11am instead? I apologize for the late notice and really appreciate your flexibility. Still very much looking forward to learning about your reporting challenges.

Best regards,
Michael Davis
Account Executive
mdavis@company.com
```

---

**End of Pattern: email_reschedule_request**
