#!/bin/bash
# verify_paths.sh - Verify documentation uses correct filesystem paths

echo "========================================"
echo "Path Verification Script"
echo "========================================"
echo ""

ERRORS=0

# Check for incorrect Input/ (should be input/)
echo "Checking for 'sample-data/Input/' (should be 'sample-data/input/')..."
if grep -r "sample-data/Input" --include="*.md" . 2>/dev/null | grep -v ".backup" | grep -v "verify_paths"; then
    echo "❌ Found incorrect 'Input/' references (should be lowercase 'input/')"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ No incorrect 'Input/' references found"
fi
echo ""

# Check for incorrect Knowledge/ (should be knowledge/)
echo "Checking for '_Shared/Knowledge/' (should be '_Shared/knowledge/')..."
if grep -r "_Shared/Knowledge" --include="*.md" . 2>/dev/null | grep -v ".backup" | grep -v "verify_paths"; then
    echo "❌ Found incorrect 'Knowledge/' references (should be lowercase 'knowledge/')"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ No incorrect 'Knowledge/' references found"
fi
echo ""

# Check for broken sandler_adapter.yaml references (should be sandler.md)
echo "Checking for 'sandler_adapter.yaml' (should be 'sandler.md')..."
if grep -r "sandler_adapter.yaml" --include="*.md" . 2>/dev/null | grep -v ".backup" | grep -v "verify_paths"; then
    echo "❌ Found incorrect 'sandler_adapter.yaml' references (should be 'sandler.md')"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ No incorrect 'sandler_adapter.yaml' references found"
fi
echo ""

# Summary
echo "========================================"
if [ $ERRORS -eq 0 ]; then
    echo "✅ All path checks passed!"
    exit 0
else
    echo "❌ Found $ERRORS path issues"
    exit 1
fi
