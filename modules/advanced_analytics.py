import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from typing import Dict, List, Optional
import json
import os
from datetime import datetime, timedelta

class AdvancedAnalytics:
    """ML-powered analytics and pattern recognition"""
    
    def __init__(self, position_tracker):
        self.position_tracker = position_tracker
        self.price_history_file = "database/price_history.json"
        self.predictions_file = "database/ml_predictions.json"
        
    def _load_price_history(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Load price history for analysis"""
        if os.path.exists(self.price_history_file):
            try:
                with open(self.price_history_file, 'r') as f:
                    history = json.load(f)
                    if symbol in history:
                        df = pd.DataFrame(history[symbol])
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        return df.tail(days * 24)
            except:
                pass
        return pd.DataFrame()
    
    def detect_patterns(self, symbol: str) -> Dict:
        """Detect technical patterns using ML"""
        df = self._load_price_history(symbol)
        
        if df.empty or len(df) < 20:
            return {'success': False, 'error': 'Insufficient data'}
        
        patterns = []
        
        prices = df['price'].values
        
        if len(prices) >= 20:
            sma_20 = np.mean(prices[-20:])
            current = prices[-1]
            
            if current > sma_20 * 1.02:
                patterns.append({
                    'pattern': 'Bullish Momentum',
                    'confidence': 0.75,
                    'signal': 'BUY',
                    'description': 'Price is 2%+ above 20-period SMA'
                })
            elif current < sma_20 * 0.98:
                patterns.append({
                    'pattern': 'Bearish Momentum',
                    'confidence': 0.75,
                    'signal': 'SELL',
                    'description': 'Price is 2%+ below 20-period SMA'
                })
        
        if len(prices) >= 50:
            sma_20 = np.mean(prices[-20:])
            sma_50 = np.mean(prices[-50:])
            
            if sma_20 > sma_50 and prices[-21] <= np.mean(prices[-51:-21]):
                patterns.append({
                    'pattern': 'Golden Cross',
                    'confidence': 0.85,
                    'signal': 'BUY',
                    'description': '20 SMA crossed above 50 SMA'
                })
            elif sma_20 < sma_50 and prices[-21] >= np.mean(prices[-51:-21]):
                patterns.append({
                    'pattern': 'Death Cross',
                    'confidence': 0.85,
                    'signal': 'SELL',
                    'description': '20 SMA crossed below 50 SMA'
                })
        
        recent_high = np.max(prices[-14:])
        recent_low = np.min(prices[-14:])
        
        if current >= recent_high * 0.99:
            patterns.append({
                'pattern': 'Breakout',
                'confidence': 0.70,
                'signal': 'BUY',
                'description': 'Price breaking 14-day high'
            })
        elif current <= recent_low * 1.01:
            patterns.append({
                'pattern': 'Breakdown',
                'confidence': 0.70,
                'signal': 'SELL',
                'description': 'Price breaking 14-day low'
            })
        
        return {
            'success': True,
            'symbol': symbol,
            'patterns': patterns,
            'analyzed_at': datetime.utcnow().isoformat()
        }
    
    def predict_price_movement(self, symbol: str, hours_ahead: int = 24) -> Dict:
        """Predict price movement using linear regression"""
        df = self._load_price_history(symbol, days=7)
        
        if df.empty or len(df) < 50:
            return {'success': False, 'error': 'Insufficient data for prediction'}
        
        df['hour'] = range(len(df))
        X = df['hour'].values.reshape(-1, 1)
        y = df['price'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        future_hours = np.array([[len(df) + hours_ahead]])
        predicted_price = model.predict(future_hours)[0]
        
        current_price = y[-1]
        price_change = ((predicted_price - current_price) / current_price) * 100
        
        confidence = min(0.95, max(0.60, 0.80 - abs(price_change) * 0.01))
        
        signal = 'HOLD'
        if price_change > 2:
            signal = 'BUY'
        elif price_change < -2:
            signal = 'SELL'
        
        prediction = {
            'success': True,
            'symbol': symbol,
            'current_price': round(current_price, 2),
            'predicted_price': round(predicted_price, 2),
            'price_change_pct': round(price_change, 2),
            'hours_ahead': hours_ahead,
            'signal': signal,
            'confidence': round(confidence, 2),
            'predicted_at': datetime.utcnow().isoformat()
        }
        
        predictions = []
        if os.path.exists(self.predictions_file):
            try:
                with open(self.predictions_file, 'r') as f:
                    predictions = json.load(f)
            except:
                pass
        
        predictions.append(prediction)
        predictions = predictions[-1000:]
        
        os.makedirs(os.path.dirname(self.predictions_file), exist_ok=True)
        with open(self.predictions_file, 'w') as f:
            json.dump(predictions, f, indent=2)
        
        return prediction
    
    def calculate_win_probability(self, user_id: str, symbol: str, side: str) -> Dict:
        """Calculate probability of winning trade based on historical performance"""
        positions = self.position_tracker.get_user_positions(user_id)
        
        symbol_positions = [p for p in positions if p.get('symbol') == symbol and p.get('status') == 'closed']
        side_positions = [p for p in symbol_positions if p.get('side') == side]
        
        if len(side_positions) < 5:
            return {
                'success': True,
                'probability': 0.50,
                'sample_size': len(side_positions),
                'note': 'Insufficient history, using neutral probability'
            }
        
        wins = len([p for p in side_positions if p.get('pnl', 0) > 0])
        total = len(side_positions)
        
        win_rate = wins / total if total > 0 else 0.5
        
        avg_pnl = np.mean([p.get('pnl', 0) for p in side_positions])
        risk_reward = abs(avg_pnl) / max(abs(np.mean([p.get('pnl', 0) for p in side_positions if p.get('pnl', 0) < 0])), 1)
        
        probability = min(0.95, max(0.05, win_rate * 0.7 + (risk_reward / 10) * 0.3))
        
        return {
            'success': True,
            'symbol': symbol,
            'side': side,
            'probability': round(probability, 2),
            'win_rate': round(win_rate, 2),
            'avg_pnl': round(avg_pnl, 2),
            'risk_reward_ratio': round(risk_reward, 2),
            'sample_size': total,
            'recommendation': 'TAKE TRADE' if probability > 0.6 else 'AVOID' if probability < 0.4 else 'NEUTRAL'
        }
    
    def get_market_sentiment(self, symbol: str) -> Dict:
        """Analyze market sentiment from recent trades"""
        df = self._load_price_history(symbol, days=1)
        
        if df.empty or len(df) < 10:
            return {'success': False, 'error': 'Insufficient data'}
        
        prices = df['price'].values
        price_changes = np.diff(prices)
        
        bullish_moves = np.sum(price_changes > 0)
        bearish_moves = np.sum(price_changes < 0)
        total_moves = len(price_changes)
        
        bullish_pct = (bullish_moves / total_moves) * 100 if total_moves > 0 else 50
        
        if bullish_pct > 60:
            sentiment = 'BULLISH'
        elif bullish_pct < 40:
            sentiment = 'BEARISH'
        else:
            sentiment = 'NEUTRAL'
        
        volatility = np.std(price_changes) / np.mean(prices) * 100
        
        return {
            'success': True,
            'symbol': symbol,
            'sentiment': sentiment,
            'bullish_percentage': round(bullish_pct, 1),
            'bearish_percentage': round(100 - bullish_pct, 1),
            'volatility': round(volatility, 2),
            'strength': 'STRONG' if abs(bullish_pct - 50) > 20 else 'MODERATE' if abs(bullish_pct - 50) > 10 else 'WEAK'
        }
