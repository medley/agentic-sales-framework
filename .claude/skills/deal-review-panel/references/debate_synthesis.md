# Debate Synthesis Protocol

This file defines how to combine outputs from 4 specialized reviewers, resolve conflicts, and generate a unified coaching report.

---

## Synthesis Workflow

### Phase 1: Collect Independent Analyses

**Inputs:** 4 reviewer outputs (200 words each)

**For each reviewer, extract:**
- Top 3 risks identified
- Recommended D1 actions (next 24 hours)
- Recommended D7 actions (next 7 days)
- Key gaps or missing information
- Overall sentiment (Optimistic | Neutral | Pessimistic)

**Create structured data:**
```
{
  "Qualification Analyst": {
    "risks": ["Risk 1", "Risk 2", "Risk 3"],
    "d1_actions": ["Action 1", "Action 2"],
    "d7_actions": ["Action 1", "Action 2", "Action 3"],
    "gaps": ["Gap 1", "Gap 2"],
    "sentiment": "Pessimistic"
  },
  ...
}
```

### Phase 2: Collect Debate Responses

**Inputs:** 4 reviewer rebuttals (100 words each)

**For each reviewer, extract:**
- Agreements with other reviewers (which points, why)
- Disagreements with other reviewers (which points, why)
- New insights from cross-review

**Create conflict map:**
```
Conflict 1: Qualification Analyst vs. Executive Alignment Coach
- QA says: "Disqualify - no Economic Buyer after 45 days"
- EAC says: "Champion securing CFO intro next week, don't bail yet"
- Evidence to resolve: deal.md timeline, champion track record

Conflict 2: Competitive Strategist vs. Deal Mechanics
- CS says: "Aggressive positioning needed NOW before competitor locks in"
- DM says: "Wait for legal approval before pushing hard (risk souring relationship)"
- Evidence to resolve: Current stage, legal timeline, competitive threat severity
```

### Phase 3: Resolve Conflicts

**For each conflict:**

1. **Identify conflict type:**
   - **Timing disagreement** (do X now vs. later) → Resolve based on timeline urgency and risk
   - **Priority disagreement** (focus on A vs. B) → Resolve based on stage exit criteria and blockers
   - **Approach disagreement** (aggressive vs. conservative) → Resolve based on deal health and relationship strength
   - **Evidence disagreement** (optimistic vs. pessimistic interpretation) → Resolve based on actual deal.md data

2. **Apply resolution framework:**

   **A. Check deal evidence:**
   - What does deal.md say? (facts > interpretation)
   - What's the stage and exit criteria? (methodology grounds decision)
   - What's the timeline? (urgency drives prioritization)

   **B. Apply heuristics:**
   - **Stage 1-2 (Discover/Qualify):** Favor Qualification Analyst (disqualification is success early)
   - **Stage 3-4 (Propose/Select):** Favor Competitive Strategist (positioning critical mid-stage)
   - **Stage 5-6 (Negotiate/Close):** Favor Deal Mechanics (execution risk is highest)
   - **All stages:** Executive Alignment Coach wins on Economic Buyer engagement questions

   **C. Synthesize nuanced recommendation:**
   - Not "pick a winner" but "sequence both perspectives"
   - Example: "Secure CFO intro (per EAC) by EOD tomorrow, but set 7-day deadline (per QA) - disqualify if no meeting scheduled"

3. **Document resolution:**
   - Note the conflict in final report
   - Show synthesis rationale
   - Provide sequenced action (not binary choice)

### Phase 4: Build Consensus Recommendations

**High-confidence actions (3-4 reviewers agree):**
- These go to D1 (next 24 hours) if urgent
- Marked as "Panel Consensus" in output
- Example: "All 4 reviewers flag missing Economic Buyer - secure CFO intro immediately"

**Medium-confidence actions (2-3 reviewers agree):**
- These go to D7 (next 7 days) or D1 if critical
- Marked with attribution: "Per Competitive Strategist + Deal Mechanics..."
- Example: "Map paper process (CS + DM) - legal timeline unknown"

