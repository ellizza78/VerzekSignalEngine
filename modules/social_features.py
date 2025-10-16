import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os

class SocialFeaturesManager:
    def __init__(self):
        self.chats_file = "database/live_chats.json"
        self.leaderboard_file = "database/leaderboard.json"
        self.competitions_file = "database/competitions.json"
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs("database", exist_ok=True)
        
        if not os.path.exists(self.chats_file):
            with open(self.chats_file, 'w') as f:
                json.dump({"rooms": {}, "messages": {}}, f)
        
        if not os.path.exists(self.leaderboard_file):
            with open(self.leaderboard_file, 'w') as f:
                json.dump({"daily": [], "weekly": [], "monthly": [], "all_time": []}, f)
        
        if not os.path.exists(self.competitions_file):
            with open(self.competitions_file, 'w') as f:
                json.dump({"active": [], "past": []}, f)
    
    def send_message(self, room_id: str, user_id: str, username: str, message: str) -> Dict:
        try:
            with open(self.chats_file, 'r') as f:
                chats = json.load(f)
            
            if room_id not in chats['rooms']:
                chats['rooms'][room_id] = {
                    "created_at": datetime.now().isoformat(),
                    "participants": []
                }
            
            if user_id not in chats['rooms'][room_id]['participants']:
                chats['rooms'][room_id]['participants'].append(user_id)
            
            if room_id not in chats['messages']:
                chats['messages'][room_id] = []
            
            message_obj = {
                "id": f"msg_{len(chats['messages'][room_id])}",
                "user_id": user_id,
                "username": username,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            
            chats['messages'][room_id].append(message_obj)
            
            if len(chats['messages'][room_id]) > 1000:
                chats['messages'][room_id] = chats['messages'][room_id][-1000:]
            
            with open(self.chats_file, 'w') as f:
                json.dump(chats, f, indent=2)
            
            return {
                "success": True,
                "message_id": message_obj['id'],
                "room_id": room_id,
                "timestamp": message_obj['timestamp']
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_messages(self, room_id: str, limit: int = 50, before_id: Optional[str] = None) -> Dict:
        try:
            with open(self.chats_file, 'r') as f:
                chats = json.load(f)
            
            if room_id not in chats['messages']:
                return {
                    "success": True,
                    "messages": [],
                    "room_id": room_id
                }
            
            messages = chats['messages'][room_id]
            
            if before_id:
                before_index = next((i for i, msg in enumerate(messages) if msg['id'] == before_id), len(messages))
                messages = messages[:before_index]
            
            messages = messages[-limit:]
            
            return {
                "success": True,
                "messages": messages,
                "room_id": room_id,
                "count": len(messages)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_active_rooms(self) -> Dict:
        try:
            with open(self.chats_file, 'r') as f:
                chats = json.load(f)
            
            active_rooms = []
            for room_id, room_data in chats['rooms'].items():
                recent_messages = len([m for m in chats['messages'].get(room_id, []) 
                                     if (datetime.now() - datetime.fromisoformat(m['timestamp'])).total_seconds() < 3600])
                
                active_rooms.append({
                    "room_id": room_id,
                    "participants_count": len(room_data['participants']),
                    "recent_messages": recent_messages,
                    "created_at": room_data['created_at']
                })
            
            active_rooms.sort(key=lambda x: x['recent_messages'], reverse=True)
            
            return {
                "success": True,
                "rooms": active_rooms
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_leaderboard(self, user_id: str, username: str, pnl: float, win_rate: float, total_trades: int) -> Dict:
        try:
            with open(self.leaderboard_file, 'r') as f:
                leaderboard = json.load(f)
            
            user_entry = {
                "user_id": user_id,
                "username": username,
                "pnl": pnl,
                "win_rate": win_rate,
                "total_trades": total_trades,
                "updated_at": datetime.now().isoformat()
            }
            
            for period in ['daily', 'weekly', 'monthly', 'all_time']:
                existing = next((i for i, u in enumerate(leaderboard[period]) if u['user_id'] == user_id), None)
                
                if existing is not None:
                    leaderboard[period][existing] = user_entry
                else:
                    leaderboard[period].append(user_entry)
                
                leaderboard[period].sort(key=lambda x: x['pnl'], reverse=True)
                leaderboard[period] = leaderboard[period][:100]
            
            with open(self.leaderboard_file, 'w') as f:
                json.dump(leaderboard, f, indent=2)
            
            rank = next((i+1 for i, u in enumerate(leaderboard['all_time']) if u['user_id'] == user_id), None)
            
            return {
                "success": True,
                "user_id": user_id,
                "rank": rank,
                "pnl": pnl,
                "win_rate": win_rate
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_leaderboard(self, period: str = 'all_time', limit: int = 100) -> Dict:
        try:
            with open(self.leaderboard_file, 'r') as f:
                leaderboard = json.load(f)
            
            if period not in leaderboard:
                period = 'all_time'
            
            entries = leaderboard[period][:limit]
            
            return {
                "success": True,
                "period": period,
                "entries": entries,
                "count": len(entries)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_user_rank(self, user_id: str, period: str = 'all_time') -> Dict:
        try:
            with open(self.leaderboard_file, 'r') as f:
                leaderboard = json.load(f)
            
            if period not in leaderboard:
                period = 'all_time'
            
            rank = next((i+1 for i, u in enumerate(leaderboard[period]) if u['user_id'] == user_id), None)
            
            if rank is None:
                return {
                    "success": True,
                    "user_id": user_id,
                    "rank": None,
                    "message": "User not in leaderboard"
                }
            
            user_data = leaderboard[period][rank-1]
            
            return {
                "success": True,
                "user_id": user_id,
                "rank": rank,
                "pnl": user_data['pnl'],
                "win_rate": user_data['win_rate'],
                "total_trades": user_data['total_trades']
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_competition(self, name: str, description: str, start_date: str, end_date: str, prize_pool: float, rules: Dict) -> Dict:
        try:
            with open(self.competitions_file, 'r') as f:
                competitions = json.load(f)
            
            competition = {
                "id": f"comp_{len(competitions['active']) + len(competitions['past'])}",
                "name": name,
                "description": description,
                "start_date": start_date,
                "end_date": end_date,
                "prize_pool": prize_pool,
                "rules": rules,
                "participants": [],
                "leaderboard": [],
                "status": "upcoming",
                "created_at": datetime.now().isoformat()
            }
            
            start_dt = datetime.fromisoformat(start_date)
            if start_dt <= datetime.now():
                competition['status'] = "active"
            
            competitions['active'].append(competition)
            
            with open(self.competitions_file, 'w') as f:
                json.dump(competitions, f, indent=2)
            
            return {
                "success": True,
                "competition_id": competition['id'],
                "name": name,
                "status": competition['status']
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def join_competition(self, competition_id: str, user_id: str, username: str) -> Dict:
        try:
            with open(self.competitions_file, 'r') as f:
                competitions = json.load(f)
            
            competition = next((c for c in competitions['active'] if c['id'] == competition_id), None)
            
            if not competition:
                return {
                    "success": False,
                    "error": "Competition not found"
                }
            
            if competition['status'] not in ['upcoming', 'active']:
                return {
                    "success": False,
                    "error": "Competition is not open for registration"
                }
            
            if user_id in competition['participants']:
                return {
                    "success": False,
                    "error": "Already registered"
                }
            
            competition['participants'].append(user_id)
            competition['leaderboard'].append({
                "user_id": user_id,
                "username": username,
                "score": 0,
                "pnl": 0,
                "trades": 0
            })
            
            with open(self.competitions_file, 'w') as f:
                json.dump(competitions, f, indent=2)
            
            return {
                "success": True,
                "competition_id": competition_id,
                "user_id": user_id,
                "participants_count": len(competition['participants'])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_competition_score(self, competition_id: str, user_id: str, pnl: float, trades: int) -> Dict:
        try:
            with open(self.competitions_file, 'r') as f:
                competitions = json.load(f)
            
            competition = next((c for c in competitions['active'] if c['id'] == competition_id), None)
            
            if not competition:
                return {
                    "success": False,
                    "error": "Competition not found"
                }
            
            user_entry = next((u for u in competition['leaderboard'] if u['user_id'] == user_id), None)
            
            if not user_entry:
                return {
                    "success": False,
                    "error": "User not registered in competition"
                }
            
            user_entry['pnl'] = pnl
            user_entry['trades'] = trades
            user_entry['score'] = pnl
            user_entry['updated_at'] = datetime.now().isoformat()
            
            competition['leaderboard'].sort(key=lambda x: x['score'], reverse=True)
            
            with open(self.competitions_file, 'w') as f:
                json.dump(competitions, f, indent=2)
            
            rank = next((i+1 for i, u in enumerate(competition['leaderboard']) if u['user_id'] == user_id), None)
            
            return {
                "success": True,
                "competition_id": competition_id,
                "user_id": user_id,
                "rank": rank,
                "score": pnl
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_competitions(self, status: str = 'active') -> Dict:
        try:
            with open(self.competitions_file, 'r') as f:
                competitions = json.load(f)
            
            if status == 'active':
                comps = competitions.get('active', [])
            elif status == 'past':
                comps = competitions.get('past', [])
            else:
                comps = competitions.get('active', []) + competitions.get('past', [])
            
            return {
                "success": True,
                "competitions": comps,
                "count": len(comps)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_competition_leaderboard(self, competition_id: str) -> Dict:
        try:
            with open(self.competitions_file, 'r') as f:
                competitions = json.load(f)
            
            competition = next((c for c in competitions['active'] + competitions['past'] if c['id'] == competition_id), None)
            
            if not competition:
                return {
                    "success": False,
                    "error": "Competition not found"
                }
            
            return {
                "success": True,
                "competition_id": competition_id,
                "name": competition['name'],
                "leaderboard": competition['leaderboard'],
                "participants_count": len(competition['participants'])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    manager = SocialFeaturesManager()
    
    manager.send_message("general", "user1", "John", "Hello everyone!")
    manager.update_leaderboard("user1", "John", 1500.50, 0.65, 120)
    
    print(json.dumps(manager.get_leaderboard('all_time', 10), indent=2))
