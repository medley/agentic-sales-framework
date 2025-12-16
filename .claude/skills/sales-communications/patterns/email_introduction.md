# Email: Introduction (Double Opt-In)

**Pattern**: email_introduction
**Type**: Connector email (3-party: AE, Person A, Person B)
**Timing**: After getting permission from both parties
**Purpose**: Facilitate connection between prospect and reference/expert

---

## When to Use

Send this email to:
- Connect prospect with customer reference
- Introduce prospect to technical specialist or implementation consultant
- Connect prospect with peer at similar company
- Facilitate peer-to-peer conversations (prospect-to-prospect)
- Enable subject matter expert connections

**CRITICAL**: ALWAYS get permission from both parties BEFORE sending this email. This is a "double opt-in" introduction.

**NOT for**:
- Initial cold outreach (use email_cold_outbound)
- Internal team introductions (use email_internal_prep)
- Following up after meetings (use email_discovery_recap or email_demo_followup)
- One-way information sharing (use email_exec_summary)

**Trigger Phrases**:
- "intro {PERSON_A} to {PERSON_B}"
- "connect {PROSPECT} with {REFERENCE}"
- "make introduction between {NAME} and {NAME}"
- "introduce {PROSPECT} to {EXPERT}"
- "can you connect me with {REFERENCE}"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Person A details (name, title, company, context)
   - Person B details (name, title, company, context)
   - Reason for introduction (shared interest, problem to solve, expertise needed)
3. **Permission obtained from BOTH parties** (confirm via prior conversations/emails)

**OPTIONAL**:
- Email style corpus (for tone matching)
- Brand guidelines (for signature formatting)
- Background context on why this intro makes sense

**NOT NEEDED**:
- Methodology stage inventory
- Detailed qualification data
- Deal stage information

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md or conversation history:
- **Person A**: Name, title, company, what they're looking for
- **Person B**: Name, title, company, what they can offer
- **Connection context**: Why this intro makes sense for both parties
- **Mutual value**: What each person brings to the conversation

**Example Context to Parse**:
```markdown
## Stakeholders
- Sarah Chen, VP Operations at MedTech Solutions (prospect - needs QMS implementation guidance)
- David Kim, Director QMS at BioPharma Corp (existing customer - implemented similar system last year)

## History
- 2025-11-10: Sarah asked for reference at similar company who went through QMS implementation
- 2025-11-11: Called David - he's happy to share lessons learned, available for 30min call
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system for tone matching (keep output warm and brief)

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply signature formatting only

---

## Email Structure

### Subject Line
**Formula**: Keep under 6 words, introduce both parties by name

**Options**:
- "{PERSON_A}, meet {PERSON_B}"
- "Introduction: {PERSON_A} <> {PERSON_B}"
- "Connecting {PERSON_A} and {PERSON_B}"
- "{PERSON_A} + {PERSON_B} intro"

### Email Recipients
**CRITICAL 3-PARTY FORMAT**:
- **To**: Person A (e.g., the prospect)
- **CC**: Person B (e.g., the reference/expert)
- **BCC**: AE (move self to BCC after initial send, or omit entirely)

**Alternative if both are equally important**:
- **To**: Both Person A and Person B
- **CC**: None

### Body Structure
**Purpose**: Introduce each person to the other, explain mutual value, gracefully step out

**Structure**: 3 short paragraphs, 100-150 words total

**Template**:
```
{PERSON_A_FIRST_NAME} / {PERSON_B_FIRST_NAME},

[PARAGRAPH 1: Introduce Person A to Person B]
{Person A name + title + company}, meet {Person B name + title + company}. {One sentence on what Person A is working on or needs}.

