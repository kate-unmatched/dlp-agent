# train_file_classifier.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# Путь для сохранения модели
MODEL_OUTPUT_PATH = os.path.join("ml", "file_content_model.pkl")

# Путь к CSV-файлу с размеченными данными
DATASET_PATH = "datasets/file_dataset.csv"  # ожидается CSV: text, label


def train_model():
    # Загрузка и проверка данных
    df = pd.read_csv(DATASET_PATH)
    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("Ожидаются колонки 'text' и 'label' в файле CSV")

    # Делим на обучающую и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    # Создаём пайплайн TF-IDF + RandomForest
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=3000, ngram_range=(1, 2))),
        ("clf", RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    # Обучение
    pipeline.fit(X_train, y_train)

    # Оценка
    y_pred = pipeline.predict(X_test)
    print("\n📊 Отчёт по классификации:\n")
    print(classification_report(y_test, y_pred))

    # Сохранение модели
    joblib.dump(pipeline, MODEL_OUTPUT_PATH)
    print(f"\n✅ Модель сохранена в: {MODEL_OUTPUT_PATH}")


if __name__ == "__main__":
    train_model()
