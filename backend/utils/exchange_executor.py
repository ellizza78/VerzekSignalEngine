"""
Exchange Trade Executor - DRY-RUN Shell (Phase 2)
Validates user permissions and simulates trade execution
IMPORTANT: NO REAL TRADES - Mock execution only
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Tuple
from sqlalchemy.orm import Session
from models import User, UserSettings, ExchangeAccount
from exchanges.exchange_router import ExchangeRouter
from utils.security import decrypt_api_key
from utils.logger import api_logger


class ExchangeExecutor:
    """
    Trade executor shell for Phase 2 validation
    Validates permissions and API keys WITHOUT executing real trades
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_user_trading_permission(self, user: User) -> Tuple[bool, str]:
        """
        Validate user can execute trades
        
        Returns:
            (allowed, reason) tuple
        """
        # Check subscription tier
        if user.subscription_type.upper() != "PREMIUM":
            return (False, f"SUBSCRIPTION_TIER_INSUFFICIENT: User is {user.subscription_type}, requires PREMIUM")
        
        # Check auto-trading enabled
        if not user.auto_trade_enabled:
            return (False, "AUTO_TRADING_DISABLED: User has disabled auto-trading")
        
        # Check email verification
        if not user.is_verified:
            return (False, "EMAIL_NOT_VERIFIED: User must verify email before trading")
        
        return (True, "OK")
    
    def validate_user_has_exchange_keys(self, user_id: int, exchange_name: str) -> Tuple[bool, str, Dict]:
        """
        Validate user has API keys for exchange
        
        Returns:
            (has_keys, message, credentials_dict)
        """
        # Query exchange account
        exchange_account = self.db.query(ExchangeAccount).filter(
            ExchangeAccount.user_id == user_id,
            ExchangeAccount.exchange == exchange_name.lower(),
            ExchangeAccount.is_active == True
        ).first()
        
        if not exchange_account:
            return (False, f"NO_API_KEYS: User has not connected {exchange_name} account", {})
        
        # Decrypt API keys
        try:
            api_key = decrypt_api_key(exchange_account.api_key)
            api_secret = decrypt_api_key(exchange_account.api_secret)
            
            return (True, "API_KEYS_FOUND", {
                "api_key": api_key,
                "api_secret": api_secret,
                "testnet": exchange_account.testnet
            })
        except Exception as e:
            return (False, f"API_KEY_DECRYPTION_FAILED: {str(e)}", {})
    
    def validate_risk_settings(self, user_id: int) -> Tuple[bool, str, Dict]:
        """
        Validate user risk settings
        
        Returns:
            (valid, message, settings_dict)
        """
        settings = self.db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
        
        if not settings:
            return (False, "NO_SETTINGS: User settings not found", {})
        
        # Check required settings
        if settings.per_trade_usdt <= 0:
            return (False, "INVALID_TRADE_SIZE: per_trade_usdt must be > 0", {})
        
        if settings.leverage < 1 or settings.leverage > 125:
            return (False, f"INVALID_LEVERAGE: {settings.leverage} (must be 1-125)", {})
        
        if settings.max_concurrent_trades < 1 or settings.max_concurrent_trades > 50:
            return (False, f"INVALID_MAX_TRADES: {settings.max_concurrent_trades} (must be 1-50)", {})
        
        return (True, "RISK_SETTINGS_VALID", {
            "capital_usdt": settings.capital_usdt,
            "per_trade_usdt": settings.per_trade_usdt,
            "leverage": settings.leverage,
            "max_concurrent_trades": settings.max_concurrent_trades
        })
    
    def simulate_trade_execution(
        self,
        user: User,
        signal: Dict,
        exchange_name: str = "binance"
    ) -> Dict:
        """
        Simulate trade execution (DRY-RUN only)
        
        Args:
            user: User object
            signal: Signal data dict
            exchange_name: Exchange to use
        
        Returns:
            Simulation result dict
        """
        result = {
            "ok": False,
            "simulation": True,
            "phase": "Phase 2 - DRY-RUN",
            "errors": [],
            "warnings": [],
            "trade_placed": False
        }
        
        # Step 1: Validate subscription
        allowed, reason = self.validate_user_trading_permission(user)
        if not allowed:
            result["errors"].append(reason)
            api_logger.warning(f"Trade rejected for user {user.id}: {reason}")
            return result
        
        # Step 2: Validate exchange API keys
        has_keys, message, credentials = self.validate_user_has_exchange_keys(user.id, exchange_name)
        if not has_keys:
            result["errors"].append(message)
            api_logger.warning(f"API keys missing for user {user.id}: {message}")
            return result
        
        # Step 3: Validate risk settings
        valid_risk, risk_message, risk_settings = self.validate_risk_settings(user.id)
        if not valid_risk:
            result["errors"].append(risk_message)
            api_logger.warning(f"Invalid risk settings for user {user.id}: {risk_message}")
            return result
        
        # Step 4: Get exchange client
        client = ExchangeRouter.get_client(
            exchange_name,
            credentials["api_key"],
            credentials["api_secret"],
            credentials["testnet"]
        )
        
        if not client:
            result["errors"].append(f"EXCHANGE_NOT_SUPPORTED: {exchange_name}")
            return result
        
        # Step 5: Test connection (MOCK in Phase 2)
        success, connection_message = client.test_connection()
        if not success:
            result["errors"].append(f"CONNECTION_FAILED: {connection_message}")
            return result
        
        # Step 6: Simulate order placement (DRY-RUN)
        symbol = signal.get("symbol", "BTCUSDT")
        side = signal.get("side", "BUY")
        entry = signal.get("entry", 50000.0)
        size = risk_settings["per_trade_usdt"] / entry
        leverage = risk_settings["leverage"]
        
        order_result = client.place_market_order(
            symbol=symbol,
            side=side,
            size=size,
            leverage=leverage
        )
        
        # Step 7: Return simulation result
        result["ok"] = True
        result["trade_placed"] = False  # Still dry-run
        result["simulation_details"] = {
            "user_id": user.id,
            "exchange": exchange_name,
            "symbol": symbol,
            "side": side,
            "entry_price": entry,
            "size": size,
            "leverage": leverage,
            "order_response": order_result,
            "risk_settings": risk_settings
        }
        result["warnings"].append("Phase 2: DRY-RUN mode - No real order was placed")
        
        api_logger.info(f"✅ Dry-run simulation complete for user {user.id}: {symbol} {side}")
        
        return result


