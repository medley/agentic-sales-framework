#!/bin/bash
# Agentic Sales Framework - One-Command Install

set -e  # Exit on error

echo "=========================================="
echo "Agentic Sales Framework - Installation"
echo "=========================================="
echo ""

# Check prerequisites
echo "✓ Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ first:"
    echo "   https://nodejs.org"
    exit 1
fi

if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code not found. Please install Claude Code first:"
    echo "   https://code.claude.com"
    exit 1
fi

echo "  ✓ Node.js installed"
echo "  ✓ Claude Code installed"
echo ""

# Create directory structure
echo "✓ Creating directory structure..."

mkdir -p sample-data/input/{playbooks,personas,battlecards,transcripts,emails,other}
mkdir -p sample-data/Runtime/_Shared/knowledge
mkdir -p sample-data/Runtime/_Shared/brand/assets
mkdir -p sample-data/Runtime/_Shared/style
mkdir -p sample-data/Runtime/_Shared/profile
mkdir -p sample-data/Runtime/Sessions/_TEMPLATES
mkdir -p sample-data/Runtime/Dashboard

echo "  ✓ sample-data directories created"
echo ""

# Copy templates
echo "✓ Setting up templates..."

if [ ! -f "sample-data/Runtime/Sessions/_TEMPLATES/deal_template.md" ]; then
    cp Framework/Templates/deal_template.md sample-data/Runtime/Sessions/_TEMPLATES/
fi

echo "  ✓ Templates ready"
echo ""

# Create demo deal
echo "✓ Creating demo deal (SampleCo)..."

if [ ! -d "sample-data/Runtime/Sessions/SampleCo" ]; then
    mkdir -p sample-data/Runtime/Sessions/SampleCo
    cat > sample-data/Runtime/Sessions/SampleCo/deal.md << 'EOF'
---
deal_id: SampleCo
company_name: "SampleCo Manufacturing"
stage: "Discovery"
methodology: "Sandler"
deal_value: "$450,000"
close_date_target: "2025-Q2"
created_on: "2025-11-15"
last_updated: "2025-11-15"
---

# Deal: SampleCo Manufacturing

## Overview
Mid-market manufacturer ($80M revenue) looking to replace legacy quality management system. Current manual processes causing compliance risk and audit delays.

## Current Stage: Discovery
- Completed initial discovery call (Nov 10)
- Identified pain: Failed FDA audit cost $2.3M in Q3
- Next: Demo scheduled for Nov 22

## Stakeholders
- **Jennifer Torres** - VP Quality (Champion, 8/10 strength)
  - Pain owner, driving initiative
  - Reports to COO
  - Budget authority: Up to $200K

- **David Kim** - COO (Economic Buyer)
  - Not yet engaged directly
  - Approved $500K capex budget for quality initiatives
  - Final signoff required for >$200K

- **Robert Chen** - IT Director (Technical Buyer)
  - Concerned about integration complexity
  - Gatekeeps all software purchases
  - Warm to solution, needs API specs

## Pain Identified
- Failed FDA audit Q3 2024: $2.3M in fines + production shutdown
- Manual document control: 40 hrs/week across 3 FTE
- Audit prep time: 6 weeks (industry average: 2 weeks)
- Compliance risk: Paper-based NCR tracking, no traceability

## Budget
- Approved capex: $500K (quality initiatives, not deal-specific)
- Decision criteria: ROI < 18 months, FDA compliance guarantee
- Timeline: Must implement before Q2 FDA re-audit

## Competition
- Incumbent: Homegrown Access database (18 years old, unsupported)
- Also evaluating: ETQ, CompetitorA (both >$600K quotes)

## Next Actions
- [ ] Schedule COO intro (via Jennifer) - By Nov 18
- [ ] Send API integration specs to Robert - By Nov 16
- [ ] Prep demo focused on audit readiness - Nov 22 demo
- [ ] Build ROI model (current state cost vs solution) - By Nov 20

## Notes
- Strong champion (Jennifer) but needs Economic Buyer engagement
- Budget exists but not allocated to this deal yet
- Timeline is tight (Q2 deadline = 4 months to implement)
- Risk: Multiple stakeholders not yet aligned on urgency
EOF

    echo "  ✓ Demo deal created: SampleCo Manufacturing"
else
    echo "  ✓ Demo deal already exists"
fi

echo ""

# Verify structure
echo "✓ Verifying installation..."

if [ -d "sample-data/Runtime/Sessions/SampleCo" ] && \
   [ -f "sample-data/Runtime/Sessions/SampleCo/deal.md" ] && \
   [ -d "sample-data/Runtime/_Shared/knowledge" ]; then
    echo "  ✓ Installation verified"
else
    echo "  ❌ Installation verification failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start Claude Code:"
echo "   $ claude"
echo ""
echo "2. Try the demo deal:"
echo '   > "Coach me on the SampleCo deal"'
echo ""
echo "3. See what the framework can do:"
echo '   > "What should I do next with SampleCo?"'
echo '   > "Draft a follow-up email for SampleCo"'
echo ""
echo "4. Create your first real deal:"
echo "   $ mkdir sample-data/Runtime/Sessions/YourDeal"
echo "   $ cp sample-data/Runtime/Sessions/_TEMPLATES/deal_template.md sample-data/Runtime/Sessions/YourDeal/deal.md"
echo "   (Then edit the deal.md file with your deal details)"
echo ""
echo "Documentation:"
echo "  - Quick Start: Framework/System/SETUP.md"
echo "  - Architecture: Framework/System/ARCHITECTURE.md"
echo "  - Developers: Framework/System/DEVELOPER_GUIDE.md"
echo ""
echo "=========================================="
