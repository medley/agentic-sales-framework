# Rules System Integration Guide

This guide shows how to integrate the Phase 1 rules system into the prospecting pipeline.

## Quick Start

```python
from rules_loader import load_rules, get_persona_patterns, get_constraints

# Load rules for tier A prospects
rules = load_rules(tier="A")

# Access different rule sections
personas = get_persona_patterns(rules)
constraints = get_constraints(rules)
```

## Integration Points

### 1. Persona Detection

**Location:** Research enrichment phase

```python
from rules_loader import load_rules, get_persona_patterns

def detect_persona(job_title: str) -> str:
    """Detect persona from job title using rules."""
    rules = load_rules(tier="A")
    patterns = get_persona_patterns(rules)

    title_lower = job_title.lower()

    for persona, pattern_list in patterns.items():
        if any(pattern in title_lower for pattern in pattern_list):
            return persona

    return None

# Usage
persona = detect_persona("VP Quality Assurance")
# Returns: "quality"
```

### 2. Signal Qualification (Tiering)

**Location:** Prospect scoring/filtering phase

```python
from rules_loader import load_rules

def qualify_prospect(signals: list, tier: str = "A") -> bool:
    """Check if prospect meets tier requirements."""
    rules = load_rules(tier=tier)
    min_signals = rules["active_tier"]["min_signals"]

    # Count qualifying signals
    qualifying_count = len([s for s in signals if s.get("qualified", False)])

    return qualifying_count >= min_signals

# Usage
signals = [
    {"type": "funding_round", "qualified": True},
    {"type": "leadership_change", "qualified": True},
    {"type": "expansion", "qualified": True}
]

is_tier_a = qualify_prospect(signals, tier="A")  # True (3 >= 3)
is_tier_b = qualify_prospect(signals, tier="B")  # True (3 >= 2)
```

### 3. Angle Selection

**Location:** Email composition phase

```python
from rules_loader import load_rules

def select_angle(persona: str, industry: str) -> dict:
    """Select best messaging angle for persona/industry."""
    rules = load_rules(tier="A")
    angles = rules["angles"]

    # Filter angles by persona and industry
    matching_angles = []
    for angle_key, angle_data in angles.items():
        if persona in angle_data["personas"]:
            if industry in angle_data["industries"]:
                matching_angles.append({
                    "key": angle_key,
                    **angle_data
                })

    # Return first match (or implement more sophisticated selection)
    return matching_angles[0] if matching_angles else None

# Usage
angle = select_angle(persona="quality", industry="pharma")
# Returns angle with pain_areas to explore
```

### 4. CTA Selection

**Location:** Email composition phase

```python
from rules_loader import load_rules

def select_cta(pain_area: str, persona: str) -> dict:
    """Select appropriate CTA for pain area and persona."""
    rules = load_rules(tier="A")
    offers = rules["offers"]

    # Find matching offer
    for offer_key, offer_data in offers.items():
        if pain_area in offer_data["pain_areas"]:
            if persona in offer_data["personas"]:
                return {
                    "key": offer_key,
                    **offer_data
                }

    return None

# Usage
cta = select_cta(pain_area="capa", persona="quality")
# Returns: {"deliverable": "1-page checklist", "text": "If helpful...", ...}
```

### 5. Subject Line Selection

**Location:** Email composition phase

```python
from rules_loader import load_rules
import random

def select_subject(pain_area: str) -> str:
    """Select subject line for pain area."""
    rules = load_rules(tier="A")
    subjects = rules["subjects"]

    subject_options = subjects.get(pain_area, ["Quality initiative"])

    # Return random option (or implement more sophisticated selection)
    return random.choice(subject_options)

# Usage
subject = select_subject(pain_area="audit_readiness")
# Returns: "Audit readiness" or "Audit prep" or "Inspection prep"
```

### 6. Constraint Validation

**Location:** Email composition phase (post-generation validation)

```python
from rules_loader import load_rules, get_constraints

def validate_email(email_body: str, subject: str) -> dict:
    """Validate email against constraints."""
    rules = load_rules(tier="A")
    constraints = get_constraints(rules)

    # Count words and sentences
    word_count = len(email_body.split())
    sentence_count = email_body.count('.') + email_body.count('!') + email_body.count('?')
    subject_word_count = len(subject.split())

    # Check banned phrases
    email_lower = email_body.lower()
    banned_found = [
        phrase for phrase in constraints["banned_phrases"]
        if phrase in email_lower
    ]

    # Build validation result
    result = {
        "valid": True,
        "issues": []
    }

    if word_count < constraints["word_count_min"]:
        result["valid"] = False
        result["issues"].append(f"Too short: {word_count} < {constraints['word_count_min']} words")

    if word_count > constraints["word_count_max"]:
        result["valid"] = False
        result["issues"].append(f"Too long: {word_count} > {constraints['word_count_max']} words")

    if sentence_count < constraints["sentence_count_min"]:
        result["valid"] = False
        result["issues"].append(f"Too few sentences: {sentence_count} < {constraints['sentence_count_min']}")

    if sentence_count > constraints["sentence_count_max"]:
        result["valid"] = False
        result["issues"].append(f"Too many sentences: {sentence_count} > {constraints['sentence_count_max']}")

    if subject_word_count > constraints["subject_word_max"]:
        result["valid"] = False
        result["issues"].append(f"Subject too long: {subject_word_count} > {constraints['subject_word_max']} words")

    if banned_found:
        result["valid"] = False
        result["issues"].append(f"Banned phrases: {', '.join(banned_found)}")

    return result

# Usage
validation = validate_email(
    email_body="I noticed you recently raised Series B...",
    subject="Quick chat"
)
# Returns: {"valid": False, "issues": ["Banned phrases: quick chat"]}
```

