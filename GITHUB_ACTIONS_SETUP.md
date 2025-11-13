# 🤖 GitHub Actions Auto-Deployment Setup
**VerzekAutoTrader - Push-Button Deployment to Vultr**

## Overview
This guide sets up automatic deployment to your Vultr VPS whenever you push code to GitHub. No manual SSH required!

---

## 🎯 How It Works

1. **You push code** to GitHub (backend changes)
2. **GitHub Actions automatically** detects the push
3. **GitHub Actions SSHs** into Vultr VPS (80.240.29.142)
4. **Runs `/root/reset_deploy.sh`** to deploy
5. **Verifies** the deployment succeeded
6. **Notifies** you of success or failure

---

## ⚙️ Setup Instructions

### Step 1: Get Your SSH Private Key

On your Vultr VPS (80.240.29.142), run:
```bash
cat ~/.ssh/id_rsa
```

Or if you use a different key:
```bash
cat ~/.ssh/your_key_name
```

Copy the ENTIRE output (including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----` lines).

### Step 2: Add Secret to GitHub

1. Go to your **backend repository** on GitHub:
   - https://github.com/ellizza78/VerzekBackend

2. Click **Settings** → **Secrets and variables** → **Actions**

3. Click **New repository secret**:

   **Required Secret:**
   - Name: `VULTR_SSH_KEY`
   - Value: (paste the SSH private key from Step 1)

**Note:** The Vultr host IP (80.240.29.142) is hardcoded in the workflow for security and simplicity.

### Step 3: Add GitHub Actions Workflow

The workflow file has already been created at:
```
.github/workflows/deploy-to-vultr.yml
```

You just need to **commit and push it** to GitHub:

```bash
cd ~/workspace/backend

# Add the GitHub Actions workflow and manifests
git add .github/workflows/deploy-to-vultr.yml
git add backend/api_version.txt
git add backend/FILE_MANIFEST.md
git add backend/FILE_MANIFEST_HASHES.txt

# Commit
git commit -m "Add GitHub Actions auto-deployment workflow"

# Push to GitHub
git push origin main
```

### Step 4: Verify It's Working

1. Go to your GitHub repository
2. Click the **Actions** tab
3. You should see a workflow run for your recent push
4. Click on it to see the deployment progress

---

## 🚀 Usage

### Automatic Deployment (Recommended)
Simply push any changes to the `backend/` folder:

```bash
cd ~/workspace/backend

# Make your changes...

git add .
git commit -m "Update backend code"
git push origin main
```

GitHub Actions will automatically:
1. Detect the push
2. SSH into Vultr (80.240.29.142)
3. Run the deployment script
4. Verify the API is responding
5. Show you the results

### Manual Trigger
You can also manually trigger deployment:

1. Go to **Actions** tab in GitHub
2. Click **Deploy Backend to Vultr** workflow
3. Click **Run workflow** button
4. Select branch (main)
5. Click **Run workflow**

---

## 📊 Monitoring Deployments

### View Deployment Logs
1. Go to GitHub repository
2. Click **Actions** tab
3. Click on any workflow run
4. View detailed logs for each step

### Deployment Steps
Each deployment includes:
- ✅ SSH connection test
- ✅ Execute deployment script
- ✅ Verify service status
- ✅ Test API endpoints (/api/ping, /api/health)
- ✅ Deployment summary

---

## 🆘 Troubleshooting

### Deployment Fails
**Check the GitHub Actions logs:**
1. Go to Actions tab
2. Click on the failed workflow
3. Read error messages

**Common issues:**
- SSH key incorrect → Re-add `VULTR_SSH_KEY` secret
- Service not starting → Check Vultr logs: `journalctl -u verzek-api.service -n 50`
- API not responding → Verify Nginx is running: `systemctl status nginx`

### Manual Rollback
If automated deployment fails:

```bash
# SSH into Vultr
ssh root@80.240.29.142

# Check service status
systemctl status verzek-api.service

# View recent logs
journalctl -u verzek-api.service -n 100

# Manually restart
systemctl restart verzek-api.service
```

---

## 🔐 Security Notes

- SSH keys are stored as **GitHub Secrets** (encrypted)
- Only accessible to GitHub Actions runners
- Never exposed in logs or public
- Can be rotated anytime by updating the secret
- Vultr IP is hardcoded (not in secrets) for simplicity

---

## 📝 Workflow Configuration

**Workflow File:** `.github/workflows/deploy-to-vultr.yml`

The workflow triggers on:
- **Push to main branch** - if backend files change
- **Manual trigger** - via Actions tab

Files that trigger deployment:
- Any file in `backend/` folder
- The workflow file itself

---

## ✅ Verification Checklist

After setup, verify:
- [ ] `VULTR_SSH_KEY` secret added to GitHub
- [ ] Workflow file committed and pushed
- [ ] Workflow appears in Actions tab
- [ ] Test deployment by pushing a small change
- [ ] Check workflow runs successfully
- [ ] Verify API responding: https://api.verzekinnovative.com/api/ping

---

## 🎉 Benefits of This Setup

✅ **Push-button deployment** - Just push to GitHub  
✅ **Automatic verification** - Tests API after deployment  
✅ **Detailed logs** - See exactly what happened  
✅ **No manual SSH** - Everything automated  
✅ **Rollback support** - Can revert if needed  
✅ **Secure** - SSH keys encrypted in GitHub  
✅ **Simple** - Only 1 secret required  

---

## 📚 Additional Resources

- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Workflow Syntax:** https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- **SSH Actions:** https://github.com/marketplace/actions/ssh-remote-commands

---

**Status:** ✅ Ready to use  
**Last Updated:** November 13, 2025  
**Maintained By:** Replit Agent
