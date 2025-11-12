#!/usr/bin/env python3
"""
Verzek AutoTrader API Server
Production-ready Flask application with JWT authentication
Entry point: api_server:app for Gunicorn
"""
import os
import sys

# Add current directory to sys.path for absolute imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize database
from db import init_db, engine, Base

# Import route blueprints
from auth_routes import bp as auth_bp
from users_routes import bp as users_bp
from signals_routes import bp as signals_bp
from positions_routes import bp as positions_bp
from payments_routes import bp as payments_bp
from admin_routes import bp as admin_bp

# Create Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, origins=["*"], supports_credentials=True)

# Configure JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET", "VerzekAutoTraderKey2025")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60 * 60  # 1 hour
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 60 * 60 * 24 * 30  # 30 days

jwt = JWTManager(app)

# Initialize database tables
try:
    with engine.begin() as conn:
        Base.metadata.create_all(bind=conn)
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"❌ Database initialization error: {e}")


# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(users_bp, url_prefix="/api/users")
app.register_blueprint(signals_bp, url_prefix="/api/signals")
app.register_blueprint(positions_bp, url_prefix="/api/positions")
app.register_blueprint(payments_bp, url_prefix="/api/payments")
app.register_blueprint(admin_bp, url_prefix="/api/admin")


# Health check endpoints
@app.route('/api/ping', methods=['GET'])
def ping():
    """Ping endpoint for basic connectivity check"""
    return jsonify({
        "status": "ok",
        "service": "VerzekBackend",
        "version": "2.1",
        "message": "Backend responding successfully 🚀"
    }), 200


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint with timestamp"""
    from datetime import datetime
    return jsonify({
        "ok": True,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200


@app.route('/api/system/ip', methods=['GET'])
def get_system_ip():
    """Get system IP (for mobile app compatibility)"""
    return jsonify({
        "ok": True,
        "ip": os.getenv("SERVER_IP", "80.240.29.142")
    }), 200


@app.route('/api/safety/status', methods=['GET'])
def safety_status():
    """Safety/system status endpoint"""
    return jsonify({
        "ok": True,
        "active_workers": 1,
        "mode": os.getenv("EXCHANGE_MODE", "paper"),
        "status": "operational"
    }), 200


@app.route('/api/reports/daily', methods=['GET'])
def get_daily_report():
    """Get latest daily trading report"""
    from reports.daily_report import get_latest_report
    
    report = get_latest_report()
    if report:
        return jsonify({"ok": True, "report": report}), 200
    else:
        return jsonify({"ok": False, "error": "Report not available"}), 404


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"ok": False, "error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"ok": False, "error": "Internal server error"}), 500


# Flask app runner (for development)
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8050"))
    print(f"🚀 Starting Verzek Auto Trader API Server (v2.1)...")
    print(f"📍 Running on http://0.0.0.0:{port}")
    print(f"🔧 Mode: {os.getenv('EXCHANGE_MODE', 'paper')}")
    print(f"📋 Registered routes:")
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            print(f"   {rule.rule} -> {rule.endpoint}")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.getenv("FLASK_ENV") == "development"
    )
