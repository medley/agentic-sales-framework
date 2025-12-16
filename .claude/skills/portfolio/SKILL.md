---
name: portfolio
description: Multi-deal portfolio analysis across all active opportunities. Generates executive summary with deal health dashboard, at-risk deals, pipeline rollup, and recommended focus areas. Use for pipeline reviews, weekly reports, forecast preparation, or portfolio-level coaching.
allowed-tools: [Read, Glob, Write]
license: "MIT - See LICENSE.md"
metadata:
  version: "1.0"
---

# Portfolio

## Overview

Scans all active deals in `sample-data/Runtime/Sessions/` and generates a portfolio-level health report with deal-by-deal status, pipeline metrics, at-risk deals, and recommended actions. Simple aggregation workflow (no complex reasoning or subagents required).

## Core Principles

1. **All Active Deals** - Scans all `deal.md` files in Sessions/ (excludes Archive/ and _TEMPLATES/)
2. **Health Scoring** - Red/Yellow/Green based on stage, activity recency, stakeholder gaps, timeline pressure
3. **Pipeline Rollup** - Total ACV, weighted pipeline (ACV × probability), stage distribution
4. **Risk Flagging** - Stale deals (14+ days), champion gaps, close date pressure
5. **Actionable** - Specific focus areas with affected deals and recommended actions

## When to Use This Skill

**Activate when:**
- Weekly pipeline reviews or forecast preparation
- User asks: "Show me my portfolio", "What deals need attention?", "Pipeline status?"
- Before QBR (Quarterly Business Review) or leadership sync
- Portfolio-level coaching needed (vs. single-deal coaching via `coach` skill)
- Identifying which deals to prioritize this week

**Do NOT use for:**
- Single-deal deep-dive (use `coach` skill instead)
- Generating deal-specific artifacts like emails or agendas (use `sales_communications` or `prep-discovery`)
- Document conversion (use `convert_and_file` skill)

## Workflow

### Step 1: Discover All Deals

1. **Scan for deal files:**
   - Use Glob: `sample-data/Runtime/Sessions/*/deal.md`
   - Exclude: `sample-data/Runtime/Sessions/Archive/**`
   - Exclude: `sample-data/Runtime/Sessions/_TEMPLATES/**`

2. **Count active deals:**
   - If 0 deals found → Output message: "No active deals found. Create deals using deal_intake skill or template."
   - If 1-50 deals → Proceed with analysis
   - If 50+ deals → Warn that output may be large, consider filtering by stage or close date

### Step 2: Load Each Deal

For each `deal.md` found:

1. **Read frontmatter (if present):**
   - `deal_id` or `company_name` (deal identifier)
   - `stage` (current stage number or name)
   - `acv` (Annual Contract Value or deal size)
   - `close_date` (expected close date)
   - `probability` (forecast probability %, default: stage-based if missing)
   - `last_updated` (timestamp of last deal.md update)

2. **Read body:**
   - Current stage and health status
   - Stakeholder map (Economic Buyer, Champion, Technical, Legal/Procurement)
   - Recent history (last 3-5 interactions)
   - Known risks

3. **Parse recent activity:**
   - If history section exists → Extract last activity date
   - If no history → Use `last_updated` from frontmatter or file modification date
   - Calculate days since last activity

4. **Build deal summary object:**
   - `company_name`, `stage`, `acv`, `close_date`, `probability`, `last_activity_date`, `days_since_activity`
   - `stakeholder_status`: Economic Buyer present? Champion present?
   - `health_score`: Calculated in Step 3

**Error handling:**
- Malformed frontmatter → Attempt body parse, use defaults (stage: 1, probability: 10%)
- Missing ACV → Note as "TBD" in output
- Missing close date → Note as "TBD" in output
- Empty history → Last activity = file creation date

### Step 3: Calculate Deal Health

For each deal, assign health score based on:

