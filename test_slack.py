from notification import send_slack_notification
import os

# Test Slack notification
def test_slack():
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if webhook_url:
        send_slack_notification("Hello from ComplianceBot!", webhook_url)
        print("Slack notification sent successfully!")
    else:
        print("SLACK_WEBHOOK_URL environment variable not set")

if __name__ == "__main__":
    test_slack()