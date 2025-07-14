# Development Workflow for Persistent Version Control

## 🎯 Purpose
This guide ensures all work done in Cursor chat sessions persists properly in the repository and is available for future sessions.

## 📋 Pre-Chat Session Checklist

### 1. Start Each Chat Session
```bash
# Check current repository status
git status
git branch
git log --oneline -5

# Always start from main branch
git checkout main
git pull origin main

# Create a new feature branch for your work
git checkout -b feature/[feature-name]
# Examples:
# git checkout -b feature/runtime-config-api
# git checkout -b feature/vm-deployment
# git checkout -b feature/alerting-system
# git checkout -b feature/ci-cd-pipeline
```

### 2. During Development
```bash
# Commit frequently (every major milestone)
git add .
git commit -m "descriptive commit message"

# Push regularly to backup work
git push origin feature/[feature-name]
```

### 3. End Each Chat Session
```bash
# Final commit of all changes
git add .
git commit -m "Complete: [feature description]"

# Push to remote to persist work
git push origin feature/[feature-name]

# Create a summary file for next session
echo "## Session Summary
- Feature: [feature-name]
- Branch: feature/[feature-name]
- Status: [Complete/In Progress]
- Next Steps: [what to do next]
- Files Modified: $(git diff --name-only main..HEAD)
" > SESSION_SUMMARY_$(date +%Y%m%d_%H%M).md

git add SESSION_SUMMARY_*.md
git commit -m "Add session summary"
git push origin feature/[feature-name]
```

## 🔄 Between Sessions Recovery

### Starting a New Chat for Existing Work
```bash
# Check what branches exist
git branch -r

# Switch to your feature branch
git checkout feature/[feature-name]
git pull origin feature/[feature-name]

# Review what was done
cat SESSION_SUMMARY_*.md
git log --oneline main..HEAD
git diff main..HEAD --name-only
```

## 📊 Feature Branch Strategy

### Branch Naming Convention
- `feature/runtime-config-api` - Runtime Configuration API
- `feature/vm-deployment` - Virtual Machine and Services Deployment  
- `feature/alerting-system` - Alerting and Notification System
- `feature/ci-cd-pipeline` - GitHub Actions CI/CD Pipeline
- `feature/[other-features]` - Any other features

### Merge Strategy
```bash
# When feature is complete
git checkout main
git pull origin main
git merge feature/[feature-name]
git push origin main

# Clean up feature branch (optional)
git branch -d feature/[feature-name]
git push origin --delete feature/[feature-name]
```

## 🎯 Chat Session Templates

### Template 1: Starting New Feature
```
Hi! I'm working on implementing [FEATURE NAME] for the braedenc/Trading-Bot repository.

Current setup:
- Repository: braedenc/Trading-Bot  
- Feature branch: feature/[feature-name]
- Goal: [specific implementation goal]

Please help me:
1. Set up the feature branch if needed
2. Implement [specific functionality]
3. Ensure all changes are committed and pushed

At the end, please create a session summary and push everything to the remote repository.
```

### Template 2: Continuing Existing Work
```
Hi! I'm continuing work on [FEATURE NAME] in the braedenc/Trading-Bot repository.

Setup needed:
- Switch to branch: feature/[feature-name]
- Review existing work and session summaries
- Continue from where I left off

Goal for this session: [specific goals]

Please check the latest session summary and continue the implementation.
```

## 📁 File Organization

### Expected Directory Structure After All Features
```
├── .github/
│   └── workflows/           # CI/CD Pipeline
├── config/
│   ├── api/                # Runtime Configuration API
│   ├── environments/       # Environment configs
│   └── settings.py         # Configuration management
├── deployment/
│   ├── vm/                 # VM deployment scripts
│   ├── docker/             # Container configs
│   └── terraform/          # Infrastructure as code
├── monitoring/
│   ├── alerts/             # Alerting system
│   ├── notifications/      # Notification handlers
│   └── dashboards/         # Monitoring dashboards
├── trading_bot/           # Existing trading bot code
└── docs/                  # Documentation
```

## 🔍 Session Recovery Commands

### Quick Status Check
```bash
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
```

## ⚠️ Important Notes

### Do This Every Session:
1. ✅ Start with git status check
2. ✅ Create/switch to appropriate feature branch  
3. ✅ Commit frequently during development
4. ✅ Push to remote before ending session
5. ✅ Create session summary

### Never Do This:
1. ❌ Work directly on main branch
2. ❌ End session without committing
3. ❌ Forget to push to remote
4. ❌ Mix multiple features in one branch

### Recovery if Work is Lost:
1. Check all remote branches: `git branch -r`
2. Look for session summaries: `find . -name "SESSION_SUMMARY_*"`
3. Check git reflog: `git reflog --oneline -20`
4. Check stash: `git stash list`

## 🎯 Next Session Plan

For your next 4 chat sessions, use these specific commands:

### Session 1: Runtime Configuration API
```bash
git checkout main && git pull origin main
git checkout -b feature/runtime-config-api
```

### Session 2: VM Deployment
```bash
git checkout main && git pull origin main  
git checkout -b feature/vm-deployment
```

### Session 3: Alerting System
```bash
git checkout main && git pull origin main
git checkout -b feature/alerting-system
```

### Session 4: CI/CD Pipeline
```bash
git checkout main && git pull origin main
git checkout -b feature/ci-cd-pipeline
```

## 📞 Emergency Recovery
If you start a session and your previous work is missing:
1. Immediately run the "Quick Status Check" commands above
2. Check all remote branches for your feature branches
3. Look for any session summary files
4. Contact me with the output of these commands for recovery assistance