#!/bin/bash
# One-Command Vultr Deployment and Verification
# This script copies everything to Vultr and runs complete verification

set -e

VULTR_IP="80.240.29.142"
VULTR_USER="root"

echo "=========================================="
echo "VERZEK AUTOTRADER - DEPLOY & VERIFY"
echo "=========================================="
echo "Target: $VULTR_USER@$VULTR_IP"
echo "Date: $(date)"
echo ""

# Check if SSH key is set up
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 $VULTR_USER@$VULTR_IP exit 2>/dev/null; then
    echo "⚠️  SSH key authentication not set up"
    echo "Please run: ssh-copy-id $VULTR_USER@$VULTR_IP"
    exit 1
fi

echo "✅ SSH connection verified"
echo ""

# Step 1: Copy verification script to Vultr
echo "📤 Uploading verification script to Vultr..."
scp vultr_verification_script.sh $VULTR_USER@$VULTR_IP:/root/verify_system.sh
ssh $VULTR_USER@$VULTR_IP "chmod +x /root/verify_system.sh"
echo "✅ Verification script uploaded"
echo ""

# Step 2: Run verification on Vultr
echo "=========================================="
echo "RUNNING VERIFICATION ON VULTR"
echo "=========================================="
ssh $VULTR_USER@$VULTR_IP "/root/verify_system.sh"

VERIFY_EXIT=$?

echo ""
echo "=========================================="
if [ $VERIFY_EXIT -eq 0 ]; then
    echo "✅ DEPLOYMENT SUCCESSFUL"
    echo "All systems operational on Vultr!"
else
    echo "⚠️  ISSUES DETECTED"
    echo "Please review the verification output above."
fi
echo "=========================================="

exit $VERIFY_EXIT
