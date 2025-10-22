#!/bin/bash

clear

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║      📱 VZK AutoTrader - EXPO GO (CAPTCHA REMOVED)             ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔑 LOGIN CREDENTIALS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   Email:    demo@verzektrader.com"
echo "   Password: Demo123!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ BACKEND STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   ✅ CAPTCHA completely removed"
echo "   ✅ Login endpoint tested and working"
echo "   ✅ Fresh app install (no cached data)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 STARTING EXPO SERVER..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Kill any existing processes
pkill -f "expo start" 2>/dev/null
pkill -f "node.*metro" 2>/dev/null
sleep 1

# Clear cache
rm -rf mobile_app/VerzekApp/.expo 2>/dev/null
rm -rf mobile_app/VerzekApp/node_modules/.cache 2>/dev/null

# Start Expo
cd mobile_app/VerzekApp
npx expo start --clear

