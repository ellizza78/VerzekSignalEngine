#!/usr/bin/env python3
"""
VerzekAutoTrader FAQ PDF Generator
Creates a comprehensive customer support FAQ document
"""

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime

class VerzekFAQPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(15, 15, 15)
        
    def header(self):
        """Page header with VZK branding"""
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(26, 154, 170)  # Teal color
        self.cell(0, 10, 'VerzekAutoTrader - Frequently Asked Questions', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(5)
        
    def footer(self):
        """Page footer with page number"""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
        
    def add_section_title(self, title):
        """Add a section title"""
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(249, 199, 79)  # Gold color
        self.ln(5)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        self.set_draw_color(249, 199, 79)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)
        
    def add_question(self, question, answer):
        """Add a Q&A pair"""
        # Question
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(10, 74, 92)  # Dark teal
        self.multi_cell(0, 6, f'Q: {question}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Answer
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 5, f'A: {answer}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

def generate_faq_pdf():
    """Generate the complete FAQ PDF"""
    pdf = VerzekFAQPDF()
    pdf.add_page()
    
    # Title Page Information
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(26, 154, 170)
    pdf.ln(20)
    pdf.cell(0, 10, 'VerzekAutoTrader', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, 'Customer Support FAQ', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.cell(0, 6, f'Last Updated: {datetime.now().strftime("%B %d, %Y")}', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    
    # Support Contact Information
    pdf.ln(20)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(249, 199, 79)
    pdf.cell(0, 8, 'Need More Help?', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 6, 'Email: support@verzektrader.com', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.cell(0, 6, 'Telegram: @VerzekSupport', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    
    # Table of Contents
    pdf.add_page()
    pdf.add_section_title('Table of Contents')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    sections = [
        '1. Getting Started',
        '2. Account Management',
        '3. Subscription & Plans',
        '4. Payment & Billing',
        '5. Exchange Integration',
        '6. Auto-Trading',
        '7. Security & Safety',
        '8. Technical Support',
        '9. Referral Program',
        '10. Terms & Policies'
    ]
    for section in sections:
        pdf.cell(0, 6, section, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # ==================== SECTION 1: GETTING STARTED ====================
    pdf.add_page()
    pdf.add_section_title('1. Getting Started')
    
    pdf.add_question(
        'What is VerzekAutoTrader?',
        'VerzekAutoTrader is a multi-tenant auto-trading platform that specializes in Dollar Cost Averaging (DCA) strategies. It monitors Telegram for trading signals and automatically executes trades on your connected exchange accounts using advanced risk management.'
    )
    
    pdf.add_question(
        'How do I download the VerzekAutoTrader app?',
        'For Android: Download the APK file from the link provided by our team or via email. For iOS: Use TestFlight (beta testing) or download through Expo Go. Contact support@verzektrader.com for download links.'
    )
    
    pdf.add_question(
        'How do I create an account?',
        'Open the app, tap "Create Account", enter your full name, email address, and password, complete the sliding puzzle CAPTCHA by dragging the slider to verify, then tap "Create Account". You\'ll receive a verification email - click the link to activate your account.'
    )
    
    pdf.add_question(
        'Why do I need to verify my email?',
        'Email verification ensures account security and is required before you can connect exchange accounts or start auto-trading. It also helps us send you important notifications about your account and trading activity.'
    )
    
    pdf.add_question(
        'I didn\'t receive the verification email. What should I do?',
        'Check your spam/junk folder first. If you still don\'t see it, tap "Resend Verification Email" on the verification screen. You can resend after 60 seconds. If problems persist, contact support@verzektrader.com.'
    )
    
    # ==================== SECTION 2: ACCOUNT MANAGEMENT ====================
    pdf.add_page()
    pdf.add_section_title('2. Account Management')
    
    pdf.add_question(
        'How do I reset my password?',
        'On the login screen, tap "Forgot Password?", enter your registered email address, and follow the instructions sent to your email to reset your password.'
    )
    
    pdf.add_question(
        'What is my referral code and where can I find it?',
        'Your referral code is automatically generated when you create an account. Find it in the Profile screen under "Referral Code". Tap the code to copy it to your clipboard and share it with friends.'
    )
    
    pdf.add_question(
        'How do I log out of the app?',
        'Go to Profile screen and tap "Logout" at the bottom. Note: The app automatically logs you out after 5 minutes of inactivity for security.'
    )
    
    pdf.add_question(
        'Why was I logged out automatically?',
        'For your security, VerzekAutoTrader automatically logs you out after 5 minutes of inactivity. This protects your account and trading data if you leave the app open accidentally.'
    )
    
    pdf.add_question(
        'Can I delete my account?',
        'Yes. To permanently delete your account, contact support@verzektrader.com with your registered email. Note: All trading data, positions, and subscription benefits will be permanently removed.'
    )
    
    # ==================== SECTION 3: SUBSCRIPTION & PLANS ====================
    pdf.add_page()
    pdf.add_section_title('3. Subscription & Plans')
    
    pdf.add_question(
        'What subscription plans are available?',
        'We offer three plans:\n\n' +
        '1. TRIAL - FREE for 4 days (limited features, perfect for testing)\n' +
        '2. VIP - $50/month (full automation, unlimited signals, priority support)\n' +
        '3. PREMIUM - $120/month (everything in VIP + advanced AI features, custom strategies)'
    )
    
    pdf.add_question(
        'How does the TRIAL subscription work?',
        'New users get a FREE 4-day TRIAL subscription to test the platform. You can activate it from the Subscription screen. No payment required. After 4 days, upgrade to VIP or PREMIUM to continue trading.'
    )
    
    pdf.add_question(
        'What\'s the difference between VIP and PREMIUM?',
        'VIP ($50/month): Full auto-trading, unlimited signals, all exchanges, priority support, advanced risk management.\n\n' +
        'PREMIUM ($120/month): Everything in VIP PLUS AI Trade Assistant, custom DCA strategies, advanced analytics, copy trading, and dedicated account manager.'
    )
    
    pdf.add_question(
        'How do I upgrade my subscription?',
        'Go to Subscription screen, select your desired plan (VIP or PREMIUM), tap "Upgrade Now", and follow the payment instructions to send USDT TRC20 to our wallet address.'
    )
    
    pdf.add_question(
        'Do subscriptions auto-renew?',
        'Subscriptions do NOT auto-renew. You must manually renew each month by submitting a new payment. This gives you full control over your subscription.'
    )
    
    # ==================== SECTION 4: PAYMENT & BILLING ====================
    pdf.add_page()
    pdf.add_section_title('4. Payment & Billing')
    
    pdf.add_question(
        'What payment methods do you accept?',
        'We accept USDT (Tether) on the TRC20 network only. This ensures fast, low-fee, and secure international payments.'
    )
    
    pdf.add_question(
        'What is the admin wallet address for payments?',
        'Our official payment address is:\n' +
        'TBjfqimYNsPecGxsk9kcX8GboPyZcWHNzb\n\n' +
        'Always verify this address in the app before sending payment. Never send funds to any other address claiming to be VerzekAutoTrader.'
    )
    
    pdf.add_question(
        'How do I make a payment?',
        'From the Subscription screen:\n' +
        '1. Select your plan (VIP or PREMIUM)\n' +
        '2. Copy the USDT TRC20 wallet address shown\n' +
        '3. Send the exact amount from your crypto wallet\n' +
        '4. Save your transaction ID (TxID)\n' +
        '5. Submit the TxID in the app for verification\n' +
        '6. Wait for admin approval (usually within 24 hours)'
    )
    
    pdf.add_question(
        'How long does payment verification take?',
        'Payments are typically verified within 24 hours. You\'ll receive a notification once your subscription is activated. If it takes longer, contact support@verzektrader.com with your transaction ID.'
    )
    
    pdf.add_question(
        'I sent payment but my subscription isn\'t active. What should I do?',
        'Make sure you submitted your transaction ID (TxID) in the app after payment. If you did and it\'s been over 24 hours, contact support@verzektrader.com with:\n' +
        '- Your registered email\n' +
        '- Transaction ID\n' +
        '- Amount sent\n' +
        '- Timestamp of payment'
    )
    
    pdf.add_question(
        'Can I get a refund?',
        'Due to the nature of our service and instant access to trading features, all payments are final and non-refundable. Please use the FREE 4-day TRIAL to test the platform before purchasing.'
    )
    
    pdf.add_question(
        'Do I earn anything by referring friends?',
        'Yes! You earn 10% recurring commission on every payment made by users who sign up with your referral code. This is paid monthly as long as they remain subscribed.'
    )
    
    # ==================== SECTION 5: EXCHANGE INTEGRATION ====================
    pdf.add_page()
    pdf.add_section_title('5. Exchange Integration')
    
    pdf.add_question(
        'Which exchanges are supported?',
        'VerzekAutoTrader currently supports:\n' +
        '- Binance Futures\n' +
        '- Bybit\n' +
        '- Phemex\n' +
        '- Kraken Futures\n\n' +
        'More exchanges will be added based on user demand.'
    )
    
    pdf.add_question(
        'How do I connect my exchange account?',
        'Go to Exchanges screen, tap "Add Exchange", select your exchange, enter your API Key and Secret, then tap "Add Exchange". Note: You must verify your email before connecting exchanges.'
    )
    
    pdf.add_question(
        'Are my API keys safe?',
        'Absolutely. Your API keys are encrypted using military-grade AES-128 encryption before being stored. We NEVER have access to your actual keys in plain text. Always use API keys with trading permissions only - never enable withdrawal permissions.'
    )
    
    pdf.add_question(
        'What permissions should I enable for my API keys?',
        'Enable ONLY:\n' +
        '- Read permissions (to check balances and positions)\n' +
        '- Trading permissions (to place and manage orders)\n\n' +
        'NEVER enable:\n' +
        '- Withdrawal permissions\n' +
        '- Transfer permissions\n\n' +
        'This ensures your funds stay safe even if your API key is compromised.'
    )
    
    pdf.add_question(
        'Do I need to whitelist an IP address for Binance?',
        'Yes, for Binance Futures, you should whitelist our server IP: 35.230.66.47\n\n' +
        'We use a Cloudflare Workers proxy with a static IP address to ensure reliable connections to Binance.'
    )
    
    pdf.add_question(
        'Can I use the same exchange account on multiple devices?',
        'Yes, your exchange connections are tied to your VerzekAutoTrader account, so you can access them from any device where you\'re logged in.'
    )
    
    pdf.add_question(
        'How do I remove an exchange connection?',
        'Go to Exchanges screen, find the exchange you want to remove, tap "Disconnect" or the delete icon, then confirm. Your encrypted API keys will be permanently deleted from our servers.'
    )
    
    # ==================== SECTION 6: AUTO-TRADING ====================
    pdf.add_page()
    pdf.add_section_title('6. Auto-Trading')
    
    pdf.add_question(
        'How does auto-trading work?',
        'VerzekAutoTrader monitors Telegram channels for trading signals. When a signal is detected, it automatically executes DCA (Dollar Cost Averaging) trades on your connected exchanges based on your configured settings and risk management rules.'
    )
    
    pdf.add_question(
        'What is Dollar Cost Averaging (DCA)?',
        'DCA is a strategy where you split your total investment into multiple smaller orders at different price levels. This reduces risk by averaging your entry price and protecting against sudden market moves.'
    )
    
    pdf.add_question(
        'How do I configure my trading settings?',
        'Go to Settings screen to configure:\n' +
        '- Capital Allocation (investment per trade, leverage 1-125x)\n' +
        '- Risk Management (max loss per trade, daily loss limit)\n' +
        '- DCA Configuration (number of orders, price deviation)\n' +
        '- Symbol Preferences (whitelist/blacklist trading pairs)'
    )
    
    pdf.add_question(
        'What is the recommended leverage setting?',
        'For beginners: Use 1x-5x leverage to minimize risk.\n' +
        'For experienced traders: 10x-20x with proper risk management.\n' +
        'For experts only: 50x-125x (high risk, high reward)\n\n' +
        'IMPORTANT: Higher leverage = higher risk. Only use what you can afford to lose.'
    )
    
    pdf.add_question(
        'How many concurrent trades can I have?',
        'You can set this in Settings > Capital Allocation > Concurrent Trades (1-20 range). Start with 1-3 trades if you\'re new, then increase as you gain experience.'
    )
    
    pdf.add_question(
        'What happens if the market moves against my position?',
        'VerzekAutoTrader has built-in safety features:\n' +
        '1. Auto-stop loss kicks in at your configured max loss\n' +
        '2. Daily loss limit prevents catastrophic losses\n' +
        '3. DCA orders average down your entry price\n' +
        '4. Progressive take-profit locks in gains at multiple levels'
    )
    
    pdf.add_question(
        'Can I manually close a position?',
        'Yes! Go to Positions screen, select the position you want to close, and tap "Close Position". This will immediately close the position at the current market price.'
    )
    
    pdf.add_question(
        'Where can I see live trading signals?',
        'Go to the Signals screen to see real-time signals from our Telegram monitoring system. You\'ll see the trading pair, direction (LONG/SHORT), entry price, and timestamp.'
    )
    
    pdf.add_question(
        'Do I need to keep the app open for auto-trading to work?',
        'No! Auto-trading runs on our servers 24/7. You can close the app, turn off your phone, and trades will continue executing automatically based on your settings.'
    )
    
    # ==================== SECTION 7: SECURITY & SAFETY ====================
    pdf.add_page()
    pdf.add_section_title('7. Security & Safety')
    
    pdf.add_question(
        'Is VerzekAutoTrader safe to use?',
        'Yes. We implement multiple security layers:\n' +
        '- Sliding puzzle CAPTCHA on login/registration\n' +
        '- Email verification requirement\n' +
        '- JWT-based authentication with secure tokens\n' +
        '- AES-128 encryption for API keys\n' +
        '- Auto-logout after 5 minutes of inactivity\n' +
        '- Rate limiting to prevent abuse\n' +
        '- Secure HTTPS connections for all data'
    )
    
    pdf.add_question(
        'Can VerzekAutoTrader withdraw my funds?',
        'NO. We never have access to withdraw your funds. When creating API keys, you should NEVER enable withdrawal permissions. We only need read and trading permissions to execute trades.'
    )
    
    pdf.add_question(
        'What is the sliding puzzle CAPTCHA?',
        'It\'s a security feature that requires you to drag a slider all the way to the right to verify you\'re human. This protects against automated bot attacks during login and registration.'
    )
    
    pdf.add_question(
        'How do I keep my account secure?',
        '1. Use a strong, unique password\n' +
        '2. Never share your password or login credentials\n' +
        '3. Enable only necessary API key permissions\n' +
        '4. Keep your email account secure\n' +
        '5. Don\'t use public WiFi for trading\n' +
        '6. Log out when using shared devices\n' +
        '7. Monitor your account activity regularly'
    )
    
    pdf.add_question(
        'What should I do if I suspect unauthorized access?',
        'Immediately:\n' +
        '1. Change your password\n' +
        '2. Revoke all exchange API keys\n' +
        '3. Create new API keys with correct permissions\n' +
        '4. Contact support@verzektrader.com\n' +
        '5. Review your recent trading activity'
    )
    
    # ==================== SECTION 8: TECHNICAL SUPPORT ====================
    pdf.add_page()
    pdf.add_section_title('8. Technical Support')
    
    pdf.add_question(
        'The app won\'t open or keeps crashing. What should I do?',
        'Try these steps:\n' +
        '1. Force close the app completely\n' +
        '2. Clear the app cache (Android: Settings > Apps > VerzekAutoTrader > Clear Cache)\n' +
        '3. Restart your phone\n' +
        '4. Reinstall the app (download latest version)\n' +
        '5. If still not working, contact support@verzektrader.com'
    )
    
    pdf.add_question(
        'I can\'t connect to my exchange. What\'s wrong?',
        'Common issues:\n' +
        '1. Check if your API key and secret are correct\n' +
        '2. Verify API key permissions (read + trading only)\n' +
        '3. For Binance, whitelist our IP: 35.230.66.47\n' +
        '4. Make sure your exchange account is verified\n' +
        '5. Check if the exchange API is operational (exchange status page)'
    )
    
    pdf.add_question(
        'My trades aren\'t executing. Why?',
        'Possible reasons:\n' +
        '1. Check your subscription status (must be VIP or PREMIUM)\n' +
        '2. Verify exchange connection is active\n' +
        '3. Ensure you have sufficient balance on the exchange\n' +
        '4. Check if the trading pair is blacklisted in your settings\n' +
        '5. Review your risk management settings (might be too restrictive)\n' +
        '6. Contact support with details of the signal'
    )
    
    pdf.add_question(
        'How do I update the app?',
        'For Android APK: Download the latest APK from the link provided and install over the old version.\n' +
        'For iOS TestFlight: Updates appear automatically in TestFlight.\n' +
        'For Expo Go: The app updates automatically when you restart it.'
    )
    
    pdf.add_question(
        'I found a bug. How do I report it?',
        'Thank you for helping us improve! Email support@verzektrader.com with:\n' +
        '- Detailed description of the bug\n' +
        '- Steps to reproduce it\n' +
        '- Screenshots (if applicable)\n' +
        '- Your device model and OS version\n' +
        '- App version'
    )
    
    pdf.add_question(
        'Do you offer phone support?',
        'We currently offer support via:\n' +
        '- Email: support@verzektrader.com (response within 24 hours)\n' +
        '- Telegram: @VerzekSupport (fastest response)\n\n' +
        'PREMIUM subscribers get priority support with faster response times.'
    )
    
    # ==================== SECTION 9: REFERRAL PROGRAM ====================
    pdf.add_page()
    pdf.add_section_title('9. Referral Program')
    
    pdf.add_question(
        'How does the referral program work?',
        'Share your unique referral code with friends. When they sign up using your code and purchase a subscription, you earn 10% of their payment every month as long as they stay subscribed.'
    )
    
    pdf.add_question(
        'Where can I find my referral code?',
        'Go to Profile screen and look for "Referral Code" section. Your code follows the format VZK + 6 characters (e.g., VZKa1b2c3). Tap it to copy and share.'
    )
    
    pdf.add_question(
        'How do I enter a referral code when signing up?',
        'During registration, there\'s an optional "Referral Code" field. Enter the code you received from a friend before creating your account. You can\'t add it later.'
    )
    
    pdf.add_question(
        'When do I receive my referral earnings?',
        'Referral commissions are calculated monthly. Contact support@verzektrader.com to request payout. Minimum payout is $10 USDT.'
    )
    
    pdf.add_question(
        'Is there a limit to how many people I can refer?',
        'No limit! Refer as many people as you want and earn 10% recurring commission from all of them. This can become significant passive income.'
    )
    
    pdf.add_question(
        'How can I track my referrals?',
        'Currently, referral tracking is managed by our admin team. Contact support@verzektrader.com to get a report of your referral earnings and active referrals.'
    )
    
    # ==================== SECTION 10: TERMS & POLICIES ====================
    pdf.add_page()
    pdf.add_section_title('10. Terms & Policies')
    
    pdf.add_question(
        'Who is responsible for my trading losses?',
        'You are solely responsible for all trading decisions and outcomes. VerzekAutoTrader is a tool that executes trades based on your settings. Cryptocurrency trading carries significant risk, and you should only trade with capital you can afford to lose.'
    )
    
    pdf.add_question(
        'What are the risks of using auto-trading?',
        'Auto-trading risks include:\n' +
        '- Market volatility and unexpected price movements\n' +
        '- Technical issues (API downtime, connectivity problems)\n' +
        '- Incorrect settings or configuration errors\n' +
        '- Signal quality variations\n' +
        '- Exchange-specific risks (liquidation, fees)\n\n' +
        'Always start with small amounts and conservative settings.'
    )
    
    pdf.add_question(
        'Can I use VerzekAutoTrader in my country?',
        'VerzekAutoTrader is available worldwide, but YOU are responsible for ensuring cryptocurrency trading and auto-trading are legal in your jurisdiction. We do not provide legal advice.'
    )
    
    pdf.add_question(
        'Do you store my personal data?',
        'We store minimal data:\n' +
        '- Email address (for account access)\n' +
        '- Encrypted API keys (for trading)\n' +
        '- Trading settings and preferences\n' +
        '- Payment transaction IDs (for verification)\n\n' +
        'We NEVER store passwords in plain text or share your data with third parties.'
    )
    
    pdf.add_question(
        'What happens if VerzekAutoTrader shuts down?',
        'Your funds are always on YOUR exchange accounts - never with us. If we shut down, you\'ll still have full access to your funds on the exchanges. Simply log into your exchange accounts directly and manage your positions.'
    )
    
    pdf.add_question(
        'Can I request my data to be deleted?',
        'Yes. Under data protection regulations, you can request deletion of your account and all associated data by contacting support@verzektrader.com. This process is permanent and cannot be reversed.'
    )
    
    # Final Page - Contact and Disclaimer
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(26, 154, 170)
    pdf.cell(0, 10, 'Still Have Questions?', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 7, 'Our support team is here to help!', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(5)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(249, 199, 79)
    pdf.cell(0, 7, 'Email: support@verzektrader.com', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.cell(0, 7, 'Telegram: @VerzekSupport', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(15)
    
    # Disclaimer
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 5, 
        'DISCLAIMER: Cryptocurrency trading carries significant risk of loss. VerzekAutoTrader is a software tool ' +
        'and does not provide financial advice. Past performance does not guarantee future results. You are solely ' +
        'responsible for your trading decisions and outcomes. Only trade with capital you can afford to lose. ' +
        'VerzekAutoTrader, its owners, and employees are not liable for any trading losses incurred while using this platform.',
        new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C'
    )
    
    # Save the PDF
    output_file = 'VerzekAutoTrader_FAQ.pdf'
    pdf.output(output_file)
    print(f'✅ FAQ PDF generated successfully: {output_file}')
    return output_file

if __name__ == '__main__':
    generate_faq_pdf()
