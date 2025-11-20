"""
Global Safety Configuration
Controls live trading vs DRY-RUN mode across entire platform
"""
import os
from typing import Dict, Any


class SafetyConfig:
    """
    Global safety configuration for VerzekAutoTrader
    
    CRITICAL: This flag controls whether REAL TRADING is enabled
    - False = DRY-RUN mode (default, safe)
    - True = LIVE TRADING (requires explicit configuration)
    """
    
    # Global safety flag (defaults to False for safety)
    LIVE_TRADING_ENABLED = os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true"
    
    # Exchange mode (paper vs live)
    EXCHANGE_MODE = os.getenv("EXCHANGE_MODE", "paper")
    
    # Testnet vs Mainnet
    USE_TESTNET = os.getenv("USE_TESTNET", "true").lower() == "true"
    
    # Emergency kill switch
    EMERGENCY_STOP = os.getenv("EMERGENCY_STOP", "false").lower() == "true"
    
    @classmethod
    def is_safe_to_trade(cls) -> bool:
        """
        Check if it's safe to execute real trades
        
        Returns:
            True only if ALL safety checks pass
        """
        return (
            cls.LIVE_TRADING_ENABLED and
            not cls.EMERGENCY_STOP and
            cls.EXCHANGE_MODE == "live"
        )
    
    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """
        Get current safety status
        
        Returns:
            Dictionary with all safety flags and current mode
        """
        return {
            "live_trading_enabled": cls.LIVE_TRADING_ENABLED,
            "exchange_mode": cls.EXCHANGE_MODE,
            "use_testnet": cls.USE_TESTNET,
            "emergency_stop": cls.EMERGENCY_STOP,
            "safe_to_trade": cls.is_safe_to_trade(),
            "current_mode": "LIVE" if cls.is_safe_to_trade() else "DRY-RUN"
        }
    
    @classmethod
    def enforce_dry_run(cls) -> bool:
        """
        Should we enforce DRY-RUN mode?
        
        Returns:
            True if DRY-RUN should be enforced
        """
        return not cls.is_safe_to_trade()


# Convenience function for quick checks
def is_live_trading_enabled() -> bool:
    """Quick check if live trading is enabled"""
    return SafetyConfig.is_safe_to_trade()


def enforce_dry_run() -> bool:
    """Quick check if DRY-RUN should be enforced"""
    return SafetyConfig.enforce_dry_run()


def get_trading_mode() -> str:
    """Get current trading mode"""
    return SafetyConfig.get_status()["current_mode"]


# Print warning on import if live trading is enabled
if SafetyConfig.LIVE_TRADING_ENABLED:
    print("⚠️  WARNING: LIVE_TRADING_ENABLED is set to TRUE")
    print("⚠️  Real trading is potentially ACTIVE")
    if SafetyConfig.is_safe_to_trade():
        print("🔴 LIVE TRADING MODE - REAL MONEY AT RISK")
    else:
        print("🟡 Live trading enabled but other safety checks preventing execution")
else:
    print("🔒 DRY-RUN MODE - No real trading (safe)")
