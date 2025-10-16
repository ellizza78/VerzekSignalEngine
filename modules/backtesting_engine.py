import json
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class BacktestingEngine:
    """Backtesting engine for strategy validation"""
    
    def __init__(self, position_tracker):
        self.position_tracker = position_tracker
        self.backtest_results_file = "database/backtest_results.json"
        self.historical_data_file = "database/historical_data.json"
        
    def _load_historical_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Load historical price data"""
        if os.path.exists(self.historical_data_file):
            try:
                with open(self.historical_data_file, 'r') as f:
                    data = json.load(f)
                    if symbol in data:
                        df = pd.DataFrame(data[symbol])
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        df = df.sort_values('timestamp')
                        return df.tail(days * 24)
            except:
                pass
        
        dates = pd.date_range(end=datetime.utcnow(), periods=days*24, freq='H')
        base_price = 50000 if 'BTC' in symbol else 3000 if 'ETH' in symbol else 100
        
        prices = []
        current_price = base_price
        
        for _ in range(len(dates)):
            change = np.random.normal(0, 0.02)
            current_price = current_price * (1 + change)
            prices.append(current_price)
        
        return pd.DataFrame({
            'timestamp': dates,
            'price': prices,
            'volume': np.random.uniform(1000, 10000, len(dates))
        })
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        df['sma_20'] = df['price'].rolling(window=20).mean()
        df['sma_50'] = df['price'].rolling(window=50).mean()
        
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        df['bb_middle'] = df['price'].rolling(window=20).mean()
        bb_std = df['price'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        return df
    
    def backtest_strategy(self, strategy_config: Dict, symbol: str, days: int = 30) -> Dict:
        """
        Run backtest on a strategy
        
        strategy_config example:
        {
            "name": "RSI Strategy",
            "entry_conditions": {"rsi": {"operator": "<", "value": 30}},
            "exit_conditions": {"rsi": {"operator": ">", "value": 70}},
            "position_size": 1000,
            "stop_loss_pct": 5,
            "take_profit_pct": 10
        }
        """
        df = self._load_historical_data(symbol, days)
        df = self._calculate_indicators(df)
        
        df = df.dropna()
        
        if df.empty:
            return {'success': False, 'error': 'Insufficient data for backtest'}
        
        trades = []
        in_position = False
        entry_price = 0
        entry_index = 0
        
        initial_capital = 10000
        capital = initial_capital
        position_size = strategy_config.get('position_size', 1000)
        stop_loss_pct = strategy_config.get('stop_loss_pct', 5)
        take_profit_pct = strategy_config.get('take_profit_pct', 10)
        
        for i in range(len(df)):
            row = df.iloc[i]
            
            if not in_position:
                entry_signal = self._check_entry_conditions(
                    row, 
                    strategy_config.get('entry_conditions', {})
                )
                
                if entry_signal and capital >= position_size:
                    in_position = True
                    entry_price = row['price']
                    entry_index = i
                    
            else:
                exit_signal = self._check_exit_conditions(
                    row, 
                    strategy_config.get('exit_conditions', {})
                )
                
                stop_hit = (entry_price - row['price']) / entry_price * 100 >= stop_loss_pct
                tp_hit = (row['price'] - entry_price) / entry_price * 100 >= take_profit_pct
                
                if exit_signal or stop_hit or tp_hit:
                    exit_price = row['price']
                    pnl = (exit_price - entry_price) / entry_price * position_size
                    capital += pnl
                    
                    trades.append({
                        'entry_time': str(df.iloc[entry_index]['timestamp']),
                        'exit_time': str(row['timestamp']),
                        'entry_price': round(entry_price, 2),
                        'exit_price': round(exit_price, 2),
                        'pnl': round(pnl, 2),
                        'pnl_pct': round((exit_price - entry_price) / entry_price * 100, 2),
                        'exit_reason': 'stop_loss' if stop_hit else 'take_profit' if tp_hit else 'signal'
                    })
                    
                    in_position = False
        
        if not trades:
            return {
                'success': True,
                'symbol': symbol,
                'strategy': strategy_config.get('name', 'Unnamed'),
                'message': 'No trades generated during backtest period',
                'total_trades': 0
            }
        
        wins = [t for t in trades if t['pnl'] > 0]
        losses = [t for t in trades if t['pnl'] <= 0]
        
        total_pnl = sum([t['pnl'] for t in trades])
        win_rate = len(wins) / len(trades) * 100 if trades else 0
        avg_win = sum([t['pnl'] for t in wins]) / len(wins) if wins else 0
        avg_loss = sum([t['pnl'] for t in losses]) / len(losses) if losses else 0
        profit_factor = abs(sum([t['pnl'] for t in wins]) / sum([t['pnl'] for t in losses])) if losses and sum([t['pnl'] for t in losses]) != 0 else 0
        
        max_drawdown = 0
        peak = initial_capital
        running_capital = initial_capital
        
        for trade in trades:
            running_capital += trade['pnl']
            if running_capital > peak:
                peak = running_capital
            drawdown = (peak - running_capital) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        result = {
            'success': True,
            'backtest_id': f"bt_{datetime.utcnow().timestamp()}",
            'symbol': symbol,
            'strategy': strategy_config.get('name', 'Unnamed'),
            'period': f"{days} days",
            'total_trades': len(trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': round(win_rate, 1),
            'total_pnl': round(total_pnl, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown_pct': round(max_drawdown, 2),
            'initial_capital': initial_capital,
            'final_capital': round(capital, 2),
            'return_pct': round((capital - initial_capital) / initial_capital * 100, 2),
            'trades': trades[-10:],
            'tested_at': datetime.utcnow().isoformat()
        }
        
        self._save_backtest_result(result)
        
        return result
    
    def _check_entry_conditions(self, row: pd.Series, conditions: Dict) -> bool:
        """Check if entry conditions are met"""
        if 'rsi' in conditions:
            rsi_cond = conditions['rsi']
            if rsi_cond['operator'] == '<' and row.get('rsi', 50) < rsi_cond['value']:
                return True
            if rsi_cond['operator'] == '>' and row.get('rsi', 50) > rsi_cond['value']:
                return True
        
        if 'price_above_sma' in conditions:
            if row['price'] > row.get('sma_20', row['price']):
                return True
        
        if 'price_below_sma' in conditions:
            if row['price'] < row.get('sma_20', row['price']):
                return True
        
        return False
    
    def _check_exit_conditions(self, row: pd.Series, conditions: Dict) -> bool:
        """Check if exit conditions are met"""
        if 'rsi' in conditions:
            rsi_cond = conditions['rsi']
            if rsi_cond['operator'] == '>' and row.get('rsi', 50) > rsi_cond['value']:
                return True
            if rsi_cond['operator'] == '<' and row.get('rsi', 50) < rsi_cond['value']:
                return True
        
        return False
    
    def _save_backtest_result(self, result: Dict):
        """Save backtest result"""
        results = []
        if os.path.exists(self.backtest_results_file):
            try:
                with open(self.backtest_results_file, 'r') as f:
                    results = json.load(f)
            except:
                pass
        
        results.append(result)
        results = results[-100:]
        
        os.makedirs(os.path.dirname(self.backtest_results_file), exist_ok=True)
        with open(self.backtest_results_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    def get_backtest_history(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get backtest history"""
        if not os.path.exists(self.backtest_results_file):
            return []
        
        try:
            with open(self.backtest_results_file, 'r') as f:
                results = json.load(f)
                return results[-20:]
        except:
            return []
