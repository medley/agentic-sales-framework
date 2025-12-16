# Document: Customer Meeting Agenda

**Pattern**: agenda_customer
**Type**: Customer-facing document
**Timing**: 24 hours before scheduled meeting
**Purpose**: Structure productive meetings, demonstrate preparation, set expectations

---

## When to Use

Create this agenda before customer calls to:
- Demonstrate professionalism and respect for their time
- Align on meeting objectives and expected outcomes
- Surface any misalignment before the meeting (not during)
- Create structure for productive discussion
- Provide reference document for meeting flow

**Trigger Phrases**:
- "Draft customer agenda for {DEAL}"
- "Create call agenda for {meeting type}"
- "Prepare customer meeting agenda"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Upcoming meeting details (from D7 tasks or History)
   - Meeting type (discovery, demo, technical deep-dive, pricing, executive review)
   - Attendees from both sides (from Stakeholders section)
   - Current stage (determines agenda focus)
3. **NOTE**: Do NOT load email style corpus (not applicable for documents)

**OPTIONAL**:
- Brand guidelines (for document formatting, headers, logos)
- Methodology stage inventory (for stage-appropriate agenda items)

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Meeting type**: From D7 tasks or upcoming History entry (discovery, demo, technical deep-dive, pricing, QBR)
- **Meeting date/time**: From D7 tasks or deal note
- **Duration**: Typically 30min (discovery), 60min (demo), 90min (technical/exec)
- **Customer attendees**: From Stakeholders section (names, titles, roles)
- **Your attendees**: From D7 tasks or standard team (AE, SE, CSM, exec)
- **Meeting objectives**: From current stage + recent History (what needs to be accomplished)
- **Open items**: From D7 tasks (questions to answer, decisions to make)
- **Decision criteria**: From MEDDPICC (topics that must be addressed)

**Example D7 Task to Parse**:
```markdown
## D7 Tasks (Week of 2025-11-11)
- [ ] Technical deep-dive call with AcmeCorp IT team - Nov 16 at 2pm ET (60min)
  - Attendees: Michael Chen (Director IT), Sarah Park (Data Analyst), Tom (our SE)
  - Topics: SSO integration, custom field mapping, data retention policies
  - Goal: Get IT signoff on technical architecture before proposal
```

### 2. Load Brand Guidelines (Section 2 of _common.md)

If brand_guidelines.md exists:
- Apply document header format (logo, company name)
- Use company colors/fonts if specified
- Include footers with contact info, disclaimers
- Match tone guidance for external documents

If missing: Use clean, professional markdown format

### 3. Load Methodology Guidance (Section 4 of _common.md)

If MEDDPICC stage inventory available:
- Use stage-appropriate agenda structure
- Include methodology-specific topics (e.g., Economic Buyer engagement, Champion validation)
- Ensure agenda advances stage exit criteria

If missing: Use generic meeting best practices by type

---

## Document Structure

### Header Section

**With Brand Guidelines**:
```
[Company Logo]
{Your Company Name}

MEETING AGENDA

{Customer Company Name}
{Meeting Type}: {Topic}
{Date} | {Time} | {Duration}
```

**Without Brand Guidelines** (generic):
```
# Meeting Agenda: {Meeting Type}

**Customer**: {Customer Company Name}
**Date**: {Date}
**Time**: {Time} {Timezone}
**Duration**: {Duration}
**Format**: {Zoom/Teams/In-person + link if applicable}
```

### Attendees Section

**Purpose**: Confirm who's attending, identify missing stakeholders

**Structure**:
```
## Attendees

**{Customer Company}**:
- {Name}, {Title} - {Role in decision/evaluation}
- {Name}, {Title} - {Role in decision/evaluation}

**{Your Company}**:
- {Name}, {Title} - {Role in meeting}
- {Name}, {Title} - {Role in meeting}
```

**Example**:
```
## Attendees

**AcmeCorp**:
- Michael Chen, Director of IT - Technical architecture approval
- Sarah Park, Data Analyst - End-user requirements, testing

**Example Corp Solutions**:
- Sarah Chen, Account Executive - Facilitate discussion
- Tom Rodriguez, Solutions Engineer - Technical deep-dive
```

