"""
run_all_bots.py
---------------
Runs all VerzekAutoTrader bots simultaneously:
- Flask API Server
- Telethon Forwarder (Auto-forwarding from personal chats)
- Broadcast Bot
- Main Signal Bot (optional - uncomment if needed)
"""

import subprocess
import sys
import time
from threading import Thread

def run_flask_api():
    """Run Flask API server"""
    print("🌐 Starting Flask API Server...")
    subprocess.run([sys.executable, "api_server.py"])

def run_telethon_forwarder():
    """Run Telethon Auto-Forwarder"""
    # Check if authenticated first
    import os
    
    # Detect if running in development (Replit workspace) vs production (deployment)
    # REPL_SLUG exists in workspace, REPL_DEPLOYMENT_ID exists in deployment
    is_development = os.getenv("REPL_SLUG") and not os.getenv("REPL_DEPLOYMENT_ID")
    
    # Skip Telethon in dev to avoid dual-IP conflicts with production
    if is_development or os.getenv("DISABLE_TELETHON", "").lower() == "true":
        print("⏭️ Telethon disabled in development (prevents dual-IP session conflicts)")
        print("📱 Telethon runs ONLY in production deployment for 24/7 signal monitoring")
        return
    
    if not os.path.exists("telethon_session_string.txt"):
        print("⚠️ Telethon not authenticated yet. Run 'python setup_telethon.py' first.")
        return
    
    print("🔄 Starting Telethon Auto-Forwarder...")
    subprocess.run([sys.executable, "telethon_forwarder.py"])

def run_broadcast_bot():
    """Run Broadcast Bot"""
    print("📡 Starting Broadcast Bot...")
    subprocess.run([sys.executable, "broadcast_bot.py"])

def run_main_bot():
    """Run Main Signal Bot"""
    print("🤖 Starting Main Signal Bot...")
    subprocess.run([sys.executable, "main.py"])

def run_target_monitor():
    """Run Target Monitor for progressive TPs"""
    print("🎯 Starting Target Monitor...")
    subprocess.run([sys.executable, "target_monitor.py"])

def run_recurring_payments():
    """Run Recurring Payments Handler for monthly commissions"""
    print("💰 Starting Recurring Payments Handler...")
    subprocess.run([sys.executable, "recurring_payments_service.py"])

def run_advanced_orders_monitor():
    """Run Advanced Orders Monitor for trailing stops and OCO orders"""
    print("📊 Starting Advanced Orders Monitor...")
    subprocess.run([sys.executable, "advanced_orders_monitor.py"])

def run_price_feed_service():
    """Run Real-Time Price Feed Service for live market data"""
    print("📡 Starting Price Feed Service...")
    subprocess.run([sys.executable, "price_feed_service.py"])

if __name__ == "__main__":
    print("🚀 VerzekAutoTrader - Starting All Services...")
    
    # Start Flask API in a thread
    flask_thread = Thread(target=run_flask_api, daemon=True)
    flask_thread.start()
    
    # Give Flask a moment to start
    time.sleep(2)
    
    # Start Telethon Auto-Forwarder in a thread
    telethon_thread = Thread(target=run_telethon_forwarder, daemon=True)
    telethon_thread.start()
    
    # Start Broadcast Bot in a thread
    broadcast_thread = Thread(target=run_broadcast_bot, daemon=True)
    broadcast_thread.start()
    
    # Start Target Monitor in a thread
    target_monitor_thread = Thread(target=run_target_monitor, daemon=True)
    target_monitor_thread.start()
    
    # Start Recurring Payments Handler in a thread
    recurring_thread = Thread(target=run_recurring_payments, daemon=True)
    recurring_thread.start()
    
    # Start Advanced Orders Monitor in a thread
    advanced_orders_thread = Thread(target=run_advanced_orders_monitor, daemon=True)
    advanced_orders_thread.start()
    
    # Start Price Feed Service in a thread
    price_feed_thread = Thread(target=run_price_feed_service, daemon=True)
    price_feed_thread.start()
    
    # Uncomment below if you want to run the main signal bot too
    # main_thread = Thread(target=run_main_bot, daemon=True)
    # main_thread.start()
    
    print("✅ All services started successfully!")
    print("🔄 Auto-Forwarder monitoring your personal chats...")
    print("📡 Broadcast Bot is listening and ready to broadcast...")
    print("🎯 Target Monitor checking for take profit levels...")
    print("💰 Recurring Payments processing monthly commissions...")
    print("📊 Advanced Orders Monitor tracking trailing stops & OCO orders...")
    print("📡 Price Feed Service streaming live market data...")
    print("🌐 API Server running on port 5000")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⛔ Shutting down all services...")
        sys.exit(0)