**Low-confidence actions (1 reviewer, others neutral or disagree):**
- Include in "Additional Considerations" section (not D1/D7)
- Note disagreement: "QA recommends disqualification; EAC + CS recommend 7-day test"
- Let user decide

### Phase 5: Prioritize Actions

**D1 Actions (Next 24 Hours) - Limit to 3-5:**

**Priority order:**
1. **Blockers to stage advancement** (consensus from 3+ reviewers)
2. **Economic Buyer engagement** (if missing or weak)
3. **Disqualification-level risks** (if time-sensitive)
4. **Competitive displacement threats** (if imminent)
5. **Timeline risks** (if close date within 14 days)

**D7 Actions (Next 7 Days) - Limit to 5-7:**

**Priority order:**
1. **Artifact creation** (required per methodology stage inventory)
2. **Stakeholder expansion** (multi-threading)
3. **Competitive positioning** (battlecards, references, FUD mitigation)
4. **Legal/procurement process mapping**
5. **Qualification gap filling** (pain quantification, budget validation)

**Backlog (Not in report, but noted):**
- Optimization opportunities
- Nice-to-haves
- Long-term relationship building

### Phase 6: Generate Unified Coaching Report

**Structure (400-600 words total):**

```markdown
# Deal Review Panel Report - {Company Name}

**Generated:** {DATE} | **Stage:** {STAGE} | **Methodology:** {METHODOLOGY} | **Panel Verdict:** {STRONG | QUALIFIED | AT RISK | DISQUALIFY}

## Panel Snapshot (6 bullets)
- Stage {X} - {one_line_health_summary}
- ACV: ${amount} | Close Date: {date} | Probability: {X}%
- Last Activity: {date} ({days_ago} days ago)
- Champion: {Name/Title} | Economic Buyer: {Name/Title or "NOT IDENTIFIED"}
- Competition: {Primary competitor or "None known"}
- Panel Verdict: {STRONG | QUALIFIED | AT RISK | DISQUALIFY}

## Panel Consensus (Top 3 Risks)
1. 🔴 **{Risk Name}** - {brief impact} → {mitigation}
   - **Flagged by:** Qualification Analyst, Competitive Strategist, Executive Alignment Coach
2. 🟡 **{Risk Name}** - {brief impact} → {mitigation}
   - **Flagged by:** Deal Mechanics, Executive Alignment Coach
3. 🟠 **{Risk Name}** - {brief impact} → {mitigation}
   - **Flagged by:** Competitive Strategist

## Panel Debate Highlights
- **Disqualification vs. Patience:** QA recommends disqualify (no Economic Buyer after 45 days). EAC counters: champion securing CFO intro next week. **Resolution:** 7-day deadline - disqualify if no meeting scheduled.
- **Aggressive vs. Conservative Positioning:** CS wants immediate competitive positioning. DM cautions against rushing before legal approval. **Resolution:** Prepare competitive briefing now (per CS), deliver after legal greenlight (per DM).

## Recommended Actions

### D1 (Next 24 Hours) - Panel Priority
- [ ] **EOD Today** - Request CFO intro from champion (Dir IT, Jane Smith) for 15-min business review (Owner: AE)
  - Why: No Economic Buyer identified (Stage 3 blocker) - **Panel Consensus** (4/4 reviewers)
- [ ] **Tomorrow AM** - Map paper process with Procurement contact (Owner: AE)
  - Why: Legal timeline unknown, close date in 30 days - **Per Deal Mechanics + Competitive Strategist**

### D7 (This Week) - Panel Priority
- [ ] **By Wed** - Create 3-slide executive briefing for CFO meeting (problem/solution/proof) (Owner: AE + SE)
  - Why: Economic Buyer requires business case, not product demo - **Per Executive Alignment Coach**
- [ ] **By Thu** - Deploy competitive battlecard vs. Competitor X (Owner: AE)
  - Why: Champion mentioned competitor yesterday - **Per Competitive Strategist**
- [ ] **By Fri** - Test champion strength: Request budget line item details (Owner: AE)
  - Why: Champion hasn't driven internal action yet - **Per Qualification Analyst**

## Unresolved Panel Tensions
- **Disqualification threshold:** QA believes deal should be disqualified now. EAC + CS recommend 7-day test. Monitor CFO intro progress closely.

## Missing Information (Panel Gaps)
- [ ] Economic Buyer's top 3 priorities (ask champion or request direct CFO call)
- [ ] Paper process timeline (legal, procurement, security review durations)
- [ ] Competitor X engagement level (ask champion: "How far along is Competitor X?")

## Suggested Skills to Run Next
1. **prep-discovery** - Prepare CFO discovery agenda (Economic Buyer call upcoming)
   - Parameters: `deal_path`, `call_type: discovery`, `focus_areas: [budget_authority, decision_process, business_priorities]`
2. **sales_communications** - Draft CFO outreach email (if champion doesn't secure intro)
   - Parameters: `deal_path`, `recipient: cfo`, `message_type: executive_intro`

## Panel Composition
- **Qualification Analyst** - Methodology compliance, disqualification specialist
- **Competitive Strategist** - Win/loss analyst, positioning expert
- **Executive Alignment Coach** - Stakeholder dynamics, Economic Buyer engagement
- **Deal Mechanics Reviewer** - Timeline, legal, procurement specialist
```

