import smtplib
import requests
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()
pswd = os.getenv("pswd")
email1 = os.getenv("email1")
email2 = os.getenv("email2")

def send_notification(subject, notification):
    try:
        sender = email1
        password = pswd  # Put your app password here
        receiver = email2

        msg = MIMEText(f"{notification}")
        msg["Subject"] = subject
        msg["From"] = f"Nidhi <{sender}>"
        msg["To"] = receiver

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)

        print("Email sent Successfully!")

    except Exception as e:
        print("Error Occured", e)

def send_slack_notification(message, webhook_url):
    payload = {
        "text": message,
        "username": "ComplianceBot"
    }
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 200:
        print("Slack notification sent!")
    else:
        print(f"Slack notification failed with status {response.status_code}: {response.text}")
