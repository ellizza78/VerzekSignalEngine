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
