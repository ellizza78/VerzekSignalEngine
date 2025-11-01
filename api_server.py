"""
api_server.py
-------------
Flask REST API layer for VerzekAutoTrader.
Allows mobile app or external dashboard to fetch real-time data.
"""

from flask import Flask, jsonify, request, render_template
from utils.logger import log_event
from trade_executor import get_all_trades
from modules import UserManager, PositionTracker, SafetyManager
from modules.auth import (
    hash_password, verify_password, 
    create_access_token, create_refresh_token,
    token_required, refresh_token_required
)
from modules.subscription_security import subscription_security
from modules.payment_system import payment_system
from flask_simple_captcha import CAPTCHA
import time
import os
import re
from datetime import datetime, timedelta

# Phase 1 Security Features
from modules.rate_limiter import init_rate_limiter
from modules.two_factor_auth import two_factor_auth
from modules.backup_system import backup_system
from modules.tronscan_client import tronscan_client
from modules.audit_logger import audit_logger, AuditEventType
from modules.admin_dashboard import admin_dashboard
from modules.push_notifications import push_service
from modules.analytics_engine import analytics_engine
from modules.advanced_orders import advanced_order_manager
from modules.webhook_handler import webhook_handler
from modules.email_service import email_service
from services.admin_notifications import admin_notifier

# Phase 4 Advanced Features
from modules.portfolio_rebalancer import PortfolioRebalancer
from modules.advanced_analytics import AdvancedAnalytics
from modules.social_trading import SocialTradingManager
from modules.custom_indicators import CustomIndicatorEngine
from modules.backtesting_engine import BacktestingEngine

# Phase 5 Advanced Features
from modules.ai_trade_assistant import AITradeAssistant
from modules.multi_timeframe_analysis import MultiTimeframeAnalysis
from modules.smart_order_routing import SmartOrderRouter
from modules.social_features import SocialFeaturesManager
from modules.advanced_charting import AdvancedChartingSystem
from modules.auto_optimization import AutoOptimizationEngine
from modules.ai_risk_scoring import AIRiskScoringSystem
from modules.trading_journal import TradingJournal
from telegram import Update, Bot
import json as json_module

app = Flask(__name__)

# Telegram Bot instance (will be set by broadcast_bot)
telegram_bot_instance = None
telegram_message_handler = None

# Configure CAPTCHA
CAPTCHA_CONFIG = {
    'SECRET_CAPTCHA_KEY': os.environ.get('CAPTCHA_SECRET_KEY'),
    'CAPTCHA_LENGTH': 6,
    'CAPTCHA_DIGITS': True,
    'EXPIRE_SECONDS': 600,
    'CAPTCHA_IMG_FORMAT': 'JPEG'
}

SIMPLE_CAPTCHA = CAPTCHA(config=CAPTCHA_CONFIG)
app = SIMPLE_CAPTCHA.init_app(app)

# Initialize rate limiter
limiter = init_rate_limiter(app)

# Initialize managers
user_manager = UserManager()
position_tracker = PositionTracker()
safety_manager = SafetyManager()

# Phase 4 managers
portfolio_rebalancer = PortfolioRebalancer(position_tracker)
advanced_analytics = AdvancedAnalytics(position_tracker)
social_trading = SocialTradingManager(position_tracker)
custom_indicators = CustomIndicatorEngine(position_tracker)
backtesting_engine = BacktestingEngine(position_tracker)

# Phase 5 managers
ai_assistant = AITradeAssistant()
mtf_analyzer = MultiTimeframeAnalysis()
order_router = SmartOrderRouter()
social_features = SocialFeaturesManager()
chart_system = AdvancedChartingSystem()
auto_optimizer = AutoOptimizationEngine()
risk_scorer = AIRiskScoringSystem()
trading_journal = TradingJournal()

# ============================
# APP STATUS
# ============================

start_time = time.time()

# ============================
# HOME PAGE
# ============================

@app.route("/")
def home():
    uptime = round(time.time() - start_time, 2)
    return jsonify({
        "name": "VerzekAutoTrader API",
        "version": "1.3-session-isolation",
        "status": "online",
        "uptime_seconds": uptime,
        "description": "Automated cryptocurrency trading bot API",
        "endpoints": {
            "/": "API documentation (this page)",
            "/api/status": "Get bot status and uptime",
            "/api/test": "Test API connection",
            "/api/trades": "Get all executed trades",
            "/api/latest": "Get latest trade",
            "/api/users": "User management (GET/POST)",
            "/api/users/<user_id>": "Single user (GET/PUT/DELETE)",
            "/api/users/<user_id>/general": "General mode settings (GET/PUT)",
            "/api/users/<user_id>/risk": "Capital & risk settings (GET/PUT)",
            "/api/users/<user_id>/strategy": "Strategy parameters (GET/PUT)",
            "/api/users/<user_id>/dca": "DCA margin call settings (GET/PUT)",
            "/api/users/<user_id>/exchanges": "Exchange accounts (GET/POST)",
            "/api/users/<user_id>/subscription": "Subscription management (GET/POST)",
            "/api/positions": "All positions (GET)",
            "/api/positions/<user_id>": "User positions (GET)",
            "/api/safety/status": "Safety system status (GET)",
            "/api/safety/killswitch": "Kill switch control (POST)",
            "/api/safety/pause": "Pause trading (POST)",
            "/api/safety/resume": "Resume trading (POST)"
        },
        "message": "VerzekAutoTrader is running smoothly! ðŸš€"
    })


@app.route("/api/status")
def get_status():
    uptime = round(time.time() - start_time, 2)
    return jsonify({
        "bot": "VerzekAutoTrader",
        "status": "online",
        "uptime_seconds": uptime,
        "message": "Bot is running smoothly ðŸš€"
    })


@app.route("/api/health")
def health_check():
    """Health check endpoint for Nginx and monitoring"""
    return jsonify({
        "status": "ok",
        "message": "Verzek Auto Trader API running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.3-session-isolation"
    }), 200


# ============================
# FETCH TRADES
# ============================

@app.route("/api/trades")
def fetch_trades():
    trades = get_all_trades()
    return jsonify({
        "count": len(trades),
        "trades": trades
    })


# ============================
# FETCH LATEST TRADE
# ============================

@app.route("/api/latest")
def latest_trade():
    trades = get_all_trades()
    if not trades:
        return jsonify({"message": "No trades found yet."})
    return jsonify(trades[-1])


# ============================
# TEST CONNECTION
# ============================

@app.route("/api/test")
def test():
    return jsonify({
        "status": "success",
        "message": "ðŸ“¡ Flask API connection successful!"
    })


@app.route("/api/test/email", methods=["POST"])
@token_required
def test_email(current_user_id):
    """Test SMTP email connection by sending a test email"""
    data = request.json
    test_email_address = data.get("email")

    if not test_email_address:
        return jsonify({"error": "Email address is required"}), 400

    subject = "Verzek SMTP Connection Test"
    html = """
    <h3>SMTP Connected Successfully ðŸŽ‰</h3>
    <p>Emails from Verzek Innovative Solutions are now verified and secure.</p>
    <p>Your VerzekAutoTrader platform is ready to send:</p>
    <ul>
        <li>âœ… Email verifications</li>
        <li>âœ… Password resets</li>
        <li>âœ… Support notifications</li>
        <li>âœ… Trading alerts</li>
    </ul>
    """

    result = email_service.send_email(test_email_address, subject, html)

    return jsonify(result)


@app.route("/api/system/ip")
def get_server_ip():
    """Get server IP for exchange API whitelisting - Returns Vultr static IPs"""
    # âœ… Vultr Infrastructure Static IPs
    static_ips = [
        "45.76.90.149",      # Frankfurt (Europe) - Hub
        "209.222.24.189",    # New Jersey (US) - Node 1
        "45.76.158.152",     # Singapore (Asia) - Node 2
        "207.148.80.196"     # Sydney (Australia) - Node 3
    ]

    server_ip = ','.join(static_ips)  # Comma-separated for easy copying

    return jsonify({
        "server_ip": server_ip,
        "ip_list": static_ips,  # Array format for mobile app
        "instructions": {
            "step_1": "Copy the IP address above",
            "step_2": "Go to your exchange (Binance, Bybit, etc.)",
            "step_3": "When creating API keys, select 'Restrict access to trusted IPs only'",
            "step_4": "Add this IP address to the whitelist",
            "step_5": "Enable 'Enable Futures' permission",
            "step_6": "Enable 'Enable Reading' permission",
            "important": "âš ï¸ ALWAYS use ISOLATED MARGIN on your exchange, NOT Cross Margin"
        },
        "supported_exchanges": [
            {
                "name": "Binance",
                "api_url": "https://www.binance.com/en/my/settings/api-management"
            },
            {
                "name": "Bybit",
                "api_url": "https://www.bybit.com/app/user/api-management"
            },
            {
                "name": "Phemex",
                "api_url": "https://phemex.com/account/api-management"
            },
            {
                "name": "Coinexx",
                "api_url": "https://www.coinexx.com/api"
            }
        ]
    })


# ============================
# CAPTCHA ENDPOINTS
# ============================

@app.route("/api/captcha/generate", methods=["GET"])
def generate_captcha():
    """Generate a new CAPTCHA challenge"""
    captcha_dict = SIMPLE_CAPTCHA.create()
    return jsonify({
        "captcha_hash": captcha_dict['captcha_hash'],
        "captcha_image": captcha_dict['captcha_base64']
    })


@app.route("/api/captcha/verify", methods=["POST"])
def verify_captcha():
    """Verify CAPTCHA (standalone endpoint for testing)"""
    data = request.json
    c_hash = data.get('captcha_hash')
    c_text = data.get('captcha_text')

    if SIMPLE_CAPTCHA.verify(c_text, c_hash):
        return jsonify({'status': 'success', 'message': 'CAPTCHA verified'}), 200
    else:
        return jsonify({'status': 'failed', 'error': 'Invalid CAPTCHA'}), 400


# ============================
# AUTHENTICATION
# ============================

