import time

pending_photos = {}

def save_pending_photo(chat_id: int, photo_id: str, ttl: int = 300):
    """Сохраняем photo_id с ограниченным временем жизни (ttl секунд)."""
    pending_photos[chat_id] = {
        'photo_id': photo_id,
        'expires_at': time.time() + ttl
    }

def get_pending_photo(chat_id: int):
    """Получаем photo_id, если время не истекло."""
    data = pending_photos.get(chat_id)
    if not data:
        return None
    if data['expires_at'] < time.time():
        delete_pending_photo(chat_id)
        return None
    return data['photo_id']

def delete_pending_photo(chat_id: int):
    """Удаляем сохранённый photo_id для chat_id."""
    pending_photos.pop(chat_id, None)


pending_agents = {}

def save_pending_agent(chat_id: int, data: dict):
    pending_agents[chat_id] = data

def get_pending_agent(chat_id: int) -> dict:
    return pending_agents.get(chat_id)

def delete_pending_agent(chat_id: int):
    pending_agents.pop(chat_id, None)


pending_deletions = {}

def save_pending_deletion(chat_id: int, data: dict):
    pending_deletions[chat_id] = data

def get_pending_deletion(chat_id: int) -> dict:
    return pending_deletions.get(chat_id)

def delete_pending_deletion(chat_id: int):
    pending_deletions.pop(chat_id, None)