#!/bin/bash
# Check why verzek-api service failed

echo "🔍 Checking service failure logs..."
echo ""

# Check service status
echo "=== SERVICE STATUS ==="
systemctl status verzek-api.service --no-pager -l
echo ""

# Check recent logs
echo "=== RECENT ERROR LOGS ==="
journalctl -u verzek-api.service -n 50 --no-pager | tail -30
echo ""

# Check if gunicorn is installed
echo "=== CHECKING GUNICORN ==="
which gunicorn
gunicorn --version 2>/dev/null || echo "Gunicorn not found or error"
echo ""

# Check working directory
echo "=== CHECKING WORKING DIRECTORY ==="
ls -la /root/VerzekBackend/backend/api_server.py 2>/dev/null || echo "api_server.py not found"
echo ""

# Check environment file
echo "=== ENVIRONMENT FILE CONTENT ==="
head -10 /root/api_server_env.sh
