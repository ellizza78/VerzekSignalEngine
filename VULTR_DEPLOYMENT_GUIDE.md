# 🚀 Vultr VPS Deployment Guide - VerzekAutoTrader

Complete guide for deploying documentation updates and code changes to your Vultr VPS (80.240.29.142).

---

## 📋 Prerequisites

Before you begin, ensure you have:
- [x] SSH access to Vultr VPS (root@80.240.29.142)
- [x] Git installed on your local machine
- [x] All secrets configured in Replit Secrets
- [x] Backup of current production system (recommended)

---

## 🔄 Deployment Steps (Recommended Method)

### **Step 1: Connect to Vultr via SSH**

```bash
ssh root@80.240.29.142
```

### **Step 2: Navigate to Project Directory**

```bash
cd /var/www/VerzekAutoTrader
```

### **Step 3: Create Backup (Safety First!)**

```bash
# Create backup with timestamp
cp -r . ../VerzekAutoTrader_backup_$(date +%Y%m%d_%H%M%S)

# Verify backup was created
ls -la ../VerzekAutoTrader_backup*
```

### **Step 4: Create Documentation Directories**

```bash
# Create directory structure
mkdir -p docs/user_guides docs/support
mkdir -p tools

# Verify directories
ls -la docs/
```

### **Step 5: Upload Documentation Files**

You have 2 options:

#### **Option A: Using SCP from Replit/Local Machine**

From your Replit terminal or local machine:

```bash
# Upload docs folder
scp -r docs/ root@80.240.29.142:/var/www/VerzekAutoTrader/

# Upload tools folder
scp -r tools/ root@80.240.29.142:/var/www/VerzekAutoTrader/
```

#### **Option B: Using Git (if your repo is setup)**

On Vultr VPS:

```bash
cd /var/www/VerzekAutoTrader

# Pull latest changes
git pull origin main

# Or clone fresh if needed
# git clone YOUR_REPO_URL .
```

#### **Option C: Manual File Creation (Copy-Paste)**

Create each file manually on Vultr:

**1. Create README:**
```bash
nano docs/README.md
# Paste content from docs/README.md, then Ctrl+X, Y, Enter
```

**2. Create Exchange Setup Guide:**
```bash
nano docs/user_guides/EXCHANGE_SETUP_GUIDES.md
# Paste content, save
```

**3. Create Video Scripts:**
```bash
nano docs/support/VIDEO_TUTORIAL_SCRIPTS.md
# Paste content, save
```

**4. Create Implementation Guide:**
```bash
nano docs/support/BINANCE_CONNECTION_IMPLEMENTATION_GUIDE.md
# Paste content, save
```

**5. Create Summary:**
```bash
nano docs/EXCHANGE_CONNECTION_SUMMARY.md
# Paste content, save
```

**6. Create Test Script:**
```bash
nano tools/test_binance_connection.py
# Paste content, save

# Make executable
chmod +x tools/test_binance_connection.py
```

### **Step 6: Set Correct Permissions**

```bash
# Set permissions for documentation
chmod -R 755 docs/
chmod +x tools/test_binance_connection.py

# Verify
ls -la docs/
ls -la tools/
```

### **Step 7: Test the Installation**

```bash
# Test 1: Verify files exist
ls -la docs/user_guides/
cat docs/README.md

# Test 2: Run connection test script
cd /var/www/VerzekAutoTrader
python3 tools/test_binance_connection.py
# (Press Ctrl+C to exit if you don't have test API keys)
```

### **Step 8: Restart Services (If Needed)**

```bash
# Restart bridge service
systemctl restart verzek-bridge

# Restart API service
systemctl restart verzek-api

# Check both are running
systemctl status verzek-bridge
systemctl status verzek-api
```

### **Step 9: Verify Everything Works**

```bash
# Check logs for errors
journalctl -u verzek-bridge -n 50
journalctl -u verzek-api -n 50

# Test API health
curl http://localhost:5000/api/health

# Test system IP endpoint
curl http://localhost:5000/api/system/ip
```

---

## 🌐 Make Documentation Accessible via Web

### **Quick Setup: Nginx Static Files**

