# FAQ - Intelligent Email System

## Q1: Does this still work with voice loading?

**Answer: YES - Now it does!**

I added **automatic voice validation** to the email assembler.

### How It Works

Every generated email is now validated against the sales rep's voice guidelines:

✅ **Checks for:**
- Banned phrases ("circle back", "synergies", "best-in-class", etc.)
- Word count (50-100 words optimal)
- Sentence count (3-5 sentences)
- Binary/qualifying questions
- Subject length (≤7 words)
- No exclamation marks (professional tone)
- Offer-based CTAs

✅ **Reports:**
```
Voice issues: None ✅
```
or
```
Voice issues: ['Contains banned phrase: synergies', 'Too long: 105 words']
```

### What Changed

**Before:**
- Components were pre-written in the sales rep's voice
- But no validation after assembly
- Risk of voice drift over time

**After:**
- Components still pre-written in the sales rep's voice
- **+ Automatic validation after assembly**
- Voice issues flagged immediately
- Ensures consistency

### Example Output

```python
email = assembler.generate_email(research, 'Sarah')

print(email['stats']['voice_issues'])
# → [] (empty = passed all checks ✅)
```

### Files Added

- **`src/voice_validator.py`** - Voice validation logic
- Integrated into **`src/email_assembler.py`** - Runs automatically

---

## Q2: Where can I fine-tune the library of pain points, triggers, CTAs, etc.?

**Answer: ONE FILE - `email_components.py`**

### Quick Reference

```
src/email_components.py
```

| Component | Line Number | What to Edit |
|-----------|-------------|--------------|
| **Pain points** | Line 59 | Pain descriptions, qualifying questions |
| **Regulatory triggers** | Line 147 | Deadlines, enforcement climate |
| **CTAs (offers)** | Line 171 | Deliverables, offer language |
| **Subject lines** | Line 228 | 1-4 word subject options |

### How to Edit

1. **Open file:**
   ```bash
   code src/email_components.py
   ```

2. **Navigate to section:**
   - Pains: Cmd+G → type "59"
   - Triggers: Cmd+G → type "147"
   - CTAs: Cmd+G → type "171"
   - Subjects: Cmd+G → type "228"

3. **Copy existing entry, modify, save**

4. **Test:**
   ```bash
   python3 test_email_assembler.py
   ```

### Example: Adding New Pain

```python
"complaint_handling": {
    "personas": ["quality", "regulatory"],
    "industries": ["medical_device"],
    "text": "Most medical device QA teams tell me complaint handling turnaround times are the bottleneck, especially when root cause investigations require cross-functional input.",
    "question": "Is complaint handling cycle time a focus this year?",
    "pain_area": "complaints",
    "metrics": ["complaint closure time"]
}
```

### Example: Adding New CTA

```python
"complaints": {
    "personas": ["quality", "regulatory"],
    "deliverable": "complaint cycle time benchmark",
    "text": "Want the complaint handling benchmark, or not relevant?"
}
```

### Full Guide

See **`LIBRARY_EDITING_GUIDE.md`** for detailed examples and best practices.

---

## Q3: How do I know if components are in the correct voice?

**Use the voice validator!**

### Validate Individual Components

```python
from src.voice_validator import VoiceValidator

validator = VoiceValidator()

# Test a pain text
pain_text = "Your new pain description here..."
issues = validator.validate_component(pain_text, "pain")

if issues:
    print("❌ Voice issues:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("✅ Passes voice check")
```

### What It Checks

**For pain text:**
- 25-40 words
- No banned phrases
- Direct, operational language

**For CTAs:**
- Uses offer language ("Want", "Should I", "Open to")
- Includes easy "no" ("or not", "or is", "or already")
- No pressure language

**For triggers:**
- 15-25 words
- Regulatory/business context
- No fear-mongering

---

## Q4: Can I override the system's choices?

**YES - Manual override available.**

### Use Case

System selects "CAPA" pain, but you want "batch release" instead.

### How

```python
assembler = EmailAssembler()

email = assembler.generate_email_with_override(
    research,
    contact_name="John",
    persona="operations",       # Force persona
    pain_area="batch_release"   # Force pain
)
```

### Available Options

List all available choices:

```python
options = assembler.list_available_options()

print(options['personas'])    # ['quality', 'operations', 'it', 'regulatory']
print(options['pain_areas'])  # ['capa', 'batch_release', 'system_sprawl', ...]
```

---

## Q5: How does persona detection work?

### Title Patterns

