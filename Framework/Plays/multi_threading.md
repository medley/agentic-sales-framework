---
name: "Multi-Threading Play"
type: "sales_play"
owner: "{YOUR_NAME}"
version: "1.0.0"
license: "MIT - See LICENSE.md"
---

# Multi-Threading Play: Stakeholder Expansion & De-Risking

<triggers>
- single_contact (only talking to one person)
- champion_departure_risk (champion might leave or lose influence)
- decision_authority_unclear (don't know who actually approves)
- deal_stalled (single thread = bottleneck)
- committee_decision (multiple stakeholders need to buy in)
- exec_misalignment (champion's boss not engaged)
</triggers>

<principles>
- **3-5 stakeholder minimum**: Enterprise deals need multiple relationships (champion, exec sponsor, technical buyer, end user, procurement)
- **Map before engaging**: Understand org chart and decision dynamics before outreach
- **Champion-enabled intros**: Get warm introductions from champion, don't go around them
- **Coordinate messaging**: Ensure all stakeholders hear consistent story (tailor details, not core message)
- **Assign owners**: Each stakeholder gets primary AE/SE owner (not everyone talks to everyone)
- **Test multi-threading strength**: Strong deal = easy to get stakeholder intros, weak deal = resistance
</principles>

<steps>
1. **Map stakeholder landscape**:
   - **Decision roles**:
     - Economic Buyer (budget authority, final approver)
     - Champion (internal seller, day-to-day driver)
     - Technical Buyer (evaluates solution fit, IT approval)
     - End Users (will use product daily)
     - Legal/Procurement (contract negotiation)
   - **Org chart**: Who reports to whom? Who has influence?
   - **Decision process**: Consensus? Single approver? Committee vote?

2. **Identify gaps**:
   - Who are you NOT talking to that matters?
   - Red flags: No Economic Buyer, no Technical Buyer, no End User validation
   - Prioritize: Economic Buyer > Champion > Technical Buyer > End Users > Procurement

3. **Get champion-enabled intros**:
   - Ask champion: "Who else should I talk to to make this successful?"
   - Offer help: "I can draft intro email for you" or "Can we do joint meeting?"
   - If champion resists = yellow flag (either weak champion or they're hiding something)

4. **Conduct stakeholder meetings**:
   - **Tailor pitch**: Economic Buyer = ROI, Technical Buyer = architecture, End User = usability
   - **Coordinate timing**: Sequence meetings logically (champion → technical → exec, not random)
   - **Share learnings**: After each meeting, update champion on what you learned

5. **Maintain relationships**:
   - **Regular touchpoints**: Don't ghost stakeholders after first meeting
   - **Value-add**: Send relevant content (benchmark, case study, insight) between meetings
   - **Document interactions**: Track last touch, next steps, concerns per stakeholder

6. **Monitor health**:
   - **Green**: 4+ active stakeholders, exec sponsor engaged, regular multi-party meetings
   - **Yellow**: 2-3 stakeholders, no exec, or champion blocking access
   - **Red**: Single-threaded, champion gatekeeping, or conflicting stakeholder messages
</steps>

<examples>
<example id="enterprise_saas_multithread">
**Context**: $1.2M SaaS deal, initial contact = IT Manager, risk of single-threading

**Situation**: IT Manager is friendly but deal has been in discovery for 4 weeks (slow progress)

**Action**: Asked IT Manager "Who else should I involve to move this forward?"

**Stakeholder map** (identified via conversation):
- **IT Manager** (initial contact) → reports to CIO
- **CIO** (Economic Buyer, budget authority)
- **VP Operations** (End User department, will use product)
- **Dir IT** (Technical Buyer, security/architecture approval)
- **Procurement** (contract negotiation)

**Multi-threading plan**:
- **Week 1**: Ask IT Manager to introduce CIO and Dir IT
- **Week 2**: Joint meeting (IT Manager + Dir IT + AE + SE) for technical deep-dive
- **Week 3**: IT Manager introduces VP Operations for business case validation
- **Week 4**: IT Manager introduces CIO for executive alignment

**Execution**:
- **Dir IT meeting**: Validated technical fit, identified security requirements (SE handled)
- **VP Ops meeting**: Confirmed business impact (ROI = $600K annual savings)
- **CIO meeting**: Aligned on budget ($1.2M approved), timeline (Q3 close), success criteria

**Outcome**: Deal accelerated from 4-week stall to contract signed in 6 weeks

**Key moves**:
- Mapped stakeholders early (didn't stay single-threaded with IT Manager)
- Champion-enabled all intros (IT Manager facilitated, AE didn't bypass)
- Sequenced meetings (technical → business → exec, logical flow)
- Each stakeholder validated different aspect (technical fit, ROI, budget)
</example>

<example id="champion_departure_save">
**Context**: $800K deal, single-threaded with Dir Product, then Dir Product announces departure

**Situation**: Champion leaving in 3 weeks, deal at risk of dying

**Emergency multi-threading**:
- **Week 1**: Asked departing champion "Who should take over? Can you intro me before you leave?"
- **Champion identified**:
  - VP Product (exec sponsor, budget authority)
  - Product Manager (new champion, day-to-day owner)
  - Sr Engineer (technical buyer, implementation owner)

**Transition plan**:
- **Week 1**: Joint meeting (departing champion + VP Product + PM + AE) for full context transfer
- **Week 2**: 1:1 with VP Product (exec alignment), 1:1 with PM (new champion relationship)
- **Week 3**: 1:1 with Sr Engineer (technical validation), departing champion's last week

**Post-departure**:
- VP Product = exec sponsor (approved budget)
- PM = new champion (drove timeline and internal approvals)
- Sr Engineer = technical validation (architecture sign-off)

**Outcome**: Deal closed 4 weeks after original champion left (multi-threading saved the deal)

**Key moves**:
- Recognized single-threading risk early (departing champion = urgency to multi-thread)
- Got departing champion to facilitate intros (credibility transfer)
- Built relationships with 3 new stakeholders before departure (not scrambling after)
- Each stakeholder had clear role (exec, champion, technical)
</example>

<example id="committee_multithread">
**Context**: $1.5M deal, 8-person buying committee, consensus decision required

**Situation**: Committee meetings are chaotic (8 people, conflicting priorities, slow)

**Strategy**: Multi-thread with 1:1 meetings, then reconvene committee

**Stakeholder map**:
1. CFO (Economic Buyer, final approver)
2. CIO (IT budget owner)
3. VP Operations (primary end user)
4. Dir IT (technical evaluation)
5. Dir Finance (ROI validation)
6. Legal (contract review)
7. Procurement (vendor management)
8. CISO (security approval)

**Multi-threading approach**:
- **Phase 1**: 1:1 meetings with all 8 stakeholders (over 2 weeks)
  - CFO: ROI and payback period (15 min)
  - CIO: Strategic alignment (20 min)
  - VP Ops: Business case and pain points (30 min)
  - Dir IT: Technical architecture (45 min with SE)
  - Dir Finance: Financial modeling (20 min)
  - Legal: Standard terms review (15 min)
  - Procurement: Vendor process (10 min)
  - CISO: Security questionnaire (30 min with SE)

- **Phase 2**: Synthesized feedback, addressed concerns individually

- **Phase 3**: Reconvened committee with pre-aligned stakeholders (30 min)
  - Each stakeholder confirmed their domain was addressed
  - Committee voted unanimous approval (no surprises)

**Outcome**: Deal closed in 5 weeks (vs typical 12 weeks for committee deals)

**Key moves**:
- Avoided large committee meetings until stakeholders were pre-aligned
- Tailored pitch per stakeholder (ROI for CFO, security for CISO, etc.)
- 1:1 meetings uncovered objections that wouldn't surface in group settings
- Committee meeting was formality (consensus already built offline)
</example>

<example id="champion_gatekeeping">
**Context**: $600K deal, champion (IT Director) is blocking access to CIO

**Situation**: IT Director says "I'll handle the CIO, you don't need to talk to him"

**Red flag analysis**:
- Champion gatekeeping = either weak champion OR hiding something
- No exec access at Stage 3 (Propose) = deal risk

**Action**:
- **Tested champion**: "I'd love to get 10 min with CIO to align on strategic priorities. Can you intro me?"
- **Champion pushback**: "That's not necessary, I'll present to him myself"
- **Follow-up**: "I appreciate that. What if we present together? I can support you."
- **Champion relented**: Agreed to joint meeting (reluctantly)

**Joint meeting** (IT Director + CIO + AE):
- **Discovery**: CIO wasn't fully briefed (IT Director had undersold business case)
- **CIO concern**: "Is this the best use of $600K right now?" (budget prioritization question)
- **AE response**: Shared ROI analysis showing $1.2M savings over 2 years (IT Director hadn't emphasized this)
- **CIO reaction**: "Why didn't I see this before? This is a no-brainer."

**Outcome**: Deal approved by CIO, but exposed that IT Director was weak champion (not effectively selling internally)

**Key moves**:
- Recognized gatekeeping as red flag (not healthy champion behavior)
- Persisted politely (didn't bypass, but insisted on joint meeting)
- Joint meeting revealed weak internal selling (IT Director hadn't built strong case)
- Direct CIO engagement saved deal (would have stalled otherwise)

**Lesson**: Champion gatekeeping = multi-thread immediately
</example>

<example id="end_user_validation">
**Context**: $900K deal, selling to IT, but end users (sales team) will use product daily

**Situation**: IT Director is champion, but sales team hasn't been engaged (risk: adoption failure)

**Action**: Asked IT Director "Can I talk to a few sales reps to understand their workflow?"

**Multi-threading to end users**:
- **Week 1**: IT Director introduced 3 sales reps (frontline users)
- **Week 2**: Conducted 20-min interviews with each rep (workflow shadowing)
- **Findings**:
  - Current tool is clunky (reps avoid using it)
  - Mobile access is critical (reps work remotely)
  - Integration with CRM is must-have (reps hate double-entry)

**Feedback loop**:
- **To IT Director**: "Sales reps need mobile + CRM integration. Can we prioritize that?"
- **To Sales Reps**: "I heard you. Mobile is part of our standard implementation."

**Pilot approach**:
- Proposed 10-rep pilot (validate adoption before full rollout)
- Sales reps became champions (they felt heard, gave testimonials to IT Director)

**Outcome**: Deal closed at $900K with pilot structure, adoption was 95% (sales reps were pre-sold)

**Key moves**:
- Engaged end users early (not just IT buyer)
- End user feedback shaped implementation plan (mobile, CRM integration)
- End users became champions (validated solution to IT Director)
- Pilot de-risked adoption concerns (IT Director's biggest fear)
</example>
</examples>

<pitfalls>
- **Bypassing champion**: Going around champion to access stakeholders = damaged trust, lost champion
- **Ignoring org politics**: Not understanding who has influence = wasting time on wrong stakeholders
- **Inconsistent messaging**: Telling CFO one thing, CIO another = confusion, distrust
- **Shotgun approach**: Meeting every stakeholder without strategy = diluted message, wasted time
- **No follow-up**: Meeting stakeholder once then ghosting = weak relationship, no progress
- **Over-reliance on champion**: Expecting champion to do all multi-threading = single point of failure
</pitfalls>
