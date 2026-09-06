import random
import logging
from email.message import EmailMessage
import aiosmtplib
from app.config import settings

logger = logging.getLogger(__name__)

def generate_otp() -> str:
    """Generate a random 6-digit verification code."""
    return f"{random.randint(100000, 999999)}"

async def send_otp_email_async(email: str, otp_code: str):
    """Sends OTP verification email asynchronously using aiosmtplib."""
    # For local development convenience, log the OTP directly to console
    if settings.ENVIRONMENT == "local":
        logger.info(f"\n==================================================\n"
                    f"[LOCAL DEV] OTP Code for {email}: {otp_code}\n"
                    f"==================================================")

    message = EmailMessage()
    message["From"] = settings.SMTP_SENDER or settings.SMTP_USERNAME
    message["To"] = email
    message["Subject"] = "Klink AI - Your Verification OTP Code"
    message.set_content(
        f"Hello,\n\n"
        f"Your verification OTP code is: {otp_code}\n"
        f"It will expire in 5 minutes.\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Best regards,\n"
        f"Klink AI Team"
    )

    try:
        # We dynamically select TLS based on ports
        use_tls = (settings.SMTP_PORT == 465)
        start_tls = (settings.SMTP_PORT == 587)
        
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            use_tls=use_tls,
            start_tls=start_tls,
            timeout=10,
        )
        logger.info(f"OTP email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {e}")
