# prep-demo Reference Guide

Detailed examples, edge cases, and troubleshooting for demo preparation skill.

> **Note:** All company names, contact names, and scenarios in this document are fictional examples created for demonstration purposes.

---

## Complete Demo Script Examples

### Example 1: Healthcare SaaS - Compliance Management Demo

**Context:** Mid-sized hospital network, pain = manual audit trails causing compliance failures, Champion = Director of Compliance, Stage 2

**Demo Script:**

```markdown
---
generated_by: prep-demo
generated_on: 2025-11-17T14:30:00Z
deal_id: Northwind Medical Center
sources:
  - sample-data/Runtime/Sessions/NorthwindMedical/deal.md
  - sample-data/Runtime/Sessions/NorthwindMedical/2025-11-10_stage1_call_summary__discovery.md
artifact_type: demo_script
---

# Demo Script: Northwind Medical Center
**Date:** 2025-11-22, 2:00 PM ET
**Duration:** 60 minutes
**Attendees:** Sarah Chen (Dir. Compliance), Mike Rodriguez (IT Security), Jennifer Adams (EVP Operations)

## Pre-Demo Checklist
- [ ] Demo environment loaded with sample audit data (hospital scenario)
- [ ] User accounts: sarah.demo@northwind.test, mike.demo@northwind.test
- [ ] Integration: Mock HL7 feed showing real-time event capture
- [ ] Backup: Screen recording ready if live demo fails

## Minute-by-Minute Flow

### 0-5 min: Opening & Pain Recap
**Presenter:** AE (John)

**Script:**
"Thanks for joining. Last week Sarah shared that manual audit trails are causing 2-3 compliance findings per quarter, with remediation taking 40+ hours each time. Today we'll show exactly how our platform eliminates manual tracking and provides real-time compliance evidence. By the end, you'll see how this prevents findings before they happen.

Quick confirmation: Sarah, Mike, Jennifer - are there specific workflows or compliance scenarios you want us to prioritize?"

**Validation Question:**
"Sarah, does that capture your top concern, or should we focus elsewhere?"

---

### 5-20 min: Use Case 1 - Automated Audit Trail Capture
**Presenter:** SE (David)

**Demo Flow:**
1. **Show current pain** (2 min)
   - Display spreadsheet with manual audit log (Sarah's current process)
   - "This is what Sarah's team does today - manually documenting every system access, data change, and policy update."

2. **Demonstrate automation** (5 min)
   - Log into platform as Sarah
   - Show real-time event feed capturing user actions automatically
   - Filter by date range, user role, data type
   - Export compliance report (PDF with regulatory headers)

3. **Highlight pain relief** (3 min)
   - "Sarah, your team spends 10 hours/week on manual logging. This is now zero manual work."
   - Show chain-of-custody validation (tamper-proof audit log)
   - Demonstrate search: "Show me all PHI accessed by contractors in past 30 days" (instant results)

4. **Interactive validation** (5 min)
   - "Sarah, how does this compare to your current Excel-based process?"
   - "Mike, from a security perspective, does this meet your tamper-proof requirements?"
   - "What concerns do you have about automated capture?"

**Pain Mapping:**
- Manual logging (10 hrs/week) → Automated capture (0 hrs)
- Compliance findings (2-3/quarter) → Proactive alerts before audits
- Remediation (40 hrs/finding) → Evidence instantly available

---

### 20-35 min: Use Case 2 - Proactive Compliance Alerts
**Presenter:** SE (David)

**Demo Flow:**
1. **Show scenario** (3 min)
   - "Jennifer mentioned quarterly audits are stressful because you don't know what auditors will find."
   - Display compliance dashboard with risk indicators (yellow/red alerts)

2. **Demonstrate proactive detection** (5 min)
   - Show alert: "Policy violation detected - User accessed PHI without documented business reason"
   - Drill into details: who, what, when, where
   - Show remediation workflow: assign to compliance officer, document resolution, close loop

3. **Highlight business impact** (3 min)
   - "This alert fires before an auditor sees it. Your team fixes it proactively."
   - Show historical trend: violations decreasing over time (behavioral change)

4. **Interactive validation** (4 min)
   - "Sarah, which compliance scenarios worry you most? HIPAA privacy? Device security? Policy adherence?"
   - "Let's set up a custom alert for your top concern right now." (live configuration)

**Pain Mapping:**
- Reactive findings → Proactive detection and remediation
- Audit anxiety → Confidence with real-time visibility
- 40 hrs remediation → 5 hrs proactive fix

---

### 35-45 min: Use Case 3 - Audit-Ready Reporting
**Presenter:** SE (David)

**Demo Flow:**
1. **Show audit scenario** (2 min)
   - "Sarah, you mentioned auditors request documentation packages. Let's build one live."

2. **Demonstrate report generation** (5 min)
   - Select date range (Q3 2025)
   - Select compliance domains (PHI access, policy adherence, breach response)
   - Generate comprehensive audit package (PDF, 200+ pages, auto-formatted)
   - Show table of contents, executive summary, detailed evidence

3. **Highlight time savings** (2 min)
   - "Your team currently spends 40 hours compiling this manually. Platform does it in 30 seconds."
   - Show version control: reports are snapshot-in-time, tamper-proof

4. **Interactive validation** (1 min)
   - "Sarah, does this format match what auditors expect, or do we need to customize?"

**Pain Mapping:**
- 40 hrs manual compilation → 30 seconds automated generation
- Auditor delays (missing docs) → Complete package instantly available

---

### 45-55 min: Technical Deep-Dive & Integration
**Presenter:** SE (David), with Mike driving questions

**Topics:**
1. **EHR Integration** (Mike's requirement)
   - Show HL7 feed configuration (live data flowing)
   - API architecture diagram
   - "Implementation: 2-week sprint, our team handles the integration"

2. **Data security** (Mike's concern)
   - Encryption at rest (AES-256) and in transit (TLS 1.3)
   - Access controls: RBAC with SSO integration
   - SOC 2 Type II, HITRUST certified

3. **Scalability** (Jennifer's concern)
   - Platform supports enterprise-scale hospital networks
   - Handles 1M+ events/day without performance degradation

**Validation Questions:**
- "Mike, what integration or security concerns remain?"
- "Jennifer, from an IT operations perspective, what worries you about implementation?"

---

### 55-60 min: Q&A & Next Steps
**Presenter:** AE (John)

**Q&A:** (5 min)
- Address any outstanding concerns
- Clarify pricing, implementation timeline, support model

**Next Steps Close:** (5 min)
"Based on what you've seen, this solves your audit trail pain and prevents compliance findings. Here's what I recommend:

**Option 1:** 30-day pilot with your compliance team (10 users)
- Timeline: Start Dec 1, results by Jan 1
- Scope: Audit trail capture + proactive alerts
- Success criteria: Zero manual logging hours, 1+ proactive finding caught

**Option 2:** Full proof-of-concept (POC) with Epic integration
- Timeline: 60 days (includes Epic HL7 setup)
- Scope: All three use cases demonstrated today
- Success criteria: Pass mock audit with auto-generated report

Which approach makes more sense given your Q1 audit schedule?"

**Validation Question:**
"Sarah, if this works as demonstrated, what would need to happen internally to move forward?"

**Commitment Ask:**
"Let's schedule 30 minutes next week to finalize pilot scope and timeline. Does [specific date] work?"

---

## Post-Demo Actions
- [ ] Send follow-up email with demo recording link
- [ ] Share audit report sample (customized for Northwind)
- [ ] Schedule pilot kickoff meeting
- [ ] Assign SE to draft Epic integration plan

## Red Flags to Watch
- Sarah disengaged or skeptical during automation demo → May doubt platform accuracy
- Mike silent on security questions → May have unvoiced concerns
- Jennifer focused on price, not value → May not feel pain urgently
- No commitment to next step → Revisit discovery (is pain real?)
```