@app.route("/api/auth/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    """Register a new user with rate limiting"""
    data = request.json

    email = data.get("email", "").strip().lower()
    password = data.get("password")
    full_name = data.get("full_name", "")
    username = data.get("username", "").strip()

    # Validation
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Username validation (alphanumeric, 3-20 chars)
    if username:
        if not re.match(r'^[a-zA-Z0-9]{3,20}$', username):
            return jsonify({"error": "Username must be 3-20 characters (letters and numbers only)"}), 400

    # Email format validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return jsonify({"error": "Invalid email format"}), 400

    # Password strength
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # Check if user already exists
    users = user_manager.get_all_users()
    for user in users:
        if user.email == email:
            return jsonify({"error": "User with this email already exists"}), 409

    # Create user with email as user_id
    user_id = email.replace("@", "_").replace(".", "_")
    user = user_manager.create_user(user_id)

    # Set user credentials
    user.email = email
    user.full_name = full_name
    user.username = username or email.split('@')[0]  # Use username or fallback to email prefix
    user.password_hash = hash_password(password)
    
    # ✅ AUTOMATIC 4-DAY TRIAL on registration
    user.plan = "trial"
    user.plan_started_at = datetime.now().isoformat()
    user.plan_expires_at = (datetime.now() + timedelta(days=4)).isoformat()
    user.telegram_group_access["trial_group"] = True
    user.telegram_group_access["vip_group"] = False

    # Generate referral code for new user
    user.referral_code = subscription_security.generate_referral_code(user_id)
    payment_system.register_referral_code(user_id, user.referral_code)

    # Generate email verification token
    user.verification_token = email_service.generate_verification_token()
    user.verification_token_expires = email_service.get_token_expiration()
    user.email_verified = False

    user_manager._save_user_to_db(user)

    # Send verification email
    email_result = email_service.send_verification_email(
        email=email,
        username=full_name or email.split('@')[0],
        token=user.verification_token
    )

    # Generate tokens
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)

    log_event("AUTH", f"New user registered: {email} with 4-day TRIAL (verification email sent: {email_result.get('success')})")

    return jsonify({
        "message": "Registration successful! You have 4 days of FREE trial access. Please verify your email.",
        "user": {
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "username": user.username,
            "plan": user.plan,
            "plan_expires_at": user.plan_expires_at,
            "email_verified": False,
            "referral_code": user.referral_code,
            "trial_days_remaining": 4
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "verification_sent": email_result.get('success', False),
        "dev_mode": email_result.get('dev_mode', False)
    }), 201


@app.route("/api/auth/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    """Login user with 2FA support and rate limiting"""
    data = request.json

    email = data.get("email", "").strip().lower()
    password = data.get("password")
    mfa_token = data.get("mfa_token")  # Optional 2FA token

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Find user by email
    users = user_manager.get_all_users()
    user = None
    for u in users:
        if u.email == email:
            user = u
            break

    if not user:
        audit_logger.log_event(
            AuditEventType.LOGIN_FAILED,
            ip_address=request.remote_addr,
            details={'reason': 'user_not_found', 'email': email}
        )
        return jsonify({"error": "Invalid email or password"}), 401

    # Verify password
    if not user.password_hash or not verify_password(password, user.password_hash):
        audit_logger.log_event(
            AuditEventType.LOGIN_FAILED,
            user_id=user.user_id,
            ip_address=request.remote_addr,
            details={'reason': 'invalid_password'}
        )
        return jsonify({"error": "Invalid email or password"}), 401

    # âœ… ENFORCE EMAIL VERIFICATION
    if not user.email_verified:
        return jsonify({
            "error": "Email verification required",
            "message": "Please verify your email address before logging in. Check your inbox for the verification link.",
            "email_verified": False,
            "email": user.email,
            "user_id": user.user_id
        }), 403

    # Check if 2FA is enabled
    if two_factor_auth.is_enabled(user.user_id):
        if not mfa_token:
            # Password correct, but 2FA required
            return jsonify({
                "requires_2fa": True,
                "message": "2FA verification required",
                "user_id": user.user_id
            }), 200

        # Verify 2FA token
        is_valid, message = two_factor_auth.verify_token(user.user_id, mfa_token)

        if not is_valid:
            audit_logger.log_event(
                AuditEventType.MFA_FAILED,
                user_id=user.user_id,
                ip_address=request.remote_addr
            )
            return jsonify({"error": f"Invalid 2FA code: {message}"}), 401

        audit_logger.log_event(
            AuditEventType.MFA_VERIFIED,
            user_id=user.user_id,
            ip_address=request.remote_addr
        )

    # Ensure user has referral code (for existing users)
    if not hasattr(user, 'referral_code') or not user.referral_code:
        user.referral_code = subscription_security.generate_referral_code(user.user_id)
        payment_system.register_referral_code(user.user_id, user.referral_code)
        user_manager._save_user_to_db(user)

    # Generate tokens
    access_token = create_access_token(user.user_id, email)
    refresh_token = create_refresh_token(user.user_id)

    audit_logger.log_event(
        AuditEventType.LOGIN_SUCCESS,
        user_id=user.user_id,
        ip_address=request.remote_addr
    )

    log_event("AUTH", f"User logged in: {email}")

    return jsonify({
        "message": "Login successful",
        "user": {
            "user_id": user.user_id,
            "email": email,
            "full_name": user.full_name,
            "plan": user.plan,
            "plan_expires_at": user.plan_expires_at,
            "mfa_enabled": two_factor_auth.is_enabled(user.user_id),
            "email_verified": user.email_verified,
            "referral_code": user.referral_code
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "email_verified": user.email_verified
    })


@app.route("/api/auth/refresh", methods=["POST"])
@refresh_token_required
def refresh():
    """Refresh access token using refresh token"""
    user_id = request.user_id
    user = user_manager.get_user(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Generate new access token
    access_token = create_access_token(user_id, user.email)

    return jsonify({
        "access_token": access_token,
        "token_type": "Bearer"
    })


@app.route("/api/auth/me", methods=["GET"])
@token_required
def get_current_user():
    """Get current authenticated user info"""
    user_id = request.user_id
    user = user_manager.get_user(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user": user.to_dict()
    })


@app.route("/api/auth/verify-email/<token>", methods=["GET", "POST"])
def verify_email(token):
    """Verify user email address via verification token

    Can be called via:
    - GET: Direct link from email (redirects to success page)
    - POST: API call from mobile app
    """
    # Find user by verification token
    users = user_manager.get_all_users()
    user = None
    for u in users:
        if u.verification_token == token:
            user = u
            break

    if not user:
        return jsonify({"error": "Invalid or expired verification link"}), 400

    # Check if already verified
    if user.email_verified:
        return jsonify({
            "message": "Email already verified",
            "email_verified": True
        }), 200

    # Check if token expired
    if not email_service.is_token_valid(user.verification_token_expires):
        return jsonify({
            "error": "Verification link expired. Please request a new one.",
            "expired": True
        }), 400

    # Verify email
    user.email_verified = True
    user.verification_token = ""  # Clear token after verification
    user.verification_token_expires = ""
    user.updated_at = datetime.now().isoformat()
    user_manager._save_user_to_db(user)

    # Send welcome email
    email_service.send_welcome_email(user.email, user.full_name or user.email.split('@')[0])

    log_event("AUTH", f"Email verified for user: {user.email}")

    return jsonify({
        "message": "Email verified successfully! You can now access all features.",
        "email_verified": True,
        "user_id": user.user_id,
        "email": user.email
    }), 200


@app.route("/api/auth/resend-verification", methods=["POST"])
@limiter.limit("3 per hour")
@token_required
def resend_verification():
    """Resend email verification link"""
    user_id = request.user_id
    user = user_manager.get_user(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.email_verified:
        return jsonify({
            "message": "Email already verified",
            "email_verified": True
        }), 200

    # Generate new verification token
    user.verification_token = email_service.generate_verification_token()
    user.verification_token_expires = email_service.get_token_expiration()
    user_manager._save_user_to_db(user)

    # Send verification email
    email_result = email_service.send_verification_email(
        email=user.email,
        username=user.full_name or user.email.split('@')[0],
        token=user.verification_token
    )

    if not email_result.get('success'):
        return jsonify({
            "error": "Failed to send verification email. Please try again later.",
            "details": email_result.get('message')
        }), 500

    log_event("AUTH", f"Verification email resent to: {user.email}")

    return jsonify({
        "message": "Verification email sent. Please check your inbox.",
        "email": user.email,
        "dev_mode": email_result.get('dev_mode', False)
    }), 200


@app.route("/api/auth/check-verification", methods=["GET"])
@token_required
def check_verification_status():
    """Check if user's email is verified"""
    user_id = request.user_id
    user = user_manager.get_user(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "email": user.email,
        "email_verified": user.email_verified,
        "verification_required": not user.email_verified
    }), 200


# ============================
# PASSWORD RESET (FORGOT + RESET)
# ============================

@app.route("/api/auth/forgot-password", methods=["POST"])
@limiter.limit("3 per hour")
def forgot_password():
    """Request a password reset link via email"""
    data = request.get_json()
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Find user
    users = user_manager.get_all_users()
    user = next((u for u in users if u.email == email), None)

    if not user:
        return jsonify({"error": "No account found with that email"}), 404

    # Generate reset token (valid 15 min)
    reset_token = email_service.generate_verification_token()
    reset_expires = (datetime.utcnow() + timedelta(minutes=15)).isoformat()

    user.reset_token = reset_token
    user.reset_token_expires = reset_expires
    user_manager._save_user_to_db(user)

    # Send password reset email
    email_result = email_service.send_password_reset_email(
        email=user.email,
        username=user.full_name or user.email.split('@')[0],
        token=reset_token
    )

    log_event("AUTH", f"Password reset email sent to {email}")
    return jsonify({
        "message": "Password reset email sent. Check your inbox.",
        "email": email,
        "sent": email_result.get("success", False)
    }), 200


@app.route("/reset-password/<token>", methods=["GET"])
def show_reset_form(token):
    """Display the password reset form in browser"""
    return render_template("reset_password.html", token=token)


@app.route("/api/auth/reset-password/<token>", methods=["POST"])
@limiter.limit("5 per hour")
def reset_password(token):
    """Reset password using a valid reset token"""
    data = request.get_json()
    new_password = data.get("new_password")

    if not new_password or len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # Find user by token
    users = user_manager.get_all_users()
    user = next((u for u in users if getattr(u, "reset_token", None) == token), None)

    if not user:
        return jsonify({"error": "Invalid or expired reset link"}), 400

    # Check token expiry
    if not email_service.is_token_valid(user.reset_token_expires):
        return jsonify({"error": "Reset link expired. Request a new one."}), 400

    # Update password securely
    user.password_hash = hash_password(new_password)
    user.reset_token = ""
    user.reset_token_expires = ""
    user_manager._save_user_to_db(user)

    # Send confirmation email
    email_service.send_password_reset_success_email(user.email, user.full_name)

    log_event("AUTH", f"Password reset successful for {user.email}")
    
    # Telegram admin notification
    try:
        admin_notifier.send_telegram(
            f"🔐 <b>PASSWORD RESET ALERT</b>\n\n"
            f"👤 User: {user.email}\n"
            f"✅ Password successfully reset\n"
            f"🕒 Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"📱 Platform: VerzekAutoTrader"
        )
    except Exception as notify_error:
        log_event("WARN", f"Telegram password reset alert failed: {notify_error}")
    
    return jsonify({"message": "Password reset successful"}), 200


# ============================
# SUPPORT
# ============================

