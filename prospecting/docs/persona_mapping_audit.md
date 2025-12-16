# Persona Mapping Logic Audit

**Generated:** 2025-12-11
**Purpose:** Surface current persona detection behavior for review. No fixes proposed.

---

## 1. Persona Rules Snapshot

### 1.1 YAML Configuration (base_config.yaml)

This is the **source of truth** loaded by `rules_loader.py`:

```yaml
personas:
  quality:
    patterns:
      - "vp quality"
      - "vice president quality"
      - "head of quality"
      - "director quality"
      - "quality director"
      - "qa director"
      - "vp qa"
      - "quality assurance"
      - "chief quality"
      - "vp qc"
      - "quality control"
      - "compliance"

  operations:
    patterns:
      - "vp operations"
      - "vice president operations"
      - "head of operations"
      - "director operations"
      - "operations director"
      - "plant director"
      - "vp ops"
      - "site director"
      - "manufacturing director"
      - "vp manufacturing"
      - "production director"

  it:
    patterns:
      - "cio"
      - "chief information"
      - "vp it"
      - "vice president it"
      - "it director"
      - "director it"
      - "head of it"
      - "vp digital"
      - "vp technology"
      - "cto"
      - "chief technology"

  regulatory:
    patterns:
      - "vp regulatory"
      - "vice president regulatory"
      - "head of regulatory"
      - "director regulatory"
      - "regulatory director"
      - "regulatory affairs"
      - "vp ra"
      - "chief regulatory"
```

### 1.2 Hardcoded Python Logic (email_components.py)

`EmailComponentLibrary` has a **duplicate, parallel implementation** that mirrors the YAML but is not loaded from it:

```python
PERSONA_PATTERNS = {
    "quality": [
        "vp quality", "vice president quality", "head of quality",
        "director quality", "quality director", "qa director",
        "vp qa", "quality assurance", "chief quality",
        "vp qc", "quality control", "compliance"
    ],
    "operations": [
        "vp operations", "vice president operations", "head of operations",
        "director operations", "operations director", "plant director",
        "vp ops", "site director", "manufacturing director",
        "vp manufacturing", "production director"
    ],
    "it": [
        "cio", "chief information", "vp it", "vice president it",
        "it director", "director it", "head of it",
        "vp digital", "vp technology", "cto", "chief technology"
    ],
    "regulatory": [
        "vp regulatory", "vice president regulatory", "head of regulatory",
        "director regulatory", "regulatory director", "regulatory affairs",
        "vp ra", "chief regulatory"
    ]
}
```

**Risk:** If YAML and Python drift, behavior will be inconsistent depending on which code path is used.

### 1.3 Detection Algorithm (relevance_engine.py:87-116)

```python
def detect_persona(self, title: Optional[str]) -> Optional[str]:
    if not title:
        logger.warning("No title provided for persona detection")
        return None

    title_lower = title.lower()

    # Get persona patterns from rules_config
    personas = self.rules_config.get('personas', {})

    for persona, config in personas.items():
        patterns = config.get('patterns', [])
        if any(pattern.lower() in title_lower for pattern in patterns):
            logger.info(f"Detected persona: {persona} from title '{title}'")
            return persona

    logger.warning(f"Could not detect persona from title '{title}'")
    # Return default persona when no match (Fix #3: never return None)
    default_persona = self._get_default_persona()
    logger.info(f"Using default persona: {default_persona}")
    return default_persona
```

### 1.4 Precedence Rules

| Rule | Behavior |
|------|----------|
| **Match order** | Iterates personas in dict order (quality → operations → it → regulatory). First match wins. |
| **Substring matching** | Uses `pattern.lower() in title_lower`. Any substring match triggers. |
| **Case sensitivity** | Case-insensitive (both sides lowercased). |
| **Multiple matches** | **Not detected.** System stops at first match. |
| **No match fallback** | Returns first persona from config (currently "quality"). |
| **Null title** | Returns `None` (not the fallback persona). |

---

## 2. Persona Truth Table

Based on **current system behavior**, not ideal behavior:

| Persona | Core Responsibility | Allowed Pain Areas | Must NEVER Frame As Owning | Default Safe Angle |
|---------|--------------------|--------------------|----------------------------|-------------------|
| **quality** | QA/QC processes, compliance, deviation closure | CAPA, deviations, audit readiness, supplier quality, training compliance, documentation | IT system architecture, manufacturing throughput, production scheduling | CAPA cycle time |
| **operations** | Manufacturing, production, site throughput | Batch release, batch review, review-by-exception, training effectiveness, manufacturing efficiency | Regulatory strategy, IT decisions, supplier contracts | Batch release time |
| **it** | Systems, validation, digital infrastructure | System sprawl, validation load, data integrity, audit trails, system integration | Quality decisions, regulatory submissions, production quotas | Validation load |
| **regulatory** | Regulatory strategy, submissions, agency interactions | Audit readiness, design control (device), regulatory deadlines | Manufacturing operations, IT infrastructure, day-to-day QA | Audit readiness |

