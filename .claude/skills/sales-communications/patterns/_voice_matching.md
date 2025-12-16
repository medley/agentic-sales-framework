# Voice Matching & Verification

**Purpose**: Load AE-specific style corpus and verify generated/improved emails match the rep's natural voice.

**Used by**:
- Email generation patterns (to match voice)
- Email coaching pattern (to preserve voice)
- NOT used by agendas/briefings (different format requirements)

---

## When to Load

| Pattern Type | Load Voice Matching? | Rationale |
|--------------|---------------------|-----------|
| Customer-facing emails | YES | Voice matters for relationship |
| Internal emails | OPTIONAL | Less critical, but still helpful |
| Agendas | NO | Structured format, not voice-dependent |
| Briefings | NO | Objective summary, not personal voice |
| One-pagers | NO | Standardized format |

---

## AE Detection & Corpus Loading

### Step 1: Determine Active AE

**Detection order** (first match wins):
1. Check deal.md frontmatter for `owner: {name}` field (primary)
2. Check deal.md frontmatter for `assigned_ae: {name}` field (alternate)
3. Check brand_guidelines.md for `primary_ae: {name}` field
4. Check environment variable `$SALES_FRAMEWORK_AE`
5. DEFAULT: Use team corpus (Tier 2 fallback)

**Corpus path construction**:
```
sample-data/Runtime/_Shared/style/ae_{DETECTED_NAME}_corpus.md
```

**Example**:
- deal.md has `owner: welf`
- Load: `sample-data/Runtime/_Shared/style/ae_welf_corpus.md`

**Note**: The deal template uses `owner` field (line 4). Both `owner` and `assigned_ae` are recognized for backwards compatibility.

### Step 2: 4-Tier Corpus Loading

**Tier 1: Per-AE Corpus** (Highest Priority)
- **Path**: `sample-data/Runtime/_Shared/style/ae_{AE_NAME}_corpus.md`
- **Content**: Real emails written by this AE (15-20+ examples)
- **Use when**: AE has built their personal corpus

**Tier 2: Team Corpus** (Fallback)
- **Path**: `sample-data/Runtime/_Shared/style/team_corpus.md`
- **Content**: Best-practice emails from sales team
- **Use when**: No per-AE corpus available OR AE corpus missing

**Tier 3: Style Guide** (Documentation Fallback)
- **Path**: `sample-data/Runtime/_Shared/style/email_style_guide.md`
- **Content**: Documented email conventions and rules
- **Use when**: No corpus files available

**Tier 4: Hardcoded Defaults** (Last Resort)
- **Characteristics**:
  - Greeting: "Hi {FIRST_NAME}," (casual) or "Hello {FULL_NAME}," (formal)
  - Opening: Reference previous conversation
  - Body: 2-3 short paragraphs
  - CTA: One clear next step (question-based)
  - Closing: "Best regards," or "Thanks,"
  - Signature: AE name + title
- **Use when**: No files available at all

### Step 3: Graceful Fallback

**If AE corpus file does not exist**:
- Fall back to team corpus (Tier 2)
- **Do NOT error** or block generation
- Log in JSON frontmatter: `style_source: "team_corpus"`
- Continue normal generation/coaching workflow

**If team corpus also missing**:
- Fall back to style guide (Tier 3)
- Log: `style_source: "style_guide"`

**If all tiers missing**:
- Use Tier 4 defaults
- Log: `style_source: "defaults"`
- Email is functional, just not personalized

---

## Voice Verification (3 Checks)

**When to run**:
- After generating email (generation mode)
- After improving draft (coaching mode)
- One-pass verification only (no loops)

### Check 1: Paragraph Structure

**Compare**:
- Generated email paragraph count
- AE corpus average paragraph count

**AE corpus analysis**:
- Count paragraphs in 5-10 corpus examples
- Calculate average: 1 paragraph vs 2-3 short paragraphs

**Verification**:
- If generated matches corpus pattern → PASS
- If mismatch (e.g., 1 long paragraph when corpus shows 2-3 short) → FLAG

**Example**:
```
Corpus: Welf uses 2-3 short paragraphs consistently
Generated: Single 150-word paragraph
→ FLAG: Mismatch detected
```

### Check 2: Greeting & Closing

**Compare**:
- Generated greeting/closing
- AE corpus standard patterns

**AE corpus patterns to extract**:
- Greeting: "Hi {first_name}," vs "Hello {full_name}," vs "Hey {name},"
- Closing: "Best," vs "Thanks," vs "Best regards," vs "Talk soon,"

**Verification**:
- If generated matches corpus exactly → PASS
- If different greeting/closing → FLAG

**Example**:
```
Corpus: Welf always uses "Hi {first_name}," and "Best,"
Generated: "Hello Jim," ... "Best regards,"
→ FLAG: Greeting/closing mismatch
```

### Check 3: Banned Tone Markers

**Extract from AE corpus** (Section 1: Style Summary):
- Emojis: yes/no
- Hype language: avoid phrases like "I'm confident", "excited to", "thrilled"
- Em dashes: avoid/allow
- Exclamation points: frequency
- Contractions: prefer/avoid ("we're" vs "we are")

**Verification**:
- Scan generated email for banned markers
- If found → FLAG

**Example**:
```
Corpus: Welf's style notes say "never sound like AI, never use hyphens, em dash"
Generated: "I'm excited to share this—it's a game-changer!"
→ FLAG: Contains em dash (—), hype language ("excited", "game-changer")
```

