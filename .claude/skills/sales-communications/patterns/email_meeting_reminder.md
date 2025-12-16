# Email: Meeting Reminder

**Pattern**: email_meeting_reminder
**Type**: Customer-facing email
**Timing**: Day-of or day-before meeting
**Purpose**: Provide logistics, reduce no-shows, set expectations

---

## When to Use

Send this email to:
- Confirm meeting logistics 24 hours before or morning-of
- Provide Zoom links, dial-in numbers, or location details
- Share attendee list from your side
- Remind of agenda or attached materials
- Reduce no-show risk for important calls
- Provide building access or parking instructions for onsite visits

**NOT for**:
- Initial meeting invitation (use calendar invite)
- Warm relationship maintenance (use email_simple_followup)
- Recapping past meetings (use email_demo_followup or email_discovery_recap)
- Multiple days before meeting (use email_simple_followup)

**Trigger Phrases**:
- "Send meeting reminder for {MEETING}"
- "Day-of logistics for {DEAL}"
- "Confirm call details"
- "Send Zoom link to {CONTACT}"
- "Meeting logistics for {DEAL}"
- "Reminder email for tomorrow's call"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Stakeholder name (recipient)
   - Meeting date and time
   - Meeting type (discovery, demo, onsite, etc.)
3. Meeting logistics:
   - Zoom link OR physical address
   - Meeting duration
   - Your team's attendee list

**OPTIONAL**:
- Agenda document path (to attach or reference)
- Email style corpus (for tone matching)
- Brand guidelines (for signature formatting)
- Dial-in backup number
- Parking/building access instructions

**NOT NEEDED**:
- Methodology stage inventory
- Detailed deal qualification data
- Past meeting history

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Recipient name**: Primary contact for meeting
- **Meeting details**: Date, time, type from D7 tasks or History
- **Meeting purpose**: Discovery, demo, technical review, etc.
- **Duration**: How long is the meeting

**Example D7 Task to Parse**:
```markdown
## D7 Tasks (This Week)
- [ ] Discovery call with Sarah Martinez - Wednesday 11/15 at 2:00pm ET (60 min)
- [ ] Onsite visit at GlobalPharma HQ - Thursday 11/16 at 10:00am PT
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system for tone matching (keep output concise and operational)

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply signature formatting only

---

## Email Structure

### Subject Line
**Formula**: Clear, operational, under 7 words

**Options**:
- "Tomorrow's call at {TIME}" (e.g., "Tomorrow's call at 2pm ET")
- "{DAY} meeting details" (e.g., "Wednesday meeting details")
- "Logistics for {EVENT}" (e.g., "Logistics for onsite visit")
- "Zoom link for {DAY}" (e.g., "Zoom link for tomorrow")
- "{TIME} call confirmation" (e.g., "2pm call confirmation")

### Body Structure
**Purpose**: Provide operational details, reduce friction, confirm attendance

**Word count**: 80-130 words total

**Template for Virtual Meetings**:
```
Hi {FIRST_NAME},

