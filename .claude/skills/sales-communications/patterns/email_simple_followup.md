# Email: Simple Follow-Up

**Pattern**: email_simple_followup
**Type**: Customer-facing email
**Timing**: Before upcoming meeting/onsite/demo
**Purpose**: Brief confirmation, maintain momentum, express enthusiasm

---

## When to Use

Send this email to:
- Confirm an upcoming meeting, onsite visit, or demo
- Express anticipation for scheduled event
- Send quick reminder without detailed agenda
- Maintain warm relationship between formal interactions
- Wish someone well before weekend/holiday

**NOT for**:
- Recapping past meetings (use email_demo_followup or email_discovery_recap)
- Detailed next steps (use appropriate recap pattern)
- Technical follow-up with resources (use email_demo_followup)
- Proposal discussions (use email_proposal_nudge)

**Trigger Phrases**:
- "Looking forward to meeting {DEAL}"
- "See you next week at {DEAL}"
- "Quick follow-up to {DEAL}"
- "Simple reminder about {EVENT}"
- "Confirm meeting with {DEAL}"
- "Wish {NAME} a nice weekend"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic

**Optional (helpful but not required)**:
- Deal context from deal.md (for recipient name, event details)
- AE style corpus (for voice matching)

**If deal context missing**:
- Use generic salutation ("team", "all")
- Generate brief confirmation without specific details
- Set frontmatter: `status: "partial_data"`

**NOT NEEDED**:
- Methodology stage inventory
- Detailed deal qualification data
- Past meeting history beyond next scheduled event

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Recipient name**: Primary contact for upcoming event
- **Event details**: Next scheduled meeting/onsite from D7 tasks or History
- **Event date**: When the meeting is scheduled
- **Event type**: Discovery, demo, onsite, technical review, etc.

**Example D7 Task to Parse**:
```markdown
## D7 Tasks (This Week)
- [ ] Onsite visit with Jim Selby and team - Tuesday 11/21 at GlobalPharma HQ
```

### 2. Load Style Corpus (Optional)

Follow patterns/_voice_matching.md:
1. Detect active AE (deal.md owner field)
2. Load corpus (4-tier system)
3. Extract style patterns (greeting, closing, paragraph count, tone)
4. Apply to email generation
5. Run voice verification (3 checks) if corpus available
6. Rewrite once if needed
7. Log style_source in frontmatter

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply signature formatting only

---

## Email Structure

### Subject Line
**Formula**: Keep under 7 words, no "RE:" prefix needed

**Options**:
- "Looking forward to {DAY}" (e.g., "Looking forward to Tuesday")
- "See you {TIMEFRAME}" (e.g., "See you next week")
- "{DAY} meeting confirmed" (e.g., "Tuesday meeting confirmed")
- "Quick note before {EVENT}" (e.g., "Quick note before the onsite")

### Body: Default to single paragraph unless AE corpus prefers multiple short paragraphs
**Purpose**: Express enthusiasm, confirm readiness, invite last-minute questions

**Structure**: 3-5 sentences maximum (suggestion - adapt to corpus if available)

**Template**:
```
Hi {FIRST_NAME},

{Enthusiasm statement about upcoming event}. {Confirmation of readiness or team prep}. {Optional: mention what to expect or what you're bringing}. {Invitation for questions if anything changes}. {Optional: weekend/holiday well-wish if timing appropriate}.

{Closing},
{Signature}
```

**Example 1 (Onsite Visit)**:
```
Hi Jim,

Looking forward to meeting with you next week during the onsite. Just wanted to send a quick note to confirm we're all set and that our team is ready. If anything changes on your side, just let me know. Wishing you a relaxing weekend.

Best,
Welf
```

**Example 2 (Discovery Call Reminder)**:
```
Hi Sarah,

Quick note to confirm our discovery call tomorrow at 2pm ET. I'm looking forward to learning more about your reporting challenges and exploring how we might help. I'll send the Zoom link an hour before we connect.

Talk soon,
Michael
```

**Example 3 (Demo Confirmation)**:
```
Hi David,

Confirming we're set for the product demo on Thursday at 10am. Our team has prepared examples specific to your Salesforce integration use case. Let me know if you'd like us to focus on anything else.

Best regards,
Anna
```

**Example 4 (Pre-Weekend Check-In)**:
```
Hi Lisa,

Just wanted to check in before the weekend - no action needed, just confirming we're still on for Monday's technical review. Enjoy your weekend and we'll connect early next week.

Cheers,
Tom
```

### Closing Options
**Casual**:
- "Best,"
- "Talk soon,"
- "See you then,"
- "Cheers,"

**Professional**:
- "Best regards,"
- "Looking forward,"
- "Thank you,"

---

## Output Formatting

### Style Alignment

- Use these structure suggestions by default
- If AE corpus shows different preferences (paragraph count, length, tone), follow corpus instead
- **Corpus wins when conflict occurs**
- See references/template_override_protocol.md for full priority hierarchy

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_simple_followup
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - sample-data/Runtime/_Shared/style/{style_file}  # if loaded
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
---
```

### 2. Compose Email Body

### Target Length

**Default**: 80-120 words (acceptable range: 60-150)
**If AE corpus averages significantly different**: Match corpus instead

**CRITICAL CONSTRAINTS**:
- Single paragraph by default (no bullet lists, no headers, no sections - unless corpus shows different preference)
- No technical details, no ROI discussion, no detailed next steps
- No recap of past events (forward-looking only)
- Conversational tone, warm but professional

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_simple_followup_{DATE}.md`

**Filename format**: `email_simple_followup_2025-11-15.md`

---

## Error Handling

**Missing upcoming event in D7 or History**:
- Generate generic "looking forward to connecting" message
- Prompt user: "I don't see an upcoming event scheduled. What meeting should I reference?"

**Missing recipient name**:
- Use generic salutation: "Hi there," or "Hi team,"

**No event date/time**:
- Use vague timeframe: "soon", "next week", "in the coming days"

---

## Simple Follow-Up Best Practices

**Brevity**: Shorter is better. Aim for 80-100 words.

**Warmth**: Use friendly tone without being overly casual (avoid emojis unless AE corpus shows heavy usage)

**Low pressure**: No asks, no deadlines, no urgency. This is relationship maintenance.

**Forward-looking**: Reference upcoming event only, no past recaps.

**Timing**:
- 1-3 days before event: Confirmation and enthusiasm
- Friday afternoon: Weekend well-wishes
- Day before event: Brief reminder with logistical details

**When NOT to use this pattern**:
- If you need to recap a past meeting → use email_demo_followup or email_discovery_recap
- If you need to advance a stalled deal → use email_proposal_nudge
- If you need to provide resources or answer technical questions → use email_demo_followup

---

## Example Output

```markdown
---
generated_by: sales-communications/email_simple_followup
generated_on: 2025-11-15T16:30:00Z
deal_id: GlobalPharma
sources:
  - sample-data/Runtime/Sessions/GlobalPharma/deal.md
  - sample-data/Runtime/_Shared/style/ae_welf_corpus.md
---

**Subject**: Looking forward to next week

Hi Jim,

Looking forward to meeting with you next week during the onsite. Just wanted to send a quick note to confirm we're all set and that our team is ready. If anything changes on your side, just let me know. Wishing you a relaxing weekend.

Best,
Welf Ludwig
Account Executive
rep@company.com
```

---

**End of Pattern: email_simple_followup**
