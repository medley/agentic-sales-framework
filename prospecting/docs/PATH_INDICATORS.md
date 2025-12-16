# Angle Scoring - Path Indicators

When you run `/prospect`, the system will show you **exactly which path was taken** for angle selection.

---

## Terminal Output Indicators

### Path 1: LLM Scoring Used ✅

**When**: 2+ candidate angles AND LLM enabled AND API available

```
--- Angle Selection ---
Method: LLM_SCORED
Candidates considered: 3
  regulatory_pressure, operational_cost, audit_readiness
Chosen angle: regulatory_pressure

Path: 2+ candidates → LLM scoring used

Weighted score: 4.45
Reason: Strong regulatory signals with recent FDA activity

All scores:
  regulatory_pressure: R=5 U=4 RL=4 → 4.45
  operational_cost: R=3 U=3 RL=4 → 3.30
  audit_readiness: R=4 U=3 RL=3 → 3.50
```

**Artifact field**: `"path": "llm_scoring_used"`

---

### Path 2: Only 1 Candidate (Skipped LLM)

**When**: Only 1 angle matches persona/industry/signals

```
--- Angle Selection ---
Method: DETERMINISTIC
Candidates considered: 1
  regulatory_pressure
Chosen angle: regulatory_pressure

Path: Only 1 candidate → skipped LLM

Deterministic scores:
  ✓ regulatory_pressure: 6
```

**Artifact field**: `"path": "only_1_candidate_skipped_llm"`

**Why**: No point using LLM to rank a single option

---

### Path 3: LLM Failed (Fallback)

**When**: LLM enabled but API call failed

```
--- Angle Selection ---
Method: DETERMINISTIC
Candidates considered: 3
  regulatory_pressure, operational_cost, audit_readiness
Chosen angle: regulatory_pressure

Path: LLM failed → fallback to deterministic
  Reason: ANTHROPIC_API_KEY not set

Deterministic scores:
  ✓ regulatory_pressure: 4
    operational_cost: 4
    audit_readiness: 4
```

**Artifact fields**:
```json
{
  "path": "llm_failed_fallback",
  "fallback_reason": "ANTHROPIC_API_KEY not set"
}
```

**Common reasons**:
- `ANTHROPIC_API_KEY not set`
- `API request failed: <error details>`
- `Invalid JSON response from LLM`
- `No valid scores parsed from output`

---

### Path 4: LLM Disabled in Config

**When**: `enable_angle_scoring: false` in config

```
--- Angle Selection ---
Method: DETERMINISTIC
Candidates considered: 3
  regulatory_pressure, operational_cost, audit_readiness
Chosen angle: regulatory_pressure

Path: LLM scoring disabled in config

Deterministic scores:
  ✓ regulatory_pressure: 6
    operational_cost: 4
    audit_readiness: 4
```

**Artifact field**: `"path": "llm_disabled_in_config"`

---

## Artifact File Path Field

Every run writes to `deliverables/angle_scoring.json` with a `path` field:

| Path Value | Meaning |
|------------|---------|
| `llm_scoring_used` | LLM successfully ranked 2+ candidates |
| `only_1_candidate_skipped_llm` | Only 1 angle matched, no ranking needed |
| `llm_failed_fallback` | LLM attempted but failed, fell back to deterministic |
| `llm_disabled_in_config` | LLM scoring disabled, used deterministic only |

---

## Decision Tree

```
Start
  │
  ├─ enable_angle_scoring = false?
  │   └─ YES → Path: "llm_disabled_in_config"
  │
  └─ enable_angle_scoring = true
      │
      ├─ Only 1 candidate?
      │   └─ YES → Path: "only_1_candidate_skipped_llm"
      │
      └─ 2+ candidates
          │
          ├─ LLM API call successful?
          │   ├─ YES → Path: "llm_scoring_used"
          │   └─ NO  → Path: "llm_failed_fallback" (+ fallback_reason)
```

---

## Why This Matters

**Debugging**: Instantly see why deterministic was used instead of LLM

**Monitoring**: Track how often LLM is actually being used vs fallback

**Cost tracking**: Know when you're making API calls

**Reliability**: Confirm graceful degradation is working

**A/B testing**: Compare LLM vs deterministic selection outcomes

---

## Example Use Cases

### 1. Verify LLM is Active
```bash
/prospect "Jane Smith" "Acme Corp"
cat deliverables/angle_scoring.json | grep path

# Expected when working:
"path": "llm_scoring_used"
```

### 2. Debug Why Deterministic Was Used
```bash
# Terminal shows:
Path: LLM failed → fallback to deterministic
  Reason: ANTHROPIC_API_KEY not set

# Fix:
export ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Track LLM Usage Rate
```bash
# After 10 prospect runs:
grep -h '"path"' deliverables/angle_scoring_*.json

# Count LLM usage:
grep -c '"llm_scoring_used"' deliverables/angle_scoring_*.json
# Output: 7

# Count fallbacks:
grep -c '"llm_failed_fallback"' deliverables/angle_scoring_*.json
# Output: 0

# Count single candidates:
grep -c '"only_1_candidate_skipped_llm"' deliverables/angle_scoring_*.json
# Output: 3
```

---

## Configuration

**Current default**: `enable_angle_scoring: true`

**To disable LLM scoring**:
```yaml
# src/rules/base_config.yaml
angle_scoring:
  enable_angle_scoring: false  # Use deterministic only
```

**To re-enable**:
```yaml
angle_scoring:
  enable_angle_scoring: true   # Use LLM when 2+ candidates
```

---

## Terminal Output Reference

All possible terminal outputs:

```
Path: 2+ candidates → LLM scoring used
Path: Only 1 candidate → skipped LLM
Path: LLM failed → fallback to deterministic
  Reason: <specific error>
Path: LLM scoring disabled in config
```

---

**Last Updated**: 2025-12-11  
**Status**: Active in current version
