# Prospecting System Glossary

*Canonical definitions for all system terminology*

---

## Core Concepts

### Account

A company targeted for outreach. An account exists in the prospecting system regardless of whether any contact has been made. Accounts are inputs to the system.

**Not to be confused with:** Opportunity (which requires engagement)

---

### Active Account

An account with an ongoing sales conversation. Active accounts have received a reply or booked a meeting. They belong in `01_Accounts/_Active/` and are outside the scope of the prospecting system.

**Prerequisite:** Reply or meeting from a contact

---

### Approved for Send

A prospecting state indicating a human has reviewed a rendered email and marked it ready for manual sending. This is the final state within the prospecting system.

**Does not mean:**
- Email was sent
- Opportunity exists
- Account is active

---

### Confidence Mode

A quality indicator assigned to each draft based on research signal strength:

| Mode | Definition |
|------|------------|
| **HIGH** | Strong, cited signals supporting personalization. Eligible for automatic rendering. |
| **MEDIUM** | Adequate signals but with caveats (ambiguity, staleness). Requires human review before rendering. |
| **LOW** | Insufficient signals for credible personalization. Not recommended for outreach. |

---

### Contact

An individual person at an account who may receive outreach. Contacts are discovered through ZoomInfo or provided in input data.

---

### Draft

An intermediate email artifact containing:
- Research context
- Selected angle and offer
- Draft sentences (not final copy)
- Quality metadata

Drafts exist in `prepared_for_rendering` state and require rendering to become final email text.

---

### Opportunity

A qualified sales conversation with expressed interest. Opportunities only exist after:
1. Email was sent (manually)
2. Recipient replied OR meeting was booked

**Key rule:** No opportunity exists without engagement. Prospecting does not create opportunities.

---

### Persona

A role category used to tailor messaging:

| Persona | Typical Titles |
|---------|---------------|
| **Quality** | VP Quality, Director QA, Quality Manager |
| **Ops** | VP Operations, Director Manufacturing |
| **IT** | CIO, IT Director, VP Technology |
| **Regulatory** | VP Regulatory, Director Regulatory Affairs |

---

### Prospecting

Pre-opportunity outreach activity. Prospecting includes:
- Account research
- Contact discovery
- Email drafting
- Review and approval

Prospecting ends when a reply is received. Everything before that point is prospecting.

---

### Rendered

A prospecting state indicating final email text has been generated and validated. Rendered emails have passed quality checks and are ready for human review.

**Rendered ≠ Approved:** Rendering is automatic; approval requires human action.

---

### Warning

A flag indicating a potential issue with a draft:

| Warning | Meaning |
|---------|---------|
| `stale_signals` | Research data is older than threshold |
| `ambiguous_persona` | Title matched multiple role categories |
| `low_signal_count` | Fewer signals than tier requires |
| `no_company_signals` | No company-level intelligence found |
| `regulatory_persona` | Contact requires extra care |

Warnings inform review decisions but do not automatically block progress (except regulatory).

---

## States

### prepared_for_rendering

First prospecting state. Indicates:
- Research complete
- Email plan built
- Context quality written
- Not yet final text

**Next state:** `rendered_validated` (after rendering)

---

### rendered_validated

Second prospecting state. Indicates:
- Final email text generated
- Validation checks passed
- Ready for human review

**Next state:** `approved_for_send` (after human approval)

---

### approved_for_send

Final prospecting state. Indicates:
- Human reviewed and approved
- Ready for manual sending
- Still in prospecting (not an opportunity)

**Next step:** Human sends email outside the system

---

### review_required

A flag (not a state) indicating human review is needed before proceeding. Triggered by:
- MEDIUM confidence
- Regulatory persona
- Specific warnings

Items with `review_required: true` are blocked from automatic rendering.

---

## Artifacts

### email_context.json

Full context file for rendering. Contains:
- Research data
- Prospect brief
- Email plan with draft sentences
- Contact information
- Context quality metadata

---

### email.md

Human-readable email plan (not final copy). Shows:
- Metadata
- Subject candidates
- Draft sentences
- Cited signals

---

### context_quality.json

Quality metadata for a draft. Contains:
- Confidence mode
- Signal counts
- Freshness data
- Warnings

---

### render_status.json

Outcome of rendering. Contains:
- Success/failure
- Best variant
- Validation results
- Repair attempts

---

### outbound_run.json / outbound_run.md

Run-level dashboard showing:
- All accounts processed
- All contacts and their states
- Summary statistics
- Skipped accounts and reasons

---

## Folders

### 02_Prospecting/

Root folder for all prospecting work. Contains:
- Input files
- Agent-generated artifacts
- Run logs

**Rule:** All prospecting artifacts belong here until an opportunity exists.

---

### 02_Prospecting/agent-prospecting/

System-generated output folder. Contains:
- Per-company draft folders
- Run dashboards
- Caches

---

### 01_Accounts/_Active/

Folder for active opportunities only. Contains accounts where:
- Email was sent
- Reply was received OR meeting was booked

**Rule:** Nothing moves here during prospecting. Only after engagement.

---

## Actions

### Render

Generate final email text from draft sentences. Includes:
- Text assembly
- Validation checks
- Repair attempts (if needed)

Rendering is automatic for HIGH confidence; blocked for MEDIUM/LOW.

---

### Approve

Human action marking a rendered email as ready to send. Does not:
- Send the email
- Create an opportunity
- Move files to 01_Accounts

---

### Promote (Deprecated Meaning)

In this system, "promote" means marking an item as approved within prospecting. It does **not** mean:
- Moving to opportunity status
- Copying to `01_Accounts/_Active/`
- Creating a deal

**Correct usage:** "Promote to approved_for_send"
**Incorrect usage:** "Promote to opportunity"

---

### Send

Manual action by human, outside this system. The prospecting system never sends emails.

---

## Gates

### Render Gate

Controls which items can be rendered automatically:

| Confidence | Gate Status |
|------------|-------------|
| HIGH | Pass |
| MEDIUM | Block (requires review) |
| LOW | Block (hard) |

---

### Promotion Gate

Controls which items can be approved:

| Condition | Gate Status |
|-----------|-------------|
| Rendered + validated | Pass |
| Review warnings present | Pass with flag |
| Regulatory persona | Block (requires explicit approval) |

---

## Execution

### CLI Mode

Execution without API calls. Uses deterministic templates and rules. Fastest option for batch processing.

---

### Headless Mode

Execution with optional API calls. Uses LLM when available, falls back to deterministic otherwise. Default for automation.

---

### Deterministic Fallback

Behavior when LLM is unavailable:
- Angle scoring uses rules
- Email uses template sentences
- Subjects use candidates from rules
- Quality is maintained; style may be less varied

---

## Key Rules (Summary)

1. **Prospecting ≠ Opportunity:** No opportunity exists without a reply
2. **Approved ≠ Sent:** Approval is permission to send, not sending
3. **01_Accounts is sacred:** Only active deals belong there
4. **Agents don't send:** All sending is manual, by humans
5. **Confidence ≠ Correctness:** HIGH confidence still needs human judgment