**🟢 Green (Healthy):**
- Last activity < 7 days
- Champion AND Economic Buyer identified
- Stage appropriate for close date timeline (e.g., not Stage 1 with close date in 2 weeks)
- No critical gaps flagged in deal.md risks section

**🟡 Yellow (Needs Attention):**
- Last activity 7-14 days
- Champion OR Economic Buyer identified (but not both)
- Close date approaching (< 30 days) with stage < 5 (Negotiate)
- Some gaps flagged but not critical

**🔴 Red (At Risk):**
- Last activity > 14 days (stale)
- Neither Champion nor Economic Buyer identified
- Close date passed without deal.md update
- Deal in same stage > 30 days (typical: 14-21 days per stage)
- Critical risks flagged in deal.md (champion departure, budget unconfirmed, competition winning)

**Algorithm:**
```
if days_since_activity > 14 OR (close_date < today AND stage != Won):
  health = Red
elif days_since_activity > 7 OR champion_missing OR economic_buyer_missing:
  health = Yellow
else:
  health = Green
```

### Step 4: Aggregate Portfolio Metrics

Calculate portfolio-level statistics:

1. **Pipeline metrics:**
   - Total Pipeline: Sum of all ACV values (across all stages)
   - Weighted Pipeline: Sum of (ACV × probability) for all deals
   - Avg Deal Size: Total ACV / Deal Count
   - Deals Closing This Quarter: Count of deals with close_date in current quarter

2. **Stage distribution:**
   - Count of deals per stage (1-7)
   - Total ACV per stage
   - Avg probability per stage

3. **Health distribution:**
   - Count of Green / Yellow / Red deals
   - % of pipeline in each health category

4. **At-Risk analysis:**
   - Count of Red deals
   - Top 3-5 Red deals by ACV or strategic importance
   - Stale deals (no activity > 14 days)

5. **Forecast categories (optional):**
   - **Best Case:** Deals with probability ≥ 75%
   - **Commit:** Deals with probability ≥ 50%
   - **Pipeline:** All active deals
   - **Omitted:** Deals with probability < 25% or stale > 30 days

### Step 5: Identify Focus Areas

Based on portfolio analysis, recommend 2-4 focus areas:

**Common patterns:**
- **Stale Deals:** If 3+ deals have no activity > 14 days → "Re-engage stale deals or disqualify"
- **Champion Gaps:** If 5+ deals missing Champion → "Cultivate champions in key deals"
- **Economic Buyer Gaps:** If 5+ deals missing EB → "Request Economic Buyer introductions"
- **Close Date Pressure:** If 3+ deals closing this quarter in Stage < 5 → "Accelerate late-stage deals"
- **Pipeline Imbalance:** If 80%+ of pipeline in Stage 1-2 → "Advance early-stage deals or add new pipeline"

For each focus area:
- List affected deals (company names)
- Recommend specific action (what to do)
- Suggest skill if applicable (e.g., `coach` for at-risk deals, `prep-discovery` for stale Stage 1-2)

### Step 6: Generate Chat Output

**Purpose:** Provide concise portfolio summary for chat/UI display.

**Format:**
- Heading: `# Chat Output`
- Single markdown code fence containing dashboard summary (5-7 bullets)
- NO full report, NO detailed tables

**Content:**
- Pipeline overview (total, weighted, deal count)
- Health distribution (Red/Yellow/Green counts)
- Top 2-3 at-risk deals
- Top 1-2 focus areas

**Example:**
```markdown
# Chat Output

```markdown
**Portfolio Dashboard - 12 Active Deals**
- **Pipeline:** $3.2M total | $1.8M weighted
- **Health:** 🟢 7 deals | 🟡 3 deals | 🔴 2 deals
- **At Risk:** Acme Corp ($500K, stale 25 days), GlobalPharma ($350K, no EB)
- **Focus:** 5 deals need Economic Buyer engagement, 3 deals stale >14 days
- **Next:** Run /coach on Acme + GlobalPharma, re-engage stale deals
```
```

