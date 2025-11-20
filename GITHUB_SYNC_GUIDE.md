# 📦 GitHub Sync Guide: VerzekBackend

## Overview

This guide helps you manually sync your backend code from Replit to GitHub, then deploy to Vultr production.

---

## 🎯 Repository

**GitHub Repo:** https://github.com/ellizza78/VerzekBackend

**Production Sync Folder:** `vultr_production_sync/` (in Replit workspace)

---

## 📂 What to Sync

The `vultr_production_sync/` folder contains ONLY production-ready files:

```
vultr_production_sync/
├── api_server.py          # Main Flask app (modular architecture)
├── auth_routes.py         # Authentication endpoints
├── users_routes.py        # User management + Exchange Balance endpoint ✨
├── signals_routes.py      # Signal ingestion endpoints
├── house_signals_routes.py # House signals (VerzekSignalEngine v2.0)
├── positions_routes.py    # Position management
├── payments_routes.py     # USDT TRC20 payments
├── admin_routes.py        # Admin dashboard endpoints
├── db.py                  # Database connection
├── models.py              # SQLAlchemy models
├── worker.py              # Background DCA worker
├── requirements.txt       # Python dependencies
├── gunicorn.conf.py       # Gunicorn configuration
├── config/                # Email templates, safety configs
├── exchanges/             # Binance, Bybit, Phemex, Kraken adapters
├── trading/               # DCA executor, paper trading
├── utils/                 # Helpers (email, notifications, security)
└── reports/               # Daily reports with TP1-TP5 breakdown ✨
```

---

## 🔄 Manual Git Workflow (From Replit Shell)

### Step 1: Initialize Git in Sync Folder (First Time Only)

```bash
cd vultr_production_sync

# Initialize git if not already
git init 2>/dev/null || echo "Git already initialized"

# Configure your GitHub credentials
git config user.name "Your Name"
git config user.email "your-email@example.com"

# Add GitHub remote
git remote add origin https://github.com/ellizza78/VerzekBackend.git 2>/dev/null || \
git remote set-url origin https://github.com/ellizza78/VerzekBackend.git

# Create .gitignore if needed
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
*.pyd
.env
*.log
.DS_Store
.vscode/
.idea/
*.swp
EOF
```

---

### Step 2: Stage and Commit Changes

```bash
cd vultr_production_sync

# Check what's changed
git status

# Stage all production files
git add -A

# Commit with descriptive message
git commit -m "Backend Sync: Production API v2.1.1 – Clean structure, Exchange Balance endpoint, TP1-TP5 stats"
```

---

### Step 3: Push to GitHub

```bash
# Push to main branch
git push -u origin main

# If this is the first push and branch doesn't exist:
git branch -M main
git push -u origin main --force

# If you need to authenticate with Personal Access Token (PAT):
# GitHub Username: ellizza78
# Password: <your_github_personal_access_token>
```

**Troubleshooting:**
- **Authentication Failed:** Create a Personal Access Token (PAT) at https://github.com/settings/tokens
- **Remote Already Exists:** Use `git remote set-url origin https://github.com/ellizza78/VerzekBackend.git`
- **Branch Conflicts:** Use `git push --force` (only if you're sure!)

---

### Step 4: Verify on GitHub

Visit: https://github.com/ellizza78/VerzekBackend

You should see:
- ✅ All backend files updated
- ✅ Latest commit message visible
- ✅ Commit timestamp matches your push

---

## 🚀 Deployment to Vultr (After GitHub Sync)

### Option 1: Automated Deployment Script (Recommended)

**From your LOCAL terminal** (not Replit, not Vultr):

```bash
# Download the deployment script from Replit
# (Copy deploy_to_vultr.sh to your local machine)

chmod +x deploy_to_vultr.sh
./deploy_to_vultr.sh
```

This script will:
1. ✅ SSH to Vultr
2. ✅ Pull latest code from GitHub
3. ✅ Install dependencies
4. ✅ Restart backend service
5. ✅ Run health checks

---

### Option 2: Manual Deployment via SSH

```bash
# SSH to Vultr
ssh root@80.240.29.142

# Navigate to backend directory
cd /root/VerzekBackend/backend

# Pull latest code
git pull origin main

# Install dependencies (force upgrade)
pip3 install --upgrade -r requirements.txt

# Restart backend service
sudo systemctl restart verzek-api.service

# Check status
sudo systemctl status verzek-api.service

# Test API
curl http://localhost:8050/api/ping
```

---

## 🔄 Quick Update Commands (For Future Syncs)

**In Replit Shell:**

```bash
cd vultr_production_sync
git add -A
git commit -m "Backend update: <describe your changes>"
git push origin main
```

**On Vultr (after push):**

```bash
cd /root/VerzekBackend/backend
git pull origin main
sudo systemctl restart verzek-api.service
```

---

## 📝 Commit Message Best Practices

Use clear, descriptive commit messages:

**Good Examples:**
- `"Add exchange balance endpoint with auto-refresh support"`
- `"Fix trial timer countdown logic in TrialBanner"`
- `"Update daily reporter with TP1-TP5 breakdown statistics"`
- `"Backend v2.1.1: Multi-TP system + Exchange balance + Trial timer"`

**Bad Examples:**
- `"Update files"` (too vague)
- `"Fix bug"` (what bug?)
- `"Changes"` (what changed?)

---

## 🛡️ Security Reminders

**NEVER commit:**
- ❌ `.env` files (contains secrets)
- ❌ API keys or tokens
- ❌ Database credentials
- ❌ Private SSH keys
- ❌ `__pycache__/` directories

**Always commit:**
- ✅ Source code (`.py` files)
- ✅ `requirements.txt`
- ✅ Configuration templates
- ✅ Documentation

---

## 🆘 Troubleshooting

### Issue: "Remote rejected"

```bash
# Force push (use with caution!)
git push --force origin main
```

### Issue: "Merge conflicts"

```bash
# Pull first, resolve conflicts, then push
git pull --rebase origin main
# Resolve conflicts in files
git add -A
git rebase --continue
git push origin main
```

### Issue: "Authentication failed"

1. Create a GitHub Personal Access Token: https://github.com/settings/tokens
2. Use token as password when prompted
3. Or use SSH keys instead of HTTPS

---

## ✅ Success Checklist

After successful sync and deployment:

- [ ] Code pushed to GitHub successfully
- [ ] Latest commit visible on GitHub repository
- [ ] Vultr backend service restarted without errors
- [ ] `curl http://80.240.29.142:8050/api/ping` returns `{"status":"ok"}`
- [ ] New exchange balance endpoint accessible (requires JWT)
- [ ] Daily reports show TP1-TP5 breakdown
- [ ] Mobile app connects to production API

---

**Next Steps:**
1. Test with mobile app (Expo Go)
2. Build production APK (`eas build`)
3. Complete testing checklist
