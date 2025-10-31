#!/bin/bash
#############################################################################
# Verzek Config Service Watchdog - Auto-restart on crash
# Paste this entire block on your Vultr server
#############################################################################

cd /root

# Create the watchdog script
cat > /root/config_watchdog.py << 'WATCHDOG_EOF'
#!/usr/bin/env python3
"""
Verzek Config Service Watchdog
Monitors config_api.py and auto-restarts if crashed
"""

import subprocess
import time
import sys
import os
from datetime import datetime

LOG_FILE = '/tmp/config_watchdog.log'
SERVICE_SCRIPT = '/root/config_api.py'
SERVICE_PORT = 5001
CHECK_INTERVAL = 30  # Check every 30 seconds

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + '\n')

def is_service_running():
    """Check if config_api.py process is running"""
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'config_api.py'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        log(f"Error checking process: {e}")
        return False

def is_port_open():
    """Check if service is responding on port"""
    try:
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
             f'http://localhost:{SERVICE_PORT}/api/app-config'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout == '200'
    except Exception:
        return False

def start_service():
    """Start the config API service"""
    try:
        # Kill any existing instances
        subprocess.run(['pkill', '-9', '-f', 'config_api.py'], 
                      capture_output=True)
        time.sleep(2)
        
        # Start new instance
        subprocess.Popen(
            ['python3', SERVICE_SCRIPT],
            stdout=open('/tmp/config_api.log', 'a'),
            stderr=subprocess.STDOUT,
            cwd='/root'
        )
        
        time.sleep(3)
        log("✅ Config service started")
        return True
    except Exception as e:
        log(f"❌ Failed to start service: {e}")
        return False

def main():
    log("🔍 Config Watchdog started")
    consecutive_failures = 0
    
    while True:
        try:
            # Check if process is running and port is open
            process_running = is_service_running()
            port_responding = is_port_open()
            
            if not process_running or not port_responding:
                consecutive_failures += 1
                log(f"⚠️  Service down (process={process_running}, port={port_responding})")
                
                if consecutive_failures >= 2:
                    log("🔄 Restarting config service...")
                    if start_service():
                        consecutive_failures = 0
                        log("✅ Service restarted successfully")
                    else:
                        log("❌ Failed to restart service")
            else:
                if consecutive_failures > 0:
                    log("✅ Service recovered")
                consecutive_failures = 0
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("🛑 Watchdog stopped by user")
            sys.exit(0)
        except Exception as e:
            log(f"❌ Watchdog error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
WATCHDOG_EOF

chmod +x /root/config_watchdog.py

# Create systemd service for watchdog
cat > /etc/systemd/system/verzek-watchdog.service << 'SERVICE_EOF'
[Unit]
Description=Verzek Config Service Watchdog
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
ExecStart=/usr/bin/python3 /root/config_watchdog.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Enable and start watchdog service
systemctl daemon-reload
systemctl enable verzek-watchdog
systemctl start verzek-watchdog

echo ""
echo "✅ CONFIG WATCHDOG INSTALLED!"
echo ""
echo "📋 Services:"
echo "  • Config API: Monitored by watchdog"
echo "  • Watchdog: Auto-starts config service if crashed"
echo ""
echo "🔍 Check status:"
echo "  systemctl status verzek-watchdog"
echo ""
echo "📝 View logs:"
echo "  tail -f /tmp/config_watchdog.log"
echo ""
echo "🧪 Test endpoint:"
curl -s http://localhost:5001/api/app-config | python3 -m json.tool | head -20
