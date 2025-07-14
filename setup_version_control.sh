#!/bin/bash

# Setup Version Control for Trading Bot Development
# This script prepares the repository for proper version control across chat sessions

echo "🔧 Setting up proper version control for Trading Bot development..."

# Ensure we're on main branch and up to date
echo "📍 Ensuring we're on main branch..."
git checkout main
git pull origin main

# Create .gitignore entries for session files if not already present
echo "📋 Setting up .gitignore for session management..."
if ! grep -q "SESSION_SUMMARY_" .gitignore; then
    echo "" >> .gitignore
    echo "# Session management files" >> .gitignore
    echo "SESSION_SUMMARY_*.md" >> .gitignore
    echo "*.log" >> .gitignore
    echo "*.tmp" >> .gitignore
    echo "__pycache__/" >> .gitignore
    echo "*.pyc" >> .gitignore
fi

# Create directories for future implementations
echo "📁 Creating directory structure for planned features..."
mkdir -p config/{api,environments}
mkdir -p deployment/{vm,docker,terraform}
mkdir -p monitoring/{alerts,notifications,dashboards}
mkdir -p .github/workflows

# Create placeholder files to ensure directories are tracked
echo "# Runtime Configuration API" > config/api/README.md
echo "# VM Deployment Scripts" > deployment/vm/README.md
echo "# Alerting System" > monitoring/alerts/README.md
echo "# GitHub Actions CI/CD" > .github/workflows/README.md

# Create a quick status script
cat > check_status.sh << 'EOF'
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
EOF

chmod +x check_status.sh

# Create feature setup scripts
echo "📜 Creating feature setup scripts..."

# Runtime Config API setup
cat > setup_runtime_config.sh << 'EOF'
#!/bin/bash
echo "🔧 Setting up Runtime Configuration API feature branch..."
git checkout main && git pull origin main
git checkout -b feature/runtime-config-api
echo "✅ Ready to implement Runtime Configuration API!"
echo "📁 Working directory: config/api/"
EOF

# VM Deployment setup
cat > setup_vm_deployment.sh << 'EOF'
#!/bin/bash
echo "🚀 Setting up VM Deployment feature branch..."
git checkout main && git pull origin main
git checkout -b feature/vm-deployment
echo "✅ Ready to implement VM Deployment!"
echo "📁 Working directory: deployment/"
EOF

# Alerting System setup
cat > setup_alerting_system.sh << 'EOF'
#!/bin/bash
echo "🚨 Setting up Alerting System feature branch..."
git checkout main && git pull origin main
git checkout -b feature/alerting-system
echo "✅ Ready to implement Alerting System!"
echo "📁 Working directory: monitoring/"
EOF

# CI/CD Pipeline setup
cat > setup_ci_cd_pipeline.sh << 'EOF'
#!/bin/bash
echo "⚙️ Setting up CI/CD Pipeline feature branch..."
git checkout main && git pull origin main
git checkout -b feature/ci-cd-pipeline
echo "✅ Ready to implement CI/CD Pipeline!"
echo "📁 Working directory: .github/workflows/"
EOF

chmod +x setup_*.sh

echo "🎯 Creating chat session templates..."

# Create templates directory
mkdir -p templates

# Template for Runtime Config API
cat > templates/runtime_config_api_prompt.md << 'EOF'
# Runtime Configuration API Implementation

## Chat Session Prompt Template

```
Hi! I'm working on implementing a Runtime Configuration API for the braedenc/Trading-Bot repository.

Current setup:
- Repository: braedenc/Trading-Bot  
- Feature branch: feature/runtime-config-api
- Goal: Create a runtime configuration API that allows dynamic configuration changes

Please help me:
1. Set up the feature branch: `git checkout -b feature/runtime-config-api`
2. Implement a comprehensive runtime configuration API with:
   - RESTful API endpoints for configuration management
   - Configuration validation and schema
   - Environment-specific configurations
   - Hot-reload capabilities for trading parameters
   - Configuration versioning and rollback
   - Secure configuration management
3. Create proper tests and documentation
4. Ensure all changes are committed and pushed

Key directories to work in:
- config/api/ - API implementation
- config/environments/ - Environment configs
- tests/ - Test files

At the end, please create a session summary and push everything to the remote repository.
```

## Expected Deliverables
- REST API for configuration management
- Configuration schema validation
- Environment-specific settings
- Hot-reload functionality
- Security implementation
- Comprehensive tests
- Documentation
EOF

# Template for VM Deployment
cat > templates/vm_deployment_prompt.md << 'EOF'
# VM Deployment and Services Implementation

## Chat Session Prompt Template

