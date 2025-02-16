# Используйте официальный образ Python
FROM python:3.12-alpine

# Установите переменную окружения для запуска в неинтерактивном режиме
ENV PYTHONPATH /app

# Пусть сервер работает в UTC зоне
ENV TZ="UTC"
ENV PYTHONUNBUFFERED=1

# Создайте и перейдите в рабочую директорию
WORKDIR /app

# Скопируйте зависимости (requirements.txt) в контейнер
COPY requirements.txt /app/

# Устанавливаем зависимости из файла
RUN pip install --no-cache-dir -r requirements.txt


# Копируем остальной код проекта в контейнер
COPY packages/backend/apps/ /app/packages/backend/apps/
COPY packages/backend/libs/ /app/packages/backend/libs/
COPY packages/backend/migrations/ /app/packages/backend/migrations/

EXPOSE 8000

CMD python migrations/run_migrations.py && python apps/tg_bot/main.py
