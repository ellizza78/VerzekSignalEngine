#!/usr/bin/env python3
"""
Telegram Forwarder Watchdog v1.0
---------------------------------
Monitors the telethon_forwarder.py process for freezes/crashes
and automatically restarts it if needed.

Checks:
1. Heartbeat file freshness (<90 seconds old)
2. Process is running (by PID in heartbeat file)
3. Sends Telegram alerts to admin on failures
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime, timedelta

# Configuration
HEARTBEAT_FILE = "/tmp/forwarder_heartbeat.json"
FORWARDER_SCRIPT = "/var/www/VerzekAutoTrader/telethon_forwarder.py"
FORWARDER_LOG = "/var/www/VerzekAutoTrader/telethon_forwarder.log"
MAX_HEARTBEAT_AGE_SECONDS = 90  # 90 seconds = heartbeat should update every 30s
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

def send_admin_alert(message):
    """Send Telegram notification to admin"""
    if not TELEGRAM_BOT_TOKEN or not ADMIN_CHAT_ID:
        print(f"⚠️ Cannot send alert (missing credentials): {message}")
        return
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": ADMIN_CHAT_ID,
            "text": f"🚨 **Forwarder Watchdog Alert**\n\n{message}",
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            print(f"✅ Alert sent to admin: {message}")
        else:
            print(f"⚠️ Failed to send alert: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to send admin alert: {e}")

def check_heartbeat():
    """Check if heartbeat file exists and is fresh"""
    if not os.path.exists(HEARTBEAT_FILE):
        return False, "Heartbeat file not found"
    
    try:
        with open(HEARTBEAT_FILE, "r") as f:
            data = json.load(f)
        
        heartbeat_time = datetime.fromisoformat(data["timestamp"])
        age_seconds = (datetime.now() - heartbeat_time).total_seconds()
        pid = data.get("pid")
        
        if age_seconds > MAX_HEARTBEAT_AGE_SECONDS:
            return False, f"Heartbeat stale ({int(age_seconds)}s old, PID: {pid})"
        
        return True, f"Heartbeat healthy ({int(age_seconds)}s old, PID: {pid})"
    except Exception as e:
        return False, f"Heartbeat read error: {e}"

def is_process_running(pid):
    """Check if process is running by PID"""
    try:
        os.kill(pid, 0)  # Signal 0 = check if process exists
        return True
    except (OSError, TypeError):
        return False

def restart_forwarder():
    """Kill old process and start new forwarder"""
    print("🔄 Restarting forwarder...")
    
    # Kill any existing forwarder processes
    try:
        subprocess.run(["pkill", "-f", "telethon_forwarder.py"], check=False)
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Error killing old process: {e}")
    
    # Start new forwarder process
    try:
        cmd = f"cd /var/www/VerzekAutoTrader && nohup python3 -u telethon_forwarder.py > {FORWARDER_LOG} 2>&1 &"
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Forwarder restarted")
        send_admin_alert("🔄 **Forwarder Restarted**\n\nThe Telegram signal forwarder was automatically restarted by the watchdog.")
        return True
    except Exception as e:
        error_msg = f"Failed to restart: {e}"
        print(f"❌ {error_msg}")
        send_admin_alert(f"❌ **Forwarder Restart Failed**\n\n{error_msg}")
        return False

def main():
    """Main watchdog check"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Forwarder Watchdog Check")
    
    # Check heartbeat
    is_healthy, status_msg = check_heartbeat()
    print(f"  {status_msg}")
    
    if not is_healthy:
        print("  ❌ Forwarder unhealthy - restarting...")
        send_admin_alert(f"⚠️ **Forwarder Frozen Detected**\n\n{status_msg}\n\nAttempting automatic restart...")
        restart_forwarder()
    else:
        print("  ✅ Forwarder healthy")

if __name__ == "__main__":
    main()
