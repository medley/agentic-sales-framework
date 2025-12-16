#!/bin/bash
# Test script to verify hooks are working correctly
# Run this after restarting Claude Code session

set +e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "🧪 Testing Hook Configuration"
echo "================================"
echo ""

# Test 1: Protect Framework hook
echo "Test 1: Protected Framework path"
echo "---------------------------------"
TEST_INPUT='{"tool_name": "Write", "tool_input": {"file_path": "'$PROJECT_ROOT'/Framework/test.md", "content": "test"}}'
echo "$TEST_INPUT" | "$SCRIPT_DIR/protect_framework.py" 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 2 ]; then
    echo "✅ PASS: Framework protection working (exit code: $EXIT_CODE)"
else
    echo "❌ FAIL: Expected exit code 2, got $EXIT_CODE"
fi
echo ""

# Test 2: Protected sample-data/Input path
echo "Test 2: Protected sample-data/Input path"
echo "-----------------------------------------"
TEST_INPUT='{"tool_name": "Write", "tool_input": {"file_path": "'$PROJECT_ROOT'/sample-data/Input/test.md", "content": "test"}}'
echo "$TEST_INPUT" | "$SCRIPT_DIR/protect_framework.py" 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 2 ]; then
    echo "✅ PASS: Input protection working (exit code: $EXIT_CODE)"
else
    echo "❌ FAIL: Expected exit code 2, got $EXIT_CODE"
fi
echo ""

# Test 3: Allowed sample-data/Runtime path
echo "Test 3: Allowed sample-data/Runtime path"
echo "-----------------------------------------"
TEST_INPUT='{"tool_name": "Write", "tool_input": {"file_path": "'$PROJECT_ROOT'/sample-data/Runtime/Sessions/test/notes.md", "content": "test"}}'
echo "$TEST_INPUT" | "$SCRIPT_DIR/protect_framework.py" 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ PASS: Runtime path allowed (exit code: $EXIT_CODE)"
else
    echo "❌ FAIL: Expected exit code 0, got $EXIT_CODE"
fi
echo ""

# Test 4: Frontmatter validation - missing frontmatter
echo "Test 4: Missing frontmatter in Runtime path"
echo "--------------------------------------------"
TEST_INPUT='{"tool_name": "Write", "tool_input": {"file_path": "'$PROJECT_ROOT'/sample-data/Runtime/Sessions/test/notes.md", "content": "# Test\nNo frontmatter here"}}'
echo "$TEST_INPUT" | "$SCRIPT_DIR/validate_frontmatter.py" 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 2 ]; then
    echo "✅ PASS: Missing frontmatter blocked (exit code: $EXIT_CODE)"
else
    echo "❌ FAIL: Expected exit code 2, got $EXIT_CODE"
fi
echo ""

# Test 5: Frontmatter validation - valid frontmatter
echo "Test 5: Valid frontmatter in Runtime path"
echo "------------------------------------------"
TEST_INPUT='{"tool_name": "Write", "tool_input": {"file_path": "'$PROJECT_ROOT'/sample-data/Runtime/Sessions/test/notes.md", "content": "---\ngenerated_by: test\ngenerated_on: 2025-11-12T00:00:00Z\ndeal_id: test_deal\nsources: []\n---\n# Test\nContent here"}}'
echo "$TEST_INPUT" | "$SCRIPT_DIR/validate_frontmatter.py" 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ PASS: Valid frontmatter allowed (exit code: $EXIT_CODE)"
else
    echo "❌ FAIL: Expected exit code 0, got $EXIT_CODE"
fi
echo ""

# Test 6: Frontmatter validation - invalid frontmatter (missing fields)
echo "Test 6: Invalid frontmatter (missing required fields)"
echo "------------------------------------------------------"
TEST_INPUT='{"tool_name": "Write", "tool_input": {"file_path": "'$PROJECT_ROOT'/sample-data/Runtime/Sessions/test/notes.md", "content": "---\ngenerated_by: test\n---\n# Test"}}'
echo "$TEST_INPUT" | "$SCRIPT_DIR/validate_frontmatter.py" 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 2 ]; then
    echo "✅ PASS: Invalid frontmatter blocked (exit code: $EXIT_CODE)"
else
    echo "❌ FAIL: Expected exit code 2, got $EXIT_CODE"
fi
echo ""

echo "================================"
echo "🏁 Hook tests complete!"
echo ""
echo "If all tests pass, hooks are configured correctly."
echo "Now restart Claude Code and try the write operations."
