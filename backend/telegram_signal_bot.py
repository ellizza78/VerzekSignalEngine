#!/usr/bin/env python3
"""
Telegram Signal Intake Bot - python-telegram-bot (Phase 2)
SAFE MODE: Uses BOT API only (NOT personal account)
Receives trading signals, validates them, and broadcasts to groups
"""
import os
import sys
import re
import json
from datetime import datetime
from typing import Optional, Dict

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    print("⚠️  python-telegram-bot not installed. Install with: pip install python-telegram-bot")
    sys.exit(1)

import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class SignalParser:
    """Parse trading signals from Telegram messages"""
    
    @staticmethod
    def parse_signal(text: str) -> Optional[Dict]:
        """
        Parse signal from message text
        
        Expected formats:
        - "BUY BTCUSDT @ 50000"
        - "SELL ETHUSDT entry: 3000, sl: 2900, tp: 3100,3200"
        - "#LONG #BTCUSDT Entry: 50000 SL: 48000 TP: 52000, 54000"
        
        Returns:
            Signal dict or None
        """
        text = text.upper().strip()
        
        signal_type = None
        if "BUY" in text or "LONG" in text or "#BUY" in text or "#LONG" in text:
            signal_type = "BUY"
        elif "SELL" in text or "SHORT" in text or "#SELL" in text or "#SHORT" in text:
            signal_type = "SELL"
        elif "CLOSE" in text or "#CLOSE" in text:
            signal_type = "CLOSE"
        elif "UPDATE" in text or "#UPDATE" in text:
            signal_type = "UPDATE"
        
        if not signal_type:
            return None
        
        symbol_match = re.search(r'(BTC|ETH|BNB|SOL|XRP|ADA|DOGE|MATIC|LINK|UNI|AVAX|ATOM)[A-Z]*', text)
        if not symbol_match:
            return None
        
        symbol = symbol_match.group(0)
        if not symbol.endswith("USDT"):
            symbol = symbol + "USDT"
        
        entry = None
        entry_patterns = [
            r'ENTRY[:\s]+(\d+\.?\d*)',
            r'@\s*(\d+\.?\d*)',
            r'PRICE[:\s]+(\d+\.?\d*)'
        ]
        for pattern in entry_patterns:
            match = re.search(pattern, text)
            if match:
                entry = float(match.group(1))
                break
        
        sl = None
        sl_match = re.search(r'SL[:\s]+(\d+\.?\d*)', text)
        if sl_match:
            sl = float(sl_match.group(1))
        
        tp_targets = []
        tp_matches = re.findall(r'TP[:\s]+(\d+\.?\d*)', text)
        if tp_matches:
            tp_targets = [float(tp) for tp in tp_matches]
        else:
            tp_match = re.search(r'TP[:\s]+([\d\.,\s]+)', text)
            if tp_match:
                tp_text = tp_match.group(1)
                tp_targets = [float(x.strip()) for x in re.findall(r'\d+\.?\d*', tp_text)]
        
        leverage = 1
        lev_match = re.search(r'(\d+)X', text)
        if lev_match:
            leverage = int(lev_match.group(1))
        
        signal = {
            "type": signal_type,
            "symbol": symbol,
            "entry": entry,
            "sl": sl,
            "tp": tp_targets if tp_targets else None,
            "leverage": leverage,
            "raw_text": text[:200],
            "source": "telegram_bot",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return signal


class SignalBot:
    """Telegram signal intake bot"""
    
    def __init__(self):
        """Initialize bot"""
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.admin_chat_id = os.getenv("ADMIN_CHAT_ID")
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable required")
        
        os.makedirs("telegram_signals", exist_ok=True)
        os.makedirs("telegram_sessions", exist_ok=True)
        
        self.application = Application.builder().token(self.bot_token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup message handlers"""
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("status", self.handle_status))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "✅ VerzekAutoTrader Signal Bot\n\n"
            "Send me trading signals and I'll broadcast them to your groups.\n\n"
            "Supported formats:\n"
            "• BUY BTCUSDT @ 50000\n"
            "• SELL ETHUSDT entry: 3000, sl: 2900, tp: 3100\n"
            "• #LONG #BTCUSDT Entry: 50000 SL: 48000 TP: 52000"
        )
    
    async def handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        await update.message.reply_text(
            "🟢 Bot Status: ACTIVE\n"
            "📡 Mode: Phase 2 - DRY-RUN\n"
            "⚠️  NO REAL TRADING ENABLED"
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        try:
            signal = SignalParser.parse_signal(update.message.text)
            
            if not signal:
                await update.message.reply_text("⚠️ Could not parse signal. Please check format.")
                return
            
            logger.info(f"📨 Signal received: {signal['symbol']} {signal['type']}")
            
            confirm_text = (
                f"✅ Signal Parsed:\n"
                f"• Symbol: {signal['symbol']}\n"
                f"• Type: {signal['type']}\n"
                f"• Entry: {signal['entry']}\n"
                f"• SL: {signal['sl']}\n"
                f"• TP: {signal['tp']}\n"
                f"• Leverage: {signal['leverage']}x\n\n"
                f"⚠️ Phase 2: DRY-RUN mode (no broadcasting yet)"
            )
            await update.message.reply_text(confirm_text)
            
            await self.save_signal_to_file(signal)
            
        except Exception as e:
            logger.error(f"Error processing signal: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def save_signal_to_file(self, signal: Dict):
        """Save signal to file for Phase 2 validation"""
        filename = f"telegram_signals/signal_{int(datetime.utcnow().timestamp())}.json"
        
        with open(filename, 'w') as f:
            json.dump(signal, f, indent=2)
        
        logger.info(f"💾 Signal saved to {filename}")
    
    def run(self):
        """Start the bot"""
        print("\n" + "="*70)
        print("🤖 VerzekAutoTrader Signal Bot - Starting...")
        print("="*70)
        print(f"Mode: Phase 2 - DRY-RUN")
        print(f"Bot Token: {'✅ Set' if self.bot_token else '❌ Missing'}")
        print(f"Admin Chat ID: {self.admin_chat_id or 'Not configured'}")
        print("="*70 + "\n")
        
        logger.info("🤖 Signal bot started (python-telegram-bot)")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    try:
        bot = SignalBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {str(e)}")
        logger.error(f"Bot crashed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
