#!/bin/bash
# Fix Email Verification on Vultr VPS
# This script fixes systemd environment loading for RESEND_API_KEY

echo "🔧 Fixing Email Verification on VPS..."
echo ""

# Step 1: Fix environment file format (remove "export" keywords)
echo "📝 Step 1: Removing 'export' keywords from environment file..."
sed -i 's/^export //g' /root/api_server_env.sh
echo "✅ Environment file format updated"
echo ""

# Step 2: Backup current systemd service
echo "💾 Step 2: Backing up systemd service..."
cp /etc/systemd/system/verzek-api.service /etc/systemd/system/verzek-api.service.backup
echo "✅ Backup created: verzek-api.service.backup"
echo ""

# Step 3: Update systemd service to load environment file
echo "⚙️  Step 3: Updating systemd service configuration..."
cat > /etc/systemd/system/verzek-api.service << 'EOF'
[Unit]
Description=Verzek Auto Trader API Server
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=root
WorkingDirectory=/root/VerzekBackend/backend
EnvironmentFile=/root/api_server_env.sh
ExecStart=/usr/local/bin/gunicorn \
    --bind 0.0.0.0:8050 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /root/api_server/logs/access.log \
    --error-logfile /root/api_server/logs/error.log \
    --log-level info \
    api_server:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
echo "✅ Service file updated with EnvironmentFile directive"
echo ""

# Step 4: Reload systemd
echo "🔄 Step 4: Reloading systemd daemon..."
systemctl daemon-reload
echo "✅ Systemd reloaded"
echo ""

# Step 5: Restart service
echo "🚀 Step 5: Restarting verzek-api service..."
systemctl restart verzek-api.service
sleep 3
echo ""

# Step 6: Check service status
echo "📊 Step 6: Checking service status..."
if systemctl is-active --quiet verzek-api.service; then
    echo "✅ Service is ACTIVE and RUNNING"
else
    echo "❌ Service failed to start. Checking logs..."
    journalctl -u verzek-api.service -n 20 --no-pager
    exit 1
fi
echo ""

# Step 7: Verify environment variables are loaded
echo "🔍 Step 7: Verifying RESEND_API_KEY is loaded..."
if grep -q "RESEND_API_KEY" /root/api_server_env.sh; then
    echo "✅ RESEND_API_KEY found in environment file"
else
    echo "❌ RESEND_API_KEY not found in environment file"
    echo "Please add it manually:"
    echo "echo 'RESEND_API_KEY=re_ACMWmmPe_CHiR7EtPzMwP8Dc9FLy_Lmyu' >> /root/api_server_env.sh"
    exit 1
fi
echo ""

# Step 8: Test API health
echo "🏥 Step 8: Testing API health..."
HEALTH_CHECK=$(curl -s https://api.verzekinnovative.com/api/health)
if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    echo "✅ API is healthy and responding"
else
    echo "⚠️  API health check failed or unexpected response"
    echo "Response: $HEALTH_CHECK"
fi
echo ""

echo "=========================================="
echo "✅ EMAIL VERIFICATION FIX COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Open your APK v1.3.1"
echo "2. Register with a real email address"
echo "3. Check your inbox for verification email"
echo "4. Click the verification link"
echo "5. Login and start trading!"
echo ""
echo "If emails still don't arrive, check logs with:"
echo "  journalctl -u verzek-api.service -f | grep -i email"
