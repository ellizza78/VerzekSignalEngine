"""
Exchange Router
Routes exchange operations to the correct exchange client
IMPORTANT: Phase 2 - All exchanges return MOCK responses (NO REAL TRADING)
"""
from typing import Optional
from .base_exchange import BaseExchange
from .binance import BinanceClient
from .bybit import BybitClient
from .phemex import PhemexClient
from .kraken import KrakenClient


class ExchangeRouter:
    """
    Unified router for exchange operations
    Selects and initializes the correct exchange client
    """
    
    SUPPORTED_EXCHANGES = ["binance", "bybit", "phemex", "kraken"]
    
    @staticmethod
    def get_client(
        exchange_name: str,
        api_key: str,
        api_secret: str,
        testnet: bool = True
    ) -> Optional[BaseExchange]:
        """
        Get exchange client instance
        
        Args:
            exchange_name: Exchange name (binance, bybit, phemex, kraken)
            api_key: API key
            api_secret: API secret
            testnet: Use testnet (True) or live (False)
        
        Returns:
            Exchange client instance or None
        """
        exchange_name = exchange_name.lower().strip()
        
        if exchange_name == "binance":
            return BinanceClient(api_key, api_secret, testnet)
        elif exchange_name == "bybit":
            return BybitClient(api_key, api_secret, testnet)
        elif exchange_name == "phemex":
            return PhemexClient(api_key, api_secret, testnet)
        elif exchange_name == "kraken":
            return KrakenClient(api_key, api_secret, testnet)
        else:
            return None
    
    @staticmethod
    def test_all_exchanges():
        """
        Test all exchange clients with mock credentials
        Used for Phase 2 validation
        
        Returns:
            dict with test results for each exchange
        """
        results = {}
        
        for exchange in ExchangeRouter.SUPPORTED_EXCHANGES:
            try:
                client = ExchangeRouter.get_client(
                    exchange,
                    api_key="test_key_12345",
                    api_secret="test_secret_67890",
                    testnet=True
                )
                
                if client:
                    success, message = client.test_connection()
                    results[exchange] = {
                        "ok": success,
                        "message": message,
                        "exchange_name": client.exchange_name
                    }
                else:
                    results[exchange] = {
                        "ok": False,
                        "message": "Failed to initialize client"
                    }
            except Exception as e:
                results[exchange] = {
                    "ok": False,
                    "message": f"Error: {str(e)}"
                }
        
        return results
    
    @staticmethod
    def is_supported(exchange_name: str) -> bool:
        """Check if exchange is supported"""
        return exchange_name.lower() in ExchangeRouter.SUPPORTED_EXCHANGES


# Convenience function for testing
def test_exchange_router():
    """Test the exchange router"""
    print("\n" + "="*70)
    print("Exchange Router Test (Phase 2 - Mock Responses Only)")
    print("="*70 + "\n")
    
    results = ExchangeRouter.test_all_exchanges()
    
    for exchange, result in results.items():
        status = "✅" if result["ok"] else "❌"
        print(f"{status} {exchange.upper()}: {result['message']}")
    
    print("\n" + "="*70)
    print(f"✅ {sum(1 for r in results.values() if r['ok'])}/{len(results)} exchanges ready")
    print("="*70 + "\n")
    
    return results


if __name__ == "__main__":
    test_exchange_router()
