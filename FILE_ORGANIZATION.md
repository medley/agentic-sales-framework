# File Organization Guide

Complete reference for where to put your company files, what gets created during setup, and how the framework uses each directory.

---

## Directory Structure Overview

```
agentic-sales-framework/
├── sample-data/                    # YOUR COMPANY DATA (gitignored)
│   ├── input/                     # SOURCE FILES (you create these)
│   │   ├── playbooks/            # Sales playbooks, process docs
│   │   ├── personas/             # Buyer personas (CFO, VP Ops, etc.)
│   │   ├── battlecards/          # Competitive positioning
│   │   ├── transcripts/          # Call recordings (text)
│   │   ├── emails/               # Email threads for style learning
│   │   └── other/                # Misc company docs
│   │
│   └── Runtime/                   # GENERATED FILES (framework creates these)
│       ├── _Shared/              # Company-wide resources
│       │   ├── brand/           # Brand guidelines (you create)
│       │   ├── style/           # Email style corpus (you create)
│       │   ├── profile/         # Your AE profile (you create)
│       │   └── knowledge/       # Converted docs (framework creates)
│       │
│       ├── Sessions/             # Deal workspaces
│       │   ├── _TEMPLATES/      # Templates for new deals
│       │   ├── CompanyA/        # Deal-specific files
│       │   ├── CompanyB/
│       │   └── ...
│       │
│       └── Dashboard/            # Portfolio views
│
├── Framework/                     # PORTABLE KNOWLEDGE (versioned)
│   ├── Methodologies/            # Sales frameworks (read-only)
│   ├── Templates/                # Generic templates (read-only)
│   ├── Style/                    # Default styles (read-only)
│   └── System/                   # Documentation (read-only)
│
└── .claude/                       # EXECUTION LAYER (versioned)
    ├── skills/                   # Skills (read-only)
    └── hooks/                    # Safety validations (read-only)
```

---

## Input Directory - Where YOU Put Files

### `sample-data/input/`

**Purpose:** Drop your source files here for conversion to structured knowledge.

**Created by:** You (manually) or install.sh (empty directories)

**File types accepted:** PDF, DOCX, TXT, MD, XLSX

#### Subdirectories

**`input/playbooks/`**
- Sales playbooks
- Process documentation
- Stage guides
- Qualification frameworks

**Examples:**
```
input/playbooks/
├── enterprise_sales_playbook_2024.pdf
├── discovery_process.docx
└── qualification_checklist.md
```

**`input/personas/`**
- Buyer personas
- Role descriptions
- Decision criteria by role

**Examples:**
```
input/personas/
├── CFO_persona_pharma.pdf
├── VP_Operations_manufacturing.docx
└── IT_Director_enterprise.md
```

**`input/battlecards/`**
- Competitive positioning
- Feature comparisons
- Objection handling

**Examples:**
```
input/battlecards/
├── vs_CompetitorA.pdf
├── vs_CompetitorB.pdf
└── pricing_objections.md
```

**`input/transcripts/`**
- Call recordings (transcribed to text)
- Meeting notes
- Discovery call summaries

**Examples:**
```
input/transcripts/
├── discovery_acme_2024-10-15.txt
├── demo_techco_2024-10-22.docx
└── negotiation_pharma_2024-11-01.md
```

**`input/emails/`**
- Email threads (for style learning)
- Sent folder exports
- Customer correspondence

**Examples:**
```
input/emails/
├── sent_emails_Q3_2024.txt
├── customer_thread_acme.txt
└── negotiation_emails_techco.txt
```

**`input/other/`**
- Anything else (case studies, product docs, pricing sheets)

---

## Runtime Directory - What Gets Created

### `sample-data/Runtime/_Shared/`

**Purpose:** Company-wide resources that apply to all deals.

**Created by:** You (configuration files) + Framework (converted knowledge)

---

#### `Runtime/_Shared/brand/`

**Purpose:** Your company's brand guidelines for generated artifacts.

**Created by:** YOU (manually create this file)

**File:** `brand_guidelines.md`

**When to create:** Optional, but recommended for professional-looking outputs

**Template location:** See `Framework/System/brand_guidelines_spec.md` for structure

