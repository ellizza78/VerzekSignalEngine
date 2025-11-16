#!/bin/bash
# One-time setup script to enable passwordless SSH from Replit to Vultr

echo "🔐 Setting up SSH Passwordless Access"
echo "======================================"
echo ""

# Check if we already have a key
if [ ! -f ~/.ssh/id_ed25519 ]; then
    echo "1️⃣ Generating new SSH key..."
    ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "replit-to-vultr"
else
    echo "1️⃣ SSH key already exists"
fi

echo ""
echo "2️⃣ Your PUBLIC key (copy this):"
echo "================================"
cat ~/.ssh/id_ed25519.pub
echo "================================"

echo ""
echo "3️⃣ MANUAL STEP: Add this key to your Vultr server"
echo ""
echo "Run this command on your Vultr server (in SSH session):"
echo ""
echo "mkdir -p ~/.ssh && echo \"$(cat ~/.ssh/id_ed25519.pub)\" >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
echo ""

echo "4️⃣ After adding, press ENTER to test connection..."
read

echo ""
echo "5️⃣ Testing SSH connection..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes root@80.240.29.142 'echo "✅ SSH working!"'; then
    echo ""
    echo "✅ SUCCESS! Passwordless SSH is now enabled!"
    echo ""
    echo "You can now use ./deploy_all.sh to deploy anytime"
else
    echo ""
    echo "❌ SSH still requires password. Please verify:"
    echo "  1. You copied the PUBLIC key correctly"
    echo "  2. You added it to ~/.ssh/authorized_keys on the server"
    echo "  3. Permissions are correct (700 for ~/.ssh, 600 for authorized_keys)"
fi

echo ""
