# ml/file_classifier.py

import joblib
import os

# Путь до модели (можно настроить через config.py)
MODEL_PATH = "C:/Projects/dlp-agent/features/file_work/ml/file_content_model.pkl"

# Загрузка модели при импорте
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    model = None
    print("⚠️ Модель классификации файлов не найдена:", MODEL_PATH)

def classify_document(text: str) -> dict:
    """
    Классифицирует текст документа как чувствительный или нет.

    Возвращает словарь с:
    - file_confidentiality_score: float (максимальная вероятность)
    - file_class_label: int (предсказанный класс)
    """
    if model is None or not text.strip():
        return {
            "file_confidentiality_score": 0.0,
            "file_class_label": 0
        }

    try:
        prediction = model.predict([text])[0]
        probabilities = model.predict_proba([text])[0]
        return {
            "file_confidentiality_score": round(float(max(probabilities)), 3),
            "file_class_label": int(prediction)
        }
    except Exception as e:
        print(f"⚠️ Ошибка при классификации документа: {e}")
        return {
            "file_confidentiality_score": 0.0,
            "file_class_label": 0
        }
