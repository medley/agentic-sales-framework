---
license: "MIT - See LICENSE.md"
---

# Next Steps — Reference Documentation

**Version:** 1.0
**Purpose:** Detailed examples, methodology walkthroughs, edge cases, and advanced patterns for the next-steps skill

---

## Table of Contents

1. [Example Outputs](#example-outputs)
2. [Methodology-Specific Guidance](#methodology-specific-guidance)
3. [Edge Cases](#edge-cases)
4. [Advanced Patterns](#advanced-patterns)
5. [Troubleshooting](#troubleshooting)

---

## Example Outputs

### Example 1: Early-Stage Discovery Deal

**Context:**
- Deal: TechCoInc
- Stage: Stage 2 (Discovery)
- Methodology: MEDDPICC
- Health: Yellow (missing champion, unclear budget)
- Last activity: Discovery call 3 days ago

**Generated Output:**

```markdown
# Next Steps - TechCoInc

**Generated:** 2025-11-17 | **Stage:** Stage 2 (Discovery) | **Health:** Yellow

## D1 Actions (Next 24 Hours)
- [ ] **Nov 18, 10 AM** - Send discovery recap email to VP Operations (Owner: You)
  Why: Confirm understanding of technical requirements before they brief Economic Buyer

## D7 Actions (This Week)
- [ ] **Nov 20** - Schedule 1:1 with Sarah Chen to explore champion potential (Owner: You)
  Why: Need internal advocate who can sell this when we're not in the room

- [ ] **Nov 22** - Request org chart and approval process document (Owner: You)
  Why: Paper Process criterion unmet - don't know how decisions get made here

- [ ] **Nov 24** - Create discovery follow-up deck with ROI framework (Owner: You + SE)
  Why: Economic Buyer asked for "business case we can take to the board"

## Missing Exit Criteria (MEDDPICC - Discovery)
❌ **Champion:** Not identified or cultivated
   → Action: Sarah Chen (Director, Quality) shows interest. Schedule 1:1 to assess.

❌ **Paper Process:** Decision timeline and approval steps unknown
   → Action: Ask "What does the approval process look like after we submit a proposal?"

❌ **Economic Buyer:** Name known (CFO) but no direct engagement yet
   → Action: Request VP Ops to intro us to CFO for strategic alignment conversation

## Suggested Skills to Run Next
1. **sales_communications/email_discovery_recap** - Send professional recap of Nov 14 discovery call
2. **prep-discovery** - Prepare for Sarah Chen 1:1 (champion cultivation focus)

---
## Provenance
source_deal: ../../deal.md
generated_by: next-steps
generated_at: 2025-11-17
methodology_ref: sample-data/Runtime/_Shared/knowledge/methodologies/MEDDPICC/stage_inventory__MEDDPICC.md
```

**Word count:** ~250 words ✅ (fits on one page)

---

### Example 2: Late-Stage Negotiation Deal

**Context:**
- Deal: Herbalife
- Stage: Stage 5 (Negotiation)
- Methodology: Sandler
- Health: Green
- Last activity: Proposal sent yesterday

**Generated Output:**

```markdown
# Next Steps - Herbalife

**Generated:** 2025-11-17 | **Stage:** Stage 5 (Negotiation) | **Health:** Green

## D1 Actions (Next 24 Hours)
- [ ] **Nov 18, 9 AM** - Follow up with Economic Buyer on proposal (Owner: You)
  Why: Proposal sent Nov 16, need to confirm receipt and schedule review call

## D7 Actions (This Week)
- [ ] **Nov 20** - Prepare negotiation playbook for potential discount requests (Owner: You + Manager)
  Why: Budget holder may push back on 3-year commitment, need pre-approved concessions

- [ ] **Nov 21** - Schedule legal review kickoff (Owner: Legal + Customer Procurement)
  Why: Close date is Dec 15, legal can take 2-3 weeks, start now to avoid delays

- [ ] **Nov 23** - Create implementation timeline with CS team (Owner: You + CS Manager)
  Why: Customer asked "When can we go live?" - need credible answer before close

## Missing Exit Criteria (Sandler - Negotiation)
✅ **Budget:** Confirmed $485K budgeted, CFO signed off
✅ **Decision Process:** 2-week legal review, then Board approval (Dec 8 meeting)
⚠️ **Pain Intensity:** Champion is 8/10, Economic Buyer only 6/10
   → Action: Re-sell pain to EB in proposal review call (focus on Q1 2026 compliance deadline)

## Suggested Skills to Run Next
1. **sales_communications/email_proposal_nudge** - Professional follow-up on Nov 16 proposal
2. **coach** - Full deal review before final negotiation stage

---
## Provenance
source_deal: ../../deal.md
generated_by: next-steps
generated_at: 2025-11-17
methodology_ref: sample-data/Runtime/_Shared/knowledge/methodologies/Sandler/stage_inventory__Sandler.md
```

**Word count:** ~260 words ✅

---

### Example 3: Stale Deal (Warning Output)

**Context:**
- Deal: AcmeCorp
- Stage: Stage 3 (Solution Design)
- Methodology: Generic
- Health: Red
- Last activity: 42 days ago

**Generated Output:**

```markdown
# Next Steps - AcmeCorp

**Generated:** 2025-11-17 | **Stage:** Stage 3 (Solution Design) | **Health:** Red

⚠️ **STALE DEAL ALERT:** Last activity was 42 days ago (Oct 6, 2025)

## D1 Actions (Next 24 Hours)
- [ ] **Nov 18** - Send re-engagement email to Champion (Owner: You)
  Why: 6+ weeks of silence is a strong disqualification signal, need to assess if deal is alive

## D7 Actions (This Week)
- [ ] **Nov 20** - Internal deal review with Manager (Owner: You + Manager)
  Why: Decide whether to keep pursuing or mark as "Closed-Lost" / "Nurture"

- [ ] **Nov 22** - If re-engaged, schedule technical validation call (Owner: You + SE)
  Why: Last conversation was solution demo, need to validate fit before investing more time

## Missing Exit Criteria (Generic - Solution Design)
❌ **Technical Validation:** No technical stakeholder sign-off documented
❌ **Economic Justification:** No ROI analysis or business case created
❌ **Timeline Agreement:** No mutual close plan or milestones agreed

## Recommended Actions
1. **Re-engage or Disqualify:** 42 days of silence suggests low priority on their end
2. **If re-engaged:** Run coach skill for full deal health assessment
3. **If no response:** Move to "Nurture" status, check back in Q1 2026

## Suggested Skills to Run Next
1. **sales_communications/email_cold_outbound** - Re-engagement email (treat like cold outreach)
2. **coach** - Full deal assessment if they respond

---
## Provenance
source_deal: ../../deal.md
generated_by: next-steps
generated_at: 2025-11-17
methodology_ref: Framework/System/methodology_loader.md (Generic fallback)
```

**Word count:** ~240 words ✅

---

## Methodology-Specific Guidance

### MEDDPICC Methodology

**Focus Areas:**
- **Metrics:** Is quantifiable impact documented? If not → Action: Schedule value discovery call
- **Economic Buyer:** Identified and engaged? If not → Action: Request intro via champion
- **Decision Criteria:** Known and documented? If not → Action: Ask "What does success look like?"
- **Decision Process:** Timeline and steps clear? If not → Action: Map approval chain
- **Paper Process:** Formal process understood? If not → Action: Request documentation
- **Identify Pain:** Business + personal pain documented? If not → Action: Pain discovery questions
- **Champion:** Identified and cultivated? If not → Action: Assess stakeholder power/willingness

**Exit Criteria Mapping:**
Each MEDDPICC element maps to stage-specific exit criteria. The next-steps skill reads these from the stage inventory and identifies gaps.

---

### Sandler Methodology

**Focus Areas:**
- **Pain:** Emotional intensity documented (1-10 scale)? If <7 → Action: Re-discover pain
- **Budget:** Not just "they have money" but "will they spend it on THIS?" If unclear → Action: Budget qualifying questions
- **Decision:** Who, when, how? If unknown → Action: Uncover decision process
- **Up-Front Contracts:** Each interaction has clear objective? If not → Action: Set agenda for next call

**Unique Sandler Guidance:**
- Sandler emphasizes disqualification. If pain <7 and budget unclear → Recommend disqualifying, not chasing.
- Next-steps skill should suggest "Disqualify this deal?" if red flags align (low pain + no budget + slow timeline)

---

### Generic Methodology (Fallback)

**When Used:**
- No methodology specified in deal.md frontmatter
- Methodology specified but no stage inventory file found

**Generic Exit Criteria:**
- **Discovery:** Understand pain, stakeholders, and fit
- **Solution Design:** Technical validation and requirements alignment
- **Proposal:** Business case, ROI, and pricing agreed
- **Negotiation:** Legal review, contracts, and final approvals
- **Close:** Signed contract, handover to CS/implementation

---

## Edge Cases

### Edge Case 1: No Gaps Found (Perfect Deal)

**Scenario:** All exit criteria met, deal is healthy, on track to close.

**Output:**
```markdown
# Next Steps - AcmeCorp

**Generated:** 2025-11-17 | **Stage:** Stage 5 (Negotiation) | **Health:** Green

✅ **All exit criteria met for current stage.**

## D1 Actions (Next 24 Hours)
- [ ] **Nov 18** - Confirm legal has contract for review (Owner: You)
  Why: Maintain momentum, avoid delays in final stage

## D7 Actions (This Week)
- [ ] **Nov 20** - Prepare mutual close plan with Champion (Owner: You)
  Why: Align on Nov 30 close date, identify any last-minute risks

## Suggested Skills to Run Next
1. **coach** - Strategic review before final close
2. **sales_communications/onepager** - Create handover doc for CS team
```

---

### Edge Case 2: Multiple Urgent Items (Triage Needed)

**Scenario:** Deal has 5+ urgent items but output must stay <600 words.

**Strategy:**
- **Prioritize ruthlessly:** Only top 2 D1 actions (most critical)
- **Consolidate D7:** Group related actions ("Complete tech validation" instead of listing 3 separate tech tasks)
- **Omit optional sections:** Skip "Missing Information" if space is tight

**Output Focus:**
- D1: 2 actions max
- D7: 3 actions max (consolidate where possible)
- Missing Exit Criteria: Top 2-3 only
- Skills: 1-2 max

---

### Edge Case 3: Conflicting Priorities

**Scenario:** Upcoming call tomorrow (needs prep) BUT also critical gap in qualification (missing Economic Buyer).

**Resolution:**
- **D1:** Prep for tomorrow's call (time-bound, can't move)
- **D7:** Address qualification gap (important but not time-critical)
- **Rationale in output:** Explain why call prep is D1 even though qualification gap is more strategic

---

## Advanced Patterns

### Pattern 1: Chained Skill Recommendations

**Goal:** Create workflow chains (next-steps → skill → next-steps)

**Example:**
```markdown
## Suggested Skills to Run Next
1. **prep-discovery** - Prepare for Nov 20 discovery call
   → After call: Re-run next-steps to incorporate new information
2. **deal_intake** - Process yesterday's call transcript
   → Then: Run next-steps to identify follow-up actions
```

---

### Pattern 2: Conditional Recommendations

**Goal:** Provide "if/then" guidance for uncertain situations

**Example:**
```markdown
## D7 Actions (This Week)
- [ ] **Nov 20** - Re-engagement call with Champion (Owner: You)
  Why: 3 weeks of silence, need to assess deal health

  **If positive response:** Schedule technical validation call
  **If slow response:** Move to nurture, check back in 30 days
  **If no response:** Disqualify and focus on active deals
```

---

### Pattern 3: Methodology Crosswalk

**Goal:** When deal uses one methodology but user thinks in another

**Example:**
If deal.md says "MEDDPICC" but user asks "What Sandler stage is this?", next-steps can include a note:

```markdown
## Methodology Note
Current stage (MEDDPICC Discovery) maps to Sandler Stage 2 (Pain).
Focus on emotional pain intensity and budget qualification.
```

---

## Troubleshooting

### Issue: Output Too Long (>600 Words)

**Solutions:**
1. **Cut rationales:** Change from "Why: Economic Buyer needs technical sign-off before Nov 30 board meeting" to "Why: EB needs tech sign-off by Nov 30"
2. **Consolidate actions:** Instead of 3 separate "send email" tasks, group as "Send 3 follow-up emails to stakeholders"
3. **Remove optional sections:** Cut "Missing Information" or "Stale Tasks"
4. **Use abbreviations:** "EB" instead of "Economic Buyer", "Tech validation" instead of "Technical validation"

---

### Issue: Deal Has No Recent Activity

**Detection:** Check deal.md History section, if last entry >30 days ago → Stale deal

**Output Adjustments:**
- Add warning banner at top
- D1: Focus on re-engagement (not advancing deal)
- D7: Internal review to decide pursue vs disqualify
- Suggest: coach for full assessment

---

### Issue: No Methodology Specified

**Fallback Behavior:**
1. Use Generic methodology exit criteria (see methodology_loader.md)
2. Note in output: "Using Generic best practices (no methodology specified in deal.md)"
3. Suggest: Update deal.md frontmatter with preferred methodology

---

### Issue: User Requests Bulk Next-Steps ("Update all my deals")

**Out of Scope for v1.0:**
Current skill is single-deal focused. For portfolio-level next-steps, recommend:
- Run next-steps individually for each active deal
- OR use portfolio skill (provides high-level next actions across all deals)

**Future Enhancement:** Could add bulk mode in v2.0

---

## Version History

- **1.0** (2025-11-14): Initial reference documentation
