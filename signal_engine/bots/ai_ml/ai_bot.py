"""
AI/ML Pattern Bot - Machine Learning Predictions
Uses trained ML model to predict price movements
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from engine.base_strategy import BaseStrategy
from core.models import SignalCandidate
from common.indicators import Indicators
from typing import Optional
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class AIBot(BaseStrategy):
    """
    AI/ML strategy using pattern recognition
    
    Features used for prediction:
    - RSI
    - MACD and histogram
    - MA spreads (distance between MAs)
    - Volume delta
    - Candle patterns
    - Volatility (ATR)
    - Price momentum
    
    Outputs:
    - Probability of upward movement
    - Probability of downward movement
    - Confidence score
    """
    
    def __init__(self, config: dict):
        super().__init__("AI/ML Bot", config)
        self.model_path = config.get('model_path')
        self.model = None
        self.min_confidence = config.get('confidence_threshold', 72)
        self.prediction_threshold = config.get('prediction_threshold', 0.65)
        self._load_model()
        
    def _load_model(self):
        """Load pre-trained ML model"""
        try:
            # Placeholder - in production, load actual trained model
            # import joblib
            # self.model = joblib.load(self.model_path)
            logger.info("AI Model loaded (placeholder - train real model for production)")
            self.model = None  # Will use rule-based fallback
        except Exception as e:
            logger.warning(f"Could not load AI model: {e}. Using rule-based fallback.")
            self.model = None
    
    async def analyze(self, symbol: str) -> Optional[SignalCandidate]:
        """Analyze symbol using AI/ML predictions"""
        try:
            # Fetch market data
            df = self.fetch_market_data(symbol, '5m', limit=200)
            if df is None:
                return None
            
            # Check cooldown
            if not self.should_generate_signal(symbol, cooldown_minutes=20):
                return None
            
            # Extract features
            features = self._extract_features(df)
            if features is None:
                return None
            
            # Make prediction
            if self.model is not None:
                prediction = self._predict_with_model(features)
            else:
                # Fallback to advanced rule-based system
                prediction = self._rule_based_prediction(features, df)
            
            if prediction is None:
                return None
            
            direction = prediction['direction']
            confidence = prediction['confidence']
            
            if confidence < self.min_confidence:
                return None
            
            current_price = df['close'].iloc[-1]
            signal = self._create_signal(
                symbol, direction, current_price, confidence, prediction
            )
            
            if self.validate_signal(signal):
                self.record_signal(symbol)
                self.log_signal(signal)
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"AI bot error analyzing {symbol}: {e}")
            return None
    
    def _extract_features(self, df) -> Optional[dict]:
        """Extract ML features from market data"""
        try:
            # Technical indicators
            rsi = self.indicators.rsi(df, 14)
            macd_line, signal_line, histogram = self.indicators.macd(df)
            ma7 = self.indicators.moving_average(df, 7, 'EMA')
            ma25 = self.indicators.moving_average(df, 25, 'EMA')
            ma50 = self.indicators.moving_average(df, 50, 'EMA')
            atr = self.indicators.atr(df, 14)
            bb_upper, bb_mid, bb_lower = self.indicators.bollinger_bands(df)
            
            current_price = df['close'].iloc[-1]
            
            # Feature engineering
            features = {
                'rsi': rsi.iloc[-1],
                'macd': macd_line.iloc[-1],
                'macd_signal': signal_line.iloc[-1],
                'macd_histogram': histogram.iloc[-1],
                'ma7_distance': (current_price - ma7.iloc[-1]) / ma7.iloc[-1] * 100,
                'ma25_distance': (current_price - ma25.iloc[-1]) / ma25.iloc[-1] * 100,
                'ma50_distance': (current_price - ma50.iloc[-1]) / ma50.iloc[-1] * 100,
                'ma_spread_7_25': (ma7.iloc[-1] - ma25.iloc[-1]) / ma25.iloc[-1] * 100,
                'volume_ratio': df['volume'].iloc[-1] / df['volume'].tail(20).mean(),
                'atr_normalized': atr.iloc[-1] / current_price * 100,
                'bb_position': (current_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1]),
                'price_momentum': df['close'].pct_change(5).iloc[-1] * 100,
                'volatility': df['close'].pct_change().tail(20).std() * 100,
                'candle_body_ratio': abs(df['close'].iloc[-1] - df['open'].iloc[-1]) / (df['high'].iloc[-1] - df['low'].iloc[-1]) if (df['high'].iloc[-1] - df['low'].iloc[-1]) > 0 else 0,
                'is_hammer': 1 if self.indicators.detect_hammer(df) else 0,
                'is_shooting_star': 1 if self.indicators.detect_shooting_star(df) else 0
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None
    
    def _predict_with_model(self, features: dict) -> Optional[dict]:
        """Use trained ML model for prediction"""
        try:
            # Convert features to array
            feature_array = np.array([list(features.values())])
            
            # Make prediction
            prediction = self.model.predict_proba(feature_array)[0]
            
            # prediction[0] = probability of down, prediction[1] = probability of up
            prob_down = prediction[0]
            prob_up = prediction[1]
            
            if prob_up > self.prediction_threshold:
                return {
                    'direction': 'LONG',
                    'confidence': prob_up * 100,
                    'prob_up': prob_up,
                    'prob_down': prob_down
                }
            elif prob_down > self.prediction_threshold:
                return {
                    'direction': 'SHORT',
                    'confidence': prob_down * 100,
                    'prob_up': prob_up,
                    'prob_down': prob_down
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Model prediction error: {e}")
            return None
    
    def _rule_based_prediction(self, features: dict, df) -> Optional[dict]:
        """Advanced rule-based prediction as fallback"""
        score = 0
        
        # RSI signals
        if features['rsi'] < 30:
            score += 3  # Oversold
        elif features['rsi'] > 70:
            score -= 3  # Overbought
        
        # MACD signals
        if features['macd'] > features['macd_signal'] and features['macd_histogram'] > 0:
            score += 2
        elif features['macd'] < features['macd_signal'] and features['macd_histogram'] < 0:
            score -= 2
        
        # MA alignment
        if features['ma7_distance'] > 0 and features['ma25_distance'] > 0:
            score += 2  # Price above MAs (bullish)
        elif features['ma7_distance'] < 0 and features['ma25_distance'] < 0:
            score -= 2  # Price below MAs (bearish)
        
        # MA spread (momentum)
        if features['ma_spread_7_25'] > 1:
            score += 1
        elif features['ma_spread_7_25'] < -1:
            score -= 1
        
        # Bollinger Band position
        if features['bb_position'] < 0.2:
            score += 2  # Near lower band (oversold)
        elif features['bb_position'] > 0.8:
            score -= 2  # Near upper band (overbought)
        
        # Volume confirmation
        if features['volume_ratio'] > 1.5:
            score += 1 if score > 0 else -1  # Amplify existing signal
        
        # Candle patterns
        if features['is_hammer'] == 1:
            score += 2
        if features['is_shooting_star'] == 1:
            score -= 2
        
        # Momentum
        if features['price_momentum'] > 2:
            score += 1
        elif features['price_momentum'] < -2:
            score -= 1
        
        # Calculate confidence based on score magnitude
        confidence = min(abs(score) * 10 + 50, 95)
        
        if score >= 5:
            return {'direction': 'LONG', 'confidence': confidence, 'score': score}
        elif score <= -5:
            return {'direction': 'SHORT', 'confidence': confidence, 'score': score}
        
        return None
    
    def _create_signal(self, symbol, direction, entry_price, confidence, prediction) -> Signal:
        """Create AI-based signal"""
        # AI bot uses adaptive TP/SL based on confidence
        if confidence > 85:
            tp_pct = 2.0
            sl_pct = 0.8
        elif confidence > 75:
            tp_pct = 1.5
            sl_pct = 0.7
        else:
            tp_pct = 1.0
            sl_pct = 0.5
        
        tp_price, sl_price = self.calculate_tp_sl(
            entry_price, direction, tp_pct, sl_pct
        )
        
        return Signal(
            symbol=symbol.replace('/', ''),
            direction=direction,
            entry_price=entry_price,
            tp_price=tp_price,
            sl_price=sl_price,
            strategy_name=f"{self.name} v1",
            timeframe='5m',
            confidence=confidence,
            metadata={
                'strategy_type': 'ai_ml',
                'prediction': prediction,
                'tp_pct': tp_pct,
                'sl_pct': sl_pct
            }
        )
