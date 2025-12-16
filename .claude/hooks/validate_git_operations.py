#!/usr/bin/env python3
"""
Validates git operations to prevent committing company data.
Blocks git add/commit if sample-data/ would be included.
"""
import sys
import json
import subprocess
import re

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
command = tool_input.get("command", "")

# Only check git add/commit commands
if not re.search(r'\bgit\s+(add|commit)', command):
    sys.exit(0)

# Block git add sample-data/
if "git add" in command and "sample-data" in command:
    print(f"❌ BLOCKED: Cannot git add sample-data/", file=sys.stderr)
    print(f"   Command: {command}", file=sys.stderr)
    print(f"", file=sys.stderr)
    print(f"   sample-data/ contains company IP and must stay gitignored.", file=sys.stderr)
    print(f"   Only Framework/ and .claude/ should be versioned.", file=sys.stderr)
    sys.exit(2)

# Check staged files before commit
if "git commit" in command:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            cwd=data.get("cwd", ".")
        )

        staged_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        company_data_files = [f for f in staged_files if f.startswith("sample-data/")]

        if company_data_files:
            print(f"❌ BLOCKED: sample-data/ files are staged for commit", file=sys.stderr)
            print(f"   Files: {', '.join(company_data_files[:5])}", file=sys.stderr)
            if len(company_data_files) > 5:
                print(f"   ... and {len(company_data_files) - 5} more", file=sys.stderr)
            print(f"", file=sys.stderr)
            print(f"   Run: git reset HEAD sample-data/", file=sys.stderr)
            print(f"   Then verify .gitignore is working correctly.", file=sys.stderr)
            sys.exit(2)

    except Exception as e:
        # If validation fails, allow operation but warn
        print(f"⚠️  Warning: Could not validate git operation: {e}", file=sys.stderr)
        sys.exit(0)

sys.exit(0)
