#!/bin/bash
#
# VerzekAutoTrader - Auto-Deploy Setup for Private GitHub Repo
# This script sets up automated deployment with GitHub token authentication
#

set -euo pipefail

echo "=== VerzekAutoTrader Auto-Deploy Setup ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: Please run as root"
    exit 1
fi

# Configuration
GITHUB_REPO="https://github.com/ellizza78/VerzekBackend.git"
INSTALL_DIR="/root/VerzekBackend"
BACKEND_DIR="$INSTALL_DIR/backend"

echo "📋 Step 1: Checking for existing installation..."
if [ -d "$INSTALL_DIR" ]; then
    echo "   Found existing installation at $INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Try to pull latest changes
    echo "   Pulling latest changes..."
    if git pull origin main 2>/dev/null; then
        echo "   ✅ Updated existing installation"
    else
        echo "   ⚠️  Pull failed, will re-clone"
        cd /root
        rm -rf "$INSTALL_DIR"
        
        # Clone with public access (repo should be public)
        echo "   Cloning repository..."
        if ! git clone "$GITHUB_REPO" "$INSTALL_DIR"; then
            echo ""
            echo "❌ ERROR: Cannot clone repository"
            echo ""
            echo "The repository appears to be private. Please either:"
            echo "1. Make the repository public at: https://github.com/ellizza78/VerzekBackend/settings"
            echo "   Go to Settings > Danger Zone > Change visibility > Make public"
            echo ""
            echo "OR"
            echo ""
            echo "2. Setup a GitHub Personal Access Token (classic) with 'repo' scope"
            echo "   and clone manually with: git clone https://TOKEN@github.com/ellizza78/VerzekBackend.git"
            echo ""
            exit 1
        fi
    fi
else
    echo "   No existing installation found"
    echo "   Cloning repository..."
    
    # Clone repository
    if ! git clone "$GITHUB_REPO" "$INSTALL_DIR"; then
        echo ""
        echo "❌ ERROR: Cannot clone repository"
        echo ""
        echo "The repository appears to be private. Please either:"
        echo "1. Make the repository public at: https://github.com/ellizza78/VerzekBackend/settings"
        echo "   Go to Settings > Danger Zone > Change visibility > Make public"
        echo ""
        echo "OR"
        echo ""
        echo "2. Run this command with a GitHub token:"
        echo "   git clone https://YOUR_TOKEN@github.com/ellizza78/VerzekBackend.git /root/VerzekBackend"
        echo ""
        exit 1
    fi
    
    echo "   ✅ Repository cloned successfully"
fi

echo ""
echo "📋 Step 2: Installing auto-deploy scripts..."

cd "$BACKEND_DIR"

# Make deploy script executable
chmod +x scripts/auto_pull_deploy.sh
echo "   ✅ Deploy script ready"

# Install systemd service
cp scripts/verzek-autodeploy.service /etc/systemd/system/
echo "   ✅ Service unit installed"

# Install systemd timer
cp scripts/verzek-autodeploy.timer /etc/systemd/system/
echo "   ✅ Timer unit installed"

# Reload systemd
systemctl daemon-reload
echo "   ✅ Systemd reloaded"

echo ""
echo "📋 Step 3: Enabling auto-deploy timer..."

systemctl enable verzek-autodeploy.timer
systemctl start verzek-autodeploy.timer
echo "   ✅ Auto-deploy timer enabled and started"

echo ""
echo "📋 Step 4: Triggering first deployment..."

systemctl start verzek-autodeploy.service
sleep 8

echo ""
echo "📊 Deployment Results:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -20 /var/log/verzek_auto_deploy.log 2>/dev/null || echo "No deployment logs yet"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "📊 Service Status:"
if systemctl is-active --quiet verzek_api; then
    echo "   ✅ verzek_api is ACTIVE and RUNNING"
else
    echo "   ⚠️  verzek_api is NOT running"
    echo "   Check logs: journalctl -u verzek_api -n 50"
fi

echo ""
echo "📊 Auto-Deploy Timer Status:"
systemctl status verzek-autodeploy.timer --no-pager | head -5

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ AUTO-DEPLOY SYSTEM INSTALLED SUCCESSFULLY!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 Next Steps:"
echo "   1. Push changes to GitHub from Replit"
echo "   2. Server auto-deploys within 2 minutes"
echo "   3. Monitor: tail -f /var/log/verzek_auto_deploy.log"
echo ""
echo "🔄 Auto-deploy checks every 2 minutes for new commits"
echo ""