### Step 7: Generate Artifact Output (Full Portfolio Report)

**Purpose:** Create the complete portfolio report for storage.

**Format:**
- Heading: `# Artifact Output`
- Single markdown code fence containing full report with frontmatter

**Content structure:**

1. **YAML frontmatter:**
   ```yaml
   ---
   generated_by: portfolio
   generated_on: {ISO_TIMESTAMP}  # YYYY-MM-DDTHH:MM:SSZ
   deal_count: {COUNT}
   total_pipeline: {ACV_SUM}
   weighted_pipeline: {ACV_WEIGHTED}
   sources:
     - sample-data/Runtime/Sessions/{DEAL1}/deal.md
     - sample-data/Runtime/Sessions/{DEAL2}/deal.md
     - [... list all scanned deals]
   ---
   ```

2. **Report body:**

   ```markdown
   # Portfolio Status Report

   **Generated:** {DATE} | **Active Deals:** {COUNT} | **Total Pipeline:** ${TOTAL} | **Weighted:** ${WEIGHTED}

   ## Executive Summary
   [2-3 sentence snapshot: health distribution, top concern, key recommendation]

   ## Pipeline Overview
   | Metric | Value |
   |--------|-------|
   | Total Pipeline | ${TOTAL_ACV} |
   | Weighted Pipeline | ${WEIGHTED} (based on probability) |
   | Active Deals | {COUNT} |
   | Avg Deal Size | ${AVG_ACV} |
   | Deals Closing This Quarter | {COUNT} |
   | Health: 🟢 Green / 🟡 Yellow / 🔴 Red | {G_COUNT} / {Y_COUNT} / {R_COUNT} |

   ## Deal Health Dashboard
   | Company | Stage | ACV | Close Date | Health | Last Activity | Key Gap |
   |---------|-------|-----|------------|--------|---------------|---------|
   | {Name}  | {X}   | ${Y}| {Date}     | 🟢/🟡/🔴 | {Days ago}    | {Gap}   |

   **Sort by:** Red first, then Yellow, then Green; within each health category, sort by ACV descending

   ## Stage Distribution
   | Stage | Count | Total ACV | Avg Probability |
   |-------|-------|-----------|-----------------|
   | 1 - Discover | {COUNT} | ${ACV} | {AVG}% |
   | 2 - Qualify | {COUNT} | ${ACV} | {AVG}% |
   | 3 - Propose | {COUNT} | ${ACV} | {AVG}% |
   | 4 - Select | {COUNT} | ${ACV} | {AVG}% |
   | 5 - Negotiate | {COUNT} | ${ACV} | {AVG}% |
   | 6 - Close | {COUNT} | ${ACV} | {AVG}% |
   | 7 - Won | {COUNT} | ${ACV} | N/A |

   ## At-Risk Deals (Require Immediate Attention)

   ### 🔴 High Priority ({RED_COUNT} deals)
   1. **{Company Name}** - ${ACV} - Stage {X}
      - Risk: {Specific issue - stale 20+ days, no EB, champion departed, etc.}
      - Action: {What to do next}
      - Owner: {AE name from deal.md if available}

   ## Focus Areas

   **1. {Focus Area Title}**
   - **Affected deals:** {Company1}, {Company2}, {Company3} ({COUNT} total)
   - **Action:** {Specific recommendation - re-engage, qualify budget, request EB intro, etc.}
   - **Suggested skill:** `{skill-name}` (if applicable)

   **2. {Focus Area Title}**
   - **Affected deals:** [...]
   - **Action:** [...]

   ## Stale Deals (No Activity > 14 Days)
   - **{Company Name}** - Last activity: {DATE} ({DAYS_AGO} days ago)
     - Stage: {X} | ACV: ${Y} | Action: {Re-engage or disqualify}

   ## Forecast Summary (Optional)
   | Category | Count | ACV |
   |----------|-------|-----|
   | Best Case (≥75%) | {COUNT} | ${ACV} |
   | Commit (≥50%) | {COUNT} | ${ACV} |
   | Pipeline (All) | {COUNT} | ${ACV} |

   ## Next Steps
   1. Run `coach` skill on top 3 Red deals ({Company1}, {Company2}, {Company3})
   2. Re-engage stale deals or disqualify to clean pipeline
   3. Request Economic Buyer introductions for {COUNT} deals missing EB
   ```

