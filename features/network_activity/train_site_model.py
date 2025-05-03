
# features/network_activity/train_site_model.py

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

MODEL_PATH = "models/site_risk_model.pkl"
DATASET_PATH = "models/semantic_site_dataset_realistic.csv"

def train_semantic_model(path=MODEL_PATH):
    df = pd.read_csv(DATASET_PATH)

    X = df["text"]
    y = df["label"]

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=1000)),
        ("clf", LogisticRegression(max_iter=1000, random_state=42))
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipeline.fit(X_train, y_train)

    from sklearn.metrics import classification_report
    y_pred = pipeline.predict(X_test)
    report = classification_report(y_test, y_pred, digits=3)
    print("Отчёт по метрикам модели")
    print(report)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(pipeline, path)
    print(f"✅ Модель сохранена в {path}")

if __name__ == "__main__":
    train_semantic_model()
