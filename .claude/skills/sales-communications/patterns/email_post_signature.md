# Email: Post-Signature

**Pattern**: email_post_signature
**Type**: Customer-facing email
**Timing**: Within 24 hours of contract signature
**Purpose**: Celebrate the win, transition to implementation, introduce CS team

---

## When to Use

Send this email to:
- Welcome new customers immediately after contract signature
- Celebrate expansion or upsell deal closure
- Acknowledge renewal signature and set up for next phase
- Transition relationship from sales to customer success
- Set expectations for implementation kickoff

**NOT for**:
- Verbal commitment without signature (use email_proposal_nudge)
- Ongoing implementation updates (CS team owns this)
- Upsell prospecting to existing customers (different pattern)
- Pre-signature "welcome aboard" messages (premature)

**Trigger Phrases**:
- "Post-signature email to {DEAL}"
- "Welcome {CUSTOMER}"
- "Congrats on signing {DEAL}"
- "Celebrate win with {DEAL}"
- "Transition {DEAL} to CS"

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for shared logic
2. Deal context from `sample-data/Runtime/Sessions/{DEAL}/deal.md`:
   - Signature date (must be confirmed)
   - Primary stakeholder name (who signed)
   - Deal type (new customer, expansion, renewal)
3. Customer Success team contact information:
   - CS Manager or CSM name
   - CS contact email
   - Implementation timeline (if known)

**OPTIONAL**:
- Email style corpus (for tone matching)
- Brand guidelines (for signature formatting)
- Onboarding timeline documentation
- Implementation plan template

**NOT NEEDED**:
- Detailed methodology qualification data
- Past meeting history (focus is forward)
- Competitive intelligence

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md)

Extract from deal.md:
- **Signature date**: When contract was signed (check History section)
- **Deal type**: New customer, expansion, renewal
- **Primary contact**: Decision maker who signed
- **Deal value**: Contract amount or expansion size
- **CS team assignment**: Who will manage implementation

**Example History Entry to Parse**:
```markdown
## History
- **2025-11-14**: Contract signed by Jim Selby, $150K annual subscription
- **2025-11-10**: Final pricing approved by Finance
```

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system for tone matching. Post-signature emails should be celebratory but professional.

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply signature formatting and any brand-specific onboarding messaging.

---

## Email Structure

### Subject Line
**Formula**: Celebratory but professional, 4-7 words

**Options by deal type**:
- **New customer**: "Welcome to {COMPANY}!" or "Excited to partner with {CUSTOMER}"
- **Expansion**: "Thrilled to expand our partnership" or "Excited for the next phase"
- **Renewal**: "Thank you for renewing!" or "Looking forward to another year"

### Body Structure (100-150 words)

**Components**:
1. Celebration (1-2 sentences)
2. Gratitude (1 sentence)
3. What happens next (2-3 sentences)
4. CS team introduction (1-2 sentences)
5. Your ongoing role (1 sentence)
6. Closing (warm, forward-looking)

**Template**:
```
Hi {FIRST_NAME},

{Celebration of partnership beginning/expanding}. {Expression of excitement about working together}.

{Gratitude for their trust/partnership}. {Acknowledgment of their team's collaboration}.

{What happens next: implementation timeline}. {CS team introduction by name}. {What to expect in next 24-48 hours from CS}.

{Your ongoing availability}. {Commitment to success together}.

{Closing},
{Signature}
```

### Example 1 (New Customer)
```
Subject: Welcome to [YourCompany]!

Hi Jim,

Congratulations on signing today! We're thrilled to officially welcome GlobalPharma to the [YourCompany] family and excited to help transform your quality management processes.

Thank you for trusting us with such a critical part of your operations. Your team's thoroughness during our discovery and demo process has set us up for a fantastic implementation.

Over the next 48 hours, Sarah Chen from our Customer Success team will reach out to schedule your implementation kickoff. Sarah will be your primary guide through onboarding and will work closely with you to ensure a smooth rollout. You can expect to go live within 6-8 weeks based on our initial scoping.

While Sarah owns implementation, I'm always here if you need anything. Looking forward to seeing GlobalPharma succeed with [YourCompany].

Congratulations again,
[Your Name]
Account Executive
your-email@yourcompany.com
```

### Example 2 (Expansion/Upsell)
```
Subject: Excited for the next phase together

Hi David,

Fantastic news on expanding to the Document Management module! I'm excited to see how this will streamline your entire product development workflow alongside your existing Quality module.

Thank you for continuing to invest in our partnership. It's been rewarding to watch your team embrace the platform over the past year.

Your existing CSM, Michael Torres, will reach out within 24 hours to schedule the expansion kickoff. Since you're already live with Quality, Michael expects the Document Management rollout to take 3-4 weeks. He'll coordinate training for the new users and ensure seamless integration.

I'll stay close to the process and check in periodically. Here's to making 2025 even more successful than 2024.

Best regards,
Anna Park
Account Executive
anna@yourcompany.com
```

