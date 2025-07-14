#!/bin/bash
echo "🚨 Setting up Alerting System feature branch..."
git checkout main && git pull origin main
git checkout -b feature/alerting-system
echo "✅ Ready to implement Alerting System!"
echo "📁 Working directory: monitoring/"
