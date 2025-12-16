# Email: Discovery Call Recap

**Pattern**: email_discovery_recap
**Type**: Customer-facing email
**Timing**: Within 24 hours after discovery call
**Purpose**: Recap discussion, confirm understanding, establish next steps

---

## When to Use

Send this email after an initial discovery call to:
- Demonstrate active listening and confirm understanding
- Document key points discussed (pain points, requirements, timeline)
- Reinforce value alignment between prospect needs and your solution
- Establish clear next steps and maintain momentum
- Create paper trail for internal stakeholders (fwd to team)

**Trigger Phrases**:
- "Draft discovery recap for {DEAL}"
- "Send discovery follow-up to {DEAL}"
- "Create discovery recap email"

---

## Prerequisites

**Required**:
- Deal context from deal.md (for discovery findings, MEDDPICC data, stakeholders)

**Optional**:
- AE style corpus (for voice matching)
- Methodology stage guide (for qualification alignment)

**If deal context missing**:
- Output error: "Discovery recap requires deal context. Please run /deal-intake or create deal.md first."
- Set frontmatter: `status: "missing_prereqs"`
- Do NOT generate generic email

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Primary contact**: Who attended the call (from Stakeholders)
- **Discovery call date**: Most recent History entry with "discovery" or "initial call"
- **Pain points discussed**: From History notes or MEDDPICC "Identify Pain" section
- **Technical requirements**: From MEDDPICC "Decision Criteria" or History
- **Timeline/urgency**: From History or MEDDPICC "Decision Process"
- **Competitors mentioned**: From MEDDPICC "Competition" field
- **D7 tasks**: Near-term follow-ups (these become next steps in email)

**Example History Entry to Parse**:
```markdown
### 2025-11-12 - Discovery Call with Jane Smith (VP Operations)
- Current system: Manual process using spreadsheets, 50+ hours/month overhead
- Pain points: Data accuracy issues, slow reporting, team frustration
- Key requirements: API integration with Salesforce, real-time dashboards, <30min onboarding
- Timeline: Budget approved, need solution by Q1 2026
- Attendees: Jane Smith (VP Ops), Michael Chen (Director IT)
- Next steps: Technical deep-dive, integration requirements doc
```

### 2. Load Style Corpus

