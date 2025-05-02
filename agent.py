# agent.py

import time
import requests
from config import USER_ID, SERVER_URL, SEND_INTERVAL
from features.file_work.file_activity import collect_file_features
from features.process_activity.processes_work import collect_process_features
from utils.system import get_timestamp


def send_to_server(features: dict):
    payload = {
        "user_id": USER_ID,
        "timestamp": get_timestamp(),
        "features": features  # <-- группы признаков
    }

    try:
        response = requests.post(SERVER_URL, json=payload, timeout=5)
        if response.status_code == 200:
            risk = response.json().get("risk_level")
            print(f"[{payload['timestamp']}] ✅ Отправлено → уровень риска: {risk}")
        else:
            print(f"[{payload['timestamp']}] ⚠️ Ошибка сервера: {response.status_code} → {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[{payload['timestamp']}] ❌ Ошибка соединения: {e}")


def main_loop():
    print("🗂️  Агент DLP: мониторинг файловой активности активен\n")

    while True:
        features = {
            # "file_activity": collect_file_features(),
            "process_activity": collect_process_features()
        }
        send_to_server(features)
        time.sleep(SEND_INTERVAL)


if __name__ == "__main__":
    main_loop()
