---
name: "Committee Selling Play"
type: "sales_play"
owner: "{YOUR_NAME}"
version: "1.0.0"
license: "MIT - See LICENSE.md"
---

# Committee Selling Play: Group Consensus Building

<triggers>
- committee_decision (buying decision requires committee approval)
- multiple_stakeholders (5+ people involved in decision)
- consensus_required (no single decision-maker, group vote needed)
- cross_functional_buy_in (IT, Ops, Finance, Legal all must approve)
- risk_averse_culture (decisions made by committee to distribute accountability)
- large_investment (>$1M typically requires committee approval)
</triggers>

<principles>
- **Identify decision-maker vs influencers**: Someone has final say (CFO, CEO, CIO) even in committees
- **Individual prep calls**: Meet each member 1:1 before committee meeting (pre-sell, uncover objections)
- **Manage group dynamics**: Loud voices ≠ decision-makers (map influence, not just titles)
- **1:1 follow-ups**: After committee meeting, address individual concerns privately
- **Champion coaches you**: Champion knows committee personalities, politics (use their insights)
- **Consensus ≠ unanimity**: You need majority + decision-maker, not 100% agreement
</principles>

<steps>
1. **Map the committee**:
   - **Members**: Names, titles, departments
   - **Roles**: Decision-maker (final approver), influencers (strong opinions), voters (vote but low influence), observers (no vote)
   - **Concerns**: What does each person care about? (CFO = ROI, CIO = integration, CISO = security)
   - **Relationships**: Who has influence over whom? Who respects whose opinion?
   - **Politics**: Any conflicts? Competing agendas? Power dynamics?

2. **Pre-sell individually** (1:1 meetings before committee):
   - **Goal**: Understand each member's concerns, build support before group meeting
   - **Schedule**: 15-30 min calls with each committee member (2-3 weeks before committee vote)
   - **Tailor pitch**: CFO gets ROI, CIO gets architecture, end users get usability, CISO gets security
   - **Uncover objections**: "What concerns do you have?" (address privately, not in front of committee)
   - **Ask for support**: "If your concerns are addressed, would you support this?" (pre-commit)

3. **Prepare champion**:
   - **Rehearse**: Walk champion through committee presentation, anticipate questions
   - **Assign roles**: Who presents what? (Champion presents business case, AE supports with data, SE handles technical)
   - **Objection handling**: Prep responses to likely objections (champion knows who will object)
   - **Vote counting**: "Who's already on board? Who's on the fence? Who's opposed?" (focus energy on fence-sitters)

