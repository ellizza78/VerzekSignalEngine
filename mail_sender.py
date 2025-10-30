#!/usr/bin/env python3
"""
Microsoft 365 Email Sender - Drop-in Utility
---------------------------------------------
Sends emails via Microsoft 365 SMTP (smtp.office365.com)
Used for verification codes, password resets, and support emails.
"""

import os
import smtplib
import ssl
import re
from email.message import EmailMessage

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.office365.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "support@verzekinnovative.com")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER)
APP_NAME = os.getenv("APP_NAME", "Verzek Auto Trader")

def send_email(to, subject, html_body, text_body=None):
    """
    Send an email via Microsoft 365 SMTP
    
    Args:
        to: Email address or list of addresses
        subject: Email subject (APP_NAME will be prepended)
        html_body: HTML content
        text_body: Plain text fallback (auto-generated if not provided)
    
    Returns:
        True if sent successfully
    
    Raises:
        Exception if SMTP credentials are missing or sending fails
    """
    if not EMAIL_USER or not EMAIL_PASS:
        raise ValueError("EMAIL_USER and EMAIL_PASS environment variables are required")
    
    # Generate text fallback if not provided
    if not text_body:
        text_body = re.sub("<[^<]+?>", "", html_body)
    
    # Create message
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = to if isinstance(to, str) else ", ".join(to)
    msg["Subject"] = f"{APP_NAME}: {subject}"
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")
    
    # Send via SMTP with TLS
    context = ssl.create_default_context()
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
    
    return True


def send_verification_email(to, code, user_name=None):
    """
    Send email verification code
    
    Args:
        to: User's email address
        code: 6-digit verification code
        user_name: Optional user name for personalization
    """
    greeting = f"Hi {user_name}," if user_name else "Hello,"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #0A4A5C, #1B9AAA); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .code {{ background: #F9C74F; color: #0A4A5C; font-size: 32px; font-weight: bold; padding: 15px; text-align: center; border-radius: 6px; letter-spacing: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Email Verification</h1>
            </div>
            <div class="content">
                <p>{greeting}</p>
                <p>Thank you for signing up with <strong>Verzek Auto Trader</strong>!</p>
                <p>Your verification code is:</p>
                <div class="code">{code}</div>
                <p>This code will expire in <strong>10 minutes</strong>.</p>
                <p>If you didn't request this code, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>© 2025 Verzek Innovative. All rights reserved.</p>
                <p>support@verzekinnovative.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to, "Email Verification", html)


def send_password_reset_email(to, code, user_name=None):
    """
    Send password reset code
    
    Args:
        to: User's email address
        code: 6-digit reset code
        user_name: Optional user name for personalization
    """
    greeting = f"Hi {user_name}," if user_name else "Hello,"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #0A4A5C, #1B9AAA); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .code {{ background: #F9C74F; color: #0A4A5C; font-size: 32px; font-weight: bold; padding: 15px; text-align: center; border-radius: 6px; letter-spacing: 5px; margin: 20px 0; }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔑 Password Reset</h1>
            </div>
            <div class="content">
                <p>{greeting}</p>
                <p>We received a request to reset your password for your <strong>Verzek Auto Trader</strong> account.</p>
                <p>Your password reset code is:</p>
                <div class="code">{code}</div>
                <p>This code will expire in <strong>10 minutes</strong>.</p>
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong> If you didn't request a password reset, please contact our support team immediately at support@verzekinnovative.com
                </div>
            </div>
            <div class="footer">
                <p>© 2025 Verzek Innovative. All rights reserved.</p>
                <p>support@verzekinnovative.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to, "Password Reset Request", html)


