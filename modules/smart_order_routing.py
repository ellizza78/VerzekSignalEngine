import json
from typing import Dict, List, Optional
from datetime import datetime
import statistics

class SmartOrderRouter:
    def __init__(self):
        self.exchange_fees = {
            'binance': {'maker': 0.001, 'taker': 0.001},
            'bybit': {'maker': 0.0001, 'taker': 0.0006},
            'phemex': {'maker': 0.0001, 'taker': 0.0006},
            'coinexx': {'maker': 0.0002, 'taker': 0.0008}
        }
        
        self.exchange_liquidity_scores = {
            'binance': 100,
            'bybit': 85,
            'phemex': 70,
            'coinexx': 60
        }
    
    def find_best_execution(self, symbol: str, side: str, quantity: float, exchange_prices: Dict[str, float]) -> Dict:
        try:
            if not exchange_prices:
                return {
                    "success": False,
                    "error": "No exchange prices provided"
                }
            
            execution_costs = {}
            
            for exchange, price in exchange_prices.items():
                if exchange.lower() not in self.exchange_fees:
                    continue
                
                fee_rate = self.exchange_fees[exchange.lower()]['taker']
                
                total_cost = quantity * price
                fee_cost = total_cost * fee_rate
                
                liquidity_score = self.exchange_liquidity_scores.get(exchange.lower(), 50)
                
                slippage_estimate = self._estimate_slippage(quantity, liquidity_score)
                slippage_cost = total_cost * slippage_estimate
                
                final_cost = total_cost + fee_cost + slippage_cost
                
                execution_costs[exchange] = {
                    "price": price,
                    "base_cost": total_cost,
                    "fee_cost": fee_cost,
                    "slippage_cost": slippage_cost,
                    "total_cost": final_cost,
                    "liquidity_score": liquidity_score,
                    "estimated_slippage_pct": slippage_estimate * 100
                }
            
            if not execution_costs:
                return {
                    "success": False,
                    "error": "No valid exchanges found"
                }
            
            best_exchange = min(execution_costs.items(), key=lambda x: x[1]['total_cost'])
            
            savings = {}
            for exchange, costs in execution_costs.items():
                if exchange != best_exchange[0]:
                    savings[exchange] = costs['total_cost'] - best_exchange[1]['total_cost']
            
            return {
                "success": True,
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "best_exchange": best_exchange[0],
                "best_price": best_exchange[1]['price'],
                "total_cost": best_exchange[1]['total_cost'],
                "fee_cost": best_exchange[1]['fee_cost'],
                "slippage_cost": best_exchange[1]['slippage_cost'],
                "estimated_slippage": f"{best_exchange[1]['estimated_slippage_pct']:.3f}%",
                "liquidity_score": best_exchange[1]['liquidity_score'],
                "all_exchanges": execution_costs,
                "potential_savings": savings,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _estimate_slippage(self, quantity: float, liquidity_score: int) -> float:
        base_slippage = 0.001
        
        if quantity < 1:
            size_factor = 1.0
        elif quantity < 10:
            size_factor = 1.5
        elif quantity < 100:
            size_factor = 2.0
        else:
            size_factor = 3.0
        
        liquidity_factor = (100 - liquidity_score) / 100
        
        estimated_slippage = base_slippage * size_factor * (1 + liquidity_factor)
        
        return estimated_slippage
    
    def split_order_across_exchanges(self, symbol: str, side: str, total_quantity: float, exchange_prices: Dict[str, float], max_exchanges: int = 3) -> Dict:
        try:
            execution_plans = []
            
            for exchange, price in exchange_prices.items():
                if exchange.lower() not in self.exchange_fees:
                    continue
                
                liquidity_score = self.exchange_liquidity_scores.get(exchange.lower(), 50)
                fee_rate = self.exchange_fees[exchange.lower()]['taker']
                
                execution_plans.append({
                    "exchange": exchange,
                    "price": price,
                    "liquidity_score": liquidity_score,
                    "fee_rate": fee_rate,
                    "cost_per_unit": price * (1 + fee_rate)
                })
            
            execution_plans.sort(key=lambda x: x['cost_per_unit'])
            
            selected_plans = execution_plans[:max_exchanges]
            
            total_liquidity = sum(p['liquidity_score'] for p in selected_plans)
            
            allocations = []
            remaining_quantity = total_quantity
            
            for i, plan in enumerate(selected_plans):
                if i == len(selected_plans) - 1:
                    allocation_quantity = remaining_quantity
                else:
                    allocation_pct = plan['liquidity_score'] / total_liquidity
                    allocation_quantity = total_quantity * allocation_pct
                
                allocation_cost = allocation_quantity * plan['price']
                allocation_fee = allocation_cost * plan['fee_rate']
                
                allocations.append({
                    "exchange": plan['exchange'],
                    "quantity": round(allocation_quantity, 8),
                    "price": plan['price'],
                    "cost": allocation_cost,
                    "fee": allocation_fee,
                    "total": allocation_cost + allocation_fee
                })
                
                remaining_quantity -= allocation_quantity
            
            total_cost = sum(a['total'] for a in allocations)
            total_fees = sum(a['fee'] for a in allocations)
            
            single_best = self.find_best_execution(symbol, side, total_quantity, exchange_prices)
            if single_best['success']:
                savings = single_best['total_cost'] - total_cost
            else:
                savings = 0
            
            return {
                "success": True,
                "symbol": symbol,
                "side": side,
                "total_quantity": total_quantity,
                "num_exchanges": len(allocations),
                "allocations": allocations,
                "total_cost": total_cost,
                "total_fees": total_fees,
                "cost_savings_vs_single": savings,
                "execution_strategy": "multi_exchange_split",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def calculate_vwap(self, exchange_orderbooks: Dict[str, List[Dict]]) -> Dict:
        try:
            all_prices = []
            all_volumes = []
            
            for exchange, orderbook in exchange_orderbooks.items():
                for level in orderbook[:10]:
                    price = float(level.get('price', 0))
                    volume = float(level.get('volume', 0))
                    all_prices.append(price)
                    all_volumes.append(volume)
            
            if not all_prices or sum(all_volumes) == 0:
                return {
                    "success": False,
                    "error": "Insufficient orderbook data"
                }
            
            vwap = sum(p * v for p, v in zip(all_prices, all_volumes)) / sum(all_volumes)
            
            exchange_vwaps = {}
            for exchange, orderbook in exchange_orderbooks.items():
                prices = [float(level.get('price', 0)) for level in orderbook[:10]]
                volumes = [float(level.get('volume', 0)) for level in orderbook[:10]]
                
                if sum(volumes) > 0:
                    exchange_vwap = sum(p * v for p, v in zip(prices, volumes)) / sum(volumes)
                    exchange_vwaps[exchange] = round(exchange_vwap, 2)
            
            return {
                "success": True,
                "global_vwap": round(vwap, 2),
                "exchange_vwaps": exchange_vwaps,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_price_impact(self, symbol: str, quantity: float, orderbook: List[Dict]) -> Dict:
        try:
            if not orderbook:
                return {
                    "success": False,
                    "error": "Empty orderbook"
                }
            
            total_volume = 0
            weighted_price = 0
            levels_consumed = 0
            
            for level in orderbook:
                level_price = float(level.get('price', 0))
                level_volume = float(level.get('volume', 0))
                
                if total_volume + level_volume >= quantity:
                    remaining = quantity - total_volume
                    weighted_price += level_price * remaining
                    total_volume += remaining
                    levels_consumed += 1
                    break
                else:
                    weighted_price += level_price * level_volume
                    total_volume += level_volume
                    levels_consumed += 1
            
            if total_volume == 0:
                return {
                    "success": False,
                    "error": "Insufficient liquidity in orderbook"
                }
            
            average_price = weighted_price / total_volume
            best_price = float(orderbook[0].get('price', 0))
            price_impact = ((average_price - best_price) / best_price) * 100
            
            return {
                "success": True,
                "symbol": symbol,
                "quantity": quantity,
                "best_price": best_price,
                "average_execution_price": round(average_price, 2),
                "price_impact_pct": round(price_impact, 3),
                "levels_consumed": levels_consumed,
                "total_liquidity_available": sum(float(l.get('volume', 0)) for l in orderbook),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def recommend_execution_strategy(self, symbol: str, side: str, quantity: float, urgency: str, exchange_data: Dict) -> Dict:
        try:
            strategies = []
            
            single_best = self.find_best_execution(symbol, side, quantity, 
                                                   {k: v['price'] for k, v in exchange_data.items()})
            
            if single_best['success']:
                strategies.append({
                    "strategy": "single_exchange",
                    "description": f"Execute entire order on {single_best['best_exchange']}",
                    "exchange": single_best['best_exchange'],
                    "total_cost": single_best['total_cost'],
                    "execution_time": "Immediate",
                    "slippage_risk": "Low" if single_best['liquidity_score'] > 80 else "Medium"
                })
            
            split_result = self.split_order_across_exchanges(symbol, side, quantity,
                                                             {k: v['price'] for k, v in exchange_data.items()})
            
            if split_result['success']:
                strategies.append({
                    "strategy": "multi_exchange_split",
                    "description": f"Split order across {split_result['num_exchanges']} exchanges",
                    "allocations": split_result['allocations'],
                    "total_cost": split_result['total_cost'],
                    "execution_time": "1-2 seconds",
                    "slippage_risk": "Very Low"
                })
            
            strategies.append({
                "strategy": "twap",
                "description": "Time-Weighted Average Price - Split order over time",
                "execution_time": "5-15 minutes",
                "slippage_risk": "Very Low",
                "note": "Recommended for large orders"
            })
            
            if urgency.lower() == "high":
                recommended = strategies[0] if strategies else None
            elif urgency.lower() == "low":
                recommended = next((s for s in strategies if s['strategy'] == 'twap'), strategies[-1])
            else:
                recommended = next((s for s in strategies if s['strategy'] == 'multi_exchange_split'), strategies[0])
            
            return {
                "success": True,
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "urgency": urgency,
                "recommended_strategy": recommended,
                "all_strategies": strategies,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    router = SmartOrderRouter()
    
    test_prices = {
        'binance': 45000.50,
        'bybit': 45005.00,
        'phemex': 44995.00,
        'coinexx': 45010.00
    }
    
    result = router.find_best_execution("BTC/USDT", "buy", 1.5, test_prices)
    print(json.dumps(result, indent=2))
