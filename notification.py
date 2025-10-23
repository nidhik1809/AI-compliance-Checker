import smtplib
import requests
from email.mime.text import MIMEText

def send_notification(subject, notification):
    try:
        sender = ""
        password = ""   # Put your app password here
        receiver = ""

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
