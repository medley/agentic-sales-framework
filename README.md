# Agentic Sales Framework

[![CI](https://github.com/medley/agentic-sales-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/medley/agentic-sales-framework/actions/workflows/ci.yml)

A Claude Code-native system that automates enterprise sales workflows. Built to support long, multi-stakeholder sales cycles where context gets lost.

> **Production Context**: This is an open-source reference implementation. 

## Quick Start

```bash
git clone https://github.com/medley/agentic-sales-framework.git
cd agentic-sales-framework
claude
```

Then: `Coach me on the SampleCo deal`

Requires [Claude Code](https://claude.ai/download). See [QUICKSTART.md](QUICKSTART.md) for full guide.

## What It Does

- **Discovery prep** - Turns deal context into structured call preparation
- **Deal coaching** - Methodology-based gap analysis and next steps
- **Sales communications** - Email generation matched to my voice and methodology
- **Account intake** - Processes new opportunities into structured deal files
- **Prospecting** - Hybrid deterministic + LLM system for research and outreach

## How It Works

11 executable skills running inside Claude Code. Each skill has a SKILL.md specification that defines inputs, outputs, and methodology.

Built around my actual workflow as an enterprise AE, not generic prompts.

## Modules

### Prospecting (`prospecting/`)

A Python-based prospecting module demonstrating:
- Confidence-based email generation (HIGH/MEDIUM/LOW/GENERIC modes)
- 6-layer validation pipeline to prevent hallucination
- Integration patterns for ZoomInfo, SEC EDGAR, and Perplexity APIs

See [prospecting/README.md](prospecting/README.md) for details.

## Stack

- Claude Code native (`.claude/skills/` auto-discovery)
- Sandler methodology support (extensible to other methodologies)
- Human-in-the-loop design (supports judgment, doesn't replace it)

## Data Safety

This repository contains **no customer data, proprietary information, or PII**. All examples use synthetic data (fictional companies like "Northwind Manufacturing").

See [DATA_POLICY.md](DATA_POLICY.md) for verification steps and design decisions.

```bash
# Verify with gitleaks
gitleaks detect --source . --verbose
```

## Related

- [RunSales.ai](https://runsales.ai) - SaaS product built on this framework
