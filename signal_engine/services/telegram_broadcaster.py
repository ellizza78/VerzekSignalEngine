"""
Telegram Broadcast Bot
Sends signals to VIP and Trial Telegram groups using python-telegram-bot
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError
import asyncio

load_dotenv()

logger = logging.getLogger(__name__)


class TelegramBroadcaster:
    """Broadcasts trading signals to Telegram groups"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.vip_group_id = os.getenv('TELEGRAM_VIP_GROUP_ID')
        self.trial_group_id = os.getenv('TELEGRAM_TRIAL_GROUP_ID')
        self.admin_group_id = os.getenv('TELEGRAM_ADMIN_GROUP_ID')
        
        self.bot = None
        self.messages_sent = 0
        self.messages_failed = 0
        
        if self.token:
            self.bot = Bot(token=self.token)
            logger.info("✅ Telegram broadcaster initialized")
        else:
            logger.warning("⚠️ Telegram bot token not found. Broadcast disabled.")
    
    async def broadcast_signal(self, message: str, to_groups: list = ['vip', 'trial']) -> bool:
        """
        Broadcast signal to specified Telegram groups
        
        Args:
            message: Formatted signal message
            to_groups: List of groups to send to ['vip', 'trial', 'admin']
            
        Returns:
            True if sent successfully to at least one group
        """
        if not self.bot:
            logger.warning("Telegram bot not initialized")
            return False
        
        success_count = 0
        
        try:
            # Send to VIP group
            if 'vip' in to_groups and self.vip_group_id:
                success = await self._send_message(self.vip_group_id, message)
                if success:
                    success_count += 1
                    logger.info("📤 Signal sent to VIP group")
            
            # Send to Trial group
            if 'trial' in to_groups and self.trial_group_id:
                success = await self._send_message(self.trial_group_id, message)
                if success:
                    success_count += 1
                    logger.info("📤 Signal sent to TRIAL group")
            
            # Send to Admin group (monitoring)
            if 'admin' in to_groups and self.admin_group_id:
                admin_message = f"🔔 ADMIN NOTIFICATION\n\n{message}"
                success = await self._send_message(self.admin_group_id, admin_message)
                if success:
                    success_count += 1
                    logger.info("📤 Signal sent to ADMIN group")
            
            if success_count > 0:
                self.messages_sent += success_count
                return True
            else:
                self.messages_failed += 1
                return False
                
        except Exception as e:
            logger.error(f"❌ Broadcast error: {e}")
            self.messages_failed += 1
            return False
    
    async def _send_message(self, chat_id: str, message: str) -> bool:
        """Send message to a specific chat"""
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram error sending to {chat_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def send_startup_notification(self):
        """Send notification when signal engine starts"""
        if not self.bot or not self.admin_group_id:
            return
        
        message = """
🚀 **VerzekSignalEngine Started**

All trading bots are now active:
✅ Scalping Bot (15s interval)
✅ Trend Bot (5m interval)
✅ QFL Bot (20s interval)
✅ AI/ML Bot (30s interval)

Signals will be broadcast automatically.
        """
        
        await self._send_message(self.admin_group_id, message.strip())
        logger.info("📤 Startup notification sent to admin")
    
    async def send_error_alert(self, error_message: str):
        """Send error alert to admin group"""
        if not self.bot or not self.admin_group_id:
            return
        
        message = f"""
⚠️ **Signal Engine Error**

{error_message}

Please check the logs for details.
        """
        
        await self._send_message(self.admin_group_id, message.strip())
    
    async def send_partial_tp_message(self, outcome, tp_number: int = None):
        """
        Send partial TP message (TP1-TP4) to Telegram groups
        
        Args:
            outcome: SignalOutcome from tracker.on_target_hit()
            tp_number: TP level (1-4), defaults to current_tp_index + 1
        """
        if not self.bot:
            logger.warning("Telegram bot not initialized")
            return False
        
        # Calculate TP number from outcome if not provided
        if tp_number is None:
            tp_number = outcome.current_tp_index + 1
        
        # Format message for partial TP
        message = f"""
🔥 **VERZEK TRADING SIGNALS** 🔥

{outcome.symbol} - 🚨 **Target {tp_number} reached**
💸 Profit collected {outcome.profit_pct:+.2f}%
⏰ Posted: {outcome.duration_formatted}
        """
        
        # Broadcast to VIP and TRIAL groups
        success = await self.broadcast_signal(message.strip(), to_groups=['vip', 'trial'])
        
        if success:
            logger.info(f"✅ TP{tp_number} message sent: {outcome.symbol} {outcome.profit_pct:+.2f}%")
        else:
            logger.error(f"❌ Failed to send TP{tp_number} message for {outcome.symbol}")
        
        return success
    
    async def send_final_tp_message(self, outcome):
        """
        Send final TP message (TP5) to Telegram groups
        
        Args:
            outcome: SignalOutcome from tracker.on_target_hit() with is_final=True
        """
        if not self.bot:
            logger.warning("Telegram bot not initialized")
            return False
        
        # Format message for final TP (TP5)
        message = f"""
🔥 **VERZEK TRADING SIGNALS** 🔥

🏋🏻‍♀️ **Gained Profit on {outcome.symbol}**
All take-profit targets achieved 😎
Profit: {outcome.profit_pct:+.2f}% 📈
Period: {outcome.duration_formatted} ⏰
        """
        
        # Broadcast to VIP and TRIAL groups
        success = await self.broadcast_signal(message.strip(), to_groups=['vip', 'trial'])
        
        if success:
            logger.info(f"✅ TP5 (FINAL) message sent: {outcome.symbol} {outcome.profit_pct:+.2f}%")
        else:
            logger.error(f"❌ Failed to send TP5 (FINAL) message for {outcome.symbol}")
        
        return success
    
    def get_stats(self) -> dict:
        """Get broadcast statistics"""
        return {
            'messages_sent': self.messages_sent,
            'messages_failed': self.messages_failed,
            'success_rate': (self.messages_sent / (self.messages_sent + self.messages_failed) * 100) if (self.messages_sent + self.messages_failed) > 0 else 0
        }


# Singleton instance
_broadcaster_instance = None

def get_broadcaster() -> TelegramBroadcaster:
    """Get or create broadcaster instance"""
    global _broadcaster_instance
    if _broadcaster_instance is None:
        _broadcaster_instance = TelegramBroadcaster()
    return _broadcaster_instance
