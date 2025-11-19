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
