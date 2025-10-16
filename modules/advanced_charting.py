import json
from typing import Dict, List, Optional
from datetime import datetime
import statistics

class AdvancedChartingSystem:
    def __init__(self):
        self.indicators = {
            'SMA': self._calculate_sma,
            'EMA': self._calculate_ema,
            'RSI': self._calculate_rsi,
            'MACD': self._calculate_macd,
            'Bollinger': self._calculate_bollinger,
            'ATR': self._calculate_atr,
            'Stochastic': self._calculate_stochastic,
            'Fibonacci': self._calculate_fibonacci,
            'Ichimoku': self._calculate_ichimoku,
            'Volume_Profile': self._calculate_volume_profile
        }
    
    def calculate_indicator(self, indicator_name: str, price_data: List[Dict], params: Dict = None) -> Dict:
        try:
            if indicator_name not in self.indicators:
                return {
                    "success": False,
                    "error": f"Unknown indicator: {indicator_name}"
                }
            
            params = params or {}
            result = self.indicators[indicator_name](price_data, params)
            
            return {
                "success": True,
                "indicator": indicator_name,
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_sma(self, price_data: List[Dict], params: Dict) -> List[Dict]:
        period = params.get('period', 20)
        closes = [float(d.get('close', 0)) for d in price_data]
        
        sma_values = []
        for i in range(len(closes)):
            if i < period - 1:
                sma_values.append(None)
            else:
                sma = statistics.mean(closes[i-period+1:i+1])
                sma_values.append(round(sma, 2))
        
        return [{"index": i, "value": v} for i, v in enumerate(sma_values)]
    
    def _calculate_ema(self, price_data: List[Dict], params: Dict) -> List[Dict]:
        period = params.get('period', 12)
        closes = [float(d.get('close', 0)) for d in price_data]
        
        k = 2 / (period + 1)
        ema_values = [None] * (period - 1)
        ema = statistics.mean(closes[:period])
        ema_values.append(ema)
        
        for price in closes[period:]:
            ema = (price * k) + (ema * (1 - k))
            ema_values.append(round(ema, 2))
        
        return [{"index": i, "value": v} for i, v in enumerate(ema_values)]
    
    def _calculate_rsi(self, price_data: List[Dict], params: Dict) -> List[Dict]:
        period = params.get('period', 14)
        closes = [float(d.get('close', 0)) for d in price_data]
        
        rsi_values = [None] * period
        
        for i in range(period, len(closes)):
            deltas = [closes[j] - closes[j-1] for j in range(i-period+1, i+1)]
            gains = [d if d > 0 else 0 for d in deltas]
            losses = [-d if d < 0 else 0 for d in deltas]
            
            avg_gain = statistics.mean(gains)
            avg_loss = statistics.mean(losses)
            
            if avg_loss == 0:
                rsi = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(round(rsi, 2))
        
        return [{"index": i, "value": v} for i, v in enumerate(rsi_values)]
    
    def _calculate_macd(self, price_data: List[Dict], params: Dict) -> List[Dict]:
        fast_period = params.get('fast', 12)
        slow_period = params.get('slow', 26)
        signal_period = params.get('signal', 9)
        
        closes = [float(d.get('close', 0)) for d in price_data]
        
        ema_fast = self._calculate_ema(price_data, {'period': fast_period})
        ema_slow = self._calculate_ema(price_data, {'period': slow_period})
        
        macd_line = []
        for i in range(len(closes)):
            if ema_fast[i]['value'] is not None and ema_slow[i]['value'] is not None:
                macd_line.append(ema_fast[i]['value'] - ema_slow[i]['value'])
            else:
                macd_line.append(None)
        
        signal_line = [None] * slow_period
        if any(v is not None for v in macd_line[slow_period:]):
            valid_macd = [v for v in macd_line[slow_period:] if v is not None]
            if len(valid_macd) >= signal_period:
                k = 2 / (signal_period + 1)
                signal = statistics.mean(valid_macd[:signal_period])
                signal_line.append(signal)
                
                for macd_val in valid_macd[signal_period:]:
                    signal = (macd_val * k) + (signal * (1 - k))
                    signal_line.append(round(signal, 4))
        
        histogram = []
        for i in range(len(macd_line)):
            if macd_line[i] is not None and i < len(signal_line) and signal_line[i] is not None:
                histogram.append(round(macd_line[i] - signal_line[i], 4))
            else:
                histogram.append(None)
        
        return [{"index": i, "macd": macd_line[i], "signal": signal_line[i] if i < len(signal_line) else None, "histogram": histogram[i]} for i in range(len(macd_line))]
    
    def _calculate_bollinger(self, price_data: List[Dict], params: Dict) -> List[Dict]:
        period = params.get('period', 20)
        std_dev = params.get('std_dev', 2)
        closes = [float(d.get('close', 0)) for d in price_data]
        
        bollinger_bands = []
        for i in range(len(closes)):
            if i < period - 1:
                bollinger_bands.append({"index": i, "upper": None, "middle": None, "lower": None})
            else:
                window = closes[i-period+1:i+1]
                middle = statistics.mean(window)
                std = statistics.stdev(window) if len(window) > 1 else 0
                upper = middle + (std_dev * std)
                lower = middle - (std_dev * std)
                
                bollinger_bands.append({
                    "index": i,
                    "upper": round(upper, 2),
                    "middle": round(middle, 2),
                    "lower": round(lower, 2)
                })
        
        return bollinger_bands
    
    def _calculate_atr(self, price_data: List[Dict], params: Dict) -> List[Dict]:
        period = params.get('period', 14)
        
        true_ranges = []
        for i in range(1, len(price_data)):
            high = float(price_data[i].get('high', 0))
            low = float(price_data[i].get('low', 0))
            prev_close = float(price_data[i-1].get('close', 0))
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        atr_values = [None] * (period)
        if len(true_ranges) >= period:
            atr = statistics.mean(true_ranges[:period])
            atr_values.append(atr)
            
            for tr in true_ranges[period:]:
                atr = ((atr * (period - 1)) + tr) / period
                atr_values.append(round(atr, 2))
        
        return [{"index": i, "value": v} for i, v in enumerate(atr_values)]
    
    def _calculate_stochastic(self, price_data: List[Dict], params: Dict) -> List[Dict]:
        period = params.get('period', 14)
        k_period = params.get('k_period', 3)
        
        stochastic_values = []
        for i in range(len(price_data)):
            if i < period - 1:
                stochastic_values.append({"index": i, "k": None, "d": None})
            else:
                window = price_data[i-period+1:i+1]
                highs = [float(d.get('high', 0)) for d in window]
                lows = [float(d.get('low', 0)) for d in window]
                close = float(price_data[i].get('close', 0))
                
                highest_high = max(highs)
                lowest_low = min(lows)
                
                if highest_high - lowest_low == 0:
                    k = 50
                else:
                    k = ((close - lowest_low) / (highest_high - lowest_low)) * 100
                
                stochastic_values.append({"index": i, "k": round(k, 2), "d": None})
        
        for i in range(period + k_period - 2, len(stochastic_values)):
            k_values = [s['k'] for s in stochastic_values[i-k_period+1:i+1] if s['k'] is not None]
            if k_values:
                d = statistics.mean(k_values)
                stochastic_values[i]['d'] = round(d, 2)
        
        return stochastic_values
    
    def _calculate_fibonacci(self, price_data: List[Dict], params: Dict) -> Dict:
        if len(price_data) < 2:
            return {"error": "Insufficient data"}
        
        closes = [float(d.get('close', 0)) for d in price_data]
        high = max(closes)
        low = min(closes)
        diff = high - low
        
        levels = {
            "0.0": round(high, 2),
            "0.236": round(high - (diff * 0.236), 2),
            "0.382": round(high - (diff * 0.382), 2),
            "0.5": round(high - (diff * 0.5), 2),
            "0.618": round(high - (diff * 0.618), 2),
            "0.786": round(high - (diff * 0.786), 2),
            "1.0": round(low, 2)
        }
        
        return {
            "high": high,
            "low": low,
            "levels": levels
        }
    
    def _calculate_ichimoku(self, price_data: List[Dict], params: Dict) -> List[Dict]:
        tenkan_period = params.get('tenkan', 9)
        kijun_period = params.get('kijun', 26)
        senkou_b_period = params.get('senkou_b', 52)
        
        ichimoku_values = []
        
        for i in range(len(price_data)):
            result = {"index": i, "tenkan": None, "kijun": None, "senkou_a": None, "senkou_b": None, "chikou": None}
            
            if i >= tenkan_period - 1:
                window = price_data[i-tenkan_period+1:i+1]
                highs = [float(d.get('high', 0)) for d in window]
                lows = [float(d.get('low', 0)) for d in window]
                result['tenkan'] = round((max(highs) + min(lows)) / 2, 2)
            
            if i >= kijun_period - 1:
                window = price_data[i-kijun_period+1:i+1]
                highs = [float(d.get('high', 0)) for d in window]
                lows = [float(d.get('low', 0)) for d in window]
                result['kijun'] = round((max(highs) + min(lows)) / 2, 2)
            
            if result['tenkan'] is not None and result['kijun'] is not None:
                result['senkou_a'] = round((result['tenkan'] + result['kijun']) / 2, 2)
            
            if i >= senkou_b_period - 1:
                window = price_data[i-senkou_b_period+1:i+1]
                highs = [float(d.get('high', 0)) for d in window]
                lows = [float(d.get('low', 0)) for d in window]
                result['senkou_b'] = round((max(highs) + min(lows)) / 2, 2)
            
            if i >= 26:
                result['chikou'] = float(price_data[i-26].get('close', 0))
            
            ichimoku_values.append(result)
        
        return ichimoku_values
    
    def _calculate_volume_profile(self, price_data: List[Dict], params: Dict) -> Dict:
        num_bins = params.get('bins', 20)
        
        if not price_data:
            return {"error": "No data"}
        
        prices = [float(d.get('close', 0)) for d in price_data]
        volumes = [float(d.get('volume', 0)) for d in price_data]
        
        min_price = min(prices)
        max_price = max(prices)
        bin_size = (max_price - min_price) / num_bins
        
        bins = {}
        for i, price in enumerate(prices):
            bin_index = int((price - min_price) / bin_size) if bin_size > 0 else 0
            bin_index = min(bin_index, num_bins - 1)
            
            if bin_index not in bins:
                bins[bin_index] = {"price_range": (min_price + bin_index * bin_size, min_price + (bin_index + 1) * bin_size), "volume": 0}
            
            bins[bin_index]["volume"] += volumes[i]
        
        profile = [{"price_low": round(v["price_range"][0], 2), "price_high": round(v["price_range"][1], 2), "volume": round(v["volume"], 2)} for v in bins.values()]
        profile.sort(key=lambda x: x['volume'], reverse=True)
        
        poc = profile[0] if profile else None
        
        return {
            "profile": profile,
            "point_of_control": poc,
            "value_area": profile[:int(len(profile) * 0.7)]
        }
    
    def generate_chart_config(self, indicators: List[str], params: Dict = None) -> Dict:
        try:
            params = params or {}
            
            config = {
                "indicators": [],
                "overlays": [],
                "subcharts": []
            }
            
            overlay_indicators = ['SMA', 'EMA', 'Bollinger', 'Ichimoku']
            subchart_indicators = ['RSI', 'MACD', 'Stochastic', 'Volume_Profile']
            
            for indicator in indicators:
                if indicator in overlay_indicators:
                    config['overlays'].append({
                        "type": indicator,
                        "params": params.get(indicator, {})
                    })
                elif indicator in subchart_indicators:
                    config['subcharts'].append({
                        "type": indicator,
                        "params": params.get(indicator, {})
                    })
                
                config['indicators'].append(indicator)
            
            return {
                "success": True,
                "config": config
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    charting = AdvancedChartingSystem()
    
    sample_data = [{"close": 45000 + i*10, "high": 45050 + i*10, "low": 44950 + i*10, "volume": 1000000} for i in range(100)]
    
    result = charting.calculate_indicator("RSI", sample_data, {"period": 14})
    print(json.dumps(result, indent=2))
