# Common Sales Communications Logic

This file contains shared logic used by all sales_communications patterns. Load this file first before processing any specific pattern.

---

## 1. Deal Context Loading

**Purpose**: Extract deal information to personalize artifacts.

**Path**: `sample-data/Runtime/Sessions/{DEAL}/deal.md`

**Required Fields**:
- `deal_id` (frontmatter) - Company name
- `stage` (frontmatter) - Current sales stage
- `methodology` (frontmatter) - Sales methodology in use (MEDDPICC, Sandler, Generic)

**Extract from Content**:
- **Stakeholders section**: Names, titles, roles, communication preferences
- **History section**: Recent events, call dates, topics discussed
- **D1 Tasks** (Deal-Level): Strategic initiatives and blockers
- **D7 Tasks** (Weekly): Near-term actions and follow-ups
- **MEDDPICC/Methodology fields**: Stage-specific qualification data
  - Metrics: Business case, ROI targets
  - Economic Buyer: Decision authority, approval process
  - Decision Criteria: Technical/business requirements
  - Decision Process: Timeline, approval stages
  - Paper Process: Legal, procurement requirements
  - Identify Pain: Business problems being solved
  - Champion: Internal advocate details
  - Competition: Competitive landscape

**Processing**:
1. Read deal.md file
2. Parse YAML frontmatter for metadata
3. Extract stakeholder list with roles
4. Review last 3-5 History entries for context
5. Check D1/D7 tasks for current priorities
6. Extract methodology-specific fields if present

**Error Handling**:
- If deal.md not found: Prompt user to run `/deal-intake` first
- If required fields missing: Use fallback values (generic salutation, no stage-specific content)
- If stakeholders section empty: Use "team" as generic addressee

---

## 2. Brand Guidelines Loading

**Purpose**: Apply company-specific formatting, tone, and visual identity.

**Path**: `sample-data/Runtime/_Shared/brand/brand_guidelines.md`

**Expected Structure** (per brand_guidelines_spec.md):
- **Company Identity**: Name, tagline, value proposition
- **Visual Identity**: Logo usage, color palette, typography
- **Tone & Voice**: Communication style (professional, casual, technical)
- **Formatting Rules**: Email signatures, document headers, spacing
- **Legal/Compliance**: Required disclaimers, confidentiality notices

**Processing**:
1. Check if brand_guidelines.md exists
2. If exists:
   - Extract tone guidance for artifact type (email vs document)
   - Apply formatting rules (signatures, headers, footers)
   - Include required disclaimers
3. If missing:
   - Use generic professional defaults
   - No error (graceful degradation)

**Default Behavior (No Brand File)**:
- Tone: Professional, consultative
- Formatting: Standard business format
- Signature: "Best regards,\n{AE_NAME}"
- No logo, no custom colors, no disclaimers

**Error Handling**:
- Missing file: Use defaults silently (no error message)
- Malformed YAML: Parse what's available, use defaults for missing sections
- Invalid formatting rules: Fall back to standard business format

---

## 3. Email Style Corpus Loading (Emails Only)

**Purpose**: Match account executive's personal writing style for authentic emails.

**4-Tier Loading System** (first match wins):

### Tier 1: Per-AE Corpus (Highest Priority)
**Path**: `sample-data/Runtime/_Shared/style/ae_{AE_NAME}_corpus.md`
**Content**: Real emails written by this AE
**Use when**: AE has sent 10+ emails (sufficient sample)

### Tier 2: Team Corpus
**Path**: `sample-data/Runtime/_Shared/style/team_corpus.md`
**Content**: Emails from sales team following best practices
**Use when**: No per-AE corpus available

### Tier 3: Style Guide
**Path**: `sample-data/Runtime/_Shared/style/email_style_guide.md`
**Content**: Documented email conventions and rules
**Use when**: No corpus files available

### Tier 4: Hardcoded Defaults (Fallback)
**Characteristics**:
- Greeting: "Hi {FIRST_NAME}," (casual) or "Hello {FULL_NAME}," (formal)
- Opening: Reference previous conversation or mutual connection
- Body: 2-3 short paragraphs, bullet points for clarity
- CTA: One clear next step
- Closing: "Best regards," or "Thanks,"
- Signature: AE name + title

**Processing**:
1. Check Tier 1 (per-AE corpus) → if exists, extract style patterns
2. If not found, check Tier 2 (team corpus) → extract common patterns
3. If not found, check Tier 3 (style guide) → follow documented rules
4. If none found, use Tier 4 defaults

**Style Pattern Extraction** (when corpus available):
- Sentence length distribution
- Paragraph structure (avg sentences per paragraph)
- Greeting/closing preferences
- Use of contractions (e.g., "we're" vs "we are")
- Question frequency
- Emoji usage (yes/no)
- Formatting preferences (bullets vs paragraphs)

