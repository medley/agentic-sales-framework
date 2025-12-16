---
name: "Budget Creation Play"
type: "sales_play"
owner: "{YOUR_NAME}"
version: "1.0.0"
license: "MIT - See LICENSE.md"
---

# Budget Creation Play: No-Budget Scenario Tactics

<triggers>
- no_budget (champion says "We don't have budget for this")
- budget_not_approved (no line item in current fiscal year)
- new_initiative (unplanned project, not budgeted)
- unplanned_purchase (emergency or opportunistic buy)
- mid_year_request (outside normal budget cycle)
- competing_priorities (budget allocated to other projects)
</triggers>

<principles>
- **Build business case**: Quantify cost of inaction (problem costs > solution cost)
- **Identify budget source**: CFO budget, departmental budget, discretionary fund, cost savings reallocation
- **Engage finance early**: Don't wait until end of cycle (finance can find budget if case is strong)
- **Start small**: Pilot or Phase 1 (easier to fund $50K than $500K from discretionary)
- **Link to strategic initiative**: Tie to CEO/board priority (gets funding priority)
- **Create urgency**: Time-limited discount, competitive threat, regulatory deadline
</principles>

<steps>
1. **Validate "no budget" claim**:
   - **True no budget**: Budget allocated, fiscal year locked, zero discretionary funds
   - **Perceived no budget**: Budget exists but allocated elsewhere (can be reallocated)
   - **Not a priority**: Budget available but solution not valued enough (need stronger business case)
   - **Test**: "If ROI is strong, can we find budget?" (if yes = perceived no budget, if no = true no budget)

2. **Quantify cost of inaction**:
   - **Current state cost**: What is problem costing them today? (labor, errors, lost revenue, risk)
   - **Opportunity cost**: What revenue/projects are delayed by not solving this?
   - **Comparison**: Is cost of problem > cost of solution? (if yes, budget becomes reallocation not new spend)
   - **Example**: "You're spending $400K/year on manual process. We're $200K. This is a cost reduction, not new spend."

3. **Identify budget sources**:
   - **CFO discretionary fund**: Most CFOs hold 5-10% budget reserve for unplanned initiatives
   - **Departmental budget**: Can champion reallocate from another project? (deprioritize lower-ROI project)
   - **Cost savings**: Fund from savings generated (e.g., eliminate $100K vendor, use savings to fund new solution)
   - **Exec sponsor budget**: VPs/C-level often have discretionary budget (ask exec sponsor to fund)
   - **Next fiscal year**: If true no budget, get commitment for next budget cycle (convert to pipeline)

4. **Build urgency**:
   - **Regulatory deadline**: "GDPR compliance required by Q2" (creates hard deadline)
   - **Competitive threat**: "Competitor just launched this capability" (creates strategic urgency)
   - **Cost escalation**: "Price increases 15% next quarter" (creates financial urgency)
   - **Limited-time offer**: "We can offer 20% discount if approved by month-end" (creates timeline urgency)

5. **Propose funding structures**:
   - **Option 1 - Pilot**: $25K-$50K pilot funded from discretionary, full contract from next fiscal year
   - **Option 2 - Phased**: Small Phase 1 this year ($100K), larger Phase 2 next year ($400K)
   - **Option 3 - Self-funding**: ROI positive in 6-9 months (use savings to fund expansion)
   - **Option 4 - Vendor financing**: Payment terms (quarterly vs annual, net 60 vs net 30)

6. **Engage finance/CFO**:
   - **Champion introduces AE to finance**: "I think this has strong ROI, can you review?"
   - **Present business case**: Show cost of problem vs cost of solution (CFO decides if budget can be found)
   - **CFO options**: Approve from discretionary, reallocate from other project, defer to next fiscal year
</steps>

<examples>
<example id="discretionary_fund">
**Context**: $400K deal, champion (VP Ops) says "I don't have budget, everything is allocated"

**Situation**: Mid-year request (outside budget cycle), no line item for this solution

**Action**: Quantified cost of inaction

**Cost of current state** (with champion):
- **Labor**: 5 FTE spending 60% time on manual process = $300K/year
- **Errors**: 8% error rate requiring rework = $80K/year
- **Vendor costs**: 2 legacy tools = $40K/year
- **Total**: $420K/year

**Solution cost**:
- **Year 1**: $150K implementation + $100K subscription = $250K
- **Year 2+**: $100K/year subscription

**ROI pitch to champion**:
- "You're spending $420K/year on current state. We're $250K Year 1, then $100K/year."
- "This isn't new spend, it's cost reallocation. Net savings = $170K Year 1, $320K/year after."

**Champion reaction**: "I never thought of it as cost reallocation. Let me talk to CFO."

**Champion to CFO**:
- Presented cost of inaction: $420K/year
- Proposed solution: $250K Year 1 (net $170K savings)
- Asked: "Can we fund this from discretionary budget?"

**CFO response**: "If it saves $170K this year, approved. Where's the contract?"

**Outcome**: CFO funded from discretionary reserve, deal closed at $400K (rounded up for buffer)

