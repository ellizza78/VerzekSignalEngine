# VerzekAutoTrader - Security Architecture

## 🔐 API Key Storage & Protection

### Critical Principle: **API Keys NEVER Touch the Mobile App**

---

## Architecture Overview

```
┌─────────────────┐        HTTPS (Encrypted)        ┌──────────────────┐
│   Mobile App    │ ──────────────────────────────> │  Backend Server  │
│                 │                                  │                  │
│  ❌ NO API KEYS │                                  │  ✅ Encrypted    │
│  ❌ NO SECRETS  │                                  │     Storage      │
└─────────────────┘                                  └──────────────────┘
                                                              │
                                                              ↓
                                                     ┌──────────────────┐
                                                     │  Exchange APIs   │
                                                     │  (Binance, etc)  │
                                                     └──────────────────┘
```

---

## Step-by-Step Flow: How API Keys Are Protected

### 1. **Initial Setup (User Adds Exchange Account)**

```javascript
// MOBILE APP (React Native)
// User enters API keys in the app form

const addExchangeAccount = async (apiKey, apiSecret) => {
  // Keys are sent ONCE via HTTPS (encrypted in transit)
  const response = await fetch('https://api.verzek.app/api/exchange/accounts', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${userToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      exchange: 'binance',
      api_key: apiKey,      // Sent encrypted via HTTPS
      api_secret: apiSecret  // Sent encrypted via HTTPS
    })
  });
  
  // ✅ Mobile app IMMEDIATELY discards the keys
  // ❌ Keys are NEVER stored in mobile app storage
  // ❌ Keys are NEVER in AsyncStorage, SecureStore, or anywhere
};
```

### 2. **Backend Storage (Encrypted at Rest)**

```python
# BACKEND (api_server.py)
@app.route("/api/exchange/accounts", methods=["POST"])
@token_required
def add_exchange_account(current_user_id):
    data = request.json
    
    # Encrypt API credentials before storing
    encrypted_creds = encryption_service.encrypt_api_credentials(
        api_key=data['api_key'],
        api_secret=data['api_secret']
    )
    
    # Store encrypted credentials in database
    exchange_account = {
        'account_id': f"ACC_{user_id}_{timestamp}",
        'exchange': data['exchange'],
        'api_key_encrypted': encrypted_creds['api_key_encrypted'],
        'api_secret_encrypted': encrypted_creds['api_secret_encrypted'],
        'encrypted': True
    }
    
    # Saved to: database/user_exchange_accounts.json
    user.exchange_accounts.append(exchange_account)
    
    # Return only the account_id to mobile app
    return jsonify({
        'account_id': exchange_account['account_id'],
        'exchange': data['exchange']
    })
```

### 3. **Mobile App Stores Only Account ID (Safe)**

```javascript
// MOBILE APP
// After adding exchange account, app only stores:

AsyncStorage.setItem('exchange_accounts', JSON.stringify([
  {
    account_id: 'ACC_user123_1234567890',  // ✅ Safe to store
    exchange: 'binance',                    // ✅ Safe to store
    label: 'My Binance Account'            // ✅ Safe to store
  }
]));

// ❌ NO API KEYS stored
// ❌ NO API SECRETS stored
// ✅ Only metadata that can't be used for trading
```

### 4. **Trading Execution (Keys Retrieved by Backend)**

```javascript
// MOBILE APP
// User wants to open a trade

const openTrade = async (signal) => {
  // App sends INSTRUCTION only (no keys)
  const response = await fetch('https://api.verzek.app/api/trade/execute', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${userToken}` },
    body: JSON.stringify({
      account_id: 'ACC_user123_1234567890',  // Just the account ID
      symbol: 'BTCUSDT',
      side: 'LONG',
      amount: 100
    })
  });
};
```

```python
# BACKEND (api_server.py)
@app.route("/api/trade/execute", methods=["POST"])
@token_required
def execute_trade(current_user_id):
    # Get encrypted credentials from database
    account = user.get_exchange_account(data['account_id'])
    
    # Decrypt API keys (in-memory only, never logged)
    decrypted_creds = encryption_service.decrypt_api_credentials(account)
    
    # Use decrypted keys to execute trade
    exchange = ExchangeAdapter(
        api_key=decrypted_creds['api_key'],
        api_secret=decrypted_creds['api_secret']
    )
    
    result = exchange.create_order(...)
    
    # ✅ Keys used and discarded (not sent to mobile app)
    return jsonify(result)
```

---

## Encryption Details

### Master Encryption Key

```python
# Stored in Environment Variables (Replit Secrets)
ENCRYPTION_MASTER_KEY=VdGhpczEyMzQ1Njc4OTEyMzQ1Njc4OTEyMzQ1Njc4OTEyMzQ=

