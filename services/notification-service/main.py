"""
Notification Service - Phase V Cloud-Native Architecture

This microservice consumes reminder events from Kafka (via Dapr Pub/Sub)
and sends notifications to users about upcoming due tasks.

Responsibilities:
- Consume events from 'reminders' Kafka topic
- Send email/push notifications to users
- Track notification delivery status
- Handle notification failures gracefully

Dependencies:
- Dapr (for Pub/Sub)
- Kafka (via Redpanda Cloud)
- Email service (e.g., SendGrid, AWS SES)
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any

from cloudevents.sdk.event import v1
from dapr.ext.grpc import App

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_PUBSUB_NAME = "kafka-pubsub"
REMINDER_TOPIC = "reminders"
DAPR_APP_PORT = int(os.getenv("DAPR_APP_PORT", "50051"))

# Email configuration (placeholder - integrate with real service)
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@todoapp.com")

# Create Dapr App
app = App()


def send_email_notification(user_id: str, subject: str, body: str) -> bool:
    """
    Send email notification to user.

    Args:
        user_id: User ID (would map to email address)
        subject: Email subject
        body: Email body

    Returns:
        True if sent successfully, False otherwise
    """
    if not EMAIL_ENABLED:
        logger.info(f"Email disabled. Would send to {user_id}: {subject}")
        return True

    try:
        # TODO: Integrate with real email service (SendGrid, AWS SES, etc.)
        # Example with SendGrid:
        # sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
        # from_email = Email(EMAIL_FROM)
        # to_email = To(get_user_email(user_id))
        # content = Content("text/html", body)
        # mail = Mail(from_email, to_email, subject, content)
        # response = sg.client.mail.send.post(request_body=mail.get())

        logger.info(f"✉️  Sent email to {user_id}: {subject}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {user_id}: {e}")
        return False


def send_push_notification(user_id: str, title: str, body: str) -> bool:
    """
    Send push notification to user's devices.

    Args:
        user_id: User ID
        title: Notification title
        body: Notification body

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # TODO: Integrate with push notification service (FCM, APNS, OneSignal, etc.)
        # Example with Firebase Cloud Messaging:
        # message = messaging.Message(
        #     notification=messaging.Notification(
        #         title=title,
        #         body=body
        #     ),
        #     token=get_user_fcm_token(user_id)
        # )
        # response = messaging.send(message)

        logger.info(f"📱 Sent push notification to {user_id}: {title}")
        return True

    except Exception as e:
        logger.error(f"Failed to send push notification to {user_id}: {e}")
        return False


def format_due_date(due_date_str: str) -> str:
    """
    Format due date for human-readable display.

    Args:
        due_date_str: ISO format datetime string

    Returns:
        Formatted date string
    """
    try:
        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        return due_date.strftime("%B %d, %Y at %I:%M %p")
    except Exception:
        return due_date_str


@app.subscribe(pubsub_name=DAPR_PUBSUB_NAME, topic=REMINDER_TOPIC)
def handle_reminder(event: Any) -> Dict[str, str]:
    """
    Handle reminder event from Kafka.

    This function is called by Dapr when a new message arrives on the 'reminders' topic.

    Args:
        event: Event data from Dapr

    Returns:
        Dict with status key indicating success or failure
    """
    try:
        # Parse event data
        if isinstance(event, bytes):
            event_data = json.loads(event.decode('utf-8'))
        elif isinstance(event, str):
            event_data = json.loads(event)
        else:
            event_data = event

        user_id = event_data.get("user_id")
        task_id = event_data.get("task_id")
        title = event_data.get("title")
        description = event_data.get("description", "")
        due_date = event_data.get("due_date")
        priority = event_data.get("priority", "medium")
        tags = event_data.get("tags", [])

        logger.info(f"📬 Received reminder event for task {task_id} (user: {user_id})")

        # Format notification content
        formatted_date = format_due_date(due_date)

        # Priority emoji
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")

        # Email subject
        email_subject = f"⏰ Reminder: {title}"

        # Email body
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>{priority_emoji} Task Reminder</h2>
            <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px;">
                <h3>{title}</h3>
                {f'<p>{description}</p>' if description else ''}
                <p><strong>Due:</strong> {formatted_date}</p>
                <p><strong>Priority:</strong> {priority.upper()}</p>
                {f'<p><strong>Tags:</strong> {", ".join(tags)}</p>' if tags else ''}
            </div>
            <p style="color: #666; font-size: 12px; margin-top: 20px;">
                This is an automated reminder from your Todo app.
            </p>
        </body>
        </html>
        """

        # Push notification body
        push_body = f"Due {formatted_date}"
        if description:
            push_body += f" - {description[:50]}..."

        # Send notifications
        email_sent = send_email_notification(user_id, email_subject, email_body)
        push_sent = send_push_notification(user_id, f"{priority_emoji} {title}", push_body)

        if email_sent or push_sent:
            logger.info(f"✅ Successfully sent reminder for task {task_id}")
            return {"status": "SUCCESS"}
        else:
            logger.error(f"❌ Failed to send any notifications for task {task_id}")
            # Return SUCCESS to avoid retrying (notifications are best-effort)
            return {"status": "SUCCESS"}

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse event data: {e}")
        return {"status": "DROP"}

    except Exception as e:
        logger.error(f"Error handling reminder event: {e}")
        # Retry on unexpected errors
        return {"status": "RETRY"}


@app.subscribe(pubsub_name=DAPR_PUBSUB_NAME, topic="task-events")
def handle_task_event(event: Any) -> Dict[str, str]:
    """
    Handle task events for potential notification triggers.

    This could be used for:
    - Notifying when a task is assigned
    - Notifying when a task is completed
    - Notifying when a task is overdue

    Args:
        event: Event data from Dapr

    Returns:
        Dict with status key indicating success or failure
    """
    try:
        # Parse event data
        if isinstance(event, bytes):
            event_data = json.loads(event.decode('utf-8'))
        elif isinstance(event, str):
            event_data = json.loads(event)
        else:
            event_data = event

        event_type = event_data.get("event_type")

        logger.debug(f"Received task event: {event_type}")

        # Can add custom notification logic here
        # For now, just acknowledge the event
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error handling task event: {e}")
        return {"status": "DROP"}


def main():
    """Start the Dapr gRPC app server."""
    logger.info(f"🚀 Starting Notification Service on port {DAPR_APP_PORT}")
    logger.info(f"📡 Listening to Kafka topic: {REMINDER_TOPIC}")
    logger.info(f"📧 Email notifications: {'enabled' if EMAIL_ENABLED else 'disabled (simulation mode)'}")

    try:
        app.run(DAPR_APP_PORT)
    except KeyboardInterrupt:
        logger.info("Shutting down Notification Service...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
