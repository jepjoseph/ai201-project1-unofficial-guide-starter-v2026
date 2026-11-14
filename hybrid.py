"""
Unit 9 Capstone: BM25 keyword retrieval.

This module does not modify the original semantic search.
Reciprocal Rank Fusion will be added in a later commit.
"""

import re
from dataclasses import dataclass

from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    """Normalize text into lowercase alphanumeric search terms."""
    return re.findall(r"[^\W_]+", text.lower(), flags=re.UNICODE)


@dataclass(frozen=True)
class KeywordResult:
    """One BM25 result with its original chunk identity."""

    text: str
    source: str
    label: str
    produced_by: str
    score: float


class BM25Retriever:
    """Keyword search over an existing list of document chunks."""

    def __init__(self, chunks):
        self.chunks = list(chunks)

        self.tokens = [
            tokenize(chunk.text)
            for chunk in self.chunks
        ]

        self.model = (
            BM25Okapi(self.tokens)
            if self.chunks and all(self.tokens)
            else None
        )

    def search(self, question: str, top_k: int = 5) -> list[KeywordResult]:
        """Return positive-scoring keyword matches, highest score first."""

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        query_tokens = tokenize(question)

        if not query_tokens or self.model is None:
            return []

        scores = self.model.get_scores(query_tokens)

        ranked = sorted(
            enumerate(scores),
            key=lambda item: (-float(item[1]), item[0]),
        )

        results = []

        for index, score in ranked:
            if float(score) <= 0:
                continue

            chunk = self.chunks[index]

            results.append(
                KeywordResult(
                    text=chunk.text,
                    source=chunk.source,
                    label=chunk.label,
                    produced_by=chunk.produced_by,
                    score=float(score),
                )
            )

            if len(results) >= top_k:
                break

        return results