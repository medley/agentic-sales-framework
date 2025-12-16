# Email Validation Flow

This document explains how generated emails are validated before output. Understanding this flow is essential before modifying any validation logic.

---

## Three Validation Layers

Every generated email passes through three validation layers. **All must pass for the email to be accepted.**

### Layer 1: Signal Integrity (`validators.py`)

**Purpose:** Ensure all personalization claims are backed by real, appropriate data.

**What it checks:**

| Check | Failure Example |
|-------|-----------------|
| All `used_signal_ids` exist in verified_signals | `signal_999` referenced but doesn't exist |
| Source type allows explicit claims | ZoomInfo data used for "I saw your $50M raise" |
| Confidence mode requirements met | HIGH mode claims with only 1 signal |

**Example failures:**
```
❌ Signal ID 'signal_999' not found in verified signals
❌ Signal 'signal_003' has source_type 'vendor_data' but email makes explicit claim
❌ Confidence mode 'high' requires 3+ signals, found 1
```

**Why this matters:** Prevents hallucinated personalization and vendor data leakage into claims.

**CRITICAL:** This layer is NEVER bypassed, even in fallback modes.

---

### Layer 2: Structure & Quality (`quality_controls.py`)

**Purpose:** Enforce structural guidelines and banned content.

**What it checks:**

| Check | Requirement |
|-------|-------------|
| Word count | 50-100 words |
| Sentence count | 3-4 sentences |
| Subject line length | ≤7 words |
| Ends with question | Must end with "?" |
| Banned phrases | No "circle back", "touch base", etc. |
| No product mentions | First-touch emails only |

**Example failures:**
```
❌ Word count: 132 words (exceeds 100 max)
❌ Contains banned phrase: "circle back"
❌ Does not end with question mark
❌ Subject line too long: 12 words (max 7)
```

**Why this matters:** Maintains consistent quality and avoids spam triggers.

**Note:** Some checks may be relaxed in deterministic fallback mode.

---

### Layer 3: Voice Consistency (`voice_validator.py`)

**Purpose:** Ensure email matches the sales rep's authentic voice patterns.

**What it checks:**

| Check | Rationale |
|-------|-----------|
| No exclamation marks | Professional voice avoids excitement language |
| Binary/qualifying questions | "Want the checklist?" not "What do you think?" |
| Offer-based CTA | Gives something, doesn't just ask for time |
| Subject style | Short, operational, no hype |

**Example failures:**
```
❌ Contains exclamation mark
❌ Question is not binary: "What are your thoughts on this?"
❌ CTA asks for meeting without offering value first
```

**Why this matters:** Maintains authentic voice that recipients recognize.

**Note:** May be relaxed in legacy fallback mode.

---

## Validation Decision Tree

```
┌──────────────────────────────────────────────────────────────┐
│                    Generated Variant                          │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │   Signal Integrity Check      │
              │   (validators.py)             │
              └───────────────────────────────┘
                    │                │
                  PASS             FAIL
                    │                │
                    │                ▼
                    │         ┌─────────────┐
                    │         │ Repair      │
                    │         │ (max 2x)    │
                    │         └─────────────┘
                    │                │
                    │          STILL FAIL?
                    │                │
                    │                ▼
                    │         ┌─────────────┐
                    │         │ DISCARD     │
                    │         │ variant     │
                    │         └─────────────┘
                    │
                    ▼
              ┌───────────────────────────────┐
              │   Structure Check             │
              │   (quality_controls.py)       │
              └───────────────────────────────┘
                    │                │
                  PASS             FAIL
                    │                │
                    │                ▼
                    │         ┌─────────────┐
                    │         │ Repair      │
                    │         │ (max 2x)    │
                    │         └─────────────┘
                    │                │
                    ▼                ▼
              ┌───────────────────────────────┐
              │   Voice Check                 │
              │   (voice_validator.py)        │
              └───────────────────────────────┘
                    │                │
                  PASS             FAIL
                    │                │
                    ▼                ▼
              ┌──────────┐    ┌─────────────┐
              │ VALID    │    │ Repair      │
              │ VARIANT  │    │ (max 2x)    │
              │    ✓     │    └─────────────┘
              └──────────┘           │
                               STILL FAIL?
                                     │
                                     ▼
                              ┌─────────────┐
                              │ DISCARD     │
                              └─────────────┘
```