---

### Example 2: Manufacturing SaaS - Supply Chain Visibility Demo

**Context:** Mid-market manufacturer, pain = production delays from supplier issues not caught early, Champion = VP Operations, Stage 3

**Demo Script Highlights:**

```markdown
## Use Case 1: Real-Time Supplier Risk Monitoring (15 min)
**Pain:** Supplier delays discovered too late (after production impact)
**Demo:** Show live dashboard with supplier health scores, lead time trends, quality metrics
**Validation:** "Tom, which suppliers worry you most? Let's set alerts for them right now."

## Use Case 2: Predictive Delay Alerts (15 min)
**Pain:** Reactive firefighting when materials don't arrive
**Demo:** Show ML-powered delay prediction (3-week advance warning), alternate supplier recommendations
**Validation:** "If you'd had this alert 3 weeks ago, would it have prevented last month's production stoppage?"

## Use Case 3: Collaboration Workflow (10 min)
**Pain:** Email chaos when coordinating supplier escalations
**Demo:** Show shared workspace with supplier, issue tracking, document sharing, resolution timeline
**Validation:** "How does this compare to your current email threads and spreadsheet tracking?"

## Technical: ERP Integration (10 min)
**Focus:** SAP integration (Tom's requirement), data sync architecture, implementation timeline
**Validation:** "IT team, what concerns do you have about SAP integration complexity?"

## Next Steps Close:
"You've mentioned production delays cost $50K per incident. If this prevents 2-3 delays per year, ROI is clear. Let's run a 60-day pilot with your top 20 suppliers. Can we get IT and procurement aligned next week to kick off?"
```