**Example structure:**
```yaml
---
company_name: "Your Company Name"
last_updated: "2024-11-15"
version: "1.0"
---

# Brand Guidelines: Your Company

## 1. Company Identity
- Company Name: Acme Corp
- Tagline: "Manufacturing Excellence"
- Website: www.acme.com

## 2. Visual Identity
- Primary Color: #003366 (Navy Blue)
- Secondary Color: #00A86B (Emerald Green)
- Logo: assets/logo.png

## 3. Tone & Voice
- Professional but approachable
- Technical depth without jargon
- Solution-focused, not feature-heavy

## 4. Email Formatting
- Signature: Name | Title | Company | Phone | Email
- Subject lines: Sentence case, no emojis
- Max 3-4 sentences per paragraph

## 5. Document Formatting
- Headers: Company logo + document title
- Footers: Page numbers + "Confidential"
```

**What uses this:**
- Email generation (signature, tone)
- Agenda generation (headers, formatting)
- Briefing generation (visual identity)
- One-pagers (brand compliance)

**Fallback:** If missing, framework uses professional defaults.

---

#### `Runtime/_Shared/style/`

**Purpose:** Your personal email writing style for authentic voice in generated emails.

**Created by:** YOU (manually create this file)

**File:** `email_style_corpus_{your_name}.md`

**When to create:** Optional, but dramatically improves email quality

**How to create:**
1. Export 20-30 of your best sent emails
2. Save as `email_style_corpus_welf.md` (replace "welf" with your name)
3. Framework learns your voice

**Example structure:**
```yaml
---
profile_id: welf
last_updated: "2024-11-15"
email_count: 25
---

# Email Style Corpus — Welf Ludwig

## Style Characteristics
- Brief (3-5 sentences max)
- Direct but warm
- Questions early ("How does Thursday at 2pm look?")
- Light humor occasionally
- Always includes specific next step

## Example Emails

### Example 1: Discovery Follow-Up
Subject: Quick follow-up from today's call

Hi Jennifer,

Great talking through the audit prep challenges today. The 6-week timeline you mentioned is exactly what we've helped other manufacturers compress to 2 weeks.

I'll send over the ETQ comparison you asked for by EOD tomorrow. Meanwhile, would Thursday at 2pm work for a 30-min technical deep-dive with Robert?

Best,
Welf

### Example 2: Demo Recap
[... 20-30 total examples ...]
```

**What uses this:**
- All email generation (discovery, demo, proposal, follow-up)

**Fallback tiers:**
1. `email_style_corpus_{profile_id}.md` (your personal style)
2. `email_style_corpus_team.md` (team style if shared)
3. `Framework/Style/email_style_guide.md` (generic professional style)
4. Default professional tone

---

#### `Runtime/_Shared/profile/`

**Purpose:** Your AE profile (links to your style corpus).

**Created by:** YOU (manually create this file)

**File:** `ae_profile.md`

**When to create:** Optional (only if using personal email style corpus)

**Example structure:**
```yaml
---
profile_id: welf
name: "Welf Ludwig"
title: "Account Executive"
email: "rep@company.com"
phone: "+1-555-0100"
---

# AE Profile: Welf Ludwig

**Territory:** Enterprise Manufacturing (West Coast)
**Quota:** $4.5M ARR
**Methodology:** Sandler + MEDDPICC hybrid
```

**What uses this:**
- Email generator (loads your style corpus via profile_id)
- Signature generation

**Fallback:** If missing, uses team/generic style.

---

#### `Runtime/_Shared/knowledge/`

**Purpose:** Structured, searchable knowledge converted from input files.

**Created by:** FRAMEWORK (via convert-and-file skill)

**When created:** When you run `"Convert all files in input/"`

**File naming:**
- `persona_{role}_{industry}.md`
- `battlecard_{competitor}_vs_{product}.md`
- `playbook_{topic}.md`
- `transcript_{deal}_{date}.md`

**Example:**
```
knowledge/
├── persona_cfo_pharma.md
├── persona_vp_operations_manufacturing.md
├── battlecard_competitorA_vs_ourproduct.md
├── playbook_enterprise_sales.md
└── transcript_acme_discovery_2024-10-15.md
```

**What uses this:**
- Coach skill (loads personas, playbooks for context-aware coaching)
- Prep-discovery skill (loads personas, methodology guides)
- All artifact generation (references for accuracy)

