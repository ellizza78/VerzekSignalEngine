#!/usr/bin/env python3
"""
Test script for admin notifications
Run this to test Telegram notifications without triggering actual payouts
"""

import os
from services.admin_notifications import admin_notifier
from utils.admin_dashboard import send_batch_payout_notification, send_daily_platform_summary
from datetime import datetime


def test_notifications():
    """Test all notification types"""
    
    print("🧪 Testing Admin Notification System\n")
    print("=" * 60)
    
    # Check if Telegram is configured
    if not admin_notifier.telegram_enabled:
        print("❌ Telegram not configured!")
        print("\nTo enable notifications, set these Replit Secrets:")
        print("  TELEGRAM_BOT_TOKEN=your_bot_token")
        print("  ADMIN_CHAT_ID=your_chat_id")
        print("\nTelegram Bot Setup:")
        print("  1. Message @BotFather on Telegram")
        print("  2. Create new bot with /newbot")
        print("  3. Copy the bot token")
        print("  4. Message your bot and get chat ID from @userinfobot")
        return
    
    print("✅ Telegram configured!\n")
    
    # Test 1: Payout Request Notification
    print("\n1️⃣ Testing Payout Request Notification...")
    test_payout = {
        'payout_id': 'PAYOUT_test_user_1234567890',
        'user_id': 'test_user_123',
        'amount_usdt': 45.50,
        'wallet_address': 'TTestWalletAddress1234567890abcdefghijk',
        'requested_at': datetime.now().isoformat()
    }
    
    result = admin_notifier.notify_payout_request(test_payout)
    print(f"   Result: {'✅ Sent' if result else '❌ Failed'}")
    
    # Test 2: Payment Received Notification
    print("\n2️⃣ Testing Payment Received Notification...")
    test_payment = {
        'user_id': 'test_user_456',
        'plan': 'pro',
        'amount_usdt': 29.00,
        'tx_hash': '9f2a1b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7',
        'referral_bonus': 2.90
    }
    
    result = admin_notifier.notify_payment_received(test_payment)
    print(f"   Result: {'✅ Sent' if result else '❌ Failed'}")
    
    # Test 3: Large Payout (High Priority)
    print("\n3️⃣ Testing High Priority Payout (>$100)...")
    large_payout = {
        'payout_id': 'PAYOUT_whale_user_9999999999',
        'user_id': 'whale_user_999',
        'amount_usdt': 250.00,
        'wallet_address': 'TWhaleWalletAddress1234567890abcdefghijk',
        'requested_at': datetime.now().isoformat()
    }
    
    result = admin_notifier.notify_payout_request(large_payout)
    print(f"   Result: {'✅ Sent' if result else '❌ Failed'}")
    
    # Test 4: System Alert
    print("\n4️⃣ Testing System Alert...")
    result = admin_notifier.notify_system_alert(
        'info',
        'Admin notification system test completed successfully!'
    )
    print(f"   Result: {'✅ Sent' if result else '❌ Failed'}")
    
    # Test 5: Daily Summary (optional - only if you want to test)
    print("\n5️⃣ Testing Daily Summary (optional)...")
    user_input = input("   Send daily summary? (y/n): ").lower()
    if user_input == 'y':
        result = send_daily_platform_summary()
        print(f"   Result: {'✅ Sent' if result else '❌ Failed'}")
    else:
        print("   Skipped")
    
    print("\n" + "=" * 60)
    print("✅ Testing complete! Check your Telegram for notifications.")
    print("\nNote: These are test notifications. No actual payouts were created.")


if __name__ == "__main__":
    test_notifications()
