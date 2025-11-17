#!/bin/bash
# Quick Cloudflare Workers Proxy Deployment Script
# Run this to deploy static IP proxy in 5 minutes

set -e

echo "🌐 VerzekAutoTrader - Cloudflare Proxy Deployment"
echo "=================================================="
echo ""

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "📦 Installing Wrangler CLI..."
    npm install -g wrangler
fi

# Login to Cloudflare
echo ""
echo "🔐 Please login to Cloudflare..."
wrangler login

# Generate proxy secret key
echo ""
echo "🔑 Generating proxy secret key..."
PROXY_SECRET=$(openssl rand -hex 32)
echo "Generated secret: $PROXY_SECRET"
echo ""

# Deploy worker
echo "🚀 Deploying Cloudflare Worker..."
cd cloudflare_proxy
wrangler deploy

# Get worker URL
echo ""
echo "✅ Deployment complete!"
echo ""
echo "=================================================="
echo "📋 NEXT STEPS:"
echo "=================================================="
echo ""
echo "1. Add these to Replit Secrets:"
echo "   PROXY_ENABLED=true"
echo "   PROXY_URL=https://YOUR_WORKER_URL.workers.dev/proxy"
echo "   PROXY_SECRET_KEY=$PROXY_SECRET"
echo ""
echo "2. In Cloudflare Dashboard:"
echo "   Workers & Pages → Your Worker → Settings → Variables"
echo "   Add: PROXY_SECRET_KEY = $PROXY_SECRET"
echo ""
echo "3. Test health:"
echo "   curl https://YOUR_WORKER_URL.workers.dev/health"
echo ""
echo "4. Restart backend API to load new config"
echo ""
echo "✅ All users' exchange calls will now route through static IP!"
echo "=================================================="
