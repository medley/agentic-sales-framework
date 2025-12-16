# Quick Start

## Try It Now (60 Seconds)

```bash
# Clone and start
git clone https://github.com/medley/agentic-sales-framework.git
cd agentic-sales-framework
claude
```

Then type: `Coach me on the SampleCo deal`

**Requires:** [Claude Code](https://claude.ai/download) installed

---

## What the Demo Shows

The repo includes a sample deal called **SampleCo** - a fictional mid-market manufacturer in the Discovery stage.

In Claude Code, try these commands:

### 1. Get Deal Coaching
```
Coach me on the SampleCo deal
```

**What you'll see:**
- Risk analysis (missing Economic Buyer engagement, tight timeline)
- Stage assessment (Discovery → needs to progress)
- 3-5 specific next actions with rationale
- Source citations for every claim

### 2. Get Next Actions
```
What should I do next with SampleCo?
```

**What you'll see:**
- Prioritized action list (D1 = today, D7 = this week)
- Calendar-ready tasks with deadlines
- Rationale for each action

### 3. Draft a Follow-Up Email
```
Draft follow-up email for SampleCo after discovery call
```

**What you'll see:**
- Ready-to-send email (no placeholders)
- References actual stakeholders from the deal
- Includes next steps with dates
- Professional tone

---

## Create Your First Real Deal

Once you've tried the demo, create a real deal:

```bash
# 1. Create deal directory
mkdir -p sample-data/Runtime/Sessions/YourCompany

# 2. Copy template
cp sample-data/Runtime/Sessions/_TEMPLATES/deal_template.md \
   sample-data/Runtime/Sessions/YourCompany/deal.md

# 3. Edit the deal file
# Open sample-data/Runtime/Sessions/YourCompany/deal.md
# Fill in:
#   - Company name
#   - Current stage (Discovery, Demo, Negotiation, etc.)
#   - Key stakeholders
#   - Brief context
```

Then run:
```
Coach me on the YourCompany deal
```

The framework will analyze your deal and recommend next actions.

---

## What You Can Do

**Deal Management:**
- `"Coach me on [deal]"` → Risk analysis + next actions
- `"What should I do next with [deal]?"` → Prioritized action list
- `"Generate portfolio status"` → Pipeline health dashboard

**Call Prep:**
- `"Prep me for discovery with [company]"` → Agenda + questions + email
- `"Prep for demo with [company]"` → Demo script + areas to probe

**Artifact Generation:**
- `"Draft follow-up email for [company]"` → Ready-to-send email
- `"Create handover doc for [company]"` → Customer success doc

**Knowledge Management:**
- `"Convert the playbook in input/"` → Structured knowledge base

---

## Add Your Company Data

To make the framework truly useful, add your company's sales materials.

### Quick Guide

**Source files** (you add these):
```bash
sample-data/input/
├── playbooks/          # Sales playbooks, methodology guides
├── personas/           # Buyer personas (CFO, VP Ops, etc.)
├── battlecards/        # Competitive positioning
├── transcripts/        # Call recordings (text)
└── emails/             # Email threads for style corpus
```

**Configuration files** (optional, you create):
```bash
sample-data/Runtime/_Shared/
├── brand/
│   └── brand_guidelines.md         # Your company's brand standards
├── style/
│   └── email_style_corpus_you.md   # Your personal email style (20-30 examples)
└── profile/
    └── ae_profile.md               # Your AE profile (links to style)
```

**Then convert:**
```
Convert all files in sample-data/input/
```

The framework creates structured markdown in `sample-data/Runtime/_Shared/knowledge/` that it references when coaching.

**For complete file organization guide:** See [FILE_ORGANIZATION.md](FILE_ORGANIZATION.md)

---

## Workspace Setup (Optional)

For better navigation, open your workspace UI (Obsidian, VS Code) at the **sample-data/** folder (not repo root).

**Why:**
- Clean view (only deals and knowledge, no technical files)
- Visual navigation between notes
- Graph view of relationships (Obsidian)

**Recommended: Obsidian**
1. Download [Obsidian](https://obsidian.md) (free)
2. Open vault → Select `sample-data/` folder
3. Navigate deals visually

**Alternative: VS Code**
1. Open `sample-data/` folder in VS Code
2. Install "Markdown All in One" extension

---

## Daily Workflow

**Before a call:**
```
Prep me for [discovery|demo|negotiation] with [Company]
```

**After a call:**
1. Update deal note with outcomes
2. Run: `What should I do next with [Company]?`

**Weekly pipeline review:**
```
Generate portfolio status
```

---

## Troubleshooting

**"Claude can't find the deal file"**
- Check path: `sample-data/Runtime/Sessions/YourDeal/deal.md`
- Ensure directory name matches what you're asking for

**"Knowledge base is empty"**
- You haven't converted company files yet
- Run: `Convert all files in sample-data/input/`

**"Output has placeholders like {{NAME}}"**
- Deal note is missing required information
- Add stakeholder names, dates, commitments to deal.md

---

## Next Steps

- **Full setup guide:** [SETUP.md](Framework/System/SETUP.md)
- **How it works:** [ARCHITECTURE.md](Framework/System/ARCHITECTURE.md)
- **Customization:** [DEVELOPER_GUIDE.md](Framework/System/DEVELOPER_GUIDE.md)

---

## Questions?

1. **Installation issues?** → See [SETUP.md](Framework/System/SETUP.md) Section 11 (Troubleshooting)
2. **Want to customize?** → See [DEVELOPER_GUIDE.md](Framework/System/DEVELOPER_GUIDE.md)
3. **Found a bug?** → Open an issue on GitHub

---

**That's it!** You're now running an AI sales operating system on your machine.

Start with the SampleCo demo, then add your first real deal. The more context you add to deal notes, the better the coaching and artifacts become.
