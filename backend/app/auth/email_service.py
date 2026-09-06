import aiosmtplib
from email.message import EmailMessage
from app.config import settings

async def send_email_async(to_email: str, subject: str, body: str):
    """
    Send an email asynchronously using aiosmtplib.
    """
    if not settings.SMTP_HOST or not settings.SMTP_USERNAME:
        print("SMTP config is missing, skipping real email send.")
        return

    message = EmailMessage()
    message["From"] = settings.SMTP_SENDER
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            use_tls=True if settings.SMTP_PORT == 465 else False,
            start_tls=True if settings.SMTP_PORT == 587 else False,
        )
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
