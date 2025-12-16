# Template Override Protocol

**Purpose**: Define priority hierarchy when pattern suggestions conflict with AE style corpus or deal context.

**Core Principle**: **Corpus wins over pattern template** when conflict occurs.

---

## Priority Hierarchy

When generating or improving emails, follow this priority order (highest to lowest):

### 1. **AE Style Corpus** (Highest Priority)
**Source**: `sample-data/Runtime/_Shared/style/ae_{NAME}_corpus.md`

**Why highest**: This represents the AE's actual voice from real emails they've sent. It's the most authentic representation of how they naturally communicate.

**What it controls**:
- Greeting style ("Hi" vs "Hello" vs "Hey")
- Closing style ("Best" vs "Thanks" vs "Best regards")
- Paragraph structure (1 long vs 2-3 short)
- Word count preferences (brief vs detailed)
- Tone markers (what to avoid: emojis, hype language, em dashes)
- Contraction usage ("we're" vs "we are")
- CTA style (question-based vs statement-based)

**Override rule**: If pattern says "single paragraph" but corpus shows "2-3 short paragraphs", use 2-3 short paragraphs.

---

### 2. **Deal Context** (Deal-Specific)
**Source**: `sample-data/Runtime/Sessions/{DEAL}/deal.md`

**Why second**: Specific stakeholder preferences or relationship history should override generic patterns.

**What it controls**:
- Stakeholder names and titles (use actual names from deal.md)
- Relationship tone (formal for new contact, casual for long relationship)
- Previous email style (if user has sent emails to this contact before)
- Industry-specific language (healthcare vs manufacturing vs tech)

**Example**: If deal.md shows contact prefers formal communication, override AE's casual corpus for this specific email.

---

### 3. **Pattern Suggestions** (Best Practices)
**Source**: Individual pattern files (email_discovery_recap.md, etc.)

**Why third**: Patterns encode sales methodology best practices and proven structures.

**What it controls**:
- Email structure (opening, body, CTA, closing)
- Content elements to include (recap, Q&A, next steps, resources)
- Word count targets (80-120 words for simple, 125-150 for demo follow-up)
- Methodology alignment (MEDDPICC fields, Sandler pain discovery)

**Override rule**: Patterns are **suggestions**, not requirements. If corpus or deal context conflicts, defer to higher priority.

---

### 4. **Team Corpus** (Company Standards)
**Source**: `sample-data/Runtime/_Shared/style/team_corpus.md`

**Why fourth**: Company-wide standards apply when no AE-specific corpus exists.

**What it controls**:
- Company tone guidelines
- Industry norms for your company's sector
- Legal/compliance language requirements
- Brand voice consistency

