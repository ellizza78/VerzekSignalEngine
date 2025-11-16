# 🚀 VerzekAutoTrader - One-Command Auto-Deploy Setup

## ✅ What This Does

Sets up **fully automated deployment** on your Vultr server. After this one-time setup:
- You edit code in Replit
- Push to GitHub
- Server auto-deploys in 2 minutes
- **Zero manual work!**

---

## 🎯 ONE COMMAND - COPY AND PASTE

SSH into your Vultr server (`root@80.240.29.142`) and run this:

```bash
cd /root && rm -rf VerzekBackend 2>/dev/null; git clone https://github.com/ellizza78/VerzekBackend.git && cd /root/VerzekBackend/backend && chmod +x scripts/auto_pull_deploy.sh && cp scripts/verzek-autodeploy.service /etc/systemd/system/ && cp scripts/verzek-autodeploy.timer /etc/systemd/system/ && systemctl daemon-reload && systemctl enable verzek-autodeploy.timer && systemctl start verzek-autodeploy.timer && echo "" && echo "✅ Auto-deploy system installed!" && echo "" && echo "📊 Triggering first deployment now..." && systemctl start verzek-autodeploy.service && sleep 10 && echo "" && tail -20 /var/log/verzek_auto_deploy.log && echo "" && systemctl status verzek_api --no-pager | grep "Active:"
```

---

## ✅ Expected Output

You should see:

```
✅ Auto-deploy system installed!
📊 Triggering first deployment now...

[2025-11-17 00:55:15] === Starting auto-deploy check ===
[2025-11-17 00:55:16] New changes detected!
[2025-11-17 00:55:17] Creating backup...
[2025-11-17 00:55:18] Pulling latest changes...
[2025-11-17 00:55:20] Stopping verzek_api...
[2025-11-17 00:55:22] Starting verzek_api...
[2025-11-17 00:55:27] ✅ SUCCESS: Deployment completed. Service is active.

Active: active (running) since ...
```

---

## 🎉 After Setup - Your New Workflow

From Replit:

```bash
# 1. Make changes in Replit
# 2. Push to GitHub
git add .
git commit -m "Your changes"
git push origin main

# 3. Done! Server deploys automatically in 2 minutes ⏱️
```

---

## 📊 Monitor Deployments

On Vultr server:

```bash
# Watch auto-deployments in real-time
tail -f /var/log/verzek_auto_deploy.log
```

---

## 🔄 What Gets Deployed

The **metadata column bug fix** is ready in your code:

✅ Fixed SQLAlchemy reserved word collision  
✅ Added backwards-compatible @property  
✅ Updated API serializers  
✅ Architect-approved, production-ready  

**The first deployment will fix your API immediately!**

---

## 🆘 If Something Goes Wrong

Check the logs:

```bash
# View deployment logs
tail -50 /var/log/verzek_auto_deploy.log

# Check timer status
systemctl status verzek-autodeploy.timer

# Check API status
systemctl status verzek_api
```

Rollback if needed:

```bash
# List backups
ls -lt /root/VerzekBackend/backups/

# Restore from backup
cd /root/VerzekBackend/backend
cp /root/VerzekBackend/backups/backup_TIMESTAMP/models.py.bak models.py
systemctl restart verzek_api
```

---

## 📖 Full Documentation

See `AUTOMATED_DEPLOYMENT_SETUP.md` for complete details.

---

**Ready!** Copy the command above and paste it into your Vultr SSH session. 🚀
