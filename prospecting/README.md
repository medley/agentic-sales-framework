# Prospecting Module

> **Portfolio Project:** Sales prospecting automation system built with Claude Code to demonstrate AI-assisted development capabilities. Created for an Enterprise AE role application at Anthropic.

**Skills Demonstrated:**
- Python architecture (modular design, validation layers, confidence modes)
- LLM integration (Anthropic Claude API, prompt engineering, output validation)
- External API integration (ZoomInfo, SEC EDGAR, Perplexity)
- Test-driven development (pytest, comprehensive test coverage)
- Production-quality documentation and code organization

Research prospects and generate first-touch emails with verifiable personalization.

**Last updated:** 2025-12-11

---

## Start Here

| If you want to... | Read this |
|-------------------|-----------|
| Understand the system in 5 minutes | [Overview](#overview) below |
| Know what must NOT break | [docs/SYSTEM_BOUNDARIES.md](docs/SYSTEM_BOUNDARIES.md) |
| Run your first prospect research | [Quick Start](#quick-start) below |
| See how components interact | [docs/PROSPECT_FLOW.md](docs/PROSPECT_FLOW.md) |
| Modify rules or components | [CONTRIBUTING.md](CONTRIBUTING.md) |

---

## Overview

### What This System Does

1. **Researches prospects** via ZoomInfo (contact data) and Perplexity (company intel)
2. **Extracts verifiable signals** from research (news, events, public data)
3. **Selects messaging strategy** based on persona and signals
4. **Generates personalized emails** in a consultative Sandler/Challenger voice
5. **Validates all claims** are backed by cited sources

### What This System Does NOT Do

- **Fact-check source URLs** (stores them but doesn't verify accuracy)
- **Guarantee LLM output** (validation catches most but not all issues)
- **Allow unsupported claims** (confidence modes prevent this)
- **Use vendor data as explicit claims** (ZoomInfo data guides strategy only)

### The Trust Model

Every personalized claim must trace back to a cited source. The system enforces this through:

- **Signal extraction** - Only public, citable data becomes "signals"
- **Confidence modes** - 3+ signals = explicit claims, 0 signals = generic only
- **Validation** - Signal integrity checks run on every generated email

This is not optional. See [docs/SYSTEM_BOUNDARIES.md](docs/SYSTEM_BOUNDARIES.md).

---

## Quick Start

### 1. Install Dependencies

```bash
cd prospecting
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env and add:
# - ZOOMINFO_USERNAME (your ZoomInfo email)
# - ZOOMINFO_CLIENT_ID (from ZoomInfo admin console)
# - ZOOMINFO_PRIVATE_KEY_FILE (path to .pem file)
# - PERPLEXITY_API_KEY
# - ANTHROPIC_API_KEY
```

### 3. Verify Setup

```bash
python scripts/utilities/test_setup.py
```

### 4. Run Prospect Research

**Via slash command (recommended):**
```bash
/prospect "John Smith" "Acme Pharma"
```

**Via Python script:**
```bash
python scripts/run_prospect_research.py "John Smith" "Acme Pharma"
```

### What Happens

1. Contact lookup via ZoomInfo (or cache)
2. Company research via Perplexity
3. Signal extraction and confidence mode assignment
4. Angle selection based on persona + signals
5. Email generation with validation
6. Output saved to account folder

---

## Glossary

**Cited Signal**: A factual claim with a source URL. The URL is stored but not validated for accuracy.

**Source Type**: Classification of signal origin:
| Type | Can Make Explicit Claims? |
|------|---------------------------|
| `public_url` | Yes |
| `user_provided` | Yes |
| `vendor_data` | No - guides strategy only |
| `inferred` | No - generic language only |

**Confidence Mode**: Automatic enforcement level based on cited signal count:
| Mode | Signals | What's Allowed |
|------|---------|----------------|
| HIGH | 3+ | Explicit company claims with citations |
| MEDIUM | 1-2 | Company mentions, limited specificity |
| LOW | 0 | Industry language only |

**Angle**: Pre-defined messaging approach (e.g., `regulatory_pressure`, `operational_cost`)

**Persona**: Role-based categorization (e.g., `quality`, `operations`, `regulatory`)

**Tier**: Prospect qualification level (Tier A = 3+ signals, Tier B = 2+ signals)

---

## Directory Structure

```
prospecting/
├── README.md                 # You are here
├── CONTRIBUTING.md           # How to safely modify the system
├── requirements.txt
├── .env.example
│
├── docs/                     # Documentation
│   ├── SYSTEM_BOUNDARIES.md  # Safety constraints (READ THIS)
│   ├── VALIDATION_FLOW.md    # How emails are validated
│   ├── CONFIDENCE_MODES.md   # Trust model details
│   ├── PROSPECT_FLOW.md      # Visual architecture diagram
│   ├── LIBRARY_EDITING_GUIDE.md  # Editing YAML rules
│   ├── PATH_INDICATORS.md    # Angle scoring diagnostics
│   ├── FAQ.md                # Common questions
│   ├── SPEED_OPTIMIZATIONS.md
│   ├── ZOOMINFO_QUICKSTART.md
│   └── archive/              # Historical implementation notes
│
├── src/                      # Python source code
│   ├── rules/                # YAML configuration
│   │   ├── base_config.yaml  # Main rules file
│   │   └── experiments/      # A/B test variants
│   ├── relevance_engine.py   # Signal extraction, angle selection
│   ├── validators.py         # Signal integrity validation
│   ├── quality_controls.py   # Structure/quality checks
│   ├── voice_validator.py    # Voice consistency
│   ├── hybrid_email_generator.py  # Email generation
│   ├── llm_renderer.py       # LLM integration
│   ├── llm_angle_scorer.py   # Angle ranking
│   └── ...
│
├── scripts/                  # Executable scripts
│   ├── run_prospect_research.py
│   ├── prepare_email_context.py
│   ├── generate_hybrid_email.py
│   └── utilities/            # Setup/test utilities
│
├── tests/                    # Test suite
├── examples/                 # Demo scripts
├── deliverables/             # Output storage
└── .cache/                   # Research cache (90-day TTL)
```

---

## Using the Rules System

### Load Rules

```python
from src.rules_loader import load_rules

# Load for tier A prospects
rules = load_rules(tier="A")

# Access sections
personas = rules["personas"]
angles = rules["angles"]
constraints = rules["constraints"]
```

### Detect Persona

```python
from src.rules_loader import get_persona_patterns

patterns = get_persona_patterns(rules)
title = "VP Quality Assurance"

for persona, pattern_list in patterns.items():
    if any(p in title.lower() for p in pattern_list):
        print(f"Detected persona: {persona}")
```

### Run with Experiments

```python
# Load experimental rules
rules = load_rules(experiment="short_subject", tier="A")
```

---

## Caching

| Data Type | TTL | Location |
|-----------|-----|----------|
| Contact data | 90 days | `.cache/prospects/` |
| Company data | 90 days | `.cache/prospects/` |
| Perplexity research | 30 days | `.cache/prospects/` |

Force refresh with:
```bash
python scripts/run_prospect_research.py "Name" "Company" --force-refresh
```

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| ZoomInfo contact not found | Uses placeholder, continues with company research |
| ZoomInfo rate limit | Falls back to cached data or WebSearch |
| Perplexity timeout | Uses generic pain points |
| Insufficient signals | Falls back to generic/industry language |
| Validation failure | Attempts repair (2x), then falls back |

The system degrades gracefully. An email is always generated, but personalization depth varies based on available data.

---

## Documentation Status

### Active (Current System)

| Document | Purpose |
|----------|---------|
| `README.md` | Entry point, overview |
| `CONTRIBUTING.md` | Modification guidelines |
| `docs/SYSTEM_BOUNDARIES.md` | Safety constraints |
| `docs/VALIDATION_FLOW.md` | Validation pipeline |
| `docs/CONFIDENCE_MODES.md` | Trust model |
| `docs/PROSPECT_FLOW.md` | Architecture diagram |
| `docs/LIBRARY_EDITING_GUIDE.md` | YAML editing |
| `docs/PATH_INDICATORS.md` | Diagnostics |

### Historical Reference

| Location | Contents |
|----------|----------|
| `docs/archive/` | 15 implementation notes from system evolution |

Archive docs are not required reading. Useful for understanding design decisions but may be outdated.

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific tests
pytest tests/test_validators.py -v
pytest tests/test_relevance_engine.py -v

# Verify imports
python -c "from src.rules_loader import load_rules; print('OK')"
```

---

## Troubleshooting

**API key not found:**
- Check `.env` file exists
- Verify key names match `.env.example`

**Cache not working:**
- Check `.cache/prospects/` directory exists
- Check file permissions

**Validation failing:**
- Check word count (50-100 words)
- Check for banned phrases
- Ensure email ends with "?"
- Review `docs/VALIDATION_FLOW.md`

**Low confidence mode when expecting high:**
- Check signal count (need 3+ for HIGH)
- Verify signals have `source_type: public_url`
- Review `docs/CONFIDENCE_MODES.md`

---

## Privacy & Compliance

This module processes contact data from third-party sources. Users are responsible for:

- **Data licensing**: Ensure your ZoomInfo (or other data provider) subscription permits your intended use
- **Email regulations**: Comply with CAN-SPAM, GDPR, CASL, and other applicable email laws
- **Consent requirements**: Some jurisdictions require prior consent before outreach
- **Data retention**: Configure cache TTLs appropriately for your compliance requirements
- **Terms of service**: Respect rate limits and usage terms of all integrated APIs

This tool is designed for legitimate B2B sales outreach. It does not bypass any verification systems or access restricted data. All personalization is derived from publicly available information or licensed data sources.

---

## Getting Help

- **Architecture questions:** [docs/PROSPECT_FLOW.md](docs/PROSPECT_FLOW.md)
- **Safety questions:** [docs/SYSTEM_BOUNDARIES.md](docs/SYSTEM_BOUNDARIES.md)
- **Modification questions:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Common issues:** [docs/FAQ.md](docs/FAQ.md)
