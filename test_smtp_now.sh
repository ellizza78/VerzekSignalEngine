#!/bin/bash
# Quick SMTP AUTH Test Script
# Run this after waiting 30 minutes from enabling SMTP AUTH

echo "📧 Testing Microsoft 365 SMTP Authentication..."
echo ""

# Test email endpoint
echo "🧪 Sending test email..."
RESPONSE=$(curl -s -X POST http://localhost:5000/send-test \
  -H "Content-Type: application/json" \
  -d '{"to":"support@verzekinnovative.com"}')

echo ""
echo "📨 Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Check if successful
if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "✅ SUCCESS! SMTP AUTH is enabled and working!"
    echo ""
    echo "📧 Test email sent to: support@verzekinnovative.com"
    echo "Please check your inbox (and spam folder)"
    echo ""
    echo "Next steps:"
    echo "1. Verify email arrived in inbox"
    echo "2. Deploy to Vultr: ./DEPLOY_EMAIL_TO_VULTR.sh"
elif echo "$RESPONSE" | grep -q "SmtpClientAuthentication is disabled"; then
    echo "❌ SMTP AUTH is still disabled"
    echo ""
    echo "This means either:"
    echo "  1. You need to wait longer (up to 30 minutes)"
    echo "  2. The setting wasn't saved correctly"
    echo "  3. You need to use an App Password (if MFA enabled)"
    echo ""
    echo "📖 See VERIFY_SMTP_AUTH.md for detailed instructions"
elif echo "$RESPONSE" | grep -q "Authentication unsuccessful"; then
    echo "❌ Authentication failed"
    echo ""
    echo "Possible issues:"
    echo "  1. Wrong EMAIL_PASS in Replit Secrets"
    echo "  2. MFA enabled - need App Password"
    echo "  3. Wrong EMAIL_USER"
    echo ""
    echo "📖 See VERIFY_SMTP_AUTH.md for solutions"
else
    echo "⚠️  Unexpected response - check the output above"
    echo ""
    echo "📖 See VERIFY_SMTP_AUTH.md for troubleshooting"
fi
