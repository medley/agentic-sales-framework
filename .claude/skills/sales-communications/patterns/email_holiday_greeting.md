# Email: Holiday Greeting

**Pattern**: email_holiday_greeting
**Type**: Customer-facing email
**Timing**: 1-2 days before holiday/year-end
**Purpose**: Seasonal touchpoint, relationship maintenance, stay top-of-mind

---

## When to Use

Send this email to:
- Maintain warm relationships during seasonal occasions
- Stay top-of-mind without a sales ask
- Show appreciation and humanity during holidays
- Send to entire book of business or select contacts
- Acknowledge industry-specific celebrations
- Mark year-end or new year transitions

**NOT for**:
- Following up on active deals (use email_simple_followup)
- Requesting meetings or next steps (use email_proposal_nudge)
- Recapping business discussions (use email_discovery_recap)
- Deals requiring immediate action (wrong timing)

**Trigger Phrases**:
- "Send holiday greeting to {DEAL}"
- "End of year message to {NAME}"
- "Happy holidays email"
- "Seasonal touchpoint for {DEAL}"
- "Thanksgiving message to customers"
- "New Year greeting for {NAME}"
- "Happy {INDUSTRY_HOLIDAY} to {DEAL}"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Stakeholder name (recipient)
   - Optional: Recent interaction or personal detail for authenticity

**OPTIONAL**:
- Email style corpus (for tone matching)
- Brand guidelines (for signature formatting)
- Occasion/holiday being acknowledged

**NOT NEEDED**:
- Methodology stage inventory
- Deal qualification data
- Business metrics or ROI data
- Meeting history beyond recent personal touchpoints

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Recipient name**: Primary contact or stakeholder
- **Recent personal detail**: Optional - recent conversation topic, shared interest, or life event mentioned
- **Relationship context**: Length of relationship, recent interactions

**Example from deal.md**:
```markdown
## Stakeholders
- Jim Selby (VP Operations) - mentioned daughter starting college, avid golfer
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system for tone matching. Holiday greetings should be warm but professional.

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply signature formatting only

### 4. Determine Occasion

**Common occasions**:
- **Year-end/New Year**: Dec 20-31, Jan 1-5
- **Thanksgiving**: Week of US Thanksgiving (late November)
- **Industry holidays**: Nurses Week (healthcare), Teacher Appreciation (education), etc.
- **Company anniversaries**: Customer's fiscal year-end, partnership anniversaries

---

## Email Structure

### Subject Line
**Formula**: Keep under 6 words, warm and personal

**Options**:
- "Happy holidays, {FIRST_NAME}"
- "Wishing you a great {YEAR}"
- "Happy {HOLIDAY}!"
- "Grateful for your partnership"
- "Cheers to {NEW_YEAR}"
- "Season's greetings"

### Body (Single Paragraph)
**Purpose**: Express genuine well-wishes, no sales content, brief and authentic

**Structure**: 2-4 sentences maximum, 50-90 words total

**Template**:
```
Hi {FIRST_NAME},

{Warm opening tied to occasion}. {Optional: brief personal reference or note of gratitude}. {Well-wishes for holiday/season/year ahead}. {Optional: very brief forward-looking note without pressure}.

{Closing},
{Signature}
```

**Example 1 (Year-End)**:
```
Hi Jim,

As we close out 2025, I wanted to take a moment to say thank you for the partnership this year. Wishing you and your team a relaxing holiday season and a fantastic start to 2026.

Best,
Welf
```

**Example 2 (Thanksgiving)**:
```
Hi Sarah,

Happy Thanksgiving! I'm grateful for the opportunity to work together this year. Hope you enjoy time with family and friends.

Warmly,
Michael
```

**Example 3 (Industry Holiday - Healthcare)**:
```
Hi Lisa,

Happy Nurses Week! Your team's dedication to patient care is truly inspiring. Wishing you all a well-deserved week of recognition and appreciation.

Best regards,
Anna
```

**Example 4 (New Year - Personal Touch)**:
```
Hi David,

Hope you had a great holiday with your family. Excited for what 2026 brings - both for your team's expansion plans and that golf tournament you mentioned. Looking forward to connecting soon.

Cheers,
Tom
```

### Closing Options
**Casual/Warm**:
- "Warmly,"
- "Cheers,"
- "Best,"
- "Gratefully,"

**Professional**:
- "Best regards,"
- "Warm regards,"
- "Sincerely,"

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_holiday_greeting
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
- Total body: 50-90 words (excluding subject and signature)
- Single paragraph only (no bullet lists, no sections, no business content)
- NO sales asks, NO meeting requests, NO deal advancement attempts
- NO business metrics, ROI, or product mentions
- Warm, authentic tone - human first, salesperson second
- Brief is better - this is a touchpoint, not a conversation

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_holiday_greeting_{DATE}.md`

**Filename format**: `email_holiday_greeting_2025-12-20.md`

---

## Error Handling

**Missing recipient name**:
- Use generic salutation: "Hi there," or use company name context

**No personal details available**:
- Keep it simple and generic - still authentic
- Focus on appreciation for partnership/relationship

**Uncertain about religious preferences**:
- Default to secular language: "holiday season", "end of year", "season's greetings"
- Avoid religious-specific holidays unless explicitly known

---

## Holiday Greeting Best Practices

**Brevity**: Shorter is always better. Aim for 50-75 words maximum.

**Authenticity**: Only send if it feels genuine. Don't force it or make it formulaic.

**No asks**: Zero business content. This is relationship maintenance only.

**Timing**:
- Year-end: Dec 20-23 (before most people leave for holidays)
- Thanksgiving: Tuesday-Wednesday of Thanksgiving week
- New Year: Jan 2-5 (after people return from break)
- Industry holidays: Day-of or day-before

**Personalization**:
- Reference shared conversations or interests if authentic
- Acknowledge recent wins or milestones they mentioned
- Keep it light - no pressure to respond

**Religious sensitivity**:
- Avoid assumptions about religious celebrations
- "Holiday season" and "New Year" are universally safe
- If you know their preferences, personalize accordingly

**When NOT to use this pattern**:
- Deal is in crisis or has urgent issues (address those first)
- You just met them (no relationship yet established)
- They explicitly prefer business-only communication
- You're sending purely out of obligation (skip it)

**Mass sending considerations**:
- Can be sent to entire book of business
- Keep it even briefer for mass sends (50-60 words)
- Remove personal details for broad distribution
- Consider BCC for privacy

---

## Example Output

```markdown
---
generated_by: sales-communications/email_holiday_greeting
generated_on: 2025-12-20T14:00:00Z
deal_id: GlobalPharma
sources:
  - sample-data/Runtime/Sessions/GlobalPharma/deal.md
  - sample-data/Runtime/_Shared/style/ae_welf_corpus.md
---

**Subject**: Happy holidays, Jim

Hi Jim,

As we close out 2025, I wanted to take a moment to say thank you for the partnership this year. Wishing you and your team a relaxing holiday season and a fantastic start to 2026.

Best,
Welf Ludwig
Account Executive
rep@company.com
```

---

**End of Pattern: email_holiday_greeting**