---

## Repair Process

When validation fails, the system attempts repair before discarding.

### Repair Settings

| Repair Type | Temperature | Max Attempts |
|-------------|-------------|--------------|
| Signal integrity | 0.3 | 2 |
| Structure | 0.3 | 2 |
| Voice | 0.3 | 2 |

### What Repair Can Fix

| Issue | Repair Strategy |
|-------|-----------------|
| Word count too high | LLM rewrites more concisely |
| Missing question mark | LLM adds qualifying question |
| Banned phrase present | LLM rephrases |
| Exclamation mark | LLM removes/rephrases |

### What Repair Cannot Fix

| Issue | Why |
|-------|-----|
| Invalid signal ID | Can't fabricate a signal that doesn't exist |
| Source type violation | Can't change where the data came from |
| Confidence mode violation | Can't invent more signals |

**Key insight:** Repair fixes language issues, not data issues.

---

## Which Validator Enforces What

Quick reference for which module handles each check:

| Check | Module | Layer | Bypassed in Fallback? |
|-------|--------|-------|----------------------|
| Signal IDs exist | validators.py | 1 | **NO** |
| Source type compliance | validators.py | 1 | **NO** |
| Confidence mode | validators.py | 1 | **NO** |
| Word count | quality_controls.py | 2 | Yes (deterministic) |
| Sentence count | quality_controls.py | 2 | Yes (deterministic) |
| Banned phrases | quality_controls.py | 2 | **NO** |
| Subject length | quality_controls.py | 2 | Yes (deterministic) |
| Ends with question | quality_controls.py | 2 | Yes (deterministic) |
| No exclamation marks | voice_validator.py | 3 | Yes (legacy) |
| Binary questions | voice_validator.py | 3 | Yes (legacy) |
| Offer-based CTA | voice_validator.py | 3 | Yes (legacy) |

### Critical Invariant

**Signal integrity checks (Layer 1) and banned phrases are NEVER bypassed.**

Even in fallback modes, these safety checks always run.

---

## Fallback Modes

When the full validation pipeline fails, the system has fallback options:

### Deterministic Fallback

**When:** LLM rendering repeatedly fails validation
**What happens:** Uses draft sentences directly without LLM transformation
**What's preserved:** Signal integrity, banned phrases
**What's relaxed:** Word count precision, sentence structure

### Legacy Fallback

**When:** Hybrid system unavailable
**What happens:** Uses older email generation path
**What's preserved:** Signal integrity, banned phrases
**What's relaxed:** Voice consistency patterns

### Generic Fallback

**When:** Insufficient signals for any personalization
**What happens:** Industry-focused email with no company claims
**What's preserved:** All validation
**What's different:** No `used_signal_ids`, generic language only

---

## Testing Validation

### Run All Validator Tests

```bash
pytest tests/test_validators.py -v
pytest tests/test_integration_hybrid_flow.py -v
```

### Test Specific Checks

```python
from src.validators import validate_all

result = validate_all(
    email_text="Your email here...",
    subject="Subject line",
    verified_signals=[...],
    used_signal_ids=["signal_001"],
    constraints={...}
)

print(result['passed'])  # True/False
print(result['issues'])  # Dict of issues by category
```

### Manual Validation Check

1. Generate an email variant
2. Check `used_signal_ids` in output
3. Verify each ID exists in `verified_signals`
4. Confirm source_type of each used signal allows claims
5. Count words, check for banned phrases

---

## Common Validation Failures

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "Signal ID not found" | LLM hallucinated a signal | Lower rendering temperature |
| "Source type violation" | ZoomInfo data in explicit claim | Review signal extraction |
| "Word count exceeded" | LLM added too much detail | Adjust constraints or temperature |
| "Banned phrase found" | LLM used common sales language | Add phrase to banned list |
| "No question mark" | LLM ended with statement | Check CTA templates |

---

## Summary

1. **Three layers:** Signal Integrity → Structure → Voice
2. **Repair attempts:** Max 2 per layer before discard
3. **Never bypassed:** Signal integrity, banned phrases
4. **Language vs. Data:** Repair fixes language; data issues can't be repaired
5. **Test before changing:** Always run validator tests after modifications
