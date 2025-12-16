# Email: Cold Outbound

**Pattern**: email_cold_outbound
**Type**: Prospecting email (new contacts, no prior relationship)
**Timing**: Initial outreach to new prospects
**Purpose**: Get first meeting, not sell product

---

## When to Use

Send this email for cold prospecting to:
- Generate new pipeline (outbound prospecting)
- Reach new contacts at existing accounts (expand into new divisions)
- Follow up on inbound signals (website visit, content download, event attendance)
- Re-engage old opportunities (6+ months since last contact)

**Trigger Phrases**:
- "Draft cold email to {prospect name} at {company}"
- "Create outbound email for {company}"
- "Write prospecting email"

---

## Prerequisites

**REQUIRED (Minimal)**:
1. Read `patterns/_common.md` for shared logic
2. Prospect information:
   - Company name
   - Contact name (first name at minimum)
   - Contact title (if available)
3. Email style corpus (4-tier loading per _common.md section 3)

**OPTIONAL** (improves personalization):
- Deal context from `sample-data/Runtime/Sessions/{PROSPECT}/deal.md` if exists (for warm outbound to existing accounts)
- Industry research (from knowledge base or web search)
- Recent company news (funding, expansion, leadership change)
- Mutual connections (LinkedIn)

---

## Content Generation Logic

### 1. Load Deal Context (Section 1 of _common.md) - CONDITIONAL

**If deal.md exists** (warm outbound to known prospect):
- Extract company information
- Check for previous interactions (History section)
- Look for mutual connections or prior context

**If NO deal.md exists** (true cold outbound):
- Skip deal context loading
- Use only information provided by user (company, name, title)
- Suggest running web research for personalization triggers

### 2. Load Email Style Corpus (Section 3 of _common.md)

Follow 4-tier system. **Cold email style critical**:
- Brevity (50-100 words max, not 200+)
- Personalization (specific to them, not generic)
- No fluff (every word earns its place)
- Clear CTA (one ask, easy to say yes)

### 3. Load Brand Guidelines (Section 2 of _common.md)

Apply company email formatting if available (signature primarily)

### 4. Research Personalization Triggers (RECOMMENDED)

**If user provides minimal info**, suggest gathering:
- Recent company news (funding, expansion, product launch)
- Industry pain points (from knowledge base)
- Mutual connections (LinkedIn)
- Recent content engagement (did they visit website, download resource?)

**Good triggers**:
- "Saw you're expanding into {region}" (growth signal)
- "Congrats on the Series B" (funding signal)
- "We helped {similar company} with {similar problem}" (relevance signal)
- "{Mutual connection} suggested I reach out" (trust signal)

