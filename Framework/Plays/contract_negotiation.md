---
name: "Contract Negotiation Play"
type: "sales_play"
owner: "{YOUR_NAME}"
version: "1.0.0"
license: "MIT - See LICENSE.md"
---

# Contract Negotiation Play: Legal & Procurement Navigation

<triggers>
- contract_redlines (legal or procurement marking up agreement)
- legal_review (general counsel or legal team engaged)
- procurement_involved (procurement or vendor management team)
- security_review (infosec or compliance reviewing terms)
- msa_required (customer requires master service agreement)
- non_standard_terms (customer requesting custom language)
</triggers>

<principles>
- **Separate business vs legal**: Close business deal BEFORE legal review (don't negotiate price during legal)
- **Engage legal early**: Don't wait until end of cycle (legal can take 2-4 weeks)
- **Standard responses**: Pre-approved redline responses (don't negotiate from scratch each time)
- **Know non-negotiables**: What terms can flex vs hard lines (liability cap, data ownership, IP)
- **Parallel track**: Run legal + procurement in parallel with technical validation (not sequential)
- **Escalate strategically**: Know when to involve your legal team vs sales leader vs exec
</principles>

<steps>
1. **Anticipate legal early**:
   - **Stage 3 (Propose)**: Ask champion "What's your legal/procurement process?"
   - **Stage 4 (Select)**: Introduce legal review to timeline (don't wait for surprise)
   - **MAP milestone**: Include "Legal review" with 2-3 week buffer

2. **Pre-negotiate business terms**:
   - **Before legal review**: Lock in pricing, scope, payment terms, SLAs
   - **Champion/Exec approval**: "Business terms approved, now legal will review contract language"
   - **Avoid**: Sending contract to legal before business deal is closed (they'll negotiate price + terms)

3. **Prepare standard contract package**:
   - **MSA (Master Service Agreement)**: If customer requires MSA, provide template
   - **Order Form / SOW**: Pricing, scope, term length
   - **DPA (Data Processing Agreement)**: If handling customer data (GDPR, privacy)
   - **SLA (Service Level Agreement)**: Uptime, support commitments
   - **Security addendum**: If security team requires specific language

4. **Manage redlines**:
   - **Review customer redlines**: Legal or procurement will mark up contract
   - **Categorize changes**:
     - **Acceptable**: Minor language clarifications, formatting
     - **Standard concessions**: Liability cap = contract value, mutual indemnity, 30-day payment terms
     - **Escalation needed**: Unlimited liability, IP transfer, unfavorable termination, data ownership
   - **Use playbook**: Standard redline responses for common requests (don't reinvent each time)

5. **Negotiate strategically**:
   - **Give/get**: If you concede on one term, ask for something back (e.g., "We'll accept 30-day net if you sign by month-end")
   - **Escalate when stuck**: If legal teams are gridlocked, escalate to business sponsors (CIO, VP Sales)
   - **Document verbally agreed changes**: Redline in Word/DocuSign, don't rely on email threads

6. **Close and execute**:
   - **Final approval**: Both legal teams approve
   - **Signature routing**: DocuSign or wet signature (know customer's process)
   - **Countersignature**: Vendor signs after customer (or simultaneous)
   - **Effective date**: Clarify when contract starts (signature date vs service start date)
</steps>

<examples>
<example id="standard_redlines">
**Context**: $1.2M SaaS deal, customer legal team sends 47 redlines on standard MSA

**Situation**: Legal marks up limitation of liability, indemnity, data ownership, termination

**Redline categories**:
- **Acceptable** (15 redlines): Grammar, formatting, clarifications (accepted all)
- **Standard concessions** (25 redlines):
  - Liability cap: Requested "12 months fees" (was "contract value") → Accepted
  - Payment terms: Requested "Net 30" (was "Net 15") → Accepted
  - Termination: Requested "30-day notice" (was "60-day") → Accepted (in exchange for annual commit)
- **Escalation needed** (7 redlines):
  - Unlimited liability (we proposed cap)
  - Customer ownership of IP (we proposed customer data, not product IP)
  - Right to audit on-demand (we proposed annual audit with 30-day notice)

**Negotiation**:
- **Acceptable + Standard**: Accepted 40 of 47 redlines (showed good faith)
- **Escalation redlines**: Sent to internal legal team for review
- **Internal legal response**:
  - Unlimited liability = non-negotiable (risk too high)
  - IP ownership = non-negotiable (customer owns data, we own product IP)
  - Audit = compromise: Annual audit + on-demand if security incident

**Counter-proposal to customer**:
- Sent redline response with 3 remaining items + rationale
- Offered call between legal teams (not endless email)

**Legal team call** (30 min):
- Unlimited liability: Customer legal agreed to cap at 12 months fees (their CFO required cap anyway)
- IP ownership: Customer legal agreed to data ownership only (standard SaaS model)
- Audit: Customer legal agreed to annual + incident-based (reasonable compromise)

**Outcome**: Contract finalized, signed within 2 weeks of legal review start

**Key moves**:
- Accepted 40 of 47 redlines (built goodwill, picked battles)
- Escalated 7 redlines to internal legal (didn't guess on risk)
- Legal team call resolved impasse (faster than email back-and-forth)
- Compromise on audit (showed flexibility without caving on core terms)
</example>

<example id="procurement_price_negotiation">
**Context**: $800K deal, business deal closed (CIO approved), then procurement gets involved

**Situation**: Procurement says "We need 20% discount to fit our vendor pricing benchmarks"

**Red flag**: Business deal already closed, procurement trying to re-negotiate price

**Response**:
- **AE to procurement**: "Pricing was approved by CIO based on business value. Is there a budget issue?"
- **Procurement**: "No budget issue, but we have benchmarks for vendor discounts"
- **AE**: "I understand. Let me check with CIO to see if scope has changed."

**AE to CIO** (via champion):
- "Procurement is requesting 20% discount. Did the business case change, or is this a procurement process?"
- **CIO response**: "Business case is the same. Tell procurement to proceed with approved pricing."

**CIO to procurement** (via email):
- "This project is approved at $800K based on ROI analysis. Please proceed with contracting."

**Outcome**: Procurement dropped discount request, contract signed at $800K

**Key moves**:
- Did NOT negotiate with procurement (business deal was closed)
- Escalated to business sponsor (CIO) to reinforce pricing approval
- CIO shut down procurement price negotiation (business value > vendor benchmarks)
</example>

<example id="msa_negotiation">
**Context**: $1.5M enterprise deal, customer requires MSA (Master Service Agreement) before any SOW

**Situation**: Customer legal says "We need to finalize MSA first, then we'll do order form"

**Challenge**: MSA negotiations can take 60-90 days (deal delay risk)

**Strategy**: Parallel track MSA + pilot

**Approach**:
- **Proposed**: Start paid pilot ($50K) while MSA is being negotiated
- **Pilot agreement**: Simple 2-page pilot agreement (not full MSA)
- **MSA timeline**: Target 60 days for MSA finalization
- **Full contract**: Once MSA done, execute $1.45M order form ($1.5M total - $50K pilot credit)

**Execution**:
- **Week 1-2**: Negotiated simple pilot agreement (signed in 10 days)
- **Week 3-10**: Pilot running (validated technical fit) + MSA negotiation in parallel
- **Week 11**: MSA finalized (47 days, faster than typical 60-90)
- **Week 12**: Order form executed for $1.45M

**Outcome**: Deal closed in 12 weeks (vs 16-20 weeks if MSA blocked pilot)

**Key moves**:
- Parallel tracked pilot + MSA (didn't wait for MSA to start)
- Simple pilot agreement (2 pages vs 20-page MSA)
- Pilot validated fit while legal negotiated (de-risked deal)
- MSA negotiation faster because business momentum from pilot
</example>

<example id="data_ownership_blocker">
**Context**: $2M deal, customer legal insists on owning all IP (including product code)

**Situation**: Customer redline says "Customer owns all intellectual property created during engagement"

**Risk**: If accepted, customer would own our product code (non-starter)

**Negotiation**:
- **AE to customer legal**: "I think there's a misunderstanding. Can we clarify intent?"
- **Customer legal**: "We need to own all work product"
- **AE**: "Understood. Let's separate customer data vs product IP"

**Counter-proposal**:
- **Customer owns**: Customer data, custom configurations, reports generated
- **Vendor owns**: Product code, platform IP, algorithms, third-party integrations
- **Shared**: Any custom integrations built for customer (joint ownership)

**Customer legal response**: "That makes sense, we just want to ensure our data is ours"

**Outcome**: Revised contract with clear data vs IP ownership, deal proceeded

**Key moves**:
- Clarified intent (customer wanted data ownership, not product IP)
- Proposed clear separation (customer data vs vendor IP)
- Avoided legal jargon, used plain language ("your data is yours, our code is ours")
</example>

<example id="security_addendum">
**Context**: $1.8M deal, CISO requires security addendum with custom terms

**Situation**: CISO sends 12-page security addendum with technical requirements

**Addendum requests**:
- **Standard**: SOC 2 Type II, penetration testing, encryption at rest/transit → Accepted (we already have)
- **Negotiable**: Customer right to audit source code → Compromised (third-party code review, not direct access)
- **Non-negotiable**: On-premise deployment (we're SaaS-only) → Declined, offered private cloud

**Negotiation**:
- **Accepted** standard security requirements (provided SOC 2 report, pen test results)
- **Compromised** on source code audit (offered third-party security firm review)
- **Declined** on-premise (explained SaaS model, offered GCP private region)

**CISO response**: "Private cloud region is acceptable if we get dedicated infrastructure"

**Outcome**: Agreed to dedicated cloud instance (standard enterprise offering), deal proceeded

**Key moves**:
- Separated standard vs negotiable vs non-negotiable (picked battles)
- Offered alternatives (third-party audit vs direct code access, private cloud vs on-premise)
- CISO accepted alternatives (met security requirements without breaking SaaS model)
</example>
</examples>

<pitfalls>
- **Legal before business deal**: Sending contract before pricing/scope approved = legal will negotiate price
- **Winging redlines**: Negotiating contract terms without legal team support = compliance risk
- **Conceding non-negotiables**: Accepting unlimited liability or IP transfer to close deal = company risk
- **Email-only negotiation**: Redline ping-pong via email = slow, misunderstood. Use calls.
- **Ignoring procurement**: Treating procurement as blocker vs partner = adversarial, delays deal
- **No escalation plan**: Legal teams gridlocked, no business sponsor to intervene = deal stalls
</pitfalls>
