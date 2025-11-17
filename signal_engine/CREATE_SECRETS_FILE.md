# Create Secrets File on Vultr Server

**CRITICAL:** Before deploying VerzekSignalEngine, you must create a secrets file on the Vultr server.

## Step 1: SSH to Vultr
```bash
ssh root@80.240.29.142
```

## Step 2: Create Secrets File
```bash
cat > /root/.verzek_secrets << 'EOF'
# VerzekSignalEngine Secrets
# DO NOT COMMIT THIS FILE TO GIT

export HOUSE_ENGINE_TOKEN="<your-house-engine-token-from-replit-secrets>"
export TELEGRAM_BOT_TOKEN="<your-broadcast-bot-token-from-replit-secrets>"
export TELEGRAM_VIP_CHAT_ID="<your-vip-chat-id-from-replit-secrets>"
export TELEGRAM_TRIAL_CHAT_ID="<your-trial-chat-id-from-replit-secrets>"
EOF
```

## Step 3: Secure the File
```bash
chmod 600 /root/.verzek_secrets
```

## Step 4: Get Secret Values from Replit

From your Replit Secrets, copy the values for:
- `HOUSE_ENGINE_TOKEN`
- `BROADCAST_BOT_TOKEN` (use this for TELEGRAM_BOT_TOKEN)
- `TELEGRAM_VIP_CHAT_ID`
- `TELEGRAM_TRIAL_CHAT_ID`

## Step 5: Edit the Secrets File
```bash
nano /root/.verzek_secrets
```

Replace the placeholder values with your actual secret values from Replit.

## Step 6: Verify Secrets File
```bash
source /root/.verzek_secrets
echo "HOUSE_ENGINE_TOKEN is set: $([ -n "$HOUSE_ENGINE_TOKEN" ] && echo 'YES' || echo 'NO')"
echo "TELEGRAM_BOT_TOKEN is set: $([ -n "$TELEGRAM_BOT_TOKEN" ] && echo 'YES' || echo 'NO')"
```

You should see:
```
HOUSE_ENGINE_TOKEN is set: YES
TELEGRAM_BOT_TOKEN is set: YES
```

## Step 7: Ready for Deployment
Once the secrets file is created and verified, the deployment will work automatically when you push changes to GitHub.

---

**Security Note:** The secrets file is owned by root with 600 permissions, making it only readable by the root user. Never commit this file to Git.
