import re
import unicodedata
from typing import Iterable, List


def strip_diacritics(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_text(text: str) -> str:
    text = strip_diacritics(text or "").lower().strip()
    text = re.sub(r"[^\w\s@.+:/-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def detect_language(text: str, requested: str = "vi") -> str:
    if requested == "en":
        return "en"
    normalized = normalize_text(text)
    english_markers = {
        "what",
        "who",
        "where",
        "which",
        "how",
        "project",
        "skill",
        "education",
        "experience",
        "contact",
    }
    if any(word in normalized.split() for word in english_markers):
        return "en"
    return "vi"


def split_sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+|(?<=\.)\s+(?=[A-ZÀ-Ỵ])", text)
    return [part.strip(" -") for part in parts if part.strip(" -")]


def unique_keep_order(items: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        key = normalize_text(item)
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result
