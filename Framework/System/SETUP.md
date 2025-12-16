# Setup Guide - Agentic Sales Framework

Complete installation and configuration guide for getting the framework running on your machine.

---

## Quick Start (Recommended)

**For first-time users, use the automated installer:**

```bash
# Clone the repo
git clone <your-repo-url>
cd agentic-sales-framework

# Run installer (creates directories + demo deal)
./install.sh

# Start Claude Code
claude

# Try the demo
> "Coach me on the SampleCo deal"
```

The installer creates all directories, sets up templates, and includes a pre-loaded demo deal so you can see value immediately.

**For manual installation or troubleshooting, follow the detailed steps below.**

---

## 1. Prerequisites

Install the following before starting:

### Required
- **Claude Code** - [Install instructions](https://code.claude.com/docs/en/overview)
- **Node.js** (v18+) - Required for Claude Code and framework orchestration
- **Python** (3.10+) - Required for skill scripts
- **Git** - Recommended for version control
- **Text Editor** - Any markdown editor works (VS Code, Obsidian, Typora, etc.)

### Package Dependencies

After cloning, install dependencies:

```bash
# Node.js dependencies (from repo root)
npm install

# Python dependencies (from repo root)
pip install -r requirements.txt

# For prospecting module
pip install -r prospecting/requirements.txt
```

### Optional (for specific skills)

Some skills require additional system tools:

- **LibreOffice** - Required for ROI model Excel recalculation and presentation thumbnails
  - macOS: `brew install --cask libreoffice`
  - Linux: `sudo apt install libreoffice`
- **Poppler utilities** - Required for PDF thumbnail generation
  - macOS: `brew install poppler`
  - Linux: `sudo apt install poppler-utils`
- **Playwright browsers** - Required for HTML-to-PowerPoint conversion
  - Run: `npx playwright install chromium`

**Operating System:** macOS, Linux, or Windows (WSL recommended on Windows)

---

## 2. Get the Framework

### Option A: Clone from Repository

```bash
git clone <your-repo-url>
cd agentic-sales-framework
```

### Option B: Download and Extract

1. Download the framework ZIP
2. Extract to your preferred location
3. Open terminal in the extracted directory

---

## 3. Create Directory Structure

The framework needs a `sample-data/` directory for your company-specific files. This directory is **gitignored** and contains proprietary information.

Run this command from the repo root:

```bash
mkdir -p sample-data/input/{playbooks,personas,battlecards,transcripts}
mkdir -p sample-data/Runtime/_Shared/knowledge
mkdir -p sample-data/Runtime/Sessions/_TEMPLATES
```

**Verify structure:**
```bash
tree -L 3 sample-data/
```

Should show:
```
sample-data/
├── input/
│   ├── playbooks/
│   ├── personas/
│   ├── battlecards/
│   └── transcripts/
└── Runtime/
    ├── _Shared/
    │   └── knowledge/
    └── Sessions/
        └── _TEMPLATES/
```

**IMPORTANT:** Directory names are case-sensitive:
- Use lowercase: `input/`, `knowledge/`
- Not capitalized: ~~`Input/`~~, ~~`Knowledge/`~~

---

## 4. Configure Claude Code

### Point Claude Code at Repository Root

1. Open terminal in the repo root directory
2. Run Claude Code:
   ```bash
   claude
   ```
3. Claude Code will automatically load `CLAUDE.md` from the repo root

### Verify Configuration

In Claude Code, type:
```
What framework am I working with?
```

Claude should respond with information about the Agentic Sales Framework and mention the three-layer architecture. If it doesn't, it's not reading `CLAUDE.md` correctly.

**Troubleshooting:**
- Ensure you're running `claude` from the repo root (not a subdirectory)
- Check that `CLAUDE.md` exists in the current directory
- Run `pwd` to verify you're in the correct location

---

## 5. First Conversion (Validation Test)

Let's validate the framework by converting a sample document.

### Step 1: Add a Test Document

Create a simple test file:

```bash
cat > sample-data/input/test_persona.txt << 'EOF'
# CFO Persona

**Role:** Chief Financial Officer
**Priorities:** Cost reduction, ROI, budget approval
**Pain Points:** Manual processes, compliance risk, audit complexity
**Decision Criteria:** Proven ROI, implementation timeline, vendor stability
EOF
```

### Step 2: Run Conversion

In Claude Code, type:
```
Convert the test_persona.txt file in sample-data/input/
```

### Step 3: Verify Output

Check that a file was created:
```bash
ls sample-data/Runtime/_Shared/knowledge/
```

You should see: `persona_cfo.md` (or similar)

**View the converted file:**
```bash
cat sample-data/Runtime/_Shared/knowledge/persona_*.md
```

**Expected output:**
- Frontmatter with `source_path`, `converted_on`, `doc_type`
- Executive Summary
- Key Facts (extracted from source)
- Validation section
- Augmentation section (clearly labeled)
- Gaps and suggested actions

**If this works, your framework is correctly configured.** ✅

---

## 6. Create Your First Deal

### Step 1: Copy Template

```bash
cp Framework/Templates/deal_template.md sample-data/Runtime/Sessions/TestDeal/deal.md
```

Or create the directory first if needed:
```bash
mkdir -p sample-data/Runtime/Sessions/TestDeal
cp Framework/Templates/deal_template.md sample-data/Runtime/Sessions/TestDeal/deal.md
```

### Step 2: Edit Deal Note

Open `sample-data/Runtime/Sessions/TestDeal/deal.md` in your editor and fill in:

**Required fields:**
- Company name
- Current stage (e.g., Discovery, Demo, Negotiation)
- Key stakeholders (at least one)
- Brief context

**Optional fields:**
- Methodology (MEDDPICC, Sandler, etc.)
- Close date target
- Deal value

### Step 3: Test Coach Agent

In Claude Code:
```
How is the TestDeal looking? What should I do next?
```

Claude should:
1. Read your deal note
2. Identify current stage
3. Point out missing information
4. Suggest next actions

---

## 7. Run First Workflow

Now test a complete workflow: prep for a discovery call.

In Claude Code:
```
Prep me for a discovery call with TestDeal tomorrow
```

**Expected output:**
- A new file: `sample-data/Runtime/Sessions/TestDeal/deal_coach_discovery_YYYY-MM-DD.md`
- Contains:
  - Status summary
  - Discovery questions (based on methodology if specified)
  - Key topics to cover
  - Risk areas to probe
  - Suggested agenda
  - Draft confirmation email

**If you get this, the framework is fully operational.** ✅

---

## 8. Set Up Workspace UI (Required)

**IMPORTANT:** Always open your workspace UI (Obsidian, VS Code, etc.) at the `sample-data/` folder, NOT the repo root.

**Why:**
- **IP Protection:** Framework/ contains your intellectual property and system internals
- **Clean Experience:** AEs should only see deals, dashboard, and knowledge base
- **Ready to Sell:** Users never see technical implementation details
- **Focused Navigation:** Only relevant files visible

### Where to Run Claude Code vs Where to Open Obsidian

**Critical distinction:**

```bash
# Terminal (Claude Code): ALWAYS run from repo root
cd /path/to/agentic_sales_framework
claude

# Obsidian/Editor: ALWAYS open sample-data folder only
Open vault → /path/to/agentic_sales_framework/sample-data
```

**Why this separation:**
- **Claude Code needs repo root:** Reads CLAUDE.md, accesses Framework/, reads/writes sample-data/
- **Obsidian needs sample-data only:** Your workspace, hides Framework from view

---

### Option A: Obsidian (Recommended)

Obsidian provides the best experience for navigating deal notes and knowledge base.

1. Download [Obsidian](https://obsidian.md)
2. Open Obsidian → "Open folder as vault"
3. Select **`sample-data/` folder** (inside your repo, NOT the repo root)
4. Disable Safe Mode if prompted

**Benefits:**
- Visual navigation of deals and knowledge
- Link preview between files
- Search across all notes
- Graph view of relationships
- Framework/ is invisible (by design)

### Option B: VS Code

1. Open **`sample-data/` folder** in VS Code (not repo root)
2. Install "Markdown All in One" extension
3. Use Explorer sidebar to navigate files
4. Framework remains hidden from view

### Option C: Any Text Editor

The framework works with any markdown editor. Always open **`sample-data/` folder**, not repo root. Framework should remain invisible to end users.

---

## 9. Load Your Company Data

Now that the framework is validated, add your real company documents.

### What to Add

**For complete file organization guide, see: [FILE_ORGANIZATION.md](../../FILE_ORGANIZATION.md)**

Quick summary - place these in `sample-data/input/`:

**Essential:**
- Sales playbook (PDF, DOCX, or MD)
- Key personas (CFO, VP Operations, etc.)
- Product information

**Recommended:**
- Stage guides (what to do at each sales stage)
- Battlecards (vs competitors)
- Case studies
- Pricing sheets

**Optional:**
- Call transcripts (for style corpus building)
- Email threads (for context)
- Past proposals (as templates)

### Optional Configuration Files

**Brand guidelines** (improves output quality):
- Path: `sample-data/Runtime/_Shared/brand/brand_guidelines.md`
- Template: See `Framework/System/brand_guidelines_spec.md`
- Used by: Email, agenda, briefing generation

**Email style corpus** (personalizes voice):
- Path: `sample-data/Runtime/_Shared/style/email_style_corpus_{yourname}.md`
- Contents: 20-30 of your sent emails
- Used by: Email generation

**AE profile** (links to style):
- Path: `sample-data/Runtime/_Shared/profile/ae_profile.md`
- Contents: Your name, profile_id, contact info
- Used by: Email signature, style loading

### Convert Everything

In Claude Code:
```
Convert all files in sample-data/input/
```

This processes each file and creates structured markdown in `sample-data/Runtime/_Shared/knowledge/`.

**Review outputs** to ensure quality and accuracy. The converter adds augmentation (clearly labeled) and identifies gaps.

---

## 10. Daily Workflow

Once set up, your typical workflow:

### Starting a New Deal
```bash
mkdir sample-data/Runtime/Sessions/CompanyName
cp Framework/Templates/deal_template.md sample-data/Runtime/Sessions/CompanyName/deal.md
# Edit deal.md with initial context
```

### Before a Call
```
Prep me for [discovery|demo|negotiation] call with CompanyName
```

### After a Call
Update deal note with outcomes, then:
```
What should I do next with CompanyName?
```

### Generate Follow-Up
```
Draft follow-up email for CompanyName after today's demo
```

### Check Portfolio Health
```
Generate portfolio status
```

### Create Handover Doc
```
Generate handover doc for CompanyName (deal just closed)
```

---

## 11. Troubleshooting

### "Claude can't find the deal file"

**Check the path:**
```bash
ls sample-data/Runtime/Sessions/YourDeal/deal.md
```

If missing, create it from template (see Step 6).

### "Knowledge base is empty"

You haven't run the conversion yet:
```
Convert all files in sample-data/input/
```

### "Claude doesn't know about the framework"

Claude Code isn't loading `CLAUDE.md`. Verify:
1. You're running `claude` from repo root
2. `CLAUDE.md` exists in current directory
3. Run `pwd` to check location

### "Generated file has no frontmatter"

This indicates a bug in the agent/skill. Check:
1. Agent spec in `.claude/skills/` or skill spec in `.claude/skills/`
2. Review `Framework/System/DEVELOPER_GUIDE.md` for frontmatter requirements

### "Converter is hallucinating information"

The converter should only extract facts from source and clearly label augmentation. If it's adding unsubstantiated claims:
1. Review the output
2. Check `.claude/skills/convert-and-file/SKILL.md` for rules
3. Adjust augmentation guidelines if needed

### "Framework is slow"

Optimization tips:
1. Keep knowledge base organized (archive old files)
2. Use targeted commands ("prep for discovery" vs "tell me everything")
3. Don't scan entire knowledge base unnecessarily
4. Check `CLAUDE.md` file size (should be <200 lines)

---

## 12. Next Steps

### Learn More

- **[Framework/System/DEVELOPER_GUIDE.md](Framework/System/DEVELOPER_GUIDE.md)** - Detailed protocols for agents and skills
- **[Framework/System/architecture_visual.md](Framework/System/architecture_visual.md)** - Visual system architecture
- **[CLAUDE.md](CLAUDE.md)** - Core operating rules (auto-loaded by Claude Code)

### Customize the Framework

- Add custom methodologies in `Framework/Methodologies/`
- Create new skills in `.claude/skills/`
- Build new agents in `.claude/skills/`
- See DEVELOPER_GUIDE.md for protocols

### Build Your Style Corpus (Future)

To make generated emails sound like you:
1. Export sent emails from Gmail
2. Place in `sample-data/input/emails/`
3. Run style builder skill (when implemented)
4. Email generator will use your voice

---

## 13. Verification Checklist

Before using in production, verify:

- [ ] Directory structure created (`sample-data/input/`, `Runtime/`, etc.)
- [ ] Claude Code loads `CLAUDE.md` correctly
- [ ] Test conversion worked (persona file created with frontmatter)
- [ ] Created first deal note from template
- [ ] Coach agent responded with context-aware advice
- [ ] Generated workflow artifact (discovery briefing)
- [ ] Company documents converted to knowledge base
- [ ] Can navigate files comfortably (Obsidian or other editor)

**If all checked, you're ready for production use.** ✅

---

## 14. Getting Help

**Documentation:**
- `CLAUDE.md` - Quick reference
- `DEVELOPER_GUIDE.md` - Comprehensive protocols
- `architecture_visual.md` - System design

**Common Issues:**
- File paths: Ensure you're using correct capitalization (`sample-data/input/` not `companydata/input/`)
- Permissions: Claude Code needs read/write access to `sample-data/`
- Frontmatter: All generated files must have YAML frontmatter

**Best Practices:**
- Keep `CLAUDE.md` concise (<200 lines)
- Update deal notes after every interaction
- Review converted knowledge for accuracy
- Archive old deals to `sample-data/Runtime/Sessions/Archive/`

---

## Setup Complete! 🎉

You now have a fully functional AI sales operating system.

**Start using it immediately:**
1. Add your next deal
2. Prep for your next call
3. Generate your next follow-up email

The more you use it, the better it gets. Deal context accumulates, knowledge base grows, and workflows become second nature.

**Pro tip:** Use it for ONE real deal this week. Don't try to migrate everything at once. Validate value on a single opportunity first.