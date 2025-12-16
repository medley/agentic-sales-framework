
# System Architecture - Agentic Sales Framework

**Version:** 1.0
**Last Updated:** 2025-11-12
**Status:** Stable

---

## Overview

The Agentic Sales Framework is a personal AI sales operating system built on a **four-layer architecture** that ensures company data remains isolated, execution logic leverages Claude Code's native features, and knowledge remains portable and reusable.

**Core Design Principles:**
1. **Separation of Concerns** - Company data, execution logic, and knowledge are strictly separated
2. **Claude Code-Native** - Built for Claude Code's agent/skill system (requires Claude Code)
3. **Methodology Agnostic** - Adapts to any B2B sales process via plug-in adapters
4. **Local-First** - No cloud dependencies, user owns all data
5. **AI-Native** - Built for LLM orchestration, not as an afterthought
6. **Knowledge Portability** - Methodologies and templates remain tool-agnostic

---

## System Context

```
┌─────────────────────────────────────────────────────────────┐
│                   AGENTIC SALES FRAMEWORK                    │
│                    (Claude Code-Native)                      │
│                                                               │
│  User → Claude Code → Skills → Artifacts                    │
│           ↓                                                   │
│      CLAUDE.md (operating rules, auto-loaded)               │
│           ↓                                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Layer 1: sample-data/ (Private, Gitignored)          │  │
│  │   - input/ (raw documents)                            │  │
│  │   - Runtime/_Shared/knowledge/ (structured)           │  │
│  │   - Runtime/Sessions/{Deal}/ (deal workspaces)        │  │
│  └──────────────────────────────────────────────────────┘  │
│           ↕                                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Layer 2: .claude/ (Execution Layer)                  │  │
│  │   - skills/ (simple to complex reasoning)             │  │
│  │   - hooks/ (validation and safety)                    │  │
│  │   - settings.json (Claude Code config)                │  │
│  └──────────────────────────────────────────────────────┘  │
│           ↕                                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Layer 3: Framework/ (Knowledge Layer)                │  │
│  │   - Methodologies/ (sales process adapters)           │  │
│  │   - Templates/ (reusable structures)                  │  │
│  │   - System/ (documentation)                           │  │
│  │   - Style/ (brand and voice guidelines)               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Architectural Layers

### Layer 1: sample-data/ (Data Layer)

**Purpose:** Isolate all company-specific and proprietary information

**Location:** `sample-data/` (root level, gitignored)

**Structure:**
```
sample-data/
├── Input/                    # Raw source documents
│   ├── playbooks/
│   ├── personas/
│   ├── battlecards/
│   └── transcripts/
└── Runtime/
    ├── _Shared/
    │   └── Knowledge/        # Converted, structured markdown
    └── Sessions/
        ├── {DealName}/       # Per-deal workspace
        │   ├── deal.md       # Deal source of truth
        │   └── artifacts/    # Generated content
        └── _TEMPLATES/       # Blank templates
