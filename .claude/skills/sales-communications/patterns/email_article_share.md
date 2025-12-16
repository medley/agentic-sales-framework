# Email: Article Share

**Pattern**: email_article_share
**Type**: Customer-facing email
**Timing**: When relevant content discovered
**Purpose**: Provide value, demonstrate industry expertise, nurture relationship

---

## When to Use

Send this email to:
- Share industry reports or research relevant to their challenges
- Forward case studies similar to their use case
- Alert them to regulatory changes affecting their business
- Provide competitive intelligence they'd find valuable
- Share thought leadership that addresses their pain points
- Maintain relationship during quiet periods with value-add content

**NOT for**:
- Product announcements (use email_demo_followup)
- Detailed proposal follow-up (use email_proposal_nudge)
- Meeting recaps (use email_discovery_recap or email_demo_followup)
- Marketing newsletters (this is 1:1 personalized)
- Content without clear connection to their specific challenges

**Trigger Phrases**:
- "Share article with {DEAL}"
- "Send {LINK} to {NAME}"
- "Thought of you when I saw this"
- "Send {RESOURCE} to {DEAL}"
- "Forward {ARTICLE} to {NAME}"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Stakeholder name (recipient)
   - Known pain points or challenges from Discovery or Context sections
   - Industry/vertical information
3. Article/resource details:
   - URL or attachment
   - Brief summary of content
   - Clear relevance to their specific situation

**OPTIONAL**:
- Email style corpus (for tone matching)
- Brand guidelines (for signature formatting)

**NOT NEEDED**:
- Methodology stage inventory
- Detailed deal qualification data
- Product features or pricing information

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Recipient name**: Primary contact or most relevant stakeholder
- **Pain points**: Specific challenges they've mentioned
- **Industry context**: Vertical, regulatory environment, market pressures
- **Recent conversations**: What you've discussed that makes this relevant

**Example Context to Parse**:
```markdown
## Discovery Notes
- Jim mentioned struggling with manual reporting across 12 manufacturing sites
- Regulatory compliance (FDA 21 CFR Part 11) is top priority for Q1
- Currently evaluating 3 vendors, decision timeline pushed to January
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system for tone matching (keep helpful/educational tone even if AE style is aggressive)

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply signature formatting only

---

## Email Structure

### Subject Line
**Formula**: Keep under 8 words, conversational and relevant

**Options**:
- "Thought of you when I saw this"
- "This reminded me of our conversation"
- "{TOPIC} research you might find useful"
- "Saw this on {TOPIC}"
- "Quick share: {TOPIC}"
- "{INDUSTRY} update worth reading"

**Examples**:
- "Thought of you when I saw this FDA report"
- "Manufacturing compliance research you might like"
- "Saw this on multi-site QMS challenges"

### Body (Single Paragraph)
**Purpose**: Provide value without pitching, demonstrate you listen and remember their challenges

**Structure**: 4-6 sentences, 80-120 words total

**Template**:
```
Hi {FIRST_NAME},

