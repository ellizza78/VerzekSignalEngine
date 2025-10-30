#!/usr/bin/env python3
"""
Test VIP and PREMIUM Welcome Emails
------------------------------------
Run this on Vultr to test the new welcome email functions
"""

import os
import sys

# Add project directory to path
sys.path.insert(0, '/var/www/VerzekAutoTrader')

# Set Gmail credentials
os.environ['EMAIL_HOST'] = 'smtp.gmail.com'
os.environ['EMAIL_PORT'] = '587'
os.environ['EMAIL_USER'] = 'verzekinnovativesolutionsltd@gmail.com'
os.environ['EMAIL_PASS'] = 'hhuvudmkfuquqgan'
os.environ['EMAIL_FROM'] = 'verzekinnovativesolutionsltd@gmail.com'

from mail_sender import send_vip_welcome_email, send_premium_welcome_email

print("=" * 60)
print("TESTING VERZEK WELCOME EMAILS")
print("=" * 60)

# Get test email from user
test_email = input("\nEnter your email address to receive test emails: ").strip()

if not test_email or '@' not in test_email:
    print("❌ Invalid email address!")
    sys.exit(1)

print(f"\n📧 Test emails will be sent to: {test_email}\n")

# Test VIP Welcome Email
print("-" * 60)
print("TEST 1: VIP Welcome Email ($50/month)")
print("-" * 60)

try:
    send_vip_welcome_email(
        to=test_email,
        user_name='John Doe',
        user_id='VIP12345'
    )
    print("✅ VIP welcome email sent successfully!")
    print("   Check your inbox for: 'Welcome to VIP - Your Signal Access Guide'")
except Exception as e:
    print(f"❌ Failed to send VIP email: {str(e)}")

print("\n")

# Test PREMIUM Welcome Email
print("-" * 60)
print("TEST 2: PREMIUM Welcome Email ($120/month)")
print("-" * 60)

try:
    send_premium_welcome_email(
        to=test_email,
        user_name='Jane Smith',
        user_id='PREM67890'
    )
    print("✅ PREMIUM welcome email sent successfully!")
    print("   Check your inbox for: 'Welcome to PREMIUM - Full Auto-Trading Access'")
except Exception as e:
    print(f"❌ Failed to send PREMIUM email: {str(e)}")

print("\n" + "=" * 60)
print("TESTING COMPLETE!")
print("=" * 60)
print("\n📧 Check your inbox for both emails:")
print("   1. VIP Welcome Email (signals only)")
print("   2. PREMIUM Welcome Email (auto-trading)")
print("\n💡 If you don't see them, check your spam folder!\n")
