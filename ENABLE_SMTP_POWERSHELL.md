# 🔧 Enable SMTP AUTH Using PowerShell (Fastest Method)

If you can't find "Authenticated SMTP" in the web interface, use PowerShell:

## ✅ Step-by-Step PowerShell Method

### 1. Open PowerShell as Administrator
- Press **Windows Key + X**
- Click **"Windows PowerShell (Admin)"** or **"Terminal (Admin)"**

### 2. Install Exchange Online Module
```powershell
Install-Module -Name ExchangeOnlineManagement -Force -AllowClobber
```

Press **Y** if prompted to install from PSGallery

### 3. Connect to Exchange Online
```powershell
Connect-ExchangeOnline
```

You'll be prompted to sign in with your Microsoft 365 admin account.

### 4. Enable SMTP AUTH for the Mailbox
```powershell
Set-CASMailbox -Identity support@verzekinnovative.com -SmtpClientAuthenticationDisabled $false
```

### 5. Verify It's Enabled
```powershell
Get-CASMailbox -Identity support@verzekinnovative.com | Format-List SmtpClientAuthenticationDisabled
```

**Expected Output:**
```
SmtpClientAuthenticationDisabled : False
```

(`False` means SMTP AUTH is **enabled** ✅)

### 6. Disconnect
```powershell
Disconnect-ExchangeOnline
```

---

## ⏱️ Wait 30 Minutes

After enabling, **wait 30 minutes** for changes to propagate, then test:

```bash
./test_smtp_now.sh
```

---

## 🎯 This Method is More Reliable

PowerShell directly sets the configuration without relying on the web interface, so it's often faster and more reliable.