### Example 3 (Renewal)
```
Subject: Thank you for renewing!

Hi Lisa,

Thank you for renewing your [YourCompany] subscription for another year! We're honored that PharmaTech continues to see value in our partnership.

Your team's success with the platform over the past two years has been impressive - from reducing audit prep time to streamlining CAPA management. We're committed to making year three even better.

Your CSM, Rachel Kim, will schedule a quarterly business review next month to align on goals for the coming year. She'll also share our 2025 product roadmap and gather your feedback on upcoming features.

I'll stay connected and check in quarterly. Please don't hesitate to reach out if you need anything from me.

Looking forward to another great year,
Tom Chen
Account Executive
tom@yourcompany.com
```

### Closing Options
**Celebratory**:
- "Congratulations again,"
- "Excited to get started,"
- "Welcome aboard,"
- "Looking forward to your success,"

**Professional**:
- "Best regards,"
- "Thank you again,"
- "Warm regards,"

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_post_signature
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - sample-data/Runtime/_Shared/style/{style_file}  # if loaded
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
---
```

### 2. Compose Email Body

**CRITICAL CONSTRAINTS**:
- Total body: 100-150 words (excluding subject and signature)
- Celebratory tone without being unprofessional
- Must include CS team introduction with name
- Must set implementation timeline expectations
- Reassure customer that AE stays involved (not abandoning)
- No selling, no upselling, no feature pitching
- Forward-looking and optimistic

### 3. Save File

**Path**: `sample-data/Runtime/Sessions/{DEAL}/artifacts/email_post_signature_{DATE}.md`

**Filename format**: `email_post_signature_2025-11-15.md`

---

## Error Handling

**Missing signature date**:
- Prompt user: "I don't see a signature date in the deal history. When was the contract signed?"
- DO NOT send post-signature email without confirmed signature

**Missing CS team assignment**:
- Use generic: "Our Customer Success team will reach out..."
- Prompt user: "Who is the assigned CSM for this account?"

**Missing implementation timeline**:
- Use vague timeframe: "in the coming days" or "shortly"
- Suggest: "Typical timeline is 4-8 weeks depending on scope"

**Deal type unclear**:
- Default to "new customer" messaging
- Prompt user: "Is this a new customer, expansion, or renewal?"

---

## Post-Signature Email Best Practices

**Celebrate together**: Use "we" language, acknowledge their decision, express genuine excitement.

**Smooth handoff**: Introduce CS by name, explain their role, set timing expectations for first contact.

**Set implementation expectations**: Provide realistic timeline, explain what happens next, reduce ambiguity.

**Stay accessible**: Reassure customer that AE remains involved, available for escalations or strategic questions.

**No selling**: This is not the time to upsell, cross-sell, or pitch additional features. Focus on what they bought.

**Timing matters**: Send within 24 hours of signature while excitement is fresh. Delay signals disorganization.

**Match tone to relationship**:
- New customers: More formal, professional celebration
- Renewals: Warmer, relationship-focused gratitude
- Expansions: Balance celebration with continuity

**What NOT to include**:
- Payment instructions (Finance/CS handles this)
- Detailed technical onboarding steps (CS owns this)
- Legal contract terms or clarifications (Legal/Sales Ops)
- Feature tutorials or training materials (CS provides)

---

## Common Scenarios

### Scenario 1: Multi-stakeholder signature
If multiple people signed (e.g., Legal, Finance, Champion), address the primary business contact but acknowledge the team effort:

```
Hi Jim,

Congratulations on finalizing the contract! Please pass along our thanks to Sarah in Legal and David in Finance for their partnership throughout the process.
```

### Scenario 2: Long sales cycle
If the deal took 6+ months, acknowledge the journey:

```
Hi Lisa,

After six months of collaboration, it's incredibly rewarding to see this partnership officially begin. Thank you for your patience and thoroughness throughout our evaluation.
```

### Scenario 3: Competitive win
If you displaced a competitor, focus on the future (not the competition):

```
Hi Tom,

Excited to earn your trust and partnership. We're committed to proving this was the right decision and delivering the value you expect.
```

### Scenario 4: Signature happened while AE was unavailable
Acknowledge the timing gap but maintain enthusiasm:

```
Hi David,

I just returned from PTO and wanted to personally welcome you to [YourCompany]. I apologize for not reaching out sooner - thank you for signing on Thursday!
```

---

## Example Output

```markdown
---
generated_by: sales-communications/email_post_signature
generated_on: 2025-11-15T18:45:00Z
deal_id: GlobalPharma
sources:
  - sample-data/Runtime/Sessions/GlobalPharma/deal.md
  - sample-data/Runtime/_Shared/style/ae_style_corpus.md
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md
---

**Subject**: Welcome to [YourCompany]!

Hi Jim,

Congratulations on signing today! We're thrilled to officially welcome GlobalPharma to the [YourCompany] family and excited to help transform your quality management processes.

Thank you for trusting us with such a critical part of your operations. Your team's thoroughness during our discovery and demo process has set us up for a fantastic implementation.

Over the next 48 hours, Sarah Chen from our Customer Success team will reach out to schedule your implementation kickoff. Sarah will be your primary guide through onboarding and will work closely with you to ensure a smooth rollout. You can expect to go live within 6-8 weeks based on our initial scoping.

While Sarah owns implementation, I'm always here if you need anything. Looking forward to seeing GlobalPharma succeed with [YourCompany].

Congratulations again,
[Your Name]
Account Executive
your-email@yourcompany.com
```

---

**End of Pattern: email_post_signature**
