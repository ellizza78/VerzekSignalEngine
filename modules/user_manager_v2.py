"""
Multi-User Management System
Handles user profiles, exchange connections, risk settings, and DCA configurations
"""

import json
import os
from typing import Dict, Optional, List
from datetime import datetime


class User:
    """Represents a single user with all their settings"""
    
    def __init__(self, user_id: str, telegram_id: Optional[str] = None):
        self.user_id = user_id
        self.telegram_id = telegram_id
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        
        # User credentials (for mobile app authentication)
        self.email: str = ""
        self.full_name: str = ""
        self.password_hash: str = ""
        
        # Email verification (Option 3: CAPTCHA + Email Verification)
        self.email_verified: bool = False
        self.verification_token: str = ""
        self.verification_token_expires: str = ""
        
        # Password reset tokens
        self.password_reset_token: str = ""
        self.password_reset_expires: str = ""
        
        # Subscription security
        self.license_key: str = ""
        self.referral_code: str = ""
        self.referred_by: str = ""  # Referral code used during signup
        
        # Subscription plan
        self.plan = "free"  # free, pro, vip
        self.plan_started_at: Optional[str] = None
        self.plan_expires_at: Optional[str] = None
        self.telegram_group_access = {
            "trial_group": False,  # -1002726167386
            "vip_group": False,     # -1002721581400
            "locked_out": False
        }
        
        # Exchange accounts
        self.exchange_accounts: List[dict] = []
        
        # General Mode Settings
        self.general_settings = {
            "mode": "demo",  # demo or live
            "default_exchange": "bybit",  # binance, bybit, phemex, coinexx
            "api_mode": "demo",  # demo or live (enables actual trade execution)
            "logging_enabled": True
        }
        
        # Capital & Risk Control Settings
        self.risk_settings = {
            "risk_per_trade": 0.005,  # 0.5% of total capital per trade
            "default_position_size": 5.0,  # $5 USDT base amount
            "max_concurrent_trades": 50,  # 1-50 slider (updated limit)
            "max_daily_trades": 100,  # Daily cap for safety (increased)
            "leverage_cap": 25,  # Hard limit for futures leverage
            "cooldown_period": 300,  # 300 seconds pause between trades
            "max_daily_loss_percent": 5.0  # Legacy setting
        }
        
        # Daily tracking (reset daily)
        self.daily_stats = {
            "date": datetime.now().date().isoformat(),
            "trades_count": 0,
            "total_pnl": 0.0
        }
        
        # Strategy Parameters
        self.strategy_settings = {
            "auto_follow": True,  # Strictly follow signals as received
            "target_based_tp": True,  # Take profit at each target reached
            "auto_stop_on_signals": True,  # Auto-stop on cancelled/SL/closed messages
            "signal_quality_filter": True,  # Filter signals based on quality score
            "signal_quality_threshold": 60.0,  # Minimum quality score (0-100) to auto-trade
            "targets": {
                "enabled": True,
                "take_profit_on_each": True  # TP at Target 1, 2, 3, 4
            }
        }
        
        # DCA Margin Call Settings (VIP only)
        self.dca_settings = {
            "enabled": False,  # Only for VIP plan
            "base_order": 5.0,  # Use default_position_size from risk_settings
            "max_investment": 100.0,  # $100 max per symbol
            "tp_pct": 1.2,  # 1.2% take profit
            "tp_mode": "whole",  # whole or partial
            "partial_tp_schema": [30, 30, 40],  # % splits for partial TP
            "sl_pct": 3.0,  # 3% stop loss
            "trailing": {
                "enabled": False,
                "callback_pct": 0.5
            },
            "levels": [
                {"drop_pct": 1.5, "multiplier": 1.0},
                {"drop_pct": 2.0, "multiplier": 1.2},
                {"drop_pct": 3.0, "multiplier": 1.5}
            ],
            "cooldown_sec": 300  # 5 min cooldown after close
        }
        
        # Trading preferences
        self.trading_preferences = {
            "auto_trade_enabled": False,  # Only VIP gets auto-trading
            "default_exchange": "binance",
            "signal_sources": [],  # List of allowed signal source IDs
            "symbol_whitelist": [],  # Empty = all allowed
            "symbol_blacklist": [],
            "notification_enabled": True,
            "notify_on_entry": True,
            "notify_on_tp": True,
            "notify_on_sl": True,
            "notify_on_dca": True
        }
        
        # Statistics
        self.stats = {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_pnl": 0.0,
            "total_volume": 0.0,
            "active_positions": 0
        }
    
    def add_exchange_account(
        self,
        exchange: str,
        api_key_id: str,
        testnet: bool = False,
        enabled: bool = True
    ):
        """Add exchange account to user"""
        account = {
            "id": f"{exchange}_{api_key_id}",
            "exchange": exchange,
            "api_key_id": api_key_id,
            "testnet": testnet,
            "enabled": enabled,
            "added_at": datetime.now().isoformat()
        }
        self.exchange_accounts.append(account)
        self.updated_at = datetime.now().isoformat()
    
    def update_exchange_account(self, account_id: str, updates: dict):
        """Update an exchange account"""
        for account in self.exchange_accounts:
            if account.get("id") == account_id:
                account.update(updates)
                self.updated_at = datetime.now().isoformat()
                break
    
    def remove_exchange_account(self, account_id: str):
        """Remove an exchange account"""
        self.exchange_accounts = [
            acc for acc in self.exchange_accounts
            if acc.get("id") != account_id
        ]
        self.updated_at = datetime.now().isoformat()
    
    def enable_exchange_account(self, account_id: str, enabled: bool = True):
        """Enable or disable an exchange account"""
        for account in self.exchange_accounts:
            if account.get("id") == account_id:
                account["enabled"] = enabled
                self.updated_at = datetime.now().isoformat()
                break
    
    def _reset_daily_stats_if_needed(self):
        """Reset daily stats if it's a new day"""
        today = datetime.now().date().isoformat()
        if self.daily_stats.get("date") != today:
            self.daily_stats = {
                "date": today,
                "trades_count": 0,
                "total_pnl": 0.0
            }
    
    def update_risk_settings(self, settings: dict):
        """Update risk management settings"""
        self.risk_settings.update(settings)
        self.updated_at = datetime.now().isoformat()
    
    def update_dca_settings(self, settings: dict):
        """Update DCA settings"""
        self.dca_settings.update(settings)
        self.updated_at = datetime.now().isoformat()
    
    def update_trading_preferences(self, preferences: dict):
        """Update trading preferences"""
        self.trading_preferences.update(preferences)
        self.updated_at = datetime.now().isoformat()
    
    def update_stats(self, stat_updates: dict):
        """Update user statistics"""
        self.stats.update(stat_updates)
        self.updated_at = datetime.now().isoformat()
    
    def record_trade(self, pnl: float):
        """Record a completed trade"""
        self._reset_daily_stats_if_needed()
        self.daily_stats["trades_count"] += 1
        self.daily_stats["total_pnl"] += pnl
        self.updated_at = datetime.now().isoformat()
    
    def activate_subscription(self, plan: str, duration_days: int):
        """Activate subscription plan
        
        Args:
            plan: 'free', 'pro', or 'vip'
            duration_days: 3 for free, 30 for pro/vip
        """
        from datetime import timedelta
        
        # Store previous plan to handle downgrades
        previous_plan = self.plan
        
        self.plan = plan
        self.plan_started_at = datetime.now().isoformat()
        self.plan_expires_at = (datetime.now() + timedelta(days=duration_days)).isoformat()
        
        # Set group access and features based on plan
        if plan == "free":
            self.telegram_group_access["trial_group"] = True
            self.telegram_group_access["vip_group"] = False
            self.dca_settings["enabled"] = False  # Disable auto-trade
            self.strategy_settings["auto_follow"] = False  # Disable auto-trading
            self.trading_preferences["auto_trade_enabled"] = False  # Disable legacy flag
        elif plan == "pro":
            self.telegram_group_access["trial_group"] = False
            self.telegram_group_access["vip_group"] = True
            self.dca_settings["enabled"] = False  # Pro doesn't get auto-trade
            self.strategy_settings["auto_follow"] = False  # No auto-trading
            self.trading_preferences["auto_trade_enabled"] = False  # Disable legacy flag
        elif plan == "vip":
            self.telegram_group_access["trial_group"] = False
            self.telegram_group_access["vip_group"] = True
            self.dca_settings["enabled"] = True  # VIP gets auto-trade with DCA
            self.strategy_settings["auto_follow"] = True  # Enable auto-trading
            self.trading_preferences["auto_trade_enabled"] = True  # Enable legacy flag
        
        self.telegram_group_access["locked_out"] = False
        self.updated_at = datetime.now().isoformat()
    
    def is_subscription_expired(self) -> bool:
        """Check if subscription is expired"""
        if not self.plan_expires_at:
            return False
        
        from datetime import datetime as dt
        expiry_date = dt.fromisoformat(self.plan_expires_at)
        return datetime.now() > expiry_date
    
    def check_and_lock_expired_users(self):
        """Check if subscription expired and lock from groups"""
        if self.is_subscription_expired():
            # Lock group access
            self.telegram_group_access["trial_group"] = False
            self.telegram_group_access["vip_group"] = False
            self.telegram_group_access["locked_out"] = True
            
            # Disable VIP-only features (auto-trade, DCA)
            self.dca_settings["enabled"] = False
            self.strategy_settings["auto_follow"] = False
            self.trading_preferences["auto_trade_enabled"] = False
            
            # Revert to free plan
            self.plan = "free"
            
            self.updated_at = datetime.now().isoformat()
    
    def get_plan_features(self) -> dict:
        """Get features available for current plan"""
        features = {
            "free": {
                "duration_days": 3,
                "signal_forwarding": True,
                "group_access": "trial",
                "auto_trading": False,
                "max_exchanges": 0,
                "price": 0
            },
            "pro": {
                "duration_days": 30,
                "signal_forwarding": True,
                "group_access": "vip",
                "auto_trading": False,
                "max_exchanges": 0,
                "price": 50
            },
            "vip": {
                "duration_days": 30,
                "signal_forwarding": True,
                "group_access": "vip",
                "auto_trading": True,
                "max_exchanges": -1,  # Unlimited
                "price": 120
            }
        }
        return features.get(self.plan, features["free"])
    
    def update_general_settings(self, settings: dict):
        """Update general mode settings"""
        self.general_settings.update(settings)
        self.updated_at = datetime.now().isoformat()
    
    def update_strategy_settings(self, settings: dict):
        """Update strategy parameters"""
        self.strategy_settings.update(settings)
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (password_hash excluded for security)"""
        return {
            "user_id": self.user_id,
            "telegram_id": self.telegram_id,
            "email": self.email,
            "full_name": self.full_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "plan": self.plan,
            "plan_started_at": self.plan_started_at,
            "plan_expires_at": self.plan_expires_at,
            "telegram_group_access": self.telegram_group_access,
            "exchange_accounts": self.exchange_accounts,
            "general_settings": self.general_settings,
            "risk_settings": self.risk_settings,
            "strategy_settings": self.strategy_settings,
            "dca_settings": self.dca_settings,
            "trading_preferences": self.trading_preferences,
            "stats": self.stats,
            "daily_stats": self.daily_stats
        }
    
    def to_storage_dict(self) -> dict:
        """Convert user to dictionary for storage (includes password_hash)"""
        data = self.to_dict()
        data["password_hash"] = self.password_hash  # Include for storage
        data["email_verified"] = self.email_verified
        data["verification_token"] = self.verification_token
        data["verification_token_expires"] = self.verification_token_expires
        return data
    
    @staticmethod
    def from_dict(data: dict) -> 'User':
        """Create user from dictionary"""
        user = User(data["user_id"], data.get("telegram_id"))
        user.email = data.get("email", "")
        user.full_name = data.get("full_name", "")
        user.password_hash = data.get("password_hash", "")  # Load from storage but never expose via to_dict()
        user.email_verified = data.get("email_verified", False)
        user.verification_token = data.get("verification_token", "")
        user.verification_token_expires = data.get("verification_token_expires", "")
        user.created_at = data.get("created_at", user.created_at)
        user.updated_at = data.get("updated_at", user.updated_at)
        user.plan = data.get("plan", "free")
        user.plan_started_at = data.get("plan_started_at")
        user.plan_expires_at = data.get("plan_expires_at")
        user.telegram_group_access = data.get("telegram_group_access", user.telegram_group_access)
        user.exchange_accounts = data.get("exchange_accounts", [])
        user.general_settings = data.get("general_settings", user.general_settings)
        user.risk_settings = data.get("risk_settings", user.risk_settings)
        user.strategy_settings = data.get("strategy_settings", user.strategy_settings)
        user.dca_settings = data.get("dca_settings", user.dca_settings)
        user.trading_preferences = data.get("trading_preferences", user.trading_preferences)
        user.stats = data.get("stats", user.stats)
        user.daily_stats = data.get("daily_stats", user.daily_stats)
        return user


class UserManager:
    """Manages all users and their settings"""
    
    def __init__(self, storage_path: str = "database/users_v2.json"):
        self.storage_path = storage_path
        self.users: Dict[str, User] = {}
        self._load_users()
    
    def _load_users(self):
        """Load users from storage"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for user_id, user_data in data.items():
                        self.users[user_id] = User.from_dict(user_data)
            except Exception as e:
                print(f"Error loading users: {e}")
                self.users = {}
        else:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            self.users = {}
    
    def _save_users(self):
        """Save users to storage"""
        try:
            data = {user_id: user.to_storage_dict() for user_id, user in self.users.items()}
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def create_user(self, user_id: str, telegram_id: Optional[str] = None) -> User:
        """Create a new user"""
        if user_id in self.users:
            return self.users[user_id]
        
        user = User(user_id, telegram_id)
        self.users[user_id] = user
        self._save_users()
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_telegram(self, telegram_id: str) -> Optional[User]:
        """Get user by Telegram ID"""
        for user in self.users.values():
            if user.telegram_id == telegram_id:
                return user
        return None
    
    def update_user(self, user_id: str, updates: dict):
        """Update user settings"""
        user = self.users.get(user_id)
        if not user:
            return
        
        if "risk_settings" in updates:
            user.update_risk_settings(updates["risk_settings"])
        if "dca_settings" in updates:
            user.update_dca_settings(updates["dca_settings"])
        if "trading_preferences" in updates:
            user.update_trading_preferences(updates["trading_preferences"])
        if "plan" in updates:
            user.plan = updates["plan"]
        if "plan_expires_at" in updates:
            user.plan_expires_at = updates["plan_expires_at"]
        
        user.updated_at = datetime.now().isoformat()
        self._save_users()
    
    def delete_user(self, user_id: str):
        """Delete a user"""
        if user_id in self.users:
            del self.users[user_id]
            self._save_users()
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        return list(self.users.values())
    
    def get_users_by_plan(self, plan: str) -> List[User]:
        """Get users by subscription plan"""
        return [user for user in self.users.values() if user.plan == plan]
    
    def get_active_traders(self) -> List[User]:
        """Get users with auto-trading enabled"""
        return [
            user for user in self.users.values()
            if user.trading_preferences.get("auto_trade_enabled", False)
        ]
    
    def add_exchange_to_user(
        self,
        user_id: str,
        exchange: str,
        api_key_id: str,
        testnet: bool = False
    ):
        """Add exchange account to user"""
        user = self.users.get(user_id)
        if user:
            user.add_exchange_account(exchange, api_key_id, testnet)
            self._save_users()
    
    def get_user_exchanges(self, user_id: str) -> List[dict]:
        """Get user's exchange accounts"""
        user = self.users.get(user_id)
        if user:
            return user.exchange_accounts
        return []
    
    def is_symbol_allowed(self, user_id: str, symbol: str) -> bool:
        """Check if symbol is allowed for user"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        prefs = user.trading_preferences
        
        # Check blacklist first
        if symbol in prefs.get("symbol_blacklist", []):
            return False
        
        # If whitelist exists and not empty, symbol must be in it
        whitelist = prefs.get("symbol_whitelist", [])
        if whitelist:
            return symbol in whitelist
        
        # No restrictions
        return True
    
    def can_open_position(self, user_id: str) -> bool:
        """Check if user can open a new position"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        max_positions = user.risk_settings.get("max_concurrent_trades", 3)
        current_positions = user.stats.get("active_positions", 0)
        
        return current_positions < max_positions
    
    def get_position_size(self, user_id: str, account_balance: float) -> float:
        """Calculate position size for user"""
        user = self.users.get(user_id)
        if not user:
            return 0.0
        
        risk_settings = user.risk_settings
        mode = risk_settings.get("position_size_mode", "percentage")
        
        if mode == "percentage":
            risk_pct = risk_settings.get("risk_per_trade", 0.01)
            return account_balance * risk_pct
        else:
            # Fixed size mode with fallback
            return risk_settings.get("fixed_position_size", 10.0)
    
    def check_leverage_cap(self, user_id: str, requested_leverage: int) -> int:
        """Check and cap leverage to user's maximum"""
        user = self.users.get(user_id)
        if not user:
            return 1
        
        leverage_cap = user.risk_settings.get("leverage_cap", 10)
        return min(requested_leverage, leverage_cap)
    
    def can_trade_today(self, user_id: str, account_balance: Optional[float] = None) -> bool:
        """Check if user can trade today (within daily limits)
        
        Args:
            user_id: User ID
            account_balance: Current account balance (optional, for loss % calculation)
        """
        user = self.users.get(user_id)
        if not user:
            return False
        
        user._reset_daily_stats_if_needed()
        
        # Check daily trade count
        max_daily_trades = user.risk_settings.get("max_daily_trades", 20)
        if user.daily_stats.get("trades_count", 0) >= max_daily_trades:
            return False
        
        # Check daily loss limit
        max_daily_loss_pct = user.risk_settings.get("max_daily_loss_percent", 5.0)
        daily_pnl = user.daily_stats.get("total_pnl", 0.0)
        
        # If losses are negative, check against limit
        if daily_pnl < 0:
            if account_balance and account_balance > 0:
                # Calculate loss as percentage of account
                loss_pct = abs(daily_pnl) / account_balance * 100
                if loss_pct >= max_daily_loss_pct:
                    return False
            else:
                # Fallback: use absolute loss threshold if no balance provided
                # This prevents unlimited losses even without balance tracking
                absolute_loss_limit = 500.0  # $500 default absolute limit
                if abs(daily_pnl) >= absolute_loss_limit:
                    return False
        
        return True
    
    def record_trade_for_user(self, user_id: str, pnl: float):
        """Record a completed trade for a user"""
        user = self.users.get(user_id)
        if user:
            user.record_trade(pnl)
            
            # Update overall stats
            user.stats["total_trades"] += 1
            if pnl > 0:
                user.stats["winning_trades"] += 1
            else:
                user.stats["losing_trades"] += 1
            user.stats["total_pnl"] += pnl
            
            self._save_users()
    
    def update_exchange_account(self, user_id: str, account_id: str, updates: dict):
        """Update exchange account for a user"""
        user = self.users.get(user_id)
        if user:
            user.update_exchange_account(account_id, updates)
            self._save_users()
    
    def remove_exchange_account(self, user_id: str, account_id: str):
        """Remove exchange account from a user"""
        user = self.users.get(user_id)
        if user:
            user.remove_exchange_account(account_id)
            self._save_users()
    
    def enable_exchange_account(self, user_id: str, account_id: str, enabled: bool = True):
        """Enable or disable exchange account for a user"""
        user = self.users.get(user_id)
        if user:
            user.enable_exchange_account(account_id, enabled)
            self._save_users()