**Note:** The "operations" persona has overlap with "quality" on training. The system currently treats training as shared.

---

## 3. Ambiguous Title Test Set

Ran each title through `relevance_engine.detect_persona()` logic:

| # | Input Title | Assigned Persona | Pattern Matched | Multiple Matches Possible? | Ambiguity Flagged? | Fallback Applied? |
|---|-------------|------------------|-----------------|---------------------------|-------------------|-------------------|
| 1 | VP Quality | quality | "vp quality" | No | No | No |
| 2 | VP, Quality & Compliance | quality | "compliance" | Yes ("quality" also matches) | **No** | No |
| 3 | Director, Quality Systems | quality | "director quality" | No | No | No |
| 4 | VP Quality Systems & IT | quality | "vp quality" | Yes (also "vp it") | **No** | No |
| 5 | Head of Quality & Regulatory | quality | "head of quality" | Yes (also "regulatory") | **No** | No |
| 6 | Director, Quality and Manufacturing | quality | "director quality" | Yes (manufacturing → ops) | **No** | No |
| 7 | VP Manufacturing & Quality | quality | "quality" (substring) | Yes | **No** | No |
| 8 | Chief Quality & Compliance Officer | quality | "chief quality" | Yes ("compliance") | **No** | No |
| 9 | SVP Ops & Quality | quality | "quality" (substring) | Yes ("ops") | **No** | No |
| 10 | VP Operations | operations | "vp operations" | No | No | No |
| 11 | Site Director | operations | "site director" | No | No | No |
| 12 | VP Manufacturing & IT | operations | "vp manufacturing" | Yes ("vp it") | **No** | No |
| 13 | Director, Manufacturing Operations | operations | "director operations" (substring?) | Partial | No | No |
| 14 | Plant Manager | **quality** (fallback) | None | N/A | No | **Yes** |
| 15 | VP Technical Operations | operations | "vp ops" (substring match) | No | No | No |
| 16 | CIO | it | "cio" | No | No | No |
| 17 | VP IT & Quality Systems | it | "vp it" | Yes ("quality") | **No** | No |
| 18 | Chief Technology Officer | it | "cto" | No | No | No |
| 19 | VP Digital & Manufacturing | it | "vp digital" | Yes ("manufacturing") | **No** | No |
| 20 | Director IT & Compliance | it | "director it" | Yes ("compliance" → quality) | **No** | No |
| 21 | Head of Information Technology | it | "head of it" (substring?) | Unlikely | No | No |
| 22 | VP Regulatory Affairs | regulatory | "vp regulatory" | No | No | No |
| 23 | VP Regulatory & Quality | regulatory | "vp regulatory" | Yes ("quality") | **No** | No |
| 24 | Chief Regulatory Officer | regulatory | "chief regulatory" | No | No | No |
| 25 | Director QA/RA | quality | "qa" (substring) | Yes ("ra") | **No** | No |
| 26 | VP Compliance | quality | "compliance" | No | No | No |
| 27 | VP GxP Compliance & IT | quality | "compliance" | Yes ("it") | **No** | No |
| 28 | MSAT Director | **quality** (fallback) | None | N/A | No | **Yes** |
| 29 | Director, Process Validation | **quality** (fallback) | None | N/A | No | **Yes** |
| 30 | VP CSV & Computer Systems Validation | **quality** (fallback) | None | N/A | No | **Yes** |
| 31 | Sr. Director Quality Engineering | quality | "director quality" | No | No | No |
| 32 | EVP Operations & Supply Chain | operations | "operations" (substring) | No | No | No |
| 33 | Head of Drug Safety | **quality** (fallback) | None | N/A | No | **Yes** |
| 34 | VP Pharmacovigilance | **quality** (fallback) | None | N/A | No | **Yes** |
| 35 | Director, Automation & Digital | it | "digital" (substring) | No | No | No |
| 36 | VP QMS | quality | "qm" — **NO, doesn't match** | N/A | No | **Yes** |
| 37 | Chief Compliance Officer | quality | "compliance" | No | No | No |
| 38 | VP R&D | **quality** (fallback) | None | N/A | No | **Yes** |
| 39 | Head of CMC | **quality** (fallback) | None | N/A | No | **Yes** |
| 40 | Director GxP Systems | **quality** (fallback) | None | N/A | No | **Yes** |

### Key Observations

1. **No ambiguity detection**: System never flags when multiple persona patterns match
2. **Fallback overuse**: 11/40 titles fall through to "quality" default
3. **Substring danger**: "compliance" matches quality, so "VP IT & Compliance" → depends on iteration order
4. **Missing patterns**: MSAT, CSV, PV, CMC, GxP, R&D, Drug Safety all fall through
5. **Order matters**: Dict iteration order determines winner when multiple match

---

## 4. Persona Safety Check

For 5 ambiguous titles, showing how different persona assignments would change sentence 1 (hook):

### Title: "Director, Quality Systems & IT"