{Personal opener referencing why this is relevant}. {1-2 sentence summary of what the content is}. {Why it's specifically relevant to their situation or challenges}. {Link or attachment reference}. {No-pressure closing}.

{Closing},
{Signature}
```

**Example 1 (Industry Research Report)**:
```
Hi Jim,

I came across this Gartner report on multi-site quality management trends and thought of our conversation about your 12 manufacturing locations. The report covers how companies like yours are handling FDA compliance across distributed operations, with some interesting data on automation ROI. Figured it might be useful as you evaluate solutions this quarter. Here's the link: [URL]. No need to respond - just thought you'd find it valuable.

Best,
Welf
```

**Example 2 (Customer Case Study)**:
```
Hi Sarah,

Saw this case study about how a mid-size pharma company solved their Part 11 compliance challenges and immediately thought of you. They had a similar setup to yours - legacy systems, multiple sites, tight compliance deadlines. The before/after metrics are pretty compelling. Link here: [URL]. Let me know if you want to discuss any of it.

Talk soon,
Michael
```

**Example 3 (Regulatory/Industry News)**:
```
Hi David,

Wanted to flag an FDA guidance update that dropped yesterday on electronic signatures and audit trails. Given your January compliance deadline, this might affect your requirements. It's a quick 10-minute read with some clarifications on cloud-based systems: [URL]. Happy to chat if it raises any questions on your end.

Best regards,
Anna
```

**Example 4 (Competitive Intelligence)**:
```
Hi Lisa,

Thought you'd be interested in this TechCrunch article about your current vendor's recent acquisition. Doesn't change anything urgently, but might be worth reading as you finalize your decision. Some interesting details about their product roadmap shifting: [URL]. As always, here if you want to talk through any implications.

Cheers,
Tom
```

### Closing Options
**Casual**:
- "Best,"
- "Talk soon,"
- "Cheers,"
- "Hope this helps,"

**Professional**:
- "Best regards,"
- "All the best,"
- "Thank you,"

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_article_share
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - sample-data/Runtime/_Shared/style/{style_file}  # if loaded
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
resource_shared: {URL_OR_FILENAME}
---
```

### 2. Compose Email Body

**CRITICAL CONSTRAINTS**:
- Total body: 80-120 words (excluding subject and signature)
- Single paragraph only (no bullet lists, no long-form analysis)
- NO product pitches, no feature mentions (unless article is your customer case study)
- NO calls to action beyond "let me know if you want to discuss"
- Educational/helpful tone, not salesy
- Must clearly explain WHY this article is relevant to THEIR specific situation
- Include actual link or attachment reference

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_article_share_{DATE}.md`

**Filename format**: `email_article_share_2025-11-15.md`

---

## Error Handling

**Missing pain points or context**:
- Prompt user: "What specific challenge or conversation does this article relate to for {DEAL}?"
- Cannot proceed without clear relevance statement

**Missing article URL or details**:
- Prompt user: "What's the URL or resource you want to share? What's it about?"

**No clear connection to deal**:
- Warn: "I can't find a clear connection between this article and {DEAL}'s challenges. Should I still send it?"

**Generic/templated feel**:
- If you can't write a specific, personalized opener, DON'T send the email
- Better to skip than send generic "thought you might like this" with no real connection

---

## Article Share Best Practices

**Relevance is everything**: If you can't explain in 1 sentence why THIS article matters to THIS person's specific challenge, don't send it.

**Brevity**: Summarize the content in 1-2 sentences max. They'll read it if interested.

**No pitching**: This is value-add, not a sales tactic. Never mention your product unless the article is a customer case study.

**Demonstrate listening**: Reference specific conversations, pain points, or challenges they've mentioned.

**No attachment overload**: One article per email. Don't bundle multiple resources unless specifically requested.

**Timing matters**:
- During active deal: Share content directly related to their evaluation criteria
- During quiet periods: Share industry trends, regulatory updates, thought leadership
- After deal closes (won): Share success stories, best practices, industry updates
- After deal closes (lost): Share content with zero ulterior motive - pure relationship building

**No expectation of response**: Make it clear they don't need to reply. This is a gift, not a conversation starter (though it might become one).

**Content types ranked by value**:
1. Regulatory/compliance updates affecting their timeline (highest urgency)
2. Competitive intelligence about their current vendor or alternatives
3. Industry research specific to their vertical and challenge
4. Customer case studies matching their use case and company profile
5. Thought leadership from respected industry voices (lowest urgency)

**When NOT to use this pattern**:
- If article is your company's marketing content → use email_demo_followup
- If you're sharing proposal/pricing docs → use email_proposal_nudge
- If article requires explanation or demo → schedule a call instead
- If you haven't spoken to them in 6+ months → re-engage differently first

---

## Example Output

```markdown
---
generated_by: sales-communications/email_article_share
generated_on: 2025-11-15T14:20:00Z
deal_id: GlobalPharma
sources:
  - sample-data/Runtime/Sessions/GlobalPharma/deal.md
  - sample-data/Runtime/_Shared/style/ae_welf_corpus.md
resource_shared: https://gartner.com/multi-site-qms-trends-2025
---

**Subject**: Thought of you when I saw this Gartner report

Hi Jim,

I came across this Gartner report on multi-site quality management trends and thought of our conversation about your 12 manufacturing locations. The report covers how companies like yours are handling FDA compliance across distributed operations, with some interesting data on automation ROI. Figured it might be useful as you evaluate solutions this quarter. Here's the link: https://gartner.com/multi-site-qms-trends-2025. No need to respond - just thought you'd find it valuable.

Best,
Welf Ludwig
Account Executive
rep@company.com
```

---

**End of Pattern: email_article_share**
