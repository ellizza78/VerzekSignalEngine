"""
Exchange Adapters for VerzekAutoTrader
Unified interface for multiple cryptocurrency exchanges
"""

from .binance_client import BinanceClient, BinanceDemoClient
from .bybit_client import BybitClient, BybitDemoClient
from .phemex_client import PhemexClient, PhemexDemoClient
from .coinexx_client import CoinexxClient, CoinexxDemoClient
from .exchange_interface import ExchangeFactory, ExchangeInterface

__all__ = [
    'BinanceClient',
    'BinanceDemoClient',
    'BybitClient',
    'BybitDemoClient',
    'PhemexClient',
    'PhemexDemoClient',
    'CoinexxClient',
    'CoinexxDemoClient',
    'ExchangeFactory',
    'ExchangeInterface'
]
