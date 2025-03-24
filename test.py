import os
import asyncio
import base64
import mimetypes
from email.message import EmailMessage
import aiosmtplib

from packages.backend.libs.config.email_sender_config import email_config

# Замените на свои реальные значения SMTP
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="voyager.group.inbound@gmail.com"
SMTP_PASSWORD="bacykezpwrxyuldn"

# async def send_email(to_email: str, subject: str, body: str, attachments: list):
#     """
#     :param to_email: адрес получателя
#     :param subject: тема письма
#     :param body: основной текст (будет и в plain, и в html)
#     :param attachments: список словарей [{"data": bytes, "filename": "image1.png"}, ...]
#     """
#     # Создаем письмо
#     message = EmailMessage()
#     message["Subject"] = subject
#     message["From"] = SMTP_USER
#     message["To"] = to_email
#
#     # 1) Пишем plain-текст
#     message.set_content(body)
#
#     # 2) Готовим HTML-версию c inline-изображениями (через base64)
#     html_body = f"<p>{body}</p>"
#
#     # Сюда будем накапливать НЕ изображение, чтобы прикрепить их отдельными вложениями
#     non_image_attachments = []
#
#     # Разбираем файлы
#     for attach in attachments:
#         file_bytes = attach["data"]
#         filename = attach["filename"]
#
#         # Узнаём MIME-тип
#         mime_type, _ = mimetypes.guess_type(filename)
#         if not mime_type:
#             mime_type = "application/octet-stream"
#         maintype, subtype = mime_type.split("/", 1)
#
#         if maintype == "image":
#             # Кодируем для вставки в <img src="data:..."> внутри HTML
#             encoded_attachment = base64.b64encode(file_bytes).decode("utf-8")
#
#             # Добавляем <img> в тело HTML
#             html_body += f"""
#             <div style="text-align: center; margin-bottom: 20px;">
#                 <img src="data:{mime_type};base64,{encoded_attachment}"
#                      alt="{filename}"
#                      style="max-width: 100%; height: auto; display: block; margin: auto;">
#             </div>
#             """
#             # Если нужно прикрепить эту же картинку как отдельный файл –
#             # НЕ вызываем `add_attachment` сейчас (это сломает последовательность).
#             # Запомним ее во временный список.
#             non_image_attachments.append((file_bytes, maintype, subtype, filename))
#         else:
#             # Это не картинка, прикрепим позже (точно так же)
#             non_image_attachments.append((file_bytes, maintype, subtype, filename))
#
#     # 3) Добавляем HTML-версию письма как "альтернативу" plain-тексту
#     html_full = f"<html><body>{html_body}</body></html>"
#     message.add_alternative(html_full, subtype="html")
#     # До этого момента письмо будет "multipart/alternative"
#
#     # 4) Теперь добавим все файлы как вложения (топовый уровень станет multipart/mixed)
#     for file_bytes, maintype, subtype, filename in non_image_attachments:
#         message.add_attachment(
#             file_bytes,
#             maintype=maintype,
#             subtype=subtype,
#             filename=filename
#         )
#
#     # 5) Отправка
#     try:
#         await aiosmtplib.send(
#             message,
#             hostname=SMTP_HOST,
#             port=SMTP_PORT,
#             username=SMTP_USER,
#             password=SMTP_PASSWORD,
#             use_tls=False,  # True если нужен SSL на 465
#             start_tls=True  # Обычный вариант для 587
#         )
#         print("Письмо успешно отправлено!")
#     except Exception as e:
#         print("Ошибка при отправке:", e)
#
#

import mimetypes
import aiosmtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

async def send_email(to_email: str, subject: str, body: str, attachments: list):
    msg = MIMEMultipart("mixed")
    msg["From"] = email_config.smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject

    # Контейнер для inline-картинок + HTML
    related = MIMEMultipart("related")

    # Внутри related будет «multipart/alternative» (plain + html)
    alternative = MIMEMultipart("alternative")

    # 1) Добавляем текст в формате plain
    alternative.attach(MIMEText(body, "plain", _charset="utf-8"))

    # 2) HTML-версия (сюда будут подшиваться изображения через cid)
    html_body = f"<html><body><p>{body}</p>"

    inline_images = []      # список для изображений inline
    other_attachments = []  # список для обычных вложений

    # 3) Разбираем attachments
    for idx, attachment in enumerate(attachments):
        file_bytes = attachment["data"]
        filename = attachment["filename"]

        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = "application/octet-stream"

        maintype, subtype = mime_type.split("/", 1)

        if maintype == "image":
            # (A) Создаём MIMEImage для inline
            image_part = MIMEImage(file_bytes, _subtype=subtype)
            cid = f"image_{idx}"

            # Заголовки для inline
            image_part.add_header("Content-ID", f"<{cid}>")
            image_part.add_header("Content-Disposition", "inline", filename=filename)

            inline_images.append(image_part)

            # Вставляем эту картинку в HTML через cid
            html_body += (
                f'<div style="text-align: center; margin-bottom: 20px;">'
                f'<img src="cid:{cid}" alt="{filename}" '
                f'style="max-width: 100%; height: auto; display: block; margin: auto;">'
                f'</div>'
            )

            # (B) Параллельно добавляем то же изображение в общий список вложений
            #     чтобы оно приходило и как «отдельный файл» вложений.
            other_attachments.append((file_bytes, maintype, subtype, filename))
        else:
            # Если это не картинка – просто как обычное вложение
            other_attachments.append((file_bytes, maintype, subtype, filename))

    # Закрываем HTML
    html_body += "</body></html>"

    # 4) Добавляем HTML-версию в «multipart/alternative»
    alternative.attach(MIMEText(html_body, "html", _charset="utf-8"))

    # 5) Кладём alternative (текст + html) в related
    related.attach(alternative)

    # 6) Добавляем inline-картинки в related
    for image_part in inline_images:
        related.attach(image_part)

    # 7) Прикрепляем related к корневому msg (mixed)
    msg.attach(related)

    # 8) Прикрепляем все «обычные» вложения (включая копии картинок)
    for file_bytes, maintype, subtype, filename in other_attachments:
        part = MIMEApplication(file_bytes, _subtype=subtype)
        part.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(part)

    # 9) Отправка
    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            use_tls=False,
            start_tls=True
        )
    except Exception as e:
        return e


async def main():
    # Список имён файлов, которые хотим отправить
    filenames = ["image1.png", "image2.png", "image3.png"]

    # Папка, где лежат файлы
    folder_path = "files"

    attachments = []
    for filename in filenames:
        path = os.path.join(folder_path, filename)
        if os.path.exists(path):
            with open(path, "rb") as f:
                file_bytes = f.read()
            attachments.append({"data": file_bytes, "filename": filename})
        else:
            print(f"Файл '{filename}' не найден, пропускаем...")

    await send_email(
        to_email="dastiw1910@gmail.com",
        subject="Тест: несколько файлов + inline-картинки",
        body="Здравствуйте, это тест.\nНиже будут картинки и вложения.",
        attachments=attachments
    )

if __name__ == "__main__":
    asyncio.run(main())





