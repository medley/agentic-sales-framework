#!/usr/bin/env python3
"""
Enhanced frontmatter validation for generated and converted documents.
Validates schema compliance, ISO timestamps, and source path existence.
"""
import sys
import json
import re
import os
from datetime import datetime

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
path = tool_input.get("file_path", "")
content = tool_input.get("content", "")

# Only validate markdown files in Runtime/
if "Runtime/" not in path or not path.endswith(".md"):
    sys.exit(0)

# Skip certain files
if "deal.md" in path or "stage_inventory__" in path or "_TEMPLATES" in path:
    sys.exit(0)

if not content or not content.strip().startswith("---"):
    print(f"❌ Missing frontmatter in: {path}", file=sys.stderr)
    print(f"   All generated/converted files require YAML frontmatter.", file=sys.stderr)
    sys.exit(2)

# Extract frontmatter
try:
    frontmatter = content.split("---", 2)[1]
except IndexError:
    print(f"❌ Malformed frontmatter in: {path}", file=sys.stderr)
    sys.exit(2)

errors = []

# Different validation for generated vs converted content
is_generated = "Runtime/Sessions" in path
is_converted = "Runtime/_Shared/knowledge" in path and "stage_inventory__" not in path

# Validation for generated content (deal artifacts)
if is_generated:
    required_fields = ["generated_by:", "generated_on:", "deal_id:"]
    missing = [f for f in required_fields if f not in frontmatter]
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")

    # Validate ISO timestamp format
    timestamp_match = re.search(r'generated_on:\s*["\']?([^"\'\n]+)', frontmatter)
    if timestamp_match:
        try:
            datetime.fromisoformat(timestamp_match.group(1).replace('Z', '+00:00'))
        except ValueError:
            errors.append("Invalid ISO timestamp format in generated_on (use YYYY-MM-DDTHH:MM:SSZ)")

# Validation for converted content (knowledge files)
if is_converted:
    required_fields = ["source_path:", "converted_on:", "doc_type:"]
    missing = [f for f in required_fields if f not in frontmatter]
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")

    # Validate ISO timestamp
    timestamp_match = re.search(r'converted_on:\s*["\']?([^"\'\n]+)', frontmatter)
    if timestamp_match:
        try:
            datetime.fromisoformat(timestamp_match.group(1).replace('Z', '+00:00'))
        except ValueError:
            errors.append("Invalid ISO timestamp format in converted_on (use YYYY-MM-DDTHH:MM:SSZ)")

# Validate sources field if present (for generated content)
if "sources:" in frontmatter:
    # Extract file paths from sources list
    sources_section = re.search(r'sources:\s*\n((?:\s*-\s*.+\n?)+)', frontmatter)
    if sources_section:
        source_paths = re.findall(r'-\s*(.+)', sources_section.group(1))
        project_dir = data.get("cwd", ".")

        for source_path in source_paths:
            source_path = source_path.strip().strip('"\'')
            # Skip Framework/ paths as they're always available (versioned)
            if not source_path.startswith("Framework/"):
                full_path = os.path.join(project_dir, source_path)
                if not os.path.exists(full_path):
                    errors.append(f"Source file does not exist: {source_path}")

# Validate source_path field if present (for converted content)
if "source_path:" in frontmatter:
    source_match = re.search(r'source_path:\s*(.+)', frontmatter)
    if source_match:
        source_path = source_match.group(1).strip().strip('"\'')
        project_dir = data.get("cwd", ".")
        full_path = os.path.join(project_dir, source_path)
        if not os.path.exists(full_path):
            errors.append(f"Source file does not exist: {source_path}")

# Report errors
if errors:
    print(f"❌ Frontmatter validation failed for {path}:", file=sys.stderr)
    for error in errors:
        print(f"   • {error}", file=sys.stderr)
    print(f"", file=sys.stderr)
    print(f"   See DEVELOPER_GUIDE.md § Frontmatter Specifications", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