4. **Conduct committee meeting**:
   - **Structure** (30-45 min recommended):
     - Min 0-5: Champion introduces (sets context, why this matters)
     - Min 5-15: AE presents business case (ROI, references, timeline)
     - Min 15-25: Q&A (SE handles technical, AE handles business, champion reinforces)
     - Min 25-30: Next steps (timeline, decision process, vote if applicable)
   - **Group dynamics**:
     - Address decision-maker first (if CFO asks question, prioritize their answer)
     - Don't let loud voices dominate (politely redirect: "Good point, let's also hear from [quiet member]")
     - If major objection surfaces, offer to follow up offline (don't derail meeting)

5. **Post-meeting follow-up**:
   - **1:1 calls**: Reach out to fence-sitters or objectors (address concerns privately)
   - **Champion sync**: "How did that go? Who's still on the fence? What concerns came up?"
   - **Provide materials**: Send ROI summary, security docs, references (whatever committee requested)

6. **Drive to decision**:
   - **Timeline**: "Committee votes next week" (set deadline)
   - **Champion counts votes**: "Who's yes, no, undecided?" (focus on undecided)
   - **Address blockers**: If 1-2 people blocking consensus, address their concerns directly
   - **Escalate if needed**: If committee gridlocked, escalate to decision-maker (CFO, CEO)
</steps>

<examples>
<example id="cross_functional_committee">
**Context**: $1.5M deal, 7-person buying committee (CFO, CIO, VP Ops, Dir IT, Dir Finance, CISO, Procurement)

**Situation**: Consensus decision required, committee meets monthly (slow process)

**Committee mapping** (with champion, Dir IT):
- **CFO** (decision-maker): Final approver, cares about ROI and payback
- **CIO** (influencer): Strong influence over CFO, cares about integration and IT roadmap alignment
- **VP Ops** (influencer): End user, cares about usability and adoption
- **Dir IT** (champion): Day-to-day owner, cares about implementation success
- **Dir Finance** (voter): Supports CFO, cares about budget and payment terms
- **CISO** (voter): Cares about security and compliance
- **Procurement** (observer): Process owner, no vote but manages vendor onboarding

**Pre-selling strategy** (1:1 meetings over 2 weeks):

1. **CFO** (15 min):
   - Presented ROI: 3.2:1, 9-month payback
   - Addressed concern: "What if implementation takes longer?" (showed reference customer timeline = 5 months avg)
   - **CFO reaction**: "If CIO is confident in integration, I'll approve"

2. **CIO** (30 min with SE):
   - Presented technical architecture, integration plan
   - Addressed concern: "Does this integrate with Salesforce and SAP?" (SE showed API connectors, existing integrations)
   - **CIO reaction**: "Integration looks solid. I'll recommend approval."

3. **VP Ops** (20 min):
   - Presented usability (showed product demo, user testimonials)
   - Addressed concern: "Will sales team actually use this?" (showed 90% adoption rate at reference customer)
   - **VP Ops reaction**: "If it's this easy to use, I'm supportive"

4. **Dir Finance** (15 min):
   - Presented payment terms (annual prepay with 5% discount)
   - Addressed concern: "Can we do quarterly payments?" (offered quarterly at list price vs discounted annual)
   - **Dir Finance**: "I'll recommend annual prepay to CFO for the discount"

5. **CISO** (20 min with SE):
   - Provided SOC 2 Type II, penetration test results, security questionnaire
   - Addressed concern: "Data residency?" (confirmed US-only data centers)
   - **CISO reaction**: "Security posture is strong, approved"

6. **Procurement** (10 min):
   - Provided vendor questionnaire, standard contract, insurance docs
   - Addressed concern: "Standard vendor onboarding process?" (followed their process, no exceptions)
   - **Procurement**: "No issues, we can onboard once approved"

**Vote count after 1:1s**:
- **Yes**: CIO, VP Ops, Dir Finance, CISO, Procurement (5 of 7)
- **Undecided**: CFO (waiting for CIO recommendation)
- **Opposed**: None

**Committee meeting** (30 min):
- **Min 0-5**: Dir IT (champion) presented business case, introduced AE
- **Min 5-15**: AE presented ROI, references, timeline
- **Min 15-25**: Q&A (mostly confirmations, no major objections because of pre-selling)
- **Min 25-30**: CFO asked CIO: "Are you confident in this?" CIO: "Yes, I recommend approval"
- **CFO**: "Let's move forward. Dir IT, work with Procurement on contracting."

**Outcome**: Committee approved unanimously (pre-selling eliminated surprises)

**Key moves**:
- 1:1 pre-selling built support before committee meeting (no surprises)
- Tailored pitch per stakeholder (ROI for CFO, security for CISO, usability for VP Ops)
- Champion (Dir IT) counted votes beforehand (knew CFO was waiting for CIO endorsement)
- Committee meeting was confirmation, not negotiation (consensus pre-built)
</example>

<example id="committee_objection_mgmt">
**Context**: $2M deal, 8-person committee, one vocal objector (VP Engineering)

**Situation**: Committee meeting, VP Engineering raises concern: "This won't scale to 10K users"

**Group dynamic challenge**: VP Eng is loud, influential, could derail deal

**Real-time response**:
- **AE**: "Great question. Our largest customer has 25K users. [SE], can you walk through the architecture?"
- **SE**: "We've architected for 50K users. Here's how we handle scale..." (2-min technical overview)
- **VP Eng**: "I'm still concerned about database sharding" (technical deep-dive objection)

**Redirection**:
- **AE**: "This is important. Can we schedule 30 min with you and [SE] this week to dive deep on architecture? I don't want to take the committee's time on technical details."
- **VP Eng**: "Sure, let's do that"
- **CIO** (decision-maker): "Good idea. VP Eng, let's let them continue and you can follow up offline."

**Committee meeting continued** (objection defused, not resolved in front of group)

**Post-meeting 1:1 with VP Eng** (30 min, AE + SE):
- **SE**: Showed architecture diagrams, database sharding approach, load testing results
- **VP Eng**: "Okay, this looks solid. I was worried you hadn't thought about scale."
- **SE**: "We've scaled this for Fortune 500s. Happy to share reference architecture."
- **VP Eng**: "I'm satisfied. I'll support this in next committee meeting."

**Outcome**: VP Eng flipped from objector to supporter (offline deep-dive addressed concerns)

**Key moves**:
- Didn't try to resolve technical objection in committee meeting (would have derailed)
- Offered offline deep-dive (showed respect for VP Eng's concerns)
- CIO backed the redirection (decision-maker supported deferring technical debate)
- SE resolved concerns in 1:1 setting (VP Eng felt heard, not dismissed)
</example>

<example id="silent_stakeholder">
**Context**: $1.2M deal, 6-person committee, one member (Dir Legal) silent in all meetings

**Situation**: Committee meetings, Dir Legal never speaks, hard to read

**Concern**: Silent stakeholders can sink deals (you don't know their objections)

**Action**: 1:1 outreach to Dir Legal

**AE email**:
```
[Dir Legal], I noticed you've been quiet in committee meetings. I wanted to check if you have any concerns about the contract or legal terms we should address before the vote.
```

**Dir Legal response**:
```
Thanks for reaching out. I have concerns about the indemnity clause and data ownership terms. Can we discuss?
```

**1:1 call** (20 min):
- **Dir Legal concerns**:
  1. Indemnity clause too broad (unlimited liability)
  2. Data ownership unclear (who owns customer data?)
  3. Termination terms unfavorable (60-day notice)

**AE responses**:
  1. Indemnity: "We can cap at contract value ($1.2M), is that acceptable?"
  2. Data ownership: "You own all customer data, we own product IP. Does that work?"
  3. Termination: "We can do 30-day notice. Sound reasonable?"

**Dir Legal**: "Yes, those changes work. I'll support the deal if we get those in the contract."

**Outcome**: Dir Legal became supporter (would have been silent blocker without 1:1)

**Key moves**:
- Proactively reached out to silent stakeholder (didn't assume silence = approval)
- Uncovered objections privately (Dir Legal wouldn't raise legal concerns in front of business stakeholders)
- Addressed concerns before committee vote (converted potential blocker to supporter)
</example>

<example id="committee_gridlock">
**Context**: $1.8M deal, 9-person committee, 3 months of meetings, no decision

**Situation**: Committee keeps deferring decision ("need more analysis", "let's revisit next month")

**Diagnosis**: No clear decision-maker, committee avoiding accountability

**Action**: Escalated to CEO (actual decision-maker)

**Champion** (CFO): "This is frustrating. Committee won't decide."

**AE**: "Who can break the gridlock? CEO?"

**CFO**: "Yes, but I don't want to bypass the committee"

**AE**: "What if we position this as 'CEO strategic review' not bypassing committee?"

**CEO meeting** (15 min, CFO + AE):
- **AE**: "Your committee has been evaluating for 3 months. They're aligned on value but hesitant to make final call. Does this still fit your strategic priorities?"
- **CEO**: "Yes, this is critical. I'll tell the committee to approve it."

**CEO to committee** (via email):
```
Team, I've reviewed the [Vendor] proposal. This aligns with our strategic priorities. Please proceed with contracting. [CFO] will own implementation.
```

**Outcome**: Committee approved immediately after CEO directive (decision-maker resolved gridlock)

**Key moves**:
- Recognized committee gridlock (3 months = not making progress)
- Identified actual decision-maker (CEO, not committee)
- Escalated with champion's support (CFO brought AE to CEO)
- CEO directive broke gridlock (committee needed top-down decision)
</example>

<example id="consensus_without_unanimity">
**Context**: $900K deal, 5-person committee, 4 yes / 1 no (Dir IT opposed)

**Situation**: Dir IT says "I don't think this integrates well with our stack"

**Committee dynamic**: Other 4 members supportive (CFO, CIO, VP Ops, Dir Finance)

**CIO response** (decision-maker):
- "Dir IT, I hear your concern. But we've seen the integration demos and reference customers. I'm comfortable moving forward. Let's do a pilot to validate."

**Pilot structure**:
- 45 days, limited scope (one department)
- Success criteria: Integration with 3 core systems, <5% error rate
- Dir IT owns pilot evaluation

**Pilot outcome**:
- Integration successful (4 systems, 1% error rate)
- Dir IT: "I was wrong. This integrates better than I expected. I support full rollout."

**Outcome**: Consensus achieved (pilot converted 1 no to yes)

**Key moves**:
- CIO (decision-maker) moved forward despite 1 no (didn't need unanimity)
- Pilot gave Dir IT path to yes (de-risked his concern)
- Dir IT owned pilot evaluation (gave him control, not overridden)
</example>
</examples>

<pitfalls>
- **Skipping 1:1s**: Going straight to committee meeting without pre-selling = objections surprise you
- **Treating all members equally**: Focusing on low-influence voters vs decision-maker = wasted energy
- **Resolving objections in group**: Debating technical details in committee = derails meeting
- **Ignoring silent stakeholders**: Assuming silence = approval (silent blockers sink deals)
- **Waiting for unanimity**: Requiring 100% consensus vs majority + decision-maker = eternal gridlock
- **No timeline**: Letting committee "evaluate indefinitely" without forcing decision = deal stalls
</pitfalls>
