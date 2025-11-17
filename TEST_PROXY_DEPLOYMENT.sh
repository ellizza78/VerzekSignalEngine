#!/bin/bash
# Test Proxy Deployment and Configuration
# Verifies that proxy infrastructure is ready

set -e

echo "🧪 VerzekAutoTrader - Proxy Deployment Test"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check environment variables
echo "📋 Test 1: Environment Variables"
echo "--------------------------------"

if [ -n "$PROXY_SECRET_KEY" ]; then
    echo -e "${GREEN}✅ PROXY_SECRET_KEY: Set${NC}"
else
    echo -e "${YELLOW}⚠️  PROXY_SECRET_KEY: Not set${NC}"
    echo "   Generate one with: openssl rand -hex 32"
fi

if [ -n "$PROXY_URL" ]; then
    echo -e "${GREEN}✅ PROXY_URL: $PROXY_URL${NC}"
else
    echo -e "${YELLOW}⚠️  PROXY_URL: Not set${NC}"
fi

if [ "${PROXY_ENABLED}" == "true" ]; then
    echo -e "${GREEN}✅ PROXY_ENABLED: true${NC}"
else
    echo -e "${YELLOW}⚠️  PROXY_ENABLED: ${PROXY_ENABLED:-false}${NC}"
fi

echo ""

# Test 2: Check ProxyHelper integration
echo "🔧 Test 2: ProxyHelper Integration"
echo "--------------------------------"

PROXY_FILES=(
    "exchanges/proxy_helper.py"
    "exchanges/binance_client.py"
    "exchanges/bybit_client.py"
    "exchanges/phemex_client.py"
    "exchanges/kraken_client.py"
)

for file in "${PROXY_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file exists${NC}"
    else
        echo -e "${RED}❌ $file missing${NC}"
    fi
done

echo ""

# Test 3: Check deployment scripts
echo "📦 Test 3: Deployment Scripts"
echo "--------------------------------"

if [ -f "cloudflare_proxy/worker.js" ]; then
    echo -e "${GREEN}✅ Cloudflare Worker ready${NC}"
else
    echo -e "${RED}❌ cloudflare_proxy/worker.js missing${NC}"
fi

if [ -f "deploy_cloudflare_proxy.sh" ]; then
    echo -e "${GREEN}✅ Deployment script ready${NC}"
else
    echo -e "${RED}❌ deploy_cloudflare_proxy.sh missing${NC}"
fi

if [ -f "DEPLOY_STATIC_IP_PROXY.md" ]; then
    echo -e "${GREEN}✅ Deployment guide ready${NC}"
else
    echo -e "${RED}❌ DEPLOY_STATIC_IP_PROXY.md missing${NC}"
fi

echo ""

# Test 4: Python proxy helper import
echo "🐍 Test 4: Python ProxyHelper Import"
echo "--------------------------------"

python3 -c "
from exchanges.proxy_helper import get_proxy_helper
proxy = get_proxy_helper()
print('✅ ProxyHelper imports successfully')
print(f'   Proxy enabled: {proxy.proxy_enabled}')
print(f'   Proxy URL: {proxy.proxy_url or \"Not set\"}')
" 2>&1 | while read line; do
    if [[ $line == *"✅"* ]]; then
        echo -e "${GREEN}$line${NC}"
    elif [[ $line == *"❌"* ]]; then
        echo -e "${RED}$line${NC}"
    else
        echo "   $line"
    fi
done

echo ""

# Summary
echo "============================================"
echo "📊 DEPLOYMENT STATUS SUMMARY"
echo "============================================"
echo ""

if [ -n "$PROXY_SECRET_KEY" ] && [ -n "$PROXY_URL" ] && [ "${PROXY_ENABLED}" == "true" ]; then
    echo -e "${GREEN}✅ READY: Proxy fully configured and enabled${NC}"
    echo "   All exchange calls will route through proxy"
elif [ -f "cloudflare_proxy/worker.js" ] && [ -f "deploy_cloudflare_proxy.sh" ]; then
    echo -e "${YELLOW}⚠️  READY TO DEPLOY: Infrastructure prepared${NC}"
    echo "   Run: ./deploy_cloudflare_proxy.sh"
    echo "   Then set environment variables in Replit Secrets"
else
    echo -e "${RED}❌ NOT READY: Missing files or configuration${NC}"
fi

echo ""
echo "📖 For deployment instructions:"
echo "   cat DEPLOY_STATIC_IP_PROXY.md"
echo ""
