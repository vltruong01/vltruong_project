from __future__ import annotations

from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .utils import normalize_text


@dataclass(frozen=True)
class LegacyAnswer:
    answer: str
    confidence: float
    type: str
    sources: List[Dict[str, str]]


class LegacyProfileMatcher:
    def __init__(self, profile_path: Path) -> None:
        self.profile_path = profile_path
        self.profile: Dict[str, Any] = {}
        self.intents: Dict[str, Dict[str, Any]] = {}
        self.qa_by_lang: Dict[str, List[Tuple[str, str]]] = {"vi": [], "en": []}
        self._load()

    def _load(self) -> None:
        if not self.profile_path.exists():
            return
        self.profile = json.loads(self.profile_path.read_text(encoding="utf-8"))
        self.intents = {
            intent["name"]: intent
            for intent in self.profile.get("intents", [])
            if intent.get("name")
        }
        for item in self.profile.get("qa", []):
            for lang in ("vi", "en"):
                localized = item.get(lang, {})
                question = localized.get("q")
                answer = localized.get("a")
                if question and answer:
                    self.qa_by_lang[lang].append((question, answer))

    def answer(self, question: str, lang: str = "vi") -> LegacyAnswer | None:
        lang = "en" if lang == "en" else "vi"
        exact = self._exact_qa(question, lang)
        if exact:
            return LegacyAnswer(
                answer=exact,
                confidence=1.0,
                type="faq",
                sources=[self._source("FAQ", "profile")],
            )

        intent_name = self._match_intent(question)
        if intent_name:
            answer = self._answer_for_intent(intent_name, lang)
            if answer:
                return LegacyAnswer(
                    answer=answer,
                    confidence=0.95,
                    type="intent",
                    sources=[self._source(intent_name, "profile")],
                )
        return None

    def fallback(self, lang: str = "vi") -> str:
        lang = "en" if lang == "en" else "vi"
        default = {
            "vi": "Mình chưa có đủ thông tin để trả lời câu hỏi này.",
            "en": "I do not have enough information to answer this question.",
        }
        return self.profile.get("fallback", {}).get(lang, default[lang])

    def _exact_qa(self, question: str, lang: str) -> str:
        normalized_question = normalize_text(question)
        for stored_question, answer in self.qa_by_lang.get(lang, []):
            if normalize_text(stored_question) == normalized_question:
                return answer
        return ""

    def _match_intent(self, question: str) -> str:
        normalized_question = f" {normalize_text(question)} "
        for intent_name, intent in self.intents.items():
            keywords = intent.get("keywords", {})
            for lang_keywords in keywords.values():
                for keyword in lang_keywords:
                    normalized_keyword = normalize_text(keyword)
                    if not normalized_keyword:
                        continue
                    if " " in normalized_keyword:
                        if f" {normalized_keyword} " in normalized_question:
                            return intent_name
                    elif re.search(rf"(?:^|\W){re.escape(normalized_keyword)}(?:$|\W)", normalized_question):
                        return intent_name
        return ""

    def _answer_for_intent(self, intent_name: str, lang: str) -> str:
        answer = self.intents.get(intent_name, {}).get("answer", {})
        if isinstance(answer, dict):
            return answer.get(lang) or answer.get("vi") or answer.get("en") or ""
        if isinstance(answer, str):
            return answer
        return ""

    def _source(self, title: str, category: str) -> Dict[str, str]:
        return {
            "title": title,
            "category": category,
            "source": self.profile_path.as_posix(),
        }