```
Hi! I'm working on implementing VM Deployment and Services for the braedenc/Trading-Bot repository.

Current setup:
- Repository: braedenc/Trading-Bot  
- Feature branch: feature/vm-deployment
- Goal: Create automated VM deployment and service management

Please help me:
1. Set up the feature branch: `git checkout -b feature/vm-deployment`
2. Implement comprehensive deployment infrastructure:
   - VM provisioning scripts (Terraform/Ansible)
   - Docker containerization for services
   - Service orchestration and management
   - Auto-scaling capabilities
   - Infrastructure monitoring
   - Backup and disaster recovery
3. Create deployment documentation and runbooks
4. Ensure all changes are committed and pushed

Key directories to work in:
- deployment/vm/ - VM scripts
- deployment/docker/ - Container configs
- deployment/terraform/ - Infrastructure as code

At the end, please create a session summary and push everything to the remote repository.
```

## Expected Deliverables
- VM provisioning automation
- Containerized services
- Infrastructure as code
- Deployment automation
- Monitoring setup
- Documentation and runbooks
EOF

# Template for Alerting System
cat > templates/alerting_system_prompt.md << 'EOF'
# Alerting and Notification System Implementation

## Chat Session Prompt Template

```
Hi! I'm working on implementing an Alerting and Notification System for the braedenc/Trading-Bot repository.

Current setup:
- Repository: braedenc/Trading-Bot  
- Feature branch: feature/alerting-system
- Goal: Create comprehensive alerting and notification capabilities

Please help me:
1. Set up the feature branch: `git checkout -b feature/alerting-system`
2. Implement a robust alerting system with:
   - Real-time monitoring and alerting
   - Multiple notification channels (email, SMS, Slack, Discord)
   - Alert severity levels and escalation
   - Custom alert rules and thresholds
   - Alert acknowledgment and resolution tracking
   - Dashboard for alert management
3. Create alert templates and notification workflows
4. Ensure all changes are committed and pushed

Key directories to work in:
- monitoring/alerts/ - Alert system
- monitoring/notifications/ - Notification handlers
- monitoring/dashboards/ - Alert dashboards

At the end, please create a session summary and push everything to the remote repository.
```

## Expected Deliverables
- Real-time monitoring system
- Multi-channel notifications
- Alert management interface
- Escalation workflows
- Alert analytics
- Comprehensive documentation
EOF

# Template for CI/CD Pipeline
cat > templates/ci_cd_pipeline_prompt.md << 'EOF'
# CI/CD Pipeline with GitHub Actions Implementation

## Chat Session Prompt Template

```
Hi! I'm working on implementing a CI/CD Pipeline with GitHub Actions for the braedenc/Trading-Bot repository.

Current setup:
- Repository: braedenc/Trading-Bot  
- Feature branch: feature/ci-cd-pipeline
- Goal: Create automated CI/CD pipeline for continuous integration and deployment

Please help me:
1. Set up the feature branch: `git checkout -b feature/ci-cd-pipeline`
2. Implement comprehensive CI/CD pipeline with:
   - Automated testing workflows
   - Code quality checks and linting
   - Security scanning
   - Automated deployment to staging/production
   - Environment promotion workflows
   - Rollback capabilities
   - Performance testing integration
3. Create deployment strategies and workflows
4. Ensure all changes are committed and pushed

Key directories to work in:
- .github/workflows/ - GitHub Actions workflows
- deployment/ - Deployment configurations
- tests/ - Test automation

At the end, please create a session summary and push everything to the remote repository.
```

## Expected Deliverables
- GitHub Actions workflows
- Automated testing pipeline
- Security and quality gates
- Deployment automation
- Environment management
- Monitoring integration
- Documentation
EOF

echo "📚 Updating main documentation..."

# Add section to README
if ! grep -q "Development Workflow" README.md; then
    echo "" >> README.md
    echo "## Development Workflow" >> README.md
    echo "See [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) for proper version control practices." >> README.md
    echo "" >> README.md
    echo "### Quick Setup Scripts" >> README.md
    echo "- \`./check_status.sh\` - Check repository status" >> README.md
    echo "- \`./setup_runtime_config.sh\` - Setup Runtime Config API branch" >> README.md
    echo "- \`./setup_vm_deployment.sh\` - Setup VM Deployment branch" >> README.md
    echo "- \`./setup_alerting_system.sh\` - Setup Alerting System branch" >> README.md
    echo "- \`./setup_ci_cd_pipeline.sh\` - Setup CI/CD Pipeline branch" >> README.md
fi

echo "✅ Version control setup complete!"
echo ""
echo "🎯 Next Steps:"
echo "1. Review DEVELOPMENT_WORKFLOW.md for detailed instructions"
echo "2. Use the setup scripts to create feature branches:"
echo "   - ./setup_runtime_config.sh"
echo "   - ./setup_vm_deployment.sh" 
echo "   - ./setup_alerting_system.sh"
echo "   - ./setup_ci_cd_pipeline.sh"
echo "3. Use the templates in templates/ folder for your chat prompts"
echo "4. Always run ./check_status.sh to verify repository state"
echo ""
echo "📋 Ready for development with proper version control!"