```bash
# Install nginx if not already installed
apt update
apt install nginx python3-pip -y

# Install markdown converter
pip3 install markdown

# Create web-accessible docs directory
mkdir -p /var/www/html/guides

# Convert markdown to HTML
python3 << 'EOF'
import markdown

# Read markdown file
with open('/var/www/VerzekAutoTrader/docs/user_guides/EXCHANGE_SETUP_GUIDES.md', 'r') as f:
    content = f.read()

# Convert to HTML
html = markdown.markdown(content, extensions=['tables', 'fenced_code', 'nl2br'])

# Create styled HTML page
html_page = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exchange Setup Guide - VerzekAutoTrader</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.8;
            color: #e8e8e8;
            background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%);
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #1a1a2e;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        h1 {{ color: #F9C74F; margin-bottom: 30px; font-size: 2.5em; }}
        h2 {{ color: #1B9AAA; margin-top: 40px; margin-bottom: 20px; border-bottom: 2px solid #1B9AAA; padding-bottom: 10px; }}
        h3 {{ color: #F9C74F; margin-top: 30px; margin-bottom: 15px; }}
        h4 {{ color: #1B9AAA; margin-top: 20px; margin-bottom: 10px; }}
        p {{ margin-bottom: 16px; }}
        code {{
            background: #0A4A5C;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: 'Monaco', 'Courier New', monospace;
            color: #F9C74F;
            font-size: 0.9em;
        }}
        pre {{
            background: #0A4A5C;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
            border-left: 4px solid #1B9AAA;
        }}
        pre code {{ background: none; padding: 0; color: #e8e8e8; }}
        table {{ 
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            background: #0A4A5C;
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            border: 1px solid #1B9AAA;
            padding: 12px 15px;
            text-align: left;
        }}
        th {{
            background: #1B9AAA;
            color: #0A4A5C;
            font-weight: 700;
        }}
        ul, ol {{ margin-left: 30px; margin-bottom: 16px; }}
        li {{ margin-bottom: 8px; }}
        strong {{ color: #F9C74F; }}
        em {{ color: #1B9AAA; font-style: italic; }}
        a {{ color: #1B9AAA; text-decoration: none; border-bottom: 1px dotted #1B9AAA; }}
        a:hover {{ color: #F9C74F; border-bottom-color: #F9C74F; }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 2px solid #1B9AAA;
        }}
        .logo {{ font-size: 4em; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">📚</div>
            <h1>Exchange Setup Guides</h1>
            <p style="color: #1B9AAA; font-size: 1.1em;">VerzekAutoTrader - Complete Connection Instructions</p>
        </div>
        {html}
    </div>
</body>
</html>'''

# Write HTML file
with open('/var/www/html/guides/exchange-setup.html', 'w') as f:
    f.write(html_page)

print("✅ HTML guide created successfully!")
EOF

# Set permissions
chmod 644 /var/www/html/guides/exchange-setup.html

# Test it
curl http://localhost/guides/exchange-setup.html | head -20
```

**Now accessible at:**
- `http://80.240.29.142/guides/exchange-setup.html`
- Or with your domain: `https://yourdomain.com/guides/exchange-setup.html`

---

## 🧪 Testing Checklist

After deployment, verify:

- [ ] **Documentation Files Exist**
  ```bash
  ls -la /var/www/VerzekAutoTrader/docs/
  ls -la /var/www/VerzekAutoTrader/tools/
  ```

- [ ] **Test Script Works**
  ```bash
  cd /var/www/VerzekAutoTrader
  python3 tools/test_binance_connection.py
  ```

- [ ] **Services Running**
  ```bash
  systemctl status verzek-bridge
  systemctl status verzek-api
  ```

- [ ] **No Errors in Logs**
  ```bash
  journalctl -u verzek-bridge -n 20 --no-pager
  journalctl -u verzek-api -n 20 --no-pager
  ```

- [ ] **API Responding**
  ```bash
  curl http://localhost:5000/api/health
  curl http://localhost:5000/api/system/ip
  ```

- [ ] **Web Guide Accessible**
  ```bash
  curl http://localhost/guides/exchange-setup.html
  ```

---

## 🔄 Quick Update Commands

For future updates, use these quick commands:

```bash
# Connect to Vultr
ssh root@80.240.29.142

# Navigate to project
cd /var/www/VerzekAutoTrader

# Backup current version
cp -r . ../backup_$(date +%Y%m%d_%H%M%S)

# Pull latest changes (if using Git)
git pull

# Or upload specific files via SCP from local/Replit:
# scp FILE root@80.240.29.142:/var/www/VerzekAutoTrader/

# Restart services
systemctl restart verzek-bridge verzek-api

# Check status
systemctl status verzek-bridge verzek-api

# View logs
journalctl -u verzek-bridge -f
```

---

## 🆘 Rollback (If Something Goes Wrong)

```bash
# Stop services
systemctl stop verzek-bridge verzek-api

# Restore from backup
cd /var/www
rm -rf VerzekAutoTrader
mv VerzekAutoTrader_backup_TIMESTAMP VerzekAutoTrader

# Restart services
systemctl start verzek-bridge verzek-api

# Verify
systemctl status verzek-bridge verzek-api
```

---

## 📁 Expected File Structure After Deployment

```
/var/www/VerzekAutoTrader/
├── api_server.py
├── bridge.py
├── exchanges/
│   ├── binance_client.py
│   ├── bybit_client.py
│   ├── phemex_client.py
│   └── kraken_client.py
├── docs/                              # ← NEW
│   ├── README.md                      # ← NEW
│   ├── EXCHANGE_CONNECTION_SUMMARY.md # ← NEW
│   ├── user_guides/                   # ← NEW
│   │   └── EXCHANGE_SETUP_GUIDES.md   # ← NEW
│   └── support/                       # ← NEW
│       ├── VIDEO_TUTORIAL_SCRIPTS.md  # ← NEW
│       └── BINANCE_CONNECTION_IMPLEMENTATION_GUIDE.md  # ← NEW
└── tools/                             # ← NEW
    └── test_binance_connection.py     # ← NEW
```

---

## ✅ Deployment Complete!

Once you've completed all steps:

1. ✅ Documentation is accessible on your server
2. ✅ Test tools are ready for troubleshooting
3. ✅ Services are running normally
4. ✅ No code changes needed (documentation only)

**Next steps:**
- Share the guide URL with users
- Record video tutorials using the scripts
- Monitor user feedback
- Update mobile app with help links (optional)

---

**Need Help?** Run these diagnostic commands:

```bash
# Full system check
systemctl status verzek-bridge verzek-api
journalctl -u verzek-bridge -n 50
journalctl -u verzek-api -n 50
curl http://localhost:5000/api/health
ls -la /var/www/VerzekAutoTrader/docs/
```

🚀 **You're all set!**
