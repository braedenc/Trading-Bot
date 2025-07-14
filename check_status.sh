#!/bin/bash
echo "=== REPOSITORY STATUS ==="
git status
echo ""
echo "=== CURRENT BRANCH ==="
git branch --show-current
echo ""
echo "=== RECENT COMMITS ==="
git log --oneline -5
echo ""
echo "=== REMOTE BRANCHES ==="
git branch -r
echo ""
echo "=== SESSION SUMMARIES ==="
ls -la SESSION_SUMMARY_*.md 2>/dev/null || echo "No session summaries found"
echo ""
echo "=== UNCOMMITTED CHANGES ==="
git diff --name-only
echo ""
echo "=== UNTRACKED FILES ==="
git ls-files --others --exclude-standard
