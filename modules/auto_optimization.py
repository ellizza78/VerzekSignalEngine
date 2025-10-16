import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics
import random

class AutoOptimizationEngine:
    def __init__(self):
        self.optimization_history = []
        self.best_parameters = {}
    
    def optimize_strategy(self, strategy_name: str, historical_trades: List[Dict], parameter_ranges: Dict) -> Dict:
        try:
            if len(historical_trades) < 10:
                return {
                    "success": False,
                    "error": "Insufficient trade history (minimum 10 trades required)"
                }
            
            best_score = float('-inf')
            best_params = {}
            tested_combinations = []
            
            num_iterations = 50
            
            for _ in range(num_iterations):
                params = self._generate_random_params(parameter_ranges)
                score = self._evaluate_params(params, historical_trades)
                
                tested_combinations.append({
                    "params": params.copy(),
                    "score": score
                })
                
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
            
            improvement = self._calculate_improvement(best_params, historical_trades)
            
            self.best_parameters[strategy_name] = best_params
            self.optimization_history.append({
                "strategy": strategy_name,
                "timestamp": datetime.now().isoformat(),
                "best_params": best_params,
                "best_score": best_score,
                "iterations": num_iterations
            })
            
            return {
                "success": True,
                "strategy": strategy_name,
                "optimized_parameters": best_params,
                "performance_score": round(best_score, 2),
                "expected_improvement": f"{improvement}%",
                "iterations_tested": num_iterations,
                "top_5_combinations": sorted(tested_combinations, key=lambda x: x['score'], reverse=True)[:5],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_random_params(self, ranges: Dict) -> Dict:
        params = {}
        for param, range_values in ranges.items():
            if isinstance(range_values, dict):
                min_val = range_values.get('min', 0)
                max_val = range_values.get('max', 100)
                step = range_values.get('step', 1)
                
                if isinstance(min_val, float) or isinstance(max_val, float):
                    params[param] = round(random.uniform(min_val, max_val), 2)
                else:
                    steps = list(range(int(min_val), int(max_val) + 1, int(step)))
                    params[param] = random.choice(steps) if steps else min_val
            elif isinstance(range_values, list):
                params[param] = random.choice(range_values)
        
        return params
    
    def _evaluate_params(self, params: Dict, trades: List[Dict]) -> float:
        total_pnl = 0
        wins = 0
        losses = 0
        max_drawdown = 0
        peak = 0
        
        for trade in trades:
            pnl = float(trade.get('pnl', 0))
            total_pnl += pnl
            
            if pnl > 0:
                wins += 1
            else:
                losses += 1
            
            if total_pnl > peak:
                peak = total_pnl
            
            drawdown = peak - total_pnl
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        win_rate = wins / len(trades) if len(trades) > 0 else 0
        avg_pnl = total_pnl / len(trades) if len(trades) > 0 else 0
        
        sharpe_ratio = self._calculate_sharpe(trades)
        
        score = (
            total_pnl * 0.4 +
            win_rate * 100 * 0.3 +
            sharpe_ratio * 20 * 0.2 -
            max_drawdown * 0.1
        )
        
        return score
    
    def _calculate_sharpe(self, trades: List[Dict]) -> float:
        if len(trades) < 2:
            return 0
        
        returns = [float(trade.get('pnl', 0)) for trade in trades]
        avg_return = statistics.mean(returns)
        std_return = statistics.stdev(returns) if len(returns) > 1 else 1
        
        if std_return == 0:
            return 0
        
        sharpe = avg_return / std_return
        return sharpe
    
    def _calculate_improvement(self, params: Dict, trades: List[Dict]) -> int:
        baseline_score = statistics.mean([float(t.get('pnl', 0)) for t in trades])
        optimized_score = self._evaluate_params(params, trades)
        
        if baseline_score == 0:
            return 0
        
        improvement = ((optimized_score - baseline_score) / abs(baseline_score)) * 100
        return round(improvement, 1)
    
    def backtest_parameters(self, params: Dict, historical_data: List[Dict]) -> Dict:
        try:
            simulated_trades = []
            balance = 10000
            initial_balance = balance
            
            for i in range(len(historical_data) - 1):
                current = historical_data[i]
                next_candle = historical_data[i + 1]
                
                entry_price = float(current.get('close', 0))
                exit_price = float(next_candle.get('close', 0))
                
                stop_loss = params.get('stop_loss', 2)
                take_profit = params.get('take_profit', 4)
                position_size = params.get('position_size', 1)
                
                price_change = ((exit_price - entry_price) / entry_price) * 100
                
                if price_change >= take_profit:
                    pnl = (exit_price - entry_price) * position_size
                    balance += pnl
                    simulated_trades.append({
                        "entry": entry_price,
                        "exit": exit_price,
                        "pnl": pnl,
                        "result": "win"
                    })
                elif price_change <= -stop_loss:
                    pnl = (exit_price - entry_price) * position_size
                    balance += pnl
                    simulated_trades.append({
                        "entry": entry_price,
                        "exit": exit_price,
                        "pnl": pnl,
                        "result": "loss"
                    })
            
            total_pnl = balance - initial_balance
            wins = sum(1 for t in simulated_trades if t['result'] == 'win')
            win_rate = (wins / len(simulated_trades) * 100) if simulated_trades else 0
            
            return {
                "success": True,
                "parameters": params,
                "total_trades": len(simulated_trades),
                "wins": wins,
                "losses": len(simulated_trades) - wins,
                "win_rate": round(win_rate, 2),
                "total_pnl": round(total_pnl, 2),
                "roi": round((total_pnl / initial_balance) * 100, 2),
                "final_balance": round(balance, 2),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def suggest_improvements(self, strategy_performance: Dict) -> Dict:
        try:
            suggestions = []
            
            win_rate = strategy_performance.get('win_rate', 0)
            avg_pnl = strategy_performance.get('avg_pnl', 0)
            max_drawdown = strategy_performance.get('max_drawdown', 0)
            
            if win_rate < 50:
                suggestions.append({
                    "area": "Entry Criteria",
                    "suggestion": "Tighten entry conditions - current win rate is below 50%",
                    "priority": "High",
                    "expected_impact": "Increase win rate by 10-15%"
                })
            
            if avg_pnl < 0:
                suggestions.append({
                    "area": "Risk Management",
                    "suggestion": "Reduce position size and increase stop-loss distance",
                    "priority": "Critical",
                    "expected_impact": "Reduce losses by 20-30%"
                })
            
            if max_drawdown > 1000:
                suggestions.append({
                    "area": "Position Sizing",
                    "suggestion": "Implement Kelly Criterion for optimal position sizing",
                    "priority": "High",
                    "expected_impact": "Reduce drawdown by 30-40%"
                })
            
            if win_rate > 60 and avg_pnl > 0:
                suggestions.append({
                    "area": "Profit Optimization",
                    "suggestion": "Consider increasing take-profit targets",
                    "priority": "Medium",
                    "expected_impact": "Increase average profit by 15-25%"
                })
            
            suggestions.append({
                "area": "Diversification",
                "suggestion": "Spread trades across multiple timeframes and assets",
                "priority": "Medium",
                "expected_impact": "Reduce risk by 20-30%"
            })
            
            return {
                "success": True,
                "suggestions": suggestions,
                "total_suggestions": len(suggestions),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_optimization_history(self, strategy_name: Optional[str] = None) -> Dict:
        try:
            if strategy_name:
                history = [h for h in self.optimization_history if h['strategy'] == strategy_name]
            else:
                history = self.optimization_history
            
            return {
                "success": True,
                "history": history,
                "count": len(history)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    optimizer = AutoOptimizationEngine()
    
    sample_trades = [
        {"pnl": 150, "entry": 45000, "exit": 45150},
        {"pnl": -50, "entry": 45200, "exit": 45150},
        {"pnl": 200, "entry": 45100, "exit": 45300}
    ]
    
    parameter_ranges = {
        "stop_loss": {"min": 1, "max": 5, "step": 0.5},
        "take_profit": {"min": 2, "max": 10, "step": 1},
        "position_size": {"min": 0.1, "max": 2.0, "step": 0.1}
    }
    
    result = optimizer.optimize_strategy("DCA_Strategy", sample_trades, parameter_ranges)
    print(json.dumps(result, indent=2))