def test_exchange_executor():
    """Test the exchange executor with mock data"""
    from db import SessionLocal
    
    print("\n" + "="*70)
    print("Exchange Executor Test (Phase 2 - DRY-RUN)")
    print("="*70 + "\n")
    
    db = SessionLocal()
    
    try:
        # Get first PREMIUM user (if exists)
        user = db.query(User).filter(User.subscription_type == "PREMIUM").first()
        
        if not user:
            print("⚠️  No PREMIUM users found in database")
            print("Creating test scenario with mock user...")
            
            # Create mock user for testing
            from datetime import datetime
            user = User(
                id=99999,
                email="test_premium@test.com",
                subscription_type="PREMIUM",
                auto_trade_enabled=True,
                is_verified=True,
                created_at=datetime.utcnow()
            )
        
        executor = ExchangeExecutor(db)
        
        # Test validation
        allowed, reason = executor.validate_user_trading_permission(user)
        print(f"{'✅' if allowed else '❌'} Trading Permission: {reason}")
        
        # Simulate trade
        mock_signal = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "entry": 50000.0,
            "tp": [52000.0, 54000.0],
            "sl": 48000.0
        }
        
        result = executor.simulate_trade_execution(user, mock_signal, "binance")
        
        print(f"\n{'✅' if result['ok'] else '❌'} Simulation Result:")
        print(f"  Phase: {result['phase']}")
        print(f"  Trade Placed: {result['trade_placed']}")
        
        if result["errors"]:
            print(f"  Errors: {', '.join(result['errors'])}")
        
        if result["warnings"]:
            print(f"  Warnings: {', '.join(result['warnings'])}")
        
        if "simulation_details" in result:
            print(f"\n  Simulation Details:")
            details = result["simulation_details"]
            print(f"    Symbol: {details['symbol']}")
            print(f"    Side: {details['side']}")
            print(f"    Size: {details['size']:.6f}")
            print(f"    Leverage: {details['leverage']}x")
        
        print("\n" + "="*70)
        print("✅ Executor test complete - NO REAL TRADES PLACED")
        print("="*70 + "\n")
        
    finally:
        db.close()


if __name__ == "__main__":
    test_exchange_executor()
