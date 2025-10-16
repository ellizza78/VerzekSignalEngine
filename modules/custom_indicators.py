import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

class CustomIndicatorEngine:
    """User-defined custom trading indicators and strategies"""
    
    def __init__(self, position_tracker):
        self.position_tracker = position_tracker
        self.indicators_file = "database/custom_indicators.json"
        self.strategies_file = "database/custom_strategies.json"
        self.indicators = self._load_indicators()
        self.strategies = self._load_strategies()
        
    def _load_indicators(self) -> Dict:
        """Load custom indicators"""
        if os.path.exists(self.indicators_file):
            try:
                with open(self.indicators_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_indicators(self):
        """Save custom indicators"""
        os.makedirs(os.path.dirname(self.indicators_file), exist_ok=True)
        with open(self.indicators_file, 'w') as f:
            json.dump(self.indicators, f, indent=2)
    
    def _load_strategies(self) -> Dict:
        """Load custom strategies"""
        if os.path.exists(self.strategies_file):
            try:
                with open(self.strategies_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_strategies(self):
        """Save custom strategies"""
        os.makedirs(os.path.dirname(self.strategies_file), exist_ok=True)
        with open(self.strategies_file, 'w') as f:
            json.dump(self.strategies, f, indent=2)
    
    def create_indicator(self, user_id: str, indicator_config: Dict) -> Dict:
        """
        Create a custom indicator
        
        Example indicator_config:
        {
            "name": "My RSI Strategy",
            "type": "rsi",
            "period": 14,
            "overbought": 70,
            "oversold": 30
        }
        """
        indicator_id = f"ind_{uuid.uuid4().hex[:8]}"
        
        indicator = {
            'indicator_id': indicator_id,
            'user_id': user_id,
            'name': indicator_config.get('name'),
            'type': indicator_config.get('type'),
            'parameters': indicator_config.get('parameters', {}),
            'enabled': True,
            'created_at': datetime.utcnow().isoformat()
        }
        
        if indicator['type'] == 'rsi':
            indicator['parameters'] = {
                'period': indicator_config.get('period', 14),
                'overbought': indicator_config.get('overbought', 70),
                'oversold': indicator_config.get('oversold', 30)
            }
        elif indicator['type'] == 'moving_average':
            indicator['parameters'] = {
                'period': indicator_config.get('period', 20),
                'type': indicator_config.get('ma_type', 'SMA')
            }
        elif indicator['type'] == 'bollinger_bands':
            indicator['parameters'] = {
                'period': indicator_config.get('period', 20),
                'std_dev': indicator_config.get('std_dev', 2)
            }
        
        self.indicators[indicator_id] = indicator
        self._save_indicators()
        
        return {
            'success': True,
            'indicator_id': indicator_id,
            'indicator': indicator
        }
    
    def create_strategy(self, user_id: str, strategy_config: Dict) -> Dict:
        """
        Create a custom trading strategy with conditions
        
        Example strategy_config:
        {
            "name": "RSI + MA Cross",
            "conditions": [
                {"type": "rsi", "operator": "<", "value": 30},
                {"type": "price", "operator": ">", "ma_period": 20}
            ],
            "action": "BUY",
            "symbols": ["BTCUSDT", "ETHUSDT"]
        }
        """
        strategy_id = f"strat_{uuid.uuid4().hex[:8]}"
        
        strategy = {
            'strategy_id': strategy_id,
            'user_id': user_id,
            'name': strategy_config.get('name'),
            'description': strategy_config.get('description', ''),
            'conditions': strategy_config.get('conditions', []),
            'action': strategy_config.get('action'),
            'symbols': strategy_config.get('symbols', []),
            'position_size': strategy_config.get('position_size', 100),
            'stop_loss_pct': strategy_config.get('stop_loss_pct'),
            'take_profit_pct': strategy_config.get('take_profit_pct'),
            'enabled': True,
            'signals_generated': 0,
            'trades_executed': 0,
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.strategies[strategy_id] = strategy
        self._save_strategies()
        
        return {
            'success': True,
            'strategy_id': strategy_id,
            'strategy': strategy
        }
    
    def evaluate_strategy(self, strategy_id: str, market_data: Dict) -> Dict:
        """Evaluate if strategy conditions are met"""
        if strategy_id not in self.strategies:
            return {'success': False, 'error': 'Strategy not found'}
        
        strategy = self.strategies[strategy_id]
        
        if not strategy.get('enabled'):
            return {'success': True, 'signal': None, 'reason': 'Strategy disabled'}
        
        conditions_met = 0
        total_conditions = len(strategy['conditions'])
        
        for condition in strategy['conditions']:
            if condition['type'] == 'rsi':
                market_rsi = market_data.get('rsi', 50)
                
                if condition['operator'] == '<' and market_rsi < condition['value']:
                    conditions_met += 1
                elif condition['operator'] == '>' and market_rsi > condition['value']:
                    conditions_met += 1
                elif condition['operator'] == '==' and abs(market_rsi - condition['value']) < 2:
                    conditions_met += 1
            
            elif condition['type'] == 'price':
                current_price = market_data.get('price', 0)
                ma_value = market_data.get(f"ma_{condition.get('ma_period', 20)}", current_price)
                
                if condition['operator'] == '>' and current_price > ma_value:
                    conditions_met += 1
                elif condition['operator'] == '<' and current_price < ma_value:
                    conditions_met += 1
            
            elif condition['type'] == 'volume':
                current_volume = market_data.get('volume', 0)
                avg_volume = market_data.get('avg_volume', current_volume)
                
                if condition['operator'] == '>' and current_volume > avg_volume * condition.get('multiplier', 1.5):
                    conditions_met += 1
        
        if conditions_met == total_conditions:
            strategy['signals_generated'] = strategy.get('signals_generated', 0) + 1
            self._save_strategies()
            
            return {
                'success': True,
                'signal': strategy['action'],
                'symbol': market_data.get('symbol'),
                'strategy_name': strategy['name'],
                'conditions_met': f"{conditions_met}/{total_conditions}",
                'position_size': strategy.get('position_size'),
                'stop_loss_pct': strategy.get('stop_loss_pct'),
                'take_profit_pct': strategy.get('take_profit_pct')
            }
        
        return {
            'success': True,
            'signal': None,
            'conditions_met': f"{conditions_met}/{total_conditions}",
            'reason': 'Not all conditions met'
        }
    
    def get_user_strategies(self, user_id: str) -> List[Dict]:
        """Get all strategies for a user"""
        user_strategies = [
            s for s in self.strategies.values()
            if s['user_id'] == user_id
        ]
        return user_strategies
    
    def toggle_strategy(self, user_id: str, strategy_id: str, enabled: bool) -> Dict:
        """Enable or disable a strategy"""
        if strategy_id not in self.strategies:
            return {'success': False, 'error': 'Strategy not found'}
        
        if self.strategies[strategy_id]['user_id'] != user_id:
            return {'success': False, 'error': 'Unauthorized'}
        
        self.strategies[strategy_id]['enabled'] = enabled
        self._save_strategies()
        
        return {
            'success': True,
            'strategy_id': strategy_id,
            'enabled': enabled
        }
    
    def delete_strategy(self, user_id: str, strategy_id: str) -> Dict:
        """Delete a custom strategy"""
        if strategy_id not in self.strategies:
            return {'success': False, 'error': 'Strategy not found'}
        
        if self.strategies[strategy_id]['user_id'] != user_id:
            return {'success': False, 'error': 'Unauthorized'}
        
        del self.strategies[strategy_id]
        self._save_strategies()
        
        return {
            'success': True,
            'message': 'Strategy deleted'
        }
