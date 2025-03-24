import mimetypes
import aiosmtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

from packages.backend.libs.config.email_sender_config import email_config


async def send_email(to_email: str, subject: str, body: str, attachments: list):
    msg = MIMEMultipart("mixed")
    msg["From"] = email_config.smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject

    related = MIMEMultipart("related")

    alternative = MIMEMultipart("alternative")

    alternative.attach(MIMEText(body, "plain", _charset="utf-8"))

    html_body = f"<html><body><p>{body}</p>"

    inline_images = []
    other_attachments = []

    for idx, attachment in enumerate(attachments):
        file_bytes = attachment["data"]
        filename = attachment["filename"]

        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = "application/octet-stream"

        maintype, subtype = mime_type.split("/", 1)

        if maintype == "image":
            image_part = MIMEImage(file_bytes, _subtype=subtype)
            cid = f"image_{idx}"

            image_part.add_header("Content-ID", f"<{cid}>")
            image_part.add_header("Content-Disposition", "inline", filename=filename)

            inline_images.append(image_part)

            html_body += (
                f'<div style="text-align: center; margin-bottom: 20px;">'
                f'<img src="cid:{cid}" alt="{filename}" '
                f'style="max-width: 100%; height: auto; display: block; margin: auto;">'
                f'</div>'
            )
            other_attachments.append((file_bytes, maintype, subtype, filename))
        else:
            other_attachments.append((file_bytes, maintype, subtype, filename))

    html_body += "</body></html>"

    alternative.attach(MIMEText(html_body, "html", _charset="utf-8"))

    related.attach(alternative)

    for image_part in inline_images:
        related.attach(image_part)

    msg.attach(related)

    for file_bytes, maintype, subtype, filename in other_attachments:
        part = MIMEApplication(file_bytes, _subtype=subtype)
        part.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(part)
    try:
        await aiosmtplib.send(
            msg,
            hostname=email_config.smtp_host,
            port=email_config.smtp_port,
            username=email_config.smtp_user,
            password=email_config.smtp_password,
            use_tls=False,
            start_tls=True
        )
    except Exception as e:
        return e