---

## Technical Setup Checklist Examples

### SaaS Platform Demo Checklist

**Environment Prep:**
- [ ] Demo instance provisioned: demo.company.com/customer-name
- [ ] Sample data loaded:
  - 100+ user accounts (realistic names, roles)
  - 6 months historical data (events, trends, reports)
  - Customer-specific scenarios (use their terminology)
- [ ] Integrations configured:
  - SSO test connection (if showing integration)
  - API endpoint with sample data flow
  - Webhook test (show real-time event capture)
- [ ] Branding applied:
  - Customer logo on login screen
  - Color scheme customized
  - White-label features enabled

**Access Validation:**
- [ ] User credentials tested: demo.user@customer.com / [DEMO_PASSWORD]
- [ ] Admin credentials tested: demo.admin@customer.com / [DEMO_PASSWORD]
- [ ] Permissions validated: demo user sees correct data scope
- [ ] SSO flow tested end-to-end (if applicable)

**Performance Check:**
- [ ] Load time under 2 seconds for all screens
- [ ] No test/dummy data visible to customer
- [ ] Search queries return results in under 1 second
- [ ] Reports generate in under 10 seconds

**Backup Plan:**
- [ ] Screen recording of full demo flow (use if live demo fails)
- [ ] Screenshot deck with annotated walkthrough
- [ ] Local demo environment (offline fallback)

**Logistics:**
- [ ] Zoom/Teams meeting scheduled with correct attendees
- [ ] Screen sharing tested (no personal data visible on desktop)
- [ ] Dual monitors configured (demo on screen 1, notes on screen 2)
- [ ] Phone on silent, notifications disabled
- [ ] Water available (avoid dry mouth during 60-min talk)

**Owner:** SE Team
**Deadline:** Day before demo (test dry-run morning of demo)

---

### On-Premise Software Demo Checklist

**Environment Prep:**
- [ ] Virtual machine provisioned with customer's OS version
- [ ] Software installed and licensed (no trial expiration warnings)
- [ ] Sample database loaded with realistic data volume
- [ ] Customer-specific configurations applied (workflows, fields, reports)

**Integration Testing:**
- [ ] LDAP/AD connection tested (if showing user sync)
- [ ] Database connection validated (SQL Server, Oracle, MySQL)
- [ ] File system integration tested (import/export scenarios)
- [ ] Email server connected (if showing notifications)

**Disaster Recovery:**
- [ ] VM snapshot taken (rollback if demo breaks)
- [ ] Local backup environment ready
- [ ] Presenter laptop fully charged + power adapter
- [ ] Offline demo mode available (no internet required)

**Owner:** SE + IT Team
**Deadline:** 2 days before demo (allow time for troubleshooting)

---

## Customer Demo Agenda Examples

### Example 1: Compliance Platform Demo (External-Facing)