def send_welcome_email(to, user_name):
    """
    Send welcome email after successful registration
    
    Args:
        to: User's email address
        user_name: User's name
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #0A4A5C, #1B9AAA); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .features {{ background: white; padding: 20px; margin: 20px 0; border-radius: 6px; }}
            .feature {{ margin: 15px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Welcome to Verzek Auto Trader!</h1>
            </div>
            <div class="content">
                <p>Hi {user_name},</p>
                <p>Welcome to <strong>Verzek Auto Trader</strong> - your automated trading platform!</p>
                <div class="features">
                    <div class="feature">✅ <strong>Real-time Telegram signals</strong> - Get trading signals instantly</div>
                    <div class="feature">✅ <strong>DCA automation</strong> - Dollar Cost Averaging with smart entry</div>
                    <div class="feature">✅ <strong>Multi-exchange support</strong> - Trade on Binance, Bybit, Phemex, Kraken</div>
                    <div class="feature">✅ <strong>Risk management</strong> - Auto stop-loss and take-profit</div>
                </div>
                <p>Get started by connecting your exchange account and enabling auto-trading in the app settings.</p>
                <p>Need help? Contact us at <strong>support@verzekinnovative.com</strong></p>
            </div>
            <div class="footer">
                <p>© 2025 Verzek Innovative. All rights reserved.</p>
                <p>support@verzekinnovative.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to, "Welcome to Verzek Auto Trader", html)


def send_vip_welcome_email(to, user_name, user_id):
    """
    Send VIP subscription welcome email with signal access instructions
    
    Args:
        to: User's email address
        user_name: User's name
        user_id: User's ID for Telegram group verification
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #0A4A5C, #1B9AAA); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .vip-badge {{ background: #F9C74F; color: #0A4A5C; padding: 10px 20px; border-radius: 20px; display: inline-block; font-weight: bold; margin-top: 10px; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .option-box {{ background: white; padding: 25px; margin: 20px 0; border-radius: 8px; border-left: 5px solid #1B9AAA; }}
            .option-title {{ color: #0A4A5C; font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
            .step {{ background: #f0f0f0; padding: 10px 15px; margin: 10px 0; border-radius: 4px; }}
            .user-id {{ background: #F9C74F; color: #0A4A5C; padding: 10px; text-align: center; font-size: 20px; font-weight: bold; border-radius: 6px; margin: 15px 0; letter-spacing: 2px; }}
            .highlight {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            .btn {{ background: #1B9AAA; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Welcome to VIP!</h1>
                <div class="vip-badge">VIP MEMBER</div>
            </div>
            <div class="content">
                <p>Hi {user_name},</p>
                <p><strong>Congratulations!</strong> Your VIP subscription is now active. You now have exclusive access to our premium trading signals!</p>
                
                <h2 style="color: #0A4A5C; margin-top: 30px;">🔔 How to Receive Signals:</h2>
                
                <div class="option-box">
                    <div class="option-title">📱 OPTION 1: Mobile App (Automatic - Already Active!)</div>
                    <p>Your VIP access has been automatically activated in the mobile app.</p>
                    <div class="step">1️⃣ Open the Verzek Auto Trader app</div>
                    <div class="step">2️⃣ Tap the "Signals" tab at the bottom</div>
                    <div class="step">3️⃣ View all premium trading signals in real-time!</div>
                    <p style="color: #28a745; font-weight: bold; margin-top: 15px;">✅ Already activated - no action needed!</p>
                </div>
                
                <div class="option-box">
                    <div class="option-title">💬 OPTION 2: VIP Telegram Group (Manual Setup)</div>
                    <p>Get signals directly on Telegram with real-time notifications.</p>
                    <div class="step">1️⃣ Open Telegram app</div>
                    <div class="step">2️⃣ Search for <strong>@VerzekSupport</strong></div>
                    <div class="step">3️⃣ Send this message:</div>
                    <div class="highlight">
                        "Hi! Please add me to the VIP Telegram group.<br>
                        <strong>User ID: {user_id}</strong><br>
                        <strong>Email: {to}</strong>"
                    </div>
                    <div class="step">4️⃣ We'll add you within 24 hours</div>
                    
                    <p style="margin-top: 15px;"><strong>Your User ID for verification:</strong></p>
                    <div class="user-id">{user_id}</div>
                    <p style="font-size: 12px; color: #666;">Keep this ID safe - you'll need it to verify your VIP status</p>
                </div>
                
                <h2 style="color: #0A4A5C; margin-top: 30px;">🎯 What's Included in VIP:</h2>
                <div class="option-box">
                    <div class="step">✅ Premium trading signals (buy/sell alerts)</div>
                    <div class="step">✅ Entry points and target prices</div>
                    <div class="step">✅ Stop-loss recommendations</div>
                    <div class="step">✅ Real-time market analysis</div>
                    <div class="step">✅ Priority support via @VerzekSupport</div>
                </div>
                
                <div class="highlight">
                    <strong>💡 Pro Tip:</strong> Use both methods! View signals in the app while you're actively trading, and get Telegram notifications when you're away from the app.
                </div>
                
                <p style="margin-top: 30px;">Need help or have questions? Contact our support team at:</p>
                <p><strong>📧 Email:</strong> support@verzekinnovative.com</p>
                <p><strong>💬 Telegram:</strong> @VerzekSupport</p>
                
                <p style="margin-top: 30px;">Happy trading!</p>
                <p><strong>The Verzek Team</strong></p>
            </div>
            <div class="footer">
                <p>© 2025 Verzek Innovative. All rights reserved.</p>
                <p>This email was sent because you subscribed to VIP ($50/month)</p>
                <p>verzekinnovativesolutionsltd@gmail.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to, "Welcome to VIP - Your Signal Access Guide", html)


def send_premium_welcome_email(to, user_name, user_id):
    """
    Send PREMIUM subscription welcome email with auto-trading access instructions
    
    Args:
        to: User's email address
        user_name: User's name
        user_id: User's ID for verification
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #0A4A5C, #1B9AAA); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .premium-badge {{ background: linear-gradient(135deg, #FFD700, #FFA500); color: #000; padding: 10px 20px; border-radius: 20px; display: inline-block; font-weight: bold; margin-top: 10px; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .option-box {{ background: white; padding: 25px; margin: 20px 0; border-radius: 8px; border-left: 5px solid #FFD700; }}
            .option-title {{ color: #0A4A5C; font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
            .step {{ background: #f0f0f0; padding: 10px 15px; margin: 10px 0; border-radius: 4px; }}
            .user-id {{ background: #F9C74F; color: #0A4A5C; padding: 10px; text-align: center; font-size: 20px; font-weight: bold; border-radius: 6px; margin: 15px 0; letter-spacing: 2px; }}
            .highlight {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Welcome to PREMIUM!</h1>
                <div class="premium-badge">⭐ PREMIUM MEMBER ⭐</div>
            </div>
            <div class="content">
                <p>Hi {user_name},</p>
                <p><strong>Congratulations!</strong> You're now a PREMIUM member with full access to automated DCA trading!</p>
                
                <h2 style="color: #0A4A5C; margin-top: 30px;">🎯 What's Included in PREMIUM:</h2>
                <div class="option-box">
                    <div class="step">✅ All VIP features (premium signals)</div>
                    <div class="step">✅ Automated DCA trading</div>
                    <div class="step">✅ Progressive take-profit</div>
                    <div class="step">✅ Auto stop-loss protection</div>
                    <div class="step">✅ Multi-exchange support (Binance, Bybit, Phemex, Kraken)</div>
                    <div class="step">✅ Up to 50 concurrent positions</div>
                    <div class="step">✅ 24/7 automated trading</div>
                    <div class="step">✅ VIP Telegram group access</div>
                    <div class="step">✅ Priority support</div>
                </div>
                
                <h2 style="color: #0A4A5C; margin-top: 30px;">📱 Getting Started:</h2>
                <div class="option-box">
                    <div class="step">1️⃣ Connect your exchange API keys in app Settings</div>
                    <div class="step">2️⃣ Configure your DCA strategy and risk settings</div>
                    <div class="step">3️⃣ Enable auto-trading in the app</div>
                    <div class="step">4️⃣ Sit back and let the bot trade for you!</div>
                </div>
                
                <h2 style="color: #0A4A5C; margin-top: 30px;">💬 Join VIP Telegram Group:</h2>
                <div class="highlight">
                    <p>Message <strong>@VerzekSupport</strong> on Telegram with:</p>
                    <p>"Hi! Please add me to the VIP Telegram group.<br>
                    <strong>User ID: {user_id}</strong><br>
                    <strong>Email: {to}</strong>"</p>
                    <div class="user-id">{user_id}</div>
                </div>
                
                <p style="margin-top: 30px;"><strong>Need help?</strong> Our team is here for you:</p>
                <p><strong>📧 Email:</strong> support@verzekinnovative.com</p>
                <p><strong>💬 Telegram:</strong> @VerzekSupport</p>
                
                <p style="margin-top: 30px;">Happy automated trading!</p>
                <p><strong>The Verzek Team</strong></p>
            </div>
            <div class="footer">
                <p>© 2025 Verzek Innovative. All rights reserved.</p>
                <p>This email was sent because you subscribed to PREMIUM ($120/month)</p>
                <p>verzekinnovativesolutionsltd@gmail.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to, "Welcome to PREMIUM - Full Auto-Trading Access", html)