```

**Key Characteristics:**
- **Never versioned** - Excluded via `.gitignore`
- **Company-specific** - Contains proprietary information
- **Stays behind** - When you change companies, this stays
- **Read/Write** - Agents and skills can read and write here

**Design Rationale:**
This layer exists to create a clean separation between company IP (which has legal/privacy constraints) and framework logic (which is portable). By isolating all company data, we ensure:
- Framework can be open-sourced safely
- No risk of leaking proprietary information
- Easy to demo without exposing real company data
- Clear ownership boundaries (company owns data, you own framework)

---

### Layer 2: .claude/ (Execution Layer)

**Purpose:** Claude Code-native execution layer - skills, hooks, and automation

**Location:** `.claude/` (root level, versioned in git)

**Structure:**
```
.claude/
├── skills/                   # All capabilities (simple to complex)
│   ├── coach/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── convert-and-file/
│   ├── deal-intake/
│   ├── next-steps/
│   ├── portfolio/
│   ├── prep-discovery/
│   └── sales-communications/
├── hooks/                    # Safety and validation
│   ├── protect_framework.py
│   ├── protect_input.py
│   ├── validate_frontmatter_enhanced.py
│   └── hooks.json
├── settings.json            # Claude Code configuration
└── settings.local.json      # User-specific settings
```

**Key Characteristics:**
- **Claude Code-native** - Designed for Claude Code's skill system
- **Version controlled** - All execution logic tracked in git
- **Auto-discovered** - Skills appear as slash commands automatically
- **Hooks enabled** - Safety validations run on file operations
- **Portable with caveat** - Requires Claude Code to function

**Design Rationale:**
This layer provides the "brain" of the system - the skills that actually do the work. By using Claude Code's native `.claude/` structure:
- Get auto-discovery of skills (no custom implementation needed)
- Leverage hooks for safety (prevent writing to wrong locations)
- Better UX (invoke skills with `/coach`, `/prep-discovery`)
- Cleaner separation between execution logic and knowledge
- Skills range from simple workflows to complex multi-step reasoning

**Trade-off:** The framework now requires Claude Code to function. This is an intentional choice prioritizing:
- Faster shipping (leverage existing tooling)
- Better UX (native Claude Code integration)
- Maintainability (less custom code)

Over:
- Tool-agnostic portability (would work with any LLM tool)

The knowledge layer (Framework/) remains tool-agnostic and portable.

---

### Layer 3: Framework/ (Knowledge Layer)

**Purpose:** Portable, reusable knowledge - methodologies, templates, documentation

**Location:** `Framework/` (root level, versioned in git)

**Structure:**
```
Framework/
├── Methodologies/            # Sales process adapters
│   ├── sandler_adapter.yaml
│   ├── sandler.md
│   └── METHODOLOGY_SPEC.md
├── Templates/                # Reusable structures
│   ├── deal_template.md
│   ├── agenda_customer.md
│   ├── agenda_internal.md
│   ├── email_followup.md
│   └── handover_doc.md
├── Style/                    # Brand and voice
│   ├── email_style_guide.md
│   ├── email_style_corpus.md
│   └── STYLE_BUILDER.md
├── Prompts/                  # Reusable prompt patterns
│   └── library.md
└── System/                   # Documentation
    ├── ARCHITECTURE.md       # This file
    ├── DEVELOPER_GUIDE.md
    ├── SETUP.md
    ├── methodology_loader.md
    └── frontmatter_spec.md
```

**Key Characteristics:**
- **Tool-agnostic** - No Claude Code dependencies
- **Portable** - Take to next company, works anywhere
- **Company-agnostic** - Zero hardcoded company logic
- **Read-only** - Agents/skills read specs, don't modify them (enforced by hooks)
- **Version controlled** - All changes tracked in git

**Design Rationale:**
This layer is YOUR portable intellectual property. It contains knowledge that's valuable regardless of which AI tool you use:
- Sales methodologies work with any LLM
- Templates are just markdown files
- Documentation explains concepts, not tool specifics
- Style guides can be referenced by any email generator

By keeping Framework/ separate from .claude/:
- Can migrate to different AI tools if needed
- Can share methodologies across teams/companies
- Can sell/open-source the knowledge layer independently
- Clear separation: execution (.claude/) vs knowledge (Framework/)

---

## Component Architecture

### Skills-Only Architecture

**Definition:** All capabilities are implemented as skills, ranging from simple workflows to complex multi-step reasoning.

**Why Skills-Only:**

The framework uses a skills-only architecture because:

1. **Skills Already ARE Agents** - They have everything needed for complex reasoning:
   - Multi-step execution patterns
   - Tool access (Read, Write, Grep, Bash)
   - Context loading and synthesis
   - Methodology-aware decision making

2. **Simpler Mental Model** - One concept instead of two:
   - No "agent vs skill" distinction to learn
   - Clearer execution model (invoke skill → get result)
   - Easier to extend (all capabilities follow same pattern)

3. **Auto-Discovery** - Skills in `.claude/skills/` automatically appear as slash commands
   - Natural language invocation (`/coach`, `/prep-discovery`)
   - No registration or configuration needed
   - Better UX than separate agent layer

4. **User Control** - Skills recommend next actions but don't auto-execute:
   - Predictable behavior (no runaway chains)
   - Lower API costs (explicit execution)
   - Easier debugging (clear execution path)

**When We'd Need Task-Spawned Sub-Agents:**

The framework could spawn sub-agents via the Task tool for:
- **Meta-orchestration** - Coordinating multiple skills across long workflows
- **Long-lived sessions** - Maintaining context across multiple user interactions
- **Parallel execution** - Running independent analyses concurrently

This is NOT currently implemented. Current skills handle complexity through:
- Progressive disclosure (references/ subdirectories)
- Skill orchestration (recommend other skills)
- Phased execution (multi-step workflows in single skill)

---

### Skill Complexity Spectrum

Skills range from simple aggregation to complex multi-step reasoning:

**Simple Skills (100-200 lines):**
- **sales_communications** - Template filling for stage-specific emails
- **portfolio** - Scan deal directories, aggregate status
- Single-phase execution
- Minimal decision logic
- Quick execution (<30s)

**Complex Skills (200-400 lines):**
- **coach** - Multi-source synthesis, methodology-aware gap analysis
- **next-steps** - Strategic action planning with stage transitions
- **prep-discovery** - Comprehensive briefing generation
- Multi-phase execution (Plan → Analyze → Generate)
- Conditional logic based on methodology
- References multiple knowledge sources
- Execution time: 30s-2min

**Compound Skills (400+ lines):**
- **deal-intake** - Two-phase workflow (normalize → synthesize)
- Should be refactored into smaller skills
- Execution time: 2-5min

**Size Guidelines:**
- **SKILL.md max:** 400 lines (beyond this, split into multiple skills)
- **references/*.md max:** 300 lines per file
- **When to extract:** Reusable logic used by 2+ skills → extract to Framework/
- **When to split:** Skill has 3+ distinct phases → consider separate skills

---

### Progressive Disclosure Pattern

Complex skills use `references/` subdirectories to keep core logic focused:

```
.claude/skills/coach/
├── SKILL.md                           # 250 lines: core workflow
└── references/
    ├── gap_analysis_framework.md      # 200 lines: methodology rules
    ├── risk_detection_patterns.md     # 180 lines: deal risk signals
    └── action_prioritization.md       # 150 lines: D1/D7 framework
