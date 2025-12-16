---
license: "MIT - See LICENSE.md"
name: convert-and-file
description: Converts unstructured sales materials (PDFs, playbooks, methodology docs) into structured markdown knowledge files with provenance tracking and augmentation sections. Use when the user asks you to process files from sample-data/input/ or convert documents into the framework's knowledge base.
allowed-tools: [Read, Write, Glob, Task]
---

# Convert & File — Runtime Specification

**Version:** 1.0
**Purpose:** Transform raw input files into structured, traceable knowledge artifacts for the Agentic Sales Framework
**Reference:** See `reference.md` for detailed examples, edge cases, and troubleshooting

---

## When to Use This Skill

**Activate when:**
- User provides files in `sample-data/input/**` that need processing
- User asks to "convert," "process," "import," or "integrate" sales materials
- Converting playbooks, methodologies, stage definitions, or sales process documentation
- Files need provenance tracking and augmentation labeling

**Do NOT use for:**
- Deal-specific artifacts (call transcripts, quotes, emails) → use `deal_intake` skill
- Simple file reads without conversion → use Read tool directly
- Editing existing knowledge files → use Edit tool
- Quick reference lookups → use Read or Grep tools

---

## Core Principles

1. **Provenance First:** Every output must trace back to specific source files
2. **Fact vs. Inference:** Always separate source facts from LLM-added interpretations
3. **Augmentation Transparency:** Label all LLM-inferred content clearly
4. **Structural Consistency:** Use standard sections and formatting
5. **Methodology Neutrality:** Never embed methodology-specific logic; keep conversion generic
6. **Respect Layer Boundaries:** Write ONLY to `sample-data/Runtime/**`; never modify `Framework/**`

---

## Processing Algorithm

### Step 1: Identify Source Files

1. **Use Glob tool** to find files in `sample-data/input/**`
   - Common patterns: `sample-data/input/**/*.pdf`, `sample-data/input/playbooks/**/*`
   - Filter by extensions: `.pdf`, `.docx`, `.md`, `.txt`, `.pptx`, `.xlsx`

2. **Assess scope:**
   - Single file → Process directly
   - 5-10 related files → Consider parallel processing with Task tool
   - 10+ files → Use parallel agents (3-5 agents, divide files by topic/section)

3. **Document inventory:** Count files, note types, identify logical groupings

---

### Step 2: Parse & Extract Core Facts

**Goal:** Extract factual information only, without interpretation.

1. **Read source file(s)** using Read tool
2. **Extract ONLY factual information:**
   - Definitions, concepts, terminology
   - Process steps, methodologies, frameworks
   - Stage names, exit criteria, required artifacts
   - Techniques, tactics, best practices
   - Checklists, templates, tools
   - Specific metrics, thresholds, quantitative criteria