---

### `sample-data/Runtime/Sessions/`

**Purpose:** Deal-specific workspaces (one folder per deal).

**Created by:** YOU (manually) or framework (via deal-intake)

---

#### `Sessions/_TEMPLATES/`

**Purpose:** Templates for creating new deals.

**Created by:** install.sh

**Files:**
- `deal_template.md` - Blank deal note structure

**Usage:**
```bash
# Create new deal
cp sample-data/Runtime/Sessions/_TEMPLATES/deal_template.md \
   sample-data/Runtime/Sessions/NewDeal/deal.md
```

---

#### `Sessions/{DealName}/`

**Purpose:** All files for a specific deal.

**Created by:** YOU (deal.md) + FRAMEWORK (artifacts)

**Structure:**
```
Sessions/Acme/
├── deal.md                          # Deal context (YOU create/update)
├── artifacts/                       # Generated files (FRAMEWORK creates)
│   ├── calls/
│   │   ├── 2024-10-15_discovery_summary.md
│   │   └── 2024-10-22_demo_summary.md
│   ├── emails/
│   │   ├── 2024-10-16_followup_email.md
│   │   └── 2024-10-23_demo_recap.md
│   └── other/
│       ├── 2024-11-01_coaching_report.md
│       └── 2024-11-05_next_steps.md
└── raw/                             # Optional: source files
    ├── transcripts/
    └── crm_exports/
```

**`deal.md` (YOU create):**
- Deal context (company, stage, stakeholders, pain, budget, competition)
- Updated after every call/interaction
- Primary source for all coaching and artifact generation

**`artifacts/` (FRAMEWORK creates):**
- Generated emails, agendas, coaching reports
- Organized by type and date
- All cite sources in frontmatter

**`raw/` (YOU create, optional):**
- Source files specific to this deal
- Transcripts, CRM exports, email threads
- Used by deal-intake skill

---

### `sample-data/Runtime/Dashboard/`

**Purpose:** Portfolio-level views (pipeline health, at-risk deals).

**Created by:** FRAMEWORK (via portfolio skill)

**Files:**
- `Deal_Overview.md` - Pipeline summary
- `At_Risk_Deals.md` - Flagged deals
- `Weekly_Review_{date}.md` - Weekly snapshots

---

## What You Need to Create (Checklist)

### Essential (Required for Basic Usage)

- [ ] **Deal notes** (`Sessions/{Deal}/deal.md`)
  - Copy from `_TEMPLATES/deal_template.md`
  - Fill in company, stage, stakeholders, context

### Recommended (Improves Quality)

- [ ] **Source files** (`input/playbooks/`, `input/personas/`)
  - Add sales playbooks, personas, battlecards
  - Run: `"Convert all files in input/"`

- [ ] **Brand guidelines** (`Runtime/_Shared/brand/brand_guidelines.md`)
  - Use `Framework/System/brand_guidelines_spec.md` as template
  - Adds professional formatting to outputs

### Optional (For Advanced Features)

- [ ] **Email style corpus** (`Runtime/_Shared/style/email_style_corpus_{name}.md`)
  - Export 20-30 sent emails
  - Framework learns your voice

- [ ] **AE profile** (`Runtime/_Shared/profile/ae_profile.md`)
  - Links to your email style corpus
  - Personalizes signature

---

## Typical Setup Workflow

### 1. Initial Install
```bash
./install.sh  # Creates directory structure + SampleCo demo
```

### 2. Add Company Knowledge (Week 1)
```bash
# Add files to input/ (copy from wherever you store your source docs)
cp /path/to/sales_playbook.pdf sample-data/input/playbooks/
cp /path/to/cfo_persona.docx sample-data/input/personas/

# Convert to structured knowledge
> "Convert all files in sample-data/input/"
```

### 3. Create Brand Guidelines (Optional)
```bash
# Copy template and customize
cat Framework/System/brand_guidelines_spec.md  # Review structure
# Then create: sample-data/Runtime/_Shared/brand/brand_guidelines.md
```

### 4. Add Email Style (Optional)
```bash
# Export sent emails, save as:
# sample-data/Runtime/_Shared/style/email_style_corpus_yourname.md
```

