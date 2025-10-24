#!/bin/bash
echo "🔍 Checking latest signals..."
echo "Last 5 entries in broadcast_log.txt:"
echo "-----------------------------------"
tail -5 database/broadcast_log.txt
echo ""
echo "⏰ Current time: $(date '+%Y-%m-%d %H:%M:%S')"
