#!/bin/bash

# Validate Skill Output Format
# Usage: ./scripts/validate-skill-output.sh <file.md>
# Returns 0 if valid, 1 if invalid

set -e

FILE="$1"

if [ -z "$FILE" ]; then
    echo "Usage: $0 <file.md>"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "Error: File not found: $FILE"
    exit 1
fi

echo "Validating skill output format: $FILE"
echo "================================================"

# Track validation status
VALID=0

# Check 1: File contains "# Chat Output" heading
echo -n "[1/7] Checking for '# Chat Output' section... "
if grep -q "^# Chat Output" "$FILE"; then
    echo "PASS"
else
    echo "FAIL - Missing '# Chat Output' heading"
    VALID=1
fi

# Check 2: File contains "# Artifact Output" heading
echo -n "[2/7] Checking for '# Artifact Output' section... "
if grep -q "^# Artifact Output" "$FILE"; then
    echo "PASS"
else
    echo "FAIL - Missing '# Artifact Output' heading"
    VALID=1
fi

# Check 3: File contains "```json summary" code fence
echo -n "[3/7] Checking for '```json summary' block... "
if grep -q '```json summary' "$FILE"; then
    echo "PASS"
else
    echo "FAIL - Missing '```json summary' code fence"
    VALID=1
fi

# Check 4: Extract and validate JSON
echo -n "[4/7] Validating JSON syntax... "
JSON=$(sed -n '/```json summary/,/```/p' "$FILE" | sed '1d;$d')
if [ -z "$JSON" ]; then
    echo "FAIL - Empty JSON block"
    VALID=1
else
    if echo "$JSON" | python3 -m json.tool > /dev/null 2>&1; then
        echo "PASS"
    else
        echo "FAIL - Invalid JSON syntax"
        VALID=1
    fi
fi

# Check 5: Verify sections are in correct order
echo -n "[5/7] Checking section order... "
CHAT_LINE=$(grep -n "^# Chat Output" "$FILE" | cut -d: -f1 | head -1)
ARTIFACT_LINE=$(grep -n "^# Artifact Output" "$FILE" | cut -d: -f1 | head -1)
JSON_LINE=$(grep -n '```json summary' "$FILE" | cut -d: -f1 | head -1)

if [ "$CHAT_LINE" -lt "$ARTIFACT_LINE" ] && [ "$ARTIFACT_LINE" -lt "$JSON_LINE" ]; then
    echo "PASS"
else
    echo "FAIL - Sections not in correct order"
    VALID=1
fi

# Check 6: Verify no content after JSON closing fence
echo -n "[6/7] Checking nothing after JSON closing fence... "
LAST_LINE=$(tail -1 "$FILE" | tr -d '[:space:]')
if [ "$LAST_LINE" = '```' ]; then
    echo "PASS"
else
    echo "FAIL - Content found after JSON closing fence"
    VALID=1
fi

# Check 7: Count code fences
echo -n "[7/7] Checking code fence count... "
FENCE_COUNT=$(grep -c '```' "$FILE" || true)
if [ "$FENCE_COUNT" -eq 6 ]; then
    echo "PASS"
else
    echo "WARNING - Expected 6 code fences, found $FENCE_COUNT"
fi

echo "================================================"

if [ $VALID -eq 0 ]; then
    echo "VALIDATION PASSED: $FILE"
    exit 0
else
    echo "VALIDATION FAILED: $FILE"
    exit 1
fi
