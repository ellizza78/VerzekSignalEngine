"""
Email Templates with Deep Linking Support
Templates for email verification and password reset using verzek-app:// scheme
"""
import os

# Deep link scheme
DEEP_LINK_SCHEME = os.getenv("DEEP_LINK_SCHEME", "verzek-app://")
WEB_DOMAIN = os.getenv("DOMAIN", "api.verzekinnovative.com")


def get_email_verification_template(verification_token: str, user_email: str) -> dict:
    """
    Get email verification template with deep link
    
    Args:
        verification_token: Email verification token
        user_email: User's email address
    
    Returns:
        Dict with 'subject', 'html', 'text'
    """
    # Deep link (opens in app)
    deep_link = f"{DEEP_LINK_SCHEME}verify-email?token={verification_token}"
    
    # Web fallback link
    web_link = f"https://{WEB_DOMAIN}/api/auth/verify-email?token={verification_token}"
    
    subject = "Verify Your Email - Verzek AutoTrader"
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #14B8A6 0%, #0ea5e9 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0;">Verzek AutoTrader</h1>
    </div>
    
    <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px;">
        <h2 style="color: #1a1a2e;">Welcome! Please Verify Your Email</h2>
        
        <p>Thank you for registering with Verzek AutoTrader!</p>
        
        <p>To activate your account and start using our automated trading platform, please verify your email address by clicking the button below:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{deep_link}" style="background: #14B8A6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                Verify Email Address
            </a>
        </div>
        
        <p style="color: #6b7280; font-size: 14px;">
            If the button doesn't work, copy and paste this link into your browser:<br>
            <a href="{web_link}" style="color: #14B8A6; word-break: break-all;">{web_link}</a>
        </p>
        
        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-top: 20px;">
            <p style="margin: 0; color: #856404;">
                <strong>Important:</strong> This verification link will expire in 24 hours. If you didn't create this account, please ignore this email.
            </p>
        </div>
        
        <p style="margin-top: 30px; color: #6b7280; font-size: 12px;">
            Email: {user_email}<br>
            Sent from Verzek AutoTrader<br>
            © 2025 Verzek Innovative. All rights reserved.
        </p>
    </div>
</body>
</html>
"""
    
    text = f"""
Verzek AutoTrader - Email Verification

Welcome! Thank you for registering with Verzek AutoTrader.

To activate your account and start using our automated trading platform, please verify your email address by visiting this link:

{web_link}

This verification link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Email: {user_email}
© 2025 Verzek Innovative. All rights reserved.
"""
    
    return {
        "subject": subject,
        "html": html,
        "text": text
    }


def get_password_reset_template(reset_token: str, user_email: str) -> dict:
    """
    Get password reset template with deep link
    
    Args:
        reset_token: Password reset token
        user_email: User's email address
    
    Returns:
        Dict with 'subject', 'html', 'text'
    """
    # Deep link (opens in app)
    deep_link = f"{DEEP_LINK_SCHEME}reset-password?token={reset_token}"
    
    # Web fallback link
    web_link = f"https://{WEB_DOMAIN}/api/auth/reset-password?token={reset_token}"
    
    subject = "Reset Your Password - Verzek AutoTrader"
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #14B8A6 0%, #0ea5e9 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0;">Verzek AutoTrader</h1>
    </div>
    
    <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px;">
        <h2 style="color: #1a1a2e;">Password Reset Request</h2>
        
        <p>We received a request to reset the password for your Verzek AutoTrader account.</p>
        
        <p>Click the button below to create a new password:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{deep_link}" style="background: #14B8A6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                Reset Password
            </a>
        </div>
        
        <p style="color: #6b7280; font-size: 14px;">
            If the button doesn't work, copy and paste this link into your browser:<br>
            <a href="{web_link}" style="color: #14B8A6; word-break: break-all;">{web_link}</a>
        </p>
        
        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-top: 20px;">
            <p style="margin: 0; color: #856404;">
                <strong>Important:</strong> This password reset link will expire in 1 hour. If you didn't request this reset, please ignore this email and your password will remain unchanged.
            </p>
        </div>
        
        <div style="background: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin-top: 15px;">
            <p style="margin: 0; color: #721c24;">
                <strong>Security Notice:</strong> Never share your password or reset links with anyone. Verzek AutoTrader will never ask for your password via email.
            </p>
        </div>
        
        <p style="margin-top: 30px; color: #6b7280; font-size: 12px;">
            Email: {user_email}<br>
            Sent from Verzek AutoTrader<br>
            © 2025 Verzek Innovative. All rights reserved.
        </p>
    </div>
</body>
</html>
"""
    
    text = f"""
Verzek AutoTrader - Password Reset Request

We received a request to reset the password for your account.

To create a new password, visit this link:

{web_link}

This password reset link will expire in 1 hour.

If you didn't request this reset, please ignore this email and your password will remain unchanged.

SECURITY NOTICE: Never share your password or reset links with anyone. Verzek AutoTrader will never ask for your password via email.

Email: {user_email}
© 2025 Verzek Innovative. All rights reserved.
"""
    
    return {
        "subject": subject,
        "html": html,
        "text": text
    }