**Note**: If Economic Buyer missing from attendees, consider if agenda should be adjusted or meeting rescheduled.

### Meeting Objectives Section

**Purpose**: Align on what success looks like for this meeting

**Structure**:
```
## Meeting Objectives

By the end of this meeting, we aim to:

1. {Primary objective with success criteria}
2. {Secondary objective with success criteria}
3. {Tertiary objective if applicable}
```

**Example (Technical Deep-Dive)**:
```
## Meeting Objectives

By the end of this meeting, we aim to:

1. **Technical Architecture Approval**: Get IT signoff that our Salesforce integration
   approach meets AcmeCorp security and data governance requirements

2. **Integration Scope Clarity**: Define exact custom fields to map, SSO provider
   details, and data retention policies

3. **Timeline Confirmation**: Align on technical implementation timeline to support
   Jan 15 go-live target
```

**Best Practices**:
- Start with verb (Get, Define, Align, Review, Decide)
- Include success criteria (what "done" looks like)
- Prioritize (most important first)
- Limit to 2-4 objectives (more = unfocused meeting)

### Agenda Items Section

**Purpose**: Time-boxed meeting flow

**Structure**:
```
## Agenda

| Time | Duration | Topic | Owner | Outcome |
|------|----------|-------|-------|---------|
| {start} | {min} | {topic} | {who leads} | {what's decided/delivered} |
| {start} | {min} | {topic} | {who leads} | {what's decided/delivered} |
```

**Example (60-minute Technical Deep-Dive)**:
```
## Agenda

| Time | Duration | Topic | Owner | Outcome |
|------|----------|-------|-------|---------|
| 2:00 PM | 5 min | Introductions & Objectives | Sarah (AE) | Alignment on meeting goals |
| 2:05 PM | 15 min | Salesforce Integration Architecture | Tom (SE) | Review API approach, SSO setup |
| 2:20 PM | 15 min | Custom Field Mapping Deep-Dive | Sarah P. | Define exact fields to sync |
| 2:35 PM | 10 min | Data Security & Retention Policies | Michael | Confirm encryption, retention rules |
| 2:45 PM | 10 min | Q&A - Open Technical Questions | All | Address any concerns |
| 2:55 PM | 5 min | Next Steps & Timeline Confirmation | Sarah (AE) | Agree on implementation timeline |
```

**Time Boxing Best Practices**:
- Start/end on time (build buffer into items, not end)
- Put critical items early (energy/attention highest)
- Assign owners (who drives that segment)
- Define outcomes (not just topics)

**Agenda Structure by Meeting Type**:

**Discovery Call (30-45 min)**:
1. Intros & context (5 min)
2. Current state exploration (15 min) - THEM talking
3. Requirements/pain points deep-dive (15 min) - THEM talking
4. High-level solution fit (5 min) - YOU brief
5. Next steps (5 min)

**Demo Call (45-60 min)**:
1. Intros & agenda align (5 min)
2. Requirements recap (5 min) - Confirm you heard them
3. Solution demo focused on THEIR use cases (30 min) - Interactive
4. Q&A (10 min)
5. Next steps (5 min)

**Technical Deep-Dive (60-90 min)**:
1. Intros & objectives (5 min)
2. Architecture overview (15 min)
3. Integration details (20 min) - Get specific
4. Security/compliance review (15 min)
5. Q&A (10 min)
6. Next steps (5 min)

**Executive Business Review (45-60 min)**:
1. Intros & context (5 min)
2. Business case recap (10 min) - ROI, metrics
3. Proposed solution (15 min) - High-level, business focused
4. Commercial terms (10 min) - Pricing, contract structure
5. Decision process discussion (10 min) - Timeline, approvals
6. Next steps (5 min)

### Background/Context Section (Optional)

**Purpose**: Remind attendees of previous discussions (useful for multi-stakeholder meetings where not everyone was in prior calls)

**Structure**:
```
## Background

{1-2 paragraph summary of deal to date}

**Previous Conversations**:
- {Date}: {Call type} - {Key outcomes}
- {Date}: {Call type} - {Key outcomes}
```

