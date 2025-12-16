# Library Editing Guide

All email components are in **ONE file:**
```
src/email_components.py
```

---

## Quick Reference

| Component | Line Number | What It Controls |
|-----------|-------------|------------------|
| **PAIN_LIBRARY** | Line 59 | Pain point descriptions (10 pains) |
| **TRIGGER_LIBRARY** | Line 147 | Regulatory triggers (3 triggers) |
| **CTA_LIBRARY** | Line 171 | Offer-based CTAs (9 CTAs) |
| **SUBJECT_LIBRARY** | Line 228 | Subject lines by pain area |

---

## How to Edit Each Section

### 1. Adding a New Pain Point (Line 59)

**Format:**
```python
"pain_key_name": {
    "personas": ["quality"],              # Who feels this pain
    "industries": ["pharma", "biotech"],  # Where it's relevant
    "text": "Your pain description here (25-40 words).",
    "question": "Your qualifying question?",  # Optional, can be None
    "pain_area": "category_name",         # For CTA matching
    "metrics": ["metric1", "metric2"]     # What you'd measure
}
```

**Example - Add a new "complaint handling" pain:**
```python
"complaint_handling_backlog": {
    "personas": ["quality", "regulatory"],
    "industries": ["medical_device"],
    "text": "Most medical device QA teams tell me complaint handling turnaround times are the bottleneck, especially when root cause investigations require cross-functional input and documentation rigor is high.",
    "question": "Is complaint handling cycle time a focus this year, or already handled?",
    "pain_area": "complaints",
    "metrics": ["complaint closure time", "investigation duration"]
}
```

**Important:**
- Keep "text" between 25-40 words
- "question" should be 8-15 words or None
- Use real industry language (DHF, CAPA, batch records, etc.)

---

### 2. Adding a New Trigger (Line 147)

**Format:**
```python
"trigger_key_name": {
    "industries": ["pharma"],           # Which industries this applies to
    "active_until": "2027-12-31",      # When trigger expires
    "text": "Your trigger context here (15-25 words).",
    "trigger_type": "regulatory_deadline"  # or "enforcement_climate"
}
```

**Example - Add EU MDR trigger:**
```python
"eu_mdr_2026": {
    "industries": ["medical_device"],
    "active_until": "2026-05-26",
    "text": "With EU MDR transition deadlines approaching, device manufacturers are finding technical file gaps and clinical evaluation requirements more extensive than expected.",
    "trigger_type": "regulatory_deadline"
}
```

**Important:**
- Date format: "YYYY-MM-DD"
- Keep text 15-25 words
- System auto-filters expired triggers

---

### 3. Adding a New CTA (Line 171)

**Format:**
```python
"pain_area_name": {
    "personas": ["quality"],
    "deliverable": "1-page guide",
    "text": "Want the guide, or not a priority?"
}
```

**Example - Add complaint CTA:**
```python
"complaints": {
    "personas": ["quality", "regulatory"],
    "deliverable": "complaint cycle time benchmark",
    "text": "Want the complaint handling benchmark (medical device companies), or not relevant?"
}
```

**Important:**
- "pain_area_name" must match a pain's "pain_area" field
- Always include easy "no" option ("or not a priority?", "or not relevant?")
- Be specific about deliverable (not "resources" or "info")

---

### 4. Adding New Subject Lines (Line 228)

**Format:**
```python
"pain_area_name": ["Option 1", "Option 2", "Option 3"]
```

**Example - Add complaint subjects:**
```python
"complaints": ["Complaint handling", "Complaint backlog", "Complaint cycle time"]
```

**Important:**
- 1-4 words optimal
- First option is default
- Pain-specific, not generic

---

## Editing Workflow

### Option 1: Direct Edit (Fast)

1. Open file:
   ```bash
   code src/email_components.py
   ```

2. Navigate to line number (Cmd+G in VS Code)

3. Copy existing entry, modify for new use case

4. Save and test:
   ```bash
   python3 test_email_assembler.py
   ```

---

### Option 2: Add via Script (Safe)

Create a helper script:

```python
# add_pain.py
from src.email_components import EmailComponentLibrary

# This would require modifying email_components.py to support dynamic additions
# For now, direct edit is recommended
```

**Recommendation:** Use Option 1 (direct edit) for now

---

## Testing Your Changes

After editing, run tests:

```bash
python3 test_email_assembler.py
```

**What to check:**
1. ✅ No syntax errors
2. ✅ New components appear in matching
3. ✅ Generated emails still 50-100 words
4. ✅ CTAs still offer-based

---

