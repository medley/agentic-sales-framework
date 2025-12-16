# Email: Improve Draft (Universal Coaching)

**Pattern**: email_coach
**Type**: Email coaching (improvement mode)
**Purpose**: Strengthen user's draft email while preserving their voice and intent

---

## When to Use

Route to this pattern when:

**Draft Provided**:
- User message contains email-like text block (greeting + body + sign-off)

**OR Coaching Verbs Used**:
- "improve this email"
- "review my draft"
- "make this better"
- "tighten this up"
- "shorten this"
- "lengthen this"
- "make this more formal"
- "make this more casual"

**Routing handled by**: SKILL.md (don't duplicate logic here)

---

## NOT for

- **Generating emails from scratch** → Use email_discovery_recap, email_demo_followup, etc.
- **Creating agendas** → Use agenda_customer or agenda_internal
- **Deal coaching** → Use coach skill
- **Simple grammar fixes** → User can use base Claude for that

This pattern is for **substantive improvement** while **preserving voice**.

---

## Coaching Guardrails (CRITICAL)

When improving drafts, you MUST:

✅ **Preserve**:
- Sender's intent and message purpose
- Any explicit commitments, dates, or promises made
- Overall length (same ballpark unless user explicitly asks for shorter/longer)
- User's greeting and closing style (unless clearly off vs their corpus)
- Paragraph structure preference (from corpus: 1 long vs 2-3 short)

❌ **Do NOT**:
- Invent new promises, offers, or stakeholders
- Add commitments not in original draft
- Change the fundamental message or tone
- Over-engineer simple messages into complex structures
- Remove specificity user included (dates, names, numbers)
- Make it sound like a different person wrote it

**Example of violation**:
```markdown
# User's draft:
Hi Jim, looking forward to seeing you next week at the onsite.

# BAD coaching (adds new commitments):
Hi Jim,

Looking forward to seeing you next week at the onsite. I'll bring technical
documentation, product samples, and our pricing proposal for your review.
Our team of 3 will arrive at 9am to set up the demo environment.

# GOOD coaching (preserves intent):
Hi Jim,

Looking forward to meeting with you next week during the onsite. Let me know
if anything changes on your side.

Best,
Welf
```

---

## Prerequisites

**REQUIRED**:
1. Read `patterns/_common.md` for deal context loading
2. Read `patterns/_voice_matching.md` for style corpus and verification
3. Extract draft email text from user message OR read from provided file path

**OPTIONAL**:
- Deal context from deal.md (helpful for adding specific names/dates if missing)
- Brand guidelines (for signature formatting)
- Methodology stage guide (to align with stage best practices)

---

## Improvement Workflow

### Step 1: Parse Draft Email

**Extract from user's draft**:
- Subject line (if provided)
- Recipient name/role (if mentioned)
- Greeting style ("Hi" vs "Hello" vs "Hey")
- Body content (key points, structure)
- Closing style ("Best" vs "Thanks" vs "Best regards")
- Signature (if included)

**Identify email type** (optional, for context):
- Discovery recap?
- Demo follow-up?
- Cold outbound?
- Simple confirmation?
- Unknown/generic

### Step 2: Load Deal Context (Optional)

**If deal mentioned or implied**:
- Load deal.md from sample-data/Runtime/Sessions/{DEAL}/
- Extract:
  - Stakeholder names (in case user wrote "Jim" but full name is "Jim Selby")
  - Recent history (to add specific references if user's draft lacks them)
  - D7 tasks (to suggest next steps if draft doesn't include them)

**If no deal context**:
- Proceed with draft improvement using only provided text
- Focus on clarity, brevity, grammar

### Step 3: Load Style Corpus

**Follow `patterns/_voice_matching.md`**:
1. Detect active AE (from deal.md assigned_ae OR user context)
2. Load corpus (4-tier system: per-AE → team → style guide → defaults)
3. Extract style patterns:
   - Greeting preference
   - Closing preference
   - Paragraph count (1 long vs 2-3 short)
   - Tone markers (what to avoid: hype, emojis, etc.)
   - Average word count
   - CTA style (question vs statement)

**Graceful fallback**:
- If no corpus → use draft's existing style as baseline
- Preserve user's original greeting/closing patterns

### Step 4: Analyze Draft Quality

**Check for**:
- [ ] **Clarity**: Is message clear and easy to understand?
- [ ] **Brevity**: Is it concise without losing key information?
- [ ] **Completeness**: Does it include necessary elements?
  - Recipient acknowledgment
  - Context/reason for email
  - Specific references (dates, names, topics)
  - Clear next step or CTA
- [ ] **Tone**: Professional and appropriate for relationship?
- [ ] **Grammar**: Spelling, punctuation, sentence structure correct?
- [ ] **Voice alignment**: Does it match AE's corpus style?

**Identify gaps**:
- Missing recipient name (use generic "team" if unavailable)
- No specific next step (vague "let me know" vs concrete "Worth a call Tuesday?")
- Too wordy (can be tightened 20-30% without losing meaning)
- Too brief (missing context that would help recipient)
- Off-voice (doesn't match AE's natural style)

### Step 5: Generate Improvements

**Improvement priorities** (in order):
1. **Grammar/spelling** - Fix obvious errors first
2. **Clarity** - Rewrite confusing sentences
3. **Brevity** - Reduce word count if overly verbose
4. **Specificity** - Add specific references from deal context if helpful
5. **CTA** - Strengthen call-to-action if weak or missing
6. **Voice alignment** - Match AE corpus (greeting, structure, tone)

**Track changes made**:
```yaml
edit_history:
  - "Fixed typo: 'recieve' → 'receive'"
  - "Reduced word count: 180 → 115 words"
  - "Added specific next step: 'Worth a call Tuesday?' instead of 'let me know'"
  - "Matched AE greeting: 'Hello' → 'Hi' (per corpus)"
  - "Split into 2 paragraphs (matches corpus preference)"
```

**Rules for improvements**:
- Keep overall length in same ballpark (±20% acceptable)
- If user said "make this shorter", reduce word count 30-50%
- If user said "make this longer", expand context/details 30-50%
- If user said "make this more formal", adjust greeting/tone ("Hi" → "Hello", remove contractions)
- If user said "make this more casual", adjust tone ("Hello" → "Hi", add contractions)

### Step 6: Voice Verification

**Follow `patterns/_voice_matching.md`**:
1. Run 3 verification checks (paragraph structure, greeting/closing, tone markers)
2. If mismatches detected, rewrite ONCE to better match corpus
3. Do NOT enter multiple rewrite loops
4. Log voice_corrections in frontmatter

**Preserve user's original voice when**:
- Draft already matches corpus well
- User explicitly requested different style ("make this more formal" overrides corpus)
- No corpus available (use draft style as baseline)

---

## Output Format

### Frontmatter

```yaml
---
generated_by: sales-communications/email_coach
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name}  # if deal context used
mode: coaching  # optional field
draft_version: {original_version + 1}  # optional, increment if provided
edit_history:  # optional, list changes made
  - "{change description}"
  - "{change description}"
style_source: "ae_welf_corpus" | "team_corpus" | "defaults"  # optional
voice_verification: "pass" | "partial_match"  # optional
voice_corrections:  # optional, if voice rewrite occurred
  - "greeting: Hello → Hi"
  - "structure: 1 paragraph → 2 paragraphs"
status: "success" | "missing_prereqs"  # optional, machine-readable status
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md  # if used
  - sample-data/Runtime/_Shared/style/{corpus_file}  # if loaded
---
```

**Note**: Optional fields may be omitted if not relevant. Do not include empty fields.

### Improved Email

```markdown
**Subject**: {improved subject line, if provided in draft}

{improved email body}
```

### Change Log (Summary)

```markdown
---

**CHANGES MADE:**
- {list substantive improvements in plain language}
- {not just typo fixes, focus on structure/tone/clarity changes}

**VOICE VERIFICATION:** {Pass/Partial/Not Run}
```

### Diff Output (Optional, if helpful)

```diff
- Hi Jane, I hope this email finds you well.
+ Hi Jane,

- We had a great conversation last week about your reporting challenges and I wanted to follow up...
+ Thanks for walking through your reporting challenges last week. Here's what we discussed:
```

---

## Error Handling

**No draft provided**:
- Output short message: "Please provide a draft email to improve. Paste the email text in your message."
- JSON: `status: "missing_prereqs"`

**Draft is not an email** (e.g., just a sentence fragment):
- Attempt improvement anyway (fix grammar, suggest structure)
- Or ask: "This doesn't look like a complete email. Did you want me to draft one from scratch instead?"

**Deal context missing** (user mentioned company but deal.md not found):
- Proceed with draft improvement using only provided text
- Note in sources: "Deal context not available"

**Corpus missing**:
- Use team corpus or defaults (graceful fallback)
- Log: `style_source: "team_corpus"` or `"defaults"`

---

## Example Interactions

### Example 1: Simple Draft Improvement

**User provides**:
```
Improve this email:

Hi Jim, I hope this email finds you well. We had a great conversation last week
about your reporting challenges and I wanted to follow up with some resources
and next steps to keep the momentum going. Let me know if you have any questions.

Thanks,
Welf
```

**Pattern output**:
```yaml
---
generated_by: sales-communications/email_coach
generated_on: 2025-11-15T16:45:00Z
mode: coaching
edit_history:
  - "Removed filler: 'I hope this email finds you well'"
  - "Made opening more direct: referenced specific topic"
  - "Strengthened CTA: question-based instead of 'let me know'"
  - "Reduced word count: 62 → 48 words"
style_source: "ae_welf_corpus"
voice_verification: "pass"
---

**Subject**: Re: Reporting challenges discussion

Hi Jim,

Thanks for walking through your reporting challenges last week. Here's what we discussed and next steps:

[Specific details would go here if deal context available]

Worth a quick call this week to confirm the approach?

Best,
Welf
```

### Example 2: User Requests "Make This Shorter"

**User provides**:
```
Make this shorter:

Hi Sarah,

I wanted to reach out and follow up on our conversation from last Tuesday's discovery
call where we discussed your team's challenges with the current manual reporting
process and how you're looking to improve efficiency and reduce the time your team
spends on data gathering and report generation, which is currently taking about
20 hours per week according to what you mentioned.

Best regards,
Welf
```

**Pattern output**:
```yaml
---
generated_by: sales-communications/email_coach
mode: coaching
edit_history:
  - "Reduced word count: 78 → 32 words (59% reduction)"
  - "Consolidated run-on sentence into concise bullet recap"
  - "Matched closing: 'Best regards' → 'Best' (per corpus)"
style_source: "ae_welf_corpus"
voice_verification: "pass"
---

Hi Sarah,

Thanks for walking me through your reporting challenges on Tuesday's call:

- Manual process takes ~20 hours/week
- Team wants faster data gathering and report generation

Worth a follow-up on how we can help?

Best,
Welf
```

### Example 3: Voice Preservation (User's Style Different from Corpus)

**User provides**:
```
Review this draft:

Hello James,

I wanted to express my sincere gratitude for taking the time to meet with our team
yesterday. Your insights regarding the compliance challenges were most illuminating.

I shall forward the technical documentation we discussed forthwith.

With warm regards,
Welf
```

**Pattern recognizes**: User's draft is more formal than Welf's corpus (which is casual/direct)

**Pattern output**:
```yaml
---
generated_by: sales-communications/email_coach
mode: coaching
edit_history:
  - "Preserved formal tone (user's choice, overrides corpus)"
  - "Simplified 'forthwith' to 'this week' for clarity"
  - "No voice corrections (user's style intentionally formal)"
style_source: "ae_welf_corpus"
voice_verification: "partial_match"  # Corpus is casual, draft is formal
voice_note: "Draft is more formal than AE corpus; preserved user's intentional tone"
---

Hello James,

Thank you for meeting with our team yesterday. Your insights on the compliance
challenges were very helpful.

I'll forward the technical documentation we discussed by end of week.

With warm regards,
Welf

---

**CHANGES MADE:**
- Simplified language ("forthwith" → "by end of week") for clarity
- Preserved formal tone (intentionally different from AE corpus)

**VOICE VERIFICATION:** Partial match (draft more formal than corpus, preserved intentionally)
```

---

## Best Practices

**Coaching Mindset**:
- Improve, don't rewrite from scratch
- Preserve user's original voice and intent
- Make targeted improvements (grammar, clarity, CTA)
- Don't over-engineer simple messages

**Voice Preservation**:
- Load AE corpus to understand their natural style
- But prioritize user's draft style if different (they chose it intentionally)
- Corpus is a guide, not a straitjacket

**Specificity**:
- If deal context available, add specific references (stakeholder names, dates)
- But don't invent details not in draft or deal.md
- Better to keep generic than hallucinate

**Brevity**:
- Most drafts can be tightened 15-25% without losing meaning
- But don't reduce so much that message becomes terse or rude

**One-Pass Improvement**:
- Make improvements in single pass
- Don't recursively optimize
- Good enough is good enough

---

**End of Pattern: email_coach**
