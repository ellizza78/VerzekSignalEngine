#!/usr/bin/env python3
"""
Telegram Signal Intake Bot - Pyrogram BOT API (Phase 2)
SAFE MODE: Uses BOT API only (NOT personal account)
Receives trading signals, validates them, and broadcasts to groups
"""
import os
import sys
import asyncio
import re
import json
from datetime import datetime
from typing import Optional, Dict

# Pyrogram imports
try:
    from pyrogram import Client, filters
    from pyrogram.types import Message
except ImportError:
    print("⚠️  Pyrogram not installed. Install with: pip install pyrogram")
    sys.exit(1)

# Flask app imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.logger import api_logger


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
        
        # Detect signal type
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
        
        # Extract symbol
        symbol_match = re.search(r'(BTC|ETH|BNB|SOL|XRP|ADA|DOGE|MATIC|LINK|UNI|AVAX|ATOM)[A-Z]*', text)
        if not symbol_match:
            return None
        
        symbol = symbol_match.group(0)
        if not symbol.endswith("USDT"):
            symbol = symbol + "USDT"
        
        # Extract entry price
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
        
        # Extract stop loss
        sl = None
        sl_match = re.search(r'SL[:\s]+(\d+\.?\d*)', text)
        if sl_match:
            sl = float(sl_match.group(1))
        
        # Extract take profit targets
        tp_targets = []
        tp_matches = re.findall(r'TP[:\s]+(\d+\.?\d*)', text)
        if tp_matches:
            tp_targets = [float(tp) for tp in tp_matches]
        else:
            # Try comma-separated format
            tp_match = re.search(r'TP[:\s]+([\d\.,\s]+)', text)
            if tp_match:
                tp_text = tp_match.group(1)
                tp_targets = [float(x.strip()) for x in re.findall(r'\d+\.?\d*', tp_text)]
        
        # Extract leverage (if mentioned)
        leverage = 1
        lev_match = re.search(r'(\d+)X', text)
        if lev_match:
            leverage = int(lev_match.group(1))
        
        # Build signal object
        signal = {
            "type": signal_type,
            "symbol": symbol,
            "entry": entry,
            "sl": sl,
            "tp": tp_targets if tp_targets else None,
            "leverage": leverage,
            "raw_text": text[:200],  # First 200 chars
            "source": "telegram_bot",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return signal


class SignalBot:
    """Telegram signal intake bot"""
    
    def __init__(self):
        """Initialize bot"""
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.trial_chat_id = os.getenv("TELEGRAM_TRIAL_CHAT_ID")
        self.vip_chat_id = os.getenv("TELEGRAM_VIP_CHAT_ID")
        self.admin_chat_id = os.getenv("ADMIN_CHAT_ID")
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable required")
        
        # Initialize Pyrogram bot client
        self.app = Client(
            "verzek_signal_bot",
            bot_token=self.bot_token,
            workdir="telegram_sessions"
        )
        
        # Register handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup message handlers"""
        
        @self.app.on_message(filters.private & filters.text)
        async def handle_private_message(client: Client, message: Message):
            """Handle private messages (signals from admin)"""
            await self.process_signal(message)
        
        @self.app.on_message(filters.command("start"))
        async def handle_start(client: Client, message: Message):
            """Handle /start command"""
            await message.reply_text(
                "✅ VerzekAutoTrader Signal Bot\n\n"
                "Send me trading signals and I'll broadcast them to your groups.\n\n"
                "Supported formats:\n"
                "• BUY BTCUSDT @ 50000\n"
                "• SELL ETHUSDT entry: 3000, sl: 2900, tp: 3100\n"
                "• #LONG #BTCUSDT Entry: 50000 SL: 48000 TP: 52000"
            )
        
        @self.app.on_message(filters.command("status"))
        async def handle_status(client: Client, message: Message):
            """Handle /status command"""
            await message.reply_text(
                "🟢 Bot Status: ACTIVE\n"
                "📡 Mode: Phase 2 - DRY-RUN\n"
                "⚠️  NO REAL TRADING ENABLED"
            )
    
    async def process_signal(self, message: Message):
        """Process incoming signal message"""
        try:
            # Parse signal
            signal = SignalParser.parse_signal(message.text)
            
            if not signal:
                await message.reply_text("⚠️ Could not parse signal. Please check format.")
                return
            
            # Log signal
            api_logger.info(f"📨 Signal received: {signal['symbol']} {signal['type']}")
            
            # Confirm to sender
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
            await message.reply_text(confirm_text)
            
            # Phase 2: Save to file (no broadcasting yet)
            await self.save_signal_to_file(signal)
            
            # Phase 3: Will broadcast to groups
            # await self.broadcast_signal(signal)
            
        except Exception as e:
            api_logger.error(f"Error processing signal: {str(e)}")
            await message.reply_text(f"❌ Error: {str(e)}")
    
    async def save_signal_to_file(self, signal: Dict):
        """Save signal to file for Phase 2 validation"""
        os.makedirs("telegram_signals", exist_ok=True)
        filename = f"telegram_signals/signal_{int(datetime.utcnow().timestamp())}.json"
        
        with open(filename, 'w') as f:
            json.dump(signal, f, indent=2)
        
        api_logger.info(f"💾 Signal saved to {filename}")
    
    async def broadcast_signal(self, signal: Dict):
        """
        Broadcast signal to groups (Phase 3)
        Phase 2: NOT IMPLEMENTED YET
        """
        # Phase 3 implementation:
        # - Send to TRIAL group (if configured)
        # - Send to VIP group (if configured)
        # - Trigger auto-trading for PREMIUM users
        pass
    
    def run(self):
        """Start the bot"""
        print("\n" + "="*70)
        print("🤖 VerzekAutoTrader Signal Bot - Starting...")
        print("="*70)
        print(f"Mode: Phase 2 - DRY-RUN")
        print(f"Bot Token: {'✅ Set' if self.bot_token else '❌ Missing'}")
        print(f"Trial Chat ID: {self.trial_chat_id or 'Not configured'}")
        print(f"VIP Chat ID: {self.vip_chat_id or 'Not configured'}")
        print("="*70 + "\n")
        
        api_logger.info("🤖 Signal bot started (Pyrogram BOT API)")
        self.app.run()


def main():
    """Main entry point"""
    try:
        bot = SignalBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {str(e)}")
        api_logger.error(f"Bot crashed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