### 7. Signal Recency Checking

**Location:** Signal enrichment phase

```python
from rules_loader import load_rules, get_signal_rules
from datetime import datetime, timedelta

def is_signal_recent(signal_type: str, signal_date: datetime) -> bool:
    """Check if signal is within recency threshold."""
    rules = load_rules(tier="A")
    signal_rules = get_signal_rules(rules)

    thresholds = signal_rules["recency_thresholds"]
    max_age_days = thresholds.get(signal_type, 90)  # Default 90 days

    cutoff_date = datetime.now() - timedelta(days=max_age_days)

    return signal_date >= cutoff_date

# Usage
funding_date = datetime(2025, 6, 1)
is_recent = is_signal_recent("funding_round", funding_date)
# Returns: True/False based on 180-day threshold
```

## Complete Pipeline Example

```python
from rules_loader import load_rules, get_persona_patterns, get_constraints
from datetime import datetime

def process_prospect(prospect_data: dict, tier: str = "A"):
    """
    Complete prospect processing using rules system.

    Args:
        prospect_data: Dict with prospect info (title, industry, signals, etc.)
        tier: Prospect tier ("A" or "B")

    Returns:
        Dict with email components or None if prospect doesn't qualify
    """
    # Load rules for tier
    rules = load_rules(tier=tier)

    # 1. Detect persona
    persona = None
    patterns = get_persona_patterns(rules)
    title_lower = prospect_data["title"].lower()

    for p, pattern_list in patterns.items():
        if any(pattern in title_lower for pattern in pattern_list):
            persona = p
            break

    if not persona:
        return None  # Can't identify persona

    # 2. Check signal qualification
    min_signals = rules["active_tier"]["min_signals"]
    if len(prospect_data["signals"]) < min_signals:
        return None  # Doesn't meet tier threshold

    # 3. Select angle
    angles = rules["angles"]
    selected_angle = None

    for angle_key, angle_data in angles.items():
        if persona in angle_data["personas"]:
            if prospect_data["industry"] in angle_data["industries"]:
                selected_angle = angle_data
                selected_angle["key"] = angle_key
                break

    if not selected_angle:
        return None  # No matching angle

    # 4. Select pain area (use first from angle)
    pain_area = selected_angle["pain_areas"][0]

    # 5. Select CTA
    offers = rules["offers"]
    selected_cta = None

    for offer_key, offer_data in offers.items():
        if pain_area in offer_data["pain_areas"]:
            if persona in offer_data["personas"]:
                selected_cta = offer_data
                selected_cta["key"] = offer_key
                break

    # 6. Select subject
    subjects = rules["subjects"]
    subject_options = subjects.get(pain_area, ["Quality initiative"])
    selected_subject = subject_options[0]

    # 7. Get constraints for generation
    constraints = get_constraints(rules)

    # Return all components for email generation
    return {
        "persona": persona,
        "angle": selected_angle,
        "pain_area": pain_area,
        "cta": selected_cta,
        "subject": selected_subject,
        "constraints": constraints,
        "tier": tier
    }

# Usage example
prospect = {
    "name": "Jane Smith",
    "title": "VP Quality Assurance",
    "company": "Acme Pharma",
    "industry": "pharma",
    "signals": [
        {"type": "funding_round", "date": "2025-06-01"},
        {"type": "leadership_change", "date": "2025-07-15"},
        {"type": "expansion", "date": "2025-08-01"}
    ]
}

email_components = process_prospect(prospect, tier="A")

if email_components:
    print(f"Persona: {email_components['persona']}")
    print(f"Angle: {email_components['angle']['name']}")
    print(f"Pain area: {email_components['pain_area']}")
    print(f"Subject: {email_components['subject']}")
    print(f"CTA: {email_components['cta']['deliverable']}")
    # Pass to LLM for generation...
else:
    print("Prospect does not qualify")
```

## A/B Testing with Experiments

```python
from rules_loader import load_rules

# Control group: Base config
control_rules = load_rules(tier="A")

# Test group: Short subject experiment
test_rules = load_rules(experiment="example_short_subject", tier="A")

# Compare
print(f"Control subjects: {control_rules['subjects']['capa']}")
print(f"Test subjects: {test_rules['subjects']['capa']}")

# Track results by experiment variant...
```

## Best Practices

1. **Cache rules at startup**: Call `load_rules()` once during initialization
2. **Use helper functions**: Prefer `get_persona_patterns()` over direct dict access
3. **Validate all outputs**: Always check constraints after LLM generation
4. **Log rule selections**: Track which rules fire for debugging
5. **Clear cache in tests**: Use `clear_cache()` between test runs
6. **Handle missing personas gracefully**: Always have fallback logic
7. **Test with both tiers**: Ensure pipeline works for A and B

## Next Steps

After Phase 1 is working:
- Add industry-specific constraint profiles
- Implement multi-angle selection logic
- Add signal weighting configuration
- Create more experiment overlays
- Add rule-based pain point matching from research data
