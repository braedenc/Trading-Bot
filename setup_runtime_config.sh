#!/bin/bash
echo "🔧 Setting up Runtime Configuration API feature branch..."
git checkout main && git pull origin main
git checkout -b feature/runtime-config-api
echo "✅ Ready to implement Runtime Configuration API!"
echo "📁 Working directory: config/api/"
