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
    
    # Uncomment below if you want to run the main signal bot too
    # main_thread = Thread(target=run_main_bot, daemon=True)
    # main_thread.start()
    
    print("✅ All services started successfully!")
    print("🔄 Auto-Forwarder monitoring your personal chats...")
    print("📡 Broadcast Bot is listening and ready to broadcast...")
    print("🌐 API Server running on port 5000")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⛔ Shutting down all services...")
        sys.exit(0)
