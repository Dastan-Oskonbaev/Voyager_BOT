import os

from dotenv import load_dotenv
from typing import NamedTuple


load_dotenv()


class TgConfig(NamedTuple):
    api_url: str
    bot_token: str
    password: str


tg_config = TgConfig(
    api_url='https://api.telegram.org',
    bot_token=os.getenv('TG_BOT_TOKEN'),
    password= os.getenv('PASSWORD')
)
