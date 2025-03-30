# test_email.py
import smtplib
import ssl
from email.message import EmailMessage
import datetime

# --- IMPORTANT: REPLACE THESE ---
SENDER_EMAIL = 'peterbuics@gmail.com'
APP_PASSWORD = 'brha ylpr typt tusw' # Use the 16-digit App Password here
# --- IMPORTANT: REPLACE THESE ---

RECEIVER_EMAIL = SENDER_EMAIL # Sending email to yourself

# Create the email content
subject = "Test Email from Simple Python Script"
body = f"""
Hello,

This is a test email sent directly via smtplib using Python.
It confirms if the App Password authentication is working correctly.

Time: {datetime.datetime.now()}
"""

# Create an EmailMessage object
em = EmailMessage()
em['From'] = SENDER_EMAIL
em['To'] = RECEIVER_EMAIL
em['Subject'] = subject
em.set_content(body)

# Gmail SMTP server details
smtp_server = "smtp.gmail.com"
port = 465  # For SSL

# Add SSL layer
context = ssl.create_default_context()

print(f"Attempting to send email from {SENDER_EMAIL} to {RECEIVER_EMAIL}...")

server = None # Initialize server to None
try:
    # Connect to server and send email
    print(f"Connecting to {smtp_server} on port {port}...")
    # Using SMTP_SSL to establish a secure connection from the start
    server = smtplib.SMTP_SSL(smtp_server, port, context=context)
    print("Connected successfully.")

    print("Attempting to log in...")
    server.login(SENDER_EMAIL, APP_PASSWORD)
    print("Login successful!")

    print("Sending email...")
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, em.as_string())
    print("Email sent successfully!")

except smtplib.SMTPAuthenticationError as e:
    print(f"\n--- Authentication FAILED ---")
    print(f"Error code: {e.smtp_code}")
    print(f"Error message: {e.smtp_error}")
    print("\nPlease double-check:")
    print("1. Your SENDER_EMAIL is correct.")
    print("2. The APP_PASSWORD is the correct 16-digit password (no spaces).")
    print("3. 2-Step Verification is enabled for the SENDER_EMAIL account.")
    print("4. You generated the App Password correctly in Google Account settings.")

except Exception as e:
    print(f"\n--- An error occurred ---")
    print(e)

finally:
    if server:
        try:
            server.quit()
            print("Server connection closed.")
        except Exception as e:
            print(f"Error closing server connection: {e}")