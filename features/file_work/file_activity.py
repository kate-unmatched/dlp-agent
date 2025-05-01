# features/file_activity.py

import os
import time
from pathlib import Path
from collections import Counter

from config import SEND_INTERVAL
from utils.text_extraction import extract_text_from_file
from features.file_work.file_classifier import classify_document

# Папки, за которыми будем следить
WATCH_DIRS = [
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Downloads")
]

# Расширения для текстовых документов
DOC_EXTENSIONS = [".docx", ".txt", ".pdf", ".xlsx"]

# Ключевые слова
SENSITIVE_KEYWORDS = ["договор", "зарплата", "паспорт", "ИНН", "клиенты", "карта", "отчёт"]

# Статистика за текущий интервал
_state = {
    "file_create_count": 0,
    "file_delete_count": 0,
    "file_copy_count": 0,
    "file_rename_count": 0,
    "file_access_sensitive_docs": 0,
    "file_sensitive_word_matches": 0,
    "file_contains_card_number": 0,
    "file_contains_passport_data": 0,
    "file_confidentiality_score": 0.0,
    "file_class_label": 0,
    "total_data_written_MB": 0.0,
    "usb_file_copy_count": 0  # Пока заглушка
}


def collect_file_features():
    """
    Основная функция сбора файловых признаков.
    """
    reset_state()

    recent_files = get_recent_files(WATCH_DIRS, last_seconds=SEND_INTERVAL)
    sensitive_hits = 0
    max_conf_score = 0.0
    max_label = 0

    for path in recent_files:
        text = extract_text_from_file(path)
        if not text:
            continue

        # Ключевые слова
        match_count = sum(text.lower().count(kw) for kw in SENSITIVE_KEYWORDS)
        _state["file_sensitive_word_matches"] += match_count
        if match_count > 0:
            _state["file_access_sensitive_docs"] += 1

        # Модель классификации
        classification = classify_document(text)
        conf = classification["file_confidentiality_score"]
        label = classification["file_class_label"]

        if conf > max_conf_score:
            max_conf_score = conf
            max_label = label

        # Доп. шаблоны (регулярки можно вставить сюда)
        if "4" in text and "0000" in text:  # псевдопроверка для номера карты
            _state["file_contains_card_number"] = 1
        if "серия" in text and "номер" in text:  # псевдопаспорт
            _state["file_contains_passport_data"] = 1

    # Наиболее чувствительный документ определяет финальную оценку
    _state["file_confidentiality_score"] = round(max_conf_score, 3)
    _state["file_class_label"] = max_label

    return dict(_state)


def reset_state():
    for key in _state:
        _state[key] = 0 if isinstance(_state[key], int) else 0.0


def get_recent_files(directories, last_seconds=30):
    """
    Возвращает список файлов, созданных или изменённых за последние last_seconds.
    """
    now = time.time()
    files = []
    for folder in directories:
        if not os.path.exists(folder):
            continue
        for path in Path(folder).rglob("*"):
            try:
                if not path.is_file():
                    continue
                stat = path.stat()
                if now - stat.st_mtime <= last_seconds:
                    files.append(str(path))
                    _state["file_create_count"] += 1
                    # Здесь можно расширить: если имя содержит copy → count как копирование
            except Exception:
                continue
    return files
