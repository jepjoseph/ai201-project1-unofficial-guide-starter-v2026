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

def hybrid_search(question: str, *, top_k: int = 5, corpus=None, variant="default", candidate_k: int = 10):
    """Retrieve from both engines, then fuse rankings by stable chunk label.

    Returns (fused_results, semantic_candidates). The latter must be used
    for the cosine-distance relevance gate, not the RRF scores.
    """
    from chunker import split_documents
    from ingest import load_documents
    from rrf import reciprocal_rank_fusion
    from store import search as semantic_search

    if top_k <= 0 or candidate_k <= 0:
        raise ValueError("top_k and candidate_k must be greater than zero")
    pool_size = max(top_k, candidate_k)
    chunks = split_documents(load_documents(corpus))
    keyword = BM25Retriever(chunks).search(question, top_k=pool_size)
    semantic = semantic_search(question, top_k=pool_size, corpus=corpus, variant=variant)
    fused = reciprocal_rank_fusion(keyword, semantic, top_k=top_k)
    return fused, semantic
