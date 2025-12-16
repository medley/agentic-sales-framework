---
name: "methodology_loader_protocol"
type: "system_protocol"
owner: "Welf Ludwig"
version: "1.0.0"
license: "MIT - See LICENSE.md"
---

# Methodology Loader Protocol

Shared pattern for how agents and skills should load and use sales methodologies
(Sandler, MEDDPICC, Generic, Hybrid, etc.).

This file lives in:
`Framework/System/methodology_loader.md`

It is **documentation**, not code. Agents/skills follow this protocol when they need methodology-aware behavior.

---

## 1. Goals

- **Single source of truth** for how methodologies are loaded
- **No hard-coding** Sandler/MEDDPICC rules inside each agent/skill
- **Easy to add** new methodologies later (MEDDPICC, Hybrid, etc.)
- **Graceful fallbacks** when methodology data is missing or incomplete

**CRITICAL:** Agents and skills MUST NOT implement their own methodology loading logic. Instead, they should literally follow the steps in §4 "Loader Pattern" when they need methodology-aware behavior. This protocol is the single source of truth for all methodology loading.

---

## 2. Where Methodology Comes From

### 2.1 Deal Frontmatter (entry point)

Every deal lives at:
`sample-data/Runtime/Sessions/{DEAL_NAME}/deal.md`

Minimum frontmatter:

```yaml
---
deal_name: "AcmeCorp"
stage: "2 - Solutioning"        # free text, but should map to a methodology stage
stage_num: 2                    # optional, recommended
owner: "Your Name"
methodology: "Sandler"          # or "MEDDPICC", "Hybrid", "Generic"
acv: 144781                     # optional
close_date: 2025-03-31          # optional
last_updated: 2025-11-12        # optional

# MEDDPICC-style fields are optional but useful for scanners:
metrics: ""
economic_buyer: ""
decision_criteria: ""
decision_process: ""
pain: ""
champion: ""
competition: ""
---
```

If `methodology` is missing, agents/skills must default to `"Generic"`.

---

### 2.2 Methodology Naming Convention

**Use TitleCase consistently across all contexts:**
- **In deal.md frontmatter:** `"Sandler"`, `"MEDDPICC"`, `"Hybrid"`, `"Generic"`
- **In folder names:** Use the same TitleCase:
  - `sample-data/Runtime/_Shared/knowledge/methodologies/Sandler/`
  - `sample-data/Runtime/_Shared/knowledge/methodologies/MEDDPICC/`
  - `sample-data/Runtime/_Shared/knowledge/methodologies/Hybrid/`
  - `sample-data/Runtime/_Shared/knowledge/methodologies/Generic/`
- **In code/pseudocode:** You may `.lower()` for case-insensitive comparisons, but always resolve to the TitleCase folder name when loading files.

This prevents accidental folder duplication (e.g., `meddpicc/` vs `MEDDPICC/`) and ensures consistent references across the framework.

---

## 3. Methodology Files & Naming

### 3.1 Runtime Methodology Knowledge (primary source)

Normalized, company-specific methodology data lives in:
`sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/`

**Example (Sandler):**
`sample-data/Runtime/_Shared/knowledge/methodologies/Sandler/stage_inventory__Sandler.md`

**Example (Generic):**
`sample-data/Runtime/_Shared/knowledge/methodologies/Generic/stage_inventory__Generic.md`

Required structure (frontmatter):

```yaml
---
methodology: "Sandler"
version: "1.0"

stages:
  - id: 1
    key: "01_discovery"
    label: "Stage 1 - Discovery"
    exit_criteria:
      - "Pain identified and quantified"
      - "Budget discussed"
    required_artifacts:
      - "discovery_notes"
      - "stakeholder_map"
    risk_indicators:
      - "No explicit pain"
      - "No budget access"

  - id: 2
    key: "02_solutioning"
    label: "Stage 2 - Solutioning"
    exit_criteria: []
    required_artifacts: []
    risk_indicators: []

global_risks:
  - "No clear Economic Buyer"
  - "Single-threaded in org"

question_frameworks:
  discovery:
    - "Walk me through your current process for &"
    - "What happens today when &?"
  budget:
    - "How have you funded similar initiatives?"
---
```

Required keys:
- `methodology` (string)
- `stages` (array of objects with `id`, `key`, `label`)
- Each stage: `exit_criteria`, `required_artifacts`, `risk_indicators` (arrays; may be empty)
- Optional: `global_risks`, `question_frameworks`

### 3.2 Framework Methodology Specs (optional meta)

High-level definitions live in:
`Framework/Methodologies/{Methodology}.md`
and/or
`Framework/Methodologies/METHODOLOGY_SPEC.md`

These are meta docs (background, theory, examples).
Agents/skills should prefer runtime `stage_inventory` files for actual logic.

---

## 4. Loader Pattern (Pseudocode)

All agents/skills that care about methodology should follow this pattern:

1. **Read deal frontmatter** from
   `sample-data/Runtime/Sessions/{DEAL_NAME}/deal.md`

2. **Determine methodology name**
   ```
   method = lower(deal.methodology || "generic")
   ```