@app.route("/api/telegram/request-access", methods=["POST"])
@limiter.limit("3 per hour")
@token_required
def request_telegram_access(current_user_id):
    """Request manual Telegram group access (TRIAL users only)"""
    user = user_manager.get_user(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Only TRIAL plan users can request Telegram access
    if user.plan.lower() != "trial":
        return jsonify({
            "error": "This feature is only for TRIAL users",
            "message": "VIP ($50) users receive signals in the app. PREMIUM ($120) users get full auto-trading access."
        }), 403
    
    # Send notification to @VerzekSupport
    telegram_message = f"""
🔔 <b>TELEGRAM GROUP ACCESS REQUEST</b>

👤 <b>User:</b> @{user.username} ({user.full_name})
📧 <b>Email:</b> {user.email}
🆔 <b>User ID:</b> {current_user_id}
📋 <b>Plan:</b> {user.plan.upper()}
⏰ <b>Trial Expires:</b> {user.plan_expires_at}

<b>Action Required:</b>
Add user to TRIAL Telegram group: -1002726167386
"""
    
    try:
        admin_notifier.send_telegram(telegram_message)
        
        log_event("TELEGRAM", f"User {current_user_id} requested Telegram group access")
        
        return jsonify({
            "success": True,
            "message": "Request sent! Contact @VerzekSupport on Telegram with your User ID to confirm.",
            "instructions": f"Message @VerzekSupport:\n\nHi! Please add me to the TRIAL group.\nUser ID: {current_user_id}\nEmail: {user.email}",
            "user_id": current_user_id,
            "telegram_support": "@VerzekSupport"
        })
    except Exception as e:
        log_event("ERROR", f"Failed to send Telegram access request: {e}")
        return jsonify({
            "error": "Failed to send request",
            "message": "Please contact @VerzekSupport directly on Telegram"
        }), 500


@app.route("/api/support/message", methods=["POST"])
@limiter.limit("5 per hour")
@token_required
def send_support_message(current_user_id):
    """Send support message from mobile app (with rate limiting)"""
    data = request.json
    message = data.get("message", "").strip()
    subject = data.get("subject", "Support Request").strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    # Get user info
    user = user_manager.get_user(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_display = user.full_name or user.email or current_user_id

    # Send support email
    try:
        email_result = email_service.send_support_notification(
            from_user=f"{user_display} ({user.email})",
            message=f"Subject: {subject}\n\n{message}",
            telegram_username=None
        )

        if email_result['success']:
            log_event("SUPPORT", f"Support message sent from user: {user.email}")
            return jsonify({
                "success": True,
                "message": "Support message sent successfully! We'll respond within 24 hours."
            }), 200
        else:
            return jsonify({
                "error": "Failed to send support message. Please try again later.",
                "details": email_result.get('error')
            }), 500

    except Exception as e:
        log_event("SUPPORT", f"Error sending support message from {user.email}: {str(e)}")
        return jsonify({
            "error": "Failed to send support message",
            "details": str(e)
        }), 500


# ============================
# USER MANAGEMENT
# ============================

@app.route("/api/users", methods=["GET", "POST"])
def handle_users():
    """Get all users or create a new user"""
    if request.method == "GET":
        users = user_manager.get_all_users()
        return jsonify({
            "count": len(users),
            "users": [user.to_dict() for user in users]
        })

    elif request.method == "POST":
        data = request.json
        user_id = data.get("user_id")
        telegram_id = data.get("telegram_id")

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        user = user_manager.create_user(user_id, telegram_id)
        return jsonify({
            "message": "User created successfully",
            "user": user.to_dict()
        }), 201


@app.route("/api/users/<user_id>", methods=["GET", "PUT", "DELETE"])
def handle_single_user(user_id):
    """Get, update, or delete a specific user"""
    if request.method == "GET":
        user = user_manager.get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user.to_dict())

    elif request.method == "PUT":
        user = user_manager.get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        updates = request.json
        user_manager.update_user(user_id, updates)
        return jsonify({
            "message": "User updated successfully",
            "user": user_manager.get_user(user_id).to_dict()
        })

    elif request.method == "DELETE":
        user = user_manager.get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_manager.delete_user(user_id)
        return jsonify({"message": "User deleted successfully"})


# ============================
# GENERAL MODE SETTINGS
# ============================

@app.route("/api/users/<user_id>/general", methods=["GET", "PUT"])
@token_required
def handle_general_settings(user_id):
    """Get or update user's general mode settings"""
    current_user_id = request.user_id
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Authorization: Verify user can only modify their own settings
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized: You can only modify your own settings"}), 403

    if request.method == "GET":
        return jsonify(user.general_settings)

    elif request.method == "PUT":
        updates = request.json
        user.update_general_settings(updates)
        user_manager._save_user_to_db(user)
        return jsonify({
            "message": "General settings updated",
            "general_settings": user.general_settings
        })


# ============================
# CAPITAL & RISK SETTINGS
# ============================

@app.route("/api/users/<user_id>/risk", methods=["GET", "PUT"])
@token_required
def handle_risk_settings(user_id):
    """Get or update user's risk settings"""
    current_user_id = request.user_id
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Authorization: Verify user can only modify their own settings
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized: You can only modify your own settings"}), 403

    if request.method == "GET":
        return jsonify(user.risk_settings)

    elif request.method == "PUT":
        updates = request.json
        user.update_risk_settings(updates)
        user_manager._save_user_to_db(user)
        return jsonify({
            "message": "Risk settings updated",
            "risk_settings": user.risk_settings
        })


# ============================
# STRATEGY PARAMETERS
# ============================

@app.route("/api/users/<user_id>/strategy", methods=["GET", "PUT"])
@token_required
def handle_strategy_settings(user_id):
    """Get or update user's strategy parameters"""
    current_user_id = request.user_id
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Authorization: Verify user can only modify their own settings
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized: You can only modify your own settings"}), 403

    if request.method == "GET":
        return jsonify(user.strategy_settings)

    elif request.method == "PUT":
        updates = request.json
        user.update_strategy_settings(updates)
        user_manager._save_user_to_db(user)
        return jsonify({
            "message": "Strategy settings updated",
            "strategy_settings": user.strategy_settings
        })


# ============================
# DCA MARGIN CALL SETTINGS (PREMIUM ONLY)
# ============================

@app.route("/api/users/<user_id>/dca", methods=["GET", "PUT"])
@token_required
def handle_dca_settings(user_id):
    """Get or update user's DCA settings (PREMIUM ONLY)"""
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # SECURITY: Check if subscription is expired
    if user.is_subscription_expired():
        return jsonify({
            "error": "Subscription expired",
            "message": "Your subscription has expired. Please renew to access auto-trading features.",
            "plan": user.plan,
            "expired_at": user.plan_expires_at
        }), 403

    # SECURITY: DCA/Auto-trade is PREMIUM (vip) plan only
    plan_features = user.get_plan_features()
    if not plan_features.get("auto_trading", False):
        return jsonify({
            "error": "Unauthorized",
            "message": "Auto-trading is available only for PREMIUM ($120/month) subscribers.",
            "current_plan": user.plan,
            "required_plan": "vip (PREMIUM)",
            "upgrade_url": "/api/subscription/upgrade"
        }), 403

    if request.method == "GET":
        return jsonify(user.dca_settings)

    elif request.method == "PUT":
        updates = request.json
        user.update_dca_settings(updates)
        user_manager._save_user_to_db(user)
        return jsonify({
            "message": "DCA settings updated",
            "dca_settings": user.dca_settings
        })


# ============================
# EXCHANGE ACCOUNTS (PREMIUM ONLY)
# ============================

@app.route("/api/users/<user_id>/exchanges", methods=["GET", "POST", "DELETE"])
@token_required
def handle_exchanges(user_id):
    """Get, add, or remove exchange accounts (PREMIUM ONLY)"""
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # SECURITY: Check if subscription is expired
    if user.is_subscription_expired():
        return jsonify({
            "error": "Subscription expired",
            "message": "Your subscription has expired. Please renew to manage exchange connections.",
            "plan": user.plan,
            "expired_at": user.plan_expires_at
        }), 403

    # SECURITY: Exchange connections require PREMIUM plan
    plan_features = user.get_plan_features()
    max_exchanges = plan_features.get("max_exchanges", 0)

    if max_exchanges == 0:
        return jsonify({
            "error": "Unauthorized",
            "message": "Exchange connections are available only for PREMIUM ($120/month) subscribers.",
            "current_plan": user.plan,
            "required_plan": "vip (PREMIUM)",
            "upgrade_url": "/api/subscription/upgrade"
        }), 403

    if request.method == "GET":
        # Return exchange accounts without exposing encrypted credentials
        safe_exchanges = []
        for exc in user.exchange_accounts:
            safe_exc = {
                "id": exc.get("id"),
                "exchange": exc.get("exchange"),
                "testnet": exc.get("testnet", False),
                "enabled": exc.get("enabled", True),
                "added_at": exc.get("added_at"),
                "encrypted": exc.get("encrypted", False)
            }
            safe_exchanges.append(safe_exc)

        return jsonify({
            "count": len(safe_exchanges),
            "exchanges": safe_exchanges,
            "max_exchanges": max_exchanges
        })

    elif request.method == "POST":
        # âœ… REQUIRE EMAIL VERIFICATION for trading features
        if not user.email_verified:
            return jsonify({
                "error": "Email verification required",
                "message": "Please verify your email address before connecting exchange accounts",
                "email_verified": False,
                "email": user.email
            }), 403

        data = request.json
        exchange = data.get("exchange")
        api_key = data.get("api_key")
        api_secret = data.get("api_secret")
        testnet = data.get("testnet", False)
        enabled = data.get("enabled", True)

        if not exchange or not api_key or not api_secret:
            return jsonify({"error": "exchange, api_key, and api_secret required"}), 400

        # Encrypt API credentials before storing
        from modules.encryption_service import EncryptionService
        encryption_service = EncryptionService()

        try:
            encrypted_creds = encryption_service.encrypt_api_credentials(api_key, api_secret)
        except Exception as e:
            log_event("ERROR", f"Encryption failed for user {user_id}: {e}")
            return jsonify({"error": "Failed to encrypt credentials"}), 500

        # Create exchange account with encrypted credentials
        import time
        account_id = f"{exchange}_{int(time.time())}"

        exchange_account = {
            "id": account_id,
            "exchange": exchange,
            "api_key_encrypted": encrypted_creds["api_key_encrypted"],
            "api_secret_encrypted": encrypted_creds["api_secret_encrypted"],
            "encrypted": True,
            "testnet": testnet,
            "enabled": enabled,
            "added_at": __import__('datetime').datetime.now().isoformat()
        }

        user.exchange_accounts.append(exchange_account)
        user_manager._save_user_to_db(user)

        log_event("EXCHANGE", f"âœ… Added encrypted {exchange} account for user {user_id}")

        return jsonify({
            "message": "Exchange account added successfully",
            "account_id": account_id,
            "exchange": exchange
        }), 201

    elif request.method == "DELETE":
        account_id = request.json.get("account_id")
        if not account_id:
            return jsonify({"error": "account_id required"}), 400

        user.exchange_accounts = [
            acc for acc in user.exchange_accounts
            if acc.get("id") != account_id
        ]
        user_manager._save_user_to_db(user)

        log_event("EXCHANGE", f"ðŸ—‘ï¸ Removed exchange account {account_id} for user {user_id}")
        return jsonify({"message": "Exchange account removed"})


# ============================
# LEVERAGE SETTINGS PER EXCHANGE
# ============================

@app.route("/api/users/<user_id>/exchanges/<exchange>/leverage", methods=["GET", "PUT"])
@token_required
def handle_exchange_leverage(user_id, exchange):
    """Get or update leverage settings for a specific exchange"""
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not hasattr(user, 'exchange_leverage_settings'):
        user.exchange_leverage_settings = {}

    if request.method == "GET":
        leverage = user.exchange_leverage_settings.get(exchange, 10)
        return jsonify({
            "exchange": exchange,
            "leverage": leverage
        })

    elif request.method == "PUT":
        data = request.json
        leverage = data.get("leverage", 10)

        if not isinstance(leverage, (int, float)) or leverage < 1 or leverage > 25:
            return jsonify({"error": "Leverage must be between 1 and 25"}), 400

        if not hasattr(user, 'exchange_leverage_settings'):
            user.exchange_leverage_settings = {}

        user.exchange_leverage_settings[exchange] = int(leverage)
        user.updated_at = time.time()
        user_manager._save_user_to_db(user)

        log_event("SETTINGS", f"ðŸ’° User {user_id} set {exchange} leverage to {leverage}x")

        return jsonify({
            "message": f"Leverage set to {leverage}x for {exchange}",
            "exchange": exchange,
            "leverage": leverage
        })


# ============================
# SUBSCRIPTION MANAGEMENT
# ============================

@app.route("/api/users/<user_id>/subscription", methods=["GET", "POST"])
@token_required
def handle_subscription(user_id):
    """Get subscription info or activate a plan (SERVER-SIDE VALIDATION REQUIRED)"""
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if request.method == "GET":
        # Check if subscription expired and lock if needed
        user.check_and_lock_expired_users()
        user_manager._save_user_to_db(user)

        return jsonify({
            "plan": user.plan,
            "plan_started_at": user.plan_started_at,
            "plan_expires_at": user.plan_expires_at,
            "is_expired": user.is_subscription_expired(),
            "group_access": user.telegram_group_access,
            "features": user.get_plan_features()
        })

    elif request.method == "POST":
        # ðŸ”’ ANTI-FRAUD: Direct plan activation is NOT allowed from client
        # Plans must be activated through payment verification endpoints only
        return jsonify({
            "error": "Unauthorized",
            "message": "Subscriptions must be activated through payment verification only.",
            "instructions": "Please submit payment via /api/payment/submit and wait for admin approval.",
            "payment_methods": {
                "TRIAL": "Automatic 4-day trial (one-time only)",
                "VIP": "$50/month - Submit USDT payment",
                "PREMIUM": "$120/month - Submit USDT payment"
            }
        }), 403
# ============================
# TRADING PREFERENCES
# ============================

@app.route("/api/users/<user_id>/preferences", methods=["GET", "PUT"])
@token_required
def handle_trading_preferences(user_id):
    """Get or update user's trading preferences
    current_user_id = request.user_id (notifications, symbols, etc)"""
    current_user_id = request.user_id
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Authorization: Verify user can only modify their own settings
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized: You can only modify your own settings"}), 403

    if request.method == "GET":
        return jsonify(user.trading_preferences)

    elif request.method == "PUT":
        updates = request.json
        user.trading_preferences.update(updates)
        user.updated_at = time.time()
        user_manager._save_user_to_db(user)
        return jsonify({
            "message": "Trading preferences updated",
            "trading_preferences": user.trading_preferences
        })


# ============================
# SIGNALS FEED
# ============================

@app.route("/api/signals", methods=["GET"])
@token_required
def get_signals():
    """Get recent trading signals from broadcast log (PROTECTED: requires active subscription)"""
    try:
        # Get authenticated user from token
        user_id = request.user_id
        user = user_manager.get_user(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # SECURITY: Check if subscription is expired
        if user.is_subscription_expired():
            return jsonify({
                "error": "Subscription expired",
                "message": "Your subscription has expired. Please renew to access trading signals.",
                "subscription_status": "expired",
                "plan": user.plan,
                "expired_at": user.plan_expires_at
            }), 403

        # SECURITY: Check if user's plan includes signal access
        plan_features = user.get_plan_features()
        if not plan_features.get("signal_forwarding", False):
            return jsonify({
                "error": "Unauthorized",
                "message": "Your current plan does not include signal access. Please upgrade your subscription.",
                "plan": user.plan,
                "required_plans": ["free (TRIAL)", "pro (VIP)", "vip (PREMIUM)"]
            }), 403

        # User is authorized - return signals
        log_file = "database/broadcast_log.txt"
        if not os.path.exists(log_file):
            return jsonify({"count": 0, "signals": [], "subscription_status": "active"})

        # Read last 50 lines from log file
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()[-50:]

        signals = []
        for line in lines:
            # Parse timestamp and text
            match = re.match(r'\[(.*?)\] (.*)', line.strip())
            if match:
                timestamp, text = match.groups()

                # Only include lines that look like signals (contain trading keywords)
                if any(kw in text.upper() for kw in ["LONG", "SHORT", "ENTRY", "TARGET", "USDT"]):
                    signals.append({
                        "timestamp": timestamp,
                        "text": text,
                        "id": f"{timestamp}_{len(signals)}"
                    })

        # Reverse to show newest first
        signals.reverse()

        return jsonify({
            "count": len(signals),
            "signals": signals,
            "subscription_status": "active",
            "plan": user.plan,
            "expires_at": user.plan_expires_at
        })
    except Exception as e:
        log_event("ERROR", f"Error reading signals: {e}")
        return jsonify({"error": "Failed to read signals", "count": 0, "signals": []}), 500


# ============================
# POSITIONS
# ============================

@app.route("/api/positions", methods=["GET"])
def get_all_positions():
    """Get all positions across all users"""
    all_positions = position_tracker.get_all_positions()
    return jsonify({
        "count": len(all_positions),
        "positions": all_positions
    })


@app.route("/api/positions/<user_id>", methods=["GET"])
def get_user_positions(user_id):
    """Get positions for a specific user"""
    # Filter positions by user_id
    all_positions = position_tracker.get_all_positions()
    user_positions = [p for p in all_positions if p.get("user_id") == user_id]

    return jsonify({
        "user_id": user_id,
        "count": len(user_positions),
        "positions": user_positions
    })


# ============================
# STATISTICS
# ============================

@app.route("/api/users/<user_id>/stats", methods=["GET"])
def get_user_stats(user_id):
    """Get user trading statistics"""
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "stats": user.stats,
        "daily_stats": user.daily_stats
    })


