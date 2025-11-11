# VerzekAutoTrader Backend Deployment Notes

## ⚠️ Known Limitations (To Fix Before Production)

### 1. Token Storage (CRITICAL)
**Issue:** Password reset and email verification tokens are stored in-memory only (`backend/utils/tokens.py` - `_active_tokens` dict).

**Impact:** 
- Tokens are lost on API restart
- Multi-worker deployments will fail (each worker has separate memory)
- Not production-safe

**Solution Required:**
Create a database table for token persistence:
```sql
CREATE TABLE verification_tokens (
  id SERIAL PRIMARY KEY,
  token VARCHAR(255) UNIQUE NOT NULL,
  user_id INTEGER REFERENCES users(id),
  token_type VARCHAR(50) NOT NULL,  -- 'password_reset', 'email_verification'
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Telegram Trial Group Link
**Issue:** Chat ID -1002726167386 cannot be used as a direct link.

**Required:** Get the actual invite link from Telegram group settings:
1. Open the trial group in Telegram
2. Go to Group Settings → Invite Links
3. Generate or copy the invite link
4. Update `SubscriptionScreen.js` with the actual link

**Formats:**
- `https://t.me/+INVITE_HASH` (private group with invite hash)
- `https://t.me/groupusername` (public group with username)
- `@groupusername` (public group)

## ✅ Completed Features

### Backend
- ✅ Email service with Resend API
- ✅ Password reset endpoints
- ✅ Referral code generation
- ✅ Welcome emails on registration
- ✅ User auto-verification (per user request)

### Mobile App
- ✅ Auth context fixed (is_verified consistency)
- ✅ Telegram support links (t.me/+7442859456)
- ✅ Email updated (support@verzekinnovative.com)
- ✅ Exchange setup forms
- ✅ Trade settings UI
- ✅ Help resources

## Deployment Instructions

### Option 1: Manual Deployment
```bash
# 1. Copy files to VPS
scp backend/models.py root@80.240.29.142:/root/VerzekBackend/backend/
scp backend/auth_routes.py root@80.240.29.142:/root/VerzekBackend/backend/blueprints/
scp backend/utils/email.py root@80.240.29.142:/root/VerzekBackend/backend/utils/
scp backend/utils/tokens.py root@80.240.29.142:/root/VerzekBackend/backend/utils/

# 2. Install dependencies
ssh root@80.240.29.142 "cd /root/VerzekBackend/backend && pip install resend"

# 3. Add RESEND_API_KEY to environment
ssh root@80.240.29.142 "echo 'export RESEND_API_KEY=re_Ekp94KgJ_M3ybkABUaRn5gpXkeCv6QCRL' >> /root/api_server_env.sh"

# 4. Recreate database with new schema
ssh root@80.240.29.142 "cd /root/VerzekBackend/backend && python3 -c 'from db import engine, Base; from models import *; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine); print(\"Database recreated\")'"

# 5. Restart API
ssh root@80.240.29.142 "systemctl restart verzek-api"

# 6. Test
curl https://api.verzekinnovative.com/api/health
```

### Option 2: Automated Script
```bash
chmod +x backend/deploy_updates.sh
./backend/deploy_updates.sh
```

## Testing Checklist

After deployment, test these endpoints:

```bash
# 1. Health check
curl https://api.verzekinnovative.com/api/health

# 2. Registration
curl -X POST https://api.verzekinnovative.com/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"Test123","full_name":"Test User"}'

# 3. Login
curl -X POST https://api.verzekinnovative.com/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"Test123"}'

# 4. Password reset request
curl -X POST https://api.verzekinnovative.com/api/auth/forgot-password \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com"}'
```

## Mobile App Updates

The Expo workflow has been restarted to push OTA updates with:
- Fixed AuthContext (is_verified consistency)
- Updated Telegram support links
- Updated email addresses
- Trial group link now directs to support

Users with existing APK will receive OTA update automatically on next app launch.