**Error Handling**:
- All tiers missing: Use Tier 4 defaults (no error)
- Corpus files malformed: Fall back to next tier
- Style guide contradicts corpus: Corpus takes precedence (real examples > rules)

---

## 4. Methodology Loading

**Purpose**: Apply sales methodology logic to ensure artifacts align with stage requirements.

**Path**: `sample-data/Runtime/_Shared/knowledge/methodologies/{METHODOLOGY}/stage_inventory__{METHODOLOGY}.md`

**Methodology Value**: From deal.md frontmatter `methodology` field (MEDDPICC, Sandler, Generic)

**Expected Structure** (per methodology_loader.md):
- **Stage Name**: e.g., "Discovery", "Technical Validation"
- **Exit Criteria**: Requirements to advance to next stage
- **Required Artifacts**: Emails, agendas, proposals needed at this stage
- **Key Questions**: Discovery questions to ask
- **Common Pitfalls**: What to avoid
- **Coaching Guidance**: How to navigate this stage

**Processing**:
1. Extract `methodology` value from deal.md frontmatter
2. Load stage inventory file for that methodology
3. Find current stage section (match deal.md `stage` field)
4. Extract exit criteria and required artifacts for context

**Generic Methodology Fallback**:
If no methodology specified or stage inventory not found, use generic B2B sales practices:
- Discovery: Understand pain, stakeholders, budget
- Demo: Show solution fit, address objections
- Proposal: Present commercial terms, ROI
- Negotiation: Handle objections, finalize contract
- Close: Secure signature, begin onboarding

**Error Handling**:
- Methodology not specified in deal.md: Use Generic
- Stage inventory file missing: Use Generic fallback (no error)
- Stage not found in inventory: Use generic stage guidance

---

## 5. Frontmatter Generation

**Purpose**: Standardize metadata for all generated artifacts.

### Base Frontmatter (Required)

**Structure**:
```yaml
---
generated_by: sales-communications/{pattern_name}
generated_on: {ISO_8601_TIMESTAMP}
deal_id: {company_name_from_deal.md}
sources:
  - sample-data/Runtime/Sessions/{DEAL}/deal.md
  - sample-data/Runtime/_Shared/brand/brand_guidelines.md  # if loaded
  - sample-data/Runtime/_Shared/style/{style_file}  # if loaded
  - sample-data/Runtime/_Shared/knowledge/methodologies/{METHOD}/stage_inventory__{METHOD}.md  # if loaded
---
```

**Required Fields**:
- `generated_by`: Pattern identifier (e.g., "sales_communications/email_discovery_recap")
- `generated_on`: ISO 8601 timestamp (e.g., "2025-11-14T10:30:00Z")
- `deal_id`: Company name from deal.md frontmatter
- `sources`: Array of file paths actually loaded (only include files that were successfully read)

### Optional Frontmatter Fields

**These fields are recommended but not required. Only include when relevant. Do not include empty fields.**

```yaml
---
# ... base fields above ...

# Mode tracking (optional)
mode: coaching | generation  # Use when distinguishing generation vs coaching workflows

# Coaching-specific fields (optional, coaching mode only)
draft_version: 2  # Increment from previous version if improving existing draft
edit_history:  # List of substantive changes made
  - "Reduced word count: 180 → 120"
  - "Matched AE greeting: 'Hello' → 'Hi'"
  - "Strengthened CTA: 'let me know' → 'worth a call?'"

# Voice matching fields (optional)
style_source: "ae_welf_corpus" | "team_corpus" | "style_guide" | "defaults"  # Which tier was used
voice_verification: "pass" | "partial_match" | "not_run"  # Result of voice verification
voice_corrections:  # If voice rewrite occurred
  - "greeting: Hello → Hi"
  - "structure: 1 paragraph → 2 paragraphs"
voice_note: "User requested formal tone, overriding corpus"  # Explanation of voice decisions

# Status tracking (optional)
status: "success" | "missing_prereqs" | "partial_data"  # Machine-readable execution status

# Override tracking (optional)
style_override: "Used 2 paragraphs (corpus) instead of 1 (pattern)"  # Template override explanation
---
```

**Optional Field Descriptions**:
- `mode`: Coaching (improving draft) vs generation (creating from scratch)
- `draft_version`: Version number if iterating on same email
- `edit_history`: Human-readable list of changes made (coaching mode)
- `style_source`: Which tier of style corpus was used (debugging)
- `voice_verification`: Result of voice matching checks
- `voice_corrections`: Specific voice adjustments made
- `voice_note`: Explanation of voice-related decisions
- `status`: Machine-readable status for app integration
- `style_override`: Documentation when corpus overrides pattern

