---
license: "MIT - See LICENSE.md"
---

# Discovery Prep — Reference Documentation

**Purpose:** Detailed examples, edge cases, troubleshooting, and best practices for the prep-discovery skill

**For runtime implementation contract:** See `SKILL.md`

---

## Examples

### Example 1: Sandler Pain Stage Discovery Prep

**User Request:**
> "Prep discovery call for Example Pharma deal next Tuesday"

**Skill Execution:**

1. **Read Context:**
   - Deal: `sample-data/Runtime/Sessions/ExamplePharma/deal.md`
   - Stage: 1 - Discover (maps to Sandler Pain stage)
   - Methodology: Default (could benefit from Sandler approach)
   - Known stakeholders: None yet (TBD)
   - History: Initial outreach completed

2. **Identify Objectives:**
   - Uncover 3-5 pain points
   - Test pain intensity (looking for 7+ on scale)
   - Identify personal stakes for stakeholders
   - Map decision makers
   - Qualify or disqualify based on pain/urgency

3. **Generate Internal Prep Agenda:**
   ```markdown
   # Internal Discovery Prep — Example Pharma
   **Date:** 2025-11-15
   **Deal Stage:** 1 - Discover (Sandler Pain focus)

   ## Discovery Objectives
   1. Uncover emotional pain related to [problem hypothesis]
   2. Test pain intensity (target: 7+ on 1-10 scale)
   3. Identify personal stakes for each attendee
   4. Map full decision maker landscape
   5. Qualify or disqualify based on pain criteria

   ## Roles & Responsibilities
   - **Sarah (AE):** Lead meeting, drive Pain Funnel questions
   - **Mike (SE):** Technical discovery, ask about current tech stack
   - **Jordan (Sales Manager):** Observer, coach on debrief

   ## Pain Discovery Question Plan

   ### Pain Hypothesis 1: [Compliance/Regulatory Challenges]
   - Opening: "Walk me through your current compliance process..."
   - Pain Funnel:
     1. Tell me more about that...
     2. Can you be more specific? Give me an example.
     3. How long has that been a problem?
     4. What have you tried to do about that?
     5. And did that work?
     6. How much do you think that has cost you?
     7. **How do you feel about that?** [Listen for emotional language]
     8. Have you given up trying to deal with the problem?
   - Personal Stakes: "How does this impact YOU personally? What's at stake if it doesn't get fixed?"

   [... 2 more pain hypotheses ...]

   ## Risks to Mitigate
   - Risk: They're just "exploring options" (intellectual, not emotional)
     - Mitigation: Use Pain Funnel Q7 ("How do you feel?") to test emotional commitment
   - Risk: We present solutions too early
     - Mitigation: No demos, no pitches - discovery only
   - Risk: Decision maker not on call
     - Mitigation: Ask "Who else needs to be part of this conversation?"

   ## Success Criteria
   - ✅ Identified 3+ pain points with 7+ intensity
   - ✅ Personal stakes articulated for each stakeholder
   - ✅ Decision makers mapped
   - ✅ Clear qualification decision (continue or disqualify)

   ## Next Steps & Owners
   - Post-call debrief: 30 min immediately after (all attendees)
   - Sarah: Create Pain Discovery Chart within 24 hours
   - Mike: Document technical requirements
   - Jordan: Coach Sarah on qualification decision
   ```