3. **Resolve adapter folder**
   ```
   if method == "sandler"      � "sample-data/Runtime/_Shared/knowledge/methodologies/Sandler/"
   if method == "meddpicc"     � ".../methodologies/MEDDPICC/"
   if method == "hybrid"       � ".../methodologies/Hybrid/"
   else                        � ".../methodologies/Generic/"
   ```

4. **Load stage inventory file**
   - Expected file name: `stage_inventory__{Methodology}.md`
   - If missing, fall back to Generic (see �5)

5. **Map current stage**
   - Try exact label match: `deal.stage` vs `stage.label`
   - Else try numeric prefix: `deal.stage` starts with `"2 -"` � `id:2`
   - Else use `stage_num` if provided
   - Else default to first stage in list

6. **Expose a mental "methodology context"** (for the prompt), e.g.:
   ```
   For this conversation, treat the methodology context as:
   " name: Sandler
   " current_stage: 2 / "Stage 2 - Solutioning"
   " exit_criteria: [&]
   " required_artifacts: [&]
   " risk_indicators: [&]
   " question_frameworks: {&}
   ```

7. **Use this context** to drive coaching, questions, artifacts, etc.

**Important:** This is a pattern for how Claude should reason, not a runtime API. When you write agent/skill specs, literally describe these steps.

---

## 5. Fallback Rules

Agents/skills must not crash due to methodology issues. Use these rules:

1. **Missing `methodology` in deal.md**
   - Treat as `"Generic"` methodology

2. **Adapter folder missing**
   - First try to fall back to `sample-data/Runtime/_Shared/knowledge/methodologies/Generic/stage_inventory__Generic.md` if it exists
   - If Generic adapter also missing, use hardcoded Generic defaults:
     ```yaml
     stages:
       - {id:1, key:"01_discovery",   label:"Discovery"}
       - {id:2, key:"02_solutioning", label:"Solutioning"}
       - {id:3, key:"03_evaluation",  label:"Evaluation"}
       - {id:4, key:"04_negotiation", label:"Negotiation"}
       - {id:5, key:"05_commit",      label:"Commit/Close"}
     ```

3. **Stage inventory file missing or malformed**
   - Fall back to Generic adapter if exists, otherwise use hardcoded Generic stage list above
   - Treat `exit_criteria`, `required_artifacts`, `risk_indicators` as empty arrays

4. **Stage mapping fails**
   - Set:
     ```
     current_stage.id: null
     current_stage.key: "unknown"
     current_stage.label: deal.stage
     ```
   - Still proceed with generic B2B best practices

---

## 6. How Existing Components Should Use This

### 6.1 Coach Agent

In `.claude/skills/coach/SKILL.md`, ensure the spec says:
- Read deal frontmatter, including `methodology` and `stage`
- Load the appropriate stage inventory file as described in this protocol
- Use:
  - `current_stage.exit_criteria` to validate stage health
  - `current_stage.required_artifacts` to check which artifacts exist / are missing
  - `current_stage.risk_indicators` to seed the risk register
  - `question_frameworks` to generate stage-appropriate questions

Coach should not hard-code Sandler terminology or stage names.

### 6.2 prep_discovery Skill

In `.claude/skills/prep-discovery/SKILL.md`, ensure:
- It reads `methodology` from the deal
- Loads the same stage inventory file
- Uses:
  - Stage `exit_criteria` � desired outcomes for the meeting
  - `question_frameworks` � discovery question list
  - `required_artifacts` � follow-up artifacts to generate

### 6.3 Other Skills (later)

When implementing new skills (`exec_readout`, `onsite_prep`, `handover_builder`, etc.):
- Add a short step: "Load methodology data per `methodology_loader.md`"
- Use the stage inventory instead of inventing stage logic locally

---

## 7. How to Add a New Methodology

1. **Create adapter folder:**
   ```
   sample-data/Runtime/_Shared/knowledge/methodologies/MEDDPICC/
   ```

2. **Add stage inventory file:**
   ```
   sample-data/Runtime/_Shared/knowledge/methodologies/MEDDPICC/stage_inventory__MEDDPICC.md
   ```

3. **Follow the same structure** as the Sandler example (`stages`, `exit_criteria`, etc.)

4. **In deal.md frontmatter**, set:
   ```yaml
   methodology: "MEDDPICC"
   ```

5. All methodology-aware agents/skills will now adapt automatically, as long as they follow this protocol.

---

## 8. Summary

- This file defines how to load and use methodologies.
- Agents/skills describe these steps in their own specs instead of inventing new patterns.
- **Today:** Sandler works.
- **Tomorrow:** MEDDPICC / Hybrid / Custom can plug in without changing core logic.

---

## 9. Example: Sandler Stage Inventory Structure

See working example at:
`sample-data/Runtime/_Shared/knowledge/methodologies/Sandler/stage_inventory__Sandler.md`

Key features:
- 7 Sandler stages (Bonding & Rapport � Post-Sell)
- Each stage has: exit criteria, required artifacts, risk indicators, momentum signals
- Question frameworks for Pain Funnel, Budget discussion, Decision mapping
- Global risks applicable across all stages

This structure enables dynamic methodology-aware behavior as demonstrated in the Sandler coaching test with example deals.
