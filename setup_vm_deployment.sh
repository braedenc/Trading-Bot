#!/bin/bash
echo "🚀 Setting up VM Deployment feature branch..."
git checkout main && git pull origin main
git checkout -b feature/vm-deployment
echo "✅ Ready to implement VM Deployment!"
echo "📁 Working directory: deployment/"
