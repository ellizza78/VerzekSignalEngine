#!/bin/bash
echo "🔍 Checking for latest signal in broadcast_log.txt..."
echo "Last 5 entries:"
tail -5 database/broadcast_log.txt
echo ""
echo "⏰ Current time: $(date '+%Y-%m-%d %H:%M:%S')"
