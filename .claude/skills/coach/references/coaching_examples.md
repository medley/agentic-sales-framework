# Coaching Examples Reference

Example coaching sessions for different stages, methodologies, and deal scenarios. Use these as templates for structuring coaching output.

## Example 1: Sandler Discovery → Qualify (Pain Stage)

**Deal Context:**
- Company: TechCorp
- Stage: 2 (Qualify - Sandler Pain)
- ACV: $250K
- Close Date: Q2 2025
- Champion: Sarah (VP Product), engaged
- Economic Buyer: CFO (not yet engaged)
- Last Activity: Discovery call 3 days ago

**Coaching Output (400-word target):**

```markdown
# Deal Coaching Report - TechCorp

**Generated:** 2025-11-14 | **Stage:** 2 (Pain) | **Methodology:** Sandler | **Health:** ⚠️ Needs Attention

## Deal Snapshot
- Stage 2 (Pain) - Discovery complete, pain qualification incomplete
- ACV: $250K | Close Date: Q2 2025 (90 days) | Probability: 40%
- Last Activity: 2025-11-11 (3 days ago) - Discovery call with VP Product
- Champion: Sarah Chen (VP Product), strong | Economic Buyer: CFO (NOT ENGAGED)
- Competition: None known
- Timeline: Demo requested for 2025-11-20

## Stage Health
- Exit Criteria: 2/5 met - Missing: Pain intensity, Budget confirmed, Economic Buyer access
- Required Artifacts: 1/3 completed - Missing: Pain quantification, Budget discussion notes
- Readiness: ⚠️ Blocked - Cannot advance without Economic Buyer engagement

## Top 3 Risks
1. 🔴 **Pain intensity unclear** - Sarah used intellectual language ("would be nice", "thinking about"), no emotional urgency → Run pain funnel questions
2. 🔴 **Economic Buyer (CFO) not engaged** - Budget unconfirmed, no access to decision maker → Request intro from Sarah
3. 🟡 **Demo requested before qualification** - Risk of free consulting (Sandler principle) → Delay demo until budget/pain qualified

## Recommended Actions

### D1 (Next 24 Hours)
- [ ] **2025-11-15 EOD** - Email Sarah (champion) to request 15-min CFO intro call (Owner: AE)
  - Why: Sandler - must qualify budget with Economic Buyer before presenting solution
- [ ] **2025-11-15 EOD** - Prepare pain funnel questions for CFO call focusing on cost of status quo (Owner: AE)
  - Why: Pain intensity insufficient (below 7/10), need emotional language and quantified impact

### D7 (This Week)
- [ ] **2025-11-18** - Schedule CFO call (if Sarah confirms availability) to qualify budget and compelling event (Owner: AE)
  - Why: Exit criteria requires Economic Buyer validation of pain and budget
- [ ] **2025-11-19** - Delay demo to 2025-11-25 (after CFO qualification) to avoid free consulting (Owner: AE)
  - Why: Sandler principle - don't present solutions before pain/budget/decision qualified
- [ ] **2025-11-20** - Document pain quantification from CFO call (time, cost, risk of inaction) (Owner: AE)
  - Why: Required artifact for stage advancement, needed for proposal justification

## Missing Information
- [ ] Pain intensity rating (1-10) from Economic Buyer → Ask directly in CFO call
- [ ] Budget allocated or requires approval? → CFO confirmation needed
- [ ] Decision timeline and approval process → Map paper process with CFO

## Suggested Skills to Run Next
1. **prep-discovery** - Prepare for CFO qualification call
   - Parameters: `deal_path`, `call_type: discovery`, `focus_areas: ["pain_intensity", "budget_qualification", "decision_process"]`
   - Why: Need structured pain funnel questions and budget qualification framework for CFO discussion
```

**Key Patterns:**
- Sandler-specific language: "free consulting", "pain intensity", "disqualify if no urgency"
- D1 actions address critical blockers (Economic Buyer access)
- D7 actions reinforce methodology principles (delay demo)
- Risks cite evidence from deal (intellectual vs emotional language)

---

## Example 2: MEDDPICC Qualify → Propose (Technical Validation)

