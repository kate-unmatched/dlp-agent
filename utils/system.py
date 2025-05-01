# utils/system.py

from datetime import datetime

def get_timestamp() -> str:
    """
    Возвращает текущее время в формате ISO 8601: YYYY-MM-DDTHH:MM:SS
    """
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