4. **Generate Customer Agenda:**
   ```markdown
   # Discovery Call Agenda — Example Pharma
   **Date:** Tuesday, November 15, 2025
   **Time:** 2:00-3:00 PM EST
   **Format:** Zoom (link below)

   ## Purpose
   Our goal for this call is to understand your current challenges and desired outcomes
   to determine if it makes sense for us to continue exploring a potential fit. By the
   end of our conversation, we'll both have a clear sense of whether there's value in
   taking next steps — or if it's not the right fit, and that's totally okay to say.

   ## Attendees
   - **Your team:** [Confirmed attendees]
   - **Our team:** Sarah (Account Executive), Mike (Solutions Engineer)

   ## Agenda (60 minutes)

   1. **Introductions** (5 min)
      - Brief intros, roles, backgrounds

   2. **Current State & Challenges** (25 min)
      - Walk us through your current [process/system]
      - What challenges are you experiencing?
      - How long has this been an issue?
      - What have you tried so far?
      - How is this impacting your team/organization?

   3. **Desired Outcomes** (15 min)
      - What would success look like?
      - What would change if this problem was solved?
      - What's driving the timing to address this now?

   4. **Decision Process & Next Steps** (10 min)
      - Who else needs to be involved in evaluation?
      - What does your typical decision process look like?
      - What would next steps be if this seems like a fit?

   5. **Wrap-Up** (5 min)
      - Determine if it makes sense to continue
      - Agree on next actions (or agree it's not a fit)

   ## What We'll Need from You
   - Candid feedback about your challenges and priorities
   - Clarity on decision process and key stakeholders
   - Honest assessment of whether this is worth exploring further

   **Note:** If at any point it becomes clear this isn't a fit, we'll both benefit
   from recognizing that early. No hard feelings — we're here to find mutual fit.

   ## Expected Outcomes
   By the end of this call, we'll both know:
   - Whether your challenges align with what we solve
   - If the timing makes sense to explore further
   - What next steps would be (if any)

   Looking forward to the conversation!

   ---
   Zoom Link: [insert]
   Direct Dial: [insert]
   ```

5. **Generate Confirmation Email:**
   ```markdown
   ---
   to: stakeholder@example.com
   cc:
   subject: Discovery Call Confirmation - Tuesday 11/15 at 2pm EST
   ---

   ```email
   Hi [First Name],

   Looking forward to our discovery call on **Tuesday, November 15 at 2:00 PM EST**.

   **Meeting Link:** [Zoom URL]
   **Duration:** 60 minutes
   **Attendees:** You, [other stakeholders], Sarah and Mike from our team

   **Purpose:** Our goal is to understand your current challenges and priorities to
   determine if there's a good fit. By the end of our conversation, we'll both have
   clarity on whether it makes sense to continue exploring — or if it's not the right
   fit, which is completely fine.

   I've attached a brief agenda to help structure our time together. The key things
   we'd like to understand:
   - Current state challenges you're facing
   - What outcomes you're hoping to achieve
   - Decision process and key stakeholders

   **Quick prep (optional but helpful):** If you have 5-10 minutes before our call,
   thinking through these questions will help us make the most of our time:
   - What's the biggest challenge you're dealing with right now related to [area]?
   - What's driving the timing to address it now?
   - Who else should be part of this conversation?

   If this timing doesn't work or you need to reschedule, just let me know.

   Thanks,
   Sarah

   [Contact info]
   ```email
   ```

6. **Provenance (added to each artifact):**
   ```yaml
   source_deal: ../../deal.md
   generated_by: prep_discovery
   generated_at: 2025-11-11
   stage_ref: ../../_Shared/knowledge/stage_inventory.md
   methodology: Sandler (Pain stage focus)
   ```

7. **Output:**
   - `sample-data/Runtime/Sessions/ExamplePharma/2025-11-15_stage1_agenda__internal_prep.md`
   - `sample-data/Runtime/Sessions/ExamplePharma/2025-11-15_stage1_agenda__customer_discovery.md`
   - `sample-data/Runtime/Sessions/ExamplePharma/2025-11-15_stage1_email__confirm_discovery.md`

8. **Deal.md Updated:**
   ```markdown
   ## Generated Artifacts
   - 2025-11-11 2025-11-15_stage1_agenda__internal_prep.md (Internal discovery prep)
   - 2025-11-11 2025-11-15_stage1_agenda__customer_discovery.md (Customer discovery agenda)
   - 2025-11-11 2025-11-15_stage1_email__confirm_discovery.md (Discovery confirmation email)
   ```

**Result:**
- ✅ Internal team aligned on pain discovery approach
- ✅ Customer agenda sets up-front contract expectations
- ✅ Confirmation email professional and pressure-free
- ✅ All artifacts linked to deal

---

### Example 2: Follow-Up Discovery (Technical Deep-Dive)

**User Request:**
> "Prep for follow-up discovery call with Example Pharma technical team next week"

