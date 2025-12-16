# Email: Touch Base

**Pattern**: email_touchbase
**Type**: Customer-facing email
**Timing**: Quarterly or semi-annual during long sales cycles
**Purpose**: Maintain relationship during extended pauses, check on previously discussed initiatives

---

## When to Use

Send this email to:
- Reconnect after 3-6+ months of no contact
- Check in on initiative discussed in previous conversation
- Maintain relationship on viable but paused deals
- Follow up after budget freeze period ends
- Reconnect after organizational change settles
- Check back with "not now but later" deals

**NOT for**:
- Weekly or monthly follow-ups (use email_check_in)
- Recent meeting follow-ups (use email_demo_followup or email_discovery_recap)
- Active deals with regular communication
- Dead deals with no future viability

**Trigger Phrases**:
- "Quarterly check-in with {DEAL}"
- "Touch base with {NAME} about {INITIATIVE}"
- "Long-cycle follow-up"
- "Check back in Q1 with {DEAL}"
- "Reconnect about {INITIATIVE} after {EVENT}"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Stakeholder name (recipient)
   - Last conversation date (must be 3+ months ago)
   - Specific initiative they mentioned (project, pain point, goal)
   - Reason for pause (budget timing, competitor eval, reorg, etc.)

**OPTIONAL**:
- Email style corpus (for tone matching)
- Brand guidelines (for signature formatting)
- Case study or relevant content to share (educational value)

**NOT NEEDED**:
- Methodology stage inventory
- Detailed qualification criteria
- Immediate next steps (deal is paused)

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Recipient name**: Primary contact from previous conversations
- **Last conversation date**: When you last spoke (should be 3+ months ago)
- **Initiative mentioned**: Specific project, pain point, or goal they discussed
- **Pause reason**: Why the deal paused (budget, timing, org change, competitor eval)
- **Current stage**: Where deal was when it paused

**Example History Entry to Parse**:
```markdown
## History
### 2025-06-15 - Discovery Call
- Spoke with Sarah Chen (VP Operations)
- Discussed quality management system modernization project
- Timeline: Q1 2026 (after new fiscal year budget approved)
- Pain: Manual document control causing audit issues
- Status: Check back in December after budget finalized
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system for tone matching (keep conversational, helpful tone)

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply signature formatting only

---

## Email Structure

### Subject Line
**Formula**: Reference their initiative or timing, keep under 8 words

**Options**:
- "Checking in on {INITIATIVE}" (e.g., "Checking in on QMS modernization")
- "{TIMEFRAME} follow-up on {TOPIC}" (e.g., "Q1 follow-up on quality systems")
- "Quick check-in on {INITIATIVE}"
- "How's {PROJECT} progressing?"
- "{SEASON} update"

### Body (90-130 words)
**Purpose**: Acknowledge time passed, reference specific initiative, offer value, low-pressure reconnect

**Structure**: 4-6 sentences

**Template**:
```
Hi {FIRST_NAME},

