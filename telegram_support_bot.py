"""
Telegram Support Bot
-------------------
Auto-replies to customer messages and forwards them to support@vezekinnovative.com
Alerts admin via Telegram when new messages arrive
Uses python-telegram-bot v13 API (same as broadcast_bot)
"""

import os
import logging
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from modules.email_service import email_service

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_SUPPORT_BOT_TOKEN', '')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', '7442859456'))

# Auto-reply message template
AUTO_REPLY_MESSAGE = """👋 Hi there!

Thanks for reaching out to Verzek Innovative Solutions.

Your message has been received ✅

We'll get back to you within a few hours.

— Verzek Support Team"""


def start_command(update: Update, context):
    """Handle /start command"""
    welcome_message = """👋 Welcome to Verzek Innovative Support!

I'm here to help you with:
• VerzekAutoTrader platform questions
• Subscription and payment issues
• Exchange integration support
• Technical troubleshooting
• General inquiries

📧 You can also email us at: support@vezekinnovative.com
💬 Or message us here directly!

Our support hours:
🕐 Monday - Friday: 9 AM - 6 PM UTC
🕐 Saturday: 10 AM - 4 PM UTC
🕐 Sunday: Closed

Type your message and we'll respond as soon as possible!"""
    
    update.message.reply_text(welcome_message)
    logger.info(f"User {update.effective_user.id} started conversation")


def info_command(update: Update, context):
    """Handle /info command"""
    info_message = """ℹ️ Verzek Innovative Solutions - Contact Information

📧 Email: support@vezekinnovative.com
💬 Telegram: @VerzekSupportBot
🌐 Platform: VerzekAutoTrader

**Support Hours:**
🕐 Monday - Friday: 9 AM - 6 PM UTC
🕐 Saturday: 10 AM - 4 PM UTC
🕐 Sunday: Closed

**Response Time:**
⚡ Urgent issues: Within 2 hours
📋 General inquiries: Within 24 hours

**What we help with:**
• Account setup and verification
• Subscription plans (TRIAL, VIP, PREMIUM)
• Exchange API integration
• Auto-trading configuration
• Payment and billing
• Technical support

Need immediate help? Send us a message here!"""
    
    update.message.reply_text(info_message)
    logger.info(f"User {update.effective_user.id} requested info")


def handle_message(update: Update, context):
    """Handle incoming messages from users"""
    user = update.effective_user
    message_text = update.message.text
    
    # User info
    user_id = user.id
    username = user.username
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    full_name = f"{first_name} {last_name}".strip() or f"User {user_id}"
    
    logger.info(f"Message from {full_name} (@{username}): {message_text}")
    
    # Send auto-reply to user
    try:
        update.message.reply_text(AUTO_REPLY_MESSAGE)
        logger.info(f"Auto-reply sent to {full_name}")
    except Exception as e:
        logger.error(f"Failed to send auto-reply: {e}")
    
    # Forward to support email via Zoho SMTP
    try:
        email_result = email_service.send_support_notification(
            from_user=full_name,
            message=message_text,
            telegram_username=username
        )
        
        if email_result['success']:
            logger.info(f"✅ Support email sent for message from {full_name}")
        else:
            logger.error(f"❌ Failed to send support email: {email_result.get('error')}")
    except Exception as e:
        logger.error(f"❌ Exception sending support email: {e}")
    
    # Notify admin on Telegram
    try:
        admin_notification = f"""🆘 *New Support Message*

*From:* {full_name}
*Username:* @{username if username else 'No username'}
*User ID:* {user_id}

*Message:*
{message_text}

---
📧 Email forwarded to support@vezekinnovative.com"""
        
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_notification,
            parse_mode='Markdown'
        )
        logger.info(f"✅ Admin notified about message from {full_name}")
    except Exception as e:
        logger.error(f"❌ Failed to notify admin: {e}")


def error_handler(update, context):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Start the support bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_SUPPORT_BOT_TOKEN not set! Bot cannot start.")
        return
    
    logger.info("🤖 Starting Verzek Support Bot...")
    
    # Delete any existing webhook to enable polling mode
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.delete_webhook()
        logger.info("✅ Deleted existing webhook (if any) to enable polling mode")
    except Exception as e:
        logger.warning(f"⚠️ Could not delete webhook: {e}")
    
    # Create updater and dispatcher
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("info", info_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Add error handler
    dispatcher.add_error_handler(error_handler)
    
    # Start bot with polling
    logger.info("✅ Support bot is running!")
    logger.info(f"📧 Messages will be forwarded to: {email_service.from_email}")
    logger.info(f"👤 Admin notifications sent to Chat ID: {ADMIN_CHAT_ID}")
    
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
