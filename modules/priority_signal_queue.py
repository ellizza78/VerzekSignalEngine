"""
Priority Signal Queue
Manages priority and regular trading signals with queue system
"""

import os
import json
import time
from typing import Dict, List, Optional
from collections import deque

class PrioritySignalQueue:
    """Queue system for managing priority and regular trading signals"""
    
    def __init__(self, db_file="database/signal_queue.json"):
        self.db_file = db_file
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        
        # In-memory queues
        self.priority_queue = deque()  # High priority signals
        self.regular_queue = deque()   # Normal signals
        
        # Load from disk if exists
        self._load_from_disk()
    
    def _load_from_disk(self):
        """Load queued signals from disk"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    self.priority_queue = deque(data.get('priority', []))
                    self.regular_queue = deque(data.get('regular', []))
            except Exception as e:
                print(f"⚠️ Error loading signal queue: {e}")
    
    def _save_to_disk(self):
        """Save queued signals to disk"""
        try:
            data = {
                'priority': list(self.priority_queue),
                'regular': list(self.regular_queue),
                'updated_at': time.time()
            }
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving signal queue: {e}")
    
    def add_signal(self, signal_data: Dict, is_priority: bool = False):
        """
        Add signal to queue
        
        Args:
            signal_data: Signal information dict
            is_priority: If True, adds to priority queue
        """
        signal_entry = {
            **signal_data,
            'queued_at': time.time(),
            'is_priority': is_priority
        }
        
        if is_priority:
            self.priority_queue.append(signal_entry)
            print(f"⚡ Added PRIORITY signal to queue: {signal_data.get('symbol', 'UNKNOWN')}")
        else:
            self.regular_queue.append(signal_entry)
            print(f"📥 Added regular signal to queue: {signal_data.get('symbol', 'UNKNOWN')}")
        
        self._save_to_disk()
    
    def get_next_signal(self) -> Optional[Dict]:
        """
        Get next signal to process (priority signals first)
        
        Returns:
            Signal dict or None if queue is empty
        """
        # Always process priority signals first
        if self.priority_queue:
            signal = self.priority_queue.popleft()
            self._save_to_disk()
            print(f"⚡ Processing PRIORITY signal: {signal.get('symbol', 'UNKNOWN')}")
            return signal
        
        # Then process regular signals
        if self.regular_queue:
            signal = self.regular_queue.popleft()
            self._save_to_disk()
            print(f"📤 Processing regular signal: {signal.get('symbol', 'UNKNOWN')}")
            return signal
        
        return None
    
    def peek_next_signal(self) -> Optional[Dict]:
        """
        Peek at next signal without removing it
        
        Returns:
            Signal dict or None if queue is empty
        """
        if self.priority_queue:
            return self.priority_queue[0]
        if self.regular_queue:
            return self.regular_queue[0]
        return None
    
    def get_queue_stats(self) -> Dict:
        """Get statistics about the queues"""
        return {
            'priority_count': len(self.priority_queue),
            'regular_count': len(self.regular_queue),
            'total_count': len(self.priority_queue) + len(self.regular_queue)
        }
    
    def clear_queue(self, queue_type: str = 'all'):
        """
        Clear queues
        
        Args:
            queue_type: 'all', 'priority', or 'regular'
        """
        if queue_type in ['all', 'priority']:
            self.priority_queue.clear()
        if queue_type in ['all', 'regular']:
            self.regular_queue.clear()
        
        self._save_to_disk()
        print(f"🗑️ Cleared {queue_type} signal queue(s)")
    
    def is_empty(self) -> bool:
        """Check if all queues are empty"""
        return len(self.priority_queue) == 0 and len(self.regular_queue) == 0
