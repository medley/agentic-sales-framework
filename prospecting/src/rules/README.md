# Rules Configuration System

Phase 1 implementation of the hybrid /prospect system's rules engine.

## Overview

The rules system provides centralized configuration for email generation:

- **Personas**: Title patterns for detecting quality, operations, IT, regulatory roles
- **Angles**: Messaging approaches (regulatory_pressure, operational_cost, audit_readiness)
- **Offers**: CTA definitions with deliverables
- **Subjects**: Subject line options by pain area
- **Constraints**: Writing guidelines (word counts, banned phrases, etc.)
- **Signal Rules**: Scope types and recency thresholds for prospect qualification
- **Tiering**: Tier A (3+ signals) vs Tier B (2+ signals)

## Usage

```python
from rules_loader import load_rules

# Load base config for tier A prospects
rules = load_rules(tier="A")

# Load base config for tier B prospects
rules = load_rules(tier="B")

# Load with experiment overlay (future)
rules = load_rules(experiment="short_subject", tier="A")
```

## Structure

```
rules/
├── base_config.yaml          # Base configuration (always loaded)
├── experiments/              # Experiment overlays (optional)
│   └── example.yaml         # Future: experiment overrides
└── README.md                 # This file
```

## Configuration Sections

### Personas
Maps job titles to persona categories (quality, operations, IT, regulatory).

### Angles
Defines messaging angles with:
- Name and description
- Target personas
- Target industries
- Related pain areas

### Offers
CTA definitions with:
- Deliverable type (checklist, benchmark, architecture)
- Target pain areas
- Target personas
- CTA text

### Subjects
Subject line options organized by pain area.

### Constraints
Writing rules including:
- Word/sentence count limits
- Subject word max
- Banned phrases
- Flags (no_meeting_ask, no_product_pitch)

### Signal Rules
Prospect qualification criteria:
- Scope types (funding_round, leadership_change, etc.)
- Recency thresholds (in days)

### Tiering
Tier definitions:
- Tier A: 3+ signals (high priority)
- Tier B: 2+ signals (standard)

## Extending the System

### Adding New Angles

Edit `base_config.yaml` under the `angles:` section:

```yaml
angles:
  your_new_angle:
    name: "Your Angle Name"
    description: "What this angle addresses"
    personas: ["quality", "operations"]
    industries: ["pharma", "biotech"]
    pain_areas: ["your_pain_area"]
```

### Creating Experiments

Create a new file in `experiments/` directory:

```yaml
# experiments/short_subject.yaml
subjects:
  capa:
    - "CAPA"
    - "Deviations"
```

Load with:
```python
rules = load_rules(experiment="short_subject", tier="A")
```

## Helper Functions

```python
from rules_loader import (
    get_persona_patterns,  # Extract persona title patterns
    get_constraints,       # Extract constraint profile
    get_signal_rules,      # Extract signal detection rules
    clear_cache           # Clear cached configs
)

# Get persona patterns
patterns = get_persona_patterns(rules)
# Returns: {"quality": ["vp quality", ...], ...}

# Get constraints
constraints = get_constraints(rules)
# Returns: {"word_count_min": 50, ...}

# Get signal rules
signals = get_signal_rules(rules)
# Returns: {"scope_types": [...], "recency_thresholds": {...}}
```

## Testing

Run the test suite:

```bash
cd /path/to/Prospecting
python -m pytest tests/test_rules_loader.py -v
```

## Future Enhancements

- [ ] Experiment overlays for A/B testing
- [ ] Industry-specific constraint profiles
- [ ] Dynamic persona detection training
- [ ] Signal weight configuration
- [ ] Template variations per angle