```

**Conditional Loading Guards:**

Skills only load references when needed:

```markdown
# In SKILL.md

## Phase 1: Load Context
- Read deal.md
- Load methodology from Runtime/_Shared/knowledge/methodologies/{Name}/

## Phase 2: Analyze Gaps (if methodology specified)
<reference file=".claude/skills/coach/references/gap_analysis_framework.md" />

IF no methodology specified:
- Use generic B2B best practices
- Skip methodology-specific exit criteria
```

**Benefits:**
- Core skill remains readable (250 lines vs 800 lines)
- Reference content reusable across skills
- Faster loading for simple cases
- Easier to maintain and update

---

### Skill Orchestration Pattern

Skills can recommend other skills but NEVER auto-execute them:

```markdown
# Example from coach skill output:

## Recommended Next Actions

D1 (Today):
- Run `/prep-discovery` to generate internal brief + customer agenda
- Run `/sales-communications discovery_confirm` for confirmation email

D7 (This Week):
- Run `/next-steps` after discovery call to plan demo prep
- Update deal.md with new pain points discovered

Why: Gives user control, prevents runaway chains, clearer debugging
```

**Anti-Pattern (DO NOT DO):**
```markdown
# ❌ WRONG - Don't auto-execute skills
- Invoke Task tool to run prep-discovery skill
- Chain to sales_communications skill
- Auto-update deal.md with results
```

**Rationale:**
- User maintains control over execution flow
- Predictable API costs (no unexpected chains)
- Easier to debug (explicit invocations visible)
- Clear provenance (each skill writes its own frontmatter)

---

### Example Skills (Detailed)

**portfolio (Simple Aggregation Skill):**

```
Purpose: Scan all deal directories, generate portfolio summary
Complexity: 150 lines, single-phase execution
Pattern:
  1. List directories in sample-data/Runtime/Sessions/
  2. For each deal: Read deal.md frontmatter (stage, close_date, value)
  3. Categorize: Active, At-Risk, Closed
  4. Generate summary markdown with:
     - Executive summary (pipeline value, close probability)
     - Deal health dashboard (count by stage)
     - At-risk deals (flagged with reasons)
     - Recommended focus areas
  5. Write to _Shared/portfolio_status_{DATE}.md