**Skill Execution:**

1. **Read Context:**
   - Deal: Example Pharma, Stage 1 - Discover
   - History: Initial discovery completed 2025-11-15
   - Existing artifacts: Pain points identified, need technical validation
   - Gap: Technical requirements not yet documented

2. **Identify Objectives:**
   - Validate technical feasibility of solving identified pains
   - Understand current tech stack and integration requirements
   - Assess technical team's pain points specifically
   - Document technical decision criteria

3. **Generate artifacts** (same 3-file structure) but:
   - Internal prep focuses on technical validation questions
   - Customer agenda emphasizes technical architecture discussion
   - Confirmation email references prior call and sets technical focus

**Result:** Discovery prep package tailored to technical follow-up phase

---

### Example 3: Multi-Stakeholder Discovery

**User Request:**
> "Prep discovery call with 5 Example Pharma stakeholders next month"

**Skill Execution:**

1. **Challenge:** Multiple stakeholders = multiple pains to uncover

2. **Internal Prep Adjustments:**
   - Role assignment: Who covers which stakeholder?
   - Pain discovery plan for EACH stakeholder
   - Risk: Meeting becomes presentation instead of discovery
   - Mitigation: Strict question-led format, no slides

3. **Customer Agenda Adjustments:**
   - Longer meeting (90 minutes vs. 60)
   - Explicit section: "We'll ask each of you about your specific challenges"
   - Set expectation: "This will be question-driven, not a presentation"

4. **Confirmation Email Adjustments:**
   - Address all stakeholders
   - "We're looking forward to hearing from each of you about your specific priorities"
   - Suggest pre-work: "Please come prepared to share your top 2-3 challenges"

**Result:** Discovery prep scaled for complex multi-stakeholder meeting

## Edge Cases & Troubleshooting

### Problem: Deal.md doesn't specify stage or methodology

**Symptoms:**
- No stage number in deal.md
- No methodology_adapter referenced
- Unclear what discovery questions to prioritize

**Solution:**
1. **Ask user:**
   - "What stage is this deal in?"
   - "Are you using Sandler methodology or default framework?"
2. **Default assumptions:**
   - Assume Stage 1 (Discover) if unspecified
   - Use Sandler Pain approach as default (qualification-focused)
3. **Add to provenance:**
   ```yaml
   assumptions: "Stage 1 assumed, Sandler Pain approach used"
   ```

---

### Problem: No stakeholders identified yet

**Symptoms:**
- Stakeholders section shows all TBD
- Don't know who will attend discovery call

**Solution:**
1. **In internal prep:** Add objective to identify stakeholders
   ```markdown
   ## Discovery Objectives
   1. Map stakeholder landscape (who needs to be involved?)
   2. [other objectives]
   ```

2. **In customer agenda:** Leave attendees generic
   ```markdown
   ## Attendees
   - **Your team:** Key stakeholders involved in [area]
   - **Our team:** [Names]
   ```

3. **In confirmation email:**
   ```
   "Please feel free to invite anyone from your team who should be part of this conversation."
   ```

---

### Problem: Discovery call is tomorrow (urgent prep)

**Symptoms:**
- User needs artifacts quickly
- No time for lengthy internal prep meeting

**Solution:**
1. **Prioritize:**
   - Generate customer agenda FIRST (user can send immediately)
   - Generate confirmation email SECOND
   - Internal prep agenda LAST (can be brief or skip if solo call)

2. **Streamline internal prep:**
   - Focus on 3-5 key questions only
   - Skip elaborate role assignments if solo
   - Highlight top 2 risks only

3. **Note in artifacts:**
   ```markdown
   Note: Expedited prep due to timing. Post-call debrief recommended to fill gaps.
   ```

---

### Problem: User wants Sandler approach but deal uses default methodology

**Symptoms:**
- Deal.md references default stage inventory
- User explicitly asks for Sandler pain discovery

**Solution:**
1. **Ask user:** "Should I switch this deal to Sandler methodology?"
2. **If yes:**
   - Update deal.md to reference Sandler adapter
   - Generate Sandler-aligned artifacts
   - Note in provenance: "Methodology changed to Sandler per user request"