**Example**:
```
## Background

AcmeCorp is evaluating reporting automation solutions to replace their current
manual process that consumes 50+ hours/month of team time. They need a solution
operational by Jan 15, 2026 to support annual planning cycle.

**Previous Conversations**:
- Nov 12: Discovery call with Jane Smith (VP Ops) - Identified pain points, budget approved
- Nov 13: Product demo with Jane, Michael, Sarah - Showed Salesforce integration, dashboards
- Nov 14: Proposal sent - Enterprise plan, $144K ACV, 12-month term
```

### Open Items Section

**Purpose**: Surface questions/concerns before the meeting (better to address via email if possible)

**Structure**:
```
## Open Items & Questions

**For AcmeCorp to address**:
- {Question or decision needed from customer}
- {Question or decision needed from customer}

**For Example Corp to address**:
- {Question or information we owe customer}
- {Question or information we owe customer}
```

**Example**:
```
## Open Items & Questions

**For AcmeCorp to address**:
- Which SSO provider does AcmeCorp use? (Okta, Azure AD, OneLogin, other?)
- What are your data retention policies for reporting data? (90 days, 1 year, indefinite?)
- Are there any Salesforce custom objects beyond standard objects we should map?

**For Example Corp to address**:
- Provide example SSO configuration for AcmeCorp's IdP
- Share data encryption specifications (at-rest and in-transit)
- Clarify user licensing model for view-only dashboard users
```

**Best Practices**:
- Send agenda 24 hours before meeting (gives time to prep answers)
- Assign ownership (who answers what)
- Prioritize (most critical questions first)

### Next Steps Section

**Purpose**: Pre-define what happens after this meeting (speeds decision-making)

**Structure**:
```
## Proposed Next Steps

Following this meeting (pending discussion outcomes):

1. **{Action item}** - Owner: {who}, Due: {when}
2. **{Action item}** - Owner: {who}, Due: {when}
3. **{Meeting/milestone}** - Date: {when}
```

**Example**:
```
## Proposed Next Steps

Following this meeting (pending technical signoff):

1. **Example Corp sends technical implementation plan** - Owner: Tom (SE), Due: Nov 17
2. **AcmeCorp IT reviews and approves architecture** - Owner: Michael, Due: Nov 21
3. **Commercial discussion call with Jane** - Date: Nov 22 at 3pm ET
4. **Contract sent (if agreed)** - Owner: Sarah (AE), Due: Nov 23
```

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/agenda_customer
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
meeting_type: {discovery|demo|technical|pricing|executive}
meeting_date: {YYYY-MM-DD}
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
  - sample-data/Runtime/_Shared/knowledge/methodologies/{METHOD}/stage_inventory__{METHOD}.md  # if loaded
---
```

### 2. Compose Document

Follow structure above with actual content from deal.md

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/agenda_customer_{MEETING_TYPE}_{DATE}.md`

**Filename format**: `agenda_customer_technical_2025-11-16.md`

---

## Error Handling

**No upcoming meeting in D7 tasks**:
- Prompt user: "I don't see an upcoming meeting scheduled. Add meeting details to D7 tasks?"
- Or generate generic agenda structure and ask for meeting details

**Missing attendee information**:
- Use generic "Customer team" and "Our team"
- Suggest updating Stakeholders section

**Missing meeting type**:
- Assume based on current stage:
  - Discovery stage → discovery call
  - Demo/Evaluation stage → demo or technical deep-dive
  - Proposal/Negotiation stage → pricing or executive review

**Missing stage/context**:
- Generate generic professional meeting agenda
- Include placeholder sections for user to fill in

---

## Customer Agenda Best Practices

### Why Send Agendas?

**Benefits**:
- Signals professionalism and respect for their time
- Surfaces misalignment BEFORE meeting (saves everyone time)
- Higher-quality meetings (attendees come prepared)
- Creates paper trail for what was agreed to discuss
- Reduces no-shows and reschedules

### When to Send

**Timing**: 24 hours before meeting (not too early, not last-minute)

**Format**: Send as:
- PDF attachment (if brand guidelines available with logo/formatting)
- Markdown in email body (if no branding, keeps it simple)
- Google Doc link (if collaborative agenda with customer input)

### What to Avoid

