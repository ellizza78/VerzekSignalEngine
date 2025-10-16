import json
from typing import Dict, List, Optional
from datetime import datetime
import statistics

class AIRiskScoringSystem:
    def __init__(self):
        self.risk_thresholds = {
            "very_low": (0, 20),
            "low": (20, 40),
            "medium": (40, 60),
            "high": (60, 80),
            "very_high": (80, 100)
        }
    
    def evaluate_position_risk(self, position: Dict, market_data: Dict, user_settings: Dict) -> Dict:
        try:
            risk_factors = {}
            
            position_size = float(position.get('size', 0))
            entry_price = float(position.get('entry_price', 0))
            current_price = float(market_data.get('current_price', entry_price))
            leverage = float(position.get('leverage', 1))
            stop_loss = float(position.get('stop_loss', 0))
            
            account_balance = float(user_settings.get('balance', 10000))
            risk_per_trade = float(user_settings.get('risk_per_trade', 2))
            
            position_value = position_size * current_price * leverage
            exposure_pct = (position_value / account_balance) * 100
            risk_factors['exposure'] = {
                "score": min(exposure_pct * 2, 100),
                "value": round(exposure_pct, 2),
                "description": "Position size relative to account"
            }
            
            leverage_risk = (leverage - 1) * 10
            risk_factors['leverage'] = {
                "score": min(leverage_risk, 100),
                "value": leverage,
                "description": "Leverage multiplier risk"
            }
            
            if stop_loss > 0:
                sl_distance = abs((current_price - stop_loss) / current_price) * 100
                sl_risk = max(0, 100 - (sl_distance * 10))
            else:
                sl_risk = 100
                sl_distance = 0
            
            risk_factors['stop_loss'] = {
                "score": sl_risk,
                "value": f"{sl_distance:.2f}%",
                "description": "Stop loss protection"
            }
            
            volatility = float(market_data.get('volatility', 5))
            volatility_risk = min(volatility * 5, 100)
            risk_factors['volatility'] = {
                "score": volatility_risk,
                "value": volatility,
                "description": "Market volatility level"
            }
            
            total_score = statistics.mean([f['score'] for f in risk_factors.values()])
            
            risk_level = self._get_risk_level(total_score)
            
            recommendations = self._generate_risk_recommendations(risk_factors, risk_level)
            
            return {
                "success": True,
                "position_id": position.get('id', 'unknown'),
                "overall_risk_score": round(total_score, 2),
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "recommendations": recommendations,
                "max_loss_potential": round((position_value * (sl_distance / 100)) if sl_distance > 0 else position_value, 2),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def evaluate_portfolio_risk(self, positions: List[Dict], account_balance: float, market_conditions: Dict) -> Dict:
        try:
            if not positions:
                return {
                    "success": True,
                    "overall_risk_score": 0,
                    "risk_level": "very_low",
                    "message": "No open positions"
                }
            
            total_exposure = sum(float(p.get('size', 0)) * float(p.get('entry_price', 0)) * float(p.get('leverage', 1)) for p in positions)
            exposure_ratio = (total_exposure / account_balance) * 100
            
            leverages = [float(p.get('leverage', 1)) for p in positions]
            avg_leverage = statistics.mean(leverages)
            max_leverage = max(leverages)
            
            symbols = set(p.get('symbol', '') for p in positions)
            diversification = len(symbols) / len(positions) if len(positions) > 0 else 0
            
            long_positions = sum(1 for p in positions if p.get('direction') == 'LONG')
            short_positions = len(positions) - long_positions
            directional_bias = abs(long_positions - short_positions) / len(positions) if len(positions) > 0 else 0
            
            risk_components = {
                "exposure": min(exposure_ratio, 100),
                "leverage": min((avg_leverage - 1) * 15, 100),
                "diversification": (1 - diversification) * 100,
                "directional_bias": directional_bias * 100,
                "market_conditions": self._assess_market_risk(market_conditions)
            }
            
            overall_score = statistics.mean(risk_components.values())
            risk_level = self._get_risk_level(overall_score)
            
            return {
                "success": True,
                "overall_risk_score": round(overall_score, 2),
                "risk_level": risk_level,
                "total_exposure": round(total_exposure, 2),
                "exposure_ratio": round(exposure_ratio, 2),
                "average_leverage": round(avg_leverage, 2),
                "max_leverage": max_leverage,
                "num_positions": len(positions),
                "num_symbols": len(symbols),
                "diversification_score": round(diversification * 100, 2),
                "long_short_ratio": f"{long_positions}:{short_positions}",
                "risk_breakdown": {k: round(v, 2) for k, v in risk_components.items()},
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def calculate_var(self, positions: List[Dict], confidence_level: float = 0.95, time_horizon_days: int = 1) -> Dict:
        try:
            if not positions:
                return {
                    "success": True,
                    "var": 0,
                    "message": "No positions to calculate VaR"
                }
            
            portfolio_value = sum(float(p.get('size', 0)) * float(p.get('entry_price', 0)) for p in positions)
            
            daily_volatility = 0.02
            
            z_score = {
                0.90: 1.28,
                0.95: 1.65,
                0.99: 2.33
            }.get(confidence_level, 1.65)
            
            var = portfolio_value * daily_volatility * z_score * (time_horizon_days ** 0.5)
            
            var_pct = (var / portfolio_value) * 100 if portfolio_value > 0 else 0
            
            return {
                "success": True,
                "var": round(var, 2),
                "var_percentage": round(var_pct, 2),
                "confidence_level": confidence_level,
                "time_horizon_days": time_horizon_days,
                "portfolio_value": round(portfolio_value, 2),
                "interpretation": f"There is a {confidence_level*100}% confidence that losses will not exceed ${var:.2f} over {time_horizon_days} day(s)",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def stress_test(self, positions: List[Dict], scenarios: List[Dict]) -> Dict:
        try:
            results = []
            
            for scenario in scenarios:
                scenario_name = scenario.get('name', 'Unnamed')
                price_change = scenario.get('price_change_pct', 0) / 100
                
                total_pnl = 0
                for position in positions:
                    entry_price = float(position.get('entry_price', 0))
                    size = float(position.get('size', 0))
                    direction = position.get('direction', 'LONG')
                    leverage = float(position.get('leverage', 1))
                    
                    new_price = entry_price * (1 + price_change)
                    
                    if direction == 'LONG':
                        pnl = (new_price - entry_price) * size * leverage
                    else:
                        pnl = (entry_price - new_price) * size * leverage
                    
                    total_pnl += pnl
                
                results.append({
                    "scenario": scenario_name,
                    "price_change": f"{scenario.get('price_change_pct', 0)}%",
                    "total_pnl": round(total_pnl, 2),
                    "severity": "Critical" if total_pnl < -1000 else "High" if total_pnl < -500 else "Medium" if total_pnl < 0 else "Low"
                })
            
            worst_case = min(results, key=lambda x: x['total_pnl']) if results else None
            
            return {
                "success": True,
                "stress_test_results": results,
                "worst_case_scenario": worst_case,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_risk_level(self, score: float) -> str:
        for level, (min_score, max_score) in self.risk_thresholds.items():
            if min_score <= score < max_score:
                return level
        return "very_high"
    
    def _assess_market_risk(self, market_conditions: Dict) -> float:
        trend = market_conditions.get('trend', 'neutral')
        volatility = market_conditions.get('volatility', 'medium')
        
        trend_risk = {
            'strong_bullish': 20,
            'bullish': 30,
            'neutral': 50,
            'bearish': 70,
            'strong_bearish': 80
        }.get(trend, 50)
        
        volatility_risk = {
            'very_low': 10,
            'low': 30,
            'medium': 50,
            'high': 70,
            'very_high': 90
        }.get(volatility, 50)
        
        return (trend_risk + volatility_risk) / 2
    
    def _generate_risk_recommendations(self, risk_factors: Dict, risk_level: str) -> List[str]:
        recommendations = []
        
        if risk_factors['exposure']['score'] > 60:
            recommendations.append("Reduce position size - exposure is too high relative to account balance")
        
        if risk_factors['leverage']['score'] > 70:
            recommendations.append("Lower leverage - current leverage significantly increases risk")
        
        if risk_factors['stop_loss']['score'] > 80:
            recommendations.append("Set or tighten stop loss - position lacks adequate protection")
        
        if risk_factors['volatility']['score'] > 70:
            recommendations.append("Consider closing position - market volatility is extremely high")
        
        if risk_level in ['high', 'very_high']:
            recommendations.append("Overall risk is elevated - consider partial or full position closure")
        
        if not recommendations:
            recommendations.append("Risk levels are acceptable - continue monitoring position")
        
        return recommendations


if __name__ == "__main__":
    risk_system = AIRiskScoringSystem()
    
    position = {
        "id": "pos_123",
        "size": 1.5,
        "entry_price": 45000,
        "leverage": 10,
        "stop_loss": 44500,
        "direction": "LONG"
    }
    
    market_data = {
        "current_price": 45200,
        "volatility": 8
    }
    
    user_settings = {
        "balance": 10000,
        "risk_per_trade": 2
    }
    
    result = risk_system.evaluate_position_risk(position, market_data, user_settings)
    print(json.dumps(result, indent=2))
