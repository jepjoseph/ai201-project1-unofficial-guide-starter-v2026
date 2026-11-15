"""Regression tests for prepared BM25 retrieval caching."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import config
from hybrid import hybrid_search
from hybrid_cache import clear_cache, get_retriever
from retrieval_timing import RetrievalTiming


class BM25CacheTests(unittest.TestCase):

    def setUp(self):
        clear_cache()

        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.root = Path(self.temp.name)
        self.corpora = self.root / "corpora"
        self.corpora.mkdir()

        self.config_patch = patch.object(
            config, "CORPORA_DIR", self.corpora
        )
        self.config_patch.start()

        # LIFO cleanup: stop patch before clearing cache.
        self.addCleanup(clear_cache)
        self.addCleanup(self.config_patch.stop)

    def make_corpus(self, name, text):
        folder = self.corpora / name / "documents"
        folder.mkdir(parents=True)

        (folder / "evidence.txt").write_text(
            text, encoding="utf-8"
        )

        return folder

    def test_cache_hit_reuses_retriever(self):
        self.make_corpus("alpha", "Housing lottery information")
        calls = []

        def factory():
            result = object()
            calls.append(result)
            return result

        first, hit1 = get_retriever("alpha", factory)
        second, hit2 = get_retriever("alpha", factory)

        self.assertFalse(hit1)
        self.assertTrue(hit2)
        self.assertIs(first, second)
        self.assertEqual(len(calls), 1)

    def test_file_change_invalidates_cache(self):
        folder = self.make_corpus(
            "alpha", "Original evidence"
        )
        calls = []

        def factory():
            result = object()
            calls.append(result)
            return result

        first, _ = get_retriever("alpha", factory)

        (folder / "evidence.txt").write_text(
            "Updated evidence with additional information",
            encoding="utf-8",
        )

        second, hit = get_retriever("alpha", factory)

        self.assertFalse(hit)
        self.assertIsNot(first, second)
        self.assertEqual(len(calls), 2)

    def test_corpora_are_isolated(self):
        self.make_corpus("alpha", "Housing lottery")
        self.make_corpus("beta", "Library services")

        first, _ = get_retriever("alpha", object)
        second, _ = get_retriever("beta", object)
        repeated, hit = get_retriever("alpha", object)

        self.assertIsNot(first, second)
        self.assertIs(first, repeated)
        self.assertTrue(hit)

    def test_chunk_size_change_invalidates_cache(self):
        self.make_corpus("alpha", "Housing lottery")

        first, _ = get_retriever("alpha", object)

        with patch.object(
            config, "CHUNK_SIZE", config.CHUNK_SIZE + 1
        ):
            second, hit = get_retriever("alpha", object)

        self.assertFalse(hit)
        self.assertIsNot(first, second)

    def test_clear_cache_forces_rebuild(self):
        self.make_corpus("alpha", "Housing lottery")

        first, _ = get_retriever("alpha", object)

        clear_cache()

        second, hit = get_retriever("alpha", object)

        self.assertFalse(hit)
        self.assertIsNot(first, second)

    def test_hybrid_results_identical_on_cache_hit(self):
        self.make_corpus(
            "alpha",
            "Housing lottery applications open in September. "
            "Students may submit their applications online.",
        )

        semantic = [
            SimpleNamespace(
                text="Housing lottery applications open in September.",
                source="evidence.txt",
                label="evidence.txt#0",
                produced_by="test",
                distance=0.2,
            )
        ]

        with patch("store.search", return_value=semantic):
            cold_timing = RetrievalTiming()

            cold, cold_semantic = hybrid_search(
                "housing lottery",
                corpus="alpha",
                top_k=1,
                timing=cold_timing,
            )

            warm_timing = RetrievalTiming()

            warm, warm_semantic = hybrid_search(
                "housing lottery",
                corpus="alpha",
                top_k=1,
                timing=warm_timing,
            )

        self.assertEqual(cold, warm)
        self.assertEqual(cold_semantic, warm_semantic)

        self.assertIn(
            "bm25_construction",
            cold_timing.as_dict(),
        )

        self.assertNotIn(
            "bm25_construction",
            warm_timing.as_dict(),
        )

        self.assertIn(
            "cache_lookup",
            warm_timing.as_dict(),
        )


if __name__ == "__main__":
    unittest.main()