**Don't**:
- Over-schedule (leave buffer, meetings run long)
- Make it one-sided (you talking for 45 min)
- Ignore their objectives (ask what they want to cover)
- Skip the "next steps" section (always advance the deal)

**Do**:
- Keep it concise (1-2 pages max)
- Focus on THEIR objectives (not your pitch)
- Assign time/owners (creates accountability)
- Send with email: "Here's the agenda - let me know if anything's missing"

---

## Example Output

```markdown
---
generated_by: sales-communications/agenda_customer
generated_on: 2025-11-14T10:00:00Z
deal_id: AcmeCorp
meeting_type: technical
meeting_date: 2025-11-16
sources:
  - sample-data/Runtime/Sessions/AcmeCorp/deal.md
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md
---

# Meeting Agenda: Technical Deep-Dive

**Customer**: AcmeCorp
**Date**: Friday, November 16, 2025
**Time**: 2:00 PM ET
**Duration**: 60 minutes
**Format**: Zoom (link in calendar invite)

---

## Attendees

**AcmeCorp**:
- Michael Chen, Director of IT - Technical architecture approval
- Sarah Park, Data Analyst - End-user requirements, testing

**Example Corp Solutions**:
- Sarah Chen, Account Executive - Facilitate discussion
- Tom Rodriguez, Solutions Engineer - Technical deep-dive

---

## Meeting Objectives

By the end of this meeting, we aim to:

1. **Technical Architecture Approval**: Get IT signoff that our Salesforce integration
   approach meets AcmeCorp security and data governance requirements

2. **Integration Scope Clarity**: Define exact custom fields to map, SSO provider
   details, and data retention policies

3. **Timeline Confirmation**: Align on technical implementation timeline to support
   Jan 15 go-live target

---

## Agenda

| Time | Duration | Topic | Owner | Outcome |
|------|----------|-------|-------|---------|
| 2:00 PM | 5 min | Introductions & Objectives | Sarah Chen | Alignment on meeting goals |
| 2:05 PM | 15 min | Salesforce Integration Architecture | Tom Rodriguez | Review API approach, SSO setup |
| 2:20 PM | 15 min | Custom Field Mapping Deep-Dive | Sarah Park | Define exact fields to sync |
| 2:35 PM | 10 min | Data Security & Retention Policies | Michael Chen | Confirm encryption, retention rules |
| 2:45 PM | 10 min | Q&A - Open Technical Questions | All | Address any concerns |
| 2:55 PM | 5 min | Next Steps & Timeline Confirmation | Sarah Chen | Agree on implementation timeline |

---

## Background

AcmeCorp is evaluating reporting automation solutions to replace their current
manual process that consumes 50+ hours/month of team time. They need a solution
operational by Jan 15, 2026 to support annual planning cycle.

**Previous Conversations**:
- Nov 12: Discovery call with Jane Smith (VP Ops) - Identified pain points, budget approved
- Nov 13: Product demo with Jane, Michael, Sarah - Showed Salesforce integration, dashboards
- Nov 14: Proposal sent - Enterprise plan, $144K ACV, 12-month term

---

## Open Items & Questions

**For AcmeCorp to address**:
- Which SSO provider does AcmeCorp use? (Okta, Azure AD, OneLogin, other?)
- What are your data retention policies for reporting data? (90 days, 1 year, indefinite?)
- Are there any Salesforce custom objects beyond standard objects we should map?

**For Example Corp to address**:
- Provide example SSO configuration for AcmeCorp's IdP
- Share data encryption specifications (at-rest and in-transit)
- Clarify user licensing model for view-only dashboard users

---

## Proposed Next Steps

Following this meeting (pending technical signoff):

1. **Example Corp sends technical implementation plan** - Owner: Tom Rodriguez, Due: Nov 17
2. **AcmeCorp IT reviews and approves architecture** - Owner: Michael Chen, Due: Nov 21
3. **Commercial discussion call with Jane Smith** - Date: Nov 22 at 3pm ET
4. **Contract sent (if agreed)** - Owner: Sarah Chen, Due: Nov 23

---

**Contact**: Sarah Chen | sarah.chen@example.com | (555) 123-4567
```

---

**End of Pattern: agenda_customer**
