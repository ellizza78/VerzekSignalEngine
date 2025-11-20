"""
Signal Engine Webhook Server
Receives webhook notifications from VerzekAutoTrader backend when positions close.
This enables real-time signal closure tracking in the Signal Tracker database.
"""

import os
import sys
import logging
from flask import Flask, request, jsonify
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.tracker import SignalTracker
from core.models import SignalOutcome

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize tracker
tracker = None

def get_tracker():
    """Get or create tracker instance"""
    global tracker
    if tracker is None:
        tracker = SignalTracker()
    return tracker


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'signal-engine-webhooks',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/signals/close', methods=['POST'])
def close_signal():
    """
    Close a signal when position is closed in backend.
    
    Authentication: Required via SIGNAL_ENGINE_WEBHOOK_SECRET header
    
    Expected payload:
    {
        "signal_id": "abc-123-def",
        "exit_price": 50200.50,
        "close_reason": "TP"  // or "SL", "CANCEL", "REVERSAL"
    }
    
    Returns:
    {
        "status": "success",
        "outcome": {
            "signal_id": "abc-123-def",
            "profit_pct": 2.5,
            "duration_minutes": 45,
            "close_reason": "TP"
        }
    }
    """
    try:
        # Verify authentication (shared secret)
        expected_secret = os.getenv('SIGNAL_ENGINE_WEBHOOK_SECRET', 'dev-secret-change-in-prod')
        provided_secret = request.headers.get('X-Webhook-Secret')
        
        if not provided_secret or provided_secret != expected_secret:
            logger.warning(f"Unauthorized webhook attempt from {request.remote_addr}")
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized: Invalid or missing X-Webhook-Secret header'
            }), 401
        
        # Validate request
        if not request.json:
            return jsonify({
                'status': 'error',
                'message': 'Invalid JSON payload'
            }), 400
        
        data = request.json
        signal_id = data.get('signal_id')
        exit_price = data.get('exit_price')
        close_reason = data.get('close_reason')
        
        # Validate required fields
        if not signal_id:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: signal_id'
            }), 400
        
        if not exit_price:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: exit_price'
            }), 400
        
        if not close_reason:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: close_reason'
            }), 400
        
        # Validate close_reason
        valid_reasons = ['TP', 'SL', 'CANCEL', 'REVERSAL']
        if close_reason not in valid_reasons:
            return jsonify({
                'status': 'error',
                'message': f'Invalid close_reason. Must be one of: {valid_reasons}'
            }), 400
        
        # Convert exit_price to float
        try:
            exit_price = float(exit_price)
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'message': 'exit_price must be a number'
            }), 400
        
        # Close signal in tracker
        tracker_instance = get_tracker()
        outcome = tracker_instance.close_signal(signal_id, exit_price, close_reason)
        
        if outcome:
            logger.info(
                f"Signal closed: {signal_id} | "
                f"Profit: {outcome.profit_pct:.2f}% | "
                f"Duration: {outcome.duration_minutes}m | "
                f"Reason: {close_reason}"
            )
            
            return jsonify({
                'status': 'success',
                'outcome': {
                    'signal_id': outcome.signal_id,
                    'profit_pct': outcome.profit_pct,
                    'duration_minutes': outcome.duration_minutes,
                    'close_reason': outcome.close_reason,
                    'closed_at': outcome.closed_at.isoformat()
                }
            }), 200
        else:
            logger.warning(f"Signal not found: {signal_id}")
            return jsonify({
                'status': 'error',
                'message': f'Signal not found: {signal_id}'
            }), 404
    
    except Exception as e:
        logger.error(f"Error closing signal: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/signals/tp-hit', methods=['POST'])
def tp_hit():
    """
    Record a take-profit target hit (partial or final).
    
    Authentication: Required via SIGNAL_ENGINE_WEBHOOK_SECRET header
    
    Expected payload:
    {
        "signal_id": "abc-123-def",
        "hit_price": 51500.00,
        "tp_number": 1  // Optional: 1-5
    }
    
    Returns:
    {
        "status": "success",
        "outcome": {
            "signal_id": "abc-123-def",
            "profit_pct": 3.0,
            "is_final": false,  // false for TP1-TP4, true for TP5
            "current_tp_index": 0,  // 0 for TP1, 4 for TP5
            "total_tps": 5
        }
    }
    """
    try:
        # Verify authentication
        expected_secret = os.getenv('SIGNAL_ENGINE_WEBHOOK_SECRET', 'dev-secret-change-in-prod')
        provided_secret = request.headers.get('X-Webhook-Secret')
        
        if not provided_secret or provided_secret != expected_secret:
            logger.warning(f"Unauthorized TP webhook attempt from {request.remote_addr}")
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized: Invalid or missing X-Webhook-Secret header'
            }), 401
        
        # Validate request
        if not request.json:
            return jsonify({
                'status': 'error',
                'message': 'Invalid JSON payload'
            }), 400
        
        data = request.json
        signal_id = data.get('signal_id')
        hit_price = data.get('hit_price')
        tp_number = data.get('tp_number')
        
        # Validate required fields
        if not signal_id:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: signal_id'
            }), 400
        
        if not hit_price:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: hit_price'
            }), 400
        
        # Convert to correct types
        try:
            hit_price = float(hit_price)
            if tp_number is not None:
                tp_number = int(tp_number)
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'message': 'Invalid data types for hit_price or tp_number'
            }), 400
        
        # Record TP hit in tracker
        tracker_instance = get_tracker()
        outcome = tracker_instance.on_target_hit(signal_id, hit_price, tp_number)
        
        if outcome:
            tp_level = outcome.current_tp_index + 1
            status_text = "FINAL" if outcome.is_final else "Partial"
            
            logger.info(
                f"TP{tp_level} HIT ({status_text}): {signal_id[:8]} | "
                f"Profit: {outcome.profit_pct:.2f}% | "
                f"is_final: {outcome.is_final}"
            )
            
            return jsonify({
                'status': 'success',
                'outcome': {
                    'signal_id': outcome.signal_id,
                    'symbol': outcome.symbol,
                    'profit_pct': outcome.profit_pct,
                    'is_final': outcome.is_final,
                    'current_tp_index': outcome.current_tp_index,
                    'total_tps': outcome.total_tps,
                    'duration_formatted': outcome.duration_formatted,
                    'close_reason': outcome.close_reason
                }
            }), 200
        else:
            logger.warning(f"Signal not found or already closed: {signal_id}")
            return jsonify({
                'status': 'error',
                'message': f'Signal not found or already closed: {signal_id}'
            }), 404
    
    except Exception as e:
        logger.error(f"Error recording TP hit: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/signals/stats', methods=['GET'])
def get_stats():
    """
    Get current signal statistics.
    
    Returns:
    {
        "active_signals": 15,
        "closed_signals": 142,
        "total_signals": 157,
        "win_rate": 68.5,
        "avg_profit": 1.85
    }
    """
    try:
        tracker_instance = get_tracker()
        stats = tracker_instance.get_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500


if __name__ == '__main__':
    logger.info("Starting Signal Engine Webhook Server on 0.0.0.0:8050")
    app.run(host='0.0.0.0', port=8050, debug=False)
