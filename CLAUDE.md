---
version: 0.5
last_updated: 2025-11-14
copyright: "© 2025 Welf Ludwig"
license: "MIT - See LICENSE.md"
bootstrap_behavior: |
  Claude Code reads this file at initialization to:
  1. Load architecture and operating rules.
  2. Auto-discover skills in .claude/skills/
  3. Respect sample-data as read-only and Framework as portable IP.
  4. Follow file and naming conventions defined below.
  5. Enable hooks in .claude/hooks/ for safety validations.
---

# Agentic Sales Framework

Personal AI sales operating system that maintains deal context and generates stage-specific artifacts on demand. Built with four-layer Claude Code-native architecture for power and portability.

---

## Architecture

**See:** [Framework/System/architecture_visual.md](Framework/System/architecture_visual.md) for detailed visual.

### Three-Layer Architecture (CRITICAL)

1. **sample-data/** - Company IP, never versioned, stays at company when you leave
2. **.claude/** - Claude Code-native execution layer (skills, hooks)
3. **Framework/** - Portable knowledge layer (methodologies, templates, docs)

**Key Directories:**
- `sample-data/input/` - Drop source files (PDFs, DOCX)
- `sample-data/Runtime/_Shared/knowledge/` - Structured, validated content
- `sample-data/Runtime/Sessions/{DEAL}/` - Per-deal workspaces
- `.claude/skills/` - Deterministic workflows (auto-discovered as slash commands)
  - Simple workflows and complex multi-step reasoning
  - YAML frontmatter enables auto-discovery based on descriptions
  - Progressive disclosure: metadata → SKILL.md → references/
- `.claude/hooks/` - Safety validations (prevent writing to wrong locations)
- `Framework/Methodologies/` - Sales methodology adapters (Sandler included, extensible)

**Claude Code Integration:** This framework requires Claude Code to function. Skills leverage Claude Code's native `.claude/` structure for auto-discovery, hooks, and settings.

See [ARCHITECTURE.md](Framework/System/ARCHITECTURE.md) for complete design.

---

## Session Tracking Override

**IMPORTANT:** This framework uses native artifact provenance tracking via frontmatter metadata.

**Session tracking protocol applies ONLY when:**
- Modifying framework code itself (developing new skills, updating documentation, refactoring)
- Implementing new features for the framework (multi-step development work)
- Tasks are software development on the framework, not artifact generation

**Session tracking does NOT apply when:**
- Generating artifacts via skills (emails, agendas, coaching reports, discovery briefs)
- Running skill invocations (skills handle their own provenance via frontmatter)
- Creating deal-specific content in `sample-data/Runtime/Sessions/{DEAL}/`

**Rationale:** Every artifact already includes comprehensive provenance:
```yaml
---
generated_by: {skill_name}
generated_on: {ISO_TIMESTAMP}
deal_id: {company_name}
sources: [{file_paths_used}]
methodology: {if_applicable}
---
```

This frontmatter provides the same context as session tracking but is embedded directly in artifacts. Adding `.ai/SESSION.md` updates for 15-90 second artifact generation would add unnecessary overhead without improving traceability.

**When in doubt:** If you're generating a deliverable artifact (email, agenda, report), skip session tracking. If you're modifying `.claude/skills/` or `Framework/` code, use session tracking.

---

## Operating Rules

### File Handling (CRITICAL)

**NEVER modify:**
- `sample-data/input/**` (source files are immutable)
- `.git/**`
- `Framework/**` (read-only; skills read specs, don't modify them)

**CRITICAL:** Skills MUST NOT write to `Framework/**`. All generated artifacts and converted knowledge go under `sample-data/Runtime/**` only

**Read/Write paths:**
- READ: `sample-data/input/` for conversion
- WRITE: `sample-data/Runtime/_Shared/knowledge/` (converted docs)
- WRITE: `sample-data/Runtime/Sessions/{DEAL}/` (deal work)

### Frontmatter Requirement

All generated files MUST start with YAML frontmatter:
```yaml
---
generated_by: {skill_name}
generated_on: {ISO_TIMESTAMP}
deal_id: {company_name}
sources: [{file_paths_used}]
---
```

See [DEVELOPER_GUIDE.md](Framework/System/DEVELOPER_GUIDE.md) for complete spec.

### Critical Constraints

- Framework must work with ANY company's data (no hardcoded company logic)
- Use variables: `{USER_DATA}`, `{DEAL_ID}`, `{DATE}` not absolute paths
- Never embed company-specific logic in Framework layer
- All generated content must be specific and actionable (no generic advice)
- Draft emails/agendas ready to send (not templates with blanks)
- Cite actual file paths in sources field

### Skills

Executable workflows in `.claude/skills/` are auto-discovered by Claude Code. Invoke skills with natural language requests - Claude will automatically select and execute the appropriate skill.

**Available skills:**
- Type `/skills list` in Claude Code to see all available skills
- Each skill has complete instructions in its own `SKILL.md` file

See [DEVELOPER_GUIDE.md](Framework/System/DEVELOPER_GUIDE.md) for skill development protocols.

### Methodology Handling

If deal note frontmatter specifies `methodology: {name}`, load methodology per `Framework/System/methodology_loader.md`:

- **Primary source:** Runtime stage inventory file at
  `sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md`
- **Optional meta:** `Framework/Methodologies/{Methodology}.md` (background/theory only, read-only)
- **Fallback:** If no methodology specified or no adapter/stage inventory available, use Generic methodology behavior described in `methodology_loader.md`

### Security

- Keep company data in sample-data/ (gitignored)

---

## Developer Environment

**Requirements:**
- Claude Code installed and configured
- Node.js 18+ (for Claude Code runtime)
- Git (recommended for version control)
- Text editor: VS Code, Obsidian, or any markdown editor

**Unexpected Behaviors:**
- sample-data/ is gitignored by default (contains company IP)
- Framework/ is versioned (your portable IP)
- Paths are case-sensitive: `input/` not `Input/`, `knowledge/` not `Knowledge/`
- If no methodology specified in deal note, system defaults to generic B2B practices

---

## Documentation Map

- **[ARCHITECTURE.md](Framework/System/ARCHITECTURE.md)** - System design and technical decisions
- **[DEVELOPER_GUIDE.md](Framework/System/DEVELOPER_GUIDE.md)** - Implementation protocols and specs
- **[SETUP.md](Framework/System/SETUP.md)** - Installation, usage guide, and workflows
- **[architecture_visual.md](Framework/System/architecture_visual.md)** - Visual diagrams

For extending the framework:
- All capabilities (simple and complex) go in `.claude/skills/`
- Skills support both simple workflows and complex multi-step reasoning
- See DEVELOPER_GUIDE.md for skill development protocols
