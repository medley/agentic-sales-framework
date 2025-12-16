
# Developer Guide - Agentic Sales Framework

Comprehensive reference for building skills and extending the framework.

---

## Table of Contents

1. [Skills Architecture](#skills-architecture)
2. [Skill Development](#skill-development)
3. [Skill Lifecycle](#skill-lifecycle)
4. [Conversion Pipeline](#conversion-pipeline)
5. [Frontmatter Specifications](#frontmatter-specifications)
6. [Methodology Handling](#methodology-handling)
7. [Plays](#plays)
8. [Quality Standards](#quality-standards)
9. [Error Handling](#error-handling)
10. [Performance Optimization](#performance-optimization)
11. [Development Workflow](#development-workflow)

---

## Skills Architecture

Skills are Claude Code-native workflows in `.claude/skills/` that handle everything from simple file conversions to complex multi-step reasoning. **Your skills already ARE agents** - they use tools, make decisions, and perform multi-step reasoning. Don't add complexity until you hit real problems.

### What Are Skills?

Skills are executable workflows that:
- Combine deal context, knowledge base, and methodology to produce intelligent outputs
- Handle simple operations (file conversion) and complex reasoning (deal coaching, risk assessment)
- Are auto-discovered by Claude Code and invoked via natural language or slash commands
- Use progressive disclosure (SKILL.md → reference.md → subdirectories) to optimize token usage

### Core Philosophy

**Skills do everything agents do:**
- Multi-step reasoning and decision-making
- Multi-source synthesis (combining deal notes, personas, stage guides)
- Contextual recommendations (next actions, artifact suggestions)
- Tool use and workflow orchestration

**When to add complexity:**
- You've built 5+ skills and see clear duplication → extract shared logic
- Token limits are actually hit (not theoretically) → split with progressive disclosure
- Multiple skills need coordination → use Task tool for orchestration

**Don't prematurely optimize.** Start simple, add structure when proven necessary.

---

## Skill Development

### When to Create a Skill

Create a skill when you need to:
- Perform file conversion (playbook → markdown)
- Generate stage-specific artifacts (emails, agendas, briefings)
- Analyze deal health and recommend actions
- Extract and validate structured data
- Coach on methodology-specific criteria

**Rule of thumb:** If you can describe the workflow in clear steps, it's a skill.

### Skill Creation Template

Every skill must have YAML frontmatter for auto-discovery:

```yaml
---
name: skill-name
description: Clear one-line description that helps Claude match user intent
triggers: [optional keywords that map to this skill]
version: 1.0
---

# Skill: skill-name

## Purpose
What problem this solves (1-2 sentences)

## Inputs
- Required: parameter_name (type, description)
- Optional: parameter_name (type, description, default)

## Outputs
- File path(s) generated
- Expected structure

## Execution Flow
1. Step one
2. Step two
3. Step three

## Examples
### Example 1: Use case
Input: ...
Output: ...

### Example 2: Edge case
Input: ...
Output: ...
```

### Skill Naming Rules

**Format:** `lowercase-with-hyphens` (directory name and slug)

**Good examples:**
- `coach` - Simple, clear
- `prep-discovery` - Multi-word, hyphenated
- `convert-and-file` - Descriptive action
- `deal-intake` - Domain-specific

**Bad examples:**
- `coachAgent` - No camelCase
- `prep_discovery` - No underscores
- `Coach` - No capitalization
- `prpdsc` - No abbreviations

**Directory structure:**
```
.claude/skills/
├── coach/
│   └── SKILL.md
├── prep-discovery/
│   ├── SKILL.md
│   └── reference.md
└── convert-and-file/
    ├── SKILL.md
    ├── reference.md
    └── templates/
```

### Choosing Minimal allowed-tools

**Philosophy:** Grant only the tools your skill actually uses. This reduces blast radius if permissions change and makes skill contracts explicit.

**Baseline tools (most skills need these):**
- `Read` - Read deal notes, artifacts, knowledge files
- `Write` - Create new output files
- `Glob` - Find files by pattern

**Optional tools (justify before adding):**
- `Edit` - Modify existing files (rare; most skills create new files)
- `Bash` - Run commands (use sparingly; prefer settings.json permissions for mkdir)
- `Task` - Parallel processing or multi-agent orchestration
- `Grep` - Search file contents (less common; usually Read + parsing is enough)

**How to choose:**

1. **Start with baseline:** `[Read, Write, Glob]`
2. **Add only if needed:**
   - Adding `Task`? Justify: "Processes 10+ files in parallel (Step 3)"
   - Adding `Edit`? Justify: "Updates existing deal.md frontmatter (Step 5)"
   - Adding `Bash`? Justify: "Creates directory structure via mkdir" (consider settings.json instead)
3. **Audit after implementation:** Remove unused tools from frontmatter

**Examples:**

```yaml
# Good: Minimal baseline
name: next-steps
allowed-tools: [Read, Write, Glob]
```

```yaml
# Good: Justified Task usage
name: convert-and-file
allowed-tools: [Read, Write, Glob, Task]  # Task: parallel processing 10+ files (Step 2)
```

```yaml
# Bad: Unused tools included
name: simple-skill
allowed-tools: [Read, Write, Edit, Glob, Bash, Task, Grep]  # Only uses Read/Write
```

**Settings.json vs allowed-tools:**
- **allowed-tools:** Skill-level permissions (what this specific skill can do)
- **settings.json:** Global permissions (applies to all skills)
- Use settings.json for common commands like `mkdir`, `chmod`, `git add`
- Use allowed-tools to restrict per-skill capabilities

**Audit checklist:**
- [ ] Does SKILL.md mention this tool in algorithm/steps?
- [ ] Is there an alternative using baseline tools?
- [ ] Would removing this tool break the skill?
- [ ] If "no" to any: remove the tool from allowed-tools

---

### Progressive Disclosure Checklist

Use progressive disclosure to optimize token usage. Add structure when needed:

**Stage 1: Start Simple (1 file)**
- Create `SKILL.md` with all content
- Use when: Skill is <500 lines, straightforward logic
- Example: `coach`, `portfolio`, `next-steps`

**Stage 2: Add Reference (2 files)**
- Split out `reference.md` with examples and edge cases
- Use when: SKILL.md exceeds 500 lines, examples are lengthy
- Example: `prep-discovery`, `deal-intake`
- Runtime reads only SKILL.md, references loaded on-demand

**Stage 3: Add Subdirectories (3+ files)**
- Create `templates/` for reusable templates
- Create `patterns/` for specialized patterns
- Use when: Multiple related templates/patterns needed
- Example: `convert-and-file`, `sales-communications`

**Decision flow:**
1. Start with single SKILL.md
2. If >500 lines → split out reference.md
3. If 3+ templates → create templates/ subdirectory
4. If specialized patterns → create patterns/ subdirectory

### When Skills Get Complex

**Option 1: Extract shared logic**
- Create utility functions in `.claude/lib/` (if needed)
- Import in multiple skills
- Use when: 3+ skills duplicate same logic

**Option 2: Split into multiple skills**
- Each skill does one thing well
- Chain skills together with Task tool
- Use when: Single skill has 2+ distinct responsibilities

**Option 3: Use Task tool for orchestration**
- Delegate sub-workflows to parallel tasks
- Aggregate results
- Use when: Processing 3+ independent items (see Orchestration Patterns)

**Philosophy:** Resist premature abstraction. Build 5-10 skills first, then refactor if clear patterns emerge.

### Skill Orchestration Patterns

When skills need to process multiple items or coordinate complex workflows, use these patterns:

**Pattern 1: Recommend, Don't Execute**

Most skills should recommend next actions, not auto-execute them:

```markdown
## Recommended Next Steps
1. Run `/prep-discovery` to prepare for Thursday's call
2. Review `artifacts/competitive_analysis.md` before demo
3. Schedule follow-up with CFO using email draft in artifacts/
```

**Why:**
- User maintains control
- Explicit over implicit
- Easier to debug

**Pattern 2: Use Task Tool for Parallel Processing**

When processing 3+ independent items (files, deals, artifacts):

```markdown
## Pattern: Parallel File Processing (3+ files)

1. Detect file count
2. If 3+ files, use Task tool:
   - Launch one task per file (max 5)
   - Each task processes independently
   - Aggregate results after all complete
3. If 1-2 files, process serially (avoid overhead)

Benefits:
- Token isolation (each task: fresh 200K budget)
- 4-5× speedup (parallel execution)
- Consistent quality (no degradation)
- Fault tolerance (one failure doesn't block others)
```

**Example: deal-intake with 5 files**
```
Serial:   15 min, 112K tokens, quality degrades
Parallel: 3 min, 5×25K tokens isolated, consistent
```

**When to use Task tool:**
- 3+ large files (10K+ tokens each)
- Mixed file types (transcripts + CRM + emails)
- Quality-critical scenarios
- Token budget concerns

**When to process serially:**
- 1-2 small files
- Files with cross-dependencies
- Rapid prototyping (avoid orchestration complexity)

See Performance Optimization section for detailed orchestration patterns and benchmarks.

### Skill File Structure

Current skills in `.claude/skills/`:

```
.claude/skills/
├── coach/
│   └── SKILL.md
├── convert-and-file/
│   ├── SKILL.md
│   ├── reference.md
│   └── templates/
├── deal-intake/
│   ├── SKILL.md
│   └── reference.md
├── next-steps/
│   ├── SKILL.md
│   └── reference.md
├── portfolio/
│   └── SKILL.md
├── prep-discovery/
│   ├── SKILL.md
│   ├── reference.md
│   └── templates/
└── sales-communications/
    ├── SKILL.md
    └── patterns/
```

### Invoking Skills

User natural language → Claude Code maps to skill:
- "Convert the playbook" → `convert-and-file` skill
- "Coach me on this deal" → `coach` skill
- "Prep for discovery call" → `prep-discovery` skill
- "What should I do next?" → `next-steps` skill

---

## Skill Lifecycle

Each skill has:
- A `SKILL.md` file in `.claude/skills/{skill_name}/`
- Optional `reference.md` for examples and edge cases
- Optional subdirectories (`templates/`, `patterns/`) for supporting files
- YAML frontmatter for auto-discovery

### Adding a New Skill

1. **Create directory and SKILL.md:**
   ```bash
   mkdir -p .claude/skills/my-skill
   touch .claude/skills/my-skill/SKILL.md
   ```

2. **Add YAML frontmatter:**
   ```yaml
   ---
   name: my-skill
   description: Clear one-line description for auto-discovery
   triggers: [optional, keywords]
   version: 1.0
   ---
   ```

3. **Define skill structure:**
   - **Purpose**: Clear one-line description
   - **Inputs**: Required and optional parameters with types
   - **Outputs**: Files generated and their locations
   - **Execution Flow**: Numbered steps
   - **Examples**: Sample invocations and expected results

4. **Add progressive disclosure (optional):**
   - Create `reference.md` if examples are lengthy
   - Create `templates/` if multiple templates needed
   - Create `patterns/` if specialized patterns needed

5. **Test thoroughly:**
   - Use real deal data from `sample-data/Runtime/Sessions/`
   - Verify outputs match expected structure
   - Check frontmatter is complete
   - Confirm no hardcoded assumptions

6. **Document (optional):**
   - Skill is auto-discovered by Claude Code
   - Add to DEVELOPER_GUIDE if complex patterns emerge

---

## Conversion Pipeline

Detailed protocol for converting input documents (playbooks, personas, battlecards) into structured knowledge.

### Conversion Steps

1. **Source validation**: Verify file exists and is readable
2. **Type detection**: Infer doc_type from content/filename
   - Options: `playbook`, `persona`, `battlecard`, `stage_guide`, `product`, `case_study`, `other`
3. **Extraction**: Pull key facts without interpretation
4. **Validation**: Check for freshness, completeness, accuracy
5. **Augmentation**: Add ONLY non-proprietary best practices, clearly labeled
6. **Gap identification**: Flag missing information or follow-up questions
7. **Action checklist**: Generate "What to do with this file" (3-6 bullets)

### Augmentation Rules

**What to add:**
- Generic sales best practices (e.g., "Include multi-threading in discovery")
- Industry-standard definitions (e.g., "Economic buyer = budget authority")
- Common objection patterns (e.g., "Price objections often mask concerns about...")

**What NOT to add:**
- Hallucinated pricing, dates, roadmaps
- Competitor information not in source
- Specific claims about products/features
- Company-confidential information

All augmentation must be clearly labeled: "**Augmented Context (Best Practices):**"

### Output Location

All converted files go to: `sample-data/Runtime/_Shared/knowledge/`

Filename convention: `{doc_type}_{descriptive_name}.md`

Examples:
- `persona_cfo_pharma.md`
- `battlecard_competitorA_vs_ourproduct.md`
- `stage_guide_discovery.md`

---

## Frontmatter Specifications

### Generated Content Frontmatter

All generated markdown files (briefings, emails, agendas) MUST include:

```yaml
---
generated_by: {skill_name}
generated_on: {ISO_TIMESTAMP}
deal_id: {deal_name}
call_type: {discovery|demo|negotiation|handover|exec|other}
sources: [{list of file paths referenced}]
---
```

Skills may add extra fields (e.g., `artifact_type`, `call_summary_id`) but MUST always include the core fields above.

**Example:**
```yaml
---
generated_by: coach
generated_on: 2025-11-12T14:30:00Z
deal_id: TechCoInc
call_type: discovery
sources:
  - sample-data/Runtime/Sessions/TechCoInc/deal.md
  - sample-data/Runtime/_Shared/knowledge/persona_cfo_pharma.md
  - sample-data/Runtime/_Shared/knowledge/stage_guide_discovery.md
---
```

### Converted Content Frontmatter

Converted documents from input files MUST include:

```yaml
---
source_path: {original file path}
source_type: pdf|docx|xlsx|txt|md
converted_on: {ISO_TIMESTAMP}
doc_type: playbook|persona|battlecard|stage_guide|product|case_study|other
confidence: high|medium|low
validation:
  freshness_hint: "Last updated Q3 2024" or ""
  findings: ["Missing pricing", "Incomplete stakeholder map"]
augmentation:
  scope: "Added generic discovery best practices"
  additions: ["Multi-threading importance", "Champion criteria"]
gaps:
  questions: ["What's the typical sales cycle length?", "Who are key competitors?"]
  suggested_sources: ["Product roadmap", "Competitive analysis doc"]
---
```

**Confidence levels:**
- `high`: Source is official, recent, complete
- `medium`: Source is older or incomplete but usable
- `low`: Source is outdated, fragmented, or questionable

### Deal Note (deal.md) Structure

**Canonical 10-Section Structure** (standardized across templates and skills):

```yaml
---
# Required frontmatter fields (all strings must be quoted)
deal_id: "{{company_name_slug}}"
deal_name: "{{COMPANY_NAME}}"
owner: "{{AE_NAME}}"
stage: ""                    # e.g., "5-Negotiating"
health: ""                   # GREEN | YELLOW | RED
acv: ""                      # e.g., "$127,978.18"
close_date: ""               # e.g., "November 2025 (Expected)"
industry: ""                 # e.g., "Nutrition/Life Sciences"
evaluation_status: ""        # Brief status summary
last_updated: "{{DATE}}"
methodology: "Generic"       # or MEDDPICC | Sandler | Custom
metrics: ""
economic_buyer: ""
decision_criteria: ""
decision_process: ""
pain: ""
champion: ""
competition: ""
---

# 1. Deal Overview
Financial summary, solution scope, timeline, strategic context

# 2. History
Chronological activity log (critical for tracking buyer engagement)

# 3. D1 Tasks (Next 24 Hours)
Action-oriented, urgency-driven tasks

# 4. D7 Tasks (Next 7 Days)
Sales velocity management tasks

# 5. Stakeholder Map
Champion, Economic Buyer, Procurement, Key Stakeholders, Decision Committee

# 6. MEDDPICC Snapshot
Metrics, Economic Buyer, Decision Criteria, Decision Process, Pain, Champion, Competition

# 7. Risks
Implementation risks, deal expansion risks with impact and mitigation

# 8. Next Steps & Mutual Close Plan
Buyer commitments, expansion opportunities

# 9. Generated Artifacts
Audit trail of coaching outputs, emails, agendas with dates and file paths

# 10. Deal Intelligence Summary
Deal health, success factors, expansion strategy, key relationships
```

**Design Rationale (Sales Best Practice):**
- **Action-focused**: D1/D7 tasks drive daily execution and sales velocity
- **Chronological tracking**: History section captures every buyer touchpoint
- **Coaching-ready**: Intelligence Summary provides strategic guidance
- **Audit trail**: Generated Artifacts shows what was created when
- **Risk visibility**: Explicit Risks section for forecast accuracy
- **Buyer commitment tracking**: Next Steps captures mutual commitments

**YAML Quoting Rules:**
- Quote all string values: `acv: "$127,978.18"`, `close_date: "2025-11-15"`
- Quote complex strings with special chars (colons, commas, parentheses)
- Leave numeric fields unquoted if truly numeric: `stage_num: 5`
- Use `""` for empty placeholders or omit the field entirely

**Templates:**
- `Framework/Templates/deal_template.md` - Framework-level template
- `sample-data/Runtime/Sessions/_TEMPLATES/deal_template.md` - Runtime template

Both templates MUST match this canonical structure exactly to ensure skills (coach, portfolio, deal-intake, sales-communications) can read and update deals consistently.

---

## Methodology Handling

The framework is methodology-agnostic. It adapts based on which methodology adapter is present.

### Methodology Adapters

At runtime, methodology data is loaded primarily from normalized stage inventory files under:

`sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md`

`Framework/Methodologies/{Methodology}.md` provides human-readable adapter definitions and meta, not the canonical runtime data.

Each runtime stage inventory defines:
```yaml
stages: [list of sales stages]
exit_criteria: {stage: [criteria bullets]}
risk_indicators: [warning signs]
required_artifacts: {stage: [document types]}
question_frameworks: {stage: [suggested questions]}
```

### Supported Methodologies

- **MEDDPICC**: Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion, Competition
- **Sandler**: Pain, Budget, Decision, Timeline
- **Challenger**: Teach, Tailor, Take Control
- **SPIN**: Situation, Problem, Implication, Need-Payoff
- **Custom**: User-defined

### Applying Methodology

1. Check deal note frontmatter for `methodology` field
2. If specified, load methodology per `Framework/System/methodology_loader.md`:
   - Resolve `{Methodology}` folder under `sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/`
   - Load `stage_inventory__{Methodology}.md` for stages, exit_criteria, required_artifacts, risk_indicators
   - Optionally consult `Framework/Methodologies/{Methodology}.md` for additional narrative/background
3. Apply stage-specific criteria to coaching/prep workflows
4. If not specified, use generic B2B sales best practices (or Generic methodology defaults)

**Example:**
```markdown
Deal note specifies: methodology: sandler

Coach skill reads:
- sample-data/Runtime/_Shared/knowledge/methodologies/sandler/stage_inventory__sandler.md
- Framework/Methodologies/sandler.md (optional background)

Applies: Pain-focused discovery questions, budget qualification early
```

### Fallback Behavior

If no methodology specified or adapter missing:
- Use generic B2B sales best practices
- Focus on stakeholder mapping, pain discovery, value articulation
- Don't force methodology-specific language

---

## Plays

Plays are reusable sales tactics that provide concrete examples and step-by-step guidance for common deal scenarios. Unlike methodologies (which define stage progression), plays are tactical patterns that can be applied at any stage.

### What Are Plays?

Plays are knowledge files in `Framework/Plays/` that capture proven sales tactics with:
- **Triggers**: Deal state patterns that indicate when to use the play
- **Principles**: Core tenets of the tactic (brevity over exhaustive lists)
- **Steps**: Tactical execution sequence
- **Examples**: 3-5 real-world scenarios with specific details (dollar amounts, timelines, personas)
- **Pitfalls**: Common mistakes to avoid

Plays follow Anthropic's multishot learning pattern: provide concrete examples (not fill-in-the-blank templates) so Claude can synthesize deal-specific recommendations.

### Available Plays

**High-priority plays** (address common deal blockers):
1. **executive_engagement** - Economic Buyer access strategy when stuck at mid-level
2. **champion_building** - Internal advocate development when no/weak champion
3. **deal_rescue** - Stalled deal recovery (ghosting, no activity >30 days)
4. **value_realization** - ROI/business case development for CFO approval

**Situational plays** (triggered by specific deal states):
5. **reference** - Social proof/customer validation strategy
6. **multi_threading** - Stakeholder expansion and de-risking
7. **poc** - Proof of value/pilot structure
8. **mutual_action_plan** - Joint buyer-seller success planning
9. **contract_negotiation** - Legal/procurement navigation
10. **committee_selling** - Group consensus building
11. **budget_creation** - No-budget scenario tactics
12. **security_compliance** - Security review navigation

### Play Structure

Each play uses XML-tagged structure for LLM parsing:

```markdown
---
name: "Play Name"
type: "sales_play"
owner: "Welf Ludwig"
version: "1.0.0"
license: "MIT - See LICENSE.md"
---

# Play Name: One-line Description

<triggers>
- trigger_1 (when to use)
- trigger_2 (deal state pattern)
- trigger_3 (stakeholder gap)
</triggers>

<principles>
- **Principle 1**: Brief explanation
- **Principle 2**: Brief explanation
</principles>

<steps>
1. **Step name**: Description
   - Sub-bullet
   - Sub-bullet
2. **Step name**: Description
</steps>

<examples>
<example id="example_name">
**Context**: Deal size, industry, situation

**Situation**: Specific challenge

**Action**: What was done

**Outcome**: Result

**Key moves**: Why it worked
</example>

[... 3-5 total examples]
</examples>

<pitfalls>
- **Pitfall 1**: What to avoid and why
- **Pitfall 2**: Common mistake
</pitfalls>
```

### Plays vs Methodologies vs Skills

**Methodologies** (Framework/Methodologies/, sample-data/.../methodologies/):
- Define sales stage progression (Discover → Qualify → Propose → Select → Negotiate → Close → Won)
- Provide exit criteria per stage
- Framework-level guidance (what stages exist, what qualifies as stage progression)

**Plays** (Framework/Plays/):
- Tactical execution patterns (how to get Economic Buyer access, how to rescue stalled deal)
- Situational (triggered by deal state, not stage)
- Portable knowledge (generic SaaS sales tactics, no company-specific logic)
- Examples-driven (3-5 concrete scenarios for Claude to learn from)

**Skills** (.claude/skills/):
- Executable workflows (coach, portfolio, deal_intake, prep-discovery)
- Invoke plays, methodologies, and knowledge base to generate outputs
- Orchestration layer (combine deal context + methodology + plays → coaching report)

**Example workflow:**
1. User runs `coach` skill on a deal
2. Coach loads methodology (Sandler) → understands stage 2 = Pain Discovery
3. Coach analyzes deal state → detects `no_economic_buyer` trigger
4. Coach loads `executive_engagement` play
5. Coach synthesizes recommendation: "Per executive_engagement play: Request warm intro from champion to CFO for 15-min business review. Prepare 3-slide exec briefing (problem/solution/proof)."

### How Coach Skill Uses Plays

The `coach` skill automatically discovers and applies plays:

**Step 3.5 in coach workflow** (added after deal state analysis):
1. **Discover plays**: Glob `Framework/Plays/*.md`
2. **Match triggers**: Compare deal state to play triggers
   - `no_economic_buyer` → executive_engagement
   - `weak_champion` → champion_building
   - `no_activity_30_days` → deal_rescue
   - `pricing_objection` → value_realization
3. **Load matched plays** (limit 2-3 most relevant)
4. **Synthesize recommendations**: Map play steps to D1/D7 actions
5. **Cite in coaching report**: Reference play name in action rationale

**Example synthesis:**
```markdown
Deal state: no_economic_buyer, weak_champion, pricing_objection

Matched plays: executive_engagement, champion_building, value_realization

D1 Actions (from plays):
- [ ] **EOD Today** - Ask champion for warm intro to CFO (Per executive_engagement play)
  - Why: No Economic Buyer identified (Stage 3 risk)
- [ ] **Tomorrow** - Test champion strength: Request last quarter's budget data (Per champion_building play)
  - Why: Champion lukewarm (hasn't driven internal meetings)

D7 Actions:
- [ ] **This Week** - Build CFO business case: Quantify current state cost vs solution ROI (Per value_realization play)
  - Why: CFO approval needed for >$500K deals
```

### Creating New Plays

**When to create a play:**
- You've executed a tactic successfully 3+ times across different deals
- The pattern is reusable (not company-specific or one-time)
- You can provide 3-5 concrete examples with specific details

**Play creation process:**
1. **Identify pattern**: What recurring deal challenge does this solve?
2. **Define triggers**: What deal state indicates this play is relevant?
3. **Extract principles**: What are the 3-5 core tenets? (Keep brief)
4. **Document steps**: Tactical execution sequence (5-7 steps max)
5. **Provide examples**: 3-5 real-world scenarios with:
   - Context (deal size, industry, stage)
   - Situation (specific challenge)
   - Action (what was done step-by-step)
   - Outcome (result)
   - Key moves (why it worked)
6. **List pitfalls**: Common mistakes to avoid (3-5 max)

**Quality bar:**
- Examples use specific numbers ($800K deal, 45-day pilot, 3 FTE saved)
- Examples show variety (different industries, deal sizes, personas)
- Steps are actionable (not vague "build relationships")
- Total length: 100-150 lines (balances detail vs brevity)

**Where to save:**
- Generic plays: `Framework/Plays/play_name.md` (portable across companies)
- Company-specific plays: `sample-data/Runtime/_Shared/knowledge/plays/play_name.md` (optional, not currently implemented)

### Play Customization (Future)

**Current implementation**: Generic plays in Framework/Plays/ (portable, version-controlled)

**Future extension** (not yet implemented):
- Company-specific plays in sample-data/.../knowledge/plays/
- Coach checks custom location first, falls back to generic
- Allows customization without modifying Framework/ (follows 3-layer architecture)

**Example:**
```
Framework/Plays/executive_engagement.md (generic SaaS tactics)
sample-data/.../knowledge/plays/executive_engagement.md (company-specific variant with internal exec access process)

Coach loads custom if exists, otherwise generic.
```

---

## Quality Standards

### Actionability

**Good:**
- "Schedule 30-min call with Sarah Chen (VP Operations) by Friday to discuss integration concerns. Draft agenda focusing on API requirements and timeline."

**Bad:**
- "Follow up with stakeholders about their concerns."

### Specificity

**Good:**
- "Risk: No executive sponsor identified. Recommended action: Request introduction to CFO through current champion (Alex Johnson, Director IT) in Thursday's call."

**Bad:**
- "Need to find a champion higher up."

### Ready-to-Use Content

Generated emails, agendas, and documents should be:
- Complete (no placeholders like `[INSERT NAME]`)
- Contextual (references actual people, dates, commitments)
- Stylistically appropriate (matches user's voice if style corpus available)

**Exception:** If critical information is genuinely missing, use `{{PLACEHOLDER}}` and flag it explicitly.

### Source Attribution

Every claim or recommendation should reference the source:
- Deal history: `(per deal note: 3 discovery calls completed)`
- Knowledge base: `(based on persona_cfo_pharma.md: CFOs prioritize ROI)`
- Methodology: `(MEDDPICC exit criteria: Economic buyer confirmed)`

---

## Error Handling

### Missing Input Files

**If input file not found:**
```
ERROR: Deal note not found at sample-data/Runtime/Sessions/TechCoInc/deal.md

Suggested action: Create deal note from template:
cp sample-data/Runtime/Sessions/_TEMPLATES/deal_template.md sample-data/Runtime/Sessions/TechCoInc/deal.md
```

### Empty Knowledge Base

**If no converted knowledge exists:**
```
WARNING: Knowledge base is empty. Coach skill will use generic best practices.

Recommended: Convert company playbooks and personas:
"Convert the playbook in sample-data/input/"
```

### Malformed Deal Note

**If deal note can't be parsed:**
```
WARNING: Deal note malformed. Missing required sections: Stakeholders, Stage

Attempting to proceed with available data. Outputs may be incomplete.
Recommended: Review deal note structure against template.
```

### Unclear Instructions

**If skill execution is ambiguous:**
```
CLARIFICATION NEEDED: Methodology selection unclear.

Question: Should I use MEDDPICC (specified in deal note) or Sandler (user preference)?
Please specify or I'll default to deal note methodology.
```

---

## Performance Optimization

### Targeted File Reads

**Don't do this:**
```
Read all files in sample-data/Runtime/_Shared/knowledge/**
```

**Do this:**
```
Read only:
- Knowledge/persona_*.md (if coaching needs persona info)
- Knowledge/stage_guide_{current_stage}.md (if prepping for specific stage)
```

### Caching

If running multiple operations in one session:
- Load methodology once, cache in memory
- Reuse knowledge base scan results
- Batch deal note reads for portfolio status

### Knowledge Base Organization

Encourage users to:
- Use descriptive filenames (not `doc1.md`, `doc2.md`)
- Include doc_type in frontmatter for filtering
- Archive old/outdated knowledge (move to `Knowledge/Archive/`)

### Parallel Processing with Task Tool

When skills need to process 3+ independent items, use Task tool for parallel execution.

#### Pattern: Parallel File Processing

**Use case:** Processing 3+ files (deal intake, conversion pipeline)

**Problem with serial processing:**
- Long execution time (4 files × 3 min = 12 min)
- Token pressure (80K+ tokens, quality degrades)
- No fault tolerance (one error blocks all)

**Solution:** Use Task tool to process files in parallel (max 5 tasks)

**Implementation:**

1. **Detect file count:** If 3+ files, use parallel pattern
2. **Launch parallel tasks** (one per file, max 5):
   ```
   For each file:
     Task tool with prompt:
     "Process {file_path} for {skill_name}.
      Return summary markdown (don't write to disk)."
   ```
3. **Wait for completion** (blocking mode)
4. **Aggregate results:**
   - Write all artifacts
   - Consolidate data (apply precedence rules)
   - Update deal.md once

**Benefits:**
- Token isolation (each task: fresh 200K budget)
- 4-5× speedup (parallel execution)
- Consistent quality (no degradation)
- Fault tolerance (one failure doesn't block others)

**Example: 5 files**
```
Serial:   15 min, 112K tokens, quality degraded in files 3-4
Parallel: 3 min, 5×25K tokens isolated, consistent quality
Speedup:  5× faster
```

#### Pattern: Sequential Dependencies

**Use case:** Pipeline where skills depend on outputs

**Example:** coach skill needs deal.md from deal-intake

**Implementation:**

1. **Task 1:** deal-intake (blocking wait)
2. **After Task 1 completes:**
   - Task 2: coach (parallel)
   - Task 3: prep-discovery (parallel)
3. **Both Tasks 2+3 read same deal.md**

**Timeline:**
```
0:00 - Launch deal-intake (5 files, parallel sub-tasks)
3:00 - deal-intake complete, deal.md updated
3:00 - Launch coach + prep-discovery (parallel)
5:00 - Both complete
Total: 5 minutes
```

#### Pattern: Batching for Scale

**Use case:** 20+ files to process

**Strategy:** Cap at 5 tasks, batch files strategically

**Priority order:**
1. CRM exports (Task 1 dedicated)
2. Quotes (Task 2)
3. Transcripts (Tasks 3-5, divide evenly)
4. Emails (batch with Task 5)

**Example: 26 files (1 CRM + 20 transcripts + 3 quotes + 2 emails)**

```
Task 1: CRM export (priority)
Task 2: 3 quotes
Task 3: Transcripts 1-7
Task 4: Transcripts 8-14
Task 5: Transcripts 15-20 + 2 emails
```

**Performance:**
```
Serial:   ~60 min (26 files × 2.5 min avg)
Parallel: ~12 min (5 tasks processing ~5 files each)
Speedup:  5× faster
```

#### Decision Matrix

| Files | Strategy | Task Count | Notes |
|-------|----------|------------|-------|
| 1-2 | Serial | 0 | Process directly, no overhead |
| 3-5 | Parallel (unbatched) | N (one per file) | One task per file |
| 6-10 | Parallel (batched) | 5 tasks | Each task processes 1-2 files |
| 10-50 | Parallel (batched) | 5 tasks | Each task processes 2-10 files |
| 50+ | Parallel (batched) | 5 tasks | Each task processes 10+ files |

#### When to Use Task Tool

**Use parallel tasks when:**
- 3+ large files (10K+ tokens each)
- Mixed file types (transcripts + CRM + emails)
- Quality-critical scenarios
- Token budget concerns

**Use serial processing when:**
- 1-2 small files
- Files with cross-dependencies
- Rapid prototyping (avoid orchestration complexity)

**Why cap at 5 tasks:**
1. Proven pattern from convert-and-file (58 PDFs → 5 tasks)
2. Orchestration overhead grows non-linearly
3. API rate limit safety margin
4. Diminishing returns beyond 5 concurrent

#### Performance Benchmarks

| Scenario | Serial | Parallel (5 tasks) | Speedup |
|----------|--------|-------------------|---------|
| 5 files, 50K tokens total | 15 min | 3 min | 5× |
| 12 files, 120K tokens | 30 min | 6 min | 5× |
| 50 files, 500K tokens | 2 hours | 25 min | ~5× |

**Speedup plateaus at ~5× due to:**
- Orchestration overhead (launching tasks, waiting)
- Aggregation step (still serial)
- Diminishing returns (API latency becomes bottleneck)

---

## Development Workflow

### Adding New Skills

1. **Create directory and SKILL.md:**
   ```bash
   mkdir -p .claude/skills/{skill_name}
   touch .claude/skills/{skill_name}/SKILL.md
   ```

2. **Add YAML frontmatter:**
   ```yaml
   ---
   name: skill-name
   description: Clear one-line description for auto-discovery
   triggers: [optional, keywords]
   version: 1.0
   ---
   ```

3. **Document structure:**
   - **Purpose:** What problem this solves (1-2 sentences)
   - **Inputs:** Required and optional parameters with types
   - **Outputs:** Files generated and their locations
   - **Execution Flow:** Numbered steps
   - **Examples:** At least 2 use cases

4. **Add progressive disclosure (as needed):**
   - `reference.md` - Examples and edge cases (if SKILL.md >500 lines)
   - `templates/` - Template files (if 3+ templates)
   - `patterns/` - Reusable patterns (if specialized patterns needed)

5. **Test thoroughly:**
   - Use real deal data from `sample-data/Runtime/Sessions/`
   - Verify outputs match expected structure
   - Check frontmatter is complete
   - Confirm no hardcoded assumptions

6. **Validate portability:**
   - Works without company-specific hardcoding
   - Uses variables: `{USER_DATA}`, `{DEAL_ID}`, `{DATE}`
   - No absolute paths to company data

7. **Auto-discovery:**
   - Skill appears as slash command in Claude Code automatically
   - Document in DEVELOPER_GUIDE if complex patterns emerge

### Adding New Methodologies

1. **Create adapter:** `Framework/Methodologies/{methodology_name}.md`
2. **Define structure:**
   ```yaml
   stages: [stage1, stage2, ...]
   exit_criteria:
     stage1: [criterion1, criterion2]
     stage2: [...]
   risk_indicators: [warning1, warning2]
   recommended_artifacts:
     stage1: [doc_type1, doc_type2]
   ```
3. **Test:** Run coach skill with methodology specified in deal note
4. **Document:** Add to methodology overview in this guide

### Testing with Sample Data

Use real deal data in `sample-data/Runtime/Sessions/` for testing:
```
sample-data/Runtime/Sessions/
├── _TEMPLATES/               # Use for creating test deals
│   └── deal_template.md
└── TestDeal/                # Create test deals here
    ├── deal.md
    └── artifacts/
```

Before testing with production deals:
1. Create test deal from template
2. Test skill with test deal
3. Verify outputs match expected structure
4. Check frontmatter is complete
5. Confirm no hardcoded assumptions
6. Clean up test deals when done

### Version Control

**What to commit:**
- All `.claude/` files (skills, hooks, settings)
- All `Framework/` files (methodologies, templates, documentation)
- `CLAUDE.md` (root-level config)

**What NOT to commit:**
- `sample-data/` (gitignored - contains company IP)
- Personal API keys
- `.env` files
- `.claude/settings.local.json` (user-specific overrides)

---

## Extensibility

### Plugin Architecture (Future)

The framework is designed for extensibility:
- Skills can invoke other skills (via natural language or slash commands)
- Skills can chain together using Task tool
- Methodologies can be composed (hybrid approaches)

**Example:** Custom methodology that combines MEDDPICC qualification with Sandler pain discovery:
```yaml
# Framework/Methodologies/hybrid_meddpicc_sandler.md
stages: [Pain Discovery, Technical Validation, Economic Validation, Decision]
pain_framework: sandler
qualification_framework: meddpicc
```

### Future Integrations

Potential extensions:
- CRM integration (Salesforce, HubSpot)
- Calendar integration (schedule prep calls automatically)
- Email integration (auto-generate follow-ups)

---

## Best Practices Summary

1. **Keep it portable:** No hardcoded company logic in Framework/
2. **Use frontmatter:** Every generated file needs provenance
3. **Be specific:** Actionable outputs, not generic advice
4. **Cite sources:** Reference actual files in knowledge base
5. **Test first:** Sample data before real company data
6. **Document clearly:** Future you (or buyers) need to understand
7. **Optimize reads:** Don't scan entire knowledge base unnecessarily
8. **Follow conventions:** Filenames, paths, frontmatter standards
9. **Start simple:** Single SKILL.md, add structure when proven necessary
10. **Resist premature abstraction:** Build 5-10 skills before refactoring

---

## Questions?

If this guide doesn't answer your question:
1. Check `CLAUDE.md` for high-level overview
2. Check `architecture_visual.md` for system design
3. Check specific skill specs in `.claude/skills/*/SKILL.md` for implementation details
4. Add your question to this guide for future reference
