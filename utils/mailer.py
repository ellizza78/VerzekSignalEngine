import os, smtplib
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.zoho.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
FROM_NAME = os.getenv("FROM_NAME", "Verzek Innovative Solutions")

def send_test_email(to_email):
    msg = MIMEText("✅ Zoho SMTP test successful – VerzekAutoTrader connected.")
    msg["Subject"] = "SMTP Test"
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
    print(f"✅ Test email sent successfully to {to_email}")