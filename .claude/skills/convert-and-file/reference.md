---
license: "MIT - See LICENSE.md"
name: convert-and-file
description: Converts unstructured sales materials (PDFs, playbooks, methodology docs) into structured markdown knowledge files with provenance tracking and augmentation sections. Use when the user asks you to process files from sample-data/input/ or convert documents into the framework's knowledge base. This skill ensures all converted knowledge is traceable to source and clearly separates facts from LLM inferences.
allowed-tools: [Read, Write, Glob, Task]
---

# Convert & File Skill

## Purpose

This skill transforms raw input files (PDFs, Word docs, text files, playbooks) into structured, traceable knowledge artifacts that integrate seamlessly with the Agentic Sales Framework. It emphasizes provenance tracking, clear separation of source facts from LLM inferences, and standardized output formatting.

## When to Use This Skill

**Activate this skill when:**
- User provides files in `sample-data/input/**` that need processing
- User asks to "convert," "process," "import," or "integrate" sales materials
- User requests methodology documentation be added to the framework
- User wants to consolidate multiple source documents into a single knowledge file
- Files need provenance tracking and augmentation labeling
- Converting playbooks, methodologies, stage definitions, or sales process documentation

**Do NOT use this skill for:**
- Simple file reads without conversion (use Read tool directly)
- Creating new content from scratch without source material (use Write tool)
- Editing existing knowledge files (use Edit tool)
- Quick reference lookups (use Read or Grep tools)

## Core Principles

1. **Provenance First:** Every output must trace back to specific source files
2. **Fact vs. Inference:** Always separate source facts from LLM-added interpretations
3. **Augmentation Transparency:** Label all LLM-inferred content clearly
4. **Structural Consistency:** Use standard sections and formatting
5. **Traceability:** Include conversion date and tool attribution

## Instructions

### Step 1: Identify Source Files

1. **Use Glob tool** to find files in `sample-data/input/**`
   ```
   Pattern examples:
   - sample-data/input/**/*.pdf
   - sample-data/input/playbooks/**/*
   - sample-data/input/methodologies/{name}/**
   ```

2. **Filter by relevant extensions:**
   - PDFs: `.pdf`
   - Documents: `.docx`, `.doc`
   - Text: `.md`, `.txt`
   - Other: `.pptx`, `.xlsx`

3. **Assess scope:**
   - Single file: Process directly
   - Multiple related files (5-10): Consider parallel processing with Task tool
   - Large collection (10+): Definitely use parallel agents to process sections
   - Ask user to confirm which files to process if ambiguous

4. **Document source inventory:**
   - Count files found
   - Note file types
   - Identify logical groupings (by topic, stage, methodology)

### Step 2: Parse & Extract Core Facts

**Goal:** Extract factual information only, without interpretation or embellishment.

1. **Read source file(s)** using Read tool
   - For PDFs: Read tool will extract text automatically
   - For multi-page docs: Read entire document unless too large

2. **Extract ONLY factual information:**
   - Definitions, concepts, terminology
   - Process steps, methodologies, frameworks
   - Stage names, exit criteria, required artifacts
   - Techniques, tactics, best practices
   - Checklists, templates, tools mentioned
   - Specific metrics, thresholds, or quantitative criteria