**Key moves**:
- Reframed as cost reallocation, not new spend (changed CFO's mental model)
- Quantified current state cost (CFO didn't realize $420K/year problem)
- Champion presented business case (AE supported, champion owned pitch)
- CFO found discretionary budget when ROI was clear
</example>

<example id="pilot_to_full_contract">
**Context**: $800K deal, champion says "Budget cycle starts in 6 months, can't do anything until then"

**Situation**: True no budget (fiscal year locked), but champion wants to move forward

**Action**: Proposed pilot structure

**Pilot proposal**:
- **Pilot cost**: $40K (funded from champion's discretionary budget)
- **Duration**: 45 days
- **Scope**: One department (50 users), limited use case
- **Success criteria**: 80% adoption, 40% time savings, zero critical bugs
- **Full contract**: If pilot succeeds, $760K contract in next fiscal year ($800K - $40K credit)

**Champion reaction**: "I can find $40K. If pilot works, I'll get $800K budgeted for next year."

**Pilot execution**:
- **Week 1-6**: Pilot ran, hit all success criteria
- **Week 7**: Champion presented pilot results to CFO for next year budget request
- **Week 8**: CFO approved $760K line item for next fiscal year

**Outcome**: Pilot closed at $40K (current year), full contract $760K closed in Q1 next fiscal year

**Key moves**:
- Pilot fit within discretionary budget (champion could fund without CFO approval)
- Pilot success de-risked full contract (CFO approved based on proof)
- Pilot timing aligned with budget cycle (results available when budget requests due)
- $40K credit incentivized pilot (customer saw it as "try before you buy")
</example>

<example id="strategic_initiative_tie_in">
**Context**: $1.2M deal, champion says "No budget, and CFO is cutting discretionary spend"

**Situation**: Budget freeze (no discretionary), true constraint

**Action**: Linked to CEO strategic initiative

**Discovery**:
- **Champion**: "CFO is cutting everything except CEO's top 3 priorities"
- **AE**: "What are the top 3 priorities?"
- **Champion**: "Digital transformation, customer experience, and operational excellence"

**Reframe strategy**:
- Our solution = operational excellence (automates manual processes, 50% efficiency gain)
- **Positioning**: Not a separate initiative, but an enabler of CEO priority

**Champion to CFO**:
- "This project directly supports operational excellence (CEO's #2 priority)"
- "ROI is 3:1, and it automates processes blocking our efficiency goals"
- "Can we fund from operational excellence budget?"

**CFO response**: "If it's tied to CEO priority, I can allocate budget. How much?"

**Outcome**: CFO allocated $1.2M from operational excellence initiative budget, deal closed

**Key moves**:
- Identified CEO strategic priorities (budget exists for these initiatives)
- Reframed solution as enabler of strategic priority (not standalone project)
- Champion positioned as aligned to CEO goals (not "nice to have" project)
- CFO found budget when tied to executive mandate
</example>

<example id="cost_savings_reallocation">
**Context**: $500K deal, champion says "We're over budget this year, can't add new vendors"

**Situation**: Budget allocated, but champion is over budget (not under)

**Action**: Identified cost savings to reallocate

**Discovery**:
- **AE**: "What vendors could you eliminate if you had our solution?"
- **Champion**: "We have 3 tools that overlap ($150K/year). Your solution replaces all 3."

**Cost savings analysis**:
- **Current tools**: Tool A ($60K), Tool B ($50K), Tool C ($40K) = $150K/year
- **Proposed solution**: $500K Year 1 (implementation + subscription), $200K/year after
- **Net cost Year 1**: $500K - $150K = $350K (net new spend)
- **Net cost Year 2+**: $200K - $150K = $50K/year (vs $150K current)

**Budget proposal to CFO**:
- "Eliminate Tool A, B, C (save $150K/year)"
- "Net new spend = $350K Year 1, then $50K/year (vs $150K current)"
- "Total savings over 3 years = $100K + better functionality"

**CFO response**: "If it consolidates vendors and saves long-term, approved. Eliminate those 3 tools."

**Outcome**: CFO approved $500K funded by eliminating 3 vendors, deal closed

**Key moves**:
- Identified vendor consolidation opportunity (replace 3 tools with 1)
- Quantified savings ($150K/year vendor elimination)
- Showed net spend (not gross $500K, but net $350K after savings)
- CFO valued vendor consolidation (fewer vendor relationships to manage)
</example>

<example id="payment_terms_flexibility">
**Context**: $600K deal, champion says "Budget exists, but we can only spend $150K per quarter"

**Situation**: Budget constrained by quarterly spend limits (not annual budget)

**Action**: Proposed quarterly payment structure

**Standard pricing**:
- $600K annual prepay (10% discount = $540K)

**Alternative pricing** (to fit quarterly budget):
- $150K/quarter × 4 quarters = $600K (list price, no discount)
- Trade-off: Champion pays $60K more, but fits quarterly budget constraints

**Champion reaction**: "I can fit $150K/quarter. Let's do quarterly payments."

**CFO approval**: Quarterly payments fit budget process, approved

**Outcome**: Deal closed at $600K (quarterly payments), champion got approved within constraints

**Key moves**:
- Flexible payment terms (quarterly vs annual) removed budget barrier
- Trade-off: Vendor got full list price, customer got budget flexibility
- Champion valued fitting quarterly budget > 10% discount
</example>
</examples>

<pitfalls>
- **Taking "no budget" at face value**: Not probing for discretionary funds, reallocation, or next cycle timing
- **Not quantifying cost of inaction**: Failing to show problem cost > solution cost (no urgency to find budget)
- **Skipping CFO/finance**: Expecting champion to find budget alone (finance controls budget, engage them)
- **No urgency**: Allowing "we'll budget next year" without timeline or commitment (deal goes cold)
- **Overselling ROI**: Promising unrealistic savings to create budget (damages credibility, deal falls apart)
- **Ignoring strategic priorities**: Not tying to CEO/board initiatives (discretionary budget prioritizes strategic projects)
</pitfalls>
