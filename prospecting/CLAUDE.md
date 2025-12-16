# CLAUDE.md - Claude Code Project Configuration

> This file helps Claude Code understand the project structure and integration points.

## Project Overview

**Prospecting Module** - A hybrid deterministic + LLM system for sales prospecting that demonstrates:
- Confidence-based generation (HIGH/MEDIUM/LOW/GENERIC modes)
- 6-layer validation pipeline to prevent hallucination
- Integration with ZoomInfo, SEC EDGAR, and Perplexity APIs

## Architecture

```
src/
├── hybrid_email_generator.py   # Main orchestrator
├── relevance_engine.py         # Deterministic signal extraction (69KB)
├── validators.py               # 6-layer validation pipeline (28KB)
├── execution_mode.py           # Claude Code environment detection
└── rules/                      # YAML-based configuration
    ├── personas.yaml           # Title pattern matching
    └── angles.yaml             # Industry/persona filtering
```

## Claude Code Integration Points

### Environment Detection
The system detects when running inside Claude Code:
```python
# src/execution_mode.py
def is_inside_claude_code() -> bool:
    """Returns True if executing within Claude Code environment."""
```

### Handoff Pattern
Python handles deterministic logic, Claude Code handles final generation:
1. `scripts/prepare_email_context.py` → Prepares JSON artifacts
2. Claude Code consumes artifacts for email generation
3. `validators.py` validates output against confidence rules

### Temperature Tuning
- **0.0** for scoring (reproducibility)
- **0.3** for repair attempts
- **0.7** for email rendering (voice flexibility)

## Key Constraints

### NEVER modify:
- `src/validators.py` validation logic without updating tests
- Confidence mode rules (HIGH/MEDIUM/LOW/GENERIC)
- Source type enforcement (public_url vs vendor_data)

### Testing requirements:
```bash
pytest tests/ -v                    # Run all tests
pytest tests/ -v -m "not slow"      # Skip slow integration tests
```

## Quick Reference

| Task | Command |
|------|---------|
| Run prospect research | `python scripts/run_prospect_research.py --account "Company Name"` |
| Validate email output | `python scripts/validate_email.py --input draft.json` |
| Run tests | `pytest tests/ -v` |

## Documentation

- [SYSTEM_BOUNDARIES.md](docs/SYSTEM_BOUNDARIES.md) - What must NOT break
- [VALIDATION_FLOW.md](docs/VALIDATION_FLOW.md) - 6-layer validation pipeline
- [CONFIDENCE_MODES.md](docs/CONFIDENCE_MODES.md) - HIGH/MEDIUM/LOW/GENERIC rules
- [PROSPECT_FLOW.md](docs/PROSPECT_FLOW.md) - Complete architecture diagram
