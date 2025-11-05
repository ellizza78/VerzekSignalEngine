#!/bin/bash
echo "🚀 Syncing latest changes to GitHub..."
git add .
git commit -m "Auto sync from Replit"
git push
echo "✅ Code successfully pushed to GitHub!"