{Meeting confirmation with date/time}. {Zoom link or meeting access}. {Dial-in backup if available}. {Who's attending from your side}. {Agenda reminder or attachment reference}. {Low-pressure closing or question invitation}.

{Closing},
{Signature}
```

**Template for Onsite Meetings**:
```
Hi {FIRST_NAME},

{Meeting confirmation with date/time}. {Physical address or building name}. {Parking instructions}. {Building access/check-in process}. {Who's attending from your side}. {What to bring or prepare}.

{Closing},
{Signature}
```

---

## Examples

### Example 1: Virtual Discovery Call

```
**Subject**: Tomorrow's discovery call at 2pm ET

Hi Sarah,

Quick reminder about our discovery call tomorrow (Wednesday, November 15) at 2:00pm ET. Here's the Zoom link: https://zoom.us/j/123456789. If you have any connection issues, you can also dial in at +1-555-123-4567 (Meeting ID: 123 456 789). From our side, it will be myself and Tom Chen, our solutions architect. I've attached a brief agenda to help guide our conversation. Let me know if you need anything before we connect.

Talk soon,
Michael
```

### Example 2: Onsite Visit

```
**Subject**: Thursday onsite visit details

Hi Jim,

Looking forward to our onsite meeting tomorrow (Thursday, November 16) at 10:00am PT at GlobalPharma headquarters. We'll meet you in the main lobby at 1500 River Road, Building A. Visitor parking is available in Lot C - I've arranged passes for our team that will be waiting at the front desk. From our side, it will be myself, Anna Rodriguez (customer success), and David Kim (implementation lead). We're planning to spend about 2 hours walking through your current workflow and exploring integration options.

See you tomorrow,
Welf
```

### Example 3: Conference Room Meeting

```
**Subject**: 10am meeting logistics

Hi David,

Confirming our technical review today at 10:00am ET. We'll meet in the Redwood conference room on the 3rd floor. I'll have the demo environment set up and ready to go. From our side, it will be myself and Lisa Park from our technical team. We'll plan for 90 minutes and walk through the Salesforce integration scenarios you mentioned. Feel free to bring any additional questions that have come up since we last spoke.

Best,
Anna
```

---

## Best Practices

### Logistics Clarity
- **Test Zoom links** before sending (verify they work)
- **Include dial-in backup** for important calls (phone number + meeting ID)
- **Provide full address** for onsite visits (building name, street, parking lot)
- **Time zone explicit** - always include ET, PT, etc.
- **Duration mention** if not obvious (30 min, 1 hour, 2 hours)

### Attendee Transparency
- **List your attendees** by name and role
- **Set expectations** on who they'll meet
- **Explain why** certain people are attending if relevant (e.g., "solutions architect to discuss technical requirements")

### Attachment Handling
- **Reference agenda** if attached or previously shared
- **Don't attach large files** - provide links instead
- **Mention if materials required** (e.g., "Please have your current workflow diagram handy")

### Timing
- **Day-before optimal**: Send 18-24 hours before meeting
- **Morning-of acceptable**: For afternoon meetings
- **Avoid last-minute**: Don't send <2 hours before unless urgent

### Tone
- **Operational, not warm**: Focus on logistics over relationship
- **Helpful, not demanding**: Provide details, don't require confirmation
- **Brief, not chatty**: Get to the point quickly

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_meeting_reminder
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
- Total body: 80-130 words (excluding subject and signature)
- Include all critical logistics (link/address, time, attendees)
- Operational tone (less warm than email_simple_followup)
- No detailed agenda content (reference attachment instead)
- No sales pitch or value prop (pure logistics)

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_meeting_reminder_{DATE}.md`

**Filename format**: `email_meeting_reminder_2025-11-15.md`

---

## Error Handling

**Missing Zoom link or address**:
- Prompt user: "I don't have meeting location details. Is this virtual (need Zoom link) or onsite (need address)?"

**Missing meeting time**:
- Prompt user: "What time is the meeting scheduled?"

**Missing attendee list**:
- Generate with placeholder: "From our side, it will be myself and [team member if applicable]"
- Use singular if solo meeting

**No agenda available**:
- Skip agenda reference, focus on meeting purpose instead
- Example: "We'll walk through your reporting challenges and explore potential solutions"

---

## Meeting Reminder vs Simple Follow-Up

**Use email_meeting_reminder when**:
- 24 hours or less before meeting
- Need to provide logistics (Zoom/address)
- First-time attendees need access instructions
- Multiple stakeholders attending (list needed)
- High-stakes meeting (reduce no-show risk)

**Use email_simple_followup when**:
- 2-7 days before meeting
- Logistics already shared via calendar
- Relationship warmth more important than logistics
- Low-stakes or recurring meeting

---

## Example Output

```markdown
---
generated_by: sales-communications/email_meeting_reminder
generated_on: 2025-11-15T09:00:00Z
deal_id: GlobalPharma
sources:
  - sample-data/Runtime/Sessions/GlobalPharma/deal.md
  - sample-data/Runtime/_Shared/style/ae_welf_corpus.md
---

**Subject**: Thursday onsite visit details

Hi Jim,

Looking forward to our onsite meeting tomorrow (Thursday, November 16) at 10:00am PT at GlobalPharma headquarters. We'll meet you in the main lobby at 1500 River Road, Building A. Visitor parking is available in Lot C - I've arranged passes for our team that will be waiting at the front desk. From our side, it will be myself, Anna Rodriguez (customer success), and David Kim (implementation lead). We're planning to spend about 2 hours walking through your current workflow and exploring integration options.

See you tomorrow,
Welf Ludwig
Account Executive
rep@company.com
```

---

**End of Pattern: email_meeting_reminder**
