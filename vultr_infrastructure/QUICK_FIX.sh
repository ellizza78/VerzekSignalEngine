#!/bin/bash
# Quick fix for VerzekSignalEngine deployment path issue

echo "Finding signal_engine location..."

# Check possible locations
if [ -d "/root/workspace/signal_engine" ]; then
    SIGNAL_PATH="/root/workspace/signal_engine"
elif [ -d "/root/signal_engine" ]; then
    SIGNAL_PATH="/root/signal_engine"
elif [ -d "$HOME/workspace/signal_engine" ]; then
    SIGNAL_PATH="$HOME/workspace/signal_engine"
else
    echo "ERROR: signal_engine not found!"
    echo "Current directory: $(pwd)"
    echo "Listing /root/:"
    ls -la /root/
    echo "Listing /root/workspace/:"
    ls -la /root/workspace/ 2>/dev/null || echo "workspace doesn't exist"
    exit 1
fi

echo "Found signal_engine at: $SIGNAL_PATH"
cd "$SIGNAL_PATH"

# Check if deploy.sh exists
if [ ! -f "deploy.sh" ]; then
    echo "ERROR: deploy.sh not found in $SIGNAL_PATH"
    exit 1
fi

# Make executable and run
chmod +x deploy.sh
echo "Running deployment from $SIGNAL_PATH..."
./deploy.sh