def get_welcome_email_template(user_name: str, user_email: str) -> dict:
    """
    Get welcome email template (sent after successful verification)
    
    Args:
        user_name: User's name
        user_email: User's email address
    
    Returns:
        Dict with 'subject', 'html', 'text'
    """
    subject = "Welcome to Verzek AutoTrader!"
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #14B8A6 0%, #0ea5e9 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0;">Welcome to Verzek AutoTrader!</h1>
    </div>
    
    <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px;">
        <h2 style="color: #1a1a2e;">Hi {user_name},</h2>
        
        <p>Your email has been verified successfully! Welcome to Verzek AutoTrader - your automated trading companion.</p>
        
        <h3 style="color: #14B8A6;">🎯 Next Steps:</h3>
        
        <ol>
            <li><strong>Connect Your Exchange Account</strong> - Link your Binance, Bybit, Phemex, or Kraken account</li>
            <li><strong>Configure Risk Settings</strong> - Set your trading preferences and risk parameters</li>
            <li><strong>Subscribe to a Plan</strong> - Choose TRIAL (4 days free), VIP, or PREMIUM for full autotrading</li>
            <li><strong>Start Receiving Signals</strong> - Get real-time trading signals in your dashboard</li>
        </ol>
        
        <div style="background: #d1fae5; border-left: 4px solid #14B8A6; padding: 15px; margin-top: 20px;">
            <p style="margin: 0; color: #065f46;">
                <strong>🎁 Trial Plan Active!</strong> You have 4 days of free access to test our platform. Upgrade anytime to unlock autotrading features.
            </p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{DEEP_LINK_SCHEME}dashboard" style="background: #14B8A6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                Open App
            </a>
        </div>
        
        <p style="color: #6b7280; font-size: 14px;">
            Need help? Check our <a href="https://{WEB_DOMAIN}/help" style="color: #14B8A6;">Help Center</a> or contact support.
        </p>
        
        <p style="margin-top: 30px; color: #6b7280; font-size: 12px;">
            Email: {user_email}<br>
            © 2025 Verzek Innovative. All rights reserved.
        </p>
    </div>
</body>
</html>
"""
    
    text = f"""
Welcome to Verzek AutoTrader!

Hi {user_name},

Your email has been verified successfully! Welcome to Verzek AutoTrader - your automated trading companion.

Next Steps:
1. Connect Your Exchange Account - Link your Binance, Bybit, Phemex, or Kraken account
2. Configure Risk Settings - Set your trading preferences and risk parameters
3. Subscribe to a Plan - Choose TRIAL (4 days free), VIP, or PREMIUM for full autotrading
4. Start Receiving Signals - Get real-time trading signals in your dashboard

TRIAL PLAN ACTIVE! You have 4 days of free access to test our platform. Upgrade anytime to unlock autotrading features.

Need help? Contact support or visit our Help Center.

Email: {user_email}
© 2025 Verzek Innovative. All rights reserved.
"""
    
    return {
        "subject": subject,
        "html": html,
        "text": text
    }
