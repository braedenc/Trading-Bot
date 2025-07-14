#!/bin/bash
echo "⚙️ Setting up CI/CD Pipeline feature branch..."
git checkout main && git pull origin main
git checkout -b feature/ci-cd-pipeline
echo "✅ Ready to implement CI/CD Pipeline!"
echo "📁 Working directory: .github/workflows/"