# ============================
# SAFETY CONTROLS
# ============================

@app.route("/api/safety/status", methods=["GET"])
def get_safety_status():
    """Get safety system status"""
    return jsonify(safety_manager.get_safety_status())


@app.route("/api/safety/killswitch", methods=["POST"])
def control_killswitch():
    """Activate or deactivate kill switch"""
    data = request.json or {}
    action = data.get("action")  # "activate" or "deactivate"
    reason = data.get("reason", "Manual activation")

    if action == "activate":
        result = safety_manager.activate_kill_switch(reason)
        return jsonify(result)
    elif action == "deactivate":
        result = safety_manager.deactivate_kill_switch()
        return jsonify(result)
    else:
        return jsonify({"error": "Invalid action. Use 'activate' or 'deactivate'"}), 400


@app.route("/api/safety/pause", methods=["POST"])
def pause_trading():
    """Pause trading for a specific duration"""
    data = request.json or {}
    duration = data.get("duration_minutes", 60)
    reason = data.get("reason", "Manual pause")

    result = safety_manager.pause_trading(duration, reason)
    return jsonify(result)


@app.route("/api/safety/resume", methods=["POST"])
def resume_trading():
    """Resume trading immediately"""
    result = safety_manager.resume_trading()
    return jsonify(result)


@app.route("/api/safety/circuit-breaker", methods=["POST"])
def control_circuit_breaker():
    """Activate or deactivate circuit breaker"""
    data = request.json or {}
    action = data.get("action")
    reason = data.get("reason", "Manual activation")

    if action == "activate":
        result = safety_manager.activate_circuit_breaker(reason)
        return jsonify(result)
    elif action == "deactivate":
        result = safety_manager.deactivate_circuit_breaker()
        return jsonify(result)
    else:
        return jsonify({"error": "Invalid action. Use 'activate' or 'deactivate'"}), 400


# ============================
# PAYMENT & SUBSCRIPTION SYSTEM
# ============================