**Use when**: No per-AE corpus available (new rep, or rep hasn't built corpus yet)

---

### 5. **Tier 4 Defaults** (Lowest Priority)
**Source**: Hardcoded in `_common.md` or `_voice_matching.md`

**Why lowest**: Generic fallback when no other sources available.

**What it controls**:
- Basic professional email format
- Standard greetings/closings
- Generic structure

**Use when**: No corpus, no deal context, no team standards available

---

## Resolution Examples

### Example 1: Paragraph Structure Conflict

**Scenario**:
- **Pattern says**: "Body (Single Paragraph)"
- **AE corpus shows**: Welf consistently uses 2-3 short paragraphs

**Resolution**:
- **Use**: 2-3 short paragraphs
- **Reason**: Corpus (Priority 1) beats pattern (Priority 3)

**Implementation**:
```markdown
# Pattern file would say:
Body: Default to single paragraph unless AE corpus prefers multiple short paragraphs
```

---

### Example 2: Greeting Style Conflict

**Scenario**:
- **Pattern suggests**: "Hi {first_name},"
- **AE corpus shows**: Welf uses "Hello {full_name}," for executive contacts

**Resolution**:
- **Use**: "Hello {full_name},"
- **Reason**: Corpus (Priority 1) beats pattern (Priority 3)

---

### Example 3: Word Count Conflict

**Scenario**:
- **Pattern says**: "Target length: 125-150 words"
- **AE corpus shows**: Average 95 words across all email types

**Resolution**:
- **Use**: ~95 words (shorter than pattern target)
- **Reason**: Corpus (Priority 1) beats pattern (Priority 3)

**Acceptable range**: 75-115 words (±20% of corpus average is fine)

---

### Example 4: Deal Context Overrides Corpus

**Scenario**:
- **AE corpus**: Welf uses casual tone ("Hi", contractions, brief)
- **Deal context**: First email to C-level exec at Fortune 500 (per deal.md notes)

**Resolution**:
- **Use**: More formal tone for this specific email
- **Reason**: Deal context (Priority 2) can override corpus (Priority 1) for relationship-specific needs

**Implementation**:
```markdown
# Pattern checks deal context:
If deal.md indicates executive stakeholder or first contact:
  - Use more formal greeting ("Hello" instead of "Hi")
  - Reduce contractions
  - Be more concise (respect their time)
```

---

### Example 5: Team Corpus When AE Corpus Missing

**Scenario**:
- **Pattern says**: "Use AE corpus for style"
- **AE corpus**: File doesn't exist (new rep)

**Resolution**:
- **Use**: Team corpus (Priority 4)
- **Reason**: Graceful fallback when Priority 1 unavailable

**Log in frontmatter**: `style_source: "team_corpus"`

---

### Example 6: Everything Conflicts - Methodology Wins

**Scenario**:
- **Pattern says**: "Include MEDDPICC qualification questions"
- **AE corpus**: Welf's emails rarely include explicit qual questions
- **Conflict**: Best practices vs personal style

**Resolution**:
- **Compromise**: Include qualification questions BUT phrase them in Welf's direct, casual style
- **Reason**: Balance methodology requirements (Priority 3) with voice (Priority 1)

**Example output**:
```markdown
# Not Welf's style (too formal):
"Could you please share your thoughts on the decision-making process and timeline?"

# Welf's style (direct, casual):
"How are you planning to make the decision, and what's the timing look like?"
```

---

## Special Cases

### Case 1: User Explicitly Requests Different Style

**Scenario**: User says "make this more formal" but corpus is casual

**Resolution**:
- **User request** becomes Priority 0 (highest)
- Override corpus for this specific email
- Log: `voice_note: "User requested formal tone, overriding corpus"`

---

### Case 2: Legal/Compliance Requirements

**Scenario**: Company requires specific disclaimers or legal language

**Resolution**:
- **Brand guidelines** (legal section) becomes Priority 0 (highest)
- Add required disclaimers even if not in corpus
- Maintain AE voice for rest of email

---

### Case 3: Customer-Stated Preferences

**Scenario**: Deal notes say "Customer prefers bullet points, no prose"

**Resolution**:
- **Deal context** (Priority 2) overrides corpus structure
- Use bullets even if AE typically uses paragraphs
- Adapt to customer's stated preference

---

## Implementation Guidelines

### For Pattern Files

**Add Style Alignment Section**:
```markdown
### Style Alignment

- Use these structure suggestions by default
- If AE corpus shows different preferences (paragraph count, length, tone), follow corpus instead
- **Corpus wins when conflict occurs**
- See references/template_override_protocol.md for full priority hierarchy
```

**Soften Hard Requirements**:
```markdown
# Instead of:
Body (Single Paragraph)  # REQUIRED

# Write:
Body: Default to single paragraph unless AE corpus prefers multiple short paragraphs
```

**Add Target Ranges (Not Exact Counts)**:
```markdown
# Instead of:
Word count: 125 words

# Write:
Target length: 125 words (acceptable range: 100-150)
If AE corpus averages significantly different, match corpus instead
```

---

### For Voice Matching

When loading corpus:
1. Extract style patterns (greeting, closing, paragraph count, tone)
2. Compare to pattern suggestions
3. If conflict detected, **use corpus**
4. Log decision in frontmatter: `style_override: "Used 2 paragraphs (corpus) instead of 1 (pattern)"`

---

### For Error Handling

**If corpus and pattern both missing**:
- Fall back to team corpus (Priority 4)
- Then Tier 4 defaults (Priority 5)
- **Never block** email generation due to missing corpus

**If corpus has conflicting examples**:
- Use most frequent pattern (majority wins)
- OR use most recent examples (last 5 emails)
- Tie-breaker: Default to pattern suggestion

---

## Conflict Resolution Checklist

When pattern and corpus conflict:

- [ ] **Identify conflict**: What specific element conflicts? (greeting, structure, word count, tone)
- [ ] **Check priority**: Which source has higher priority? (AE corpus usually wins)
- [ ] **Apply override**: Use higher priority source
- [ ] **Log decision**: Record in frontmatter why override occurred
- [ ] **Validate output**: Does final email feel natural for this AE?

---

## FAQ

**Q: Should patterns ever override corpus?**
A: Rarely. Only when:
  - User explicitly requests different style
  - Legal/compliance requires specific language
  - Methodology best practice is critical (e.g., MEDDPICC qualification in discovery)
  - Even then, try to phrase in AE's natural voice

**Q: What if AE corpus has bad examples (too verbose, poor CTAs)?**
A: Corpus represents AE's current style. If you want to improve it:
  - Coach the AE separately (use learning loop in Phase 4)
  - Update corpus with better examples
  - Don't silently override their voice in generated emails

**Q: How to handle multiple AEs with different styles on same deal?**
A: Use assigned_ae field in deal.md to determine which corpus to load.
  - If email is from Welf → use ae_welf_corpus.md
  - If email is from Maria → use ae_maria_corpus.md

**Q: Should team corpus ever override AE corpus?**
A: No. AE corpus (Priority 1) always beats team corpus (Priority 4).
Team corpus is only used when AE corpus doesn't exist.

---

**Summary**:
1. **AE corpus wins** in most conflicts
2. **Deal context** can override for relationship-specific needs
3. **Patterns are suggestions**, not rigid requirements
4. **User requests** override everything
5. **When in doubt, preserve AE's natural voice**

---

**End of Template Override Protocol**
