import aiosmtplib
import base64
import mimetypes

from email.message import EmailMessage

from packages.backend.libs.config.email_sender_config import email_config


async def send_email(to_email: str, subject: str, body: str, attachment: bytes, filename: str):
    message = EmailMessage()
    message["From"] = email_config.smtp_user
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type is None:
        mime_type = "application/octet-stream"
    maintype, subtype = mime_type.split("/", 1)

    if maintype == "image":
        # Если файл изображение, встраиваем его в HTML-сообщение
        encoded_attachment = base64.b64encode(attachment).decode('utf-8')
        html_body = f"""
            <html>
              <body>
                <p>{body}</p>
                <div style="text-align: center;">
                  <img src="data:{mime_type};base64,{encoded_attachment}" alt="{filename}" style="max-width: 100%; height: auto; display: block; margin: auto;">
                </div>
              </body>
            </html>
            """
        message.add_alternative(html_body, subtype="html")
    else:
        message.add_attachment(attachment, maintype=maintype, subtype=subtype, filename=filename)

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