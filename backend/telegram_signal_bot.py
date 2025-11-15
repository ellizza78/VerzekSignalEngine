#!/usr/bin/env python3
"""
Telegram Signal Bridge Bot - Phase 4
Listens to group messages, parses signals, forwards to backend for autotrading
Uses python-telegram-bot library (bot API only, no personal account)
"""
import os
import sys
import re
import json
from datetime import datetime
from typing import Optional, Dict, List

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    print("⚠️  python-telegram-bot not installed")
    sys.exit(1)

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Import safety config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from config.safety import SafetyConfig, get_trading_mode
except ImportError:
    logger.warning("Safety config not found, defaulting to DRY-RUN mode")
    class SafetyConfig:
        @staticmethod
        def enforce_dry_run():
            return True
    
    def get_trading_mode():
        return "DRY-RUN"


class SignalParser:
    """Parse trading signals from Telegram messages"""
    
    # Supported crypto symbols
    SUPPORTED_SYMBOLS = [
        'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'MATIC', 
        'LINK', 'UNI', 'AVAX', 'ATOM', 'DOT', 'LTC', 'BCH', 'FTM',
        'NEAR', 'ALGO', 'SAND', 'MANA', 'AXS', 'GALA', 'ENJ'
    ]
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Remove emojis and extra whitespace from text"""
        # Remove common emojis and special chars
        text = re.sub(r'[🚀📈📉💰🔥⚡️✅❌🎯📊💎🌙🐂🐻]', '', text)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def parse_signal(text: str) -> Optional[Dict]:
        """
        Parse trading signal from message text
        
        Supported formats:
        - "BUY BTCUSDT @ 50000"
        - "SELL ETHUSDT entry: 3000, sl: 2900, tp: 3100"
        - "#LONG #BTCUSDT Entry: 50000 SL: 48000 TP: 52000"
        - "🚀 LONG BTC Entry 50000 TP1: 51000 TP2: 52000 SL: 48000"
        
        Returns:
            Signal dict or None if not a valid signal
        """
        if not text:
            return None
        
        original_text = text
        text = SignalParser.clean_text(text).upper()
        
        # Must contain a signal type keyword
        signal_keywords = ['BUY', 'SELL', 'LONG', 'SHORT', 'CLOSE', 'UPDATE']
        if not any(keyword in text for keyword in signal_keywords):
            return None
        
        # Detect signal type
        signal_type = None
        if any(word in text for word in ['BUY', 'LONG', '#BUY', '#LONG']):
            signal_type = "BUY"
        elif any(word in text for word in ['SELL', 'SHORT', '#SELL', '#SHORT']):
            signal_type = "SELL"
        elif 'CLOSE' in text:
            signal_type = "CLOSE"
        elif 'UPDATE' in text:
            signal_type = "UPDATE"
        
        if not signal_type:
            return None
        
        # Extract symbol
        symbol = None
        for sym in SignalParser.SUPPORTED_SYMBOLS:
            pattern = f'#{sym}|{sym}USDT|{sym}/USDT|{sym} '
            if re.search(pattern, text):
                symbol = f"{sym}USDT"
                break
        
        if not symbol:
            return None
        
        # Extract entry price
        entry = None
        entry_patterns = [
            r'ENTRY[:\s]+(\d+\.?\d*)',
            r'@\s*(\d+\.?\d*)',
            r'PRICE[:\s]+(\d+\.?\d*)',
            r'ENTER[:\s]+(\d+\.?\d*)'
        ]
        for pattern in entry_patterns:
            match = re.search(pattern, text)
            if match:
                entry = float(match.group(1))
                break
        
        # Extract stop loss
        sl = None
        sl_patterns = [
            r'SL[:\s]+(\d+\.?\d*)',
            r'STOP[\s]?LOSS[:\s]+(\d+\.?\d*)',
            r'STOPLOSS[:\s]+(\d+\.?\d*)'
        ]
        for pattern in sl_patterns:
            match = re.search(pattern, text)
            if match:
                sl = float(match.group(1))
                break
        
        # Extract take profit targets
        tp_targets = []
        # Try TP1, TP2, TP3 format
        for i in range(1, 4):
            match = re.search(rf'TP{i}[:\s]+(\d+\.?\d*)', text)
            if match:
                tp_targets.append(float(match.group(1)))
        
        # If no TP1/TP2/TP3, try general TP format
        if not tp_targets:
            tp_matches = re.findall(r'TP[:\s]+(\d+\.?\d*)', text)
            if tp_matches:
                tp_targets = [float(tp) for tp in tp_matches]
        
        # Extract leverage
        leverage = 1
        lev_match = re.search(r'(\d+)X|LEVERAGE[:\s]+(\d+)', text)
        if lev_match:
            leverage = int(lev_match.group(1) or lev_match.group(2))
        
        # Build signal object
        signal = {
            "type": signal_type,
            "symbol": symbol,
            "entry": entry,
            "sl": sl,
            "tp": tp_targets if tp_targets else None,
            "leverage": leverage,
            "raw_text": original_text[:500],
            "source": "telegram_bot",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return signal


class SignalBridgeBot:
    """
    Telegram Signal Bridge Bot
    Listens to configured groups, parses signals, forwards to backend
    """
    
    def __init__(self):
        """Initialize bot with configuration"""
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.admin_chat_id = os.getenv("ADMIN_CHAT_ID")
        
        # Group IDs (where bot listens for signals)
        self.trial_group_id = os.getenv("TELEGRAM_TRIAL_GROUP_ID")
        self.vip_group_id = os.getenv("TELEGRAM_VIP_GROUP_ID")
        self.debug_group_id = os.getenv("TELEGRAM_ADMIN_DEBUG_GROUP_ID")
        
        # Authorized signal sources
        authorized_bots = os.getenv("AUTHORIZED_SIGNAL_BOT_USERNAMES", "")
        self.authorized_bot_usernames = [b.strip() for b in authorized_bots.split(',') if b.strip()]
        
        authorized_users = os.getenv("AUTHORIZED_ADMIN_USER_IDS", "572038606")
        self.authorized_user_ids = [int(u.strip()) for u in authorized_users.split(',') if u.strip().isdigit()]
        
        # Backend API for forwarding signals
        self.backend_api = os.getenv("API_BASE_URL", "https://api.verzekinnovative.com")
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN required")
        
        # Create directories
        os.makedirs("telegram_signals", exist_ok=True)
        os.makedirs("telegram_sessions", exist_ok=True)
        
        # Initialize bot application
        self.application = Application.builder().token(self.bot_token).build()
        self.setup_handlers()
    
    def is_authorized_sender(self, message) -> bool:
        """Check if message sender is authorized"""
        # Check if from authorized bot
        if message.from_user.is_bot and message.from_user.username in self.authorized_bot_usernames:
            return True
        
        # Check if from authorized admin user
        if message.from_user.id in self.authorized_user_ids:
            return True
        
        return False
    
    def is_authorized_group(self, chat_id: int) -> bool:
        """Check if message is from authorized group"""
        authorized_groups = []
        
        if self.trial_group_id:
            try:
                authorized_groups.append(int(self.trial_group_id))
            except ValueError:
                pass
        
        if self.vip_group_id:
            try:
                authorized_groups.append(int(self.vip_group_id))
            except ValueError:
                pass
        
        if self.debug_group_id:
            try:
                authorized_groups.append(int(self.debug_group_id))
            except ValueError:
                pass
        
        return chat_id in authorized_groups
    
    def setup_handlers(self):
        """Setup message handlers"""
        # Commands (work in private chat and groups)
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("status", self.handle_status))
        self.application.add_handler(CommandHandler("help", self.handle_help))
        
        # Group messages (signal parsing)
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
                self.handle_group_message
            )
        )
        
        # Private messages (direct signals from admin)
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
                self.handle_private_message
            )
        )
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "✅ VerzekAutoTrader Signal Bridge Bot\n\n"
            "I listen to group messages and forward valid trading signals to the backend.\n\n"
            "Supported formats:\n"
            "• BUY BTCUSDT @ 50000\n"
            "• SELL ETHUSDT entry: 3000, sl: 2900, tp: 3100\n"
            "• #LONG #BTCUSDT Entry: 50000 SL: 48000 TP: 52000\n\n"
            f"Current Mode: {get_trading_mode() if 'get_trading_mode' in globals() else 'DRY-RUN'}"
        )
    
    async def handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        trading_mode = get_trading_mode() if 'get_trading_mode' in globals() else 'DRY-RUN'
        dry_run = SafetyConfig.enforce_dry_run() if hasattr(SafetyConfig, 'enforce_dry_run') else True
        
        status_text = (
            "🟢 Bot Status: ACTIVE\n"
            f"📡 Trading Mode: {trading_mode}\n"
            f"🔒 DRY-RUN: {'Yes' if dry_run else 'No'}\n"
            f"👥 Monitoring Groups: {len([g for g in [self.trial_group_id, self.vip_group_id, self.debug_group_id] if g])}\n"
            f"🤖 Authorized Bots: {len(self.authorized_bot_usernames)}\n"
            f"👤 Authorized Users: {len(self.authorized_user_ids)}"
        )
        
        await update.message.reply_text(status_text)
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "📚 VerzekAutoTrader Signal Bridge Bot Help\n\n"
            "Commands:\n"
            "/start - Welcome message\n"
            "/status - Check bot status\n"
            "/help - This help message\n\n"
            "Configuration:\n"
            "• Add bot to your signal groups\n"
            "• Configure group IDs in environment\n"
            "• Whitelist authorized signal sources\n\n"
            "The bot will automatically parse and forward valid signals to the backend."
        )
        
        await update.message.reply_text(help_text)
    
    async def handle_group_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages in groups"""
        try:
            message = update.message
            chat_id = message.chat_id
            
            # Check if group is authorized
            if not self.is_authorized_group(chat_id):
                logger.debug(f"Ignoring message from unauthorized group: {chat_id}")
                return
            
            # Check if sender is authorized
            if not self.is_authorized_sender(message):
                logger.debug(f"Ignoring message from unauthorized sender: {message.from_user.username}")
                return
            
            # Parse signal
            signal = SignalParser.parse_signal(message.text)
            
            if not signal:
                logger.debug("Message did not contain a valid signal")
                return
            
            # Add metadata
            signal["group_id"] = chat_id
            signal["sender_username"] = message.from_user.username
            signal["sender_id"] = message.from_user.id
            signal["is_bot"] = message.from_user.is_bot
            
            logger.info(f"📨 Signal detected: {signal['symbol']} {signal['type']} from {message.from_user.username}")
            
            # Save signal to file
            await self.save_signal_to_file(signal)
            
            # Forward to backend (Phase 4 - when backend signal ingestion is ready)
            # await self.forward_signal_to_backend(signal)
            
            # Optional: React to message to confirm receipt
            try:
                await message.add_reaction("✅")
            except:
                pass  # Reactions might not be available
                
        except Exception as e:
            logger.error(f"Error handling group message: {str(e)}")
    
    async def handle_private_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle private messages (admin testing)"""
        try:
            message = update.message
            
            # Only allow from authorized admin users
            if message.from_user.id not in self.authorized_user_ids:
                await message.reply_text("⚠️ Unauthorized. This bot only responds to authorized users.")
                return
            
            # Parse signal
            signal = SignalParser.parse_signal(message.text)
            
            if not signal:
                await message.reply_text("⚠️ Could not parse signal. Please check format.")
                return
            
            logger.info(f"📨 Private signal: {signal['symbol']} {signal['type']}")
            
            # Confirm to sender
            confirm_text = (
                f"✅ Signal Parsed:\n"
                f"• Symbol: {signal['symbol']}\n"
                f"• Type: {signal['type']}\n"
                f"• Entry: {signal['entry']}\n"
                f"• SL: {signal['sl']}\n"
                f"• TP: {signal['tp']}\n"
                f"• Leverage: {signal['leverage']}x\n\n"
                f"Mode: {get_trading_mode() if 'get_trading_mode' in globals() else 'DRY-RUN'}"
            )
            await message.reply_text(confirm_text)
            
            # Save signal
            await self.save_signal_to_file(signal)
            
        except Exception as e:
            logger.error(f"Error handling private message: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def save_signal_to_file(self, signal: Dict):
        """Save signal to file for audit and processing"""
        filename = f"telegram_signals/signal_{int(datetime.utcnow().timestamp())}.json"
        
        with open(filename, 'w') as f:
            json.dump(signal, f, indent=2)
        
        logger.info(f"💾 Signal saved to {filename}")
    
    async def forward_signal_to_backend(self, signal: Dict):
        """
        Forward signal to backend API for autotrading
        TODO: Implement in Phase 4 when backend signal ingestion endpoint is ready
        """
        # This will POST to /api/signals/intake endpoint
        # Backend will validate, store, and trigger autotrading for PREMIUM users
        pass
    
    def run(self):
        """Start the bot"""
        print("\n" + "="*70)
        print("🤖 VerzekAutoTrader Signal Bridge Bot - Starting...")
        print("="*70)
        trading_mode = get_trading_mode() if 'get_trading_mode' in globals() else 'DRY-RUN'
        print(f"Mode: {trading_mode}")
        print(f"Bot Token: {'✅ Set' if self.bot_token else '❌ Missing'}")
        print(f"Trial Group: {self.trial_group_id or 'Not configured'}")
        print(f"VIP Group: {self.vip_group_id or 'Not configured'}")
        print(f"Debug Group: {self.debug_group_id or 'Not configured'}")
        print(f"Authorized Bots: {', '.join(self.authorized_bot_usernames) or 'None'}")
        print(f"Authorized Users: {', '.join(map(str, self.authorized_user_ids))}")
        print("="*70 + "\n")
        
        logger.info("🤖 Signal bridge bot started (python-telegram-bot)")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    try:
        bot = SignalBridgeBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {str(e)}")
        logger.error(f"Bot crashed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
