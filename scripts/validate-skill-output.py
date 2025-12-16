#!/usr/bin/env python3

"""
Validate Skill Output Format
Usage: python3 scripts/validate-skill-output.py <file.md>
Returns 0 if valid, 1 if invalid
"""

import sys
import json
import re

def validate_skill_output(filepath):
    """Validate that a skill output file follows the three-section envelope format."""

    print(f"Validating skill output format: {filepath}")
    print("=" * 60)

    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return 1

    valid = True

    # Check 1: File contains "# Chat Output" heading
    print("[1/7] Checking for '# Chat Output' section... ", end="")
    if re.search(r'^# Chat Output$', content, re.MULTILINE):
        print("PASS")
    else:
        print("FAIL - Missing '# Chat Output' heading")
        valid = False

    # Check 2: File contains "# Artifact Output" heading
    print("[2/7] Checking for '# Artifact Output' section... ", end="")
    if re.search(r'^# Artifact Output$', content, re.MULTILINE):
        print("PASS")
    else:
        print("FAIL - Missing '# Artifact Output' heading")
        valid = False

    # Check 3: File contains "```json summary" code fence
    print("[3/7] Checking for '```json summary' block... ", end="")
    if '```json summary' in content:
        print("PASS")
    else:
        print("FAIL - Missing '```json summary' code fence")
        valid = False

    # Check 4: Extract and validate JSON
    print("[4/7] Validating JSON syntax... ", end="")
    json_match = re.search(r'```json summary\n(.*?)\n```', content, re.DOTALL)
    if json_match:
        json_text = json_match.group(1)
        try:
            json.loads(json_text)
            print("PASS")
        except json.JSONDecodeError as e:
            print(f"FAIL - Invalid JSON syntax: {e}")
            valid = False
    else:
        print("FAIL - Could not extract JSON block")
        valid = False

    # Check 5: Verify sections are in correct order
    print("[5/7] Checking section order... ", end="")
    chat_pos = content.find('# Chat Output')
    artifact_pos = content.find('# Artifact Output')
    json_pos = content.find('```json summary')

    if chat_pos < artifact_pos < json_pos:
        print("PASS")
    else:
        print("FAIL - Sections not in correct order")
        valid = False

    # Check 6: Verify no content after JSON closing fence
    print("[6/7] Checking nothing after JSON closing fence... ", end="")
    last_fence = content.rfind('```')
    after_fence = content[last_fence+3:].strip()
    if not after_fence:
        print("PASS")
    else:
        print("FAIL - Content found after JSON closing fence")
        valid = False

    # Check 7: Count code fences
    print("[7/7] Checking code fence count... ", end="")
    fence_count = content.count('```')
    if fence_count == 6:
        print("PASS")
    else:
        print(f"WARNING - Expected 6 code fences, found {fence_count}")

    print("=" * 60)

    if valid:
        print(f"VALIDATION PASSED: {filepath}")
        return 0
    else:
        print(f"VALIDATION FAILED: {filepath}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 validate-skill-output.py <file.md>")
        sys.exit(1)

    sys.exit(validate_skill_output(sys.argv[1]))
