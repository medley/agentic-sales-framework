# Prospecting Scripts

## test_setup.py

Validates that the Prospecting module is correctly configured.

**Usage**:
```bash
python3 scripts/utilities/test_setup.py
```

**Tests**:
- ✓ Python dependencies installed (requests, python-dotenv)
- ✓ API keys configured in .env file
- ✓ All Python modules can be imported
- ✓ Cache directory exists and is writable
- ✓ API clients initialize correctly

**Before running**: Create `.env` file by copying `.env.example` and adding your API keys.

---

## run_prospect_research.py

Runs end-to-end prospect research workflow.

**Usage**:
```bash
# Basic usage
python3 scripts/run_prospect_research.py "John Smith" "Acme Corp"

# Force fresh research (skip cache)
python3 scripts/run_prospect_research.py "John Smith" "Acme Corp" --force-refresh

# Save research brief to file
python3 scripts/run_prospect_research.py "John Smith" "Acme Corp" --save-brief /path/to/brief.md
```

**Output**:
- Contact profile (name, title, email, phone)
- Company profile (industry, size, tech stack, pains)
- Triggers (recent news, events)
- Email context (personalization hooks, pain points)
- JSON output for programmatic use

**Note**: Requires valid ZoomInfo and Perplexity API keys in `.env` file.

---

## Quick Start

1. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Configure API keys**:
   ```bash
   cp .env.example .env
   # Edit .env and add your actual API keys
   ```

3. **Test setup**:
   ```bash
   python3 scripts/test_setup.py
   ```

4. **Run prospect research**:
   ```bash
   python3 scripts/run_prospect_research.py "John Smith" "Acme Pharma"
   ```

5. **Or use the slash command**:
   ```bash
   /prospect "John Smith" "Acme Pharma"
   ```
