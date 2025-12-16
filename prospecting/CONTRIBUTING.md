# Contributing to Prospecting

This guide explains how to safely modify the Prospecting system. **Read this before making changes.**

---

## Before You Start

### Required Reading

1. **[SYSTEM_BOUNDARIES.md](docs/SYSTEM_BOUNDARIES.md)** - Understand what must not break
2. **[VALIDATION_FLOW.md](docs/VALIDATION_FLOW.md)** - Understand how emails are validated
3. **[CONFIDENCE_MODES.md](docs/CONFIDENCE_MODES.md)** - Understand the trust model

### Development Setup

```bash
cd prospecting

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Verify setup
python scripts/utilities/test_setup.py
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_validators.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

---

## DO NOT CHANGE (System Invariants)

These components enforce safety guarantees. **Do not modify without explicit approval and safety review.**

### Signal Integrity Validation

**File:** `src/validators.py`
**Functions:**
- `validate_signal_integrity()` - Ensures signal IDs exist
- `validate_source_type_compliance()` - Ensures vendor data isn't used for claims

**Why it's critical:** Prevents hallucinated personalization and vendor data leakage.

**If you think you need to change this:** You probably don't. Understand the implications first.

---

### Confidence Mode Thresholds

**File:** `src/rules/base_config.yaml` (lines ~189-200)
**Section:** `confidence_modes:`

**Why it's critical:** Controls when explicit claims are allowed. Lowering thresholds allows claims with insufficient evidence.

**If you think you need to change this:** Document the business justification and get sign-off.

---

### Angle Scoring Temperature

**Files:** `src/llm_angle_scorer.py`, `src/relevance_engine.py`
**Setting:** `temperature=0.0`

**Why it's critical:** Angle scoring must be reproducible. Non-zero temperature makes results non-deterministic.

**If you think you need to change this:** You're probably trying to solve the wrong problem.

---

### Fallback Signal Integrity Bypass

**File:** `src/hybrid_email_generator.py`
**Behavior:** Signal integrity checks run even in fallback modes

**Why it's critical:** Ensures no email ever makes unsupported claims, even when other validation is relaxed.

**If you think you need to change this:** Stop. This is the final safety net.

---

## Safe to Modify (Configuration Knobs)

These can be changed without safety review, but still require testing.

### YAML Rules (`src/rules/base_config.yaml`)

**Safe changes:**
- Add new personas (with patterns)
- Add new angles (with pain points, triggers)
- Add new offers (with descriptions)
- Modify word count ranges
- Add banned phrases
- Adjust signal recency thresholds

**Example: Adding a new persona**
```yaml
personas:
  # Existing personas...

  supply_chain:
    patterns:
      - "vp supply chain"
      - "director supply chain"
      - "head of logistics"
    priority: 5
    default_angles:
      - supply_visibility
      - vendor_compliance
```

**After changing:** Run `pytest tests/test_rules_loader.py -v`

---

### Email Components (`src/email_components.py`)

**Safe changes:**
- Edit pain point text
- Update CTA wording
- Add subject line variants
- Modify template sentences

**After changing:** Run `pytest tests/test_email_assembler.py -v`

---

### LLM Temperatures (with caution)

| Setting | Current | Safe Range | Purpose |
|---------|---------|------------|---------|
| Rendering | 0.7 | 0.5-0.9 | Voice flexibility |
| Repair | 0.3 | 0.1-0.4 | Precision |
| Angle scoring | 0.0 | **0.0 only** | Reproducibility |

**After changing:** Generate 10+ sample emails and manually review.

---

## How to Add New Components

### Adding a New Angle

1. **Define in YAML** (`src/rules/base_config.yaml`):
```yaml
angles:
  new_angle_id:
    name: "New Angle Name"
    personas: [quality, operations]  # Which personas this applies to
    pain_points:
      - "First pain point text"
      - "Second pain point text"
    triggers:
      - pattern: "keyword to detect"
        weight: 0.8
    priority: 3
```

2. **Add tests** (`tests/test_relevance_engine.py`):
```python
def test_new_angle_selection():
    # Test that angle is selected for appropriate signals
    pass
```

3. **Test end-to-end**:
```bash
python scripts/run_prospect_research.py "Test Contact" "Test Company"
```

---

### Adding a New Signal Source

1. **Define source type** in `src/relevance_engine.py`:
```python
VALID_SOURCE_TYPES = [
    'public_url',
    'vendor_data',
    'user_provided',
    'inferred',
    'new_source_type'  # Add here
]
```

2. **Decide claim permissions** - Can this source make explicit claims?
   - If YES: Add to allowed types in `validators.py`
   - If NO: Leave it out (default is no explicit claims)

3. **Update documentation** in `docs/SYSTEM_BOUNDARIES.md`

4. **Add tests** for the new source type

---

### Adding a New Validation Check

1. **Determine which layer** (see `docs/VALIDATION_FLOW.md`):
   - Signal integrity → `validators.py`
   - Structure/quality → `quality_controls.py`
   - Voice → `voice_validator.py`

2. **Implement the check**:
```python
def validate_new_check(email_text: str, constraints: dict) -> Tuple[bool, List[str]]:
    issues = []
    # Your validation logic
    if problem_found:
        issues.append("Description of the issue")
    return len(issues) == 0, issues
```

3. **Add to validation pipeline** in the appropriate module

4. **Add tests**:
```python
def test_new_check_passes():
    # Valid case
    pass

def test_new_check_fails():
    # Invalid case
    pass
```

5. **Update `docs/VALIDATION_FLOW.md`** with the new check

---

## Code Style

### Python

- Follow PEP 8
- Use type hints for function signatures
- Docstrings for public functions
- No unused imports

### YAML

- 2-space indentation
- Comments for non-obvious configurations
- Group related settings

### Commits

```
type: short description

Longer description if needed.

Refs: #issue-number (if applicable)
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

---

## Pull Request Checklist

Before submitting:

- [ ] Read `docs/SYSTEM_BOUNDARIES.md` (if touching validation)
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] No new test failures introduced
- [ ] Documentation updated (if behavior changed)
- [ ] Manual testing with sample prospect
- [ ] No changes to invariant code (or explicit approval obtained)

### For Safety-Critical Changes

If your PR touches:
- `validators.py`
- `confidence_modes` in YAML
- Fallback behavior in `hybrid_email_generator.py`

Then also:
- [ ] Documented business justification
- [ ] Explicit approval from team lead
- [ ] Additional manual testing with edge cases
- [ ] Updated `docs/SYSTEM_BOUNDARIES.md` if boundaries changed

---

## Getting Help

- **Architecture questions:** Read `docs/PROSPECT_FLOW.md`
- **Validation questions:** Read `docs/VALIDATION_FLOW.md`
- **"Can I change X?":** Check this document's DO NOT CHANGE section
- **Still stuck:** Review the architecture docs in the docs/ folder

---

## Summary

| Change Type | Review Required | Test Required | Doc Update |
|-------------|-----------------|---------------|------------|
| YAML rules | No | Yes | No |
| Email components | No | Yes | No |
| LLM temperatures | Caution | Yes + manual | No |
| New angle/persona | No | Yes | Optional |
| New signal source | Yes | Yes | Yes |
| New validation check | Yes | Yes | Yes |
| Invariant code | **Approval required** | Yes | Yes |
