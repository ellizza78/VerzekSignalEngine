"""
DCA Orchestrator
Integrates DCA engine with user management, safety rails, and exchange execution
"""

from typing import Optional, Dict
import hashlib
from modules import DCAEngine, PositionTracker, UserManager, SafetyManager, PositionSide
from exchanges import ExchangeFactory
from utils.logger import log_event
import trade_executor


class DCAOrchestrator:
    """Orchestrates DCA trading with all safety and management layers"""
    
    def __init__(self):
        self.user_manager = UserManager()
        self.safety_manager = SafetyManager()
        self.position_tracker = PositionTracker()
        self.dca_engines: Dict[str, DCAEngine] = {}  # user_id -> engine
        self.exchange_factory = ExchangeFactory()
        
        log_event("ORCHESTRATOR", "DCA Orchestrator initialized")
    
    def execute_signal(
        self,
        user_id: str,
        symbol: str,
        side: str,
        entry_price: Optional[float] = None,
        leverage: int = 10
    ) -> dict:
        """Execute a trading signal with full safety checks
        
        Args:
            user_id: User ID
            symbol: Trading symbol (e.g., BTCUSDT)
            side: LONG or SHORT
            entry_price: Entry price (optional, will use market if None)
            leverage: Leverage (will be capped to user's max)
        
        Returns:
            Execution result dictionary
        """
        # Step 1: Get user
        user = self.user_manager.get_user(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Step 2: Check if DCA is enabled for user
        if not user.dca_settings.get("enabled", False):
            return {"success": False, "error": "DCA not enabled for user"}
        
        # Step 3: Safety checks
        trading_allowed, reason = self.safety_manager.is_trading_allowed()
        if not trading_allowed:
            log_event("ORCHESTRATOR", f"Trading blocked: {reason}")
            return {"success": False, "error": f"Trading blocked: {reason}"}
        
        # Step 4: User-level safety checks
        if not self.user_manager.can_open_position(user_id):
            return {"success": False, "error": "Max concurrent positions reached"}
        
        # Get user's exchange account
        exchanges = user.exchange_accounts
        if not exchanges or not any(e.get("enabled", True) for e in exchanges):
            return {"success": False, "error": "No active exchange account"}
        
        active_exchange = next(e for e in exchanges if e.get("enabled", True))
        exchange_name = active_exchange["exchange"]
        testnet = active_exchange.get("testnet", False)
        
        # Get exchange client
        client = self.exchange_factory.get_client(exchange_name, testnet=testnet)
        if not client:
            return {"success": False, "error": f"Exchange {exchange_name} not supported"}
        
        # Step 5: Symbol validation
        is_valid, msg = self.safety_manager.validate_symbol(
            symbol,
            user.trading_preferences.get("symbol_whitelist"),
            user.trading_preferences.get("symbol_blacklist")
        )
        if not is_valid:
            return {"success": False, "error": msg}
        
        # Step 6: Leverage validation and capping
        leverage = self.user_manager.check_leverage_cap(user_id, leverage)
        is_valid, msg = self.safety_manager.validate_leverage(
            leverage,
            user.risk_settings.get("leverage_cap", 20)
        )
        if not is_valid:
            return {"success": False, "error": msg}
        
        # Step 7: Get account balance
        try:
            balance_data = client.get_account_balance()
            if isinstance(balance_data, dict):
                account_balance = balance_data.get("balance", 1000.0)
            else:
                account_balance = 1000.0  # Fallback
        except Exception as e:
            log_event("ORCHESTRATOR", f"Error fetching balance: {e}")
            account_balance = 1000.0
        
        # Step 8: Check daily trading limits
        can_trade = self.user_manager.can_trade_today(user_id, account_balance)
        if not can_trade:
            return {"success": False, "error": "Daily trading limits exceeded"}
        
        # Step 9: Get or create DCA engine for user
        if user_id not in self.dca_engines:
            self.dca_engines[user_id] = DCAEngine(
                user_id=user_id,
                config=user.dca_settings
            )
        
        engine = self.dca_engines[user_id]
        
        # Step 10: Get current price if not provided
        if entry_price is None:
            try:
                entry_price = client.get_ticker_price(symbol)
            except Exception as e:
                log_event("ORCHESTRATOR", f"Error fetching price for {symbol}: {e}")
                return {"success": False, "error": f"Cannot fetch price for {symbol}"}
        
        # Step 11: Calculate position size
        base_order_size = user.dca_settings.get("base_order", 10.0)
        is_valid, msg = self.safety_manager.validate_order_size(base_order_size)
        if not is_valid:
            return {"success": False, "error": msg}
        
        # Step 12: Open position with DCA
        position_side = PositionSide.LONG if side.upper() == "LONG" else PositionSide.SHORT
        
        try:
            position = engine.open_position(
                symbol=symbol,
                side=position_side,
                entry_price=entry_price,
                leverage=leverage
            )
            
            if not position:
                return {"success": False, "error": "Failed to create position"}
            
            # Step 13: Place base order via trade_executor (supports demo mode)
            order_result = self._place_order(
                client=client,
                symbol=symbol,
                side="buy" if position_side == PositionSide.LONG else "sell",
                quantity=base_order_size / entry_price,  # Convert USD to coins
                price=entry_price,
                leverage=leverage,
                user_id=user_id
            )
            
            if not order_result.get("success"):
                # Rollback position
                engine.close_position(symbol)
                return {"success": False, "error": "Failed to place order on exchange"}
            
            # Step 14: Track position
            self.position_tracker.save_position({
                "user_id": user_id,
                "symbol": symbol,
                "side": side,
                "entry_price": entry_price,
                "quantity": base_order_size / entry_price,
                "leverage": leverage,
                "status": "open",
                "dca_enabled": True
            })
            
            # Step 15: Update user stats
            user.stats["active_positions"] = user.stats.get("active_positions", 0) + 1
            self.user_manager._save_users()
            
            log_event("ORCHESTRATOR", f"✅ Position opened for {user_id}: {symbol} {side} @ {entry_price}")
            
            return {
                "success": True,
                "position_id": position.position_id,
                "symbol": symbol,
                "side": side,
                "entry_price": entry_price,
                "quantity": base_order_size / entry_price,
                "leverage": leverage,
                "exchange_order": order_result.get("order_id")
            }
            
        except Exception as e:
            log_event("ORCHESTRATOR", f"Error executing signal: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_idempotent_order_id(
        self,
        user_id: str,
        symbol: str,
        side: str,
        price: float,
        quantity: float
    ) -> str:
        """Generate stable order ID based on signal context for idempotency"""
        # Create hash from signal parameters (stable across retries)
        signal_data = f"{user_id}:{symbol}:{side}:{price:.2f}:{quantity:.6f}"
        order_hash = hashlib.md5(signal_data.encode()).hexdigest()[:12]
        return f"{symbol}_{order_hash}"
    
    def _place_order(
        self,
        client,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        leverage: int,
        user_id: str
    ) -> dict:
        """Place order via trade_executor for demo mode support"""
        try:
            # Generate idempotent order ID
            order_id = self._generate_idempotent_order_id(
                user_id, symbol, side, price, quantity
            )
            
            # Check idempotency (prevents duplicate orders)
            if not self.safety_manager.check_order_idempotency(order_id):
                log_event("ORCHESTRATOR", f"Duplicate order blocked: {order_id}")
                return {"success": False, "error": "Duplicate order detected"}
            
            # Use trade_executor for demo mode support
            # It falls back to simulation if no API keys
            trade_result = trade_executor.execute_trade(
                symbol=symbol,
                side=side,
                amount=quantity,
                tp=None,  # TP/SL managed by DCA engine
                sl=None
            )
            
            self.safety_manager.mark_order_placed(order_id)
            
            return {
                "success": True,
                "order_id": order_id,
                "result": trade_result,
                "mode": trade_result.get("mode", "simulation")
            }
        except Exception as e:
            log_event("ORCHESTRATOR", f"Order placement error: {e}")
            return {"success": False, "error": str(e)}
    
    def check_dca_triggers(self, user_id: str, symbol: str, current_price: float) -> dict:
        """Check if DCA margin call should be triggered
        
        Args:
            user_id: User ID
            symbol: Trading symbol
            current_price: Current market price
        
        Returns:
            DCA execution result
        """
        if user_id not in self.dca_engines:
            return {"success": False, "error": "No active engine for user"}
        
        engine = self.dca_engines[user_id]
        user = self.user_manager.get_user(user_id)
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Check if margin call needed
        result = engine.check_margin_call(symbol, current_price)
        
        if result.get("margin_call_needed"):
            level = result["level"]
            
            # Get exchange client
            exchanges = [e for e in user.exchange_accounts if e.get("enabled", True)]
            if not exchanges:
                return {"success": False, "error": "No active exchange"}
            
            exchange_name = exchanges[0]["exchange"]
            testnet = exchanges[0].get("testnet", False)
            client = self.exchange_factory.get_client(exchange_name, testnet=testnet)
            
            # Place DCA order
            position = engine.positions.get(symbol)
            if not position:
                return {"success": False, "error": "Position not found"}
            
            dca_quantity = level["order_size"] / current_price
            side = "buy" if position.side == PositionSide.LONG else "sell"
            
            order_result = self._place_order(
                client=client,
                symbol=symbol,
                side=side,
                quantity=dca_quantity,
                price=current_price,
                leverage=position.leverage,
                user_id=user_id
            )
            
            if order_result.get("success"):
                # Record DCA fill
                engine.add_dca_fill(symbol, current_price, level["order_size"])
                
                log_event("ORCHESTRATOR", f"🔄 DCA triggered for {user_id}: {symbol} level {level['level']} @ {current_price}")
                
                return {
                    "success": True,
                    "dca_level": level["level"],
                    "price": current_price,
                    "quantity": dca_quantity,
                    "order_id": order_result.get("order_id")
                }
        
        return {"success": False, "dca_not_needed": True}
    
    def close_position(
        self,
        user_id: str,
        symbol: str,
        exit_price: float,
        reason: str = "Manual close"
    ) -> dict:
        """Close a position and record results"""
        if user_id not in self.dca_engines:
            return {"success": False, "error": "No active engine for user"}
        
        engine = self.dca_engines[user_id]
        user = self.user_manager.get_user(user_id)
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Close position in engine
        close_result = engine.close_position(symbol, exit_price, reason)
        
        if close_result.get("success"):
            pnl = close_result["pnl"]
            
            # Record trade result for circuit breaker
            try:
                balance_data = user.exchange_accounts[0] if user.exchange_accounts else {}
                account_balance = 1000.0  # Fallback
                self.safety_manager.record_trade_result(pnl, user_id, account_balance)
            except:
                pass
            
            # Record for user
            self.user_manager.record_trade_for_user(user_id, pnl)
            
            # Update active positions count
            user.stats["active_positions"] = max(0, user.stats.get("active_positions", 1) - 1)
            self.user_manager._save_users()
            
            log_event("ORCHESTRATOR", f"🏁 Position closed for {user_id}: {symbol} PnL: ${pnl:.2f}")
            
            return close_result
        
        return {"success": False, "error": "Failed to close position"}
