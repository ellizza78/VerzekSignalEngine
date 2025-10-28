# ==========================================================
# Verzek Auto Trader – Replit Bridge API (Production)
# ==========================================================
# Purpose:
# Acts as a simple HTTPS bridge between my mobile app
# (https://verzek-auto-trader.replit.app)
# and the live backend running on my Vultr server.
# ==========================================================

from flask import Flask, request, jsonify
import requests
import logging

app = Flask("VerzekBridge")

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("VerzekBridge")

# === My live backend server (Vultr) ===
VULTR_BACKEND = "http://80.240.29.142:5000"

@app.route("/")
def home():
    """Bridge status endpoint"""
    logger.info("Bridge status check")
    return jsonify({
        "bridge": "VerzekAutoTrader",
        "status": "running",
        "backend": VULTR_BACKEND,
        "message": "HTTPS bridge active - forwarding to Vultr backend"
    })

@app.route("/ping")
def ping():
    """Forward ping requests to Vultr"""
    logger.info("Forwarding /ping to Vultr")
    try:
        r = requests.get(f"{VULTR_BACKEND}/ping", timeout=6)
        return jsonify(r.json()), r.status_code
    except requests.exceptions.Timeout:
        logger.error("Vultr backend timeout on /ping")
        return jsonify({"error": "Backend timeout"}), 504
    except Exception as e:
        logger.error(f"Error forwarding /ping: {str(e)}")
        return jsonify({"error": str(e)}), 502

@app.route("/status")
def status():
    """Forward system status to Vultr"""
    logger.info("Forwarding /status to Vultr")
    try:
        r = requests.get(f"{VULTR_BACKEND}/status", timeout=6)
        return jsonify(r.json()), r.status_code
    except requests.exceptions.Timeout:
        logger.error("Vultr backend timeout on /status")
        return jsonify({"error": "Backend timeout"}), 504
    except Exception as e:
        logger.error(f"Error forwarding /status: {str(e)}")
        return jsonify({"error": str(e)}), 502

@app.route("/signals")
def signals():
    """Forward signals or trade logs"""
    logger.info("Forwarding /signals to Vultr")
    try:
        r = requests.get(f"{VULTR_BACKEND}/logs", timeout=6)
        return jsonify(r.json()), r.status_code
    except requests.exceptions.Timeout:
        logger.error("Vultr backend timeout on /signals")
        return jsonify({"error": "Backend timeout"}), 504
    except Exception as e:
        logger.error(f"Error forwarding /signals: {str(e)}")
        return jsonify({"error": str(e)}), 502

@app.route("/api/<path:endpoint>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def api_proxy(endpoint):
    """Forward all /api/* requests to Vultr backend"""
    logger.info(f"Forwarding /api/{endpoint} [{request.method}] to Vultr")
    try:
        url = f"{VULTR_BACKEND}/api/{endpoint}"
        
        # Forward the request with the same method, headers, and data
        r = requests.request(
            method=request.method,
            url=url,
            headers={key: value for key, value in request.headers if key.lower() != 'host'},
            data=request.get_data(),
            params=request.args,
            timeout=10
        )
        
        # Return the response from Vultr
        return r.content, r.status_code, r.headers.items()
    except requests.exceptions.Timeout:
        logger.error(f"Vultr backend timeout on /api/{endpoint}")
        return jsonify({"error": "Backend timeout"}), 504
    except Exception as e:
        logger.error(f"Error forwarding /api/{endpoint}: {str(e)}")
        return jsonify({"error": str(e)}), 502

@app.route("/health")
def health():
    """Health check endpoint for Replit"""
    return jsonify({"status": "healthy", "bridge": "active"}), 200

if __name__ == "__main__":
    logger.info("🌉 VerzekBridge starting...")
    logger.info(f"🎯 Forwarding to: {VULTR_BACKEND}")
    logger.info("🔒 HTTPS endpoint: https://verzek-auto-trader.replit.app")
    
    # Replit serves public apps on port 5000 (mapped to port 80 externally)
    app.run(host="0.0.0.0", port=5000)
