#!/bin/bash

echo "📱 Starting VerzekAutoTrader Mobile App..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔑 TEST ACCOUNT CREDENTIALS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Email:    demo@verzektrader.com"
echo "Password: Demo123!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 INSTRUCTIONS:"
echo "1. Install Expo Go on your phone from App/Play Store"
echo "2. Scan the QR code below with:"
echo "   - iOS: Camera app"
echo "   - Android: Expo Go app"
echo "3. App will open on your phone!"
echo ""
echo "Starting Expo development server..."
echo ""

cd mobile_app/VerzekApp
npx expo start