```markdown
Subject: Northwind Medical Center - Compliance Platform Demo (Nov 22)

Hi Sarah, Mike, Jennifer,

Thanks for scheduling time to see our platform in action. Based on our discovery discussion, we'll focus on the pain points you shared:

**Agenda (60 minutes):**
1. **Recap Your Priorities** [5 min]
   - Manual audit trail burden (10 hrs/week)
   - Reactive compliance findings (2-3 per quarter)
   - Audit preparation stress (40+ hours per audit)

2. **Live Demo: Automated Audit Trails** [15 min]
   - Real-time event capture (eliminate manual logging)
   - Chain-of-custody validation (tamper-proof)
   - Instant search and reporting

3. **Live Demo: Proactive Compliance Alerts** [15 min]
   - Policy violation detection before audits
   - Custom alert configuration for your scenarios
   - Remediation workflow tracking

4. **Live Demo: Audit-Ready Reporting** [10 min]
   - One-click audit package generation
   - Customizable report templates
   - Version control and evidence preservation

5. **Technical Q&A: Integration & Security** [10 min]
   - Epic EHR integration approach
   - Data security and compliance certifications
   - Implementation timeline and support

6. **Next Steps** [5 min]
   - Pilot options and timelines
   - Success criteria and decision process

**Please Confirm:**
- Are these the right attendees, or should we include others?
- Any specific workflows or compliance scenarios to prioritize?
- Do you have 60 minutes, or should we shorten the agenda?

Looking forward to showing you how this eliminates compliance findings and saves your team 50+ hours per quarter.

Best,
John Smith
Account Executive
(555) 123-4567
```

---

### Example 2: Supply Chain Platform Demo (External-Facing)

```markdown
Subject: Acme Manufacturing - Supply Chain Visibility Demo (Dec 5)

Hi Tom,

Per our conversation, here's the agenda for next week's product demo. We'll focus on solving the supplier delay issues that caused last month's production stoppage.

**Agenda (75 minutes):**
1. **Recap & Context** [5 min]
   - Supplier delays discovered too late (after production impact)
   - $50K cost per production stoppage
   - Manual supplier monitoring across 100+ suppliers

2. **Demo: Real-Time Supplier Risk Monitoring** [20 min]
   - Live dashboard with supplier health scores
   - Lead time trend analysis
   - Quality metrics and risk indicators
   - Custom alerts for your critical suppliers

3. **Demo: Predictive Delay Alerts** [20 min]
   - 3-week advance warning of potential delays
   - Machine learning models using historical patterns
   - Alternate supplier recommendations
   - Impact analysis (which production lines affected)

4. **Demo: Supplier Collaboration Workflow** [15 min]
   - Shared workspace for issue escalation
   - Document sharing and version control
   - Resolution timeline tracking
   - Automated status updates

5. **Technical Deep-Dive: SAP Integration** [10 min]
   - Data sync architecture (purchase orders, inventory, receipts)
   - Implementation approach and timeline
   - IT requirements and support model

6. **Next Steps & Pilot Discussion** [5 min]
   - 60-day pilot scope (top 20 suppliers)
   - Success criteria (prevent 1+ production delay)
   - Timeline to decision

**Attendees:**
- Tom Jackson (VP Operations)
- Lisa Chen (Procurement Director)
- Mark Williams (IT Lead)

Please confirm this agenda works, or let me know what to adjust.

Best,
Sarah Johnson
Account Executive
(555) 987-6543
```

---

## Demo Anti-Patterns to Avoid

### 1. Feature Tour (Not Value-Led)
**Bad:**
"Let me show you all our features. First, the dashboard. It has 15 widgets. You can customize them. Next, the reporting module. We have 50+ report templates. Now let's look at the admin panel..."

**Why It Fails:** Customer loses interest, no connection to pain, no differentiation

**Good:**
"You mentioned production delays cost $50K each. Let me show exactly how this alert would have prevented last month's delay—3 weeks in advance. Watch this..."

**Why It Works:** Immediate connection to quantified pain, specific value demonstration

---

### 2. Talking at Customer (Not Interactive)
**Bad:**
60 minutes of presenter monologue with no questions or validation

**Why It Fails:** No engagement, no confirmation of fit, customer checks out

**Good:**
"Tom, does this alert format give you enough advance notice, or would you need more detail?"
"Lisa, how does this compare to your current supplier scorecards?"
"Mark, pause me anytime if you have integration questions."

**Why It Works:** Validates fit in real-time, surfaces objections early, keeps customer engaged

---

### 3. Technical Jargon Overload
**Bad:**
"Our microservices architecture leverages Kubernetes orchestration with Redis caching and Kafka event streaming for sub-millisecond latency..."

