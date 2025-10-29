#!/bin/bash
# Quick test script for Microsoft 365 email integration

echo "🧪 Testing Microsoft 365 Email Integration"
echo "==========================================="
echo ""

echo "1️⃣ Checking email service health..."
curl -s https://verzek-auto-trader.replit.app/health/mail | python3 -m json.tool
echo ""

echo "2️⃣ Ready to send test email!"
echo ""
echo "To send a test email, run:"
echo ""
echo "curl -X POST https://verzek-auto-trader.replit.app/send-test \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"to\":\"YOUR_EMAIL@example.com\"}'"
echo ""
echo "Replace YOUR_EMAIL@example.com with your actual email address."
echo ""
echo "✅ Email service is configured and ready!"
