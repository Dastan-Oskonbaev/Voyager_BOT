import time

pending_files = {}


def save_pending_file(chat_id: int, file_id: str, filename: str, ttl: int = 300):
    pending_files[chat_id] = {
        'file_id': file_id,
        'filename': filename,
        'expires_at': time.time() + ttl
    }


def get_pending_file(chat_id: int):
    data = pending_files.get(chat_id)
    if not data:
        return None
    if data['expires_at'] < time.time():
        delete_pending_file(chat_id)
        return None
    return data


def delete_pending_file(chat_id: int):
    pending_files.pop(chat_id, None)


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


pending_redactions = {}

def save_pending_redact(chat_id: int, data: dict):
    pending_redactions[chat_id] = data


def get_pending_redact(chat_id: int) -> dict:
    return pending_redactions.get(chat_id)


def delete_pending_redact(chat_id: int):
    pending_redactions.pop(chat_id, None)