**Why It Fails:** Business stakeholders tune out, sounds complex and risky

**Good:**
"It's fast—search results appear instantly, even across millions of records. And it's reliable—our platform has 99.9% uptime."

**Why It Works:** Business outcomes, not technical architecture

**Exception:** When Technical Buyer is in the room, layer in technical depth during dedicated section

---

### 4. Ignoring Discovery Context
**Bad:**
Running generic demo with no reference to customer's specific pain, stakeholders, or use cases

**Why It Fails:** Feels impersonal, not tailored, customer questions relevance

**Good:**
"Sarah, you mentioned compliance findings take 40 hours to remediate. Watch how this generates the exact report auditors requested—in 30 seconds."

**Why It Works:** Directly addresses stated pain with specific time savings

---

### 5. No Clear Next Step
**Bad:**
Demo ends with "Any questions? Great, we'll follow up soon."

**Why It Fails:** No momentum, no commitment, deal stalls

**Good:**
"Based on what you've seen, this solves your audit trail pain. Let's run a 30-day pilot starting Dec 1. Can we schedule 30 minutes next week to finalize the scope?"

**Why It Works:** Clear next step, specific timeline, asks for commitment

---

### 6. Demo Fails with No Backup Plan
**Bad:**
Live demo crashes, presenter fumbles, customer loses confidence

**Why It Fails:** Looks unprofessional, raises reliability concerns

**Good:**
"Looks like we have a network issue. Let me switch to our backup recording while we troubleshoot. You'll see the same flow..."

**Why It Works:** Professionalism maintained, demo continues without gap

**Prevention:** Always have screen recording or screenshot deck as backup

---

## Troubleshooting Guide

### Issue: No Discovery Notes Available

**Symptom:** deal.md History section is sparse, Pain section has generic placeholders

**Diagnosis:** Discovery incomplete or poorly documented

**Solutions:**
1. **Option A:** Run coach skill to assess deal health—may need discovery before demo
2. **Option B:** Embed discovery validation questions in demo call
   - "Before we start, help me understand your current process for [workflow]..."
   - "What happens when [pain scenario] occurs today?"
   - "Who's most impacted by [problem]?"
3. **Option C:** Schedule separate discovery call before demo (recommend to user)

**Communication:**
```
WARNING: Limited discovery context found in deal.md
IMPACT: Demo script will be generic without pain-specific customization
RECOMMENDATION: Run coach skill to assess whether discovery is complete, or embed validation questions in demo call
```

---

### Issue: Too Many Use Cases to Cover

**Symptom:** Deal has 8+ pain points, 90-minute demo agenda, risk of feature tour

**Diagnosis:** Lack of prioritization, trying to show everything

**Solutions:**
1. **Prioritize ruthlessly:** Pick top 3 pain points by severity and stakeholder importance
2. **Ask user:** "Which pain matters most—compliance, cost, or efficiency?"
3. **Defer secondary use cases:** "We can cover reporting in a follow-up if time allows"

**Demo Script Adjustment:**
```
Primary Use Cases (must-show):
1. [Highest pain] - 15 min
2. [Second pain] - 15 min
3. [Third pain] - 10 min

Defer to follow-up:
4-8. [Other pains] - Mention briefly, offer deep-dive later
```

---

### Issue: Technical Buyer Dominates with Edge Cases

**Symptom:** IT person derails demo with "What if..." questions about rare scenarios

**Diagnosis:** Technical validation needed but blocking business stakeholder engagement

**Solutions:**
1. **Acknowledge and defer:** "Great question—let's cover that in the technical section at [timestamp]"
2. **Parallel track:** "Mark, can we schedule 30 min separately for technical deep-dive? I want to make sure Sarah and Tom see the business value today."
3. **Direct answer with time-box:** "Here's how we handle that [2-min answer]. Any blockers, or can we continue?"

**Script Language:**
"Mark, I'm noting your integration questions—we'll have dedicated time at minute 45 to dive deep. Sound good?"

---

### Issue: Executive Stakeholder Joins Late

**Symptom:** EVP joins 20 minutes into demo, misses context and pain recap

**Diagnosis:** Exec scheduling conflict, not a deal-killer but needs re-anchoring

