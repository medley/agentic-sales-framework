# Email: Thank You

**Pattern**: email_thank_you
**Type**: Customer-facing email
**Timing**: Within 2-4 hours after meeting/call
**Purpose**: Express genuine gratitude without next steps, pure relationship maintenance

---

## When to Use

Send this email to:
- Thank stakeholder immediately after discovery call, demo, or meeting
- Acknowledge their time investment without asking for anything
- Build relationship warmth after initial introductions
- Express appreciation after technical review or onsite visit
- Pure gratitude message with NO forward motion required

**NOT for**:
- Recapping meeting content (use email_demo_followup or email_discovery_recap)
- Including next steps or asks (use email_simple_followup)
- Sending resources or technical details (use email_demo_followup)
- Advancing deal momentum (use appropriate recap pattern)

**Trigger Phrases**:
- "Thank you email to {NAME}"
- "Send thanks to {DEAL}"
- "Appreciate their time"
- "Quick thank you to {DEAL}"
- "Just say thanks to {NAME}"
- "Gratitude email for {DEAL}"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Stakeholder name (recipient)
   - Recent History entry showing completed meeting/call
   - Meeting type (discovery, demo, intro call, etc.)

**OPTIONAL**:
- Email style corpus (for tone matching)
- Brand guidelines (for signature formatting)

**NOT NEEDED**:
- Methodology stage inventory
- Detailed deal qualification data
- Future meeting schedule or D7 tasks

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Recipient name**: Primary contact from recent meeting
- **Meeting type**: Discovery, demo, intro call, technical review, onsite
- **Meeting date**: When it occurred (from History section)
- **Company context**: Brief reference to their situation if mentioned

**Example History Entry to Parse**:
```markdown
## History
- **2025-11-15**: Discovery call with Sarah Jenkins - discussed reporting pain points and compliance requirements
- **2025-11-08**: Intro call with David Chen - initial conversation about integration needs
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system for tone matching (keep output brief and authentic)

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply signature formatting only

---

## Email Structure

### Subject Line
**Formula**: Keep under 6 words, simple and genuine

**Options**:
- "Thank you, {FIRST_NAME}"
- "Thanks for your time today"
- "Appreciated the conversation"
- "Thank you for meeting"
- "Great talking with you"

### Body (1-2 Sentences Only)
**Purpose**: Pure gratitude, acknowledge their time, express appreciation

**Structure**: 60-100 words maximum, absolutely NO next steps

**Template**:
```
Hi {FIRST_NAME},

{Brief thank you statement}. {Acknowledgment of their time or what you appreciated}. {Optional: personal touch or well-wish}.

{Closing},
{Signature}
```

**Example 1 (Post-Discovery Call)**:
```
Hi Sarah,

Thank you for taking the time to walk me through your reporting challenges today. I really appreciated your candid insights about the compliance pressures your team is facing. Hope you have a great rest of your week.

Best,
Welf
```

**Example 2 (Post-Intro Call)**:
```
Hi David,

Thanks for the conversation this morning. I appreciate you sharing your perspective on the integration landscape at Acme Corp. Enjoy the rest of your day.

Cheers,
Michael
```

**Example 3 (Post-Demo)**:
```
Hi Lisa,

Thank you for making time for today's demo. I enjoyed hearing your team's questions and seeing how engaged everyone was with the Salesforce integration examples.

Best regards,
Anna
```

**Example 4 (Post-Onsite Visit)**:
```
Hi Jim,

Thanks to you and your team for the warm welcome during yesterday's onsite. I really appreciated the opportunity to meet everyone face-to-face and see your operation firsthand.

Thank you,
Tom
```

### Closing Options
**Casual**:
- "Best,"
- "Cheers,"
- "Thanks again,"
- "Appreciate it,"

**Professional**:
- "Best regards,"
- "Thank you,"
- "Gratefully,"
- "Sincerely,"

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_thank_you
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
- 1-2 short sentences or single paragraph only
- NO next steps, NO asks, NO meeting recaps with bullet points
- NO forward-looking statements about future calls/meetings
- NO resources, links, or attachments
- Authentic gratitude tone, warm but professional
- Focus purely on appreciation, not deal advancement

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_thank_you_{DATE}.md`

**Filename format**: `email_thank_you_2025-11-15.md`

---

## Error Handling

**Missing recent meeting in History**:
- Prompt user: "I don't see a recent meeting. What call or meeting should I thank them for?"
- DO NOT generate generic thank you without context

**Missing recipient name**:
- Use generic salutation: "Hi there," (but warn user this is less personal)

**No meeting type specified**:
- Use generic reference: "for taking the time to meet" or "for the conversation"

**Multiple stakeholders at meeting**:
- Ask user: "Should I thank {NAME1}, {NAME2}, or send to both?"

---

## Thank You Email Best Practices

**Extreme brevity**: This is the shortest email pattern. 60-80 words ideal.

**Authentic gratitude**: Be specific about what you appreciated (their insights, their time, their team's engagement)

**No ulterior motive**: Resist urge to add next steps, meeting recaps, or asks. Pure thank you only.

**Timing matters**: Send within 2-4 hours of meeting while it's fresh. Don't wait until next day.

**Personal touch**: Reference something specific from the conversation when possible (without recapping entire meeting)

**When to use vs. recap emails**:
- Use thank_you when: Relationship building is priority, no action needed, simple gratitude
- Use recap patterns when: Need to confirm next steps, provide resources, advance deal

**Tone calibration**:
- Match AE's natural style but err on side of warmth
- Avoid overly formal language ("I would like to express my gratitude")
- Avoid overly casual tone unless AE corpus shows consistent casual style

**What NOT to include**:
- Meeting recap or summary
- Next steps or action items
- "Let me know if you have questions"
- Resources, links, or attachments
- Deadlines or urgency
- Any form of ask or request

---

## Example Output

```markdown
---
generated_by: sales-communications/email_thank_you
generated_on: 2025-11-15T18:30:00Z
deal_id: GlobalPharma
sources:
  - sample-data/Runtime/Sessions/GlobalPharma/deal.md
  - sample-data/Runtime/_Shared/style/ae_welf_corpus.md
---

**Subject**: Thank you, Sarah

Hi Sarah,

Thank you for taking the time to walk me through your reporting challenges today. I really appreciated your candid insights about the compliance pressures your team is facing. Hope you have a great rest of your week.

Best,
Welf Ludwig
Account Executive
rep@company.com
```

---

**End of Pattern: email_thank_you**