**Usage Guidelines**:
- Include optional fields only when they provide value
- Coaching mode should include: `mode`, `edit_history`, `voice_verification`
- Generation mode should include: `style_source`, `voice_verification` (if run)
- Status field useful for app integration (detecting errors)
- Do NOT include fields with null/empty values

**Processing**:
1. Generate timestamp in ISO 8601 format
2. Extract deal_id from deal.md
3. List all files successfully loaded (deal.md + brand + style + methodology)
4. Omit files that weren't found or loaded
5. Add optional fields only when relevant to this execution

---

## 6. Error Handling

**Philosophy**: Graceful degradation - generate best possible artifact with available data.

**Missing File Scenarios**:

| Missing File | Behavior | User Notification |
|--------------|----------|-------------------|
| deal.md | BLOCK - Prompt to run `/deal-intake` | Error message |
| brand_guidelines.md | Continue with defaults | Silent fallback |
| Style corpus (all tiers) | Use Tier 4 defaults | Silent fallback |
| Methodology stage inventory | Use Generic methodology | Silent fallback |
| Pattern file | List available patterns | Error message |

**Data Quality Issues**:

| Issue | Behavior |
|-------|----------|
| deal.md missing stakeholders | Use generic salutation ("team", "all") |
| deal.md missing stage | Assume "Discovery" (earliest stage) |
| deal.md missing history | Generate artifact without recent context references |
| Malformed YAML frontmatter | Parse what's valid, use defaults for missing fields |
| Empty methodology fields | Omit methodology-specific content from artifact |

**Best Practices**:
1. Never fail artifact generation due to missing optional files (brand, style, methodology)
2. Only block on missing deal.md (required for personalization)
3. Log what files were loaded in frontmatter `sources` array for transparency
4. Degrade gracefully: generic > personalized, but always functional

---

## Usage in Pattern Files

Each pattern file should:

1. **Load this file first**: Read `patterns/_common.md` for instructions
2. **Execute loading sequence**:
   - Deal context (REQUIRED)
   - Brand guidelines (OPTIONAL)
   - Style corpus (OPTIONAL, emails only)
   - Methodology (OPTIONAL)
3. **Generate artifact content**: Apply pattern-specific logic
4. **Format output using three-section envelope** (see section 7 below)
5. **Write file**: Save ONLY Artifact Output content to `sample-data/Runtime/Sessions/{DEAL}/artifacts/{filename}`

**Token Optimization**:
- Only load files needed for this pattern (e.g., don't load style corpus for documents)
- Extract only relevant sections from large files (e.g., current stage from methodology)
- Cache loaded content if generating multiple artifacts in same session

---

## 7. Output Envelope Format (CRITICAL)

**ALL patterns MUST emit output using the three-section envelope structure defined in the main SKILL.md file.**

### Quick Reference

**Section 1: `# Chat Output`**
- Single markdown code fence
- ONLY the final email (Subject/To/Body)
- NO analysis, NO notes, NO duplicates
- For coaching: improved version only (not before/after)

**Section 2: `# Artifact Output`**
- Single markdown code fence
- Complete artifact with:
  - YAML frontmatter (section 5 above)
  - Email body
  - Email Analysis section (pattern used, deal context, brand alignment)
  - Voice Verification section (if corpus loaded)
  - Notes section (missing info, assumptions, next actions)

**Section 3: ` ```json summary`**
- Valid JSON with required schema:
  ```json
  {
    "mode": "pattern_name",
    "pattern": "email_pattern_name",
    "subject": "Email subject line",
    "toPersona": "Recipient name or role",
    "fromPersona": "Sender name",
    "summaryBullets": ["Brief purpose", "Key point"],
    "nextActions": ["Action 1", "Action 2"]
  }
  ```

### Enforcement Rules

1. **Always emit all three sections** in order: Chat Output → Artifact Output → JSON Summary
2. **Never emit more than one Chat Output** (no duplicates)
3. **Chat Output is clean** - final email only, no meta-commentary
4. **All analysis in Artifact Output** - pattern selection, voice notes, all metadata
5. **JSON must be valid** - parseable with all required keys
6. **Code fences properly closed** - each section has opening and closing fences
7. **JSON fence labeled "summary"** - use ` ```json summary` not ` ```json`

### File Output

After generating the three-section envelope:
- Save ONLY the Artifact Output content (including frontmatter) to disk
- Chat Output and JSON Summary are for chat/API consumption only (not saved separately)

**Full specification**: See "Output Format (CRITICAL)" section in main SKILL.md file.

---

**End of Common Logic**
