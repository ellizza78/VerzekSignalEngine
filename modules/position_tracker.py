"""
Position Tracker - Manages trading positions and DCA levels
Handles position storage, retrieval, and persistence
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class PositionTracker:
    """Tracks all trading positions across users and exchanges"""
    
    def __init__(self, storage_path: str = "database/positions.json"):
        self.storage_path = storage_path
        self.positions: Dict[str, dict] = {}
        self._load_positions()
    
    def _load_positions(self):
        """Load positions from storage"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    self.positions = json.load(f)
            except Exception as e:
                print(f"Error loading positions: {e}")
                self.positions = {}
        else:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            self.positions = {}
    
    def _save_positions(self):
        """Save positions to storage"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.positions, f, indent=2)
        except Exception as e:
            print(f"Error saving positions: {e}")
    
    def add_position(self, position_data: dict) -> str:
        """Add a new position"""
        position_id = position_data.get("position_id")
        if not position_id:
            position_id = f"{position_data['user_id']}_{position_data['symbol']}_{int(datetime.now().timestamp())}"
            position_data["position_id"] = position_id
        
        self.positions[position_id] = position_data
        self._save_positions()
        return position_id
    
    def update_position(self, position_id: str, updates: dict):
        """Update an existing position"""
        if position_id in self.positions:
            self.positions[position_id].update(updates)
            self._save_positions()
    
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
            self._save_positions()
    
    def delete_position(self, position_id: str):
        """Delete a position (use sparingly, prefer closing)"""
        if position_id in self.positions:
            del self.positions[position_id]
            self._save_positions()
    
    def get_position_count(self, user_id: str, status: str = "active") -> int:
        """Get count of positions for a user"""
        return len(self.get_user_positions(user_id, status))
    
    def get_all_positions(self) -> List[dict]:
        """Get all positions"""
        return list(self.positions.values())
