# System Boundaries and Safety Constraints

This document defines the safety-critical boundaries of the Prospecting system. **Read this before modifying any validation or signal-handling code.**

---

## What This System Guarantees

| Guarantee | Enforced By |
|-----------|-------------|
| Every company-specific claim has a cited source URL | `validators.py` |
| Vendor data (ZoomInfo) never appears as explicit claims | `validators.py` |
| Low-confidence mode prevents unsupported personalization | `relevance_engine.py` |
| Banned phrases are checked deterministically | `quality_controls.py` |
| Voice consistency follows defined patterns | `voice_validator.py` |

## What This System Does NOT Guarantee

| Limitation | Why |
|------------|-----|
| Source URLs are not validated for accuracy | System stores URLs but doesn't fetch/verify them |
| LLM can still hallucinate | Validation catches most but not all fabrications |
| Signal "recency" is based on data availability | Not validated against actual event timing |
| ZoomInfo data accuracy | Vendor data may be stale or incorrect |

---

## Decision Boundary 1: Signal Source Types

**This is the most important safety boundary in the system.**

### The Rule

Only signals with `source_type: 'public_url'` or `'user_provided'` can be used for explicit company claims.

### Source Type Definitions

| Source Type | Can Make Explicit Claims? | Example Use |
|-------------|---------------------------|-------------|
| `public_url` | YES | "I saw your FDA warning letter from March..." |
| `user_provided` | YES | Facts the user explicitly validated |
| `vendor_data` | NO - generic only | Guides angle selection, not explicit claims |
| `inferred` | NO - generic only | "Companies in your situation often..." |

### Enforced In

`validators.py` → `validate_source_type_compliance()`

### Example Violation

```python
# BAD: ZoomInfo funding data as explicit claim
"I noticed you raised $50M in Series B last month"
# source_type: 'vendor_data' → REJECTED by validator

# GOOD: ZoomInfo data guides angle selection generically
"Most companies after a funding round tell me there's pressure to prove ROI"
# source_type: 'vendor_data' → used for strategy, not claims
```

### Why This Matters

ZoomInfo data is not publicly verifiable by the recipient. Using it as explicit claims:
- Reduces email credibility ("How do they know this?")
- Creates compliance risk if data is stale/wrong
- Violates the system's trust model

---

## Decision Boundary 2: LLM vs. Deterministic Responsibilities

### LLM Decides (Language Generation)

| Task | Temperature | Why |
|------|-------------|-----|
| How to phrase draft sentences naturally | 0.7 | Voice flexibility |
| How to rank candidate angles | 0.0 | Reproducible scoring |
| How to repair validation failures | 0.3 | Precision over creativity |

### LLM Does NOT Decide (Truth & Safety)

| Task | Handled By | Why Deterministic |
|------|------------|-------------------|
| Which signals are valid | Python extraction | No hallucination risk |
| Which angles are eligible | YAML rules | Auditable, testable |
| Which facts can be claimed | validators.py | Safety-critical |
| Word count, banned phrases | quality_controls.py | Consistent enforcement |

### The Principle

**Language generation = LLM. Truth validation = Python.**

Moving validation logic to the LLM would risk hallucinated "validation passes." Keep truth logic deterministic.

---

## Decision Boundary 3: Confidence Mode Enforcement

### Automatic Assignment (Cannot Be Overridden)

| Signal Count | Mode | What's Allowed |
|--------------|------|----------------|
| 3+ cited signals | HIGH | Explicit company claims with citations |
| 1-2 cited signals | MEDIUM | Company mentions, limited specificity |
| 0 cited signals | LOW/GENERIC | Industry language only, no company claims |

### Why This Cannot Be User-Overridden

Confidence modes exist to prevent making bold claims with insufficient evidence. Allowing override would let users:
- Send highly personalized emails with no backing data
- Risk credibility when claims can't be verified
- Bypass the system's core value proposition

### Enforced In

- Mode assignment: `relevance_engine.py`
- Mode constraints: `validators.py` → `validate_confidence_mode()`
- Tier thresholds: `base_config.yaml` lines 189-200

---

## Decision Boundary 4: Validation Order

Validation happens in a specific order. **All layers must pass.**

```
Generated Email
     │
     ▼
┌─────────────────────────────────┐
│ Layer 1: Signal Integrity       │  ← NEVER BYPASSED
│ (validators.py)                 │
│ - Signal IDs exist              │
│ - Source type compliance        │
│ - Confidence mode requirements  │
└─────────────────────────────────┘
     │ PASS
     ▼
┌─────────────────────────────────┐
│ Layer 2: Structure & Quality    │  ← Bypassed in deterministic fallback
│ (quality_controls.py)           │
│ - Word count (50-100)           │
│ - Sentence count (3-4)          │
│ - Banned phrases                │
│ - Ends with question            │
└─────────────────────────────────┘
     │ PASS
     ▼
┌─────────────────────────────────┐
│ Layer 3: Voice Consistency      │  ← Bypassed in legacy fallback
│ (voice_validator.py)            │
│ - No exclamation marks          │
│ - Binary question format        │
│ - Offer-based CTA               │
└─────────────────────────────────┘
     │ PASS
     ▼
   Valid Email ✓
```

### Critical Invariant

**Signal integrity (Layer 1) is NEVER bypassed**, even in fallback modes. This ensures no email ever makes claims without cited sources.

---

## What You Can Safely Modify

### Configuration Knobs (Safe)

| File | What You Can Change |
|------|---------------------|
| `src/rules/base_config.yaml` | Personas, angles, offers, word counts, banned phrases |
| `src/email_components.py` | Pain point text, CTA wording, subject variants |
| LLM temperatures | Rendering (0.7), Repair (0.3) - with testing |

### Requires Careful Testing

| File | Risk If Changed Incorrectly |
|------|----------------------------|
| `relevance_engine.py` persona detection | Wrong angles selected |
| `relevance_engine.py` signal extraction | Wrong personalization allowed |
| `base_config.yaml` tier thresholds | Claims with insufficient evidence |

### DO NOT Modify Without Safety Review

| File/Function | Why It's Critical |
|---------------|-------------------|
| `validators.py` → `validate_source_type_compliance()` | Enforces truth boundary |
| `validators.py` → `validate_signal_integrity()` | Prevents hallucinated signals |
| Confidence mode thresholds | Credibility/compliance boundary |
| Angle scoring temperature (must stay 0.0) | Reproducibility requirement |

---

## Testing Safety Boundaries

Before any PR that touches validation:

```bash
# Run full test suite
pytest tests/ -v

# Specifically test validators
pytest tests/test_validators.py -v

# Check for signal integrity in sample output
python -c "from src.validators import validate_all; print('Validators loaded')"
```

### Manual Checks

1. Generate an email with only ZoomInfo data (no public URLs)
2. Verify it uses generic language, not explicit claims
3. Check that `used_signal_ids` only references valid signals
4. Confirm confidence mode matches signal count

---

## Summary: The Three Laws

1. **Never let vendor data become explicit claims** (source type boundary)
2. **Never move truth validation to the LLM** (deterministic boundary)
3. **Never bypass signal integrity checks** (validation order boundary)

When in doubt, ask: "Could this change allow an email to make a claim that can't be verified?"

If yes, don't make the change without safety review.
