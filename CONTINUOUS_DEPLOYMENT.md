# 🚀 VerzekAutoTrader - Continuous Deployment System

## Current Status

✅ **Deployment scripts created**  
✅ **Fix scripts ready**  
⏳ **SSH access needs one-time setup**

---

## 🔧 ONE-TIME SETUP (Required First!)

### Step 1: Enable Passwordless SSH

In your **Replit Shell**, run:

```bash
bash scripts/setup_ssh_access.sh
```

This will:
1. Generate a new SSH key pair
2. Show you the PUBLIC key
3. Ask you to add it to your Vultr server

**Then in your Vultr SSH session** (screenshot shows you're already logged in), run:

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
# Paste the public key from Replit
# Save and exit (Ctrl+X, Y, Enter)
chmod 600 ~/.ssh/authorized_keys
```

Press ENTER in Replit shell to test the connection.

---

### Step 2: Fix the Metadata Column Bug & Deploy

After SSH is working, run this **ONCE** in Replit Shell:

```bash
bash scripts/fix_metadata_and_deploy.sh
```

This will:
- ✅ Fix `metadata` → `meta_data` column in models.py on server
- ✅ Fix `house_signals_routes.py` to use `meta_data`
- ✅ Clear Python cache
- ✅ Restart API
- ✅ Test the endpoint
- ✅ Deploy all files from Replit

Expected output:
```json
{
  "ok": true,
  "signal_id": 123,
  "message": "House signal ingested and position opened"
}
```

---

## 📦 DAILY DEPLOYMENT (After Setup)

Every time you make code changes in Replit, run:

```bash
bash deploy_all.sh
```

This automatically:
1. Uploads `backend/*` → `/root/VerzekBackend/backend/`
2. Uploads `worker.py` → `/root/VerzekBackend/backend/`
3. Uploads `signal_engine/*` → `/root/signal_engine/`
4. Clears Python cache
5. Restarts `verzek_api`, `verzek_worker`, `verzek-signalengine`
6. Runs health check

**No manual SSH needed!** Everything happens automatically.

---

## 🎯 Files Created

| File | Purpose |
|------|---------|
| `deploy_all.sh` | Main deployment script (use daily) |
| `scripts/setup_ssh_access.sh` | SSH key setup (one-time) |
| `scripts/fix_metadata_and_deploy.sh` | Fix metadata bug + deploy (one-time) |
| `CONTINUOUS_DEPLOYMENT.md` | This guide |

---

## 🔍 Troubleshooting

### "Permission denied (publickey,password)"

SSH key not set up correctly:

1. Run `bash scripts/setup_ssh_access.sh` again
2. Copy the **entire** PUBLIC key (starts with `ssh-ed25519`)
3. Add it to `/root/.ssh/authorized_keys` on Vultr
4. Verify permissions: `chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys`

### "Endpoint not found" when testing

API not picking up the new route:

```bash
ssh root@80.240.29.142
cd /root/VerzekBackend/backend
systemctl restart verzek_api
tail -20 logs/api_error.log  # Check for errors
```

### Signal engine not generating signals

```bash
ssh root@80.240.29.142
systemctl status verzek-signalengine
journalctl -u verzek-signalengine -n 50 --no-pager
```

---

## 📊 Deployment Flow

```
┌─────────────────┐
│  Replit (Dev)   │
│                 │
│  1. Edit code   │
│  2. Run deploy  │
└────────┬────────┘
         │
         │ deploy_all.sh
         ↓
┌─────────────────────────────┐
│  Vultr (Production)         │
│  80.240.29.142              │
│                             │
│  ├─ Backend API (8050)      │
│  ├─ Worker (background)     │
│  └─ SignalEngine (4 bots)   │
└─────────────────────────────┘
         │
         │ Signals
         ↓
┌─────────────────┐
│  Mobile App     │
│  (React Native) │
└─────────────────┘
```

---

## ✅ Next Steps

1. **Right now**: Run `bash scripts/setup_ssh_access.sh`
2. **After SSH works**: Run `bash scripts/fix_metadata_and_deploy.sh`
3. **Going forward**: Use `bash deploy_all.sh` anytime

---

## 🎉 Benefits

✅ **No manual file copying** - Everything automated  
✅ **No manual service restarts** - All handled automatically  
✅ **Health checks included** - Verify deployment success  
✅ **Cache clearing** - Python picks up changes immediately  
✅ **Fast deployment** - ~10-15 seconds total  
✅ **Safe** - No production data touched, only code updates

---

**Ready to deploy!** Start with `bash scripts/setup_ssh_access.sh`
