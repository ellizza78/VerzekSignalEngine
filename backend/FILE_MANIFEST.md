# Backend File Manifest
**Last Updated:** 2025-11-13  
**Commit:** 55e0bdd  
**Version:** 2.1

## Critical Files Checklist

### Core API Files
- [x] api_server.py - Main Flask application
- [x] db.py - Database configuration
- [x] models.py - SQLAlchemy models
- [x] requirements.txt - Python dependencies

### Route Files
- [x] auth_routes.py - Authentication endpoints
- [x] users_routes.py - User management
- [x] positions_routes.py - Trading positions
- [x] signals_routes.py - Signal management
- [x] payments_routes.py - Payment processing
- [x] admin_routes.py - Admin functions

### Utility Files
- [x] utils/email.py - Email verification (Resend API)
- [x] utils/tokens.py - JWT token management
- [x] utils/security.py - Security utilities
- [x] utils/notifications.py - Push notifications
- [x] utils/telegram_notifications.py - Telegram integration
- [x] utils/logger.py - Logging configuration
- [x] utils/rate_limiter.py - Rate limiting
- [x] utils/price_feed.py - Price data

### Trading Engine
- [x] trading/executor.py - Trade execution
- [x] trading/paper_client.py - Paper trading
- [x] worker.py - Background worker
- [x] broadcast.py - Signal broadcasting
- [x] signal_listener.py - Signal monitoring

### Configuration
- [x] config/keywords.json - Signal keywords
- [x] api_version.txt - Version tracking

### Deployment
- [x] deploy/deploy_to_vultr.sh - Deployment script
- [x] deploy/verzek_api.service - Systemd service
- [x] deploy/verzek_worker.service - Worker service

### Documentation
- [x] README.md
- [x] DEPLOYMENT_GUIDE.md
- [x] SECURITY.md
- [x] FILE_MANIFEST.md

## Critical Dependencies (requirements.txt)

```
Flask==3.0.3
Flask-JWT-Extended==4.6.0
Flask-CORS==4.0.0
SQLAlchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.1
requests==2.32.3
python-telegram-bot==21.6
gunicorn==22.0.0
cryptography==41.0.7
bcrypt==4.1.2
resend==2.19.0
```

## File Count Summary
- Python files: 15+
- Route files: 6
- Utility files: 8
- Trading files: 4
- Config files: 2
- Deployment files: 3
- Documentation files: 10+

## Verification Command
```bash
# Run this to verify all critical files exist
for file in api_server.py db.py models.py requirements.txt \
            auth_routes.py users_routes.py positions_routes.py \
            utils/email.py utils/tokens.py trading/executor.py; do
    [ -f "$file" ] && echo "✅ $file" || echo "❌ MISSING: $file"
done
```

## Version Verification
```bash
# Verify resend package version
grep "resend==" requirements.txt
# Expected: resend==2.19.0
```
