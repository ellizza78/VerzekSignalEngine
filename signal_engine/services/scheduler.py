"""
Async Scheduler for Running Multiple Bots in Parallel
Uses asyncio and uvloop for high performance
"""
import asyncio
import uvloop
import logging
import json
from datetime import datetime
from typing import Dict, List
from ..bots.scalper.scalping_bot import ScalpingBot
from ..bots.trend.trend_bot import TrendBot
from ..bots.qfl.qfl_bot import QFLBot
from ..bots.ai_ml.ai_bot import AIBot
from .dispatcher import get_dispatcher
from .telegram_broadcaster import get_broadcaster

logger = logging.getLogger(__name__)


class BotScheduler:
    """Manages and schedules all trading bots"""
    
    def __init__(self, config_path='./config/engine_settings.json'):
        self.config = self._load_config(config_path)
        self.watchlist = self._load_watchlist()
        self.dispatcher = get_dispatcher()
        self.broadcaster = get_broadcaster()
        self.running = False
        
        # Initialize bots
        self.scalping_bot = ScalpingBot(self.config['bots']['scalping'])
        self.trend_bot = TrendBot(self.config['bots']['trend'])
        self.qfl_bot = QFLBot(self.config['bots']['qfl'])
        self.ai_bot = AIBot(self.config['bots']['ai_ml'])
        
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
    
    async def run_bot_cycle(self, bot, symbols: List[str], bot_name: str):
        """Run one cycle of a bot across all symbols"""
        for symbol in symbols:
            try:
                signal = await bot.analyze(symbol)
                
                if signal:
                    logger.info(f"🎯 {bot_name} generated signal for {symbol}")
                    
                    # Dispatch to backend API
                    await self.dispatcher.dispatch(signal.to_dict())
                    
                    # Broadcast to Telegram
                    telegram_message = signal.to_telegram_message()
                    await self.broadcaster.broadcast_signal(
                        telegram_message,
                        to_groups=['vip', 'trial', 'admin']
                    )
                    
            except Exception as e:
                logger.error(f"Error in {bot_name} for {symbol}: {e}")
    
    async def scalping_task(self):
        """Scalping bot runs every 15 seconds"""
        while self.running:
            try:
                symbols = self.watchlist.get('scalping_whitelist', ['BTC/USDT', 'ETH/USDT'])
                await self.run_bot_cycle(self.scalping_bot, symbols, 'Scalping Bot')
                await asyncio.sleep(15)  # 15 seconds
            except Exception as e:
                logger.error(f"Scalping task error: {e}")
                await asyncio.sleep(15)
    
    async def trend_task(self):
        """Trend bot runs every 5 minutes"""
        while self.running:
            try:
                symbols = self.watchlist.get('trend_whitelist', ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
                await self.run_bot_cycle(self.trend_bot, symbols, 'Trend Bot')
                await asyncio.sleep(300)  # 5 minutes
            except Exception as e:
                logger.error(f"Trend task error: {e}")
                await asyncio.sleep(300)
    
    async def qfl_task(self):
        """QFL bot runs every 20 seconds"""
        while self.running:
            try:
                symbols = self.watchlist.get('qfl_whitelist', ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'])
                await self.run_bot_cycle(self.qfl_bot, symbols, 'QFL Bot')
                await asyncio.sleep(20)  # 20 seconds
            except Exception as e:
                logger.error(f"QFL task error: {e}")
                await asyncio.sleep(20)
    
    async def ai_task(self):
        """AI bot runs every 30 seconds"""
        while self.running:
            try:
                symbols = self.watchlist.get('priority', ['BTC/USDT', 'ETH/USDT'])
                await self.run_bot_cycle(self.ai_bot, symbols, 'AI/ML Bot')
                await asyncio.sleep(30)  # 30 seconds
            except Exception as e:
                logger.error(f"AI task error: {e}")
                await asyncio.sleep(30)
    
    async def stats_task(self):
        """Print statistics every 5 minutes"""
        while self.running:
            try:
                await asyncio.sleep(300)  # 5 minutes
                
                dispatcher_stats = self.dispatcher.get_stats()
                broadcaster_stats = self.broadcaster.get_stats()
                
                logger.info("=" * 60)
                logger.info("📊 SIGNAL ENGINE STATISTICS")
                logger.info(f"Signals Sent: {dispatcher_stats['signals_sent']}")
                logger.info(f"Signals Failed: {dispatcher_stats['signals_failed']}")
                logger.info(f"Success Rate: {dispatcher_stats['success_rate']:.1f}%")
                logger.info(f"Telegram Messages: {broadcaster_stats['messages_sent']}")
                logger.info("=" * 60)
                
            except Exception as e:
                logger.error(f"Stats task error: {e}")
    
    async def start(self):
        """Start all bots in parallel"""
        self.running = True
        
        logger.info("🚀 Starting VerzekSignalEngine v1.0")
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