# OR generated from password + salt (PBKDF2)
ENCRYPTION_PASSWORD=VerzekAutoTrader2025SecureEncryption!@#
ENCRYPTION_SALT=VerzekSalt2025
```

### Encryption Algorithm
- **Algorithm**: AES-128 (Fernet symmetric encryption)
- **Mode**: CBC (Cipher Block Chaining)
- **Key Derivation**: PBKDF2 with 100,000 iterations
- **Encoding**: Base64 (URL-safe)

### Storage Format

```json
// database/user_exchange_accounts.json
{
  "user123": {
    "exchange_accounts": [
      {
        "account_id": "ACC_user123_1234567890",
        "exchange": "binance",
        "api_key_encrypted": "gAAAAABk1x2y...",  // Encrypted
        "api_secret_encrypted": "gAAAAABk1x2z...", // Encrypted
        "encrypted": true,
        "created_at": "2025-10-16T15:30:00Z"
      }
    ]
  }
}
```

---

## Security Layers

### ✅ Layer 1: Transport Security
- **HTTPS/TLS 1.3**: All API communication encrypted in transit
- **Certificate Pinning**: Mobile app validates server certificate
- **JWT Authentication**: Every request requires valid token

### ✅ Layer 2: Storage Encryption
- **At-Rest Encryption**: API keys encrypted using Fernet (AES-128)
- **Master Key Protection**: Stored in environment variables (Replit Secrets)
- **No Plaintext Storage**: Keys never stored unencrypted

### ✅ Layer 3: Access Control
- **User Isolation**: Users can only access their own keys
- **Token Validation**: JWT token verified on every request
- **Role-Based Access**: Admin/User/VIP permissions

### ✅ Layer 4: Mobile App Security
- **Zero Key Storage**: API keys NEVER stored on mobile device
- **Secure Token Storage**: JWT tokens stored in SecureStore (encrypted)
- **Biometric Lock**: Optional FaceID/TouchID for app access

### ✅ Layer 5: Operational Security
- **Audit Logging**: All API key usage logged
- **IP Whitelisting**: Exchange APIs restricted to server IP (dynamic - fetch via /api/system/ip)
- **Key Rotation**: Automated rotation reminders every 90 days
- **Breach Detection**: Monitor for unusual API activity

---

## Attack Scenarios & Mitigations

### ❌ Scenario 1: Mobile App Compromised
**Attack**: Hacker reverse-engineers mobile app
**Impact**: ✅ **ZERO** - No API keys stored in app
**Mitigation**: Keys are backend-only, app can't access them

### ❌ Scenario 2: Database Breach
**Attack**: Attacker gains access to database files
**Impact**: ⚠️ **Minimal** - Keys are encrypted
**Mitigation**: Without encryption master key, data is unreadable

### ❌ Scenario 3: Man-in-the-Middle Attack
**Attack**: Network traffic intercepted
**Impact**: ✅ **ZERO** - HTTPS/TLS encryption protects data
**Mitigation**: Certificate pinning prevents MITM attacks

### ❌ Scenario 4: Server Compromise
**Attack**: Backend server hacked
**Impact**: 🔴 **HIGH** - Decryption possible if master key exposed
**Mitigation**: 
- Master key in Replit Secrets (not in code)
- Hardware Security Module (HSM) for production
- Key rotation policy
- Intrusion detection system

---

## Best Practices for Users

### ✅ Do This:
1. **Use API Key Restrictions** on exchange:
   - IP Whitelist: Get current IP from **Exchange Setup tab** in mobile app (dynamically fetched)
   - Permissions: Trading only (no withdrawals)
   - Expiry: Set 90-day auto-expiration

2. **Enable 2FA** on exchange account

3. **Monitor API Activity** on exchange dashboard

4. **Rotate Keys Regularly** (every 90 days)

### ❌ Never Do This:
1. ❌ Screenshot API keys
2. ❌ Share API keys via email/chat
3. ❌ Store keys in notes app
4. ❌ Enable withdrawal permissions
5. ❌ Disable IP whitelisting

---

## Compliance & Standards

- **OWASP Top 10**: Protected against injection, XSS, broken auth
- **PCI DSS**: Encryption standards for sensitive data
- **GDPR**: User data protection and right to erasure
- **ISO 27001**: Information security management

---

## Emergency Response

### If API Keys Are Compromised:

1. **Immediate Action** (< 1 minute):
   ```bash
   # Revoke keys on exchange dashboard
   # Disable trading in VerzekAutoTrader
   POST /api/safety/kill-switch
   ```

2. **Short-term** (< 5 minutes):
   - Generate new API keys on exchange
   - Update keys in VerzekAutoTrader
   - Enable IP whitelisting

3. **Long-term** (< 24 hours):
   - Audit all recent trades
   - Review account permissions
   - Rotate master encryption key
   - Update security policies

---

## Future Enhancements

### Coming Soon:
1. **Hardware Security Module (HSM)** integration
2. **Multi-signature approvals** for large trades
3. **Biometric authentication** for trade execution
4. **Quantum-resistant encryption** (post-quantum cryptography)
5. **Decentralized key management** (zero-knowledge proofs)

---

**Last Updated**: October 16, 2025  
**Security Auditor**: VerzekAutoTrader Security Team