3. **If no (just want Sandler questions):**
   - Use Sandler Pain Funnel in question plan
   - Keep deal in default methodology
   - Note: "Using Sandler questioning techniques within default framework"

---

### Problem: Discovery already happened, user wants retroactive prep

**Symptoms:**
- User asks for "discovery prep" but meeting already occurred
- Timestamps don't make sense (prep dated after call date)

**Solution:**
1. **Clarify intent:**
   - "It looks like the discovery call already happened. Do you want:"
     - A) Retroactive prep documentation (for records)?
     - B) Follow-up discovery prep for next meeting?
     - C) Post-discovery debrief instead of prep?

2. **If retroactive documentation:**
   - Generate artifacts but note in provenance:
     ```yaml
     note: "Retroactive documentation created post-meeting for record-keeping"
     ```
   - Adjust tone to past tense where appropriate

3. **If really needs post-discovery artifacts:**
   - Suggest using different skill or creating custom artifacts
   - Discovery prep skill is designed for pre-meeting, not post

---

### Problem: User provides meeting date but no year

**Symptoms:**
- "Prep discovery call for next Tuesday"
- Unclear what date to use in filenames

**Solution:**
1. **Infer from context:**
   - If today is 2025-11-11 and they say "next Tuesday," calculate date
   - Next Tuesday from 2025-11-11 is 2025-11-18

2. **Confirm with user:**
   - "I'm preparing artifacts for Tuesday, November 18, 2025. Is that correct?"

3. **Use calculated date in filenames:**
   - `2025-11-18_stage1_agenda__internal_prep.md`

## Tips for Effective Discovery Prep

### 1. Discovery is About Questions, Not Pitches
- Prepare 10-15 discovery questions
- Do NOT prepare slides or demos
- Sandler principle: "No free consulting" = no solutions until qualified

### 2. Pain Funnel is Your Best Tool
The 8-question sequence:
1. Tell me more about that...
2. Can you be more specific? Give me an example.
3. How long has that been a problem?
4. What have you tried to do about that?
5. And did that work?
6. How much do you think that has cost you?
7. **How do you feel about that?** ← Emotional commitment test
8. Have you given up trying to deal with the problem?

Use this for EACH pain point identified.

### 3. Personal Stakes = Qualification Signal
Always ask: "How does this impact YOU personally?"
- Good signs: Job security, bonus, promotion at risk
- Bad signs: "Not really my problem," "Just exploring"

### 4. Set Up-Front Contracts
Every customer agenda should include:
- Purpose explicitly stated
- Permission to say "it's not a fit"
- Expected outcomes defined
- Time boundaries clear

### 5. Prepare to Disqualify
Best discovery prep includes disqualification criteria:
- "If we hear X, we should walk away"
- "If pain intensity is below 7, disqualify"
- "If no urgency, disqualify"

### 6. Role Clarity Prevents Chaos
For multi-person calls (your team):
- One person leads (asks questions)
- One person takes notes
- Others observe or handle specific topics
- No stepping on each other

### 7. Tailor to Methodology
- **Sandler:** Focus on pain intensity, emotional commitment, qualification
- **Default:** Broader discovery, less aggressive disqualification
- **Custom:** Follow company playbook if provided

## Version History

- **1.0** (2025-11-11): Initial skill created during framework setup
  - Structured as proper Claude Code skill with YAML frontmatter
  - Expanded from 11-line spec to 600+ line comprehensive guide
  - Added Sandler Pain stage alignment
  - Included examples, troubleshooting, edge cases
  - Aligned with Anthropic best practices for agent skills

---

## Additional Resources

**Methodology Loading:**
- `Framework/System/methodology_loader.md` - Protocol for loading and using sales methodologies

**Templates and Stage Data:**
- `templates/` - Discovery question banks and agenda templates
- Framework templates: `Framework/Templates/agenda_internal.md`, `agenda_customer.md`
- Stage inventories: `sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md`

**Developer Guidance:**
- `Framework/System/DEVELOPER_GUIDE.md` - Implementation protocols and specs
