#!/bin/bash
#
# VerzekSignalEngine - Master Fusion Engine Quick Deploy
# Deploy updated engine with fusion capabilities to Vultr
#

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  🚀 VerzekSignalEngine v2.0 - Fusion Engine Deployment"
echo "═══════════════════════════════════════════════════════════"

# Step 1: SSH Key Check
echo ""
echo "📍 Step 1: Checking SSH Configuration..."
if [ -f ~/.ssh/agent_key ]; then
    echo "✅ SSH key exists: ~/.ssh/agent_key"
    echo "📋 Public key (add to Vultr if not already done):"
    cat ~/.ssh/agent_key.pub
else
    echo "❌ SSH key not found. Creating..."
    ssh-keygen -t ed25519 -f ~/.ssh/agent_key -N "" -C "replit-agent@vultr"
    echo "✅ SSH key created"
    echo "📋 Add this public key to Vultr /root/.ssh/authorized_keys:"
    cat ~/.ssh/agent_key.pub
fi

# Step 2: Git Status
echo ""
echo "📍 Step 2: Checking Git Status..."
cd "$(dirname "$0")"
git status --short

# Step 3: Commit Changes
echo ""
echo "📍 Step 3: Committing Fusion Engine Upgrades..."
git add -A
git commit -m "Implement Master Fusion Engine v2.0 with Balanced Mode

- Added core models (SignalCandidate, SignalOutcome)
- Implemented FusionEngineBalanced with intelligent filtering
- Updated all 4 bots to return SignalCandidate objects
- Added cooldown rules, trend bias, rate limiting
- Prepared for signal tracking and daily reporting

Status: Phases 1-4 complete, integration pending" || echo "No changes to commit"

# Step 4: Push to GitHub
echo ""
echo "📍 Step 4: Pushing to GitHub..."
git push origin main

# Step 5: Deploy to Vultr (if SSH is configured)
echo ""
echo "📍 Step 5: Deploying to Vultr (80.240.29.142)..."

# Test SSH connection
if ssh -i ~/.ssh/agent_key -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@80.240.29.142 "echo OK" 2>/dev/null; then
    echo "✅ SSH connection successful"
    
    # Pull latest code
    echo "📥 Pulling latest code on Vultr..."
    ssh -i ~/.ssh/agent_key root@80.240.29.142 << 'ENDSSH'
        cd /root/VerzekSignalEngine
        git pull origin main
        
        # Check for Python dependencies
        pip3 install -q -r requirements.txt 2>/dev/null || true
        
        # Restart service
        systemctl restart verzek-signalengine
        sleep 3
        systemctl status verzek-signalengine --no-pager
ENDSSH
    
    echo "✅ Deployment complete"
    
else
    echo "⚠️  SSH connection failed"
    echo "📋 Manual Steps Required:"
    echo ""
    echo "1. Add SSH public key to Vultr:"
    echo "   ssh root@80.240.29.142"
    echo "   cat >> ~/.ssh/authorized_keys << 'EOF'"
    cat ~/.ssh/agent_key.pub 2>/dev/null || echo "[SSH key not found]"
    echo "EOF"
    echo "   chmod 600 ~/.ssh/authorized_keys"
    echo ""
    echo "2. Manual deploy:"
    echo "   cd /root/VerzekSignalEngine"
    echo "   git pull origin main"
    echo "   systemctl restart verzek-signalengine"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Deployment Process Complete"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📊 Next Steps:"
echo "   1. Complete remaining integration phases (see FUSION_ENGINE_UPGRADE_PROGRESS.md)"
echo "   2. Wire fusion engine into scheduler.py"
echo "   3. Update dispatcher to handle SignalCandidate list"
echo "   4. Add master_engine config to engine_settings.json"
echo "   5. Implement signal tracking (tracker.py)"
echo "   6. Implement daily reporter (daily_reporter.py)"
echo ""
echo "📖 Documentation: signal_engine/FUSION_ENGINE_UPGRADE_PROGRESS.md"
echo "📊 Monitor logs: journalctl -u verzek-signalengine -f"
echo ""