**Deal Context:**
- Company: HealthNet
- Stage: 3 (Propose - MEDDPICC Technical Validation)
- ACV: $500K
- Close Date: Q3 2025
- Champion: John (Director IT), strong
- Economic Buyer: CIO (engaged, 1 meeting)
- Last Activity: Technical deep-dive 5 days ago

**Coaching Output:**

```markdown
# Deal Coaching Report - HealthNet

**Generated:** 2025-11-14 | **Stage:** 3 (Propose) | **Methodology:** MEDDPICC | **Health:** 🟢 On Track

## Deal Snapshot
- Stage 3 (Propose) - Technical validation in progress, strong champion and Economic Buyer engagement
- ACV: $500K | Close Date: Q3 2025 (120 days) | Probability: 65%
- Last Activity: 2025-11-09 (5 days ago) - Technical deep-dive with IT team
- Champion: John Miller (Director IT), strong advocate | Economic Buyer: CIO (engaged, 1 meeting)
- Competition: Competitor X (active, POC running parallel)
- Timeline: Proposal due 2025-12-01, decision by 2025-12-15

## Stage Health
- Exit Criteria: 5/7 met (MEDDPICC) - Missing: Decision Criteria finalized, Paper Process mapped
- Required Artifacts: 3/4 completed - Missing: Executive summary for CIO
- Readiness: 🟢 Mostly Ready - Two gaps to close before proposal submission

## Top 3 Risks
1. 🟡 **Decision Criteria unclear** - John provided criteria but CIO hasn't validated (risk: criteria favor Competitor X) → Schedule CIO alignment call
2. 🟡 **Paper Process not mapped** - Procurement/Legal approval timeline unknown → John to introduce Procurement contact
3. 🟠 **Competition POC in progress** - Competitor X POC wraps 2025-11-20, stakeholder feedback unknown → Request competitive debrief from John

## Recommended Actions

### D1 (Next 24 Hours)
- [ ] **2025-11-15 EOD** - Request John schedule 30-min CIO alignment call by 2025-11-22 (Owner: AE)
  - Why: Must validate Decision Criteria directly with Economic Buyer (MEDDPICC - "D")
- [ ] **2025-11-15 EOD** - Ask John for intro to Procurement lead to map paper process (Owner: AE)
  - Why: Paper Process ("P" in MEDDPICC) required to forecast close date accurately

### D7 (This Week)
- [ ] **2025-11-18** - Prepare executive summary (1-pager) for CIO meeting highlighting Metrics (M) and business outcomes (Owner: AE)
  - Why: Required artifact, must tie solution to CIO's strategic goals
- [ ] **2025-11-20** - Schedule competitive debrief with John post-Competitor X POC (Owner: AE)
  - Why: Understand stakeholder feedback on Competitor X to refine positioning
- [ ] **2025-11-21** - Document paper process (approvals, signers, timeline) from Procurement intro (Owner: AE)
  - Why: Required to map decision timeline and identify blockers before proposal submission

## Missing Information
- [ ] Decision Criteria validated by CIO → Confirm in alignment call
- [ ] Paper Process: Who signs, in what order, by when? → Procurement intro
- [ ] Competitor X POC outcome → John debrief

## Suggested Skills to Run Next
1. **sales_communications** - Generate executive summary (1-pager) for CIO
   - Parameters: `artifact_type: onepager`, `recipient: CIO`, `focus: business_outcomes`
   - Why: Required artifact for CIO alignment call, must be metrics-focused (MEDDPICC "M")
```

**Key Patterns:**
- MEDDPICC framework explicit: Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion, Competition (M-E-D-D-P-I-C)
- D1 actions address missing MEDDPICC elements (D, P)
- Risks reference competitive dynamics (Competition in MEDDPICC)
- Artifact recommendations tied to methodology (executive summary = Metrics focus)

---

## Example 3: Generic B2B Negotiate → Close (Final Approvals)

**Deal Context:**
- Company: RetailCo
- Stage: 6 (Negotiate)
- ACV: $180K
- Close Date: 2025-11-30 (16 days away)
- Champion: Lisa (COO), strong
- Economic Buyer: CEO (signed off on proposal)
- Last Activity: Pricing negotiation 2 days ago

