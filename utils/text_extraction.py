from pathlib import Path
import os

# .docx
try:
    from docx import Document
except ImportError:
    Document = None

# .pdf
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

def extract_text_from_file(path: str) -> str | None:
    """
    Универсальный интерфейс для извлечения текста из поддерживаемых типов файлов.
    """
    ext = Path(path).suffix.lower()
    try:
        if ext == ".txt":
            return extract_from_txt(path)
        elif ext == ".docx" and Document:
            return extract_from_docx(path)
        elif ext == ".pdf" and fitz:
            return extract_from_pdf(path)
        else:
            return None
    except Exception:
        return None


def extract_from_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_from_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_from_pdf(path: str) -> str:
    text = ""
    with fitz.open(path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text