**Avoid**:
- Generic "I was looking at your website..." (spam signal)
- "How are you?" (wastes words)
- Long company pitch (they don't care yet)

---

## Email Structure (COLD OUTBOUND)

### CRITICAL RULES for Cold Emails

**Length**: 50-100 words MAXIMUM (not including signature)
**Paragraphs**: 2-3 short paragraphs (2-3 sentences each)
**Ask**: ONE clear CTA (not multiple options)
**Tone**: Professional but human (not robotic)
**Personalization**: Specific to THEM (not generic spray-and-pray)

### Subject Line
**Formula**: Personalized + Intriguing + Non-salesy

**Approaches**:

**1. Mutual Connection**:
- "{Name} suggested I reach out"
- "Quick intro from {Mutual Connection}"

**2. Specific Trigger**:
- "Congrats on {recent news}"
- "{Similar Company} use case"
- "Expanding into {region}?"

**3. Direct Value**:
- "Reduce {pain point} by {quantified outcome}"
- "{Specific capability} for {their industry}"

**4. Question**:
- "Still using {incumbent tool}?"
- "{Pain point} challenges at {company}?"

**AVOID**:
- ❌ Generic: "Quick question", "Following up", "Touching base"
- ❌ Salesy: "Revolutionary platform", "Game-changing solution"
- ❌ Vague: "I have an idea for you", "Interested in learning more?"

**Examples**:
- ✅ "Reducing Salesforce reporting time (Acme Corp use case)"
- ✅ "Jane Chen suggested we connect"
- ✅ "Congrats on the Series B - reporting automation?"

### Opening Line
**Purpose**: Establish relevance in 1 sentence

**Formula**: {Personalization trigger} + {transition to their problem}

**Templates**:

**Mutual Connection**:
```
{Mutual connection} mentioned you're evaluating {category} solutions and suggested
we connect.
```

**Trigger Event**:
```
Saw {company} is expanding into {region} - we help {similar companies} scale
{specific process} during growth phases.
```

**Similar Customer**:
```
We recently helped {similar company in their industry} {quantified outcome} and
thought it might be relevant for {their company}.
```

**Direct Value**:
```
{Company} teams using {incumbent tool/process} typically spend {time/money} on
{manual task} - we automate that.
```

**Examples**:
```
✅ Jane Chen at Example Corp mentioned you're evaluating reporting tools and suggested we connect.

✅ Saw AcmeCorp is expanding into EMEA - we help healthcare companies scale their
Salesforce reporting during international growth.

✅ We recently helped a Fortune 500 pharma company reduce reporting overhead by 80%
and thought it might be relevant for AcmeCorp.
```

**AVOID**:
- ❌ "I hope this email finds you well" (generic, wastes words)
- ❌ "I was looking at your website..." (everyone says this)
- ❌ "My name is X and I work at Y..." (they can see your signature)

### Body Paragraph (1-2 sentences)
**Purpose**: Show you understand their world + hint at value

**Formula**: {Their likely pain point} → {How you solve it (high-level)}

**Template**:
```
{Title/role} I talk to often struggle with {specific pain point}. {Company} {does X}
to {outcome} without {common objection}.
```

**Example**:
```
VPs of Operations I talk to often struggle with manual Salesforce reporting eating
50+ hours/month of team time. Example Corp automates that end-to-end - real-time
dashboards without SQL or custom dev work.
```

**AVOID**:
- ❌ Long feature lists
- ❌ Company history ("Founded in 2010...")
- ❌ Generic value props ("We help companies improve efficiency")

### CTA Paragraph (1-2 sentences)
**Purpose**: ONE clear, low-friction ask

**Formula**: {Simple ask} + {Make it easy to say yes}

**Template**:
```
Worth a 15-minute conversation? {Suggest specific time or ask for availability}.
```

**Examples**:
```
✅ Worth a 15-minute call next week? I'm free Tuesday/Wednesday afternoon if that works.

✅ Would a quick 15-minute intro call make sense? Happy to share the {Similar Company}
case study if helpful.

✅ Open to a brief call? I can show you the {specific capability} in 10 minutes and
you can decide if it's relevant.
```

**AVOID**:
- ❌ Multiple CTAs ("Can we schedule a call? Or I can send more info? Or...")
- ❌ Vague asks ("Let me know if you're interested")
- ❌ Pushy language ("When can I get 30 minutes on your calendar?")

### Closing
**Keep it simple**:
- "Thanks," or "Best," or "Cheers,"
- Signature (from brand guidelines or default)

**AVOID**:
- ❌ "Looking forward to hearing from you!" (sounds desperate)
- ❌ "Let me know if you have any questions" (they won't)

---

## Full Email Structure (Template)

```
Subject: {Personalized trigger}

{Opening line - personalization + relevance}

{Body - their pain + your solution high-level (1-2 sentences)}

{CTA - one clear ask + make it easy (1-2 sentences)}

{Closing},
{Signature}
```

**Total length**: 50-100 words max

---

## Output Formatting

### 1. Generate Frontmatter (Section 5 of _common.md)

```yaml
---
generated_by: sales-communications/email_cold_outbound
generated_on: {ISO_8601_TIMESTAMP}
prospect_company: {company_name}
prospect_name: {contact_name}
sources:
  - sample-data/Runtime/Sessions/{PROSPECT}/deal.md  # if exists
  - sample-data/Runtime/_Shared/style/{style_file}  # if loaded
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
---
```

**Note**: Use `prospect_company` instead of `deal_id` since this is often sent before deal exists.

### 2. Compose Email Body

Follow structure above with actual personalization

### 3. Save File

**If deal.md exists**:
**Path**: `sample-data/Runtime/Sessions/{PROSPECT}/artifacts/email_cold_outbound_{DATE}.md`

**If NO deal.md**:
**Path**: `sample-data/Runtime/Sessions/_Prospects/email_cold_outbound_{COMPANY}_{DATE}.md`

---

## Error Handling

**Missing company name**:
- BLOCK: Prompt user "I need at least a company name and contact name to draft a cold email"

**Missing contact name**:
- Use generic salutation "team" or "all" (not ideal for cold email)
- Suggest user provides first name at minimum

**Missing personalization triggers**:
- Generate generic cold email structure
- Warn user: "This email will be more effective with personalization. Can you share: recent news, industry, mutual connections, or pain points?"

**No style corpus**:
- Use Tier 4 defaults (brief, professional, clear CTA)

---

## Cold Outbound Best Practices

### Response Rate Factors

**What increases response rates**:
- ✅ Brevity (50-100 words = 50% higher response than 200+ words)
- ✅ Personalization (specific to them, not templated)
- ✅ Relevance (solve a problem they actually have)
- ✅ Social proof (similar customer, mutual connection)
- ✅ Clear CTA (one specific ask)
- ✅ Mobile-friendly (short paragraphs, <100 words)

**What kills response rates**:
- ❌ Length (200+ words = <5% response rate)
- ❌ Generic templates ("I was looking at your website...")
- ❌ Feature dumps (nobody cares about your product yet)
- ❌ Vague asks ("Let me know if interested")
- ❌ Multiple CTAs (confuses recipient)
- ❌ Desperation ("Just following up for the 5th time...")

### Timing & Cadence

**Best send times** (B2B):
- Tuesday-Thursday, 8-10am or 2-4pm (local time to recipient)
- Avoid Monday mornings (inbox overload) and Friday afternoons (weekend mode)

**Follow-up cadence**:
1. Day 0: Initial email
2. Day 3: Bump (add value - share resource)
3. Day 7: Different angle (new personalization trigger)
4. Day 14: Breakup email ("Should I close your file?")

**Max touches**: 4-5 emails over 2 weeks, then stop (respect boundaries)

### Personalization Research (5 minutes per prospect)

**Quick research checklist**:
1. LinkedIn: Recent posts, mutual connections, job changes
2. Company website: Recent news, press releases, product launches
3. Funding databases (Crunchbase): Recent funding rounds
4. Industry trends: Is their industry going through change?

**Use this to**:
- Reference recent news in subject line
- Mention similar customers in opening line
- Show you understand their industry challenges

---

## Example Output (Mutual Connection)

```markdown
---
generated_by: sales-communications/email_cold_outbound
generated_on: 2025-11-14T11:30:00Z
prospect_company: AcmeCorp
prospect_name: Jane Smith
sources:
  - sample-data/Runtime/_Shared/style/ae_sarahchen_corpus.md
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md
---

**Subject**: Jane Chen suggested we connect

Hi Jane,

Jane Chen at Example Corp mentioned you're evaluating reporting automation tools and
suggested we connect.

VPs of Operations I talk to often struggle with manual Salesforce reporting eating
50+ hours/month of team time. We automate that end-to-end - real-time dashboards
without SQL or custom dev work.

Worth a 15-minute call next week? I'm free Tuesday/Wednesday afternoon if that works.

Best,
Sarah Chen
Senior Account Executive
Example Corp Solutions
sarah.chen@example.com | (555) 123-4567
```

---

## Example Output (Similar Customer)

```markdown
---
generated_by: sales-communications/email_cold_outbound
generated_on: 2025-11-14T11:30:00Z
prospect_company: GlobalPharma
prospect_name: Michael Rodriguez
sources:
  - sample-data/Runtime/_Shared/style/ae_sarahchen_corpus.md
---

**Subject**: Reducing Salesforce reporting time

Hi Michael,

Many enterprise pharma companies struggle with Salesforce reporting overhead—one
team cut their monthly admin time significantly with automated dashboards.

The biggest win is usually real-time executive visibility without waiting days
for custom reports.

Worth a quick 15-minute intro call to see if this applies to GlobalPharma?

Thanks,
Sarah Chen
Example Corp Solutions
sarah.chen@example.com | (555) 123-4567
```

---

## Example Output (Trigger Event - Expansion)

```markdown
---
generated_by: sales-communications/email_cold_outbound
generated_on: 2025-11-14T11:30:00Z
prospect_company: AcmeCorp
prospect_name: Jane Smith
sources:
  - sample-data/Runtime/_Shared/style/team_corpus.md
---

**Subject**: Congrats on EMEA expansion - reporting automation?

Hi Jane,

Saw AcmeCorp is expanding into EMEA - we help healthcare companies scale their
Salesforce reporting during international growth (15+ multi-region implementations).

Quick question: Still doing manual Salesforce reporting, or have you automated that?

Open to a 10-minute call next week if automation is on your radar.

Best,
Sarah Chen
Example Corp Solutions
sarah.chen@example.com
```

---

**End of Pattern: email_cold_outbound**
