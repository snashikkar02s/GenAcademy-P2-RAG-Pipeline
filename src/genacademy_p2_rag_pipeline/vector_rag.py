"""Baseline: classic vector RAG over document chunks."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

import numpy as np

# The Rust-based Xet downloader ignores the OS cert store; plain HTTP downloads honour truststore.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from . import llm
from .data import KnowledgeBase

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
# bge models expect this prefix on queries (not on passages).
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


@dataclass
class Chunk:
    doc_id: str
    title: str
    text: str


def chunk_documents(kb: KnowledgeBase, window: int = 3, stride: int = 2) -> list[Chunk]:
    """Overlapping windows of `window` sentences, each prefixed by its document title."""
    chunks = []
    for doc in kb.documents.values():
        sentences = re.split(r"(?<=[.!?])\s+", doc.text.strip())
        for start in range(0, max(len(sentences) - window + stride, 1), stride):
            text = " ".join(sentences[start:start + window])
            if text:
                chunks.append(Chunk(doc.id, doc.title, text))
    return chunks


class VectorRAG:
    def __init__(self, kb: KnowledgeBase):
        from fastembed import TextEmbedding

        self.chunks = chunk_documents(kb)
        self.model = TextEmbedding(EMBED_MODEL)
        self.matrix = self._normalize(
            np.array(list(self.model.embed([f"{c.title}: {c.text}" for c in self.chunks])))
        )

    @staticmethod
    def _normalize(m: np.ndarray) -> np.ndarray:
        return m / np.linalg.norm(m, axis=-1, keepdims=True)

    def retrieve(self, question: str, k: int = 4) -> list[tuple[Chunk, float]]:
        q = self._normalize(np.array(list(self.model.embed([QUERY_PREFIX + question])))[0])
        scores = self.matrix @ q
        top = np.argsort(-scores)[:k]
        return [(self.chunks[i], float(scores[i])) for i in top]

    def context(self, question: str, k: int = 4) -> str:
        return "\n\n".join(
            f"[{c.doc_id}: {c.title}]\n{c.text}" for c, _ in self.retrieve(question, k)
        )

    def answer(self, question: str, k: int = 4) -> dict:
        context = self.context(question, k)
        return {"answer": llm.answer(question, context), "context": context}