**As Quality:**
> With the Northwind acquisition closing in Q1, your GMP manufacturing was cited as a key asset.

**As IT:**
> When quality workflows are split across too many tools, audit trail integrity and access controls become a validation risk.

**Safety assessment:** Quality hook safer — references company fact. IT hook assumes system sprawl pain that may not exist.

---

### Title: "VP Manufacturing & Quality"

**As Quality:**
> I'm seeing QA teams pushed to shorten deviation and CAPA cycle time, but manual handoffs keep approvals slow.

**As Operations:**
> A lot of sites are trying to cut batch release time without adding headcount.

**Safety assessment:** Either is plausible. Quality slightly safer — broader applicability to dual-role.

---

### Title: "VP Regulatory & Quality"

**As Quality:**
> Most QA teams are balancing speeding up deviations while keeping audit readiness high.

**As Regulatory:**
> With QMSR enforcement Feb 2, 2026, device QA teams are finding DHF gaps in change control.

**Safety assessment:** Depends on industry. Regulatory hook only valid for medical device. Quality hook safer as default.

---

### Title: "Director IT & Compliance"

**As IT:**
> When quality workflows live across too many tools, every change feels like a validation project.

**As Quality (via "compliance"):**
> I'm seeing QA teams pushed to shorten CAPA cycle time, but training gaps keep approvals slow.

**Safety assessment:** IT hook more relevant to title. Quality assignment (current behavior) risks being off-target.

---

### Title: "VP GxP Compliance & IT"

**As Quality (current):**
> QA teams are balancing speed with compliance in quality workflows.

**As IT:**
> When quality workflows are split across multiple tools, audit trail integrity becomes a risk.

**Safety assessment:** Both reasonable. GxP context suggests IT/validation hook may resonate more with systems focus.

---

## 5. Persona Diagnostics Artifact

**Current state: No structured diagnostics object is emitted.**

The system logs warnings but does not return a machine-readable diagnostic. Example of what would be useful:

```json
{
  "input_title": "VP Quality Systems & IT",
  "matched_persona_rules": [
    {"persona": "quality", "pattern": "vp quality", "position": 0},
    {"persona": "it", "pattern": "vp it", "position": 1}
  ],
  "selected_persona": "quality",
  "selection_reason": "first_match",
  "ambiguity_detected": true,
  "ambiguity_note": "Multiple personas matched (quality, it). Selected 'quality' by iteration order.",
  "fallback_applied": false,
  "confidence": "low"
}
```

**This object does not exist today.** The only output is:
- Logger warning: "Could not detect persona from title 'X'"
- Logger info: "Detected persona: X from title 'Y'"

No structured return of matched rules, ambiguity flags, or confidence.

---

## 6. Known Weak Spots

### Titles I Am Least Confident About

| Title | Issue |
|-------|-------|
| MSAT Director | No pattern. Falls to quality. May be ops or quality depending on company. |
| Director, Process Validation | No pattern. Falls to quality. Should probably be quality or it. |
| VP CSV / VP Computer Systems Validation | No pattern. Falls to quality. Likely should be IT. |
| VP Drug Safety / VP Pharmacovigilance | No pattern. Falls to quality. PV is distinct function. |
| VP QMS | "QMS" doesn't match. Falls to quality. Should match quality. |
| Head of CMC | No pattern. Falls to quality. CMC is R&D adjacent. |
| Plant Manager | No pattern. Falls to quality. Should probably be operations. |
| VP R&D | No pattern. Falls to quality. R&D is distinct function. |
| Director GxP Systems | No pattern. Falls to quality. Could be IT or quality. |

### Where System Likely Misclassifies Today

1. **Dual-role titles with IT second:** "VP Quality & IT" → quality. "VP IT & Quality" → it. Order in title affects nothing, but persona dict order does.

2. **Compliance-heavy IT roles:** "Director IT & Compliance" → quality (via "compliance" substring). Wrong.

3. **GxP/CSV roles:** These are IT-adjacent but fall to quality default.

4. **Manufacturing + Quality combos:** Always resolve to quality due to iteration order, even when ops context is stronger.

5. **PV/Drug Safety:** No patterns exist. These contacts get quality messaging about CAPA, which may be irrelevant.

### Where I Relied on Judgment Rather Than Rules

1. **Deciding which fallback is "safer":** Currently hardcoded to "quality" but no explicit rationale in code.

2. **Substring matching danger:** "VP QC" matches but "VP QMS" doesn't. Logic doesn't explain why.

3. **Order of personas in YAML:** Determines match priority but isn't documented as intentional.

4. **No scoring of pattern specificity:** "vp quality" and "quality" substring are treated equally.

---

## Summary

The current system:
- Has simple substring matching with first-match-wins
- Does not detect or flag ambiguous titles
- Falls back to "quality" for everything unrecognized
- Has parallel implementations (YAML + Python) that could drift
- Emits no structured diagnostics for debugging
- Lacks patterns for significant role families (MSAT, CSV, PV, CMC, GxP)

This document surfaces reality. No fixes proposed.
