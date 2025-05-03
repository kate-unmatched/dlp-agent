# features/file_activity.py

import os
import time
import re
import json
from pathlib import Path
from config import SEND_INTERVAL
from utils.text_extraction import extract_text_from_file
from features.file_work.file_classifier import classify_document

WATCH_DIRS = [
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Downloads")
]

ARCHIVE_EXTENSIONS = [".zip", ".rar", ".7z"]
SENSITIVE_KEYWORDS = ["договор", "зарплата", "паспорт", "ИНН", "клиенты", "карта", "отчёт"]
CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
PASSPORT_REGEX = re.compile(r"\b\d{4}\s?\d{6}\b")

CACHE_FILE = os.path.expanduser("~/.dlp_filecache.json")

SYSTEM_DIRS = [
    "C:/Windows",
    "C:/Program Files",
    "C:/Program Files (x86)",
    "C:/ProgramData"
]

_state = {
    "file_create_count": 0,
    "file_update_count": 0,
    "file_delete_count": 0,
    "file_access_sensitive_docs": 0,
    "file_sensitive_word_matches": 0,
    "file_contains_card_number": 0,
    "file_contains_passport_data": 0,
    "file_confidentiality_score": 0.0,
    "archive_created_count": 0,
    "file_permission_changed_count": 0,
    "file_system_update_count": 0
}

def collect_file_features():
    reset_state()
    recent_files, current_file_map, current_perm_map = get_recent_files(WATCH_DIRS + SYSTEM_DIRS, last_seconds=SEND_INTERVAL)
    previous_file_map = load_file_cache()
    previous_perm_map = load_permission_cache()

    deleted_paths = set(previous_file_map.keys()) - set(current_file_map.keys())
    _state["file_delete_count"] = len(deleted_paths)

    confidences = []

    for path in recent_files:
        try:
            abs_path = os.path.abspath(path)
            is_now_writable = os.access(abs_path, os.W_OK)
            was_writable = previous_perm_map.get(abs_path)
            if was_writable is not None and was_writable != is_now_writable:
                print(f"🔒 Изменена доступность записи: {abs_path}")
                _state["file_permission_changed_count"] += 1
        except Exception:
            continue
        text = extract_text_from_file(path)
        if not text:
            continue

        match_count = sum(text.lower().count(kw) for kw in SENSITIVE_KEYWORDS)
        _state["file_sensitive_word_matches"] += match_count
        if match_count > 0:
            _state["file_access_sensitive_docs"] += 1

        classification = classify_document(text)
        confidences.append(classification["file_confidentiality_score"])

        if CARD_REGEX.search(text):
            _state["file_contains_card_number"] = 1
        if PASSPORT_REGEX.search(text):
            _state["file_contains_passport_data"] = 1

    if confidences:
        _state["file_confidentiality_score"] = round(sum(confidences) / len(confidences), 3)

    save_file_cache(current_file_map)
    save_permission_cache(current_perm_map)
    return dict(_state)

def get_recent_files(directories, last_seconds=30):
    now = time.time()
    files = []
    current_file_map = {}
    current_perm_map = {}

    for folder in directories:
        if not os.path.exists(folder):
            continue
        for path in Path(folder).rglob("*"):
            try:
                if not path.is_file():
                    continue

                file_path = str(path)
                abs_path = os.path.abspath(file_path)
                stat = path.stat()
                current_file_map[file_path] = stat.st_size
                current_perm_map[file_path] = os.access(abs_path, os.W_OK)

                stat = path.stat()
                modified_recently = now - stat.st_mtime <= last_seconds
                created_recently = now - stat.st_ctime <= last_seconds

                if modified_recently:
                    files.append(file_path)
                    if created_recently:
                        _state["file_create_count"] += 1
                    else:
                        _state["file_update_count"] += 1

                    if any(path.suffix.lower() == ext for ext in ARCHIVE_EXTENSIONS):
                        _state["archive_created_count"] += 1

                    if any(abs_path.lower().startswith(os.path.abspath(sd).lower()) for sd in SYSTEM_DIRS):
                        _state["file_system_update_count"] += 1

            except Exception:
                continue

    return files, current_file_map, current_perm_map

def reset_state():
    for key in _state:
        _state[key] = 0 if isinstance(_state[key], int) else 0.0

def load_permission_cache():
    path = CACHE_FILE.replace("filecache", "permcache")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_permission_cache(perm_map):
    path = CACHE_FILE.replace("filecache", "permcache")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(perm_map, f)
    except Exception:
        pass


def load_file_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_file_cache(file_map):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(file_map, f)
    except Exception:
        pass