[PARAGRAPH 2: Introduce Person B to Person A]
{Person B name}, {Person A} is {context about Person A's situation}. {One sentence on why Person B is the perfect person to talk to}.

[PARAGRAPH 3: State mutual value and step out]
{Why this conversation will be valuable for both}. I'll let you two take it from here. {Optional: suggest they connect directly to schedule time}.

{Closing},
{Signature}
```

---

## Examples

### Example 1: Prospect → Customer Reference

```
Sarah / David,

Sarah Chen, VP Operations at MedTech Solutions, meet David Kim, Director of Quality at BioPharma Corp. Sarah is evaluating QMS systems and approaching a deployment decision in the next quarter.

David, Sarah is working through implementation planning and wanted to connect with someone who's been through a similar rollout. You mentioned you'd be happy to share lessons learned from your deployment last year.

I think you'll both find this conversation valuable. I'll let you two take it from here - feel free to connect directly to find a time that works.

Best,
Welf
```

### Example 2: Prospect → Technical Specialist

```
Jim / Maria,

Jim Selby, VP Engineering at GlobalPharma, meet Maria Rodriguez, our Solutions Architect specializing in validation automation. Jim's team is working through 21 CFR Part 11 compliance requirements for their new QMS.

Maria, Jim has some specific questions about electronic signature workflows and audit trail architecture that are outside my wheelhouse. You're the expert here and I know you can help.

I'll step out and let you two dig into the technical details. Maria will send you some time options directly.

Cheers,
Michael
```

### Example 3: Prospect → Peer at Similar Company

```
Lisa / Tom,

Lisa Anderson, Director of Regulatory Affairs at PharmaTech, meet Tom Chen, Head of Regulatory at BioGenix. Lisa is exploring how other companies in the space are handling document lifecycle management.

Tom, Lisa's team is wrestling with similar challenges you faced last year around SOP versioning and approval routing. You mentioned you'd be open to a peer conversation about what worked (and what didn't).

This should be a great conversation for both of you. I'll move myself to BCC so you can coordinate directly.

Best regards,
Anna
```

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_introduction
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
- Total body: 100-150 words (excluding subject and signature)
- Three short paragraphs (intro Person A, intro Person B, mutual value + step out)
- No overselling either party - be authentic and specific
- Make both parties look good (highlight relevant expertise/context)
- Graceful exit - AE steps out of the conversation
- No asks, no pressure - just facilitate the connection

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_introduction_{DATE}.md`

**Filename format**: `email_introduction_2025-11-15.md`

---

## Error Handling

**Missing Person A or Person B details**:
- Prompt user: "I need details about both people for this introduction. Who should I connect, and what context should I provide?"

**No permission confirmed**:
- WARNING: "Have you confirmed both parties are open to this introduction? Double opt-in is required."
- Prompt user to confirm before proceeding

**Unclear mutual value**:
- Prompt user: "What's the reason for this introduction? What will make this valuable for both people?"

---

## Introduction Email Best Practices

**Always get permission first**: Never surprise someone with an unsolicited introduction. Confirm both parties are open to connecting BEFORE sending.

**Make both parties look good**: Highlight relevant context and expertise that makes each person valuable to the other.

**Be specific about mutual value**: Generic "I think you two should meet" is weak. Explain exactly why this connection makes sense.

**Step out gracefully**: AE's job is to facilitate, then get out of the way. Move to BCC or let them take it from there.

**Keep it brief**: Don't write a novel. Short, warm, clear introductions work best.

**Use first names in salutation**: "Sarah / David," or "Jim / Maria," creates peer-to-peer tone.

**No pressure**: This is a gift to both parties, not a sales tactic. Don't add deadlines or urgency.

**Timing matters**:
- Send early in the week (Monday-Wednesday) so they can schedule
- Avoid Friday afternoons or right before holidays
- Consider time zones if parties are in different regions

**Follow-up protocol**:
- Move yourself to BCC after initial send
- If no response after 5-7 days, a gentle nudge is okay: "Just wanted to make sure this didn't get buried - still happy to facilitate if you're both interested"

**When NOT to use this pattern**:
- If you haven't confirmed both parties are interested (get permission first!)
- If this is an internal team intro (use email_internal_prep)
- If you need to stay involved in the conversation (then don't "step out")
- If Person B doesn't actually want to be a reference (don't volunteer them without asking)

---

## Example Output

```markdown
---
generated_by: sales-communications/email_introduction
generated_on: 2025-11-15T14:20:00Z
deal_id: MedTech_Solutions
sources:
  - sample-data/Runtime/Sessions/MedTech_Solutions/deal.md
  - sample-data/Runtime/_Shared/style/ae_welf_corpus.md
---

**To**: Sarah Chen <schen@medtechsolutions.com>
**CC**: David Kim <dkim@biopharmacorp.com>
**Subject**: Sarah, meet David

Sarah / David,

Sarah Chen, VP Operations at MedTech Solutions, meet David Kim, Director of Quality at BioPharma Corp. Sarah is evaluating QMS systems and approaching a deployment decision in the next quarter.

David, Sarah is working through implementation planning and wanted to connect with someone who's been through a similar rollout. You mentioned you'd be happy to share lessons learned from your deployment last year.

I think you'll both find this conversation valuable. I'll let you two take it from here - feel free to connect directly to find a time that works.

Best,
Welf Ludwig
Account Executive
rep@company.com
```

---

**End of Pattern: email_introduction**
