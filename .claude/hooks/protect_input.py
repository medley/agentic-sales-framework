#!/usr/bin/env python3
"""
Protect sample-data/input/ from modifications (immutable source files).
Exit code 2 blocks the operation and provides feedback.
"""
import sys
import json

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
path = tool_input.get("file_path", "")

# Block any Write or Edit operations in sample-data/input/
if "sample-data/input" in path:
    print(f"❌ BLOCKED: sample-data/input/ is immutable (source files)", file=sys.stderr)
    print(f"   Attempted path: {path}", file=sys.stderr)
    print(f"", file=sys.stderr)
    print(f"   Input files should never be modified after drop.", file=sys.stderr)
    print(f"   Use convert_and_file skill to process into Runtime/_Shared/knowledge/", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
