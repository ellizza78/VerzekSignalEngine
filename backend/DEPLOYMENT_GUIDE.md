# VerzekAutoTrader - Complete Deployment Guide

## ✅ Email Verification System - Production Ready

The system now includes complete email verification with database-persisted tokens.

### Database Schema Changes

New table added:
```sql
CREATE TABLE verification_tokens (
  id INTEGER PRIMARY KEY,
  token VARCHAR(255) UNIQUE NOT NULL,
  user_id INTEGER REFERENCES users(id) NOT NULL,
  token_type VARCHAR(50) NOT NULL,  -- 'email_verification' or 'password_reset'
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Email Verification Flow

1. **Registration** (`POST /api/auth/register`)
   - User is created with `is_verified=False`
   - Verification token generated (24-hour expiry)
   - Verification email sent via Resend API
   - Returns access/refresh tokens but login will fail until verified

2. **Email Verification** (`POST /api/auth/verify-email`)
   - User clicks link in email with token
   - Token validated from database
   - User marked as `is_verified=True`
   - Token deleted from database

3. **Login** (`POST /api/auth/login`)
   - Checks credentials
   - **Blocks unverified users** with HTTP 403 and `needs_verification: true`
   - Verified users get access/refresh tokens

4. **Resend Verification** (`POST /api/auth/resend-verification`)
   - Requires JWT token
   - Generates new verification token
   - Sends new verification email

### Password Reset Flow

1. **Request Reset** (`POST /api/auth/forgot-password`)
   - Generates 15-minute token
   - Stores in database
   - Sends reset email

2. **Reset Password** (`POST /api/auth/reset-password`)
   - Validates token from database
   - Updates password
   - Deletes token

### Deployment Steps

#### Step 1: Backup Current Database
```bash
ssh root@80.240.29.142 "cd /root/VerzekBackend/backend && cp verzek.db verzek.db.backup_$(date +%Y%m%d_%H%M%S)"
```

#### Step 2: Copy Updated Files
```bash
# Models
scp backend/models.py root@80.240.29.142:/root/VerzekBackend/backend/

# Auth routes
scp backend/auth_routes.py root@80.240.29.142:/root/VerzekBackend/backend/blueprints/

# Utilities
scp backend/utils/tokens.py root@80.240.29.142:/root/VerzekBackend/backend/utils/
scp backend/utils/email.py root@80.240.29.142:/root/VerzekBackend/backend/utils/
```

#### Step 3: Add RESEND_API_KEY
```bash
# ⚠️ IMPORTANT: Replace YOUR_RESEND_API_KEY with your actual Resend API key
# Get your key from: https://resend.com/api-keys
ssh root@80.240.29.142 "echo 'export RESEND_API_KEY=YOUR_RESEND_API_KEY' >> /root/api_server_env.sh"
```

#### Step 4: Install Dependencies
```bash
ssh root@80.240.29.142 "cd /root/VerzekBackend/backend && pip install resend"
```

#### Step 5: Update Database Schema
```bash
ssh root@80.240.29.142 "cd /root/VerzekBackend/backend && python3 << 'PYEOF'
from db import engine, Base, SessionLocal
from models import VerificationToken

# Add new table
Base.metadata.create_all(bind=engine)
print('✅ verification_tokens table created')

# Verify existing users
db = SessionLocal()
from models import User
users = db.query(User).all()
print(f'Found {len(users)} users in database')

# Optional: Mark existing users as verified (for migration)
for user in users:
    if not user.is_verified:
        user.is_verified = False  # They will need to verify
        print(f'User {user.email} needs verification')

db.commit()
db.close()
print('✅ Database migration complete')
PYEOF"
```

#### Step 6: Restart API Service
```bash
ssh root@80.240.29.142 "systemctl restart verzek-api && systemctl status verzek-api"
```

#### Step 7: Test Endpoints

```bash
# 1. Health check
curl https://api.verzekinnovative.com/api/health

# 2. Register new user
curl -X POST https://api.verzekinnovative.com/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "test@example.com",
    "password": "Test123",
    "full_name": "Test User"
  }'

# Expected: Returns access_token but user is not verified

# 3. Try to login (should fail)
curl -X POST https://api.verzekinnovative.com/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "test@example.com",
    "password": "Test123"
  }'

# Expected: HTTP 403 with "needs_verification": true

# 4. Verify email (get token from email)
curl -X POST https://api.verzekinnovative.com/api/auth/verify-email \
  -H 'Content-Type: application/json' \
  -d '{
    "token": "VERIFICATION_TOKEN_FROM_EMAIL"
  }'