3. **Organize into logical sections:**
   - Use bullet lists for criteria, checklists, requirements
   - Use tables for stage mappings, comparisons, crosswalks
   - Use code blocks for templates, scripts, example text
   - Use headings to create clear hierarchy (##, ###)

4. **Preserve source language:**
   - Quote key terms exactly as they appear
   - Use the same terminology/naming from source
   - Don't paraphrase unless necessary for clarity

5. **CRITICAL: Do NOT mix source facts with interpretations**
   - Save interpretations for Step 4 (Augmentation)

---

### Step 3: Validate Extracted Information

**Goal:** Document quality issues, inconsistencies, or gaps.

1. **Check for internal inconsistencies:**
   - Do different sections contradict each other?
   - Are definitions used consistently throughout?
   - Do examples match stated principles?

2. **Note ambiguities or unclear sections:**
   - Terms used without definition
   - References to external materials not provided
   - Incomplete processes or missing steps

3. **Flag missing information or gaps:**
   - Stages mentioned but not documented
   - Tools referenced but not described
   - Prerequisites stated but not defined

4. **Document validation issues in dedicated section:**
   ```markdown
   ## Validation Notes
   - Source refers to "DISC profiles" but doesn't define DISC types
   - Page 23 shows 7 stages; page 45 shows 6 stages (discrepancy)
   - Budget discussion techniques reference "Monkey's Paw" without explanation
   ```

5. **Do NOT "fix" issues with your own knowledge** - just document them

---

### Step 4: Augment with LLM Inferences

**Goal:** Add helpful interpretations, examples, and guidance NOT in source material.

1. **Create clearly labeled section:**
   ```markdown
   ## Augmentation (LLM-Inferred)

   > **Notice:** The content in this section contains interpretations, examples,
   > and guidance not explicitly present in source documents. Review and validate
   > before relying on this information.
   ```

2. **Add value-added content:**
   - Interpretations of unclear concepts from source
   - Concrete examples illustrating source concepts
   - General best practices aligned with source principles
   - Crosswalks mapping source methodology to framework's default stages (generic mapping only)
   - Usage guidance: "What to Do With This File" checklists
   - Edge cases not covered in source but logically relevant

3. **Common augmentation sections:**
   - `### General Best Practices` - High-level guidance
   - `### Crosswalk to Default Stage Inventory` - Generic stage mapping
   - `### What to Do With This File` - Usage instructions
   - `### When to Use vs. Avoid` - Situational guidance
   - `### Common Pitfalls` - Mistakes to avoid

4. **Keep augmentation clearly separate:**
   - Use distinct heading structure
   - Always label as "LLM-Inferred" or "Interpretation"
   - Never merge augmented content into source sections

5. **CRITICAL: Keep methodology-agnostic**
   - Don't embed Sandler/MEDDPICC/Challenger-specific logic
   - Provide generic guidance only
   - Methodology-aware reasoning belongs in agents (coach_agent, prep agents)

---

### Step 5: Add Provenance Footer

**Goal:** Make every output file fully traceable to its sources.

**Always append this footer:**
```markdown
---

## Provenance

source_paths:
  - "sample-data/input/path/to/source1.pdf"
  - "sample-data/input/path/to/source2.docx"

converted_by: convert_and_file
converted_at: YYYY-MM-DD
stage_ref: sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md  # or null if not applicable
augmentation_notice: >
  Sections under **Augmentation (LLM-inferred)** contain general guidance not
  explicitly present in source documents. Review before adoption.
```

**Customize each field:**
- `source_paths`: List ALL source files used (relative or absolute paths)
- `converted_at`: Use actual ISO date (YYYY-MM-DD format)
- `stage_ref`: Adjust relative path based on output location
- Add custom fields if needed: `methodology`, `version`, `reviewed_by`, `validation_notes`, `agents_used`

**For parallel agent processing:**
- List all files processed by all agents
- Note: `converted_by: convert_and_file (parallel agent analysis)`
- Include: `agents_used: 5`

---

### Step 6: Determine Output Path

**Goal:** Place output file in appropriate location within framework structure.

**Choose output directory based on content type:**

**Shared Knowledge (primary target):**
- Default: `sample-data/Runtime/_Shared/knowledge/`
- Methodology-specific: `sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/`
- Stage definitions: `sample-data/Runtime/_Shared/knowledge/methodologies/{Methodology}/stage_inventory__{Methodology}.md`

**Framework Documentation (read-only, NOT a write target):**
- `Framework/Methodologies/{Methodology}.md` is maintained by the user as background/meta
- This skill MUST NOT write into `Framework/**`

**Choose filename using naming convention:**
- Stage inventory: `stage_inventory__{Methodology}.md` (e.g., `stage_inventory__Sandler.md`)
- Topic-based: `{doc_type}_{descriptive_name}.md` (e.g., `persona_cfo_pharma.md`)
- Methodology topics: `{topic}_{Methodology}.md` in the appropriate `methodologies/{Methodology}/` directory

**Create directory if needed:**
```bash
mkdir -p "path/to/output/directory"
```

**Verify path doesn't conflict:**
- Use Glob to check for existing file
- Ask user if overwrite is intended
- Suggest versioned filename if preserving old version

---

### Step 7: Write Output File

1. **Use Write tool** to create output file
   - Full absolute path required
   - Include all sections: extracted facts, validation, augmentation, provenance

2. **Verify file structure:**
   - Markdown is well-formed
   - Headings are properly hierarchical
   - Code blocks are properly fenced
   - Lists are formatted correctly

3. **Confirm file creation to user:**
   - Report file path
   - Report file size or line count
   - Summarize what was included

---

### Step 8: Update Deal Artifacts (If Applicable)

**Only if conversion was for a specific deal:**

1. **Update the deal's `deal.md` file:**
   ```markdown
   ## Generated Artifacts
   - 2025-11-13 stage_inventory__Sandler.md (Sandler methodology stage definitions)
   ```

2. **Use Edit tool** to append entry to existing "Generated Artifacts" section

3. **Include:**
   - Date (YYYY-MM-DD)
   - Filename
   - Brief description in parentheses

**Note:** Most convert-and-file operations create shared knowledge and do NOT update deal.md. Only update if explicitly converting deal-specific content.

---

## Quick Decision Trees

### When to Use Parallel Agents?

```
File count:
├─ 1-4 files → Process directly (no agents)
├─ 5-10 files → Optional (consider if files are large)
└─ 10+ files → Recommended (3-5 agents, divide by topic/section)

File size:
├─ < 50 pages total → Process directly
├─ 50-200 pages → Optional parallel processing
└─ 200+ pages → Recommended parallel processing
```

### Output Path Logic

```
Is this a methodology or framework concept?
├─ Yes → sample-data/Runtime/_Shared/knowledge/
│         (or methodologies/{name}/ subdirectory)
└─ No → Is it specific to one customer/deal?
         ├─ Yes → sample-data/Runtime/Sessions/{deal}/
         └─ No → sample-data/Runtime/_Shared/knowledge/
```

### File Type Detection

```
Extension:
├─ .pdf → Read directly (PDF support built-in)
├─ .md, .txt → Read directly (text)
├─ .docx → Read directly (Word support built-in)
├─ .pptx, .xlsx → Read directly (Office support built-in)
└─ Other → Ask user or attempt Read tool

If Read fails → Report error, ask for alternate format
```

---

## Additional Resources

**Templates:**
- `templates/provenance_footer.md` - Standard footer template
- `templates/augmentation_section.md` - Boilerplate for augmentation sections

**Related Files:**
- Framework stage inventory: `sample-data/Runtime/_Shared/knowledge/stage_inventory.md`
- Methodology adapter spec: `Framework/Methodologies/METHODOLOGY_SPEC.md`

**For detailed examples and troubleshooting:**
- See `reference.md` (full walkthroughs, edge cases, tips)

---

**Version History:**
- **1.0** (2025-11-13): Split from SKILL.md into runtime/reference pattern
