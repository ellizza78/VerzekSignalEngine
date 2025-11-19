"""
Async Scheduler for Running Multiple Bots in Parallel
Uses asyncio and uvloop for high performance
Master Fusion Engine v2.0 - Intelligent Signal Filtering
"""
import asyncio
import uvloop
import logging
import json
from datetime import datetime
from typing import Dict, List
from bots.scalper.scalping_bot import ScalpingBot
from bots.trend.trend_bot import TrendBot
from bots.qfl.qfl_bot import QFLBot
from bots.ai_ml.ai_bot import AIBot
from services.dispatcher import get_dispatcher
from services.telegram_broadcaster import get_broadcaster
from services.tracker import get_tracker
from core.fusion_engine import FusionEngineBalanced

logger = logging.getLogger(__name__)


class BotScheduler:
    """Manages and schedules all trading bots"""
    
    def __init__(self, config_path='./config/engine_settings.json'):
        self.config = self._load_config(config_path)
        self.watchlist = self._load_watchlist()
        self.dispatcher = get_dispatcher()
        self.broadcaster = get_broadcaster()
        self.tracker = get_tracker()
        self.running = False
        
        # Initialize Master Fusion Engine v2.0
        self.fusion_engine = FusionEngineBalanced(self.config['master_engine'])
        
        # Initialize bots
        self.scalping_bot = ScalpingBot(self.config['bots']['scalping'])
        self.trend_bot = TrendBot(self.config['bots']['trend'])
        self.qfl_bot = QFLBot(self.config['bots']['qfl'])
        self.ai_bot = AIBot(self.config['bots']['ai_ml'])
        
        logger.info("✅ Master Fusion Engine v2.0 initialized")
        logger.info("✅ All bots initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load engine configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _load_watchlist(self) -> Dict:
        """Load symbol watchlist"""
        try:
            with open('./config/watchlist.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading watchlist: {e}")
            return {'futures': ['BTC/USDT', 'ETH/USDT'], 'priority': ['BTC/USDT']}
    
    def _get_default_config(self) -> Dict:
        """Default configuration fallback"""
        return {
            'bots': {
                'scalping': {'enabled': True, 'primary_timeframe': '5m', 'confidence_threshold': 70},
                'trend': {'enabled': True, 'primary_timeframe': '1h', 'confidence_threshold': 75},
                'qfl': {'enabled': True, 'primary_timeframe': '15m', 'confidence_threshold': 80},
                'ai_ml': {'enabled': True, 'confidence_threshold': 72}
            }
        }
    
    async def collect_candidates(self, bot, symbols: List[str], bot_name: str) -> List:
        """Collect signal candidates from a bot across all symbols"""
        candidates = []
        for symbol in symbols:
            try:
                candidate = await bot.analyze(symbol)
                if candidate:
                    candidates.append(candidate)
                    logger.debug(f"🔍 {bot_name} generated candidate for {symbol}")
            except Exception as e:
                logger.error(f"Error in {bot_name} for {symbol}: {e}")
        return candidates
    
    async def process_and_dispatch_signals(self, all_candidates: List):
        """Process candidates through Fusion Engine and dispatch approved signals"""
        if not all_candidates:
            return
        
        # Update trend bias from Trend Bot signals
        for candidate in all_candidates:
            if candidate.bot_source == "TREND":
                self.fusion_engine.update_trend_bias(candidate.symbol, candidate.side)
        
        # Process through Fusion Engine
        approved_signals = self.fusion_engine.process_candidates(all_candidates)
        
        if not approved_signals:
            logger.debug("🔒 No signals approved by Fusion Engine this cycle")
            return
        
        logger.info(f"✅ Fusion Engine approved {len(approved_signals)}/{len(all_candidates)} signals")
        
        # Dispatch approved signals
        for signal in approved_signals:
            try:
                logger.info(f"🎯 {signal.bot_source} signal approved: {signal.symbol} {signal.side}")
                
                # Track signal in database (CRITICAL - must happen before dispatch)
                track_success = self.tracker.open_signal(signal)
                if not track_success:
                    logger.error(f"⚠️  Failed to track signal {signal.signal_id[:8]}, skipping dispatch")
                    continue
                
                # Dispatch to backend API
                dispatch_success = await self.dispatcher.dispatch_candidate(signal)
                
                if not dispatch_success:
                    logger.error(f"⚠️  Failed to dispatch signal {signal.signal_id[:8]}")
                    # Signal is tracked but dispatch failed - will remain ACTIVE in DB
                    continue
                
                # Broadcast to Telegram
                telegram_message = signal.to_telegram_message()
                await self.broadcaster.broadcast_signal(
                    telegram_message,
                    to_groups=['vip', 'trial', 'admin']
                )
                
            except Exception as e:
                logger.error(f"Error processing signal {signal.signal_id}: {e}")
    
    async def scalping_task(self):
        """Scalping bot runs every 15 seconds"""
        while self.running:
            try:
                symbols = self.watchlist.get('scalping_whitelist', ['BTCUSDT', 'ETHUSDT'])
                candidates = await self.collect_candidates(self.scalping_bot, symbols, 'Scalping Bot')
                await self.process_and_dispatch_signals(candidates)
                await asyncio.sleep(15)  # 15 seconds
            except Exception as e:
                logger.error(f"Scalping task error: {e}")
                await asyncio.sleep(15)
    
    async def trend_task(self):
        """Trend bot runs every 5 minutes"""
        while self.running:
            try:
                symbols = self.watchlist.get('trend_whitelist', ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'])
                candidates = await self.collect_candidates(self.trend_bot, symbols, 'Trend Bot')
                await self.process_and_dispatch_signals(candidates)
                await asyncio.sleep(300)  # 5 minutes
            except Exception as e:
                logger.error(f"Trend task error: {e}")
                await asyncio.sleep(300)
    
    async def qfl_task(self):
        """QFL bot runs every 20 seconds"""
        while self.running:
            try:
                symbols = self.watchlist.get('qfl_whitelist', ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'])
                candidates = await self.collect_candidates(self.qfl_bot, symbols, 'QFL Bot')
                await self.process_and_dispatch_signals(candidates)
                await asyncio.sleep(20)  # 20 seconds
            except Exception as e:
                logger.error(f"QFL task error: {e}")
                await asyncio.sleep(20)
    
    async def ai_task(self):
        """AI bot runs every 30 seconds"""
        while self.running:
            try:
                symbols = self.watchlist.get('priority', ['BTCUSDT', 'ETHUSDT'])
                candidates = await self.collect_candidates(self.ai_bot, symbols, 'AI/ML Bot')
                await self.process_and_dispatch_signals(candidates)
                await asyncio.sleep(30)  # 30 seconds
            except Exception as e:
                logger.error(f"AI task error: {e}")
                await asyncio.sleep(30)
    
    async def reconciliation_task(self):
        """
        Polling backup mechanism: Auto-close signals that should be closed but webhook missed
        Runs immediately on startup, then every 30 minutes as safety net for missed webhooks
        """
        # Run immediately on startup (don't wait 30 minutes)
        first_run = True
        
        while self.running:
            try:
                if not first_run:
                    await asyncio.sleep(1800)  # 30 minutes
                first_run = False
                
                logger.info("🔄 Running reconciliation task (polling backup)...")
                
                # Get all active signals from tracker
                active_signals = self.tracker.get_active_signals()
                
                if not active_signals:
                    logger.debug("No active signals to reconcile")
                    continue
                
                # For each active signal, check if it's been active too long (>24 hours)
                # Auto-close these signals as they likely had webhook failures
                from datetime import datetime
                current_time = datetime.now()
                closed_count = 0
                
                for signal in active_signals:
                    opened_at = datetime.fromisoformat(signal['opened_at'])
                    hours_active = (current_time - opened_at).total_seconds() / 3600
                    
                    if hours_active > 24:
                        logger.warning(
                            f"⚠️  Stale signal detected: {signal['signal_id'][:8]} "
                            f"({signal['symbol']}) active for {hours_active:.1f} hours - AUTO-CLOSING"
                        )
                        
                        # Auto-close with entry price (break-even) and TIMEOUT reason
                        # This is conservative - assumes position was closed at entry if webhook missed
                        outcome = self.tracker.close_signal(
                            signal_id=signal['signal_id'],
                            exit_price=signal['entry_price'],  # Break-even assumption
                            close_reason='TIMEOUT'
                        )
                        
                        if outcome:
                            closed_count += 1
                            logger.info(
                                f"✅ Auto-closed stale signal: {signal['signal_id'][:8]} "
                                f"({signal['symbol']}) at break-even (${signal['entry_price']})"
                            )
                        else:
                            logger.error(
                                f"❌ Failed to auto-close signal: {signal['signal_id'][:8]}"
                            )
                
                if closed_count > 0:
                    logger.warning(
                        f"🚨 RECONCILIATION: Auto-closed {closed_count} stale signals "
                        f"(active >24h). These had missed webhooks."
                    )
                else:
                    logger.info("✅ Reconciliation complete: No stale signals found")
                    
            except Exception as e:
                logger.error(f"Reconciliation task error: {e}")
    
    async def stats_task(self):
        """Print statistics every 5 minutes"""
        while self.running:
            try:
                await asyncio.sleep(300)  # 5 minutes
                
                dispatcher_stats = self.dispatcher.get_stats()
                broadcaster_stats = self.broadcaster.get_stats()
                fusion_stats = self.fusion_engine.get_stats()
                active_signals = self.tracker.get_active_signals()
                
                logger.info("=" * 60)
                logger.info("📊 SIGNAL ENGINE STATISTICS (Fusion Engine v2.0)")
                logger.info(f"Signals Sent: {dispatcher_stats['signals_sent']}")
                logger.info(f"Signals Failed: {dispatcher_stats['signals_failed']}")
                logger.info(f"Success Rate: {dispatcher_stats['success_rate']:.1f}%")
                logger.info(f"Telegram Messages: {broadcaster_stats['messages_sent']}")
                logger.info("-" * 60)
                logger.info("🔥 FUSION ENGINE STATISTICS")
                logger.info(f"Total Candidates: {fusion_stats['total_candidates']}")
                logger.info(f"Approved Signals: {fusion_stats['approved']}")
                logger.info(f"Approval Rate: {fusion_stats['approval_rate']:.1f}%")
                logger.info(f"Rejected (Confidence): {fusion_stats['rejected_confidence']}")
                logger.info(f"Rejected (Cooldown): {fusion_stats['rejected_cooldown']}")
                logger.info(f"Rejected (Trend Bias): {fusion_stats['rejected_trend']}")
                logger.info(f"Rejected (Opposite Signal): {fusion_stats['rejected_opposite']}")
                logger.info(f"Rejected (Rate Limit): {fusion_stats['rejected_rate_limit']}")
                logger.info(f"Active Signals (Fusion): {fusion_stats['active_signals']}")
                logger.info("-" * 60)
                logger.info("📈 SIGNAL TRACKER STATISTICS")
                logger.info(f"Active Signals (Tracked): {len(active_signals)}")
                logger.info("=" * 60)
                
            except Exception as e:
                logger.error(f"Stats task error: {e}")
    
    async def start(self):
        """Start all bots in parallel"""
        self.running = True
        
        logger.info("🚀 Starting VerzekSignalEngine v2.0 - Master Fusion Engine")
        logger.info("=" * 60)
        
        # Send startup notification
        await self.broadcaster.send_startup_notification()
        
        # Create tasks for each bot
        tasks = []
        
        if self.config['bots']['scalping'].get('enabled', True):
            tasks.append(asyncio.create_task(self.scalping_task()))
            logger.info("✅ Scalping Bot started (15s interval)")
        
        if self.config['bots']['trend'].get('enabled', True):
            tasks.append(asyncio.create_task(self.trend_task()))
            logger.info("✅ Trend Bot started (5m interval)")
        
        if self.config['bots']['qfl'].get('enabled', True):
            tasks.append(asyncio.create_task(self.qfl_task()))
            logger.info("✅ QFL Bot started (20s interval)")
        
        if self.config['bots']['ai_ml'].get('enabled', True):
            tasks.append(asyncio.create_task(self.ai_task()))
            logger.info("✅ AI/ML Bot started (30s interval)")
        
        # Add stats task
        tasks.append(asyncio.create_task(self.stats_task()))
        
        # Add reconciliation task (polling backup)
        tasks.append(asyncio.create_task(self.reconciliation_task()))
        logger.info("✅ Reconciliation task started (30m interval)")
        
        logger.info("=" * 60)
        logger.info("🔥 All bots running. Press Ctrl+C to stop.")
        
        # Run all tasks concurrently
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("\n⚠️ Shutdown signal received")
            self.running = False
            
            # Cancel all tasks
            for task in tasks:
                task.cancel()
            
            logger.info("✅ VerzekSignalEngine stopped gracefully")


def run_signal_engine():
    """Main entry point for signal engine"""
    # Use uvloop for better performance
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    scheduler = BotScheduler()
    asyncio.run(scheduler.start())