### Step 8: Emit Structured JSON Summary

**Purpose:** Provide machine-readable summary for API/Next.js app consumption.

**Format:**
- Code fence with label: ` ```json summary `
- This is the THIRD and FINAL section of the three-section envelope

**CRITICAL Output Order:**
1. `# Chat Output` (Step 6)
2. `# Artifact Output` (Step 7)
3. ` ```json summary` (Step 8 - this step)
4. Nothing else after the closing fence

**JSON Schema:** Portfolio-specific schema

```json
{
  "totalDeals": 12,
  "atRiskCount": 2,
  "healthyCount": 7,
  "totalPipeline": 3200000,
  "weightedPipeline": 1800000,
  "summaryBullets": [
    "12 active deals, $3.2M total pipeline",
    "7 healthy, 3 yellow, 2 at-risk",
    "Top focus: Economic Buyer engagement (5 deals)"
  ],
  "atRiskDeals": ["Acme Corp", "GlobalPharma"],
  "recommendedFocus": [
    "Run /coach on Acme + GlobalPharma",
    "Re-engage 3 stale deals",
    "Request EB intros for 5 deals"
  ]
}
```

**Validation:**
- ✅ Valid JSON - passes JSON.parse()
- ✅ All required fields: totalDeals, atRiskCount, healthyCount, totalPipeline, weightedPipeline, summaryBullets, atRiskDeals, recommendedFocus
- ✅ Nothing after closing fence

### Step 9: Write Output File

**Write ONLY the Artifact Output content (with frontmatter) to the file:**
   - Path: `sample-data/Runtime/portfolio_report_{ISO_DATE}.md`

**Quality checks before writing:**
- ✅ All deals scanned (count matches expected)
- ✅ Health scores calculated for all deals
- ✅ Pipeline metrics accurate (sum ACV, weighted correctly)
- ✅ At-risk deals identified with specific risks
- ✅ Focus areas actionable (not vague)
- ✅ Sources list all scanned deal.md files

## Error Handling

| Error | Severity | Behavior | Fallback | Output Note |
|-------|----------|----------|----------|-------------|
| No deals found | WARNING | Output message | N/A | "No active deals found in Sessions/" |
| Deal.md malformed | WARNING | Skip or partial parse | Use defaults | "Data quality issues in {deal}" |
| Missing ACV | INFO | Proceed | Mark as "TBD" | "[Company] - ACV: TBD" |
| Missing close date | INFO | Proceed | Mark as "TBD" | "[Company] - Close Date: TBD" |
| Missing stakeholders | WARNING | Flag as Red | Red health score | "{Company} - Risk: No stakeholders" |
| 50+ deals | WARNING | Proceed but warn | Full analysis | "Large portfolio, consider filtering" |

## Example Use Cases

**Weekly Pipeline Review:**
- User: "Show me my portfolio status"
- Portfolio skill: Scans all deals, outputs health dashboard with Red deals flagged
- User: Runs `coach` skill on top 3 Red deals for deep-dive

**Forecast Preparation:**
- User: "What's my forecast for Q1?"
- Portfolio skill: Calculates weighted pipeline, Best Case/Commit categories
- User: Reviews deals in Commit category, validates probabilities

**QBR Preparation:**
- User: "I need a portfolio report for my QBR"
- Portfolio skill: Generates comprehensive report with stage distribution, trends
- User: Exports report for presentation

## Resources

This skill does not require bundled resources (scripts, references, assets). It's a straightforward aggregation workflow.
