"""
Unit 9 Capstone: Reciprocal Rank Fusion.

Combines ranked results without comparing BM25 scores
directly against semantic cosine distances.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FusedResult:
    text: str
    source: str
    label: str
    produced_by: str
    rrf_score: float
    keyword_rank: int | None
    semantic_rank: int | None
    semantic_distance: float | None


def reciprocal_rank_fusion(
    keyword_results,
    semantic_results,
    top_k: int = 5,
    k: int = 60,
) -> list[FusedResult]:
    """Fuse two ranked lists using their original chunk labels."""

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    if k <= 0:
        raise ValueError("k must be greater than zero")

    records = {}

    for method, results in (
        ("keyword", keyword_results),
        ("semantic", semantic_results),
    ):
        seen = set()

        for rank, result in enumerate(results, start=1):
            label = result.label

            # A repeated chunk within one retriever contributes once.
            if label in seen:
                continue

            seen.add(label)

            if label not in records:
                records[label] = {
                    "result": result,
                    "score": 0.0,
                    "keyword_rank": None,
                    "semantic_rank": None,
                    "semantic_distance": None,
                }

            record = records[label]
            record["score"] += 1.0 / (k + rank)
            record[f"{method}_rank"] = rank

            if method == "semantic":
                # Prefer semantic text/metadata when available.
                record["result"] = result
                record["semantic_distance"] = result.distance

    fused = []

    for label, record in records.items():
        result = record["result"]

        fused.append(
            FusedResult(
                text=result.text,
                source=result.source,
                label=label,
                produced_by=result.produced_by,
                rrf_score=record["score"],
                keyword_rank=record["keyword_rank"],
                semantic_rank=record["semantic_rank"],
                semantic_distance=record["semantic_distance"],
            )
        )

    return sorted(
        fused,
        key=lambda item: (-item.rrf_score, item.label),
    )[:top_k]