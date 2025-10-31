# 🚀 VERZEK DYNAMIC UPDATE - DEPLOYMENT GUIDE

## Quick Start

### Step 1: Deploy Backend (Vultr)

```bash
# Copy VULTR_DEPLOY_DYNAMIC_CONFIG.sh to your Vultr server
scp VULTR_DEPLOY_DYNAMIC_CONFIG.sh root@80.240.29.142:~/

# SSH and run deployment
ssh root@80.240.29.142
bash VULTR_DEPLOY_DYNAMIC_CONFIG.sh

# Verify deployment
curl http://localhost:5000/api/app-config | jq
```

### Step 2: Test Remote Config

```bash
# From anywhere
curl https://verzek-auto-trader.replit.app/api/app-config | jq .featureFlags
```

### Step 3: Push OTA Update

```bash
# From Replit shell
cd mobile_app/VerzekApp
./push_update.sh "Added dynamic config support"
```

---

## 📋 Complete Feature List

### Backend Features ✅
- `/api/app-config` endpoint (public, 5min cache)
- `/api/admin/config` endpoint (admin only)
- SQLite config storage with versioning
- CLI management tool
- Config update notifier

### Mobile App Features ✅
- Remote config context provider
- Auto-refresh every 5 minutes
- Feature flag system
- Force update modal
- OTA update support
- Offline caching

---

## 🛠️ Management Commands

```bash
# View all configs
python3 /root/manage_config.py view

# Toggle features
python3 /root/manage_config.py feature autoTrade on
python3 /root/manage_config.py feature emailVerification off
```

---

## 📱 Usage in Mobile App

```javascript
import { useRemoteConfig } from '../context/RemoteConfigContext';

function MyComponent() {
  const { isFeatureEnabled, getMessage, getTradingLimit } = useRemoteConfig();
  
  if (isFeatureEnabled('aiAssistant')) {
    return <AIAssistant />;
  }
  
  return <View>...</View>;
}
```

---

**Ready to deploy! See mobile_app/VerzekApp/DYNAMIC_UPDATES.md for complete documentation.**