**Solutions:**
1. **Quick re-anchor:** "Jennifer, thanks for joining. Quick context: We're showing Sarah how this eliminates 40 hours of manual audit work per quarter. You'll see the ROI in the next section."
2. **Summarize pain:** "In discovery, your team shared three priorities: [pain 1], [pain 2], [pain 3]. We're demonstrating solutions for each."
3. **Adjust remaining demo:** Emphasize business outcomes for exec (ROI, risk reduction, efficiency) over technical details

**Script Language:**
"Jennifer, welcome! We just showed automated audit trails—saving Sarah's team 10 hours per week. Next up is proactive compliance alerts to prevent findings before audits. This directly impacts your Q1 audit risk."

---

### Issue: Customer Requests Features Not on Roadmap

**Symptom:** "Can your platform do [feature X]?" and answer is "not yet"

**Diagnosis:** Feature gap, risk of disqualification if critical

**Solutions:**
1. **Validate criticality:** "Is [feature X] a must-have, or nice-to-have?"
2. **Workaround offer:** "We don't have [X] built-in, but customers solve this with [workaround Y]"
3. **Roadmap transparency:** "[Feature X] is on our Q2 roadmap—we can prioritize it if you move forward"
4. **Redirect to differentiation:** "We focus on [your strength] instead of [their request]. Does that solve your core problem?"

**Script Language:**
"We don't have [X] today, but 80% of customers solve this with [workaround]. If [X] is a blocker, we can explore custom development. What's driving that requirement?"

---

### Issue: Silent Stakeholder (Not Engaging)

**Symptom:** One attendee hasn't spoken or asked questions, possible hidden objection

**Diagnosis:** Disinterest, irrelevant role, or unvoiced concern

**Solutions:**
1. **Direct engagement:** "Mike, from a security perspective, what concerns do you have about [topic]?"
2. **Role-specific question:** "Jennifer, how does this impact your operations budget planning?"
3. **Post-demo follow-up:** AE reaches out individually: "Wanted to check—did the demo address your priorities?"

**Script Language:**
"Mike, you've been quiet—what's your take on the integration approach? Any red flags from IT's perspective?"

---

### Issue: Demo Runs Long (Time Overrun)

**Symptom:** 60-minute agenda hitting 75 minutes, risk of losing attendees

**Diagnosis:** Too much detail, too many questions, poor time management

**Solutions:**
1. **Skip secondary use cases:** "In the interest of time, let's skip [use case 3] and jump to Q&A"
2. **Accelerate pace:** "I'll move quickly through this next section—stop me if you have questions"
3. **Offer follow-up:** "We're running long—can we schedule 30 min next week to cover [deferred topics]?"

**Script Language:**
"We're at 50 minutes and I want to leave time for Q&A. Let me summarize [remaining section] quickly, and we can go deeper in follow-up if needed."

---

## When to Abort Demo and Return to Discovery

**Red Flags During Demo:**

1. **Customer can't articulate pain clearly**
   - Symptom: Vague answers like "We want to be more efficient"
   - Action: Stop demo, ask discovery questions: "Help me understand your current process and where it breaks down"

2. **Decision maker not present**
   - Symptom: Technical team attending, but Economic Buyer absent
   - Action: "Before we continue, who will make the final purchase decision? Should we reschedule to include them?"

3. **No budget discussion**
   - Symptom: Customer loves demo but goes silent on pricing or timeline
   - Action: "If this solves your problem, what budget has been allocated? What's the approval process?"

4. **Stakeholder conflict visible**
   - Symptom: IT says "This won't work with our systems" while business says "We need this now"
   - Action: "I'm hearing different priorities. Let's pause and align on what success looks like for both teams."

5. **Customer already decided on competitor**
   - Symptom: "How does this compare to [competitor] we're evaluating?"
   - Action: Stop demo, run coach skill to assess competitive position, may need discovery reset

**Script Language:**
"I'm realizing we may need to take a step back. Before I show more product, help me understand: What problem are you trying to solve, and what happens if you don't solve it? Who needs to be involved in this decision?"

---

## Related Skills

- **prep-discovery** - Run this BEFORE prep-demo if discovery incomplete
- **coach** - Assess deal health if demo prep reveals major gaps
- **sales_communications** - Generate confirmation email with demo agenda
- **roi-model** - Prepare financial justification for demo discussion
- **next-steps** - Generate post-demo action plan