# Expected: HTTP 200 with success message

# 5. Login after verification (should succeed)
curl -X POST https://api.verzekinnovative.com/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "test@example.com",
    "password": "Test123"
  }'

# Expected: HTTP 200 with access_token
```

### Cron Job for Token Cleanup

Add to crontab to clean expired tokens hourly:
```bash
ssh root@80.240.29.142 "crontab -e"
# Add line:
0 * * * * cd /root/VerzekBackend/backend && python3 -c 'from utils.tokens import cleanup_expired_tokens; from db import SessionLocal; db = SessionLocal(); cleanup_expired_tokens(db); db.close()' >> /var/log/verzek_cleanup.log 2>&1
```

### Mobile App Changes Required

The mobile app needs to handle the verification flow:

1. **Registration Screen**
   - Show success message with verification instructions
   - Inform user to check email

2. **Login Screen**
   - Check for `needs_verification: true` in error response
   - Show "Email not verified" message
   - Provide "Resend Verification Email" button

3. **Email Verification Screen** (NEW - needs implementation)
   - Deep link handler for verification URLs
   - Call `/api/auth/verify-email` with token from URL
   - Show success/failure message
   - Navigate to login on success

## Security Notes

1. **Token Security**: Tokens are 32-byte URL-safe random strings
2. **Email Privacy**: Password reset never reveals if email exists
3. **Token Expiry**: Verification = 24h, Password Reset = 15min
4. **Auto-Cleanup**: Expired tokens are deleted automatically
5. **One-Time Use**: Tokens are deleted after successful use
6. **API Keys**: NEVER commit API keys to the repository. Always use environment variables.

## Rollback Plan

If issues occur, roll back to previous version:

```bash
# Restore database backup
ssh root@80.240.29.142 "cd /root/VerzekBackend/backend && cp verzek.db.backup_TIMESTAMP verzek.db"

# Restart API
ssh root@80.240.29.142 "systemctl restart verzek-api"
```

## Next Steps

1. Deploy to VPS
2. Test email verification flow end-to-end
3. Update mobile app to handle verification flow
4. Monitor logs for any issues
5. Test OTA updates for remote config changes

---

## 🔐 Admin System (NEW - Nov 12, 2025)

### Admin Endpoints for Payment & Subscription Management

**CRITICAL: Set ADMIN_EMAIL environment variable**
```bash
# In /root/api_server_env.sh
export ADMIN_EMAIL="your_admin_email@example.com"
```

### Admin Endpoints:
- `GET /api/admin/payments/pending` - View pending payment verifications
- `POST /api/admin/payments/approve/<payment_id>` - Approve payment & upgrade user
- `POST /api/admin/payments/reject/<payment_id>` - Reject payment  
- `GET /api/admin/payments/all` - All payments with filters
- `GET /api/admin/subscriptions/overview` - Revenue & subscription stats
- `GET /api/admin/referrals` - Complete referral tree
- `GET /api/admin/referrals/payouts` - Calculate referral bonuses
- `GET /api/admin/stats` - Platform statistics

**Full admin guide:** See `ADMIN_REFERRAL_GUIDE.md`

### Security Fix Applied:
✅ Payment approval now restricted to admin only (prevents self-upgrade vulnerability)

---

## 📦 Quick Deployment Checklist

1. **Backup database**
   ```bash
   cp database/verzek_autotrader.db database/verzek_autotrader.db.backup.$(date +%Y%m%d)
   ```

2. **Upload & extract package**
   ```bash
   scp /tmp/verzek_backend_complete.tar.gz root@80.240.29.142:/tmp/
   cd /root/VerzekBackend/backend && tar -xzf /tmp/verzek_backend_complete.tar.gz
   ```

3. **Run migrations** (if not already done)
   ```bash
   sqlite3 database/verzek_autotrader.db < database/migrations/add_verification_tokens.sql
   sqlite3 database/verzek_autotrader.db < database/migrations/add_device_tokens.sql
   ```

4. **Set ADMIN_EMAIL** (in `/root/api_server_env.sh`)
   ```bash
   export ADMIN_EMAIL="admin@verzekinnovative.com"
   ```

5. **Restart API**
   ```bash
   /root/restart_verzek_api.sh
   ```

6. **Verify deployment**
   ```bash
   curl https://api.verzekinnovative.com/api/health
   tail -f /root/VerzekBackend/backend/logs/api.log  # Check for ADMIN_EMAIL warning
   ```