@app.route("/api/payments/create", methods=["POST"])
@token_required
def create_payment_request(current_user_id):
    """Create payment request for subscription upgrade"""
    # ✅ ENFORCE EMAIL VERIFICATION for PREMIUM ($120) payments
    user = user_manager.get_user(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not user.email_verified:
        return jsonify({
            "error": "Email verification required",
            "message": "Please verify your email address before making subscription payments. Check your inbox for the verification link.",
            "email_verified": False,
            "email": user.email
        }), 403
    
    data = request.json
    plan = data.get('plan')

    # Normalize plan name to lowercase and handle legacy 'pro' (case-insensitive)
    if plan:
        plan = plan.lower()
        if plan == 'pro':
            plan = 'premium'
    
    if not plan or plan not in ['premium', 'vip']:
        return jsonify({'error': 'Invalid plan. Choose premium or vip'}), 400

    result = payment_system.create_payment_request(current_user_id, plan)
    return jsonify(result)


@app.route("/api/payments/verify", methods=["POST"])
@token_required
def submit_payment_verification(current_user_id):
    """Submit payment for verification with TX hash (signature optional for mobile app)"""
    # ✅ ENFORCE EMAIL VERIFICATION before confirming PREMIUM ($120) payments
    user = user_manager.get_user(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not user.email_verified:
        return jsonify({
            "error": "Email verification required",
            "message": "Please verify your email address before confirming subscription payments. This is required for $120 PREMIUM payments.",
            "email_verified": False,
            "email": user.email
        }), 403
    
    data = request.json

    payment_id = data.get('payment_id')
    tx_hash = data.get('tx_hash')
    referral_code = data.get('referral_code')
    signature = request.headers.get('X-Payment-Signature')

    if not payment_id or not tx_hash:
        return jsonify({'error': 'payment_id and tx_hash required'}), 400

    # Signature verification is OPTIONAL (mobile app doesn't send it)
    # If signature is provided (admin/internal calls), verify it
    if signature:
        payment_data = {
            'payment_id': payment_id,
            'tx_hash': tx_hash,
            'user_id': current_user_id
        }

        if not subscription_security.verify_payment_signature(payment_data, signature):
            return jsonify({'error': 'Invalid payment signature'}), 403
        
        log_event("PAYMENT", f"Payment verification with valid signature from user {current_user_id}")
    else:
        # No signature provided - mobile app client call
        # TronScan verification will handle authenticity check
        log_event("PAYMENT", f"Payment verification without signature (mobile client) from user {current_user_id}")

    result = payment_system.verify_usdt_payment(
        payment_id, tx_hash, current_user_id, referral_code
    )
    return jsonify(result)


@app.route("/api/payments/pending", methods=["GET"])
@token_required
def get_pending_payments_admin(current_user_id):
    """Admin: Get pending payment verifications"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    pending = payment_system.get_pending_payments()
    return jsonify({'count': len(pending), 'payments': pending})


@app.route("/api/payments/confirm/<payment_id>", methods=["POST"])
@token_required
def confirm_payment_admin(current_user_id, payment_id):
    """Admin: Confirm payment and activate subscription with MANDATORY HMAC signature"""
    from datetime import datetime, timedelta

    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.json
    is_valid = data.get('is_valid', False)
    signature = request.headers.get('X-Admin-Signature')

    if not signature:
        return jsonify({'error': 'X-Admin-Signature header required for security'}), 401

    admin_action = {
        'payment_id': payment_id,
        'admin_id': current_user_id,
        'is_valid': is_valid,
        'timestamp': int(datetime.now().timestamp())
    }

    if not subscription_security.verify_payment_signature(admin_action, signature):
        return jsonify({'error': 'Invalid admin signature'}), 403

    result = payment_system.admin_confirm_payment(payment_id, is_valid)

    if result['success'] and is_valid:
        target_user = user_manager.get_user(result['user_id'])
        target_user.plan = result['plan']
        target_user.plan_started_at = datetime.now().isoformat()
        target_user.plan_expires_at = (datetime.now() + timedelta(days=30)).isoformat()

        license_key = subscription_security.generate_license_key(
            result['user_id'], result['plan'], 30
        )
        target_user.license_key = license_key

        user_manager._save_user_to_db(user)

        result['license_key'] = license_key

    return jsonify(result)


# ============================
# REFERRAL SYSTEM
# ============================

@app.route("/api/referral/code", methods=["GET"])
@token_required
def get_referral_code(current_user_id):
    """Get user's referral code"""
    user = user_manager.get_user(current_user_id)

    if not hasattr(user, 'referral_code') or not user.referral_code:
        user.referral_code = subscription_security.generate_referral_code(current_user_id)
        payment_system.register_referral_code(current_user_id, user.referral_code)
        user_manager._save_user_to_db(user)

    return jsonify({
        'referral_code': user.referral_code,
        'referral_link': f"https://verzek.app/register?ref={user.referral_code}"
    })


@app.route("/api/referral/stats", methods=["GET"])
@token_required
def get_referral_stats_endpoint(current_user_id):
    """Get referral statistics, earnings, and in-app wallet balance"""
    stats = payment_system.get_referral_stats(current_user_id)
    return jsonify(stats)


@app.route("/api/wallet/balance", methods=["GET"])
@token_required
def get_wallet_balance(current_user_id):
    """Get user's in-app wallet balance"""
    wallet_balance = payment_system.referrals.get('wallets', {}).get(current_user_id, 0.0)
    return jsonify({
        'balance': wallet_balance,
        'currency': 'USDT',
        'minimum_withdrawal': 10.0,
        'withdrawal_fee': 1.0
    })


@app.route("/api/referral/payout", methods=["POST"])
@token_required
def request_referral_payout_endpoint(current_user_id):
    """Request payout of referral earnings"""
    data = request.json
    wallet_address = data.get('wallet_address')

    if not wallet_address:
        return jsonify({'error': 'wallet_address required'}), 400

    result = payment_system.request_referral_payout(current_user_id, wallet_address)
    return jsonify(result)


@app.route("/api/referral/payouts/pending", methods=["GET"])
@token_required
def get_pending_payouts_admin(current_user_id):
    """Admin: Get pending referral payouts"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    pending = payment_system.get_pending_payouts()
    return jsonify({'count': len(pending), 'payouts': pending})


@app.route("/api/referral/payouts/<payout_id>/complete", methods=["POST"])
@token_required
def complete_payout_admin(current_user_id, payout_id):
    """Admin: Mark payout as completed after sending USDT"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.json
    tx_hash = data.get('tx_hash')

    if not tx_hash:
        return jsonify({'error': 'tx_hash required (transaction hash of sent USDT)'}), 400

    # Import admin dashboard utilities
    from utils.admin_dashboard import process_payout

    result = process_payout(payout_id, tx_hash, current_user_id)

    if result.get('success'):
        audit_logger.log_event(
            AuditEventType.ADMIN_ACTION,
            user_id=current_user_id,
            ip_address=request.remote_addr,
            details={
                'action': 'complete_payout',
                'payout_id': payout_id,
                'amount': result.get('amount'),
                'tx_hash': tx_hash
            }
        )

    return jsonify(result)


# ============================
# SUBSCRIPTION SECURITY
# ============================

@app.route("/api/subscription/validate", methods=["POST"])
@token_required
def validate_subscription(current_user_id):
    """Validate user's subscription and license key"""
    user = user_manager.get_user(current_user_id)

    if not hasattr(user, 'license_key') or not user.license_key:
        return jsonify({
            'valid': False,
            'plan': user.plan,
            'message': 'No license key found'
        })

    is_valid, message = subscription_security.validate_license_key(
        user.license_key, current_user_id
    )

    # Downgrade to free if license invalid (include legacy 'pro' plan)
    if not is_valid and user.plan in ['premium', 'vip', 'pro']:
        user.plan = 'free'
        user_manager._save_user_to_db(user)

    return jsonify({
        'valid': is_valid,
        'plan': user.plan,
        'message': message
    })


# ============================
# 2FA / MFA ENDPOINTS
# ============================

@app.route("/api/2fa/enroll", methods=["POST"])
@token_required
def enroll_2fa(current_user_id):
    """Enroll user in 2FA"""
    user = user_manager.get_user(current_user_id)

    enrollment_data = two_factor_auth.enroll_user(current_user_id, user.email)

    audit_logger.log_event(
        AuditEventType.MFA_ENROLLED,
        user_id=current_user_id,
        ip_address=request.remote_addr
    )

    return jsonify({
        'success': True,
        'qr_code': enrollment_data['qr_code'],
        'secret': enrollment_data['secret'],
        'backup_codes': enrollment_data['backup_codes'],
        'message': 'Scan QR code with Google Authenticator or Authy'
    })


@app.route("/api/2fa/verify", methods=["POST"])
@token_required
def verify_2fa_enable(current_user_id):
    """Verify and enable 2FA for user"""
    data = request.json
    token = data.get('token')

    if not token:
        return jsonify({'error': 'Verification token required'}), 400

    is_valid, message = two_factor_auth.verify_and_enable(current_user_id, token)

    if is_valid:
        audit_logger.log_event(
            AuditEventType.MFA_ENABLED,
            user_id=current_user_id,
            ip_address=request.remote_addr
        )

    return jsonify({
        'success': is_valid,
        'message': message
    })


@app.route("/api/2fa/disable", methods=["POST"])
@token_required
def disable_2fa(current_user_id):
    """Disable 2FA for user (requires password)"""
    data = request.json
    password = data.get('password')

    if not password:
        return jsonify({'error': 'Password required to disable 2FA'}), 400

    user = user_manager.get_user(current_user_id)

    if not verify_password(password, user.password_hash):
        return jsonify({'error': 'Invalid password'}), 403

    is_success, message = two_factor_auth.disable_2fa(current_user_id, password)

    if is_success:
        audit_logger.log_event(
            AuditEventType.MFA_DISABLED,
            user_id=current_user_id,
            ip_address=request.remote_addr
        )

    return jsonify({
        'success': is_success,
        'message': message
    })


@app.route("/api/2fa/backup-codes", methods=["POST"])
@token_required
def regenerate_backup_codes(current_user_id):
    """Regenerate 2FA backup codes"""
    try:
        backup_codes = two_factor_auth.regenerate_backup_codes(current_user_id)

        audit_logger.log_event(
            AuditEventType.ADMIN_ACTION,
            user_id=current_user_id,
            ip_address=request.remote_addr,
            details={'action': 'regenerate_backup_codes'}
        )

        return jsonify({
            'success': True,
            'backup_codes': backup_codes
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route("/api/2fa/status", methods=["GET"])
@token_required
def get_2fa_status(current_user_id):
    """Get 2FA status for user"""
    status = two_factor_auth.get_mfa_status(current_user_id)
    return jsonify(status)


# ============================
# BACKUP & DISASTER RECOVERY
# ============================

@app.route("/api/backup/create", methods=["POST"])
@token_required
def create_backup(current_user_id):
    """Create system backup (admin only)"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    try:
        backup_path = backup_system.create_backup()

        audit_logger.log_event(
            AuditEventType.BACKUP_CREATED,
            user_id=current_user_id,
            ip_address=request.remote_addr,
            details={'backup_path': backup_path}
        )

        return jsonify({
            'success': True,
            'backup_path': backup_path,
            'message': 'Backup created successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/backup/list", methods=["GET"])
@token_required
def list_backups(current_user_id):
    """List all available backups (admin only)"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    backups = backup_system.list_backups()
    stats = backup_system.get_backup_stats()

    return jsonify({
        'backups': backups,
        'stats': stats
    })


@app.route("/api/backup/restore/<backup_name>", methods=["POST"])
@token_required
def restore_backup(current_user_id, backup_name):
    """Restore from backup (admin only, DANGEROUS)"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    # Require password confirmation
    data = request.json
    password = data.get('password')

    if not password or not verify_password(password, user.password_hash):
        return jsonify({'error': 'Password confirmation required'}), 403

    success = backup_system.restore_backup(backup_name)

    if success:
        audit_logger.log_event(
            AuditEventType.BACKUP_RESTORED,
            user_id=current_user_id,
            ip_address=request.remote_addr,
            details={'backup_name': backup_name},
            severity='critical'
        )

    return jsonify({
        'success': success,
        'message': 'Backup restored successfully' if success else 'Restore failed'
    })


# ============================
# TRONSCAN AUTO-VERIFICATION
# ============================

@app.route("/api/payments/auto-verify/<payment_id>", methods=["POST"])
@token_required
def auto_verify_payment(current_user_id, payment_id):
    """Auto-verify payment using TronScan API (admin only)"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    # Get payment details
    payment = next((p for p in payment_system.payments if p['payment_id'] == payment_id), None)

    if not payment:
        return jsonify({'error': 'Payment not found'}), 404

    if 'tx_hash' not in payment:
        return jsonify({'error': 'Transaction hash not submitted yet'}), 400

    # Verify with TronScan
    verification = tronscan_client.verify_transaction(
        payment['tx_hash'],
        payment['amount_usdt']
    )

    if verification.get('verified'):
        # Auto-confirm payment
        result = payment_system.admin_confirm_payment(payment_id, True)

        if result['success']:
            target_user = user_manager.get_user(result['user_id'])
            target_user.plan = result['plan']
            target_user.plan_started_at = datetime.now().isoformat()
            target_user.plan_expires_at = (datetime.now() + timedelta(days=30)).isoformat()

            license_key = subscription_security.generate_license_key(
                result['user_id'], result['plan'], 30
            )
            target_user.license_key = license_key

            user_manager._save_user_to_db(user)

            audit_logger.log_event(
                AuditEventType.PAYMENT_CONFIRMED,
                user_id=current_user_id,
                ip_address=request.remote_addr,
                details={
                    'payment_id': payment_id,
                    'auto_verified': True,
                    'amount': verification['amount']
                }
            )

            return jsonify({
                'success': True,
                'verified': True,
                'message': 'Payment auto-verified and confirmed',
                'license_key': license_key,
                'verification_details': verification
            })

    return jsonify({
        'success': False,
        'verified': False,
        'error': verification.get('error', 'Verification failed'),
        'verification_details': verification
    })


# ============================
# AUDIT LOGS
# ============================

@app.route("/api/audit/user/<user_id>", methods=["GET"])
@token_required
def get_user_audit_logs(current_user_id, user_id):
    """Get audit logs for a user (admin or self)"""
    user = user_manager.get_user(current_user_id)

    # Can only view own logs unless admin
    if user.plan != 'admin' and current_user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    limit = request.args.get('limit', 50, type=int)
    events = audit_logger.get_user_activity(user_id, limit)

    return jsonify({
        'user_id': user_id,
        'event_count': len(events),
        'events': events
    })


@app.route("/api/audit/suspicious", methods=["GET"])
@token_required
def get_suspicious_activity(current_user_id):
    """Get suspicious activity (admin only)"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    limit = request.args.get('limit', 20, type=int)
    events = audit_logger.get_suspicious_activity(limit)

    return jsonify({
        'event_count': len(events),
        'events': events
    })


@app.route("/api/audit/alerts", methods=["GET"])
@token_required
def get_security_alerts(current_user_id):
    """Get security alerts (admin only)"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    resolved = request.args.get('resolved')
    if resolved is not None:
        resolved = resolved.lower() == 'true'

    alerts = audit_logger.get_alerts(resolved)

    return jsonify({
        'alert_count': len(alerts),
        'alerts': alerts
    })


# ============================
# ADMIN DASHBOARD
# ============================

@app.route("/admin/dashboard")
def admin_dashboard_view():
    """Serve admin dashboard web interface"""
    return render_template('admin_dashboard.html')


@app.route("/api/admin/overview", methods=["GET"])
@token_required
def admin_overview(current_user_id):
    """Get system overview dashboard (admin only)"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    overview = admin_dashboard.get_system_overview()

    audit_logger.log_event(
        AuditEventType.ADMIN_ACTION,
        user_id=current_user_id,
        ip_address=request.remote_addr,
        details={'action': 'view_dashboard_overview'}
    )

    return jsonify(overview)


@app.route("/api/admin/users", methods=["GET"])
@token_required
def admin_users_list(current_user_id):
    """Get user list with filtering (admin only)"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    plan_filter = request.args.get('plan')
    search = request.args.get('search')

    users = admin_dashboard.get_user_list(plan_filter, search)

    return jsonify({
        'total': len(users),
        'users': users
    })


@app.route("/api/admin/payments/pending", methods=["GET"])
@token_required
def admin_pending_payments(current_user_id):
    """Get pending payment verifications (admin only)"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    pending = admin_dashboard.get_pending_payments()

    return jsonify({
        'total': len(pending),
        'payments': pending
    })


@app.route("/api/admin/activity", methods=["GET"])
@token_required
def admin_recent_activity(current_user_id):
    """Get recent system activity (admin only)"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    limit = request.args.get('limit', 50, type=int)
    activities = admin_dashboard.get_recent_activity(limit)

    return jsonify({
        'total': len(activities),
        'activities': activities
    })


@app.route("/api/admin/health", methods=["GET"])
@token_required
def admin_system_health(current_user_id):
    """Get system health metrics (admin only)"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    health = admin_dashboard.get_system_health()

    return jsonify(health)


@app.route("/api/admin/revenue", methods=["GET"])
@token_required
def admin_revenue_analytics(current_user_id):
    """Get revenue analytics (admin only)"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    days = request.args.get('days', 30, type=int)
    analytics = admin_dashboard.get_revenue_analytics(days)

    return jsonify(analytics)


@app.route("/api/admin/trading/performance", methods=["GET"])
@token_required
def admin_trading_performance(current_user_id):
    """Get trading performance metrics (admin only)"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    performance = admin_dashboard.get_trading_performance()

    return jsonify(performance)


@app.route("/api/admin/audit", methods=["GET"])
@token_required
def get_audit_log(current_user_id):
    """
    Secure admin endpoint to retrieve system audit events.
    Returns audit log entries for monitoring authentication and system events.
    """
    try:
        user = user_manager.get_user(current_user_id)

        # Restrict access to admin users only
        if not user or user.plan != 'admin':
            return jsonify({"error": "Admin access required"}), 403

        # Get limit from query params (default 200)
        limit = request.args.get('limit', 200, type=int)
        event_type = request.args.get('event_type')  # Optional filter

        # Read audit log file
        audit_file = "database/security_audit.jsonl"
        events = []
        
        if os.path.exists(audit_file):
            with open(audit_file, 'r') as f:
                lines = f.readlines()
                
            # Parse and filter events
            for line in reversed(lines[-limit*2:]):  # Read more than needed for filtering
                try:
                    event = json_module.loads(line.strip())
                    
                    # Apply event type filter if specified
                    if event_type and event.get('event_type') != event_type:
                        continue
                    
                    events.append(event)
                    
                    if len(events) >= limit:
                        break
                except json_module.JSONDecodeError:
                    continue

        return jsonify({
            "count": len(events),
            "events": events,
            "message": "Audit log retrieved successfully."
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


@app.route("/admin/audit", methods=["GET"])
def show_audit_dashboard():
    """
    Render visual admin audit dashboard.
    Authentication is handled client-side via login form.
    """
    return render_template("admin_audit.html")


# ============================
# PUSH NOTIFICATIONS
# ============================

@app.route("/api/notifications/register", methods=["POST"])
@token_required
def register_device_token(current_user_id):
    """Register device for push notifications"""
    data = request.json
    device_token = data.get('device_token')

    if not device_token:
        return jsonify({'error': 'device_token is required'}), 400

    success = push_service.register_device(current_user_id, device_token)

    audit_logger.log_event(
        AuditEventType.SETTINGS_CHANGED,
        user_id=current_user_id,
        ip_address=request.remote_addr,
        details={'action': 'register_push_token'}
    )

    return jsonify({
        'success': success,
        'message': 'Device registered for notifications' if success else 'Device already registered'
    })


@app.route("/api/notifications/unregister", methods=["POST"])
@token_required
def unregister_device_token(current_user_id):
    """Unregister device from push notifications"""
    data = request.json
    device_token = data.get('device_token')

    if not device_token:
        return jsonify({'error': 'device_token is required'}), 400

    success = push_service.unregister_device(current_user_id, device_token)

    return jsonify({
        'success': success,
        'message': 'Device unregistered' if success else 'Device not found'
    })


@app.route("/api/notifications/test", methods=["POST"])
@token_required
def test_notification(current_user_id):
    """Send test notification"""
    result = push_service.send_notification(
        current_user_id,
        "ðŸ”” Test Notification",
        "VerzekAutoTrader push notifications are working!"
    )

    return jsonify(result)


# ============================
# ADVANCED ANALYTICS
# ============================

@app.route("/api/analytics/performance", methods=["GET"])
@token_required
def user_performance_analytics(current_user_id):
    """Get user performance analytics"""
    days = request.args.get('days', 30, type=int)
    performance = analytics_engine.get_user_performance(current_user_id, days)

    return jsonify(performance)


@app.route("/api/analytics/risk", methods=["GET"])
@token_required
def user_risk_metrics(current_user_id):
    """Get user risk metrics"""
    risk_metrics = analytics_engine.get_risk_metrics(current_user_id)

    return jsonify(risk_metrics)


@app.route("/api/analytics/platform", methods=["GET"])
@token_required
def platform_analytics(current_user_id):
    """Get platform-wide analytics (admin only)"""
    user = user_manager.get_user(current_user_id)

    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    days = request.args.get('days', 30, type=int)
    analytics = analytics_engine.get_platform_analytics(days)

    return jsonify(analytics)


# ============================
# ADVANCED ORDERS (Phase 3)
# ============================

@app.route("/api/orders/trailing-stop", methods=["POST"])
@token_required
def create_trailing_stop(current_user_id):
    """Create a trailing stop loss order"""
    data = request.json

    position_id = data.get('position_id')
    trail_percent = data.get('trail_percent', 0)
    trail_amount = data.get('trail_amount', 0)
    activation_price = data.get('activation_price')

    if not position_id:
        return jsonify({'error': 'position_id is required'}), 400

    result = advanced_order_manager.create_trailing_stop(
        current_user_id,
        position_id,
        trail_percent,
        trail_amount,
        activation_price
    )

    if result['success']:
        audit_logger.log_event(
            AuditEventType.TRADE_EXECUTED,
            user_id=current_user_id,
            ip_address=request.remote_addr,
            details={'action': 'create_trailing_stop', 'position_id': position_id}
        )

    return jsonify(result)


@app.route("/api/orders/oco", methods=["POST"])
@token_required
def create_oco_order(current_user_id):
    """Create a One-Cancels-Other order"""
    data = request.json

    position_id = data.get('position_id')
    take_profit_price = data.get('take_profit_price')
    stop_loss_price = data.get('stop_loss_price')
    quantity = data.get('quantity')

    if not all([position_id, take_profit_price, stop_loss_price]):
        return jsonify({'error': 'position_id, take_profit_price, and stop_loss_price are required'}), 400

    result = advanced_order_manager.create_oco_order(
        current_user_id,
        position_id,
        float(take_profit_price),
        float(stop_loss_price),
        float(quantity) if quantity else None
    )

    if result['success']:
        audit_logger.log_event(
            AuditEventType.TRADE_EXECUTED,
            user_id=current_user_id,
            ip_address=request.remote_addr,
            details={'action': 'create_oco_order', 'position_id': position_id}
        )

    return jsonify(result)


@app.route("/api/orders/oco/<oco_id>", methods=["DELETE"])
@token_required
def cancel_oco_order(current_user_id, oco_id):
    """Cancel an OCO order"""
    result = advanced_order_manager.cancel_oco_order(current_user_id, oco_id)

    if result['success']:
        audit_logger.log_event(
            AuditEventType.TRADE_EXECUTED,
            user_id=current_user_id,
            ip_address=request.remote_addr,
            details={'action': 'cancel_oco_order', 'oco_id': oco_id}
        )

    return jsonify(result)


@app.route("/api/orders/advanced", methods=["GET"])
@token_required
def get_advanced_orders(current_user_id):
    """Get all advanced orders for user"""
    orders = advanced_order_manager.get_user_advanced_orders(current_user_id)

    return jsonify(orders)


# ============================
# WEBHOOK INTEGRATION
# ============================

@app.route("/api/webhooks", methods=["POST"])
@token_required
def create_webhook(current_user_id):
    """Create a new webhook endpoint"""
    data = request.json

    name = data.get('name')
    source = data.get('source', 'custom')

    if not name:
        return jsonify({'error': 'name is required'}), 400

    result = webhook_handler.create_webhook(current_user_id, name, source)

    audit_logger.log_event(
        AuditEventType.SETTINGS_CHANGED,
        user_id=current_user_id,
        ip_address=request.remote_addr,
        details={'action': 'create_webhook', 'name': name}
    )

    return jsonify(result), 201


@app.route("/api/webhooks", methods=["GET"])
@token_required
def get_user_webhooks(current_user_id):
    """Get user's webhooks"""
    webhooks = webhook_handler.get_user_webhooks(current_user_id)

    return jsonify({'webhooks': webhooks})


@app.route("/api/webhooks/<webhook_id>/toggle", methods=["POST"])
@token_required
def toggle_webhook(current_user_id, webhook_id):
    """Enable/disable webhook"""
    data = request.json
    enabled = data.get('enabled', True)

    result = webhook_handler.toggle_webhook(current_user_id, webhook_id, enabled)

    return jsonify(result)


@app.route("/api/webhooks/<webhook_id>", methods=["DELETE"])
@token_required
def delete_webhook(current_user_id, webhook_id):
    """Delete webhook"""
    result = webhook_handler.delete_webhook(current_user_id, webhook_id)

    return jsonify(result)


@app.route("/api/webhook/<webhook_id>", methods=["POST"])
def receive_webhook_signal(webhook_id):
    """Receive signal from external webhook (no auth required)"""
    data = request.json
    signature = request.headers.get('X-Webhook-Signature')

    result = webhook_handler.process_webhook_signal(webhook_id, data, signature)

    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


# ============================
# POSITION MANAGEMENT
# ============================

@app.route("/api/positions/bulk-close", methods=["POST"])
@token_required
def bulk_close_positions(current_user_id):
    """Close multiple positions at once"""
    data = request.json
    position_ids = data.get('position_ids', [])

    if not position_ids:
        return jsonify({'error': 'position_ids is required'}), 400

    results = []
    for pos_id in position_ids:
        position = position_tracker.get_position(pos_id)
        if position and position.user_id == current_user_id and position.status == 'active':
            # Mark for closure
            position.status = 'pending_close'
            results.append({'position_id': pos_id, 'status': 'pending_close'})

    position_tracker.save_positions()

    audit_logger.log_event(
        AuditEventType.TRADE_EXECUTED,
        user_id=current_user_id,
        ip_address=request.remote_addr,
        details={'action': 'bulk_close', 'count': len(results)}
    )

    return jsonify({
        'success': True,
        'closed': len(results),
        'positions': results
    })


@app.route("/api/positions/emergency-exit", methods=["POST"])
@token_required
def emergency_exit(current_user_id):
    """Emergency exit - close ALL active positions"""
    positions = position_tracker.load_positions()
    closed_count = 0

    for position in positions:
        if position.user_id == current_user_id and position.status == 'active':
            position.status = 'emergency_close'
            closed_count += 1

    position_tracker.save_positions()

    audit_logger.log_event(
        AuditEventType.TRADE_EXECUTED,
        user_id=current_user_id,
        ip_address=request.remote_addr,
        details={'action': 'emergency_exit', 'count': closed_count},
        severity='critical'
    )

    log_event("POSITION_MGMT", f"âš ï¸ EMERGENCY EXIT triggered by user {current_user_id}: {closed_count} positions")

    return jsonify({
        'success': True,
        'message': f'Emergency exit initiated for {closed_count} positions',
        'closed_count': closed_count
    })


@app.route("/api/positions/limits", methods=["POST"])
@token_required
def set_position_limits(current_user_id):
    """Set position limits for user"""
    data = request.json

    user = user_manager.get_user(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Set position limits
    if 'max_positions' in data:
        user.max_positions = int(data['max_positions'])
    if 'max_exposure' in data:
        user.max_exposure = float(data['max_exposure'])
    if 'max_position_size' in data:
        user.max_position_size = float(data['max_position_size'])

    user_manager._save_user_to_db(user)

    audit_logger.log_event(
        AuditEventType.SETTINGS_CHANGED,
        user_id=current_user_id,
        ip_address=request.remote_addr,
        details={'action': 'set_position_limits', 'limits': data}
    )

    return jsonify({
        'success': True,
        'limits': {
            'max_positions': getattr(user, 'max_positions', None),
            'max_exposure': getattr(user, 'max_exposure', None),
            'max_position_size': getattr(user, 'max_position_size', None)
        }
    })


@app.route("/api/positions/limits", methods=["GET"])
@token_required
def get_position_limits(current_user_id):
    """Get position limits for user"""
    user = user_manager.get_user(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'limits': {
            'max_positions': getattr(user, 'max_positions', None),
            'max_exposure': getattr(user, 'max_exposure', None),
            'max_position_size': getattr(user, 'max_position_size', None)
        }
    })


# ============================
# PHASE 4: PORTFOLIO REBALANCING
# ============================

@app.route("/api/portfolio/allocation", methods=["POST"])
@token_required
def set_portfolio_allocation(current_user_id):
    """Set target portfolio allocation"""
    data = request.json
    allocations = data.get('allocations', {})

    result = portfolio_rebalancer.set_allocation(current_user_id, allocations)
    return jsonify(result)


@app.route("/api/portfolio/allocation", methods=["GET"])
@token_required
def get_portfolio_allocation(current_user_id):
    """Get current and target portfolio allocation"""
    current = portfolio_rebalancer.get_current_allocation(current_user_id)
    drift = portfolio_rebalancer.get_allocation_drift(current_user_id)

    return jsonify({
        'current_allocation': current,
        'drift': drift
    })


@app.route("/api/portfolio/rebalance", methods=["POST"])
@token_required
def rebalance_portfolio(current_user_id):
    """Execute portfolio rebalancing"""
    data = request.json
    dry_run = data.get('dry_run', True)

    result = portfolio_rebalancer.execute_rebalance(current_user_id, dry_run=dry_run)
    return jsonify(result)


@app.route("/api/portfolio/auto-rebalance", methods=["POST"])
@token_required
def enable_auto_rebalance(current_user_id):
    """Enable automatic rebalancing"""
    data = request.json
    threshold = data.get('threshold', 5.0)

    result = portfolio_rebalancer.enable_auto_rebalance(current_user_id, threshold)
    return jsonify(result)


# ============================
# PHASE 4: ADVANCED ANALYTICS
# ============================

@app.route("/api/analytics/patterns/<symbol>", methods=["GET"])
@token_required
def detect_patterns(current_user_id, symbol):
    """Detect trading patterns for a symbol"""
    result = advanced_analytics.detect_patterns(symbol)
    return jsonify(result)


@app.route("/api/analytics/predict/<symbol>", methods=["GET"])
@token_required
def predict_price(current_user_id, symbol):
    """Predict future price movement"""
    hours_ahead = request.args.get('hours', 24, type=int)
    result = advanced_analytics.predict_price_movement(symbol, hours_ahead)
    return jsonify(result)


@app.route("/api/analytics/win-probability", methods=["POST"])
@token_required
def calculate_win_probability(current_user_id):
    """Calculate win probability for a trade"""
    data = request.json
    symbol = data.get('symbol')
    side = data.get('side')

    result = advanced_analytics.calculate_win_probability(current_user_id, symbol, side)
    return jsonify(result)


@app.route("/api/analytics/sentiment/<symbol>", methods=["GET"])
@token_required
def get_market_sentiment(current_user_id, symbol):
    """Get market sentiment analysis"""
    result = advanced_analytics.get_market_sentiment(symbol)
    return jsonify(result)


# ============================
# PHASE 4: SOCIAL TRADING
# ============================

@app.route("/api/social/become-master", methods=["POST"])
@token_required
def become_master(current_user_id):
    """Register as a master trader"""
    data = request.json
    result = social_trading.become_master_trader(current_user_id, data)
    return jsonify(result)


@app.route("/api/social/masters", methods=["GET"])
@token_required
def get_top_masters(current_user_id):
    """Get top performing master traders"""
    limit = request.args.get('limit', 10, type=int)
    sort_by = request.args.get('sort_by', 'pnl')

    masters = social_trading.get_top_masters(limit, sort_by)
    return jsonify({'masters': masters})


@app.route("/api/social/copy", methods=["POST"])
@token_required
def copy_master(current_user_id):
    """Start copying a master trader"""
    data = request.json
    master_id = data.get('master_id')
    settings = data.get('settings', {})

    result = social_trading.copy_trader(current_user_id, master_id, settings)
    return jsonify(result)


@app.route("/api/social/stop-copy", methods=["POST"])
@token_required
def stop_copy(current_user_id):
    """Stop copying a master trader"""
    data = request.json
    copy_id = data.get('copy_id')

    result = social_trading.stop_copying(current_user_id, copy_id)
    return jsonify(result)


# ============================
# PHASE 4: CUSTOM INDICATORS
# ============================

@app.route("/api/indicators", methods=["POST"])
@token_required
def create_indicator(current_user_id):
    """Create custom indicator"""
    data = request.json
    result = custom_indicators.create_indicator(current_user_id, data)
    return jsonify(result)


@app.route("/api/strategies", methods=["POST"])
@token_required
def create_strategy(current_user_id):
    """Create custom trading strategy"""
    data = request.json
    result = custom_indicators.create_strategy(current_user_id, data)
    return jsonify(result)


@app.route("/api/strategies", methods=["GET"])
@token_required
def get_strategies(current_user_id):
    """Get user's custom strategies"""
    strategies = custom_indicators.get_user_strategies(current_user_id)
    return jsonify({'strategies': strategies})


@app.route("/api/strategies/<strategy_id>/toggle", methods=["POST"])
@token_required
def toggle_strategy(current_user_id, strategy_id):
    """Enable/disable a strategy"""
    data = request.json
    enabled = data.get('enabled', True)

    result = custom_indicators.toggle_strategy(current_user_id, strategy_id, enabled)
    return jsonify(result)


@app.route("/api/strategies/<strategy_id>", methods=["DELETE"])
@token_required
def delete_strategy(current_user_id, strategy_id):
    """Delete a custom strategy"""
    result = custom_indicators.delete_strategy(current_user_id, strategy_id)
    return jsonify(result)


@app.route("/api/strategies/<strategy_id>/evaluate", methods=["POST"])
@token_required
def evaluate_strategy(current_user_id, strategy_id):
    """Evaluate strategy against current market data"""
    data = request.json
    market_data = data.get('market_data', {})

    result = custom_indicators.evaluate_strategy(strategy_id, market_data)
    return jsonify(result)


# ============================
# PHASE 4: BACKTESTING
# ============================

@app.route("/api/backtest", methods=["POST"])
@token_required
def run_backtest(current_user_id):
    """Run strategy backtest"""
    data = request.json
    strategy_config = data.get('strategy')
    symbol = data.get('symbol', 'BTCUSDT')
    days = data.get('days', 30)

    result = backtesting_engine.backtest_strategy(strategy_config, symbol, days)
    return jsonify(result)


@app.route("/api/backtest/history", methods=["GET"])
@token_required
def get_backtest_history(current_user_id):
    """Get backtest history"""
    history = backtesting_engine.get_backtest_history(current_user_id)
    return jsonify({'history': history})


# ============================
# PHASE 5: AI TRADE ASSISTANT
# ============================

@app.route("/api/ai/analyze-signal", methods=["POST"])
@token_required
def ai_analyze_signal(current_user_id):
    """AI-powered signal analysis"""
    data = request.json
    result = ai_assistant.analyze_signal(data)
    return jsonify(result)


@app.route("/api/ai/recommend-trade", methods=["POST"])
@token_required
def ai_recommend_trade(current_user_id):
    """AI trade recommendation"""
    market_data = request.json.get('market_data', {})
    user_profile = request.json.get('user_profile', {})
    result = ai_assistant.generate_trade_recommendation(market_data, user_profile)
    return jsonify(result)


@app.route("/api/ai/analyze-portfolio", methods=["POST"])
@token_required
def ai_analyze_portfolio(current_user_id):
    """AI portfolio analysis"""
    positions = position_tracker.get_user_positions(current_user_id)
    market_conditions = request.json.get('market_conditions', {})
    result = ai_assistant.analyze_portfolio(positions, market_conditions)
    return jsonify(result)


@app.route("/api/ai/predict-market", methods=["POST"])
@token_required
def ai_predict_market(current_user_id):
    """AI market prediction"""
    data = request.json
    result = ai_assistant.predict_market_movement(
        data.get('symbol'),
        data.get('timeframe'),
        data.get('historical_data', [])
    )
    return jsonify(result)


@app.route("/api/ai/sentiment", methods=["POST"])
@token_required
def ai_sentiment(current_user_id):
    """AI sentiment analysis"""
    data = request.json
    result = ai_assistant.sentiment_analysis(
        data.get('news', []),
        data.get('social_media', [])
    )
    return jsonify(result)


@app.route("/api/ai/chat", methods=["POST"])
@token_required
def ai_chat(current_user_id):
    """AI trading assistant chat"""
    data = request.json
    result = ai_assistant.chat_assistant(
        data.get('message'),
        data.get('conversation_history', [])
    )
    return jsonify(result)


# ============================
# PHASE 5: MULTI-TIMEFRAME ANALYSIS
# ============================

@app.route("/api/analysis/multi-timeframe", methods=["POST"])
@token_required
def multi_timeframe_analysis(current_user_id):
    """Multi-timeframe analysis"""
    data = request.json
    result = mtf_analyzer.analyze_multiple_timeframes(
        data.get('symbol'),
        data.get('price_data', {})
    )
    return jsonify(result)


@app.route("/api/analysis/divergence", methods=["POST"])
@token_required
def detect_divergence(current_user_id):
    """Detect price/indicator divergence"""
    data = request.json
    result = mtf_analyzer.detect_divergence(
        data.get('price_data', []),
        data.get('indicator', 'rsi')
    )
    return jsonify(result)


# ============================
# PHASE 5: SMART ORDER ROUTING
# ============================

@app.route("/api/routing/best-execution", methods=["POST"])
@token_required
def find_best_execution(current_user_id):
    """Find best execution across exchanges"""
    data = request.json
    result = order_router.find_best_execution(
        data.get('symbol'),
        data.get('side'),
        data.get('quantity'),
        data.get('exchange_prices', {})
    )
    return jsonify(result)


@app.route("/api/routing/split-order", methods=["POST"])
@token_required
def split_order(current_user_id):
    """Split order across exchanges"""
    data = request.json
    result = order_router.split_order_across_exchanges(
        data.get('symbol'),
        data.get('side'),
        data.get('quantity'),
        data.get('exchange_prices', {}),
        data.get('max_exchanges', 3)
    )
    return jsonify(result)


@app.route("/api/routing/price-impact", methods=["POST"])
@token_required
def analyze_price_impact(current_user_id):
    """Analyze price impact"""
    data = request.json
    result = order_router.analyze_price_impact(
        data.get('symbol'),
        data.get('quantity'),
        data.get('orderbook', [])
    )
    return jsonify(result)


@app.route("/api/routing/recommend-strategy", methods=["POST"])
@token_required
def recommend_execution_strategy(current_user_id):
    """Recommend execution strategy"""
    data = request.json
    result = order_router.recommend_execution_strategy(
        data.get('symbol'),
        data.get('side'),
        data.get('quantity'),
        data.get('urgency', 'medium'),
        data.get('exchange_data', {})
    )
    return jsonify(result)


# ============================
# PHASE 5: SOCIAL FEATURES
# ============================

@app.route("/api/social/chat/send", methods=["POST"])
@token_required
def send_chat_message(current_user_id):
    """Send chat message"""
    data = request.json
    result = social_features.send_message(
        data.get('room_id'),
        current_user_id,
        data.get('username'),
        data.get('message')
    )
    return jsonify(result)


@app.route("/api/social/chat/messages/<room_id>", methods=["GET"])
@token_required
def get_chat_messages(current_user_id, room_id):
    """Get chat messages"""
    limit = request.args.get('limit', 50, type=int)
    result = social_features.get_messages(room_id, limit)
    return jsonify(result)


@app.route("/api/social/chat/rooms", methods=["GET"])
@token_required
def get_chat_rooms(current_user_id):
    """Get active chat rooms"""
    result = social_features.get_active_rooms()
    return jsonify(result)


@app.route("/api/social/leaderboard", methods=["GET"])
@token_required
def get_leaderboard(current_user_id):
    """Get leaderboard"""
    period = request.args.get('period', 'all_time')
    limit = request.args.get('limit', 100, type=int)
    result = social_features.get_leaderboard(period, limit)
    return jsonify(result)


@app.route("/api/social/leaderboard/rank", methods=["GET"])
@token_required
def get_user_rank(current_user_id):
    """Get user rank"""
    period = request.args.get('period', 'all_time')
    result = social_features.get_user_rank(current_user_id, period)
    return jsonify(result)


@app.route("/api/social/competitions", methods=["GET"])
@token_required
def get_competitions(current_user_id):
    """Get competitions"""
    status = request.args.get('status', 'active')
    result = social_features.get_competitions(status)
    return jsonify(result)


@app.route("/api/social/competitions/<competition_id>/join", methods=["POST"])
@token_required
def join_competition(current_user_id, competition_id):
    """Join competition"""
    data = request.json
    result = social_features.join_competition(
        competition_id,
        current_user_id,
        data.get('username')
    )
    return jsonify(result)


@app.route("/api/social/competitions/<competition_id>/leaderboard", methods=["GET"])
@token_required
def get_competition_leaderboard(current_user_id, competition_id):
    """Get competition leaderboard"""
    result = social_features.get_competition_leaderboard(competition_id)
    return jsonify(result)


# ============================
# PHASE 5: ADVANCED CHARTING
# ============================

@app.route("/api/charting/indicator", methods=["POST"])
@token_required
def calculate_indicator(current_user_id):
    """Calculate technical indicator"""
    data = request.json
    result = chart_system.calculate_indicator(
        data.get('indicator'),
        data.get('price_data', []),
        data.get('params', {})
    )
    return jsonify(result)


@app.route("/api/charting/config", methods=["POST"])
@token_required
def generate_chart_config(current_user_id):
    """Generate chart configuration"""
    data = request.json
    result = chart_system.generate_chart_config(
        data.get('indicators', []),
        data.get('params', {})
    )
    return jsonify(result)


# ============================
# PHASE 5: AUTO-OPTIMIZATION
# ============================

@app.route("/api/optimization/optimize", methods=["POST"])
@token_required
def optimize_strategy(current_user_id):
    """Optimize strategy parameters"""
    data = request.json
    result = auto_optimizer.optimize_strategy(
        data.get('strategy_name'),
        data.get('historical_trades', []),
        data.get('parameter_ranges', {})
    )
    return jsonify(result)


@app.route("/api/optimization/backtest", methods=["POST"])
@token_required
def backtest_parameters(current_user_id):
    """Backtest parameters"""
    data = request.json
    result = auto_optimizer.backtest_parameters(
        data.get('params', {}),
        data.get('historical_data', [])
    )
    return jsonify(result)


@app.route("/api/optimization/suggestions", methods=["POST"])
@token_required
def get_optimization_suggestions(current_user_id):
    """Get optimization suggestions"""
    data = request.json
    result = auto_optimizer.suggest_improvements(data)
    return jsonify(result)


# ============================
# PHASE 5: AI RISK SCORING
# ============================

@app.route("/api/risk/position", methods=["POST"])
@token_required
def evaluate_position_risk(current_user_id):
    """Evaluate position risk"""
    data = request.json
    result = risk_scorer.evaluate_position_risk(
        data.get('position', {}),
        data.get('market_data', {}),
        data.get('user_settings', {})
    )
    return jsonify(result)


@app.route("/api/risk/portfolio", methods=["GET"])
@token_required
def evaluate_portfolio_risk(current_user_id):
    """Evaluate portfolio risk"""
    positions = position_tracker.get_user_positions(current_user_id)
    user_data = user_manager.get_user_by_id(current_user_id)
    balance = float(user_data.get('balance', 10000)) if user_data else 10000
    market_conditions = request.json.get('market_conditions', {}) if request.json else {}
    result = risk_scorer.evaluate_portfolio_risk(positions, balance, market_conditions)
    return jsonify(result)


@app.route("/api/risk/var", methods=["POST"])
@token_required
def calculate_var(current_user_id):
    """Calculate Value at Risk"""
    positions = position_tracker.get_user_positions(current_user_id)
    data = request.json
    result = risk_scorer.calculate_var(
        positions,
        data.get('confidence_level', 0.95),
        data.get('time_horizon_days', 1)
    )
    return jsonify(result)


@app.route("/api/risk/stress-test", methods=["POST"])
@token_required
def run_stress_test(current_user_id):
    """Run portfolio stress test"""
    positions = position_tracker.get_user_positions(current_user_id)
    data = request.json
    result = risk_scorer.stress_test(
        positions,
        data.get('scenarios', [])
    )
    return jsonify(result)


# ============================
# PHASE 5: TRADING JOURNAL
# ============================

@app.route("/api/journal/entry", methods=["POST"])
@token_required
def add_journal_entry(current_user_id):
    """Add journal entry"""
    data = request.json
    result = trading_journal.add_entry(
        current_user_id,
        data.get('trade', {}),
        data.get('notes', ''),
        data.get('emotions', [])
    )
    return jsonify(result)


@app.route("/api/journal/entries", methods=["GET"])
@token_required
def get_journal_entries(current_user_id):
    """Get journal entries"""
    limit = request.args.get('limit', 50, type=int)
    result = trading_journal.get_entries(current_user_id, limit)
    return jsonify(result)


@app.route("/api/journal/patterns", methods=["GET"])
@token_required
def analyze_journal_patterns(current_user_id):
    """Analyze trading patterns"""
    result = trading_journal.analyze_patterns(current_user_id)
    return jsonify(result)


@app.route("/api/journal/insights", methods=["GET"])
@token_required
def get_journal_insights(current_user_id):
    """Get trading insights"""
    result = trading_journal.generate_insights(current_user_id)
    return jsonify(result)


# ============================
# TELEGRAM WEBHOOK ENDPOINT
# ============================

@app.route("/webhook/broadcast", methods=["POST"])
def telegram_webhook():
    """Webhook endpoint for Telegram broadcast bot"""
    try:
        update_data = request.get_json()

        if not update_data:
            log_event("WEBHOOK", "No JSON data received")
            return jsonify({"ok": False, "error": "No data"}), 400

        log_event("WEBHOOK", f"Received webhook update: {update_data}")

        # Import and process the update using the broadcast bot handler
        import broadcast_bot_webhook_handler
        broadcast_bot_webhook_handler.handle_webhook_update(update_data)

        return jsonify({"ok": True})
    except Exception as e:
        log_event("WEBHOOK", f"Error processing webhook: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": True}), 200  # Return 200 even on error to prevent Telegram retries


@app.route("/api/broadcast/signal", methods=["POST"])
def receive_signal_from_telethon():
    """Direct signal receiver from Telethon forwarder (faster than Telegram webhooks)"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"ok": False, "error": "No signal text provided"}), 400
        
        text = data.get('text', '').strip()
        source = data.get('source', 'Unknown')
        source_type = data.get('source_type', 'unknown')
        
        if not text:
            return jsonify({"ok": False, "error": "Empty signal text"}), 400
        
        log_event("SIGNAL", f"Received signal from Telethon: {source} ({source_type})")
        
        # Import and process using broadcast handler
        import broadcast_bot_webhook_handler
        
        # Create a minimal message structure for compatibility
        fake_message_data = {
            'message': {
                'text': text,
                'from': {'id': int(os.getenv("ADMIN_CHAT_ID", "0"))},
                'chat': {
                    'id': int(os.getenv("ADMIN_CHAT_ID", "0")),
                    'type': 'private' if source_type == 'personal_chat' else 'supergroup',
                    'title': source,
                    'username': source
                }
            }
        }
        
        broadcast_bot_webhook_handler.handle_webhook_update(fake_message_data)
        
        return jsonify({"ok": True, "message": "Signal processed"})
    except Exception as e:
        log_event("SIGNAL", f"Error processing signal from Telethon: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    log_event("API", f"Starting Flask API on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