---

## Voice Correction (One-Pass Rewrite)

**If any checks FLAG**:
1. Identify specific mismatches (paragraph structure, greeting, tone markers)
2. Rewrite email ONCE to match AE corpus preferences
3. **Do NOT enter multiple rewrite loops** - one correction pass only
4. Re-verify after rewrite (optional, for logging)

**Rewrite priorities**:
1. Fix greeting/closing first (easiest, highest impact)
2. Adjust paragraph structure (break long paragraph into 2-3 short)
3. Remove banned tone markers (delete hype, em dashes, etc.)

**Example rewrite**:
```markdown
# Before (flagged):
Hello Jim,

I'm excited to share the demo recap with you—here's everything we covered in yesterday's session, including the technical Q&A we discussed and next steps for the POC evaluation process, which I think will be really valuable for your team's decision-making timeline!

Best regards,
Welf

# After (corrected to match corpus):
Hi Jim,

Thanks for walking through the demo yesterday. Here's what we covered:

- Technical Q&A on SSO integration
- POC evaluation scope and timeline
- Next steps for your team's decision process

Worth a quick call this week to confirm the POC approach?

Best,
Welf
```

**Changes made**:
- Greeting: "Hello" → "Hi" (matches corpus)
- Structure: 1 long paragraph → 3 elements (2 short paragraphs + bullet list)
- Tone: Removed hype ("excited", "really valuable"), removed em dash
- Closing: "Best regards" → "Best" (matches corpus)
- CTA: Changed to question-based (matches corpus preference)

---

## Style Pattern Extraction (from Corpus)

When loading per-AE corpus, extract these patterns:

**From Style Summary section**:
- Preferred greeting
- Preferred closing
- Tone guidelines (what to avoid)
- Paragraph preference (count, length)
- Emoji usage (yes/no)
- Contraction usage (frequent/rare)

**From Example Emails**:
- Average word count per email type
- Sentence length distribution
- CTA style (question vs statement)
- Formatting preferences (bullets vs prose)

**Log extracted patterns** (optional, for debugging):
```yaml
style_patterns:
  greeting: "Hi {first_name},"
  closing: "Best,"
  paragraph_count: 2-3
  avg_word_count: 95
  tone_markers:
    avoid: ["excited", "thrilled", "game-changer", "em-dash"]
    prefer: ["direct", "calm", "specific details"]
  cta_style: "question-based"
```

---

## Error Handling

**Missing corpus file**:
- Fallback to next tier (team → style guide → defaults)
- Do NOT block generation
- Log in frontmatter: `style_source: "{tier_used}"`

**Malformed corpus file** (invalid YAML, missing sections):
- Parse what's available
- Fallback to defaults for missing sections
- Warn in frontmatter: `style_warning: "Corpus malformed, using partial data"`

**Voice verification fails repeatedly** (after rewrite still flagged):
- Accept the rewrite anyway (one pass only)
- Log in frontmatter: `voice_verification: "partial_match"`
- Do NOT block output

**Corpus has conflicting examples** (some use "Hi", others use "Hello"):
- Use most frequent pattern (majority wins)
- Or use most recent examples (last 5 emails)

---

## Output Frontmatter

After loading corpus and running verification, log these fields:

```yaml
---
# ... existing fields ...
style_source: "ae_welf_corpus" | "team_corpus" | "style_guide" | "defaults"
voice_verification: "pass" | "partial_match" | "not_run"
voice_corrections: # optional, if rewrite occurred
  - "greeting: Hello → Hi"
  - "structure: 1 paragraph → 2 paragraphs"
  - "removed: em-dash, hype language"
---
```

**Note**: These fields are optional. Only include if relevant.

---

## Usage in Patterns

**In generation patterns** (email_discovery_recap, email_demo_followup, etc.):

```markdown
### Step 2: Load Style Corpus

Follow patterns/_voice_matching.md:
1. Detect active AE (deal.md assigned_ae field)
2. Load corpus (4-tier system)
3. Extract style patterns (greeting, closing, paragraph count, tone)
4. Apply to email generation
5. Run voice verification (3 checks)
6. Rewrite once if needed
7. Log style_source in frontmatter
```

**In coaching pattern** (email_coach.md):

```markdown
### Step 3: Preserve Voice

Follow patterns/_voice_matching.md:
1. Load original drafter's corpus (AE who wrote draft)
2. Extract their style patterns
3. Improve draft while preserving:
   - Greeting/closing style
   - Paragraph structure preference
   - Tone markers (avoid banned phrases)
4. Run voice verification (ensure preservation)
5. Log voice_corrections if changes made
```

---

## Best Practices

**Corpus Quality**:
- Minimum 15-20 email examples per AE
- Include variety: cold, discovery, demo, proposal, internal
- Use recent emails (last 6-12 months)
- Redact sensitive info but keep structure/tone

**Voice Verification**:
- Run for customer-facing emails only
- Skip for internal emails if token budget tight
- One-pass correction (no recursive loops)
- Accept "good enough" (don't over-optimize)

**Corpus Updates**:
- Refresh every 6 months minimum
- Add new examples as AE's style evolves
- Flag as stale if >12 months since update

**New Rep Onboarding**:
- Start with team corpus (Tier 2)
- Build per-AE corpus over first 30-60 days
- Migrate from Tier 2 → Tier 1 as examples accumulate

---

**End of Voice Matching Reference**
