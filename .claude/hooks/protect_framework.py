#!/usr/bin/env python3
import sys, json

data = json.load(sys.stdin)
input = data.get("tool_input", {})
path = input.get("file_path") or ""

# Allow Framework/System/ (documentation) updates
if "Framework/System/" in path:
    sys.exit(0)

# Allow Framework/Plays/ (reusable sales patterns) updates
if "Framework/Plays/" in path:
    sys.exit(0)

# Block other Framework/ modifications
if path.startswith("Framework/") or "/Framework/" in path:
    print(f"❌ BLOCKED: Cannot modify Framework directory (read-only)", file=sys.stderr)
    print(f"   Attempted path: {path}", file=sys.stderr)
    print(f"   Framework is read-only except for System/ and Plays/. Use sample-data/Runtime/ for generated content.", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
