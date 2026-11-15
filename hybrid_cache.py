"""Bounded in-memory cache for prepared BM25 retrieval data."""

import os
from collections import OrderedDict
from threading import RLock

import config

_MAX_ENTRIES = 4
_cache = OrderedDict()
_lock = RLock()


def clear_cache():
    """Discard all cached BM25 retrievers."""
    with _lock:
        _cache.clear()


def _signature(corpus):
    """Identify corpus contents and relevant chunking settings."""
    folder = config.corpus_path(corpus).resolve()

    if not folder.is_dir():
        raise FileNotFoundError(f"No corpus at {folder}")

    fingerprint = []

    with os.scandir(folder) as entries:
        for entry in entries:
            if not entry.name.lower().endswith((".txt", ".md")):
                continue

            if not entry.is_file():
                continue

            metadata = entry.stat()

            fingerprint.append(
                (
                    entry.name,
                    metadata.st_size,
                    metadata.st_mtime_ns,
                )
            )

    fingerprint.sort(key=lambda item: item[0])

    return (
        str(folder),
        config.CHUNK_SIZE,
        config.CHUNK_OVERLAP,
        tuple(fingerprint),
    )


def get_retriever(corpus, factory):
    """Return (retriever, cache_hit).

    The factory runs only when the cache is empty or invalid.
    """
    with _lock:
        signature = _signature(corpus)
        key = signature[0]

        if key in _cache:
            old_signature, retriever = _cache[key]

            if old_signature == signature:
                _cache.move_to_end(key)
                return retriever, True

            del _cache[key]

        retriever = factory()

        _cache[key] = (signature, retriever)
        _cache.move_to_end(key)

        while len(_cache) > _MAX_ENTRIES:
            _cache.popitem(last=False)

        return retriever, False
