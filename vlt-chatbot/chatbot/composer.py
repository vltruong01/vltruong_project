from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .retriever import RetrievalResult
from .utils import detect_language, normalize_text, split_sentences, unique_keep_order


UNKNOWN = {
    "vi": "Mình chưa có đủ thông tin để trả lời câu hỏi này.",
    "en": "I do not have enough information to answer this question.",
}


@dataclass(frozen=True)
class ChatAnswer:
    answer: str
    confidence: float
    type: str
    sources: List[Dict[str, str]]


class GroundedComposer:
    def __init__(self, min_confidence: float = 0.50, max_sentences: int = 5) -> None:
        self.min_confidence = min_confidence
        self.max_sentences = max_sentences

    def compose(self, question: str, results: List[RetrievalResult], lang: str = "vi") -> ChatAnswer:
        lang = detect_language(question, lang)
        confidence = round(max((result.score for result in results), default=0.0), 4)
        usable = [
            result
            for result in results
            if result.score >= self.min_confidence and result.score >= confidence * 0.78
        ]
        if not usable:
            return ChatAnswer(
                answer=UNKNOWN[lang],
                confidence=confidence,
                type="unknown",
                sources=[],
            )

        question_terms = set(normalize_text(question).split())
        selected: List[str] = []
        for result in usable:
            sentences = split_sentences(result.chunk.content)
            ranked = sorted(
                sentences,
                key=lambda sentence: len(question_terms.intersection(normalize_text(sentence).split())),
                reverse=True,
            )
            for sentence in ranked[:2]:
                if sentence:
                    selected.append(sentence)

        selected = unique_keep_order(selected)[: self.max_sentences]
        if not selected:
            selected = unique_keep_order(result.chunk.content for result in usable)[:2]

        answer = self._format_answer(selected, lang)
        sources = []
        seen = set()
        for result in usable:
            key = (result.chunk.title, result.chunk.category)
            if key not in seen:
                seen.add(key)
                sources.append(result.chunk.to_source())

        return ChatAnswer(
            answer=answer,
            confidence=confidence,
            type="semantic",
            sources=sources[:3],
        )

    @staticmethod
    def _format_answer(sentences: List[str], lang: str) -> str:
        if not sentences:
            return UNKNOWN[lang]
        prefix = "Dựa trên dữ liệu hiện có: " if lang == "vi" else "Based on the current knowledge base: "
        body = " ".join(sentence.strip() for sentence in sentences)
        return prefix + body
