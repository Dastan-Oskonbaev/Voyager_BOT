from packages.backend.libs.database.database import Database
from packages.backend.libs.config.db_config import db_config

# Создаем глобальную переменную для экземпляра базы данных
db = Database(db_config.postgres_url)