## Common Edits

### Edit 1: Change Existing Pain Text

**File:** `email_components.py`
**Line:** 59+ (find the pain key)

**Before:**
```python
"text": "I'm seeing QA teams pushed to shorten deviation and CAPA cycle time..."
```

**After:**
```python
"text": "Most pharma QA teams tell me CAPA closure times are the #1 audit finding, especially when investigations span multiple departments and approval loops slow down corrective actions."
```

**Save and test.**

---

### Edit 2: Update Trigger Expiration Date

**File:** `email_components.py`
**Line:** 147+ (find the trigger key)

**Before:**
```python
"active_until": "2026-02-02"
```

**After:**
```python
"active_until": "2027-02-02"  # Extended another year
```

---

### Edit 3: Add New Industry Support

**File:** `email_components.py`
**Line:** 59+ (find the pain)

**Before:**
```python
"industries": ["pharma", "biotech"]
```

**After:**
```python
"industries": ["pharma", "biotech", "medical_device"]  # Now works for med device too
```

---

### Edit 4: Refine CTA Wording

**File:** `email_components.py`
**Line:** 171+ (find the CTA)

**Before:**
```python
"text": "If helpful, I can send a 1-page checklist. Want it?"
```

**After:**
```python
"text": "Want the 1-page CAPA time sink checklist, or is this already handled?"
```

**More specific → better.**

---

## Voice Consistency Checklist

When adding/editing components, ensure the sales rep's voice:

✅ **Do:**
- Short, plain English
- Specific operational pains
- Binary/easy "no" options
- Industry jargon okay (DHF, CAPA, etc.)
- Direct, calm tone

❌ **Don't:**
- Buzzwords ("transformational", "best-in-class")
- Corporate speak ("synergies", "circle back")
- Long sentences
- Vague pains ("quality challenges")
- Pressure language

---

## Real Example: Adding Full Pain + CTA + Subject

Let's add "data migration" pain for IT persona:

### Step 1: Add Pain (Line 59)

```python
"data_migration_risk": {
    "personas": ["it"],
    "industries": ["pharma", "biotech", "medical_device"],
    "text": "Most IT leaders tell me data migration and system cutover are the highest risk moments in QMS upgrades, especially when validation and audit trail continuity matter.",
    "question": "Is a QMS migration on your roadmap, or keeping current systems?",
    "pain_area": "migration",
    "metrics": ["migration duration", "data loss risk"]
}
```

### Step 2: Add CTA (Line 171)

```python
"migration": {
    "personas": ["it"],
    "deliverable": "migration checklist",
    "text": "Want the 1-page QMS migration checklist (validation + audit trail continuity), or not planning a change?"
}
```

### Step 3: Add Subject (Line 228)

```python
"migration": ["QMS migration", "Data migration", "System cutover"]
```

### Step 4: Test

```bash
python3 test_email_assembler.py
```

**Expected:** New pain shows up for IT persona, matches properly.

---

## Maintenance Tips

**Weekly:**
- Review which pains get replies → keep those
- A/B test subject lines → update SUBJECT_LIBRARY

**Monthly:**
- Add 1-2 new pains based on real conversations
- Update trigger dates if deadlines shift
- Refine CTA wording based on feedback

**Quarterly:**
- Archive underperforming pains
- Add industry variations
- Expand persona coverage

---

## File Structure

```
Prospecting/
└── src/
    └── email_components.py  ← EDIT THIS FILE
        ├── Line 59:  PAIN_LIBRARY (10 pains)
        ├── Line 147: TRIGGER_LIBRARY (3 triggers)
        ├── Line 171: CTA_LIBRARY (9 CTAs)
        └── Line 228: SUBJECT_LIBRARY (9 pain areas)
```

**That's it. One file to rule them all.**

---

## Quick Edit Commands

Open file:
```bash
code src/email_components.py
```

Jump to section:
- **Pains:** Cmd+G → type "59" → Enter
- **Triggers:** Cmd+G → type "147" → Enter
- **CTAs:** Cmd+G → type "171" → Enter
- **Subjects:** Cmd+G → type "228" → Enter

Test changes:
```bash
python3 test_email_assembler.py
```

---

## Help

**Syntax errors?**
→ Check Python dict formatting (commas, quotes, brackets)

**Component not matching?**
→ Verify "personas" and "industries" tags match
→ Check "pain_area" matches between PAIN and CTA

**Email too long?**
→ Shorten "text" field (aim for 25-40 words per component)

**Need to add more personas?**
→ Line 22: Add patterns to PERSONA_PATTERNS dict