3. **Organize into logical sections:**
   - **Use bullet lists** for criteria, checklists, requirements
   - **Use tables** for stage mappings, comparisons, crosswalks
   - **Use code blocks** for templates, scripts, example text
   - **Use headings** to create clear hierarchy (##, ###)

4. **Preserve source language:**
   - Quote key terms exactly as they appear
   - Use the same terminology/naming from source
   - Don't paraphrase unless necessary for clarity

5. **CRITICAL: Do NOT mix source facts with your interpretations yet**
   - If you add context or explanation, note it separately
   - Save interpretations for Step 4 (Augmentation)

**Example Extraction:**
```markdown
## Stage 2: Pain Discovery

### Exit Criteria (from source)
- Prospect has personal AND emotional pain solvable with your product/service
- Gap between desired and current outcomes clearly established
- Pain intensity rated 7+ on 1-10 scale

### Required Artifacts (from source)
- Pain Discovery Chart
- Pain Question Creator worksheet
- Pain Funnel documentation (8-question sequence)
```

### Step 3: Validate Extracted Information

**Goal:** Document quality issues, inconsistencies, or gaps in source material.

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

4. **Document validation issues in a dedicated section:**
   ```markdown
   ## Validation Notes
   - Source refers to "DISC profiles" but doesn't define DISC types
   - Page 23 shows 7 stages; page 45 shows 6 stages (discrepancy)
   - Budget discussion techniques reference "Monkey's Paw" without explanation
   ```

5. **Do NOT "fix" these issues with your own knowledge yet**
   - Just document them
   - Flag for user review if critical

### Step 4: Augment with LLM Inferences

**Goal:** Add helpful interpretations, examples, and guidance NOT in the source material.

1. **Create clearly labeled section:**
   ```markdown
   ## Augmentation (LLM-Inferred)

   > **Notice:** The content in this section contains interpretations, examples,
   > and guidance not explicitly present in source documents. Review and validate
   > before relying on this information.
   ```

2. **Add value-added content:**
   - **Interpretations:** Explain unclear concepts from source
   - **Examples:** Provide concrete scenarios illustrating source concepts
   - **Best practices:** General guidance aligned with source principles
   - **Crosswalks:** Map source methodology to framework's default stages
   - **Usage guidance:** "What to Do With This File" checklists
   - **Edge cases:** Situations not covered in source but logically relevant

3. **Common augmentation sections:**
   - `### General Best Practices` - High-level guidance
   - `### Crosswalk to Default Stage Inventory` - Methodology mapping
   - `### What to Do With This File` - Usage instructions
   - `### When to Use vs. Avoid` - Situational guidance
   - `### Common Pitfalls` - Mistakes to avoid

4. **Keep augmentation clearly separate from source facts:**
   - Use distinct heading structure
   - Always label as "LLM-Inferred" or "Interpretation"
   - Never merge augmented content into source sections

**Example Augmentation:**
```markdown
## Augmentation (LLM-Inferred)

### General Best Practices
- **Disqualify Early and Often:** The source emphasizes qualification, suggesting
  that disqualifying non-buyers early saves time (interpretation of "you can't
  lose what you don't have" principle)
- **Emotional vs. Intellectual:** Source requires "emotionally-oriented language" -
  this means looking for words like "frustrated" or "concerned" rather than
  "thinking about" or "considering" (inference from source criteria)

### Crosswalk to Default Stage Inventory
| Source Stage | Default Stage | Notes |
|--------------|---------------|-------|
| Pain | Stage 1: Discover | Pain discovery happens during discovery phase |
| Budget | Stage 3: Propose | Budget discussion before proposal delivery |
```

### Step 5: Add Provenance Footer

**Goal:** Make every output file fully traceable to its sources.

1. **Always append this footer** to output files:

```markdown
---

## Provenance

source_paths:
  - "sample-data/input/path/to/source1.pdf"
  - "sample-data/input/path/to/source2.docx"

converted_by: convert_and_file
converted_at: 2025-11-11
stage_ref: ../../_Shared/knowledge/stage_inventory.md
augmentation_notice: >
  Sections under **Augmentation (LLM-inferred)** contain general guidance not
  explicitly present in source documents. Review before adoption.
```

2. **Customize each field:**
   - `source_paths`: List ALL source files used (absolute or relative paths)
   - `converted_at`: Use actual ISO date (YYYY-MM-DD format)
   - `stage_ref`: Adjust relative path based on output location
   - Add custom fields if needed: `methodology`, `version`, `reviewed_by`, etc.

3. **For parallel agent processing:**
   - List all files processed by all agents
   - Note in footer: `converted_by: convert_and_file (parallel agent analysis)`
   - Include agent count if relevant: `agents_used: 5`

### Step 6: Determine Output Path

**Goal:** Place output file in appropriate location within framework structure.

1. **Choose output directory based on content type:**

   **Shared Knowledge (most common):**
   - Default: `sample-data/Runtime/_Shared/knowledge/`
   - Methodology-specific: `sample-data/Runtime/_Shared/knowledge/methodologies/{methodology_name}/`
   - Stage definitions: `sample-data/Runtime/_Shared/knowledge/stage_inventory*.md`

   **Deal-Specific Knowledge:**
   - `sample-data/Runtime/Sessions/{deal_name}/`
   - Use when content applies only to one deal/customer

   **Framework Documentation:**
   - `Framework/Methodologies/{methodology_name}.md`
   - Use for framework-level adapter configs or overviews

2. **Choose filename using naming convention:**
   - Stage inventory: `stage_inventory__{methodology}.md`
   - Topic-based: `{topic}_{methodology}.md`
   - Playbook: `{company}_playbook.md`
   - Techniques: `{technique_name}_guide.md`

3. **Create directory if needed:**
   ```bash
   mkdir -p "path/to/output/directory"
   ```

4. **Verify path doesn't conflict with existing files:**
   - Use Glob to check for existing file
   - Ask user if overwrite is intended
   - Suggest versioned filename if preserving old version

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

### Step 8: Update Deal Artifacts (If Applicable)

**If this conversion was for a specific deal:**

1. **Update the deal's `deal.md` file:**
   ```markdown
   ## Generated Artifacts
   - 2025-11-11 stage_inventory__Sandler.md (Sandler methodology stage definitions)
   ```

2. **Use Edit tool** to append entry to existing "Generated Artifacts" section

3. **Include:**
   - Date (YYYY-MM-DD)
   - Filename
   - Brief description in parentheses

## Examples

### Example 1: Converting Methodology PDFs (Complex Multi-File)

**User Request:**
> "Process the Sandler methodology PDFs in sample-data/input/playbooks/methodologies/Sandler/"

**Skill Execution:**

1. **Identify Sources:**
   ```
   Glob: sample-data/input/playbooks/methodologies/Sandler/**/*.pdf
   Result: 58 PDFs found
   Decision: Launch parallel agents (5 agents, each handling 10-12 PDFs)
   ```

2. **Parse & Extract (via parallel agents):**
   - Agent 1: Pain methodology docs → Pain stages, exit criteria, artifacts
   - Agent 2: Budget methodology docs → Budget techniques, checklists
   - Agent 3: Decision methodology docs → Decision mapping, timelines
   - Agent 4: Fulfillment/Post-Sell docs → Presentation requirements
   - Agent 5: Gate/Process docs → Overall Submarine model, philosophy

3. **Validate:**
   - All agents report consistent 7-stage model
   - Some terminology varies (e.g., "Up-Front Contract" vs "Rules of Engagement")
   - No major gaps identified

4. **Augment:**
   - Add crosswalk mapping Sandler stages → Default framework stages
   - Create "General Best Practices" section interpreting core philosophy
   - Add "What to Do With This File" checklist for coaches using Sandler

5. **Provenance:**
   ```yaml
   source_paths: [list all 19 PDFs actually referenced]
   converted_by: convert_and_file (parallel agent analysis)
   agents_used: 5
   converted_at: 2025-11-11
   ```

6. **Output:**
   - Path: `sample-data/Runtime/_Shared/knowledge/methodologies/Sandler/stage_inventory__Sandler.md`
   - Size: 450+ lines
   - Sections: Overview, 7 stage definitions, augmentation, provenance

**Result:**
- ✅ Comprehensive stage inventory created
- ✅ All 7 Sandler stages documented with exit criteria and artifacts
- ✅ Augmentation section clearly labeled
- ✅ Full provenance with 19 source file paths

---

### Example 2: Converting Single Sales Playbook

**User Request:**
> "Convert our internal sales playbook to framework format"

**Skill Execution:**

1. **Identify Sources:**
   ```
   Glob: sample-data/input/playbooks/acme_sales_playbook.pdf
   Result: 1 file found (125 pages)
   Decision: Process directly (no parallel agents needed)
   ```

2. **Parse & Extract:**
   - Chapter 1: Qualification criteria (extracted as bullet list)
   - Chapter 2: Objection handling scripts (extracted as code blocks)
   - Chapter 3: Pricing guidelines (extracted as table)
   - Chapter 4: Success stories (extracted with headings)

3. **Validate:**
   - ⚠️ Pricing data shows 2023 copyright → may be outdated
   - ⚠️ References "CRM fields" but doesn't specify which CRM
   - ✅ Objection handling scripts are complete and specific

4. **Augment:**
   - Add section mapping playbook stages to framework's default stages
   - Create "When to Use This Playbook" guidance based on deal types mentioned
   - Note that pricing needs user confirmation before use

5. **Provenance:**
   ```yaml
   source_paths:
     - "sample-data/input/playbooks/acme_sales_playbook.pdf"
   converted_by: convert_and_file
   converted_at: 2025-11-11
   validation_notes: "Pricing from 2023, confirm current before use"
   ```

6. **Output:**
   - Path: `sample-data/Runtime/_Shared/knowledge/acme_playbook.md`
   - Size: 200 lines
   - Sections: Qualification, Objection Handling, Pricing, Success Stories, Augmentation, Provenance

**Result:**
- ✅ Internal playbook now accessible within framework
- ✅ Validation note flags outdated pricing
- ✅ Clear separation of source content from augmented guidance

---

### Example 3: Converting Deal-Specific Meeting Notes

**User Request:**
> "File these discovery call notes into the Example Pharma deal"

**Skill Execution:**

1. **Identify Sources:**
   ```
   User provides: sample-data/input/deals/examplepharma/discovery_notes_2025-11-08.txt
   Result: 1 text file
   ```

2. **Parse & Extract:**
   - Attendees: [list extracted]
   - Pain points mentioned: [3 pain points extracted]
   - Budget indications: [notes about budget extracted]
   - Next steps: [action items extracted]

3. **Validate:**
   - ✅ Notes clearly structured
   - ⚠️ No explicit decision maker identified (gap noted)

4. **Augment:**
   - Add "Recommended Follow-Up" section based on Sandler Pain stage criteria
   - Map identified pains to potential solutions (inference)
   - Flag missing information (decision maker, timeline)

5. **Provenance:**
   ```yaml
   source_paths:
     - "sample-data/input/deals/examplepharma/discovery_notes_2025-11-08.txt"
   converted_by: convert_and_file
   converted_at: 2025-11-11
   deal_ref: ../../deal.md
   ```

6. **Output:**
   - Path: `sample-data/Runtime/Sessions/ExamplePharma/2025-11-08_discovery_notes.md`
   - Update: `sample-data/Runtime/Sessions/ExamplePharma/deal.md` with artifact entry

7. **Deal.md Update:**
   ```markdown
   ## Generated Artifacts
   - 2025-11-08 2025-11-08_discovery_notes.md (Discovery call notes with pain analysis)
   ```

**Result:**
- ✅ Discovery notes filed in correct deal directory
- ✅ Deal.md updated with artifact reference
- ✅ Gaps flagged for follow-up (missing decision maker)

## Edge Cases & Troubleshooting

### Problem: PDF has poor OCR quality / unreadable text

**Symptoms:**
- Read tool returns garbled characters
- Missing sections or incomplete text
- Formatting completely lost

**Solution:**
1. Note in validation section that source quality is poor
2. Extract whatever is readable
3. Flag sections as `[UNCLEAR - source OCR quality poor, requires review]`
4. Ask user if they have alternate format (Word, original file)
5. Suggest user re-scan PDF with better OCR if available

**Example:**
```markdown
## Validation Notes
- Pages 15-23: OCR quality poor, text partially illegible
- Stage 3 criteria may be incomplete due to source quality
- Recommend user provide Word doc or rescan for full accuracy
```

---

### Problem: Multiple contradictory sources

**Symptoms:**
- Source A says 7 stages, Source B says 6 stages
- Conflicting definitions of same term
- Different exit criteria for same stage

**Solution:**
1. **Do NOT resolve contradiction with your own judgment**
2. Document BOTH versions in extraction section
3. Add note in validation: "Source A (page X) says Y; Source B (page Z) says W"
4. Ask user which version to prioritize or if both should be noted
5. If user clarifies, note their decision in provenance

**Example:**
```markdown
## Stage Definitions

### Version Discrepancy
- **Source A** (2019_sandler_guide.pdf, p. 12): Defines 7 stages including "Bonding & Rapport"
- **Source B** (sandler_quick_ref.pdf, p. 3): Shows 6 stages, omits "Bonding & Rapport"

> **User Clarification (2025-11-11):** Use Source A's 7-stage model as canonical.
> Source B is simplified quick reference.
```

---

### Problem: Source has no clear structure

**Symptoms:**
- Narrative text without section headers
- Concepts scattered throughout document
- No explicit stage definitions or lists

**Solution:**
1. **Impose framework structure** to make usable:
   - Create sections: Stages, Exit Criteria, Artifacts, Techniques
   - Extract concepts and organize logically
2. **Note in augmentation** that structure was imposed for usability
3. **Link concepts to source page numbers** for verification
4. Consider this a heavier augmentation (more LLM interpretation)

**Example:**
```markdown
## Stage 2: Pain Discovery

### Exit Criteria (interpreted from source, pp. 45-52)
- Source mentions "emotional commitment" throughout → interpreted as exit criterion
- Page 47 mentions "7+ intensity" → extracted as quantitative threshold
- Page 50 discusses "personal stakes" → interpreted as required criterion

## Augmentation (LLM-Inferred)
> **Structure Notice:** Source material is narrative format without explicit stage
> definitions. The structure above (stages, exit criteria, artifacts) was imposed
> by this conversion process to align with framework requirements. All concepts
> are sourced from original material but organized differently.
```

---

### Problem: Output path unclear (shared vs. deal-specific)

**Symptoms:**
- Unclear if content applies to all deals or one specific deal
- Methodology guidance but tied to specific customer
- Playbook that might be reusable

**Solution:**
1. **Ask user:** "Should this be shared knowledge or deal-specific?"
2. **Default logic:**
   - Methodology, stage definitions, techniques → Shared
   - Deal notes, customer specifics, meeting agendas → Deal-specific
   - Playbooks, general guidance → Shared (unless customer-branded)
3. **Can always move later** with file system operations

**Example Decision Tree:**
```
Is this a methodology or framework concept?
├─ Yes → sample-data/Runtime/_Shared/knowledge/
└─ No → Is it specific to one customer/deal?
         ├─ Yes → sample-data/Runtime/Sessions/{deal}/
         └─ No → sample-data/Runtime/_Shared/knowledge/
```

---

### Problem: Source is too large (100+ pages, 50+ files)

**Symptoms:**
- Read tool output truncated
- Context window concerns
- Processing time excessive

**Solution:**
1. **Use parallel agents** (Task tool) to divide work:
   - Create 3-5 agents, each handling subset of files or chapters
   - Define clear scope for each agent
   - Consolidate agent outputs into single file
2. **Process in multiple passes:**
   - Pass 1: Extract high-level structure (chapters, sections)
   - Pass 2: Deep-dive into each section
3. **Use file offsets:**
   - Read tool supports line offset and limit
   - Process large files in chunks

**Example:**
```
58 PDF files found → Launch 5 parallel agents
- Agent 1: Files 1-12 (Pain methodology)
- Agent 2: Files 13-24 (Budget methodology)
- Agent 3: Files 25-36 (Decision methodology)
- Agent 4: Files 37-48 (Fulfillment methodology)
- Agent 5: Files 49-58 (Post-Sell & misc)

Consolidate agent findings into single stage_inventory file
```

---

### Problem: Source references external materials not available

**Symptoms:**
- "See Appendix B" but no Appendix B provided
- "Download worksheet from website" but no URL
- References to "certified training" materials

**Solution:**
1. **Note gap in validation section:**
   ```markdown
   ## Validation Notes
   - Source references "DISC Adapter Worksheet" but file not provided in input
   - Page 67 mentions "certified training materials" - not accessible for conversion
   ```
2. **Add to augmentation section:**
   ```markdown
   ## Augmentation (LLM-Inferred)
   ### Missing Materials
   - DISC Adapter Worksheet: Likely a tool for adapting communication style to
     buyer personality types. Recommend user obtain from original source.
   ```
3. **Ask user** if they can provide missing materials
4. **Do NOT fabricate** missing content - just flag it

---

### Problem: Unclear what depth of detail to extract

**Symptoms:**
- Source has 100 pages but only 10 are relevant
- Every paragraph could be extracted vs. just key points
- Balance between comprehensive and concise

**Solution:**
1. **Prioritize framework-aligned content:**
   - Stage definitions, exit criteria, required artifacts → Extract in full
   - Background context, history, theory → Summarize or skip
   - Examples and stories → Extract representative samples, not all
2. **Target output size:**
   - Single concept/technique: 50-100 lines
   - Full methodology: 300-500 lines
   - If exceeding 500 lines, consider splitting into multiple files
3. **Ask user** if they want comprehensive vs. executive summary version

**Heuristic:**
- Extract: Definitions, criteria, checklists, processes, tools, templates
- Summarize: Context, rationale, theory, history
- Sample: Examples, stories, case studies (2-3 representative ones)

## Tips for Effective Conversion

### 1. Maintain Conversion Log
Keep track of what you've converted in the session:
```
Session Conversions:
- sandler.md (58 PDFs → stage_inventory__Sandler.md)
- acme_playbook.pdf → acme_playbook.md
- discovery_notes.txt → ExamplePharma/2025-11-08_discovery_notes.md
```

### 2. Batch Similar Files
If user provides multiple similar files, process them together:
- Multiple methodology chapters → Single methodology file
- Multiple meeting notes → Consolidated deal notes
- Multiple playbooks → Compare/contrast in single file

### 3. Ask Clarifying Questions Early
Don't assume:
- "Should this go in shared knowledge or Example Pharma deal folder?"
- "Do you want just stages or full techniques too?"
- "Should I consolidate all PDFs or keep separate?"

### 4. Preserve Useful Formatting
When extracting from source:
- Keep numbered steps as numbered lists
- Preserve tables if they organize info well
- Maintain code blocks for scripts or templates
- Use blockquotes for key principles or quotes

### 5. Link Related Knowledge
In augmentation section, cross-reference related files:
```markdown
## Augmentation (LLM-Inferred)
### Related Knowledge Files
- See also: [Default Stage Inventory](../../stage_inventory.md)
- Compare with: [MEDDIC Methodology](../MEDDIC/stage_inventory__MEDDIC.md)
- Templates: [Framework/Templates/](../../../../Framework/Templates/)
```

## Version History

- **1.0** (2025-11-11): Initial skill created during framework setup
  - Structured as proper Claude Code skill with YAML frontmatter
  - Expanded from 23-line spec to 800+ line comprehensive guide
  - Added examples, troubleshooting, edge cases
  - Aligned with Anthropic best practices for agent skills

---

## Additional Resources

See also:
- `templates/provenance_footer.md` - Standard footer template
- Framework stage inventory: `sample-data/Runtime/_Shared/knowledge/stage_inventory.md`
- Methodology adapter spec: `Framework/Methodologies/METHODOLOGY_SPEC.md`
