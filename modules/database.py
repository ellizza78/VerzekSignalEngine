"""
SQLite Database Module for VerzekAutoTrader
--------------------------------------------
Thread-safe database with ACID compliance.
Replaces JSON file storage to prevent data corruption.
"""

import sqlite3
import json
import threading
from contextlib import contextmanager
from typing import Dict, List, Optional, Any
import os

DATABASE_PATH = "database/verzek.db"

# Thread-local storage for connections
_thread_local = threading.local()


class Database:
    """Thread-safe SQLite database with connection pooling"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(_thread_local, 'connection'):
            _thread_local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                isolation_level=None  # Autocommit off for manual transactions
            )
            _thread_local.connection.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrent performance
            _thread_local.connection.execute("PRAGMA journal_mode=WAL")
            _thread_local.connection.execute("PRAGMA synchronous=NORMAL")
        return _thread_local.connection
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions with automatic rollback"""
        conn = self._get_connection()
        try:
            conn.execute("BEGIN")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def _initialize_database(self):
        """Create database schema if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self.transaction() as conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email_verified INTEGER DEFAULT 0,
                    verification_token TEXT,
                    verification_expires INTEGER,
                    created_at INTEGER NOT NULL,
                    subscription_plan TEXT DEFAULT 'TRIAL',
                    subscription_expires INTEGER,
                    referral_code TEXT UNIQUE,
                    referred_by TEXT,
                    referral_earnings REAL DEFAULT 0.0,
                    total_profit REAL DEFAULT 0.0,
                    total_loss REAL DEFAULT 0.0,
                    win_rate REAL DEFAULT 0.0,
                    total_trades INTEGER DEFAULT 0,
                    data JSON
                )
            """)
            
            # Exchange accounts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS exchange_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    exchange TEXT NOT NULL,
                    encrypted_api_key TEXT NOT NULL,
                    encrypted_api_secret TEXT NOT NULL,
                    is_demo INTEGER DEFAULT 0,
                    created_at INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    UNIQUE(user_id, exchange, is_demo)
                )
            """)
            
            # Positions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    position_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    exchange TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    quantity REAL NOT NULL,
                    leverage INTEGER,
                    stop_loss REAL,
                    take_profit_levels JSON,
                    status TEXT DEFAULT 'OPEN',
                    pnl REAL DEFAULT 0.0,
                    created_at INTEGER NOT NULL,
                    closed_at INTEGER,
                    data JSON,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            # Licenses table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS licenses (
                    license_key TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    issued_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            # Payments table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    tx_hash TEXT UNIQUE NOT NULL,
                    amount REAL NOT NULL,
                    plan TEXT NOT NULL,
                    status TEXT DEFAULT 'PENDING',
                    created_at INTEGER NOT NULL,
                    confirmed_at INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            # Safety state table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS safety_state (
                    user_id TEXT PRIMARY KEY,
                    auto_stop_enabled INTEGER DEFAULT 1,
                    daily_loss_limit REAL,
                    current_daily_loss REAL DEFAULT 0.0,
                    max_positions INTEGER DEFAULT 5,
                    last_reset INTEGER,
                    data JSON,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_plan, subscription_expires)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_positions_user ON positions(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)")
    
    # User operations
    def create_user(self, user_id: str, username: str, email: str, password_hash: str, **kwargs) -> bool:
        """Create a new user"""
        with self.transaction() as conn:
            try:
                import time
                created_at = int(time.time())
                data = json.dumps(kwargs.get('data', {}))
                
                conn.execute("""
                    INSERT INTO users (user_id, username, email, password_hash, created_at, data)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, username, email, password_hash, created_at, data))
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        conn = self._get_connection()
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if row:
            user = dict(row)
            if user['data']:
                user['data'] = json.loads(user['data'])
            return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = self._get_connection()
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row:
            user = dict(row)
            if user['data']:
                user['data'] = json.loads(user['data'])
            return user
        return None
    
    def update_user(self, user_id: str, **updates) -> bool:
        """Update user fields"""
        if not updates:
            return False
        
        # Handle JSON data field
        if 'data' in updates:
            updates['data'] = json.dumps(updates['data'])
        
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [user_id]
        
        with self.transaction() as conn:
            conn.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
            return conn.execute("SELECT changes()").fetchone()[0] > 0
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        conn = self._get_connection()
        rows = conn.execute("SELECT * FROM users").fetchall()
        users = []
        for row in rows:
            user = dict(row)
            if user['data']:
                user['data'] = json.loads(user['data'])
            users.append(user)
        return users
    
    # Position operations
    def create_position(self, position_id: str, user_id: str, symbol: str, exchange: str, 
                       side: str, entry_price: float, quantity: float, **kwargs) -> bool:
        """Create a new position"""
        with self.transaction() as conn:
            import time
            created_at = int(time.time())
            data = json.dumps(kwargs.get('data', {}))
            tp_levels = json.dumps(kwargs.get('take_profit_levels', []))
            
            conn.execute("""
                INSERT INTO positions 
                (position_id, user_id, symbol, exchange, side, entry_price, quantity, 
                 leverage, stop_loss, take_profit_levels, status, created_at, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (position_id, user_id, symbol, exchange, side, entry_price, quantity,
                  kwargs.get('leverage'), kwargs.get('stop_loss'), tp_levels,
                  kwargs.get('status', 'OPEN'), created_at, data))
            return True
    
    def get_positions(self, user_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        """Get positions with optional filters"""
        conn = self._get_connection()
        query = "SELECT * FROM positions WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        if status:
            query += " AND status = ?"
            params.append(status)
        
        rows = conn.execute(query, params).fetchall()
        positions = []
        for row in rows:
            pos = dict(row)
            if pos['data']:
                pos['data'] = json.loads(pos['data'])
            if pos['take_profit_levels']:
                pos['take_profit_levels'] = json.loads(pos['take_profit_levels'])
            positions.append(pos)
        return positions
    
    def update_position(self, position_id: str, **updates) -> bool:
        """Update position fields"""
        if not updates:
            return False
        
        if 'data' in updates:
            updates['data'] = json.dumps(updates['data'])
        if 'take_profit_levels' in updates:
            updates['take_profit_levels'] = json.dumps(updates['take_profit_levels'])
        
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [position_id]
        
        with self.transaction() as conn:
            conn.execute(f"UPDATE positions SET {set_clause} WHERE position_id = ?", values)
            return True
    
    # License operations
    def create_license(self, license_key: str, user_id: str, plan: str, issued_at: int, expires_at: int) -> bool:
        """Create a new license"""
        with self.transaction() as conn:
            try:
                conn.execute("""
                    INSERT INTO licenses (license_key, user_id, plan, issued_at, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (license_key, user_id, plan, issued_at, expires_at))
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_license(self, license_key: str) -> Optional[Dict]:
        """Get license by key"""
        conn = self._get_connection()
        row = conn.execute("SELECT * FROM licenses WHERE license_key = ?", (license_key,)).fetchone()
        return dict(row) if row else None
    
    def get_user_licenses(self, user_id: str) -> List[Dict]:
        """Get all licenses for a user"""
        conn = self._get_connection()
        rows = conn.execute("SELECT * FROM licenses WHERE user_id = ? ORDER BY issued_at DESC", (user_id,)).fetchall()
        return [dict(row) for row in rows]


# Singleton instance
_db_instance = None

def get_database() -> Database:
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