### 5. Create First Real Deal
```bash
mkdir -p sample-data/Runtime/Sessions/Acme
cp sample-data/Runtime/Sessions/_TEMPLATES/deal_template.md \
   sample-data/Runtime/Sessions/Acme/deal.md

# Edit deal.md with deal details
# Then: > "Coach me on the Acme deal"
```

---

## What Gets Auto-Created vs What You Create

### YOU Create Manually

| Path | File | Purpose |
|------|------|---------|
| `input/playbooks/` | `*.pdf, *.docx` | Source files to convert |
| `input/personas/` | `*.pdf, *.docx` | Buyer personas |
| `Runtime/_Shared/brand/` | `brand_guidelines.md` | Brand standards |
| `Runtime/_Shared/style/` | `email_style_corpus_{name}.md` | Your email style |
| `Runtime/_Shared/profile/` | `ae_profile.md` | Your profile |
| `Sessions/{Deal}/` | `deal.md` | Deal context (updated regularly) |

### FRAMEWORK Creates Automatically

| Path | File | Created When |
|------|------|--------------|
| `Runtime/_Shared/knowledge/` | `persona_*.md` | You run convert-and-file |
| `Runtime/_Shared/knowledge/` | `playbook_*.md` | You run convert-and-file |
| `Sessions/{Deal}/artifacts/` | `*_email.md` | You request email generation |
| `Sessions/{Deal}/artifacts/` | `*_agenda.md` | You request call prep |
| `Sessions/{Deal}/artifacts/` | `*_coaching.md` | You run coach skill |
| `Runtime/Dashboard/` | `Deal_Overview.md` | You run portfolio skill |

### INSTALL.SH Creates (Setup Only)

| Path | File | Purpose |
|------|------|---------|
| `input/*` | (empty dirs) | Ready for your files |
| `Sessions/_TEMPLATES/` | `deal_template.md` | Template for new deals |
| `Sessions/SampleCo/` | `deal.md` | Demo deal |

---

## Data Flow

```
1. YOU ADD SOURCE FILES
   ↓
   input/playbooks/sales_process.pdf
   input/personas/cfo.docx

2. FRAMEWORK CONVERTS
   ↓
   > "Convert all files in input/"
   ↓
   Runtime/_Shared/knowledge/playbook_sales_process.md
   Runtime/_Shared/knowledge/persona_cfo.md

3. YOU CREATE DEAL
   ↓
   Sessions/Acme/deal.md (filled in with context)

4. FRAMEWORK GENERATES ARTIFACTS
   ↓
   > "Coach me on Acme"
   ↓
   Sessions/Acme/artifacts/other/coaching_report.md
   (cites: deal.md, playbook_sales_process.md, persona_cfo.md)
```

---

## FAQs

**Q: Do I need brand guidelines?**
A: No. Framework uses professional defaults if missing. Add for polished outputs.

**Q: Do I need an email style corpus?**
A: No. Framework uses professional style guide if missing. Add for personalized voice.

**Q: What if I don't have playbooks to convert?**
A: Framework still works with just deal notes. Coaching will use generic best practices + methodology guides.

**Q: Can I delete files from input/ after conversion?**
A: Yes, but keep originals as backup. Converted files in knowledge/ are what framework uses.

**Q: What's the minimum to get started?**
A: Just create a deal note (`Sessions/{Deal}/deal.md`). Everything else is optional.

**Q: How do I update brand guidelines?**
A: Edit `Runtime/_Shared/brand/brand_guidelines.md` directly. Changes apply to next generation.

**Q: Where do CRM exports go?**
A: `input/other/` or `Sessions/{Deal}/raw/crm_exports/` (deal-specific)

**Q: Can I version control sample-data/?**
A: Not recommended (company IP). Framework/ is versioned, sample-data/ is gitignored.

---

## Summary

**You create:**
- Source files in `input/` (playbooks, personas, transcripts)
- Configuration files in `Runtime/_Shared/` (brand, style, profile)
- Deal notes in `Sessions/{Deal}/deal.md`

**Framework creates:**
- Structured knowledge in `Runtime/_Shared/knowledge/`
- Artifacts in `Sessions/{Deal}/artifacts/`
- Portfolio views in `Runtime/Dashboard/`

**Start simple:** Just create deal notes. Add knowledge base, brand guidelines, style corpus as you go.
