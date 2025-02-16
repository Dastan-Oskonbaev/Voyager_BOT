import os

from dotenv import load_dotenv
from typing import NamedTuple

from packages.backend.libs.types.core_types import Environment


load_dotenv()


class CoreConfig(NamedTuple):
    environment: Environment
    port_main_api: int


core_config = CoreConfig(
    environment=os.getenv("ENVIRONMENT", Environment.DEVELOPMENT),  # 'development' | 'test' | 'production' | 'local'
    port_main_api=int(os.getenv("PORT_MAIN_API", '8000')),
)
