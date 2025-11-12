#!/bin/bash
# Update RESEND_API_KEY on Vultr VPS
# This script adds the RESEND API key to the environment file

echo "🔧 Updating RESEND_API_KEY on Vultr VPS..."

# Check if RESEND_API_KEY is already in the file
ssh root@80.240.29.142 << 'EOF'
if grep -q "RESEND_API_KEY" /root/api_server_env.sh; then
    echo "✅ RESEND_API_KEY already exists in environment file"
    echo "Current value (first 10 chars): $(grep RESEND_API_KEY /root/api_server_env.sh | cut -d'=' -f2 | cut -c1-10)..."
else
    echo "❌ RESEND_API_KEY not found in environment file"
    echo "Please add it manually:"
    echo "ssh root@80.240.29.142"
    echo "echo 'RESEND_API_KEY=YOUR_KEY_HERE' >> /root/api_server_env.sh"
    echo "systemctl restart verzek-api.service"
fi
EOF

echo "Done!"
