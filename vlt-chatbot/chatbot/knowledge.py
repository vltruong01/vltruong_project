from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import re
from typing import Dict, List


@dataclass(frozen=True)
class KnowledgeChunk:
    id: str
    title: str
    category: str
    content: str
    source: str

    def to_source(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "category": self.category,
            "source": self.source,
        }

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


def _clean_markdown(text: str) -> str:
    text = re.sub(r"^\s{0,3}#{1,6}\s+.+$", " ", text, flags=re.MULTILINE)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1: \2", text)
    text = re.sub(r"(?im)^\s*Vietnamese summary:\s*", "", text)
    text = re.sub(r"[*_>#]", " ", text)
    text = re.sub(r"\r\n?", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _title_from_markdown(text: str, fallback: str) -> str:
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}#{1,3}\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return fallback.replace("-", " ").replace("_", " ").title()


def _split_sections(markdown: str) -> List[str]:
    sections: List[str] = []
    current: List[str] = []
    for line in markdown.splitlines():
        if re.match(r"^\s{0,3}#{1,3}\s+", line) and current:
            sections.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current).strip())
    return [section for section in sections if section]


def _chunk_section(section: str, max_chars: int) -> List[str]:
    cleaned = _clean_markdown(section)
    if len(cleaned) <= max_chars:
        return [cleaned] if cleaned else []

    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)
            for sentence in sentences:
                if len(current) + len(sentence) + 1 > max_chars and current:
                    chunks.append(current.strip())
                    current = sentence
                else:
                    current = f"{current} {sentence}".strip()
            continue
        if len(current) + len(paragraph) + 2 > max_chars and current:
            chunks.append(current.strip())
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}".strip()
    if current:
        chunks.append(current.strip())
    return chunks


def load_knowledge(knowledge_dir: Path, max_chars: int = 900) -> List[KnowledgeChunk]:
    if not knowledge_dir.exists():
        return []

    chunks: List[KnowledgeChunk] = []
    for path in sorted(knowledge_dir.glob("*.md")):
        markdown = path.read_text(encoding="utf-8").strip()
        if not markdown:
            continue
        category = path.stem.lower()
        document_title = _title_from_markdown(markdown, category)
        for section_index, section in enumerate(_split_sections(markdown), start=1):
            for chunk_index, content in enumerate(_chunk_section(section, max_chars), start=1):
                chunks.append(
                    KnowledgeChunk(
                        id=f"{category}-{section_index}-{chunk_index}",
                        title=document_title,
                        category=category,
                        content=content,
                        source=str(path.as_posix()),
                    )
                )
    return chunks
