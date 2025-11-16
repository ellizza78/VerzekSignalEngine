"""
Unified Market Data System using CCXT
Fetches real-time data from Binance Futures and Bybit
"""
import ccxt
import pandas as pd
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MarketDataFeed:
    """Unified market data provider for all strategy bots"""
    
    def __init__(self, exchange_name='binance', testnet=False):
        self.exchange_name = exchange_name
        self.testnet = testnet
        self.exchange = self._initialize_exchange()
        
    def _initialize_exchange(self):
        """Initialize CCXT exchange connection"""
        try:
            if self.exchange_name == 'binance':
                exchange = ccxt.binanceusdm({
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'future',
                    }
                })
            elif self.exchange_name == 'bybit':
                exchange = ccxt.bybit({
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'linear',
                    }
                })
            else:
                raise ValueError(f"Unsupported exchange: {self.exchange_name}")
            
            if self.testnet:
                exchange.set_sandbox_mode(True)
                
            exchange.load_markets()
            logger.info(f"✅ Connected to {self.exchange_name} {'testnet' if self.testnet else 'mainnet'}")
            return exchange
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.exchange_name}: {e}")
            raise
    
    def get_ohlcv(self, symbol: str, timeframe: str = '5m', limit: int = 200) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV candlestick data
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe ('1m', '5m', '15m', '1h', '4h')
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            logger.debug(f"📊 Fetched {len(df)} candles for {symbol} {timeframe}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error fetching OHLCV for {symbol}: {e}")
            return None
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """
        Get current ticker data (price, volume, change%)
        
        Returns:
            Dict with: last, bid, ask, volume, change_24h
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            
            return {
                'symbol': symbol,
                'last': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume_24h': ticker['quoteVolume'],
                'change_24h': ticker['percentage'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low'],
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching ticker for {symbol}: {e}")
            return None
    
    def get_orderbook(self, symbol: str, limit: int = 20) -> Optional[Dict]:
        """
        Get current order book (bid/ask depth)
        
        Returns:
            Dict with: bids, asks, spread
        """
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit=limit)
            
            best_bid = orderbook['bids'][0][0] if orderbook['bids'] else 0
            best_ask = orderbook['asks'][0][0] if orderbook['asks'] else 0
            spread = best_ask - best_bid
            
            return {
                'symbol': symbol,
                'bids': orderbook['bids'][:5],  # Top 5 bids
                'asks': orderbook['asks'][:5],  # Top 5 asks
                'best_bid': best_bid,
                'best_ask': best_ask,
                'spread': spread,
                'spread_pct': (spread / best_bid * 100) if best_bid > 0 else 0,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching orderbook for {symbol}: {e}")
            return None
    
    def get_funding_rate(self, symbol: str) -> Optional[float]:
        """Get current funding rate for futures"""
        try:
            if self.exchange_name == 'binance':
                funding = self.exchange.fetch_funding_rate(symbol)
                return funding['fundingRate']
            else:
                return None
        except Exception as e:
            logger.error(f"❌ Error fetching funding rate: {e}")
            return None
    
    def get_24h_stats(self, symbol: str) -> Optional[Dict]:
        """Get comprehensive 24h statistics"""
        ticker = self.get_ticker(symbol)
        if not ticker:
            return None
        
        return {
            'symbol': symbol,
            'price': ticker['last'],
            'volume_24h': ticker['volume_24h'],
            'change_24h_pct': ticker['change_24h'],
            'high_24h': ticker['high_24h'],
            'low_24h': ticker['low_24h'],
            'price_range_pct': ((ticker['high_24h'] - ticker['low_24h']) / ticker['low_24h'] * 100) if ticker['low_24h'] > 0 else 0
        }
    
    def get_multi_timeframe_data(self, symbol: str, timeframes: List[str] = ['5m', '15m', '1h']) -> Dict:
        """Fetch data from multiple timeframes simultaneously"""
        data = {}
        for tf in timeframes:
            df = self.get_ohlcv(symbol, tf, limit=100)
            if df is not None:
                data[tf] = df
        return data
    
    def close(self):
        """Close exchange connection"""
        try:
            self.exchange.close()
            logger.info(f"✅ Closed {self.exchange_name} connection")
        except:
            pass


# Singleton instance for shared use
_market_feed_instance = None

def get_market_feed(exchange='binance', testnet=False) -> MarketDataFeed:
    """Get or create singleton market feed instance"""
    global _market_feed_instance
    if _market_feed_instance is None:
        _market_feed_instance = MarketDataFeed(exchange, testnet)
    return _market_feed_instance
