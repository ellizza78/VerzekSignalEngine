# 🔐 Verzek AutoTrader - Security & Secrets Management

## Critical Security Requirements

### 1. Encryption Key (REQUIRED)

The `ENCRYPTION_KEY` is **mandatory** and must be generated before deployment. This key encrypts all exchange API credentials stored in the database.

**Generate encryption key:**
```bash
python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

**⚠️ IMPORTANT:**
- Generate this key **once** and store it securely
- **Never** regenerate this key after users have added exchange accounts
- Regenerating will make all stored API credentials **unreadable**
- Keep this key in `/root/api_server_env.sh` (chmod 600)

### 2. Deployment Secrets File

**Before deployment**, create `/root/api_server_env.sh` on your Vultr VPS:

```bash
#!/bin/bash
# Verzek AutoTrader Configuration

# Security (REQUIRED)
export JWT_SECRET="VerzekAutoTraderKey2025"
export API_KEY="Verzek2025AutoTrader"

# Encryption Key (REQUIRED - GENERATE ONCE AND KEEP SAFE)
export ENCRYPTION_KEY="<YOUR_GENERATED_FERNET_KEY>"

# Database
export DATABASE_URL="sqlite:////root/api_server/database/verzek.db"
export EXCHANGE_MODE="paper"

# Telegram (REQUIRED for broadcasting)
export TELEGRAM_BOT_TOKEN="<YOUR_BOT_TOKEN>"
export TELEGRAM_VIP_CHAT_ID="<YOUR_VIP_CHAT_ID>"
export TELEGRAM_TRIAL_CHAT_ID="<YOUR_TRIAL_CHAT_ID>"

# Worker
export WORKER_POLL_SECONDS="10"

# Server
export FLASK_ENV="production"
export PORT="8050"
export SERVER_IP="80.240.29.142"
```

**Set proper permissions:**
```bash
chmod 600 /root/api_server_env.sh
chown root:root /root/api_server_env.sh
```

### 3. Telegram Bot Setup

1. **Create bot** via [@BotFather](https://t.me/BotFather)
   ```
   /newbot
   Follow prompts to get your TELEGRAM_BOT_TOKEN
   ```

2. **Create VIP group**
   - Create new Telegram group
   - Add your bot as admin
   - Get chat ID: `/my_id` via [@userinfobot](https://t.me/userinfobot)
   
3. **Create TRIAL group**
   - Repeat process for trial users
   
4. **Update environment file** with:
   - `TELEGRAM_BOT_TOKEN` from BotFather
   - `TELEGRAM_VIP_CHAT_ID` from your VIP group
   - `TELEGRAM_TRIAL_CHAT_ID` from your Trial group

### 4. Production Deployment Checklist

**On Vultr VPS (80.240.29.142):**

1. ✅ Create `/root/api_server_env.sh` with all secrets
2. ✅ Set permissions: `chmod 600 /root/api_server_env.sh`
3. ✅ Generate and save `ENCRYPTION_KEY` (DO NOT LOSE THIS)
4. ✅ Configure Telegram bot and groups
5. ✅ Run deployment script: `./deploy/deploy_to_vultr.sh`
6. ✅ Verify API: `curl https://api.verzekinnovative.com/api/health`
7. ✅ Test Telegram broadcasting
8. ✅ Backup encryption key to secure location

### 5. Secret Rotation

**If you need to rotate secrets:**

**JWT_SECRET:**
```bash
# Update /root/api_server_env.sh
# Restart services
systemctl restart verzek_api verzek_worker
```

**ENCRYPTION_KEY (⚠️ DANGEROUS):**
```bash
# DO NOT ROTATE unless absolutely necessary
# Will invalidate all stored exchange credentials
# Users will need to re-add their exchange accounts
```

**Telegram Bot Token:**
```bash
# Get new token from @BotFather
# Update /root/api_server_env.sh
# Restart services
systemctl restart verzek_api verzek_worker
```

### 6. Backup & Recovery

**Critical files to backup:**
```bash
/root/api_server_env.sh          # Secrets file
/root/api_server/database/       # User data and positions
```

**Backup command:**
```bash
tar -czf verzek_backup_$(date +%Y%m%d).tar.gz \
  /root/api_server_env.sh \
  /root/api_server/database/
```

**Recovery:**
```bash
# Restore secrets file
cp verzek_backup_*/api_server_env.sh /root/
chmod 600 /root/api_server_env.sh

# Restore database
tar -xzf verzek_backup_*.tar.gz -C /
systemctl restart verzek_api verzek_worker
```

### 7. Security Best Practices

✅ **DO:**
- Keep `/root/api_server_env.sh` with chmod 600
- Rotate JWT_SECRET quarterly
- Monitor API logs for suspicious activity
- Use SSL/TLS (Let's Encrypt) for API
- Keep system packages updated
- Backup encryption key to secure offline storage

❌ **DON'T:**
- Commit secrets to git
- Share encryption key via email/chat
- Regenerate ENCRYPTION_KEY after user onboarding
- Expose API without SSL
- Run services as non-root without proper permissions
- Log secrets in application logs

### 8. Incident Response

**If encryption key is compromised:**
1. Immediately rotate the key
2. Notify all users to re-add exchange accounts
3. Audit database for unauthorized access
4. Review systemd service logs

**If Telegram bot token is leaked:**
1. Revoke old token via @BotFather
2. Generate new token
3. Update `/root/api_server_env.sh`
4. Restart services

**If API credentials are exposed:**
1. Rotate JWT_SECRET immediately
2. Force all users to re-login
3. Audit trade logs for suspicious activity
4. Review nginx access logs

---

## Contact

For security concerns, contact: **security@verzekinnovative.com**

**Never** discuss secrets in public channels or GitHub issues.
