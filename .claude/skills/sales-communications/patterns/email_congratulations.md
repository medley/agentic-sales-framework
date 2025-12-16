# Email: Congratulations

**Pattern**: email_congratulations
**Type**: Customer-facing email
**Timing**: Within 24 hours of seeing news (LinkedIn, press release, etc.)
**Purpose**: Celebrate their win, build authentic relationship, stay top-of-mind

---

## When to Use

Send this email to:
- Congratulate on promotion or new role announcement
- Celebrate funding round or acquisition news
- Acknowledge product launch or company milestone
- Recognize award or industry recognition
- Mark significant company achievement

**NOT for**:
- Prospecting to cold contacts (use email_cold_outbound)
- Following up on meetings (use email_demo_followup or email_discovery_recap)
- Advancing stalled deals (use email_proposal_nudge)
- Reconnecting after long silence (use email_reengagement)

**Trigger Phrases**:
- "Congrats to {NAME} on {ACHIEVEMENT}"
- "Congratulate {DEAL} on promotion/funding/launch"
- "Celebrate {COMPANY} news"
- "Acknowledge {NAME}'s new role"
- "Recognition email for {ACHIEVEMENT}"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Stakeholder name (recipient)
   - Company name
   - Previous context/relationship
3. **Achievement details**: What specific news/accomplishment triggered this email
   - Source (LinkedIn, press release, company announcement)
   - Date of announcement
   - Nature of achievement (promotion, funding, launch, award, milestone)

**OPTIONAL**:
- Email style corpus (for tone matching)
- Brand guidelines (for signature formatting)
- Previous conversation history (to reference shared context)

**NOT NEEDED**:
- Methodology stage inventory
- Detailed deal qualification data
- Sales objectives or next steps (this is relationship-building only)

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Recipient name**: Person who achieved the milestone or company contact
- **Company name**: For company-level achievements
- **Relationship context**: Previous conversations, meetings, or interactions
- **Achievement details**: What happened and when

**Example from History**:
```markdown
## History
- 2025-10-15: Discovery call with Sarah Chen (VP Operations)
- 2025-10-20: Demo to Sarah + procurement team
- 2025-11-14: Saw LinkedIn post: Sarah promoted to SVP Operations
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system for tone matching (authentic and warm, never salesy)

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply signature formatting only

---

## Email Structure

### Subject Line
**Formula**: Keep under 6 words, genuine and specific

**Options by Achievement Type**:
- **Promotion**: "Congrats on the new role!"
- **Funding**: "Exciting news on the funding!"
- **Product Launch**: "Congrats on the launch!"
- **Award/Recognition**: "Well-deserved recognition!"
- **Company Milestone**: "Congrats on {MILESTONE}!"

**AVOID**:
- Generic subjects: "Congratulations"
- Sales-y additions: "Congrats + quick question"
- Fake personalization: "RE: Your promotion"

### Body (Single Paragraph)
**Purpose**: Authentic celebration, brief connection to their goals, no hidden agenda

**Structure**: 3-5 sentences, 70-110 words total

**Template**:
```
Hi {FIRST_NAME},

{Specific congratulations on achievement}. {Personal observation or why this matters}. {Optional: brief connection to previous conversation or their goals}. {Well-wish for their success in new role/venture}.

{Closing},
{Signature}
```

**Example 1 (Promotion)**:
```
Hi Sarah,

Just saw the news about your promotion to SVP Operations - huge congratulations! This is well-deserved given everything you've accomplished with the quality systems transformation. I know you mentioned wanting to tackle the enterprise-wide reporting challenges, and this new role gives you the perfect platform. Wishing you continued success.

Best,
Michael
```

**Example 2 (Funding Round)**:
```
Hi David,

Congratulations on closing the Series B! $25M is incredible validation of what you're building. I remember you sharing the vision for expanding into European markets during our last conversation, and now you've got the fuel to make it happen. Exciting times ahead.

Cheers,
Anna
```

**Example 3 (Product Launch)**:
```
Hi Tom,

Saw the announcement about your AI compliance module launching yesterday - congrats to you and the team! The timing is perfect given all the regulatory changes hitting the industry. This is exactly the innovation you mentioned was coming when we spoke in September. Well done.