**Coaching Output:**

```markdown
# Deal Coaching Report - RetailCo

**Generated:** 2025-11-14 | **Stage:** 6 (Negotiate) | **Methodology:** Generic | **Health:** 🟡 Needs Attention

## Deal Snapshot
- Stage 6 (Negotiate) - Verbal agreement on pricing, awaiting contract signature
- ACV: $180K | Close Date: 2025-11-30 (16 days) | Probability: 80%
- Last Activity: 2025-11-12 (2 days ago) - Pricing call with COO and CEO
- Champion: Lisa Tran (COO), strong | Economic Buyer: CEO (verbally committed)
- Competition: None active (Competitor Y eliminated Stage 4)
- Timeline: Contract to Legal 2025-11-18, signature target 2025-11-28

## Stage Health
- Exit Criteria: 4/5 met - Missing: Legal redlines resolved
- Required Artifacts: 5/5 completed - All docs ready (MSA, SOW, BAA)
- Readiness: 🟡 On Track but Close - Legal review may delay close date

## Top 3 Risks
1. 🔴 **Legal redlines unknown** - Contract sent to Legal 2025-11-10, no feedback yet (4 days) → Follow up with COO to expedite
2. 🟡 **Close date pressure** - 16 days to signature, Legal review typically 10-14 days → May slip to early December
3. 🟠 **MSA negotiation risk** - First-time vendor, MSA may require executive review beyond Legal → Confirm approval chain with COO

## Recommended Actions

### D1 (Next 24 Hours)
- [ ] **2025-11-15 EOD** - Email COO (Lisa) to check Legal review status and request any redlines by 2025-11-20 (Owner: AE)
  - Why: 4 days in Legal with no feedback, risk of close date slip
- [ ] **2025-11-15 EOD** - Alert Sales Ops and Finance that close may slip to 2025-12-05 based on Legal timeline (Owner: AE)
  - Why: Forecast accuracy, manage internal expectations

### D7 (This Week)
- [ ] **2025-11-18** - If Legal redlines received, schedule call with COO + Legal to resolve objections same-day (Owner: AE)
  - Why: Minimize delay, show responsiveness, keep close date on track
- [ ] **2025-11-19** - Confirm MSA approval chain: Does CEO need to re-review post-Legal redlines? (Owner: AE)
  - Why: Avoid surprise approval delays after Legal resolution
- [ ] **2025-11-21** - Prep handover doc for Customer Success (run handover_builder skill) (Owner: AE)
  - Why: Deal likely to close by month-end, ensure smooth delivery transition

## Missing Information
- [ ] Legal redlines and objections → COO follow-up
- [ ] MSA approval chain post-Legal → Confirm with COO
- [ ] Signature authority: Can COO sign or CEO required? → Clarify before final contract

## Suggested Skills to Run Next
1. **sales_communications** - Draft Legal expedite email to COO
   - Parameters: `artifact_type: email`, `recipient: COO`, `context: legal_followup`
   - Why: Professional nudge to Legal without being pushy, maintain relationship while driving urgency
```

**Key Patterns:**
- Generic B2B language (no methodology jargon)
- D1 actions address close-date risk (Legal delay)
- D7 actions prepare for post-sale (handover)
- Risks focus on timeline and approval process (standard late-stage concerns)

---

## Usage in Coaching

When generating coaching reports:
1. Select example closest to deal's stage and methodology
2. Adapt structure (sections, bullet counts) but maintain brevity (400-600 words)
3. Use methodology-specific language if applicable:
   - Sandler: Pain intensity, free consulting, disqualification
   - MEDDPICC: M-E-D-D-P-I-C checklist, metrics focus
   - Generic: Standard qualification (stakeholders, pain, budget, decision, timeline)
4. Ensure D1/D7 actions are specific with What/Who/Why
5. Cite evidence from deal.md (not generic placeholders)

Load this reference when:
- User asks for example coaching sessions
- Need template for unfamiliar methodology or stage
- Otherwise, keep out of context (progressive disclosure)
