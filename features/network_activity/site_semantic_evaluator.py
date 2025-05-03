# features/network_activity/site_semantic_evaluator.py

import requests
from bs4 import BeautifulSoup
import joblib
import numpy as np
import os

MODEL_PATH = "features/network_activity/models/site_risk_model.pkl"

try:
    model = joblib.load(MODEL_PATH)
except:
    model = None
    print("⚠️ Не удалось загрузить модель семантической оценки сайтов.")


def extract_text_from_site(url: str) -> str:
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title else ""
        headings = " ".join([h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])])
        paragraphs = " ".join([p.get_text(strip=True) for p in soup.find_all("p")])

        text = f"{title} {headings} {paragraphs}"
        return text.strip()
    except Exception:
        return ""


def evaluate_site_risk_semantic(url: str) -> float:
    if not model:
        return 0.0
    text = extract_text_from_site(url)
    if not text:
        return 0.0
    try:
        prob = model.predict_proba([text])[0][1]
        return round(prob, 3)
    except:
        return 0.0


def evaluate_multiple_sites(urls: list[str]) -> dict:
    result = {}
    for url in urls:
        score = evaluate_site_risk_semantic(url)
        result[url] = score
    avg_score = round(np.mean(list(result.values())), 3) if result else 0.0
    return {
        "site_semantic_risk_score": avg_score,
        "individual_scores": result
    }
