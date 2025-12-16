# Confidence Modes

Confidence modes control how personalized an email can be based on available evidence. This is a **safety mechanism** that prevents making claims without sufficient backing data.

---

## How Modes Are Assigned

Confidence mode is **automatically assigned** based on the number of cited signals. It **cannot be overridden by the user**.

| Cited Signals | Mode Assigned | Rationale |
|---------------|---------------|-----------|
| 3+ signals | HIGH | Sufficient evidence for specific claims |
| 1-2 signals | MEDIUM | Some evidence, limit specificity |
| 0 signals | LOW/GENERIC | No evidence, use industry language only |

### What Counts as a "Cited Signal"

A signal counts toward the threshold if:
- It has a `source_url` that is a valid HTTP/HTTPS URL
- The `source_type` is `public_url` or `user_provided`

Signals from `vendor_data` or `inferred` sources do NOT count toward citation thresholds.

---

## What Each Mode Allows

### HIGH Mode (3+ Cited Signals)

**Allowed:**
- Explicit company-specific claims with citations
- Named references to company events, news, or public data
- Specific personalization ("I saw your FDA warning letter from March")
- Full use of all extracted signals

**Constraints:**
- Every claim must reference a verified signal
- Source URLs must be present for cited facts
- Claims must match signal content (no exaggeration)

**Example email in HIGH mode:**
```
Subject: After your 483

Saw the FDA issued a 483 to [Company] in March regarding
documentation gaps in your CAPA process.

Most quality leaders I talk to after a 483 say the real
challenge isn't the immediate response—it's preventing
repeat observations.

We built a checklist from 20+ companies who cleared
re-inspection without findings. Want me to send it, or
not a fit right now?
```

---

### MEDIUM Mode (1-2 Cited Signals)

**Allowed:**
- Company mentions without specific claims
- Reference to general situation implied by signal
- Limited personalization based on available evidence

**Constraints:**
- Cannot make claims beyond what the 1-2 signals support
- Must phrase carefully to avoid implying more knowledge
- Generic industry context can supplement

**Example email in MEDIUM mode:**
```
Subject: Quality documentation

Noticed [Company] has been expanding your quality team
recently.

Most quality leaders at growing life sciences companies
tell me the hardest part is keeping documentation
consistent across new hires.

We put together a documentation standards checklist that
speeds up onboarding. Worth a look, or not relevant?
```

---

### LOW/GENERIC Mode (0 Cited Signals)

**Allowed:**
- Industry-level language only
- Role-based assumptions (based on persona)
- Generic pain points common to the industry

**NOT Allowed:**
- Any company-specific claims
- References to company events or news
- Personalization based on vendor data

**Example email in LOW mode:**
```
Subject: Quality documentation

Most quality leaders at life sciences companies tell me
documentation consistency is their biggest challenge
during FDA inspections.

We built a checklist from companies who've cleared
inspection without findings. Might be useful for your
team.

Want me to send it, or not relevant to what you're
working on?
```

---

## Mode Enforcement Points

Confidence mode is enforced at multiple stages:

### 1. Signal Extraction (`relevance_engine.py`)

Mode is assigned here based on signal count:

```python
def determine_confidence_mode(signals: List[Signal]) -> str:
    cited_count = sum(1 for s in signals
                      if s.source_type in ['public_url', 'user_provided']
                      and s.source_url)
    if cited_count >= 3:
        return 'high'
    elif cited_count >= 1:
        return 'medium'
    return 'low'
```

### 2. Constraint Building (`relevance_engine.py`)

Mode determines which constraints are applied:

```python
if confidence_mode == 'high':
    constraints['allow_explicit_claims'] = True
    constraints['require_signal_citation'] = True
elif confidence_mode == 'medium':
    constraints['allow_explicit_claims'] = False
    constraints['allow_company_mentions'] = True
else:  # low
    constraints['allow_explicit_claims'] = False
    constraints['allow_company_mentions'] = False
```

### 3. Validation (`validators.py`)

Mode requirements are checked during validation:

```python
def validate_confidence_mode(email_text, used_signals, mode):
    if mode == 'low' and any_company_specific_claims(email_text):
        return False, "Low confidence mode does not allow company claims"
    if mode == 'high' and not all_claims_have_signals(email_text, used_signals):
        return False, "High mode requires all claims to have signals"
    return True, None
```

---

## Why Modes Cannot Be Overridden

### The Problem with Manual Override

If users could set `confidence_mode: high` manually:
- They could send highly personalized emails with no backing data
- Claims would appear confident but be unverifiable
- Recipients might verify claims and find them wrong
- System credibility would be undermined

### The Trust Model

The Prospecting system's value comes from **verifiable personalization**:

1. Research finds real, citable signals
2. Signals are validated and stored with source URLs
3. Email generation uses only what's been verified
4. Recipients can verify claims if they want to

Breaking this chain by allowing mode override defeats the purpose.

---

## Common Questions

### Q: What if I have vendor data that I know is accurate?

**A:** Vendor data (ZoomInfo, etc.) may be accurate, but it's not publicly verifiable by the recipient. The system is conservative by design. If you have high-confidence vendor data, you can:

1. Find a public source that confirms it (news article, press release)
2. Add that public source as a signal
3. The system will then allow explicit claims

### Q: Can I add more signal sources to reach HIGH mode?

**A:** Yes, this is the intended workflow:

1. Run initial research → get signal count
2. If MEDIUM mode, look for additional public sources
3. Add new signals with `source_type: public_url`
4. Re-run to get HIGH mode

### Q: What happens if validation fails in HIGH mode?

**A:** The system will:
1. Attempt repair (max 2 times)
2. If repair fails, try lower mode rendering
3. If still failing, fall back to generic mode
4. Never send an email with unsupported claims

### Q: How do I check what mode was used?

**A:** The output includes mode information:

```json
{
  "confidence_mode": "high",
  "cited_signal_count": 3,
  "used_signal_ids": ["signal_001", "signal_002", "signal_003"]
}
```

---

## Mode Thresholds Configuration

Thresholds are defined in `src/rules/base_config.yaml`:

```yaml
confidence_modes:
  high:
    min_signals: 3
    allow_explicit_claims: true
    source_types_allowed:
      - public_url
      - user_provided
  medium:
    min_signals: 1
    allow_explicit_claims: false
    allow_company_mentions: true
  low:
    min_signals: 0
    allow_explicit_claims: false
    allow_company_mentions: false
```

**Warning:** Changing these thresholds affects the system's safety guarantees. See `docs/SYSTEM_BOUNDARIES.md` before modifying.

---

## Summary

| Mode | Signals Required | Company Claims | Company Mentions |
|------|------------------|----------------|------------------|
| HIGH | 3+ | Yes (with citation) | Yes |
| MEDIUM | 1-2 | No | Yes |
| LOW | 0 | No | No |

**Key principle:** The system only allows claims it can back up. This is a feature, not a limitation.
