#!/usr/bin/env python3
"""
VerzekAutoTrader Email Service Test & Diagnostic Tool
-------------------------------------------------------
Run this script on your Vultr server to test and diagnose email service issues.

Usage:
    python3 test_email_service.py
"""

import os
import sys
import smtplib
import socket
import ssl
from email.mime.text import MIMEText

# ANSI color codes for pretty output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")

def test_port_connectivity():
    """Test if SMTP ports are accessible"""
    print_header("STEP 1: Testing SMTP Port Connectivity")
    
    ports = [587, 25, 465]
    host = "smtp.office365.com"
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print_success(f"Port {port} is OPEN and accessible")
            else:
                print_error(f"Port {port} is BLOCKED or unreachable")
        except Exception as e:
            print_error(f"Port {port} test failed: {str(e)}")
    
    print_info("If ports are blocked, open a Vultr support ticket to request access")

def check_environment_variables():
    """Check if required environment variables are set"""
    print_header("STEP 2: Checking Environment Variables")
    
    required_vars = {
        'EMAIL_HOST': 'smtp.office365.com',
        'EMAIL_PORT': '587',
        'EMAIL_USER': 'support@verzekinnovative.com',
        'EMAIL_PASS': 'Your app password',
        'EMAIL_FROM': 'support@verzekinnovative.com'
    }
    
    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == 'EMAIL_PASS':
                print_success(f"{var} is set (hidden for security)")
            else:
                print_success(f"{var} = {value}")
        else:
            print_error(f"{var} is NOT set (expected: {description})")
            all_set = False
    
    if not all_set:
        print_warning("\nTo set variables, add them to .env file or ~/.bashrc")
        print_info("Example: export EMAIL_USER='support@verzekinnovative.com'")
    
    return all_set

def test_smtp_connection():
    """Test SMTP connection and authentication"""
    print_header("STEP 3: Testing SMTP Connection & Authentication")
    
    email_host = os.getenv('EMAIL_HOST', 'smtp.office365.com')
    email_port = int(os.getenv('EMAIL_PORT', '587'))
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    
    if not email_user or not email_pass:
        print_error("EMAIL_USER and EMAIL_PASS must be set!")
        return False
    
    try:
        print_info(f"Connecting to {email_host}:{email_port}...")
        
        # Create SMTP connection
        server = smtplib.SMTP(email_host, email_port, timeout=10)
        print_success("Connected to SMTP server")
        
        # Start TLS
        print_info("Starting TLS encryption...")
        context = ssl.create_default_context()
        server.starttls(context=context)
        print_success("TLS encryption established")
        
        # Authenticate
        print_info("Authenticating...")
        server.login(email_user, email_pass)
        print_success(f"Authentication successful for {email_user}")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print_error(f"Authentication failed: {str(e)}")
        print_warning("Check your app password (no spaces, 16 characters)")
        print_warning("Ensure SMTP AUTH is enabled for the mailbox")
        print_warning("Try disabling Security Defaults in Microsoft 365")
        return False
        
    except smtplib.SMTPConnectError as e:
        print_error(f"Connection failed: {str(e)}")
        print_warning("Port 587 may be blocked by Vultr")
        return False
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def send_test_email():
    """Send a test email"""
    print_header("STEP 4: Sending Test Email")
    
    email_host = os.getenv('EMAIL_HOST', 'smtp.office365.com')
    email_port = int(os.getenv('EMAIL_PORT', '587'))
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    email_from = os.getenv('EMAIL_FROM', email_user)
    
    if not email_user or not email_pass:
        print_error("EMAIL_USER and EMAIL_PASS must be set!")
        return False
    
    # Get recipient email from user
    print_info("Enter recipient email address for test:")
    recipient = input(f"{BOLD}To: {RESET}").strip()
    
    if not recipient or '@' not in recipient:
        print_error("Invalid email address")
        return False
    
    try:
        # Create message
        msg = MIMEText('<h1>✅ Success!</h1><p>Your Vultr email service is working correctly!</p><p>Sent from VerzekAutoTrader</p>', 'html')
        msg['Subject'] = 'Verzek Auto Trader: Email Test Successful'
        msg['From'] = email_from
        msg['To'] = recipient
        
        # Send email
        print_info(f"Sending test email to {recipient}...")
        
        context = ssl.create_default_context()
        with smtplib.SMTP(email_host, email_port, timeout=10) as server:
            server.starttls(context=context)
            server.login(email_user, email_pass)
            server.send_message(msg)
        
        print_success(f"Test email sent successfully to {recipient}")
        print_info("Check your inbox (and spam folder)")
        return True
        
    except Exception as e:
        print_error(f"Failed to send email: {str(e)}")
        return False

def test_mail_sender_module():
    """Test the mail_sender.py module"""
    print_header("STEP 5: Testing mail_sender.py Module")
    
    try:
        # Try to import mail_sender
        sys.path.insert(0, os.getcwd())
        from mail_sender import send_email, send_verification_email
        print_success("mail_sender.py module imported successfully")
        
        # Get recipient email
        print_info("Enter recipient email for verification code test:")
        recipient = input(f"{BOLD}To: {RESET}").strip()
        
        if recipient and '@' in recipient:
            print_info("Sending verification code email...")
            send_verification_email(recipient, "123456", "Test User")
            print_success("Verification email sent! Check your inbox.")
        
        return True
        
    except ImportError:
        print_warning("mail_sender.py not found in current directory")
        print_info("Make sure you're running this from the project directory")
        return False
        
    except Exception as e:
        print_error(f"Error testing mail_sender: {str(e)}")
        return False

def show_next_steps(results):
    """Show next steps based on test results"""
    print_header("Summary & Next Steps")
    
    all_passed = all(results.values())
    
    if all_passed:
        print_success("All tests passed! Email service is fully operational! 🎉")
        print_info("\nNext steps:")
        print("  1. Test from mobile app (register new user)")
        print("  2. Try password reset functionality")
        print("  3. Monitor email logs for any issues")
    else:
        print_warning("Some tests failed. Follow the recommendations above.")
        print_info("\nCommon fixes:")
        print("  1. Request SMTP port access from Vultr support")
        print("  2. Create app password in Microsoft 365")
        print("  3. Set environment variables correctly")
        print("  4. Disable Security Defaults in Microsoft 365")
        
        print_info("\nDetailed guide: See VULTR_EMAIL_SETUP_GUIDE.md")

def main():
    """Run all diagnostic tests"""
    print(f"{BOLD}{GREEN}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     VerzekAutoTrader Email Service Diagnostic Tool       ║")
    print("║                                                           ║")
    print("║  This tool will test your email configuration and help   ║")
    print("║  identify issues with Microsoft 365 SMTP setup           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{RESET}\n")
    
    results = {}
    
    # Run tests
    test_port_connectivity()
    
    results['env_vars'] = check_environment_variables()
    
    if results['env_vars']:
        results['smtp_connection'] = test_smtp_connection()
        
        if results['smtp_connection']:
            results['test_email'] = send_test_email()
            results['mail_sender'] = test_mail_sender_module()
        else:
            results['test_email'] = False
            results['mail_sender'] = False
    else:
        results['smtp_connection'] = False
        results['test_email'] = False
        results['mail_sender'] = False
    
    show_next_steps(results)
    
    print(f"\n{BOLD}Diagnostic complete!{RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test cancelled by user{RESET}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
