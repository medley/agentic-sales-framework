# Email: Demo Follow-Up

**Pattern**: email_demo_followup
**Type**: Customer-facing email
**Timing**: Within 4-6 hours after product demo
**Purpose**: Reinforce solution fit, address questions, advance to proposal/POC

---

## When to Use

Send this email after a product demonstration to:
- Reinforce how solution addresses their specific requirements
- Answer questions raised during demo
- Provide promised resources (recordings, docs, trial access)
- Address any concerns or objections surfaced
- Advance to commercial discussion (proposal, POC, trial)

**Trigger Phrases**:
- "Draft demo follow-up for {DEAL}"
- "Send demo recap to {DEAL}"
- "Create demo follow-up email"

---

## Prerequisites

**Required**:
- Deal context from deal.md (for demo details, stakeholders, Q&A topics)

**Optional**:
- AE style corpus (for voice matching)
- Methodology stage guide (for POC/trial alignment)

**If deal context missing**:
- Output error: "Demo follow-up requires deal context. Please run /deal-intake or create deal.md first."
- Set frontmatter: `status: "missing_prereqs"`
- Do NOT generate generic email

**STANDARD REQUIREMENTS**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Recent demo call in History section
   - Stakeholder names and titles (who attended demo)
   - Current stage should be "Demo", "Technical Validation", or "Evaluation"
   - Decision Criteria from MEDDPICC (features shown should map to these)
3. Email style corpus (4-tier loading per _common.md section 3)

**OPTIONAL ENHANCEMENTS**:
- Brand guidelines (for formatting, tone)
- Methodology stage inventory (for demo stage best practices)

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Demo attendees**: From Stakeholders section and History entry
- **Demo date and topics covered**: Most recent History entry with "demo" or "presentation"
- **Features shown**: From History notes (which capabilities were demoed)
- **Questions asked**: From History (technical questions, concerns, objections)
- **Decision criteria**: From MEDDPICC section (requirements that demo addressed)
- **Competitors**: From MEDDPICC "Competition" (position against alternatives)
- **D7 tasks**: Follow-up items (send docs, schedule POC, send proposal)

**Example History Entry to Parse**:
```markdown
### 2025-11-13 - Product Demo with AcmeCorp Technical Team
- Attendees: Jane Smith (VP Ops), Michael Chen (Director IT), Sarah Park (Data Analyst)
- Demo focus: Salesforce integration, real-time dashboards, custom reporting
- Features shown: API connector setup (5 min config), executive dashboard templates,
  drill-down analytics, mobile app
- Questions: SSO compatibility? Custom field mapping? Data retention policies?
- Concerns: Michael mentioned current vendor contract through Q1, Sarah asked about
  training requirements
- Next: Send integration technical doc, schedule POC kickoff, pricing discussion
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow patterns/_voice_matching.md:
1. Detect active AE (deal.md owner field)
2. Load corpus (4-tier system)
3. Extract style patterns (greeting, closing, paragraph count, tone)
4. Apply to email generation
5. Run voice verification (3 checks) if corpus available
6. Rewrite once if needed
7. Log style_source in frontmatter

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply company email formatting if available

### 4. Load Methodology Guidance (Section 4 of _common.md)

If MEDDPICC stage inventory available:
- Ensure email advances toward Economic Buyer engagement
- Address Decision Criteria systematically
- Position against Competition if mentioned

---

## Email Structure

### Target Length

**Default**: 125-150 words (acceptable range: 100-180)
**If AE corpus averages significantly different**: Match corpus instead

**Sections**: Default to 4 sections (opening, recap, Q&A, next steps) unless corpus shows preference for simpler structure

### Subject Line
**Formula**: `Re: [Company] Demo - Resources & Next Steps`

**Options**:
- Direct: "Re: AcmeCorp Demo - Technical Docs & POC Discussion"
- Value-focused: "Re: Dashboard Demo - Addressing Your Custom Reporting Needs"
- Action-oriented: "Next Steps: POC Timeline & Pricing Discussion"

### Opening Paragraph
**Purpose**: Thank attendees, acknowledge engagement, reference specific demo moments

**Default structure**: 2-3 sentences unless AE corpus prefers different length

**Template**:
```
Hi {FIRST_NAME},

Thanks to you and the team ({list other attendees}) for the time today. I enjoyed
showing you {specific feature} and hearing {specific question or insight from call}.
{Reference a memorable moment or aha moment from demo}.

I wanted to follow up on the questions raised and outline next steps.
```

**Example**:
```
Hi Jane,

Thanks to you, Michael, and Sarah for the time today. I enjoyed showing you our
Salesforce integration and hearing Sarah's question about custom field mapping -
that's exactly the kind of flexibility our platform was designed for.

