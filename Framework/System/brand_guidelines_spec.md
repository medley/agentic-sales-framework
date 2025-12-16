# Brand Guidelines Specification

**Version**: 1.0
**Purpose**: Define schema for company brand guidelines used by sales_communications skill
**Location**: This spec lives in `Framework/System/` (portable). Actual guidelines live in `sample-data/Runtime/_Shared/brand/brand_guidelines.md` (company-specific).

---

## Overview

The sales_communications skill loads brand guidelines from `sample-data/Runtime/_Shared/brand/brand_guidelines.md` to apply company-specific formatting, tone, and visual identity to generated artifacts (emails, agendas, briefings, one-pagers).

**Key Principles**:
1. **Portable Skill Logic**: Pattern files reference generic path, content changes per company
2. **Graceful Fallback**: Missing brand file = use professional defaults (no errors)
3. **IP Protection**: Brand guidelines stay in sample-data/ (not versioned), skills in .claude/skills/ (versioned)
4. **Customizable**: Each company creates their own guidelines file from EXAMPLE template

---

## File Structure

### Required Frontmatter

```yaml
---
company_name: {Your Company Name}
last_updated: {YYYY-MM-DD}
version: {1.0}
---
```

### Required Sections

```markdown
# Brand Guidelines: {Company Name}

## 1. Company Identity
## 2. Visual Identity (Documents)
## 3. Tone & Voice
## 4. Email Formatting
## 5. Document Formatting
## 6. Legal & Compliance
```

---

## Section Specifications

### 1. Company Identity

**Fields**:
- Company Name
- Brand Name (if different)
- Tagline
- Value Proposition
- Industry
- Website

### 2. Visual Identity (Documents)

**Fields**:
- Logo (path, usage, restrictions)
- Color Palette (primary, secondary, accent with hex codes)
- Typography (headings, body, code fonts)

### 3. Tone & Voice

**Fields**:
- Overall Tone
- Customer-Facing Emails (greeting style, paragraph structure, language, enthusiasm)
- Customer-Facing Documents (formality, technical depth, visuals)
- Internal Communications (formality, detail level)

### 4. Email Formatting

**Fields**:
- Signature Format
- Subject Line Style (capitalization, max length, emoji)
- Disclaimers (confidentiality, auto-footer)

### 5. Document Formatting

**Fields**:
- Header (logo, title format, metadata)
- Section Structure (heading levels, spacing)
- Footer (contact info, page numbers, confidentiality)

### 6. Legal & Compliance

**Fields**:
- Industry Regulations
- Required Disclaimers
- Restricted Claims
- Confidentiality (NDA language, customer data handling)

---

## Loading Behavior

**Load Sequence**:
1. Check if `sample-data/Runtime/_Shared/brand/brand_guidelines.md` exists
2. If exists: Parse YAML frontmatter, extract relevant sections
3. If missing: Use defaults (no error)

**Section-Specific Loading**:
- **Email patterns**: Load sections 1, 3, 4, 6 (skip 2, 5)
- **Document patterns**: Load sections 1, 2, 3, 5, 6 (skip 4)

**Fallback Defaults**:
- Tone: Professional, consultative
- Greeting: Casual first-name ("Hi Jane,")
- Signature: Standard business format
- Document: Clean markdown, no logo

---

## See Also

- `brand_guidelines_EXAMPLE.md` - Template file in sample-data/
- `patterns/_common.md` - Loading logic implementation
- `DEVELOPER_GUIDE.md` - Implementation protocols

---

**End of Specification**
