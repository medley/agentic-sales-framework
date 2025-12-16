#!/usr/bin/env python3
"""
Protect .git/ directory from any modifications.
Prevents git repository corruption.
"""
import sys
import json

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
path = tool_input.get("file_path", "")

# Block any operations on .git/
if "/.git/" in path or path.startswith(".git/"):
    print(f"❌ BLOCKED: Cannot modify .git/ directory", file=sys.stderr)
    print(f"   Attempted path: {path}", file=sys.stderr)
    print(f"", file=sys.stderr)
    print(f"   Use git commands via Bash tool instead of direct file operations.", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
