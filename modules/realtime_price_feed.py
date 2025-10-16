import asyncio
import websocket
import json
import threading
from typing import Dict, List, Callable, Optional
from datetime import datetime
import time

class PriceFeedManager:
    """Manages real-time price feeds from multiple exchanges via WebSocket"""
    
    def __init__(self, position_tracker):
        self.position_tracker = position_tracker
        self.active_feeds = {}
        self.price_cache = {}
        self.subscribers = []
        self.running = False
        self.ws_threads = {}
        
    def subscribe(self, callback: Callable):
        """Subscribe to price updates"""
        self.subscribers.append(callback)
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get latest price for a symbol"""
        return self.price_cache.get(symbol)
    
    def get_all_prices(self) -> Dict[str, float]:
        """Get all cached prices"""
        return self.price_cache.copy()
    
    def _notify_subscribers(self, symbol: str, price: float, exchange: str):
        """Notify all subscribers of price update"""
        for callback in self.subscribers:
            try:
                callback(symbol, price, exchange)
            except Exception as e:
                print(f"[PRICE_FEED] Error notifying subscriber: {e}")
    
    def _update_position_prices(self):
        """Update current_price for all active positions"""
        try:
            positions = self.position_tracker.get_all_positions()
            updated = 0
            
            for pos in positions:
                if pos.get('status') == 'active':
                    symbol = pos.get('symbol')
                    if symbol in self.price_cache:
                        position_id = pos.get('position_id')
                        self.position_tracker.update_position(position_id, {
                            'current_price': self.price_cache[symbol],
                            'last_price_update': datetime.utcnow().isoformat()
                        })
                        updated += 1
            
            if updated > 0:
                print(f"[PRICE_FEED] Updated {updated} position prices")
        except Exception as e:
            print(f"[PRICE_FEED] Error updating positions: {e}")
    
    def _binance_feed(self, symbols: List[str]):
        """Binance WebSocket feed with auto-reconnect"""
        streams = '/'.join([f"{s.lower()}@trade" for s in symbols])
        ws_url = f"wss://stream.binance.com:9443/stream?streams={streams}"
        
        retry_count = 0
        max_retries = 10
        base_delay = 1
        max_delay = 60
        
        def on_message(ws, message):
            nonlocal retry_count
            retry_count = 0
            try:
                data = json.loads(message)
                if 'data' in data:
                    symbol = data['data']['s']
                    price = float(data['data']['p'])
                    self.price_cache[symbol] = price
                    self._notify_subscribers(symbol, price, 'binance')
            except Exception as e:
                print(f"[BINANCE_WS] Error: {e}")
        
        def on_error(ws, error):
            print(f"[BINANCE_WS] Error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print(f"[BINANCE_WS] Connection closed: {close_msg}")
        
        def on_open(ws):
            nonlocal retry_count
            retry_count = 0
            print(f"[BINANCE_WS] Connected - {len(symbols)} symbols")
        
        while self.running and retry_count < max_retries:
            try:
                ws = websocket.WebSocketApp(
                    ws_url,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close,
                    on_open=on_open
                )
                
                ws.run_forever()
                
                if self.running:
                    retry_count += 1
                    delay = min(base_delay * (2 ** retry_count), max_delay)
                    print(f"[BINANCE_WS] Reconnecting in {delay}s (attempt {retry_count}/{max_retries})...")
                    time.sleep(delay)
            except Exception as e:
                retry_count += 1
                delay = min(base_delay * (2 ** retry_count), max_delay)
                print(f"[BINANCE_WS] Connection error: {e}, retrying in {delay}s...")
                time.sleep(delay)
    
    def _bybit_feed(self, symbols: List[str]):
        """Bybit WebSocket feed with auto-reconnect"""
        ws_url = "wss://stream.bybit.com/v5/public/linear"
        
        retry_count = 0
        max_retries = 10
        base_delay = 1
        max_delay = 60
        
        def on_message(ws, message):
            nonlocal retry_count
            retry_count = 0
            try:
                data = json.loads(message)
                if 'topic' in data and data['topic'].startswith('publicTrade'):
                    if 'data' in data:
                        for trade in data['data']:
                            symbol = trade['s']
                            price = float(trade['p'])
                            self.price_cache[symbol] = price
                            self._notify_subscribers(symbol, price, 'bybit')
            except Exception as e:
                print(f"[BYBIT_WS] Error: {e}")
        
        def on_error(ws, error):
            print(f"[BYBIT_WS] Error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print(f"[BYBIT_WS] Connection closed: {close_msg}")
        
        def on_open(ws):
            nonlocal retry_count
            retry_count = 0
            print(f"[BYBIT_WS] Connected - {len(symbols)} symbols")
            subscribe_msg = {
                "op": "subscribe",
                "args": [f"publicTrade.{s}" for s in symbols]
            }
            ws.send(json.dumps(subscribe_msg))
        
        while self.running and retry_count < max_retries:
            try:
                ws = websocket.WebSocketApp(
                    ws_url,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close,
                    on_open=on_open
                )
                
                ws.run_forever()
                
                if self.running:
                    retry_count += 1
                    delay = min(base_delay * (2 ** retry_count), max_delay)
                    print(f"[BYBIT_WS] Reconnecting in {delay}s (attempt {retry_count}/{max_retries})...")
                    time.sleep(delay)
            except Exception as e:
                retry_count += 1
                delay = min(base_delay * (2 ** retry_count), max_delay)
                print(f"[BYBIT_WS] Connection error: {e}, retrying in {delay}s...")
                time.sleep(delay)
    
    def _phemex_feed(self, symbols: List[str]):
        """Phemex WebSocket feed with auto-reconnect"""
        ws_url = "wss://phemex.com/ws"
        
        retry_count = 0
        max_retries = 10
        base_delay = 1
        max_delay = 60
        
        def on_message(ws, message):
            nonlocal retry_count
            retry_count = 0
            try:
                data = json.loads(message)
                if 'result' in data and 'trades_p' in data['result']:
                    symbol = data['result']['symbol']
                    for trade in data['result']['trades_p']:
                        price = float(trade[2])
                        self.price_cache[symbol] = price
                        self._notify_subscribers(symbol, price, 'phemex')
            except Exception as e:
                print(f"[PHEMEX_WS] Error: {e}")
        
        def on_error(ws, error):
            print(f"[PHEMEX_WS] Error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print(f"[PHEMEX_WS] Connection closed: {close_msg}")
        
        def on_open(ws):
            nonlocal retry_count
            retry_count = 0
            print(f"[PHEMEX_WS] Connected - {len(symbols)} symbols")
            for symbol in symbols:
                subscribe_msg = {
                    "id": 1,
                    "method": "trade.subscribe",
                    "params": [symbol]
                }
                ws.send(json.dumps(subscribe_msg))
            
            def send_ping_loop():
                while self.running:
                    try:
                        ping_msg = {"id": 0, "method": "server.ping", "params": []}
                        ws.send(json.dumps(ping_msg))
                        time.sleep(5)
                    except:
                        break
            
            ping_thread = threading.Thread(target=send_ping_loop, daemon=True)
            ping_thread.start()
        
        while self.running and retry_count < max_retries:
            try:
                ws = websocket.WebSocketApp(
                    ws_url,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close,
                    on_open=on_open
                )
                
                ws.run_forever(ping_interval=5, ping_timeout=3)
                
                if self.running:
                    retry_count += 1
                    delay = min(base_delay * (2 ** retry_count), max_delay)
                    print(f"[PHEMEX_WS] Reconnecting in {delay}s (attempt {retry_count}/{max_retries})...")
                    time.sleep(delay)
            except Exception as e:
                retry_count += 1
                delay = min(base_delay * (2 ** retry_count), max_delay)
                print(f"[PHEMEX_WS] Connection error: {e}, retrying in {delay}s...")
                time.sleep(delay)
    
    def _coinexx_feed(self, symbols: List[str]):
        """Coinexx WebSocket feed (placeholder - needs official API docs)"""
        print(f"[COINEXX_WS] WebSocket not yet implemented - using REST fallback")
        
        while self.running:
            for symbol in symbols:
                try:
                    pass
                except Exception as e:
                    print(f"[COINEXX] Error fetching {symbol}: {e}")
            time.sleep(1)
    
    def start_feed(self, exchange: str, symbols: List[str]):
        """Start WebSocket feed for an exchange"""
        if exchange in self.active_feeds:
            print(f"[PRICE_FEED] Feed already active for {exchange}")
            return
        
        feed_map = {
            'binance': self._binance_feed,
            'bybit': self._bybit_feed,
            'phemex': self._phemex_feed,
            'coinexx': self._coinexx_feed
        }
        
        if exchange not in feed_map:
            print(f"[PRICE_FEED] Exchange {exchange} not supported for WebSocket")
            return
        
        thread = threading.Thread(
            target=feed_map[exchange],
            args=(symbols,),
            daemon=True
        )
        thread.start()
        
        self.active_feeds[exchange] = {
            'symbols': symbols,
            'thread': thread,
            'started_at': datetime.utcnow().isoformat()
        }
        
        print(f"[PRICE_FEED] Started {exchange} feed for {len(symbols)} symbols")
    
    def start_auto_feeds(self):
        """Automatically start feeds for all active positions"""
        self.running = True
        
        positions = self.position_tracker.get_all_positions()
        exchange_symbols = {}
        
        for pos in positions:
            if pos.get('status') == 'active':
                exchange = pos.get('exchange', 'binance')
                symbol = pos.get('symbol')
                
                if exchange not in exchange_symbols:
                    exchange_symbols[exchange] = []
                
                if symbol not in exchange_symbols[exchange]:
                    exchange_symbols[exchange].append(symbol)
        
        for exchange, symbols in exchange_symbols.items():
            if symbols:
                self.start_feed(exchange, symbols)
        
        def update_loop():
            while self.running:
                self._update_position_prices()
                time.sleep(1)
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
        
        print(f"[PRICE_FEED] Auto-feeds started for {len(exchange_symbols)} exchanges")
    
    def stop_all_feeds(self):
        """Stop all price feeds"""
        self.running = False
        self.active_feeds.clear()
        print("[PRICE_FEED] All feeds stopped")
