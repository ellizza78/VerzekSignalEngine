import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import statistics

class TradingJournal:
    def __init__(self):
        self.journal_file = "database/trading_journal.json"
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs("database", exist_ok=True)
        if not os.path.exists(self.journal_file):
            with open(self.journal_file, 'w') as f:
                json.dump({"entries": [], "insights": []}, f)
    
    def add_entry(self, user_id: str, trade_data: Dict, notes: str = "", emotions: List[str] = None) -> Dict:
        try:
            with open(self.journal_file, 'r') as f:
                journal = json.load(f)
            
            entry = {
                "id": f"entry_{len(journal['entries'])}",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "trade": trade_data,
                "notes": notes,
                "emotions": emotions or [],
                "tags": self._auto_tag_trade(trade_data)
            }
            
            journal['entries'].append(entry)
            
            with open(self.journal_file, 'w') as f:
                json.dump(journal, f, indent=2)
            
            return {
                "success": True,
                "entry_id": entry['id'],
                "tags": entry['tags']
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_entries(self, user_id: str, limit: int = 50, filters: Dict = None) -> Dict:
        try:
            with open(self.journal_file, 'r') as f:
                journal = json.load(f)
            
            entries = [e for e in journal['entries'] if e['user_id'] == user_id]
            
            if filters:
                if 'start_date' in filters:
                    start = datetime.fromisoformat(filters['start_date'])
                    entries = [e for e in entries if datetime.fromisoformat(e['timestamp']) >= start]
                
                if 'end_date' in filters:
                    end = datetime.fromisoformat(filters['end_date'])
                    entries = [e for e in entries if datetime.fromisoformat(e['timestamp']) <= end]
                
                if 'tags' in filters:
                    entries = [e for e in entries if any(tag in e['tags'] for tag in filters['tags'])]
            
            entries = sorted(entries, key=lambda x: x['timestamp'], reverse=True)[:limit]
            
            return {
                "success": True,
                "entries": entries,
                "count": len(entries)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_patterns(self, user_id: str) -> Dict:
        try:
            with open(self.journal_file, 'r') as f:
                journal = json.load(f)
            
            user_entries = [e for e in journal['entries'] if e['user_id'] == user_id]
            
            if len(user_entries) < 10:
                return {
                    "success": True,
                    "message": "Insufficient data for pattern analysis (minimum 10 trades required)",
                    "patterns": []
                }
            
            patterns = []
            
            time_pattern = self._analyze_time_patterns(user_entries)
            if time_pattern:
                patterns.append(time_pattern)
            
            emotion_pattern = self._analyze_emotion_patterns(user_entries)
            if emotion_pattern:
                patterns.append(emotion_pattern)
            
            symbol_pattern = self._analyze_symbol_patterns(user_entries)
            if symbol_pattern:
                patterns.append(symbol_pattern)
            
            mistake_pattern = self._identify_common_mistakes(user_entries)
            if mistake_pattern:
                patterns.extend(mistake_pattern)
            
            return {
                "success": True,
                "patterns": patterns,
                "total_trades_analyzed": len(user_entries),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_insights(self, user_id: str) -> Dict:
        try:
            with open(self.journal_file, 'r') as f:
                journal = json.load(f)
            
            user_entries = [e for e in journal['entries'] if e['user_id'] == user_id]
            
            if not user_entries:
                return {
                    "success": True,
                    "insights": ["Start logging trades to receive personalized insights"],
                    "metrics": {}
                }
            
            trades = [e['trade'] for e in user_entries]
            
            total_pnl = sum(float(t.get('pnl', 0)) for t in trades)
            wins = sum(1 for t in trades if float(t.get('pnl', 0)) > 0)
            losses = len(trades) - wins
            win_rate = (wins / len(trades)) * 100 if trades else 0
            
            avg_win = statistics.mean([float(t.get('pnl', 0)) for t in trades if float(t.get('pnl', 0)) > 0]) if wins > 0 else 0
            avg_loss = statistics.mean([float(t.get('pnl', 0)) for t in trades if float(t.get('pnl', 0)) < 0]) if losses > 0 else 0
            
            profit_factor = abs(avg_win * wins / (avg_loss * losses)) if avg_loss != 0 and losses > 0 else 0
            
            insights = []
            
            if win_rate > 60:
                insights.append(f"Strong performance with {win_rate:.1f}% win rate - maintain your strategy")
            elif win_rate < 40:
                insights.append(f"Win rate of {win_rate:.1f}% needs improvement - review entry criteria")
            
            if profit_factor > 2:
                insights.append(f"Excellent risk/reward with profit factor of {profit_factor:.2f}")
            elif profit_factor < 1:
                insights.append(f"Poor risk/reward (PF: {profit_factor:.2f}) - consider tighter stops and wider targets")
            
            if total_pnl < 0:
                insights.append("Overall negative PnL - consider reducing position sizes and reviewing strategy")
            
            best_day = self._find_best_worst_day(user_entries, 'best')
            worst_day = self._find_best_worst_day(user_entries, 'worst')
            
            if best_day:
                insights.append(f"Best trading day: {best_day['day']} (avg PnL: ${best_day['avg_pnl']:.2f})")
            if worst_day:
                insights.append(f"Avoid trading on {worst_day['day']} (avg PnL: ${worst_day['avg_pnl']:.2f})")
            
            metrics = {
                "total_trades": len(trades),
                "total_pnl": round(total_pnl, 2),
                "win_rate": round(win_rate, 2),
                "avg_win": round(avg_win, 2),
                "avg_loss": round(avg_loss, 2),
                "profit_factor": round(profit_factor, 2)
            }
            
            return {
                "success": True,
                "insights": insights,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _auto_tag_trade(self, trade: Dict) -> List[str]:
        tags = []
        
        pnl = float(trade.get('pnl', 0))
        if pnl > 0:
            tags.append("winner")
            if pnl > 500:
                tags.append("big_win")
        else:
            tags.append("loser")
            if pnl < -500:
                tags.append("big_loss")
        
        symbol = trade.get('symbol', '')
        if 'BTC' in symbol:
            tags.append("btc")
        elif 'ETH' in symbol:
            tags.append("eth")
        
        direction = trade.get('direction', '')
        if direction:
            tags.append(direction.lower())
        
        return tags
    
    def _analyze_time_patterns(self, entries: List[Dict]) -> Optional[Dict]:
        hour_performance = {}
        
        for entry in entries:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            hour = timestamp.hour
            pnl = float(entry['trade'].get('pnl', 0))
            
            if hour not in hour_performance:
                hour_performance[hour] = []
            hour_performance[hour].append(pnl)
        
        best_hour = max(hour_performance.items(), key=lambda x: statistics.mean(x[1]))
        worst_hour = min(hour_performance.items(), key=lambda x: statistics.mean(x[1]))
        
        return {
            "type": "time_pattern",
            "best_hour": f"{best_hour[0]}:00",
            "best_hour_avg_pnl": round(statistics.mean(best_hour[1]), 2),
            "worst_hour": f"{worst_hour[0]}:00",
            "worst_hour_avg_pnl": round(statistics.mean(worst_hour[1]), 2),
            "recommendation": f"Focus trading around {best_hour[0]}:00, avoid {worst_hour[0]}:00"
        }
    
    def _analyze_emotion_patterns(self, entries: List[Dict]) -> Optional[Dict]:
        emotion_pnl = {}
        
        for entry in entries:
            emotions = entry.get('emotions', [])
            pnl = float(entry['trade'].get('pnl', 0))
            
            for emotion in emotions:
                if emotion not in emotion_pnl:
                    emotion_pnl[emotion] = []
                emotion_pnl[emotion].append(pnl)
        
        if not emotion_pnl:
            return None
        
        best_emotion = max(emotion_pnl.items(), key=lambda x: statistics.mean(x[1]))
        worst_emotion = min(emotion_pnl.items(), key=lambda x: statistics.mean(x[1]))
        
        return {
            "type": "emotion_pattern",
            "best_emotion": best_emotion[0],
            "best_emotion_avg_pnl": round(statistics.mean(best_emotion[1]), 2),
            "worst_emotion": worst_emotion[0],
            "worst_emotion_avg_pnl": round(statistics.mean(worst_emotion[1]), 2),
            "recommendation": f"Trades when feeling '{best_emotion[0]}' perform best, avoid trading when '{worst_emotion[0]}'"
        }
    
    def _analyze_symbol_patterns(self, entries: List[Dict]) -> Optional[Dict]:
        symbol_stats = {}
        
        for entry in entries:
            symbol = entry['trade'].get('symbol', 'Unknown')
            pnl = float(entry['trade'].get('pnl', 0))
            
            if symbol not in symbol_stats:
                symbol_stats[symbol] = []
            symbol_stats[symbol].append(pnl)
        
        best_symbol = max(symbol_stats.items(), key=lambda x: sum(x[1]))
        worst_symbol = min(symbol_stats.items(), key=lambda x: sum(x[1]))
        
        return {
            "type": "symbol_pattern",
            "best_symbol": best_symbol[0],
            "best_symbol_total_pnl": round(sum(best_symbol[1]), 2),
            "worst_symbol": worst_symbol[0],
            "worst_symbol_total_pnl": round(sum(worst_symbol[1]), 2),
            "recommendation": f"Focus on {best_symbol[0]}, reconsider trading {worst_symbol[0]}"
        }
    
    def _identify_common_mistakes(self, entries: List[Dict]) -> List[Dict]:
        mistakes = []
        
        losing_trades = [e for e in entries if float(e['trade'].get('pnl', 0)) < 0]
        
        if len(losing_trades) > len(entries) * 0.5:
            avg_loss = statistics.mean([float(e['trade'].get('pnl', 0)) for e in losing_trades])
            mistakes.append({
                "type": "common_mistake",
                "mistake": "High loss frequency",
                "description": f"Over 50% of trades are losses (avg loss: ${avg_loss:.2f})",
                "recommendation": "Tighten entry criteria and improve trade selection"
            })
        
        big_losses = [e for e in losing_trades if float(e['trade'].get('pnl', 0)) < -500]
        if len(big_losses) > 3:
            mistakes.append({
                "type": "common_mistake",
                "mistake": "Large losses",
                "description": f"Experienced {len(big_losses)} trades with losses exceeding $500",
                "recommendation": "Implement strict stop losses and reduce position sizes"
            })
        
        return mistakes
    
    def _find_best_worst_day(self, entries: List[Dict], mode: str) -> Optional[Dict]:
        day_pnl = {}
        
        for entry in entries:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            day_name = timestamp.strftime('%A')
            pnl = float(entry['trade'].get('pnl', 0))
            
            if day_name not in day_pnl:
                day_pnl[day_name] = []
            day_pnl[day_pnl].append(pnl)
        
        if not day_pnl:
            return None
        
        if mode == 'best':
            best = max(day_pnl.items(), key=lambda x: statistics.mean(x[1]))
            return {"day": best[0], "avg_pnl": statistics.mean(best[1])}
        else:
            worst = min(day_pnl.items(), key=lambda x: statistics.mean(x[1]))
            return {"day": worst[0], "avg_pnl": statistics.mean(worst[1])}


if __name__ == "__main__":
    journal = TradingJournal()
    
    trade = {
        "symbol": "BTC/USDT",
        "direction": "LONG",
        "pnl": 250,
        "entry": 45000,
        "exit": 45250
    }
    
    journal.add_entry("user_123", trade, "Great trade, followed the plan", ["confident", "focused"])
    
    print(json.dumps(journal.generate_insights("user_123"), indent=2))
