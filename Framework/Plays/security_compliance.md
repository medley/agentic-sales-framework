---
name: "Security & Compliance Play"
type: "sales_play"
owner: "{YOUR_NAME}"
version: "1.0.0"
license: "MIT - See LICENSE.md"
---

# Security & Compliance Play: Security Review Navigation

<triggers>
- security_questionnaire (100+ question security assessment)
- infosec_review (CISO or security team must approve)
- compliance_requirements (GDPR, HIPAA, SOC 2, ISO 27001, FedRAMP)
- vendor_assessment (vendor risk management process)
- data_privacy_concerns (customer data handling, data residency)
- penetration_test_request (customer wants pen test results or right to test)
</triggers>

<principles>
- **Standard responses**: Pre-approved security questionnaire answers (don't answer from scratch each time)
- **Security champion**: Find internal security advocate (not just business champion)
- **Third-party attestations**: SOC 2, ISO 27001, pen test reports (use existing vs custom for each customer)
- **Parallel process**: Run security review in parallel with business/legal (not sequential)
- **Engage security early**: Stage 2-3 (don't wait until Stage 5 contract negotiation)
- **Know your limits**: What security concessions you can make vs escalate to internal security team
</principles>

<steps>
1. **Anticipate security review**:
   - **Stage 1-2**: Ask champion "What's your security approval process?" (don't wait for surprise)
   - **Risk industries**: Healthcare (HIPAA), finance (SOC 2/PCI), government (FedRAMP), EU (GDPR)
   - **Deal size**: >$500K often triggers vendor risk assessment
   - **Timeline**: Add 2-4 weeks to sales cycle for security review

2. **Prepare security package**:
   - **SOC 2 Type II report**: Industry standard (if you have it, provide proactively)
   - **Penetration test results**: Annual pen test report (redact sensitive details)
   - **Security questionnaire responses**: Pre-fill standard questionnaire (SIG, CAIQ, etc.)
   - **Compliance certifications**: ISO 27001, GDPR DPA, HIPAA BAA (if applicable)
   - **Security whitepaper**: 2-4 page overview (architecture, encryption, access controls, incident response)
   - **Insurance**: Cyber liability insurance certificate ($2M-$5M coverage typical)

3. **Identify security stakeholders**:
   - **CISO or Dir Security**: Final approver (engage directly, don't rely on champion to relay)
   - **Security Analyst**: Day-to-day reviewer (handles questionnaire, pen test review)
   - **Compliance team**: GDPR, HIPAA, SOC 2 specialists (if separate from security)
   - **Risk Management**: Vendor risk assessment (enterprise companies often have dedicated team)

4. **Conduct security review**:
   - **Questionnaire**: Provide pre-filled responses (100-300 questions typical)
   - **Clarifications**: Security team will ask follow-ups (respond within 24-48 hours)
   - **Concerns**: Common asks:
     - Data residency (US-only, EU-only, multi-region options)
     - Encryption (at rest + in transit, key management)
     - Access controls (SSO, MFA, RBAC)
     - Incident response (breach notification SLA, process)
     - Subprocessors (who has access to customer data?)
     - Audit rights (can customer audit your security annually?)

5. **Negotiate security terms**:
   - **Standard concessions** (low risk, usually accepted):
     - Annual security audit rights (with 30-day notice)
     - Breach notification within 72 hours (GDPR standard)
     - Data residency options (if you have multi-region infrastructure)
     - Subprocessor list and approval process
   - **Escalation needed** (high risk, requires internal security approval):
     - On-demand audits (no notice required)
     - Customer access to production environment or source code
     - Unlimited liability for data breaches
     - Custom encryption key management (customer-managed keys)

6. **Parallel track with business deal**:
   - **Week 1-2**: Start security review (while business case is being built)
   - **Week 3-4**: Address security questions (while technical validation happening)
   - **Week 5**: Security approval (while legal review starting)
   - **Avoid**: Waiting until legal review to start security (adds 2-4 weeks to cycle)

7. **Get security sign-off**:
   - **Security approval**: CISO or Security team approves vendor
   - **Risk accepted**: Document any residual risks (e.g., "Vendor doesn't have FedRAMP, but has SOC 2 Type II - risk accepted")
   - **Conditional approval**: "Approved if [X security control added]" (negotiate or implement control)
</steps>

<examples>
<example id="standard_security_review">
**Context**: $1.2M SaaS deal, healthcare customer (HIPAA required), CISO must approve

**Situation**: Champion (CIO) says "CISO will need to review security before we proceed"

**Action**: Proactive security engagement (Stage 2, before proposal)

**Security package provided**:
- SOC 2 Type II report (passed all controls)
- HIPAA Business Associate Agreement (BAA) template
- Penetration test results (annual test, zero critical findings)
- Security questionnaire (pre-filled SIG Lite, 100 questions)
- Security whitepaper (encryption, access controls, incident response)

**Security review process**:
- **Week 1**: Security team reviewed SOC 2 report (no issues)
- **Week 2**: Security team sent follow-up questions:
  1. "Do you support customer-managed encryption keys?" (No, but we use AWS KMS with annual key rotation)
  2. "What's your data residency?" (US-only data centers, no offshore access)
  3. "Who are your subprocessors?" (AWS, SendGrid for email, Stripe for payments)
- **Week 3**: Security team requested call to discuss architecture (30 min with SE + Security Analyst)
- **Week 4**: CISO approved vendor (conditional on BAA execution)

**Outcome**: Security approval in 4 weeks (parallel with business deal), no blockers

**Key moves**:
- Provided security package proactively (didn't wait for request)
- SOC 2 Type II + HIPAA BAA addressed 90% of questions (standard for healthcare)
- Security call (SE + Analyst) resolved architecture questions (built trust)
- Parallel track: Security review done before legal review started (no cycle delay)
</example>

<example id="security_questionnaire_efficiency">
**Context**: $2M enterprise deal, customer sends 287-question security questionnaire

**Situation**: Custom questionnaire (not SIG or CAIQ standard), very detailed

**Challenge**: Answering 287 questions from scratch = 20+ hours of internal security team time

**Action**: Requested questionnaire mapping to SOC 2

**AE to customer security team**:
```
Thanks for the questionnaire. We've completed SOC 2 Type II audit, which covers most of these controls.
Can we provide SOC 2 report + answer gaps, rather than full 287-question questionnaire?
This will be faster and more reliable (audited vs self-reported).
```

**Customer security response**:
```
Good idea. Send SOC 2 report. We'll review and flag any gaps.
```

**Outcome**: Customer reviewed SOC 2, identified 12 gaps (vs 287 questions), AE answered 12 questions

**Time saved**: 20 hours → 2 hours (10x faster)

**Key moves**:
- Proposed SOC 2 mapping (avoided custom questionnaire)
- Positioned as faster + more reliable (customer benefit, not just vendor convenience)
- Customer security team valued efficiency (they didn't want to review 287 answers either)
</example>

<example id="data_residency_negotiation">
**Context**: $1.5M deal, EU customer, requires EU-only data residency (GDPR)

**Situation**: Customer legal says "Data cannot leave EU" (hard requirement)

**Challenge**: Vendor primary data centers in US, EU expansion planned but not launched yet

**Options analysis**:
1. **Delay deal until EU data center live** (6 months = deal dies)
2. **Decline deal** (walk away from $1.5M)
3. **Negotiate transition plan** (start in US, migrate to EU when ready)
4. **Partner with EU hosting provider** (custom deployment, expensive)

**Chosen approach**: Option 3 (transition plan)

**Proposal to customer**:
- **Phase 1** (0-6 months): Data in US data center with GDPR-compliant DPA (legal, but not preferred)
- **Phase 2** (6+ months): Migrate to EU data center when launched (customer is early access)
- **Customer benefit**: Early access to product now + EU data residency later (vs waiting 6 months)
- **Vendor benefit**: Close deal now, customer becomes EU reference customer

**Customer legal response**: "If DPA is GDPR-compliant and we get early access to EU, acceptable"

**Outcome**: Deal closed with transition plan, customer migrated to EU data center 7 months later

**Key moves**:
- Didn't walk away from deal (proposed creative solution)
- Transition plan met customer legal requirement (GDPR DPA) + preference (EU residency eventually)
- Customer valued early access (didn't want to wait 6 months)
- Vendor got EU reference customer (strategic value beyond $1.5M)
</example>

<example id="penetration_test_negotiation">
**Context**: $800K deal, CISO requests "right to conduct annual penetration test"

**Situation**: Customer wants to pen test vendor's production environment annually

**Risk**: Customer pen test could disrupt service, expose vulnerabilities, liability concerns

**Negotiation**:
- **Customer request**: "We need right to pen test your environment annually"
- **Vendor position**: "We conduct annual third-party pen tests. Can we provide results instead?"
- **Customer**: "We prefer our own pen test team"
- **Vendor counter-offer**: "How about this: We provide our annual pen test results. If you have concerns, we'll engage a mutually-agreed third-party to conduct additional testing (not customer's team directly)."

**Rationale**:
- Vendor annual pen test = already done, no incremental cost
- Third-party pen test (if needed) = neutral, professional, insured
- Customer pen test team = risk (unknown methodology, potential service disruption, liability)

**Customer CISO response**: "Third-party pen test is acceptable. We'll review your annual report first."

**Outcome**: Contract includes "Vendor provides annual pen test results; if gaps identified, mutually-agreed third-party conducts additional testing at vendor's expense"

**Key moves**:
- Proposed alternative (third-party vs customer team) that met customer's goal (validation) without vendor risk
- CISO valued professional pen test > internal team (higher quality, insured)
- Vendor controlled methodology and timing (vs customer ad-hoc testing)
</example>

<example id="security_champion_advocacy">
**Context**: $1.8M deal, complex security review (CISO + Security Architect + Compliance team)

**Situation**: Business champion (VP Ops) doesn't understand security requirements, can't drive security approval

**Action**: Identified security champion (separate from business champion)

**Security champion**: Sr Security Analyst (part of CISO's team)

**Engagement**:
- **Week 1**: AE + SE met with Sr Security Analyst (not just CISO)
- **Week 2**: Security Analyst reviewed SOC 2 report, asked detailed questions (SE answered)
- **Week 3**: Security Analyst became internal advocate (told CISO "I've reviewed, they're solid")
- **Week 4**: CISO approved vendor (trusted Security Analyst's recommendation)

**Outcome**: Security Analyst championed deal through CISO approval (business champion couldn't do this)

**Key moves**:
- Identified security champion separate from business champion (different expertise)
- Built relationship with Security Analyst (not just CISO)
- SE engaged deeply on technical security (built credibility)
- Security Analyst sold internally to CISO (more effective than external vendor pitching)
</example>
</examples>

<pitfalls>
- **Waiting until late-stage**: Starting security review in Stage 5 (Contract) = 2-4 week delay
- **No standard responses**: Answering every questionnaire from scratch = inefficient, inconsistent
- **Over-promising**: Agreeing to custom security controls you can't deliver = deal falls apart in implementation
- **Bypassing security team**: Trying to close deal without CISO approval = contract blocked at last minute
- **No security champion**: Relying on business champion to navigate security = they don't have expertise
- **Ignoring compliance**: Not identifying HIPAA, GDPR, SOC 2 requirements early = rework and delays
</pitfalls>
