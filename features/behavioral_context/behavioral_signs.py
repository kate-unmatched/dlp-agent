# features/behavioral_context/behavioral_signs.py

import datetime
import pyperclip
import re

# Регулярки для чувствительных данных
CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PASSWORD_HINTS = [
    "password", "пароль", "pwd", "pass", "пароли", "паролчик", "123456", "qwerty", "letmein", "secret", "my_password", "admin", "login", "логин", "access"
]

WORK_HOURS = (8, 18)  # рабочие часы с 8:00 до 18:00 по умолчанию

_state = {
    "activity_outside_work_hours": 0,
    "activity_weekend_hours": 0,
    "clipboard_sensitive_matches": 0
}

def collect_behavioral_context():
    reset_state()
    now = datetime.datetime.now()

    # Проверка времени
    hour = now.hour
    weekday = now.weekday()  # 0 — понедельник, 6 — воскресенье

    if hour < WORK_HOURS[0] or hour >= WORK_HOURS[1]:
        _state["activity_outside_work_hours"] = 1

    if weekday >= 5:
        _state["activity_weekend_hours"] = 1

    # Проверка содержимого буфера обмена
    try:
        clip = pyperclip.paste()
        if clip:
            count = 0
            count += len(CARD_REGEX.findall(clip))
            count += len(EMAIL_REGEX.findall(clip))
            count += sum(1 for pw in PASSWORD_HINTS if pw in clip.lower())
            _state["clipboard_sensitive_matches"] = count
    except Exception:
        pass

    return dict(_state)


def reset_state():
    for key in _state:
        _state[key] = 0
