import os

from dotenv import load_dotenv
from typing import NamedTuple


load_dotenv()


class DbConfig(NamedTuple):
    postgres_url: str


db_config = DbConfig(
    postgres_url=os.getenv('DB_PG_URL'),
)
