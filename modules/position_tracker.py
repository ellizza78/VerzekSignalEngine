"""
Position Tracker - Manages trading positions and DCA levels
Handles position storage, retrieval, and persistence
Now using SQLite for production-grade ACID compliance
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from modules.database import get_database


class PositionTracker:
    """Tracks all trading positions across users and exchanges - SQLite backend"""
    
    def __init__(self, storage_path: str = "database/positions.json"):
        self.db = get_database()
        self.positions: Dict[str, dict] = {}
        self._load_positions_from_db()
    
    def _load_positions_from_db(self):
        """Load positions from SQLite database"""
        try:
            db_positions = self.db.get_positions()
            for db_pos in db_positions:
                position_dict = dict(db_pos)
                if position_dict.get('data'):
                    position_dict.update(position_dict['data'])
                self.positions[db_pos['position_id']] = position_dict
        except Exception as e:
            print(f"Error loading positions from database: {e}")
            self.positions = {}
    
    def _save_position_to_db(self, position_data: dict):
        """Save single position to database"""
        try:
            position_id = position_data.get("position_id")
            existing = self.db.get_positions()
            position_exists = any(p['position_id'] == position_id for p in existing)
            
            if position_exists:
                self.db.update_position(
                    position_id,
                    status=position_data.get('status', 'OPEN'),
                    pnl=position_data.get('pnl', 0.0),
                    data=position_data
                )
            else:
                self.db.create_position(
                    position_id=position_id,
                    user_id=position_data.get('user_id', ''),
                    symbol=position_data.get('symbol', ''),
                    exchange=position_data.get('exchange', ''),
                    side=position_data.get('side', ''),
                    entry_price=position_data.get('entry_price', 0.0),
                    quantity=position_data.get('quantity', 0.0),
                    leverage=position_data.get('leverage'),
                    stop_loss=position_data.get('stop_loss'),
                    take_profit_levels=position_data.get('take_profit_levels', []),
                    status=position_data.get('status', 'OPEN'),
                    data=position_data
                )
        except Exception as e:
            print(f"Error saving position to database: {e}")
    
    def add_position(self, position_data: dict) -> str:
        """Add a new position"""
        position_id = position_data.get("position_id")
        if not position_id:
            position_id = f"{position_data['user_id']}_{position_data['symbol']}_{int(datetime.now().timestamp())}"
            position_data["position_id"] = position_id
        
        self.positions[position_id] = position_data
        self._save_position_to_db(position_data)
        return position_id
    
    def update_position(self, position_id: str, updates: dict):
        """Update an existing position"""
        if position_id in self.positions:
            self.positions[position_id].update(updates)
            self._save_position_to_db(self.positions[position_id])
    
    def get_position(self, position_id: str) -> Optional[dict]:
        """Get a specific position"""
        return self.positions.get(position_id)
    
    def get_user_positions(self, user_id: str, status: Optional[str] = None) -> List[dict]:
        """Get all positions for a user, optionally filtered by status"""
        positions = [p for p in self.positions.values() if p.get("user_id") == user_id]
        if status:
            positions = [p for p in positions if p.get("status") == status]
        return positions
    
    def get_active_positions(self, user_id: Optional[str] = None) -> List[dict]:
        """Get all active positions, optionally for a specific user"""
        positions = [p for p in self.positions.values() if p.get("status") == "active"]
        if user_id:
            positions = [p for p in positions if p.get("user_id") == user_id]
        return positions
    
    def close_position(self, position_id: str, close_data: dict):
        """Close a position"""
        if position_id in self.positions:
            self.positions[position_id].update({
                "status": "closed",
                "closed_at": datetime.now().isoformat(),
                **close_data
            })
            self._save_position_to_db(self.positions[position_id])
    
    def delete_position(self, position_id: str):
        """Delete a position (use sparingly, prefer closing)"""
        if position_id in self.positions:
            del self.positions[position_id]
        try:
            conn = self.db._get_connection()
            conn.execute("DELETE FROM positions WHERE position_id = ?", (position_id,))
            conn.commit()
        except Exception as e:
            print(f"Error deleting position: {e}")
    
    def get_position_count(self, user_id: str, status: str = "active") -> int:
        """Get count of positions for a user"""
        return len(self.get_user_positions(user_id, status))
    
    def get_all_positions(self) -> List[dict]:
        """Get all positions"""
        return list(self.positions.values())