Why simple: No complex reasoning, pure aggregation and categorization
Execution: ~15-30 seconds
```

**coach (Complex Reasoning Skill):**

```
Purpose: Analyze single deal, provide methodology-aware coaching
Complexity: 250 lines + 530 lines in references/
Pattern:
  1. LOAD PHASE
     - Read deal.md (current stage, history, stakeholders)
     - Load methodology stage inventory from Runtime/_Shared/knowledge/
     - Scan _Shared/knowledge/ for relevant personas, battlecards

  2. ANALYZE PHASE (uses references/gap_analysis_framework.md)
     - Check stage exit criteria against deal state
     - Identify gaps (missing info, incomplete qualification)
     - Detect risk patterns (uses references/risk_detection_patterns.md)
     - Assess deal health (Red/Yellow/Green)

  3. RECOMMEND PHASE (uses references/action_prioritization.md)
     - Generate D1 actions (today)
     - Generate D7 actions (this week)
     - Recommend specific skills to run next
     - Cite sources for every recommendation

  4. OUTPUT PHASE
     - Write Sessions/{DEAL}/coach_output_{DATE}.md
     - Include frontmatter with sources
     - Format for readability (emoji indicators, clear structure)

Why complex: Multi-source synthesis, methodology rules, strategic judgment
Execution: ~45-90 seconds
```

**Progressive Disclosure in coach:**
- Core SKILL.md: 250 lines (workflow logic)
- references/gap_analysis_framework.md: 200 lines (loaded if methodology specified)
- references/risk_detection_patterns.md: 180 lines (loaded for all deals)
- references/action_prioritization.md: 150 lines (loaded in recommend phase)

Total: 780 lines, but only loads what's needed for each execution

---

## Data Flow Architecture

### End-to-End Pipeline

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐
│  Input   │────▶│  Convert &   │────▶│  Knowledge  │
│  Files   │     │  File Skill  │     │    Base     │
└──────────┘     └──────────────┘     └─────────────┘
                                              │
                                              ▼
┌──────────┐     ┌──────────────┐     ┌─────────────┐
│Generated │◀────│    Skills    │◀────│    Deal     │
│Artifacts │     │              │     │   Sessions  │
└──────────┘     └──────────────┘     └─────────────┘
```

### Step-by-Step Flow

**1. User adds documents**
```
sample-data/input/playbook.pdf
```

**2. Conversion skill processes**
```
User: "Convert playbook.pdf"
↓
convert-and-file skill:
  - Extracts content
  - Validates information
  - Adds augmentation (labeled)
  - Identifies gaps
↓
Writes: sample-data/Runtime/_Shared/knowledge/playbook_sales_process.md
```

**3. Knowledge base grows**
```
sample-data/Runtime/_Shared/knowledge/
├── playbook_sales_process.md
├── persona_cfo.md
├── battlecard_competitor_a.md
└── stage_guide_discovery.md
```

**4. User creates deal**
```
sample-data/Runtime/Sessions/TechCoInc/deal.md
  - Frontmatter: methodology, stage, close_date
  - Body: Stakeholders, history, context
```

**5. Skill analyzes deal**
```
User: "Prep me for discovery with TechCoInc"
↓
coach skill:
  - Reads: deal.md
  - Reads: Knowledge/persona_*.md, stage_guide_discovery.md
  - Loads: Methodologies/sandler.md (specified in deal frontmatter)
  - Analyzes: gaps, risks, opportunities
↓
Writes: sample-data/Runtime/Sessions/TechCoInc/coach_output_2025-11-12.md
```

**6. Skill generates artifact**
```
User: "Generate discovery agenda"
↓
prep_discovery skill:
  - Reads: deal.md, deal_coach_discovery_*.md
  - Fills: Templates/agenda_template.md
  - Applies: Sandler methodology questions
↓
Writes: sample-data/Runtime/Sessions/TechCoInc/agenda_discovery_2025-11-12.md
```

---

## Methodology Architecture

### Plugin System

Methodologies are **adapters** that modify agent behavior without changing agent code.

**Location:** `Framework/Methodologies/{name}.md`