Follow patterns/_voice_matching.md:
1. Detect active AE (deal.md owner field)
2. Load corpus (4-tier system)
3. Extract style patterns (greeting, closing, paragraph count, tone)
4. Apply to email generation (qualification questions phrased in AE's direct style)
5. Run voice verification (3 checks) if corpus available
6. Rewrite once if needed
7. Log style_source in frontmatter

**Note**: If AE corpus shows casual/direct style, phrase qualification questions in that voice (e.g., "How are you planning to make the decision?" instead of "Could you please share your thoughts on the decision-making process?")

### 3. Load Brand Guidelines (Section 2 of _common.md)

If brand_guidelines.md exists:
- Apply email signature format
- Include required disclaimers
- Match tone guidance (professional/consultative/casual)

If missing: Use generic professional defaults

### 4. Load Methodology Guidance (Section 4 of _common.md)

If MEDDPICC stage inventory available:
- Reference Discovery stage exit criteria
- Ensure email addresses key qualification questions
- Include methodology-specific CTAs (e.g., "Confirm Metrics")

If missing: Use generic discovery best practices

---

## Email Structure

### Subject Line
**Formula**: `Re: [Call Topic] - Next Steps`

**Options** (choose based on style corpus):
- Formal: "Re: Discovery Discussion - {Company Name} & {Your Company}"
- Casual: "Great chatting about [pain point]"
- Methodology-driven: "Discovery Recap: [Key Metric or Pain Point]"

**Example**: "Re: Operations Automation Discussion - Next Steps"

### Opening Paragraph
**Purpose**: Acknowledge the call, express appreciation, set email agenda

**Default Template** (adapt to style corpus):
```
Hi {FIRST_NAME},

Thanks for taking the time to walk me through {COMPANY}'s {pain point/process}
today. I appreciated learning about {specific detail from call} and how your
team is currently {current state}.

I wanted to recap what we discussed and outline next steps.
```

**Style Variations** (use if AE corpus shows preference):
- Consultative: "I enjoyed our conversation about..."
- Enthusiastic: "It was great connecting with you..."
- Direct: "Following up on our call regarding..."

**Corpus Override**: If AE typically uses shorter/longer openings, match that pattern instead

### Key Discussion Points Section
**Purpose**: Demonstrate active listening, confirm understanding

**Default Structure**: Bulleted list of 3-5 main topics (unless AE corpus prefers different approach)

**Default Template**:
```
Here's what I heard:

- **Current Challenge**: {pain point in prospect's words}
  {One sentence elaboration from call}

- **Key Requirements**: {technical/business needs}
  {Specific examples mentioned}

- **Timeline**: {urgency and decision process}
  {Budget cycle, deadline, constraints}

- **Success Metrics**: {how they'll measure improvement}
  {Quantified outcomes if discussed}
```

**Corpus Override**: If AE corpus shows they summarize discoveries in paragraph form or use fewer/more bullets, follow that pattern instead

**Example**:
```
Here's what I heard:

- **Current Challenge**: Manual data aggregation from 15+ sources taking your
  team 50+ hours/month, leading to delayed reports and frustrated stakeholders.

- **Key Requirements**: Real-time Salesforce integration, customizable dashboards
  for different exec personas, and <30 minute onboarding for new users.

- **Timeline**: Budget approved for Q4 deployment, need solution operational by
  Jan 15 to support annual planning cycle.

- **Success Metrics**: Reduce reporting overhead by 80%, increase data accuracy
  to 99%+, deliver executive dashboards within 24 hours of request.
```

### Value Alignment Paragraph
**Purpose**: Connect their needs to your solution capabilities

**Default Template** (1-2 sentences, not salesy, unless AE corpus prefers different approach):
```
Based on what you shared, I think {your solution} could address {primary pain
point} through {specific capability}. I'd love to show you {specific feature}
in our next conversation.
```

**Tone**: Consultative, not pushy. Focus on fit, not features.

**Corpus Override**: If AE corpus shows they skip explicit value statements or phrase them differently, follow that pattern

**Example**:
```
Based on what you shared, our Salesforce native integration and pre-built
executive dashboard templates could eliminate your manual aggregation work
entirely. I'd love to show you how we handled a similar use case for {comparable
customer} in our next conversation.
```

### Next Steps Section
**Purpose**: Clear, time-bound action items for both parties

**Default Structure**: Numbered list with owners and deadlines (unless AE corpus shows preference for different format)

**Default Template**:
```
Next steps:

1. **{Your company}**: {action item} by {date}
2. **{Their company}**: {action item} by {date}
3. **Both**: {meeting/call} on {proposed date/time}
```

**Example**:
```
Next steps:

1. **Our team**: Send technical integration requirements doc and sample
   dashboard templates by Thursday 11/16
2. **Your team**: Review requirements, flag any Salesforce customizations
   or security concerns by Monday 11/20
3. **Both**: Technical deep-dive call Tuesday 11/21 at 2pm ET - I'll send
   calendar invite with Zoom link
```

**Best Practices** (default recommendations unless AE corpus shows different approach):
- Default to assign owners to every action (avoid vague "we should...")
- Default to include specific dates (avoid "early next week")
- Default to lead with what YOU're doing (demonstrate commitment)
- Target 3-5 items (more = lower completion rate), but adjust if AE corpus shows preference for more/fewer items

**Corpus Override**: If AE typically uses simpler next steps format or different action item style, match that pattern

### Closing Paragraph
**Purpose**: Express enthusiasm, open door for questions

**Default Template** (adapt to style corpus):
```
{Enthusiasm statement}. {Question invitation}.

{Closing},
{Signature}
```

**Corpus Override**: Match AE's typical closing style (length, tone, formality)

**Example**:
```
Looking forward to diving deeper into the technical details next week. Let me
know if any questions come up in the meantime.

Best regards,
[AE Name]
```

**Style Variations**:
- Formal: "I look forward to our continued discussions."
- Casual: "Excited to keep the conversation going!"
- Consultative: "Happy to answer any questions that come up."

### Signature
Apply brand guidelines signature format if available, otherwise use:

```
[AE Name]
[Title]
[Company Name]
[Email] | [Phone]
```

---

## Target Length

**Default**: 130-160 words (acceptable range: 100-200)
**If AE corpus averages significantly different**: Match corpus instead

**Sections**: Default to opening + qualification summary + next steps unless corpus shows preference for simpler structure

---

## Style Alignment

- Use these structure suggestions by default
- If AE corpus shows different preferences (paragraph count, length, tone), follow corpus instead
- **Corpus wins when conflict occurs**
- See references/template_override_protocol.md for full priority hierarchy

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_discovery_recap
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - sample-data/Runtime/_Shared/style/{style_file}  # if loaded
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
  - sample-data/Runtime/_Shared/knowledge/methodologies/{METHOD}/stage_inventory__{METHOD}.md  # if loaded
---
```

### 2. Compose Email Body

Follow structure above with actual content from deal.md

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_discovery_recap_{DATE}.md`

**Filename format**: `email_discovery_recap_2025-11-14.md`

---

## Error Handling

**Missing deal.md**: BLOCK - Prompt user to run `/deal-intake` first

**Missing discovery call in History**:
- Generate generic discovery recap structure
- Prompt user: "I don't see a recent discovery call in History. Add details about the call first?"

**Missing stakeholders**:
- Use generic salutation "team" or "all"
- Suggest updating Stakeholders section

**Missing D7 tasks**:
- Omit next steps section
- Suggest specific follow-ups based on stage

**Missing style corpus (all tiers)**:
- Use Tier 4 defaults from _common.md section 3
- Professional tone, standard business format

**Missing methodology**:
- Use generic discovery best practices
- Focus on understanding pain, requirements, timeline

---

## Example Output

```markdown
---
generated_by: sales-communications/email_discovery_recap
generated_on: 2025-11-14T15:30:00Z
deal_id: AcmeCorp
sources:
  - sample-data/Runtime/Sessions/AcmeCorp/deal.md
  - sample-data/Runtime/_Shared/style/team_corpus.md
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md
---

**Subject**: Re: Operations Automation Discussion - Next Steps

Hi Jane,

Thanks for taking the time to walk me through AcmeCorp's reporting challenges
today. I appreciated learning about your 15-source data aggregation process and
how your team is currently managing this manually.

I wanted to recap what we discussed and outline next steps.

Here's what I heard:

- **Current Challenge**: Manual data aggregation from 15+ sources taking your
  team 50+ hours/month, leading to delayed reports and frustrated stakeholders.

- **Key Requirements**: Real-time Salesforce integration, customizable dashboards
  for different exec personas, and <30 minute onboarding for new users.

- **Timeline**: Budget approved for Q4 deployment, need solution operational by
  Jan 15 to support annual planning cycle.

- **Success Metrics**: Reduce reporting overhead by 80%, increase data accuracy
  to 99%+, deliver executive dashboards within 24 hours of request.

Based on what you shared, our Salesforce native integration and pre-built
executive dashboard templates could eliminate your manual aggregation work
entirely. I'd love to show you how we handled a similar use case for a Fortune
500 healthcare company in our next conversation.

Next steps:

1. **Our team**: Send technical integration requirements doc and sample
   dashboard templates by Thursday 11/16
2. **Your team**: Review requirements, flag any Salesforce customizations
   or security concerns by Monday 11/20
3. **Both**: Technical deep-dive call Tuesday 11/21 at 2pm ET - I'll send
   calendar invite with Zoom link

Looking forward to diving deeper into the technical details next week. Let me
know if any questions come up in the meantime.

Best regards,
Sarah Chen
Senior Account Executive
Example Corp Solutions
sarah.chen@example.com | (555) 123-4567
```

---

**End of Pattern: email_discovery_recap**
