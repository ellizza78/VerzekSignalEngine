import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import statistics

class MultiTimeframeAnalysis:
    def __init__(self):
        self.timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
        self.indicators_cache = {}
    
    def analyze_multiple_timeframes(self, symbol: str, price_data: Dict[str, List[Dict]]) -> Dict:
        try:
            analysis_results = {}
            
            for timeframe in self.timeframes:
                if timeframe in price_data:
                    data = price_data[timeframe]
                    analysis_results[timeframe] = self._analyze_timeframe(symbol, timeframe, data)
            
            overall_signal = self._determine_overall_signal(analysis_results)
            strength_score = self._calculate_signal_strength(analysis_results)
            
            return {
                "success": True,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "timeframe_analysis": analysis_results,
                "overall_signal": overall_signal,
                "signal_strength": strength_score,
                "recommendation": self._generate_recommendation(overall_signal, strength_score)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_timeframe(self, symbol: str, timeframe: str, data: List[Dict]) -> Dict:
        if len(data) < 20:
            return {"error": "Insufficient data"}
        
        closes = [float(d.get('close', 0)) for d in data]
        highs = [float(d.get('high', 0)) for d in data]
        lows = [float(d.get('low', 0)) for d in data]
        volumes = [float(d.get('volume', 0)) for d in data]
        
        current_price = closes[-1]
        
        sma_20 = statistics.mean(closes[-20:]) if len(closes) >= 20 else current_price
        sma_50 = statistics.mean(closes[-50:]) if len(closes) >= 50 else current_price
        
        ema_12 = self._calculate_ema(closes, 12)
        ema_26 = self._calculate_ema(closes, 26)
        macd = ema_12 - ema_26
        
        rsi = self._calculate_rsi(closes, 14)
        
        trend = self._identify_trend(closes)
        
        support_levels = self._find_support_levels(lows)
        resistance_levels = self._find_resistance_levels(highs)
        
        volume_trend = "increasing" if statistics.mean(volumes[-5:]) > statistics.mean(volumes[-20:-5]) else "decreasing"
        
        signal = self._determine_signal(current_price, sma_20, sma_50, rsi, macd, trend)
        
        return {
            "timeframe": timeframe,
            "current_price": current_price,
            "sma_20": round(sma_20, 2),
            "sma_50": round(sma_50, 2),
            "ema_12": round(ema_12, 2),
            "ema_26": round(ema_26, 2),
            "macd": round(macd, 4),
            "rsi": round(rsi, 2),
            "trend": trend,
            "support_levels": support_levels[:3],
            "resistance_levels": resistance_levels[:3],
            "volume_trend": volume_trend,
            "signal": signal
        }
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        if len(prices) < period:
            return prices[-1]
        
        k = 2 / (period + 1)
        ema = statistics.mean(prices[:period])
        
        for price in prices[period:]:
            ema = (price * k) + (ema * (1 - k))
        
        return ema
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        if len(prices) < period + 1:
            return 50.0
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = statistics.mean(gains[-period:])
        avg_loss = statistics.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _identify_trend(self, prices: List[float]) -> str:
        if len(prices) < 10:
            return "neutral"
        
        recent_avg = statistics.mean(prices[-5:])
        older_avg = statistics.mean(prices[-15:-5])
        
        if recent_avg > older_avg * 1.02:
            return "strong_bullish"
        elif recent_avg > older_avg:
            return "bullish"
        elif recent_avg < older_avg * 0.98:
            return "strong_bearish"
        elif recent_avg < older_avg:
            return "bearish"
        else:
            return "neutral"
    
    def _find_support_levels(self, lows: List[float]) -> List[float]:
        if len(lows) < 20:
            return []
        
        recent_lows = lows[-20:]
        sorted_lows = sorted(recent_lows)
        
        supports = []
        for i in range(0, len(sorted_lows), 5):
            level = statistics.mean(sorted_lows[i:i+5])
            if level not in supports:
                supports.append(round(level, 2))
        
        return supports[:3]
    
    def _find_resistance_levels(self, highs: List[float]) -> List[float]:
        if len(highs) < 20:
            return []
        
        recent_highs = highs[-20:]
        sorted_highs = sorted(recent_highs, reverse=True)
        
        resistances = []
        for i in range(0, len(sorted_highs), 5):
            level = statistics.mean(sorted_highs[i:i+5])
            if level not in resistances:
                resistances.append(round(level, 2))
        
        return resistances[:3]
    
    def _determine_signal(self, price: float, sma_20: float, sma_50: float, rsi: float, macd: float, trend: str) -> str:
        bullish_signals = 0
        bearish_signals = 0
        
        if price > sma_20 > sma_50:
            bullish_signals += 2
        elif price < sma_20 < sma_50:
            bearish_signals += 2
        
        if rsi < 30:
            bullish_signals += 2
        elif rsi > 70:
            bearish_signals += 2
        elif 40 < rsi < 60:
            pass
        
        if macd > 0:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        if "bullish" in trend:
            bullish_signals += 2
        elif "bearish" in trend:
            bearish_signals += 2
        
        if bullish_signals > bearish_signals + 2:
            return "strong_buy"
        elif bullish_signals > bearish_signals:
            return "buy"
        elif bearish_signals > bullish_signals + 2:
            return "strong_sell"
        elif bearish_signals > bullish_signals:
            return "sell"
        else:
            return "hold"
    
    def _determine_overall_signal(self, analysis_results: Dict) -> str:
        signals_weight = {
            '1m': 1,
            '5m': 2,
            '15m': 3,
            '1h': 4,
            '4h': 5,
            '1d': 6
        }
        
        signal_scores = {
            'strong_buy': 3,
            'buy': 2,
            'hold': 0,
            'sell': -2,
            'strong_sell': -3
        }
        
        total_score = 0
        total_weight = 0
        
        for timeframe, analysis in analysis_results.items():
            if 'signal' in analysis:
                signal = analysis['signal']
                weight = signals_weight.get(timeframe, 1)
                score = signal_scores.get(signal, 0)
                total_score += score * weight
                total_weight += weight
        
        if total_weight == 0:
            return "hold"
        
        avg_score = total_score / total_weight
        
        if avg_score >= 2:
            return "strong_buy"
        elif avg_score >= 0.5:
            return "buy"
        elif avg_score <= -2:
            return "strong_sell"
        elif avg_score <= -0.5:
            return "sell"
        else:
            return "hold"
    
    def _calculate_signal_strength(self, analysis_results: Dict) -> int:
        if not analysis_results:
            return 0
        
        signals = []
        for analysis in analysis_results.values():
            if 'signal' in analysis:
                signals.append(analysis['signal'])
        
        if not signals:
            return 0
        
        signal_counts = {}
        for signal in signals:
            signal_counts[signal] = signal_counts.get(signal, 0) + 1
        
        max_count = max(signal_counts.values())
        strength = int((max_count / len(signals)) * 100)
        
        return strength
    
    def _generate_recommendation(self, signal: str, strength: int) -> str:
        if strength >= 80:
            confidence = "Very High"
        elif strength >= 60:
            confidence = "High"
        elif strength >= 40:
            confidence = "Moderate"
        else:
            confidence = "Low"
        
        action_map = {
            "strong_buy": "STRONG BUY - Consider aggressive position entry",
            "buy": "BUY - Consider entering a position",
            "hold": "HOLD - Wait for clearer signals",
            "sell": "SELL - Consider reducing position or exiting",
            "strong_sell": "STRONG SELL - Consider closing positions immediately"
        }
        
        action = action_map.get(signal, "HOLD - Analysis inconclusive")
        
        return f"{action} (Confidence: {confidence} - {strength}%)"
    
    def detect_divergence(self, price_data: List[Dict], indicator: str = 'rsi') -> Dict:
        try:
            closes = [float(d.get('close', 0)) for d in price_data]
            
            if indicator.lower() == 'rsi':
                indicator_values = [self._calculate_rsi(closes[:i+1], 14) for i in range(13, len(closes))]
            elif indicator.lower() == 'macd':
                indicator_values = []
                for i in range(13, len(closes)):
                    ema_12 = self._calculate_ema(closes[:i+1], 12)
                    ema_26 = self._calculate_ema(closes[:i+1], 26)
                    indicator_values.append(ema_12 - ema_26)
            else:
                return {"success": False, "error": "Unsupported indicator"}
            
            price_highs = []
            price_lows = []
            indicator_highs = []
            indicator_lows = []
            
            for i in range(1, len(closes) - 1):
                if closes[i] > closes[i-1] and closes[i] > closes[i+1]:
                    price_highs.append((i, closes[i]))
                if closes[i] < closes[i-1] and closes[i] < closes[i+1]:
                    price_lows.append((i, closes[i]))
            
            for i in range(1, len(indicator_values) - 1):
                if indicator_values[i] > indicator_values[i-1] and indicator_values[i] > indicator_values[i+1]:
                    indicator_highs.append((i, indicator_values[i]))
                if indicator_values[i] < indicator_values[i-1] and indicator_values[i] < indicator_values[i+1]:
                    indicator_lows.append((i, indicator_values[i]))
            
            bullish_divergence = False
            bearish_divergence = False
            
            if len(price_lows) >= 2 and len(indicator_lows) >= 2:
                if price_lows[-1][1] < price_lows[-2][1] and indicator_lows[-1][1] > indicator_lows[-2][1]:
                    bullish_divergence = True
            
            if len(price_highs) >= 2 and len(indicator_highs) >= 2:
                if price_highs[-1][1] > price_highs[-2][1] and indicator_highs[-1][1] < indicator_highs[-2][1]:
                    bearish_divergence = True
            
            return {
                "success": True,
                "bullish_divergence": bullish_divergence,
                "bearish_divergence": bearish_divergence,
                "signal": "buy" if bullish_divergence else ("sell" if bearish_divergence else "none"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    analyzer = MultiTimeframeAnalysis()
    
    sample_data = {
        "1m": [{"close": 45000 + i*10, "high": 45050 + i*10, "low": 44950 + i*10, "volume": 1000000} for i in range(50)],
        "5m": [{"close": 45000 + i*20, "high": 45100 + i*20, "low": 44900 + i*20, "volume": 2000000} for i in range(50)],
        "1h": [{"close": 45000 + i*50, "high": 45200 + i*50, "low": 44800 + i*50, "volume": 5000000} for i in range(50)]
    }
    
    result = analyzer.analyze_multiple_timeframes("BTC/USDT", sample_data)
    print(json.dumps(result, indent=2))
