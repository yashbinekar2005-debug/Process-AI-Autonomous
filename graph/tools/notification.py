import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
from config import settings

def send_slack_message(message: str) -> str:
    """
    Sends a notification to a Slack webhook channel.
    
    Args:
        message (str): Message text.
        
    Returns:
        str: Response status message.
    """
    if not settings.SLACK_WEBHOOK_URL or settings.SLACK_WEBHOOK_URL == "":
        print(f"[MOCK SLACK NOTIFICATION]: {message}")
        return f"Slack message simulated successfully: '{message}' (Configure SLACK_WEBHOOK_URL for real delivery)"
    
    try:
        payload = {"text": message}
        response = httpx.post(settings.SLACK_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            return "Slack notification sent successfully."
        else:
            return f"Failed to send Slack message. Status Code: {response.status_code}. Response: {response.text}"
    except Exception as e:
        return f"Error sending Slack notification: {str(e)}"

def send_email(subject: str, body: str) -> str:
    """
    Sends an email notification using SMTP configuration.
    
    Args:
        subject (str): Email subject.
        body (str): Email body text.
        
    Returns:
        str: Response status message.
    """
    if not settings.SMTP_USER or settings.SMTP_PASSWORD == "":
        print(f"[MOCK EMAIL NOTIFICATION]\nTo: {settings.EMAIL_TO}\nSubject: {subject}\nBody:\n{body}")
        return f"Email simulated successfully to {settings.EMAIL_TO} with subject: '{subject}'"
        
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USER
        msg['To'] = settings.EMAIL_TO
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            
        return f"Email sent successfully to {settings.EMAIL_TO}."
    except Exception as e:
        return f"Error sending email: {str(e)}"
