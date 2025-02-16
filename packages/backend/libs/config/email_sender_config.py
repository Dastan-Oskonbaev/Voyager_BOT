import os
from typing import NamedTuple

from dotenv import load_dotenv

load_dotenv()


class EmailConfig(NamedTuple):
    smtp_host: str
    smtp_port: str
    smtp_user: str
    smtp_password: str


email_config = EmailConfig(
    smtp_host=os.getenv('SMTP_HOST'),
    smtp_port=os.getenv('SMTP_PORT'),
    smtp_user= os.getenv('SMTP_USER'),
    smtp_password= os.getenv('SMTP_PASSWORD')
)
