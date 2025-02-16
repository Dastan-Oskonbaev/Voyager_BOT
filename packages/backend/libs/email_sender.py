import aiosmtplib

from email.message import EmailMessage

from packages.backend.libs.config.email_sender_config import email_config


async def send_email(to_email: str, subject: str, body: str, attachment: bytes, filename: str):
    message = EmailMessage()
    message["From"] = email_config.smtp_user
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    message.add_attachment(attachment, maintype="image", subtype="jpeg", filename=filename)

    try:
        await aiosmtplib.send(
            message,
            hostname=email_config.smtp_host,
            port=email_config.smtp_port,
            username=email_config.smtp_user,
            password=email_config.smtp_password,
            use_tls=False,
            start_tls=True
        )
    except Exception as e:
        return e