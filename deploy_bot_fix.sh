#!/bin/bash
###############################################################################
# Fixed Telegram Bot Deployment
# Switches from Pyrogram to python-telegram-bot (simpler, no API ID needed)
###############################################################################

echo "======================================================================"
echo "🤖 VerzekAutoTrader - Fixed Bot Deployment"
echo "======================================================================"
echo ""

# Stop old bot
echo "⏹️  Stopping old bot..."
systemctl stop verzek-signal-bot.service

# Uninstall Pyrogram
echo "🗑️  Removing Pyrogram..."
pip3 uninstall -y pyrogram

# Install python-telegram-bot
echo "📦 Installing python-telegram-bot..."
pip3 install python-telegram-bot

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
cd /root/VerzekBackend
git pull origin main

# Create directories
echo "📁 Creating directories..."
mkdir -p backend/telegram_signals
mkdir -p backend/telegram_sessions
chmod 777 backend/telegram_signals
chmod 777 backend/telegram_sessions

# Restart bot
echo "🚀 Starting fixed bot..."
systemctl restart verzek-signal-bot.service
sleep 3

# Check status
echo ""
echo "======================================================================"
echo "✅ Deployment Complete! Status:"
echo "======================================================================"
systemctl status verzek-signal-bot.service --no-pager | head -15

echo ""
echo "======================================================================"
echo "📋 View logs: journalctl -u verzek-signal-bot.service -f"
echo "🧪 Test your bot on Telegram now!"
echo "======================================================================"