**Schema:**
```yaml
---
methodology: Sandler
version: 1.0
---

## Stages
- pain_discovery
- budget_qualification
- decision_process
- fulfillment

## Exit Criteria

### pain_discovery
- At least 3 pain points identified and quantified
- Economic impact documented
- Compelling event identified

### budget_qualification
- Budget range confirmed
- Approval process mapped
- Timeline for budget availability

## Risk Indicators
- Prospect won't discuss budget
- No pain beyond "nice to have"
- Multiple stakeholders, no internal champion
- Long sales cycle with no compelling event

## Recommended Artifacts

### pain_discovery
- pain_summary.md
- stakeholder_map.md
- discovery_agenda.md

### budget_qualification
- roi_calculator.md
- pricing_scenarios.md
```

### How Skills Use Methodologies

**1. Skill loads methodology**
```
Read deal.md frontmatter:
  methodology: sandler

Load: Framework/Methodologies/sandler.md
```

**2. Skill applies methodology rules**
```
Current stage: pain_discovery

Check exit criteria:
  ✓ 3 pain points identified
  ✗ Economic impact not documented  ← GAP
  ✗ No compelling event identified  ← GAP

Assess risks:
  - "No pain beyond nice to have" risk detected
  - Evidence: deal note mentions "nice to have" 3 times
```

**3. Skill generates methodology-aware output**
```
Recommendations:
  D1: Quantify economic impact of top pain ($X lost per month)
  D7: Identify compelling event (budget cycle, compliance deadline)

Suggested next actions:
  - Run roi_calculator with pain points as inputs
  - Generate pain_summary artifact
```

**Design Decision: Methodologies are Markdown, Not Code**

We use markdown specs (not Python/JS code) because:
- Non-technical users can create methodologies
- Easy to version and diff
- Human-readable for debugging
- LLMs parse markdown naturally

**Trade-off:** Less flexible than code, but gains simplicity and portability.

---

## Frontmatter Architecture

### Provenance Tracking

Every generated file includes YAML frontmatter for full traceability.

**Required Fields:**
```yaml
---
generated_by: {skill_name}
generated_on: {ISO_TIMESTAMP}
deal_id: {deal_name}
call_type: {discovery|demo|negotiation|status}
sources:
  - sample-data/Runtime/Sessions/TechCoInc/deal.md
  - sample-data/Runtime/_Shared/knowledge/persona_cfo.md
  - Framework/Methodologies/sandler.md
---
```

**Design Rationale:**

**Why frontmatter?**
- Structured metadata (machine-readable)
- Standard markdown format
- Obsidian-friendly (renders in UI)
- Git-diffable

**Why track sources?**
- Debugging (why did agent recommend X?)
- Auditing (which knowledge informed this?)
- Reproducibility (re-run with same inputs)
- Trust (user can verify claims)

**Why ISO timestamps?**
- Sortable lexicographically
- Timezone-aware
- Industry standard
- Works across all platforms

---

## Security Architecture

### Threat Model

**Threats We Defend Against:**
1. **Data leakage** - Company data accidentally committed to git
2. **Prompt injection** - Malicious content in uploaded files
3. **Hallucination** - AI making up facts about company
4. **Credential exposure** - API keys in files

**Defenses:**

**1. Data Isolation**
- sample-data/ gitignored by default
- Framework/ cannot write to itself (read-only)
- Clear documentation warns about git add

**2. Augmentation Labeling**
- All AI-added content clearly marked
- Source extraction vs augmentation separated
- Users can easily identify LLM additions

**3. Source Citation**
- Every claim cites source file
- Frontmatter tracks which files informed output
- Users verify by checking sources

**4. Local-First Architecture**
- No cloud dependencies required
- Data never leaves user's machine (unless user exports)
- API keys managed by Claude Code, not stored in files

### Privacy Considerations

**What's Private:**
- All sample-data/ content
- Deal notes and stakeholder information
- Email drafts and call transcripts
- Generated artifacts

**What's Shareable:**
- Framework/ logic (completely generic)
- Example methodology adapters
- System documentation

---

## Extensibility Architecture

### Adding New Components

**New Skills:**
1. Create `.claude/skills/{skill_name}/SKILL.md`
2. Add YAML frontmatter (name, description, allowed-tools)
3. Define workflow logic, examples, error handling
4. For complex skills: Create `references/` subdirectory for supporting content
5. Test with real deals
6. Skills auto-discovered by Claude Code as slash commands

