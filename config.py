# config.py

# Уникальный идентификатор пользователя или рабочей станции
USER_ID = "user42"

# Адрес основного модуля (локальный HTTP-сервер Flask)
SERVER_URL = "http://127.0.0.1:8000/predict"

# Интервал между отправками данных (в секундах)
SEND_INTERVAL = 30

# Включить или отключить эмуляцию (если False — будет попытка реального сбора)
USE_SIMULATION = True

# Количество признаков и их имена (для генерации и отладки)
FEATURE_NAMES = [
    "file_operations",
    "http_requests",
    "usb_usage",
    "process_count",
    "websites_visited"
]
