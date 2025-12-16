<!--
DEAL NOTE INPUT FORMAT

This template defines the structure for deal tracking. Users fill this in
with deal context, and skills like `coach`, `prep-discovery`, and `next-steps`
read this file to generate context-aware outputs.

The intelligence is in the skills that process this input, not in this template.
Skills use methodology loaders (Sandler, MEDDPICC) to provide stage-specific
coaching, risk analysis, and actionable next steps based on the data here.

See: .claude/skills/ for the skills that consume this format.
-->

---
deal_id: "{{company_name_slug}}"
deal_name: "{{COMPANY_NAME}}"
owner: "{{AE_NAME}}"
stage: ""
health: ""
acv: ""
close_date: ""
industry: ""
evaluation_status: ""
last_updated: "{{DATE}}"
methodology: "Generic"
metrics: ""
economic_buyer: ""
decision_criteria: ""
decision_process: ""
pain: ""
champion: ""
competition: ""
---

# 1. Deal Overview

**Company:** {{COMPANY_NAME}}
**Industry:**
**Deal Status:**
**Quote:**
**Salesforce Stage:**

## Financial Summary

- **ACV:**
- **Year 1 Total:**
- **Contract Term:**
- **Total Contract Value:**
- **Expansion Potential:**

## Solution Scope

**Products:**

**Deployment:**
- Users:
- Locations:
- Key requirements:

## Critical Timeline

- **Project Kickoff:**
- **Target Go-Live:**
- **Hard Deadline:**
- **Urgency:**

## Strategic Context

Why this deal matters strategically:

---

# 2. History

**[DATE]** - [Event]
- Details
- Key takeaways
- Commitments made

**[DATE]** - [Event]
- Details

---

# 3. D1 Tasks (Next 24 Hours)

1. **[Task]**
   - Owner:
   - Why it matters:
   - Expected outcome:

---

# 4. D7 Tasks (Next 7 Days)

1. **[Task]** (Owner)
   - Context:
   - Action:
   - Success criteria:

---

# 5. Stakeholder Map

## Champion

**[Name]** - [Title]
- **Email:**
- **Phone:**
- **Role:**
- **Power Level:**
- **Engagement:**
- **Evidence:**

## Economic Buyer

**[Name]** - [Title]
- **Email:**
- **Phone:**
- **Authority:**
- **Engagement:**

## Procurement/Execution

**[Name]** - [Title]
- **Email:**
- **Phone:**
- **Role:**
- **Engagement:**

## Key Operational Stakeholders

**[Name]** - [Title/Role]
- Influence:
- Pain Points:

## Decision Committee

- Who makes the final decision?
- Evaluation method:
- Process:

---

# 6. MEDDPICC Snapshot

## Metrics

**Current State Pain:**
-

**Target Success Metrics:**
-

## Economic Buyer

**Identified:**
**Authority:**
**Evidence:**

## Decision Criteria (How We Win)

1.
2.
3.

## Decision Process

- **Process:**
- **Committee:**
- **Format:**
- **Timeline:**
- **Current Stage:**

## Pain

**Primary Pain Points:**

1. **[Pain Category]**
   - Impact:
   - Evidence:

## Champion

**[Name]** - [Title]
**Power:**
**Engagement:**

**Evidence of Championship:**
-

## Competition

**Primary Competitor:**

**Why They're Leaving Current Vendor:**
1.
2.
3.

**Other Competitors:**

---

# 7. Risks

## Implementation Risks

### HIGH PRIORITY

**Risk #1: [Risk Name]**
- **Impact:**
- **Mitigation:**
  -
  -

## Deal Expansion Risks

**Risk: [Risk Name]**
- **Impact:**
- **Mitigation:**

---

# 8. Next Steps & Mutual Close Plan

## [Current Phase Name]

**[Date/Milestone]** - [Event]
- **Owner:**
- **Objective:**
- **Actions:**

## [Next Phase Name]

**Timeline:**
-

**Actions:**
-

## Expansion Opportunities

**Phase 2 ([Timeframe]):** [Products]
- **Evidence:**
- **Priority:**

---

# 9. Generated Artifacts

**Generated on:** {{DATE}}

**[Category]:**
- **[DATE]** - `[file_path]` - [Description]

---

# 10. Deal Intelligence Summary

## Deal Health: [GREEN/YELLOW/RED]

**Status:**

**Why This Deal Succeeded/Is Progressing:**

1. **[Factor]:**
2. **[Factor]:**

## Critical Success Factors for [Next Phase]

1.
2.
3.

## Expansion Strategy

**Near-term ([Timeframe]):**
-

**Medium-term ([Timeframe]):**
-

**Long-term ([Timeframe]):**
-

## Key Relationships to Maintain

-
-

## Strategic Alignment

How this deal aligns with customer's strategic initiatives:

---

**Current Status:**
**Confidence Level:**
**Next Milestone:**
**Target Close:**