**New Methodologies:**
1. Create `Framework/Methodologies/{name}.md`
2. Define: Stages, Exit Criteria, Risks, Artifacts
3. Create stage inventory in `sample-data/Runtime/_Shared/knowledge/methodologies/{Name}/`
4. Test with coach skill
5. Document methodology in DEVELOPER_GUIDE

### Future Extension Points

**Planned:**
- Calendar sync for automated prep scheduling
- Email integration for follow-up automation
- Team features (shared knowledge base)

**Not Planned:**
- Cloud hosting (local-first is a feature)
- Web dashboard (CLI-first philosophy)
- Mobile app (desktop-focused workflow)

---

## Design Decisions & Trade-offs

### Decision: Three Layers

**Architecture:** sample-data/ (data) + .claude/ (execution) + Framework/ (knowledge)

**Rationale:**
- Clear separation of concerns
- sample-data stays with company (gitignored)
- Framework is portable IP (versioned)
- .claude/ is Claude Code native (auto-discovery)

---

### Decision: Local-First vs Cloud-Based

**Considered:** Building a web app with centralized database

**Chose:** Local-first with markdown files

**Rationale:**
- User owns their data (no vendor lock-in)
- Works offline
- No monthly hosting costs
- Git-friendly (version control built-in)
- Privacy-first (data never leaves machine)

**Trade-off:** No team collaboration features (yet), but individual productivity is maximized

---

### Decision: Markdown Specs vs Code

**Considered:** Writing skills in Python/TypeScript

**Chose:** Markdown specifications interpreted by Claude Code

**Rationale:**
- LLMs parse markdown natively
- Non-technical users can modify specs
- Easy to version control and diff
- Cross-platform (no runtime dependencies)

**Trade-off:** Less programmatic control, but gains simplicity and AI-native design

---

### Decision: Skills Recommend Other Skills vs Auto-Execute

**Considered:** Skills automatically chaining to other skills

**Chose:** Skills recommend, user confirms

**Rationale:**
- User maintains control
- Easier debugging (explicit execution)
- Lower API costs (no runaway chains)
- Clearer mental model

**Trade-off:** Extra user interaction, but higher trust and predictability

---

## Version History

**v1.1 (2025-11-15)** - Skills-only architecture
- Migrated to skills-only architecture (removed separate agent layer)
- Documented skill complexity spectrum (simple to complex)
- Added progressive disclosure pattern for complex skills
- Updated all examples to reflect skills-only approach

**v1.0 (2025-11-12)** - Initial architecture
- Four-layer separation established
- Agent vs Skill distinction defined
- Methodology plugin system designed
- Frontmatter schema finalized
- Local-first security model

**Future versions will track here**

---

## Related Documentation

- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Detailed protocols for building skills
- **[architecture_visual.md](architecture_visual.md)** - Visual diagrams and flow charts
- **[SETUP.md](SETUP.md)** - Installation and configuration guide
- **[ROADMAP.md](ROADMAP.md)** - Development plan and milestones
- **[claude.md](../../claude.md)** - Core operating rules (auto-loaded by Claude Code)

---

## Summary

The Agentic Sales Framework uses a four-layer architecture to achieve:

1. **Safety** - Company data stays isolated and private (Layer 1: sample-data/)
2. **Power** - Claude Code-native execution with skills-only architecture (Layer 2: .claude/)
3. **Portability** - Tool-agnostic knowledge layer (Layer 3: Framework/)
4. **Extensibility** - Easy to add methodologies and skills (simple to complex)
5. **Trust** - Full provenance tracking and source attribution

**Skills-Only Architecture:** All capabilities are skills, ranging from simple workflows to complex multi-step reasoning. This provides:
- Simpler mental model (one concept instead of two)
- Auto-discovery (skills appear as slash commands)
- User control (skills recommend, don't auto-execute)
- Progressive disclosure (complex skills use references/ subdirectories)

**Key Trade-off:** Execution layer (.claude/) requires Claude Code, but knowledge layer (Framework/) remains portable. This prioritizes:
- Better UX (native Claude Code features)
- Faster shipping (leverage existing tooling)
- Cleaner separation (execution vs knowledge)

Over:
- Full tool-agnostic portability (would work with any LLM tool)

This architecture is the foundation for a personal AI sales operating system that respects data ownership, leverages best-in-class tooling, and delivers genuine productivity gains.