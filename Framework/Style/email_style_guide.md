
# Email Style Guide (Framework-Level)

This guide defines **universal, portable email rules** for the Agentic Sales Framework.

It is **not personal or company-specific** – it should work for any Enterprise SaaS AE.

Agents and skills (especially `email_generator`) should treat these as the
default rules when no user-specific style corpus is present.

---

## 1. Global Principles

1. **Clarity over cleverness**
   - Simple language
   - Avoid jargon and buzzwords
   - One main idea per email

2. **Brevity**
   - Standard modes: **75–125 words**
   - Exec-facing emails: up to **150 words** if necessary
   - No “wall of text” – use short paragraphs

3. **Tone**
   - Professional, confident, calm
   - No hype, no exaggeration, no hard pressure
   - Respectful of the reader’s time

4. **Formatting**
   - Short paragraphs (1–3 sentences)
   - Blank lines between paragraphs
   - No emojis
   - Minimal exclamation marks (ideally none)

5. **CTA (Call to Action)**
   - Every external email must have a clear CTA
   - Prefer **question-based**, low-friction CTAs:
     - “Would it be worth a brief call to explore this?”
     - “Are you open to a quick review of options?”
   - Internal emails may have checklist-style action items

---

## 2. Standard Structure by Mode

These are **generic patterns**. User-specific style/corpus may refine them.

### 2.1 Cold Outbound

**Goal:** Earn a short conversation, not sell the whole product.

**Structure:**
1. **Trigger** – Specific reason for reaching out
2. **Problem** – What this likely causes/risks
3. **Social Proof** – Who you’ve helped (anonymous or named)
4. **CTA** – Light, interest-based question

**Rules:**
- 75–110 words
- One clear problem, one outcome
- No generic “I hope this email finds you well”

---

### 2.2 Discovery Recap

**Goal:** Confirm understanding and next steps.

**Structure:**
1. Thank them + reminder of meeting context
2. 3–5 bullet points of what you heard (pains, goals)
3. Next steps (who does what by when)
4. CTA to confirm / correct

**Rules:**
- 90–130 words
- Use bullets for clarity
- Explicitly invite corrections: “If I missed anything, please let me know.”

---

### 2.3 Demo Recap

**Goal:** Anchor value shown and secure next milestone.

**Structure:**
1. Thanks + quick reminder of what you showed
2. 3–4 specific things that resonated / mattered
3. Risks or open questions identified
4. Clear next step (e.g., validation, additional stakeholders, decision discussion)

**Rules:**
- 90–130 words
- Reference outcomes, not features
- Anchor next milestone (“our next step is…”)

---

### 2.4 Exec Readout

**Goal:** TL;DR business case for VP/C-level.

**Structure:**
1. One-sentence TL;DR (pain → impact → outcome)
2. 2–3 bullets quantifying risk or opportunity
3. Proposed path / timeline
4. CTA around decision or sponsorship

**Rules:**
- 110–150 words
- Avoid technical detail; focus on business impact
- Respect hierarchy (don’t forward internal back-and-forth)

---

### 2.5 Proposal / Quote Follow-up

**Goal:** De-risk silence and clarify decision process.

**Structure:**
1. Brief reference to proposal/quote
2. Confirm they have everything needed
3. Ask about decision process & timeline
4. Offer to clarify or adjust

**Rules:**
- 75–120 words
- No guilt-tripping or “just bumping this”
- Emphasize helpfulness and clarity

---

### 2.6 Internal Prep / Alignment

**Goal:** Align internal team on context and objectives.

**Structure:**
1. TL;DR: deal + meeting purpose
2. Bullets: who’s attending and why it matters
3. Meeting objectives (2–3)
4. Ask for input / confirm roles

**Rules:**
- 90–140 words
- Use bullets and headings for scan-ability
- Explicitly assign owners where possible

---

## 3. Quality Checklist (For Any Email)

Before considering an email “done,” validate:

- [ ] Under 150 words (unless explicitly long-form)
- [ ] One clear CTA
- [ ] No emojis
- [ ] Minimal jargon
- [ ] Paragraphs are short and separated by blank lines
- [ ] Subject line is specific, not clickbait
- [ ] Recipient and context are correctly referenced

---

## 4. Interaction with Style Corpus

- If a **user-specific style corpus** exists (see `style_builder.md`),
  `email_generator` should:
  - Prefer phrasing patterns from the corpus
  - Prefer subject line formats from the corpus
  - Still enforce this guide’s structural rules

- If **no personal corpus** exists:
  - Use this guide + any generic examples in `email_style_corpus.md`.

This guide = **guardrails**. Corpus = **flavor and examples**.