---

## Synthesis Quality Checks

Before finalizing report:

✅ **Conflict resolution:** All major conflicts addressed (documented or synthesized)
✅ **Attribution clarity:** Panel Consensus (3-4 reviewers) vs. specific reviewer attribution
✅ **Action specificity:** What/Who/Why for each D1/D7 action
✅ **Word count:** 400-600 words total (strict limit)
✅ **No vague advice:** "Improve relationships" → "Schedule 1:1 with CFO by Friday"
✅ **Evidence cited:** All claims grounded in deal.md or reviewer analysis
✅ **Unresolved tensions surfaced:** Don't hide disagreements, let user decide
✅ **Frontmatter complete:** generated_by, generated_on, deal_id, sources

---

## Common Synthesis Patterns

### Pattern 1: Unanimous Concern (4/4 reviewers flag same risk)
**Synthesis:** Escalate to D1 with "Panel Consensus" label. High confidence → immediate action.

**Example:**
- All 4 reviewers flag: "No Economic Buyer identified"
- D1 Action: "Secure CFO intro by EOD tomorrow (Panel Consensus - 4/4 reviewers)"

### Pattern 2: Split Decision (2 vs. 2)
**Synthesis:** Sequence both recommendations or set decision deadline.

**Example:**
- QA + DM say: "Disqualify now"
- EAC + CS say: "Give it 7 more days"
- Resolution: "7-day test - disqualify if no Economic Buyer engagement by next Friday"

### Pattern 3: Specialist Insight (1 reviewer, domain-specific)
**Synthesis:** Defer to domain expert unless contradicts consensus.

**Example:**
- Only Deal Mechanics flags: "Security review will take 45 days minimum"
- Even if others don't mention it, include in timeline risk (DM is expert)

### Pattern 4: Optimist vs. Pessimist (sentiment divergence)
**Synthesis:** Surface both perspectives, lean pessimistic for risk assessment.

**Example:**
- EAC says: "Champion is strong, deal is healthy"
- QA says: "Champion can't articulate pain, weak qualification"
- Resolution: "Test champion strength by requesting specific action (e.g., share budget data)"

---

## Output Filename Convention

`panel_review_{call_type}_{ISO_DATE}.md`

Examples:
- `panel_review_stage_gate_2025-11-15.md`
- `panel_review_deal_stuck_2025-11-15.md`
- `panel_review_weekly_review_2025-11-15.md`

---

## Progressive Disclosure Note

This file is loaded only when deal-review-panel skill activates during synthesis phase. Not loaded for other skills.