I wanted to follow up on the technical questions raised and outline next steps
toward your Q1 deployment timeline.
```

### Recap: What We Showed
**Purpose**: Reinforce solution fit by mapping features to their requirements

**Default structure**: Bulleted list (3-5 items) unless AE corpus prefers narrative format

**Structure**: Bulleted list connecting demo features to their needs

**Template**:
```
Here's what we covered:

- **{Feature/Capability}**: {How it addresses their requirement}
  {Specific example from demo if applicable}

- **{Feature/Capability}**: {How it addresses their requirement}
  {Specific example from demo if applicable}
```

**Example**:
```
Here's what we covered:

- **Salesforce Native Integration**: Showed how our API connector maps to custom
  fields in under 5 minutes, addressing your need for seamless data sync without
  IT overhead.

- **Executive Dashboard Templates**: Walked through pre-built templates for VP
  and C-suite personas, demonstrating how you can deliver board-ready reports
  within 24 hours.

- **Drill-Down Analytics**: Showed Sarah how end-users can click from summary
  metrics into underlying data without building custom queries.

- **Mobile Access**: Demoed the iOS app for on-the-go reporting, addressing your
  request for executive access during travel.
```

### Addressing Questions/Concerns
**Purpose**: Answer questions raised, remove obstacles, demonstrate responsiveness

**Default structure**: Q&A format unless AE corpus prefers narrative style

**Structure**: Q&A format or narrative addressing each concern

**Template (Q&A format)**:
```
On the questions you raised:

**{Question from demo}**
{Clear, specific answer with evidence/examples}

**{Concern from demo}**
{Acknowledgment + mitigation strategy}
```

**Example**:
```
On the questions you raised:

**SSO Compatibility (Michael's question)**
We support SAML 2.0 SSO with all major identity providers including Okta, Azure AD,
and OneLogin. I'm attaching our SSO setup guide - typical implementation takes
1-2 hours for IT teams. Happy to have our solutions engineer walk Michael through
this during POC kickoff.

**Current Vendor Contract Through Q1 (Michael's concern)**
Understood on the timing. Many customers run a parallel POC while finishing out
existing contracts to ensure seamless transition. We can structure the POC to
conclude before your Q1 renewal decision point, giving you proof of value before
making the switch.

**Training Requirements (Sarah's question)**
Our average onboarding time is <30 minutes for end-users like Sarah. I'm including
our quick-start video library and interactive tutorial link below. During POC we'll
do a 1-hour train-the-trainer session with your team.
```

### Resources Attached/Linked
**Purpose**: Provide promised materials, enable further evaluation

**Template**:
```
Resources as promised:

- {Resource name}: {Link or attachment} - {What it contains}
- {Resource name}: {Link or attachment} - {What it contains}
```

**Example**:
```
Resources as promised:

- **Technical Integration Guide**: [Link] - Salesforce API setup, SSO config,
  custom field mapping instructions
- **Demo Recording**: [Link] - Today's session with timestamps for each feature
- **Customer Case Study**: [Link] - Healthcare Fortune 500 company with similar
  Salesforce reporting use case (80% time savings)
- **Interactive Trial**: [Link] - 14-day sandbox environment with sample data
  (credentials in separate email)
```

### Next Steps Section
**Purpose**: Advance deal to next stage (POC, proposal, commercial discussion)

**Default structure**: Numbered list (3-4 items) unless AE corpus prefers simpler/shorter format

**Template**:
```
Proposed next steps:

1. **Your team**: {Technical evaluation action} by {date}
2. **Our team**: {Supporting action} by {date}
3. **Both**: {Next meeting - POC kickoff, pricing call, etc.} on {proposed date/time}
```

**Example**:
```
Proposed next steps:

1. **Your team**: Michael reviews SSO integration guide, Sarah explores trial
   environment with your Salesforce data by Friday 11/17
2. **Our team**: Set up POC environment with your Salesforce instance, prepare
   custom dashboard mockups for your exec personas by Monday 11/20
3. **Both**: POC kickoff call Tuesday 11/21 at 10am ET (I'll send invite) -
   Technical setup walkthrough + pricing discussion with Jane

This timeline positions us to have POC results before your December budget review,
as you mentioned in discovery.
```

### Closing Paragraph
**Purpose**: Express confidence, invite questions, maintain momentum

**Default structure**: 1-2 sentences unless AE corpus prefers different style

**Template**:
```
{Confidence statement about fit}. {Question invitation}. {Timeline reinforcement}.

{Closing},
{Signature}
```

**Example**:
```
Based on today's conversation, I'm confident our platform can deliver the 80%
reporting time savings and real-time visibility you're targeting. Let me know if
any other questions come up as you explore the trial environment. Looking forward
to kicking off the POC next week.

Best regards,
Sarah Chen
```

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
generated_by: sales-communications/email_demo_followup
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

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_demo_followup_{DATE}.md`

**Filename format**: `email_demo_followup_2025-11-14.md`

---

## Error Handling

**Missing demo in History**:
- Generate generic demo follow-up structure
- Prompt user: "I don't see a recent demo in History. Add demo details first?"

**Missing questions/concerns**:
- Omit Q&A section
- Focus on recap and next steps only

**Missing Decision Criteria**:
- Generic feature recap (not mapped to requirements)

**Missing D7 tasks**:
- Suggest standard next steps: POC, trial, pricing discussion

**No attendee names**:
- Use generic salutation "team" or "all"

---

## Demo Follow-Up Best Practices

**Timing**: Send within 4-6 hours while demo is fresh in their minds

**Personalization**:
- Reference specific questions from specific attendees
- Call out "aha moments" or positive reactions during demo
- Acknowledge concerns transparently (don't ignore objections)

**Advancement**:
- Always include concrete next step (POC, trial, pricing call)
- Tie timeline to their business drivers ("before your Q1 budget review")
- Make it easy to say yes (provide resources, reduce friction)

**Positioning**:
- If competing against incumbent: Emphasize ease of switching, parallel POC
- If competing against build-in-house: Emphasize time-to-value, total cost
- If competing against other vendors: Differentiate on specific capabilities shown

---

## Example Output

```markdown
---
generated_by: sales-communications/email_demo_followup
generated_on: 2025-11-13T18:45:00Z
deal_id: AcmeCorp
sources:
  - sample-data/Runtime/Sessions/AcmeCorp/deal.md
  - sample-data/Runtime/_Shared/style/ae_sarahchen_corpus.md
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md
---

**Subject**: Re: AcmeCorp Demo - Technical Docs & POC Timeline

Hi Jane,

Thanks to you, Michael, and Sarah for the time today. I enjoyed showing you our
Salesforce integration and hearing Sarah's question about custom field mapping -
that's exactly the kind of flexibility our platform was designed for.

I wanted to follow up on the technical questions raised and outline next steps
toward your Q1 deployment timeline.

Here's what we covered:

- **Salesforce Native Integration**: Showed how our API connector maps to custom
  fields in under 5 minutes, addressing your need for seamless data sync without
  IT overhead.

- **Executive Dashboard Templates**: Walked through pre-built templates for VP
  and C-suite personas, demonstrating how you can deliver board-ready reports
  within 24 hours.

- **Drill-Down Analytics**: Showed Sarah how end-users can click from summary
  metrics into underlying data without building custom queries.

- **Mobile Access**: Demoed the iOS app for on-the-go reporting, addressing your
  request for executive access during travel.

On the questions you raised:

**SSO Compatibility (Michael's question)**
We support SAML 2.0 SSO with all major identity providers including Okta, Azure AD,
and OneLogin. I'm attaching our SSO setup guide - typical implementation takes
1-2 hours for IT teams. Happy to have our solutions engineer walk Michael through
this during POC kickoff.

**Current Vendor Contract Through Q1 (Michael's concern)**
Understood on the timing. Many customers run a parallel POC while finishing out
existing contracts to ensure seamless transition. We can structure the POC to
conclude before your Q1 renewal decision point, giving you proof of value before
making the switch.

**Training Requirements (Sarah's question)**
Our average onboarding time is <30 minutes for end-users like Sarah. I'm including
our quick-start video library and interactive tutorial link below. During POC we'll
do a 1-hour train-the-trainer session with your team.

Resources as promised:

- **Technical Integration Guide**: [Link] - Salesforce API setup, SSO config,
  custom field mapping instructions
- **Demo Recording**: [Link] - Today's session with timestamps for each feature
- **Customer Case Study**: [Link] - Healthcare Fortune 500 company with similar
  Salesforce reporting use case (80% time savings)
- **Interactive Trial**: [Link] - 14-day sandbox environment with sample data
  (credentials in separate email)

Proposed next steps:

1. **Your team**: Michael reviews SSO integration guide, Sarah explores trial
   environment with your Salesforce data by Friday 11/17
2. **Our team**: Set up POC environment with your Salesforce instance, prepare
   custom dashboard mockups for your exec personas by Monday 11/20
3. **Both**: POC kickoff call Tuesday 11/21 at 10am ET (I'll send invite) -
   Technical setup walkthrough + pricing discussion with Jane

This timeline positions us to have POC results before your December budget review,
as you mentioned in discovery.

Based on today's conversation, I'm confident our platform can deliver the 80%
reporting time savings and real-time visibility you're targeting. Let me know if
any other questions come up as you explore the trial environment. Looking forward
to kicking off the POC next week.

Best regards,
Sarah Chen
Senior Account Executive
Example Corp Solutions
sarah.chen@example.com | (555) 123-4567
```

---

**End of Pattern: email_demo_followup**
