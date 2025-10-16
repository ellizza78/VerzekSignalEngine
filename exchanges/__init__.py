"""
Exchange Adapters for VerzekAutoTrader
Unified interface for multiple cryptocurrency exchanges
"""

from .binance_client import BinanceClient, BinanceDemoClient

__all__ = [
    'BinanceClient',
    'BinanceDemoClient'
]
