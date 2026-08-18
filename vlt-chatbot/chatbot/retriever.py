from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np

from .knowledge import KnowledgeChunk
from .utils import normalize_text


STOPWORDS = {
    "ban",
    "cua",
    "toi",
    "minh",
    "la",
    "gi",
    "ve",
    "cac",
    "nhung",
    "the",
    "you",
    "your",
    "what",
    "are",
    "is",
    "do",
}

CATEGORY_ALIASES = {
    "about": {"ban la ai", "gioi thieu", "so thich", "tinh cach", "hometown"},
    "education": {"hoc van", "hoc", "truong", "university", "education", "major"},
    "skills": {"cong nghe", "ky nang", "tech", "technology", "technologies", "skill", "skills", "fastapi", "python"},
    "projects": {"du an", "project", "chatbot", "ai project"},
    "thesis": {"nghien cuu", "research", "researching", "thesis", "de tai"},
    "experience": {"kinh nghiem", "experience", "deploy", "fly.io"},
    "contact": {"lien he", "email", "phone", "contact", "sdt"},
    "certifications": {"chung chi", "certificate", "certification"},
    "lifestyle": {
        "de gan",
        "it noi",
        "lay loi",
        "lang xet",
        "nhat",
        "di choi",
        "du lich",
        "o nha",
        "danh bai",
        "nha o dau",
        "cang an thoi",
        "lifestyle",
        "friendly",
        "quiet",
        "travel",
        "stay home",
        "cards",
    },
    "favorites": {
        "banh cuon",
        "banh cuon nong",
        "ngay nay nam ay",
        "anime",
        "7 vien ngoc rong",
        "dragon ball",
        "mau yeu thich",
        "mau gi",
        "gu an mac",
        "hoc tai thi tach",
        "favorite",
        "song",
        "color",
        "fashion",
        "quote",
    },
}


@dataclass(frozen=True)
class RetrievalResult:
    chunk: KnowledgeChunk
    score: float


class SemanticRetriever:
    def __init__(
        self,
        chunks: List[KnowledgeChunk],
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        self.chunks = chunks
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name, device="cpu")
        self.embeddings = self._encode([self._text_for_embedding(chunk) for chunk in chunks])

    def _encode(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, 384), dtype=np.float32)
        return self.model.encode(
            texts,
            batch_size=16,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype(np.float32)

    @staticmethod
    def _text_for_embedding(chunk: KnowledgeChunk) -> str:
        return f"{chunk.title}\nCategory: {chunk.category}\n{chunk.content}"

    def search(self, query: str, top_k: int = 4) -> List[RetrievalResult]:
        if not query.strip() or not self.chunks:
            return []
        query_embedding = self._encode([query])[0]
        semantic_scores = np.matmul(self.embeddings, query_embedding)
        scores = np.array(
            [
                self._combined_score(query, chunk, float(score))
                for chunk, score in zip(self.chunks, semantic_scores)
            ],
            dtype=np.float32,
        )
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            RetrievalResult(chunk=self.chunks[int(index)], score=float(scores[int(index)]))
            for index in top_indices
        ]

    def _combined_score(self, query: str, chunk: KnowledgeChunk, semantic_score: float) -> float:
        lexical_score = self._lexical_score(query, chunk)
        alias_matched = self._alias_matched(query, chunk.category)
        if alias_matched:
            return min(1.0, (semantic_score * 0.50) + (lexical_score * 0.40) + 0.12)
        return min(1.0, (semantic_score * 0.70) + (lexical_score * 0.15))

    @staticmethod
    def _lexical_score(query: str, chunk: KnowledgeChunk) -> float:
        normalized_query = normalize_text(query)
        normalized_chunk = normalize_text(
            f"{chunk.title} {chunk.category} {chunk.content}"
        )
        query_tokens = {
            token for token in normalized_query.split() if len(token) > 2 and token not in STOPWORDS
        }
        if not query_tokens:
            return 0.0

        overlap = len(query_tokens.intersection(normalized_chunk.split())) / max(len(query_tokens), 1)
        alias_bonus = 1.0 if SemanticRetriever._alias_matched(query, chunk.category) else 0.0
        return min(1.0, (overlap * 0.75) + (alias_bonus * 0.25))

    @staticmethod
    def _alias_matched(query: str, category: str) -> bool:
        normalized_query = normalize_text(query)
        return any(alias in normalized_query for alias in CATEGORY_ALIASES.get(category, set()))


class LexicalRetriever:
    def __init__(self, chunks: List[KnowledgeChunk]) -> None:
        self.chunks = chunks

    def search(self, query: str, top_k: int = 4) -> List[RetrievalResult]:
        if not query.strip() or not self.chunks:
            return []

        scores = np.array(
            [SemanticRetriever._lexical_score(query, chunk) for chunk in self.chunks],
            dtype=np.float32,
        )
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            RetrievalResult(chunk=self.chunks[int(index)], score=float(scores[int(index)]))
            for index in top_indices
            if scores[int(index)] > 0
        ]