Best regards,
Lisa
```

**Example 4 (Award/Recognition)**:
```
Hi Jennifer,

Just read that MedCorp won the Innovation Excellence Award - congratulations! Your team's work on the digital quality platform clearly stood out. This recognition is well-earned, especially after all the effort you shared about modernizing your legacy systems. Fantastic achievement.

Talk soon,
James
```

### Closing Options
**Warm and authentic**:
- "Best,"
- "Cheers,"
- "Congrats again,"
- "Well done,"

**Professional**:
- "Best regards,"
- "Warm regards,"
- "All the best,"

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_congratulations
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - sample-data/Runtime/_Shared/style/{style_file}  # if loaded
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
trigger: {description of achievement/news}
---
```

### 2. Compose Email Body

**CRITICAL CONSTRAINTS**:
- Total body: 70-110 words (excluding subject and signature)
- Single paragraph only (no bullet lists, no headers, no sections)
- MUST reference specific achievement details (not generic)
- NO sales pitch, NO call-to-action, NO meeting requests
- Optional: ONE brief connection to previous conversation (1 sentence max)
- Authentic tone - should feel like genuine congratulations, not prospecting
- Include what you saw and where (LinkedIn, press release, etc.) to show it's real

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_congratulations_{DATE}.md`

**Filename format**: `email_congratulations_2025-11-15.md`

---

## Error Handling

**Missing achievement details**:
- Prompt user: "What specific achievement should I congratulate them on? (promotion, funding, launch, award, milestone)"
- Request source: "Where did you see this news? (LinkedIn, press release, company site)"

**Missing recipient name**:
- Cannot generate - this pattern requires personal recipient
- Prompt: "Who should receive this congratulations email?"

**No previous relationship context in deal.md**:
- Generate simpler version without referencing past conversations
- Focus purely on public achievement and general well-wishes

**Achievement too vague**:
- Request specific details: "What was the specific promotion/funding amount/product name/award?"

---

## Congratulations Email Best Practices

**Authenticity**: Only send if you genuinely saw the news and have real context. Never fabricate congratulations.

**Timing**: Within 24 hours of announcement for maximum relevance. After 48 hours, it feels stale.

**Specificity**: Reference exact details (role title, funding amount, product name, award title). Generic "congrats on your success" feels automated.

**No hidden agenda**: This is NOT a prospecting email. No "congrats + are you free for 15 min?" combinations.

**Brief connection only**: If you reference previous conversation, keep it to one sentence. The focus should be THEIR achievement, not your product.

**Source acknowledgment**: Mention where you saw it ("saw on LinkedIn", "read the press release", "noticed the announcement") to show you're actually paying attention.

**When to skip soft connection**:
- Very early in relationship (first 1-2 interactions)
- Company-wide achievement (not personal)
- Award/recognition from outside sources (unless directly relevant)

**When to include soft connection**:
- Personal promotion and they previously mentioned career goals
- Funding round and they shared expansion plans
- Product launch they specifically discussed in prior meeting

**What NOT to do**:
- Don't ask for anything (meeting, intro, referral)
- Don't pitch your product or solution
- Don't use this as excuse to "check in on proposal"
- Don't congratulate on achievements that happened weeks/months ago
- Don't send to someone you've never actually interacted with

---

## Example Output

```markdown
---
generated_by: sales-communications/email_congratulations
generated_on: 2025-11-15T09:15:00Z
deal_id: MedCorp
sources:
  - sample-data/Runtime/Sessions/MedCorp/deal.md
  - sample-data/Runtime/_Shared/style/ae_welf_corpus.md
trigger: LinkedIn announcement - Sarah Chen promoted to SVP Operations
---

**Subject**: Congrats on the new role!

Hi Sarah,

Just saw the news about your promotion to SVP Operations - huge congratulations! This is well-deserved given everything you've accomplished with the quality systems transformation. I know you mentioned wanting to tackle the enterprise-wide reporting challenges, and this new role gives you the perfect platform. Wishing you continued success.

Best,
Welf Ludwig
Account Executive
rep@company.com
```

---

**End of Pattern: email_congratulations**