| Title Contains | Detected As |
|----------------|-------------|
| "vp quality", "qa director" | quality |
| "vp operations", "plant director" | operations |
| "cio", "vp it", "cto" | it |
| "vp regulatory", "regulatory affairs" | regulatory |

### What If Title Doesn't Match?

System defaults to **quality** persona (safest fallback).

### Adding New Patterns

Edit `email_components.py` line 22:

```python
PERSONA_PATTERNS = {
    "quality": [
        "vp quality", "qa director",
        "your new pattern here"  # Add here
    ]
}
```

---

## Q6: How does pain matching work?

### Matching Logic

1. **Get all pains** for persona
2. **Filter by industry** (if available)
3. **Return top match**

### Example

**Input:**
- Persona: quality
- Industry: pharma

**Matching:**
- Pharma + quality → capa_cycle_time, audit_readiness, supplier_oversight
- **Selected:** capa_cycle_time (first match)

### Changing Priority

Reorder pains in `PAIN_LIBRARY` (line 59):
- First match = highest priority
- System picks top match

---

## Q7: How do regulatory triggers work?

### Trigger Selection

1. **Get all triggers** for industry
2. **Filter expired** (past active_until date)
3. **Return first active trigger**

### Example

**Medical device industry:**
- qmsr_2026 (active until Feb 2, 2026) ✅
- fda_inspection_climate (active until Dec 31, 2026) ✅

**System picks:** qmsr_2026 (more specific)

### Updating Trigger Dates

Edit `TRIGGER_LIBRARY` (line 147):

```python
"qmsr_2026": {
    "active_until": "2027-02-02"  # Extend if needed
}
```

### Adding New Triggers

```python
"eu_mdr_2026": {
    "industries": ["medical_device"],
    "active_until": "2026-05-26",
    "text": "With EU MDR transition deadlines approaching...",
    "trigger_type": "regulatory_deadline"
}
```

---

## Q8: What if I want emails without triggers?

### Option 1: Remove from Library

Comment out trigger in `TRIGGER_LIBRARY` (line 147):

```python
# "qmsr_2026": {
#     ...
# }
```

### Option 2: Expire Trigger

Set `active_until` to past date:

```python
"qmsr_2026": {
    "active_until": "2020-01-01"  # Expired
}
```

System will skip expired triggers automatically.

---

## Q9: Can I A/B test subject lines?

**YES - Multiple options per pain area.**

### How Subject Selection Works

System picks **first option** from list:

```python
SUBJECT_LIBRARY = {
    "capa": ["CAPA backlog", "Deviation cycle time", "CAPA closure"]
}
```

**Default:** "CAPA backlog"

### A/B Testing

1. **Test variant A:** Use "CAPA backlog"
2. **Test variant B:** Reorder list:
   ```python
   "capa": ["Deviation cycle time", "CAPA backlog"]
   ```
3. **Track replies** for each
4. **Keep winner** in first position

---

## Q10: How do I track what works?

### Manual Tracking (Now)

Create spreadsheet:
| Contact | Persona | Pain | Trigger | Subject | Reply? |
|---------|---------|------|---------|---------|--------|
| Sarah | quality | capa | fda_inspection | CAPA backlog | Yes |
| John | operations | batch_release | None | Batch release | No |

### Identify Patterns

- Which pains get replies?
- Which triggers work?
- Which CTAs convert?

### Optimize Library

- Keep high-reply components
- Archive low-reply components
- A/B test variations

---

## Summary

### Voice Loading
✅ **YES** - Automatic voice validation added
- Checks banned phrases, word count, tone
- Reports issues in email stats
- Ensures voice consistency

### Library Editing
✅ **ONE FILE** - `src/email_components.py`
- Line 59: Pains
- Line 147: Triggers
- Line 171: CTAs
- Line 228: Subjects

### Testing
```bash
python3 test_email_assembler.py
```

### Documentation
- **`INTELLIGENT_EMAIL_SYSTEM.md`** - How system works
- **`LIBRARY_EDITING_GUIDE.md`** - How to edit components
- **`FAQ.md`** - This file

---

## Quick Commands

**Open library:**
```bash
code src/email_components.py
```

**Test changes:**
```bash
python3 test_email_assembler.py
```

**Validate voice:**
```python
from src.voice_validator import VoiceValidator
validator = VoiceValidator()
issues = validator.validate(subject, body)
```

**Generate email:**
```python
from src.email_assembler import EmailAssembler
assembler = EmailAssembler()
email = assembler.generate_email(research, contact_name)
```
