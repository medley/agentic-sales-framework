#!/usr/bin/env python3
"""
Validates deal.md files follow the expected structure.
Ensures agents can reliably parse deal context and Dataview dashboards work.
"""
import sys
import json
import re

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
path = tool_input.get("file_path", "")
content = tool_input.get("content", "")

# Only validate deal.md files
if not path.endswith("/deal.md"):
    sys.exit(0)

# Skip template file
if "_TEMPLATES" in path:
    sys.exit(0)

# Required sections in deal note
REQUIRED_SECTIONS = [
    "## Stakeholders",
    "## History",
]

# At least one of these methodology tracking sections recommended
METHODOLOGY_SECTIONS = [
    "## MEDDPICC",
    "## D1 Actions",
    "## D7 Strategic"
]

errors = []
warnings = []

# Check for required sections
for section in REQUIRED_SECTIONS:
    if section not in content:
        errors.append(f"Missing required section: {section}")

# Check for at least one methodology section (warning only)
has_methodology_section = any(section in content for section in METHODOLOGY_SECTIONS)
if not has_methodology_section:
    warnings.append("No methodology tracking section found (MEDDPICC, D1, D7)")

# Validate frontmatter for Dataview compatibility
if content.strip().startswith("---"):
    try:
        frontmatter = content.split("---", 2)[1]

        # Check methodology field (warning only)
        if "methodology:" not in frontmatter:
            warnings.append("No methodology specified in frontmatter (will use generic practices)")

        # Validate stage_num field (CRITICAL for Dataview)
        if "stage_num:" not in frontmatter:
            errors.append("Missing 'stage_num:' field (required for Dataview dashboards)")
        else:
            stage_num_match = re.search(r'stage_num:\s*(\S+)', frontmatter)
            if stage_num_match:
                value = stage_num_match.group(1)
                if not value.isdigit():
                    errors.append(f"Invalid stage_num: '{value}' (must be numeric 0-5)")

        # Validate acv field (CRITICAL for Dataview sum queries)
        if "acv:" not in frontmatter:
            errors.append("Missing 'acv:' field (required for Dataview dashboards)")
        else:
            acv_match = re.search(r'acv:\s*(\S+)', frontmatter)
            if acv_match:
                value = acv_match.group(1)
                # Check for invalid formatting ($ or commas)
                if '$' in value or ',' in value:
                    errors.append(f"Invalid acv: '{value}' (must be numeric only - no $ or commas)")
                elif not value.replace('.', '').isdigit() and value != "0":
                    errors.append(f"Invalid acv: '{value}' (must be numeric, e.g., 144781.11)")

        # Validate close_date format (warning for Dataview date queries)
        if "close_date:" in frontmatter:
            close_date_match = re.search(r'close_date:\s*(\S+)', frontmatter)
            if close_date_match:
                value = close_date_match.group(1).strip('"\'')
                # Check YYYY-MM-DD format
                if not re.match(r'^\d{4}-\d{2}-\d{2}$', value) and value not in ["", "YYYY-MM-DD"]:
                    warnings.append(f"Invalid close_date format: '{value}' (should be YYYY-MM-DD)")

    except IndexError:
        errors.append("Malformed frontmatter (missing closing ---)")

# Report errors
if errors:
    print(f"❌ Deal note validation failed for {path}:", file=sys.stderr)
    for error in errors:
        print(f"   • {error}", file=sys.stderr)
    print(f"", file=sys.stderr)
    print(f"   Agents may fail to parse this deal note.", file=sys.stderr)
    print(f"   See sample-data/Runtime/Sessions/_TEMPLATES/deal_template.md for structure.", file=sys.stderr)
    sys.exit(2)

# Report warnings (don't block)
if warnings:
    print(f"⚠️  Deal note warnings for {path}:", file=sys.stderr)
    for warning in warnings:
        print(f"   • {warning}", file=sys.stderr)

sys.exit(0)
