#!/bin/bash
echo "=============================="
echo "🚀 VerzekAutoTrader Startup"
echo "=============================="

# Function to start the Cloudflare tunnel
start_tunnel() {
  echo "🔵 Starting Cloudflare Tunnel..."
  ./cloudflared tunnel run my-tunnel &
  TUNNEL_PID=$!
  sleep 8
  if ps -p $TUNNEL_PID > /dev/null; then
    echo "✅ Tunnel is running (PID: $TUNNEL_PID)"
  else
    echo "❌ Tunnel failed to start!"
  fi
}

# Function to start your bot
start_bot() {
  echo "🤖 Starting VerzekAutoTrader Bot..."
  python crypto_bot.py &
  BOT_PID=$!
  sleep 5
  if ps -p $BOT_PID > /dev/null; then
    echo "✅ Bot is running (PID: $BOT_PID)"
  else
    echo "❌ Bot failed to start!"
  fi
}

# Start both processes
start_tunnel
start_bot

# Auto-restart loop if either process stops
while true; do
  if ! ps -p $TUNNEL_PID > /dev/null; then
    echo "⚠️ Tunnel stopped — restarting..."
    start_tunnel
  fi
  if ! ps -p $BOT_PID > /dev/null; then
    echo "⚠️ Bot stopped — restarting..."
    start_bot
  fi
  sleep 30
done