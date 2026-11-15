import time

import config
import gate
from hybrid import hybrid_search
from store import index_exists, search


def validate_index(corpus: str, variant: str):
    if not corpus or not variant:
        raise ValueError("Corpus and variant are required.")

    corpus_path = config.corpus_path(corpus).resolve()
    corpora_root = config.CORPORA_DIR.resolve()

    if corpus_path.parent != corpora_root / corpus:
        raise ValueError("Invalid corpus path.")

    if not corpus_path.is_dir():
        raise ValueError(f"Unknown corpus: {corpus}")

    if not index_exists(corpus, variant):
        raise ValueError(
            f"No ready index for corpus={corpus}, variant={variant}"
        )


def available_indexes():
    from store import _client

    collections = _client().list_collections()
    available = []

    for collection in collections:
        name = collection if isinstance(collection, str) else collection.name

        for corpus_dir in sorted(config.CORPORA_DIR.iterdir()):
            if not corpus_dir.is_dir():
                continue

            prefix = f"{corpus_dir.name}__"

            if name.startswith(prefix):
                variant = name[len(prefix):]

                if variant and index_exists(corpus_dir.name, variant):
                    available.append({
                        "corpus": corpus_dir.name,
                        "variant": variant,
                        "collection": name,
                    })

    return available


def run_retrieval(
    question: str,
    corpus: str,
    variant: str,
    retrieval: str,
    top_k: int,
    threshold: float,
):
    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    validate_index(corpus, variant)

    started = time.perf_counter()

    if retrieval == "semantic":
        results = search(
            question,
            top_k=top_k,
            corpus=corpus,
            variant=variant,
        )
        semantic_candidates = results

    elif retrieval == "hybrid":
        results, semantic_candidates = hybrid_search(
            question,
            top_k=top_k,
            corpus=corpus,
            variant=variant,
        )

    else:
        raise ValueError("Unknown retrieval mode.")

    decision = gate.check(
        semantic_candidates,
        threshold=threshold,
    )

    elapsed_ms = (time.perf_counter() - started) * 1000

    documents = []

    for rank, result in enumerate(results, start=1):
        item = {
            "rank": rank,
            "label": result.label,
            "source": result.source,
            "text": result.text,
            "produced_by": result.produced_by,
        }

        if retrieval == "semantic":
            item["distance"] = result.distance
        else:
            item["rrf_score"] = result.rrf_score
            item["semantic_distance"] = result.semantic_distance
            item["semantic_rank"] = result.semantic_rank
            item["keyword_rank"] = result.keyword_rank

        documents.append(item)

    return {
        "question": question,
        "corpus": corpus,
        "variant": variant,
        "retrieval": retrieval,
        "top_k": top_k,
        "threshold": decision.threshold,
        "gate": {
            "passed": decision.passed,
            "refused": not decision.passed,
            "best_distance": decision.best_distance,
            "explanation": decision.explanation,
        },
        "duration_ms": round(elapsed_ms, 2),
        "result_count": len(documents),
        "documents": documents,
    }


def compare_retrievals(
    question: str,
    corpus: str,
    variant: str,
    top_k: int,
    threshold: float,
):
    semantic = run_retrieval(
        question, corpus, variant, "semantic", top_k, threshold
    )

    hybrid = run_retrieval(
        question, corpus, variant, "hybrid", top_k, threshold
    )

    semantic_ranks = {
        doc["label"]: doc["rank"]
        for doc in semantic["documents"]
    }

    hybrid_ranks = {
        doc["label"]: doc["rank"]
        for doc in hybrid["documents"]
    }

    labels = sorted(set(semantic_ranks) | set(hybrid_ranks))

    comparison = [
        {
            "label": label,
            "semantic_rank": semantic_ranks.get(label),
            "hybrid_rank": hybrid_ranks.get(label),
        }
        for label in labels
    ]

    return {
        "question": question,
        "corpus": corpus,
        "variant": variant,
        "semantic": semantic,
        "hybrid": hybrid,
        "rank_comparison": comparison,
    }
