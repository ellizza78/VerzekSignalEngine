# GitHub Actions Auto-Deployment to Vultr

## Overview
This project is configured with GitHub Actions to automatically deploy to your Vultr VPS whenever code is pushed to the `main` branch.

## Workflow File
**Location:** `.github/workflows/deploy.yml`

## Required GitHub Secrets
To enable auto-deployment, you need to configure these secrets in your GitHub repository:

### 1. Navigate to Repository Settings
- Go to your GitHub repository
- Click **Settings** → **Secrets and variables** → **Actions**
- Click **New repository secret**

### 2. Add Required Secrets

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `VULTR_IP` | Your Vultr server IP address | `45.76.90.149` |
| `VULTR_USER` | SSH username for Vultr server | `root` or `verzek` |
| `VULTR_SSH_KEY` | Private SSH key for authentication | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `APP_PATH` | Full path to app directory on server | `/opt/VerzekAutoTrader` |

### 3. Generate SSH Key (if needed)

If you don't have an SSH key pair:

```bash
# On your local machine
ssh-keygen -t rsa -b 4096 -C "github-actions@verzek"

# Copy the PRIVATE key (id_rsa) to VULTR_SSH_KEY secret
cat ~/.ssh/id_rsa

# Copy the PUBLIC key to your Vultr server
ssh-copy-id -i ~/.ssh/id_rsa.pub root@YOUR_VULTR_IP
```

## How It Works

### Trigger
The workflow triggers automatically on every push to the `main` branch:

```yaml
on:
  push:
    branches:
      - main
```

### Steps

1. **Checkout Repository**
   - Downloads your latest code from GitHub

2. **Copy Files to Vultr**
   - Uses SCP to transfer all files to your Vultr server
   - Target: `/opt/VerzekAutoTrader` (or your configured path)

3. **Restart Service**
   - Connects via SSH to Vultr server
   - Navigates to app directory
   - Restarts the `verzekbot` systemd service

## Deployment Flow

```
┌─────────────────┐
│  Push to main   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │
│   Triggered     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Checkout Code  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SCP Files to   │
│  Vultr Server   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Restart App    │
│  systemctl      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  App Running    │
│  Updated Code   │
└─────────────────┘
```

## Verify Deployment

After pushing to `main`, you can:

1. **Check GitHub Actions Tab**
   - Go to your repository
   - Click **Actions** tab
   - View the deployment workflow run

2. **Check Vultr Server**
   ```bash
   ssh root@YOUR_VULTR_IP
   cd /opt/VerzekAutoTrader
   systemctl status verzekbot
   ```

3. **View Logs**
   ```bash
   journalctl -u verzekbot -f
   ```

## Systemd Service Setup

The workflow assumes you have a systemd service named `verzekbot` on your Vultr server:

**Create service file:** `/etc/systemd/system/verzekbot.service`

```ini
[Unit]
Description=VerzekAutoTrader Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/VerzekAutoTrader
ExecStart=/usr/bin/python3 run_all_bots.py
Restart=always
RestartSec=10
Environment="PATH=/usr/local/bin:/usr/bin:/bin"

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
systemctl daemon-reload
systemctl enable verzekbot
systemctl start verzekbot
```

## Troubleshooting

### Deployment Fails - SSH Connection Error
**Solution:** Ensure your SSH key is correctly added to GitHub secrets and the public key is in `/root/.ssh/authorized_keys` on Vultr.

### Deployment Succeeds but App Not Running
**Solution:** Check systemd service status and logs:
```bash
systemctl status verzekbot
journalctl -u verzekbot -n 50
```

### Permission Denied
**Solution:** Ensure the SSH user has permissions to access `/opt/VerzekAutoTrader` and restart services:
```bash
chown -R root:root /opt/VerzekAutoTrader
chmod -R 755 /opt/VerzekAutoTrader
```

## Manual Deployment

If you need to deploy manually without GitHub Actions:

```bash
# On your local machine
scp -r ./* root@YOUR_VULTR_IP:/opt/VerzekAutoTrader/

# SSH into server
ssh root@YOUR_VULTR_IP

# Restart service
systemctl restart verzekbot
```

## Security Best Practices

1. ✅ Use SSH keys instead of passwords
2. ✅ Limit SSH access to specific IPs (optional)
3. ✅ Use a dedicated deploy user instead of root (recommended)
4. ✅ Never commit secrets to the repository
5. ✅ Rotate SSH keys periodically
6. ✅ Enable 2FA on GitHub account

## Next Steps

After configuring secrets:
1. Push code to `main` branch
2. Monitor GitHub Actions tab for deployment status
3. Verify app is running on Vultr server
4. Check logs for any issues

Your VerzekAutoTrader will now auto-deploy to Vultr on every push! 🚀