{Acknowledge time passed since last conversation}. {Reference specific initiative or pain point they mentioned}. {Ask how it's progressing or if timing has changed}. {Optional: Offer new value - case study, insight, relevant content}. {Low-pressure invitation to reconnect if timing is better now}. {Optional: Express understanding if still not the right time}.

{Closing},
{Signature}
```

### Example 1 (Post-Budget-Freeze)

**Context**: Deal paused in June due to budget timing, checking back in December after new fiscal year

```
Hi Sarah,

Hope you've had a good few months since we last spoke in June. I wanted to check in on the quality management system modernization project you mentioned - I know you were waiting for the new fiscal year budget to be finalized. How's that progressing?

We've been working with several life sciences companies on audit prep efficiency - happy to share what we're seeing in the market if it's helpful. If the timing is better now, I'd love to reconnect briefly. And if it's still not the right moment, no worries at all.

Best,
Michael
```

### Example 2 (Post-Competitor-Eval)

**Context**: Customer was evaluating competitors in May, checking back in November

```
Hi David,

It's been a while since we last connected - I think it was back in May when you were evaluating different quality systems. I wanted to check in and see how that evaluation went and whether you've made any decisions.

No pressure at all if you went another direction. But if you're still exploring options or if anything has changed, I'd be happy to reconnect and share some updates on our platform. Just let me know.

Thanks,
Anna
```

### Example 3 (Post-Reorg)

**Context**: Deal paused in March during VP transition, checking back in September after new VP settled in

```
Hi Lisa,

Hope the transition with the new VP of Quality has gone smoothly over the past few months. I know things were in flux back in March when we last spoke about your document control challenges.

Now that the team has had time to settle in, I wanted to check if those audit readiness concerns are still a priority. We've released some new validation features that might be relevant. Happy to catch up briefly if it makes sense, or just stay in touch for when the timing is better.

Cheers,
Tom
```

### Closing Options
**Casual**:
- "Best,"
- "Cheers,"
- "Thanks,"
- "Hope to hear from you,"

**Professional**:
- "Best regards,"
- "Warm regards,"
- "Looking forward to hearing from you,"

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_touchbase
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
- Total body: 90-130 words (excluding subject and signature)
- Single paragraph format (can be 2 short paragraphs if needed)
- Reference SPECIFIC initiative from past conversation (not generic)
- Acknowledge significant time gap (3+ months)
- Low-pressure tone (understand if still not right time)
- Offer new value when possible (case study, insight, update)
- No pushy language, no urgency, no hard asks

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_touchbase_{DATE}.md`

**Filename format**: `email_touchbase_2025-11-15.md`

---

## Error Handling

**Missing last conversation date**:
- Use generic timeframe: "It's been a while since we last connected"
- Prompt user: "When did you last speak with this contact?"

**Missing specific initiative**:
- Generate generic business health check-in
- Prompt user: "What initiative or pain point did they mention previously?"

**Last conversation too recent (< 3 months)**:
- Warning: "This pattern is for 3+ month gaps. Consider email_check_in instead."

**No pause reason documented**:
- Use generic timing language: "I know the timing wasn't quite right before"

---

## Touch Base Best Practices

**Reference specifics**: Always mention the actual initiative or pain point they discussed (not "your project" but "the quality management modernization project")

**Acknowledge time**: Explicitly acknowledge the time gap - shows you respect their timeline and aren't just spamming

**Offer value**: Include case study, new feature, industry insight - give them a reason to engage beyond just your sales agenda

**Low pressure**: Make it easy to say "still not ready" without feeling guilty. This preserves long-term relationship.

**Timing windows**:
- Budget freeze → Check back when new fiscal year starts
- Competitor eval → Check back 4-6 months later
- Organizational change → Check back 3-4 months after change
- "Not now" deals → Check back next quarter

**When NOT to use this pattern**:
- Less than 3 months since last contact → use email_check_in
- Deal is dead with no future viability → don't send
- You have regular ongoing communication → this is for paused deals only
- Customer explicitly asked not to follow up → respect their request

---

## Example Output

```markdown
---
generated_by: sales-communications/email_touchbase
generated_on: 2025-12-10T14:20:00Z
deal_id: LifeScienceCorp
sources:
  - sample-data/Runtime/Sessions/LifeScienceCorp/deal.md
  - sample-data/Runtime/_Shared/style/ae_michael_corpus.md
---

**Subject**: Checking in on QMS modernization

Hi Sarah,

Hope you've had a good few months since we last spoke in June. I wanted to check in on the quality management system modernization project you mentioned - I know you were waiting for the new fiscal year budget to be finalized. How's that progressing?

We've been working with several life sciences companies on audit prep efficiency - happy to share what we're seeing in the market if it's helpful. If the timing is better now, I'd love to reconnect briefly. And if it's still not the right moment, no worries at all.

Best,
Michael Stevens
Account Executive
michael@company.com
```

---

**End of Pattern: email_touchbase**
