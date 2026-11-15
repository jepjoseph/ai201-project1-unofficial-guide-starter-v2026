import unittest
from unittest.mock import patch
from types import SimpleNamespace

from retrieval_timing import RetrievalTiming


class RetrievalTimingTests(unittest.TestCase):

    def test_empty_collector(self):
        timing = RetrievalTiming()
        self.assertEqual(timing.as_dict(), {})

    def test_measures_stage(self):
        timing = RetrievalTiming()

        with patch(
            "retrieval_timing.perf_counter",
            side_effect=[1.0, 1.025],
        ):
            with timing.measure("semantic_search"):
                pass

        self.assertAlmostEqual(
            timing.as_dict()["semantic_search"],
            25.0,
            places=3,
        )

    def test_accumulates_repeated_stage(self):
        timing = RetrievalTiming()

        with patch(
            "retrieval_timing.perf_counter",
            side_effect=[1.0, 1.01, 2.0, 2.02],
        ):
            with timing.measure("keyword_search"):
                pass
            with timing.measure("keyword_search"):
                pass

        self.assertAlmostEqual(
            timing.as_dict()["keyword_search"],
            30.0,
            places=3,
        )

    def test_records_duration_when_stage_raises(self):
        timing = RetrievalTiming()

        with patch(
            "retrieval_timing.perf_counter",
            side_effect=[1.0, 1.005],
        ):
            with self.assertRaisesRegex(ValueError, "test failure"):
                with timing.measure("document_loading"):
                    raise ValueError("test failure")

        self.assertAlmostEqual(
            timing.as_dict()["document_loading"],
            5.0,
            places=3,
        )



class HybridTimingIntegrationTests(unittest.TestCase):

    @patch("store.search")
    @patch("ingest.load_documents")
    @patch("chunker.split_documents")
    def test_timing_preserves_hybrid_results(self, split, load, search):
        from hybrid import hybrid_search

        chunk = SimpleNamespace(
            text="Housing lottery opens in September",
            source="housing.txt",
            label="housing.txt#0",
            produced_by="test",
        )

        semantic = SimpleNamespace(
            text=chunk.text,
            source=chunk.source,
            label=chunk.label,
            produced_by="test",
            distance=0.2,
        )

        split.return_value = [chunk]
        search.return_value = [semantic]

        baseline, baseline_semantic = hybrid_search(
            "housing lottery", top_k=1
        )

        timing = RetrievalTiming()

        measured, measured_semantic = hybrid_search(
            "housing lottery", top_k=1, timing=timing
        )

        self.assertEqual(baseline, measured)
        self.assertEqual(baseline_semantic, measured_semantic)

        self.assertEqual(
            set(timing.as_dict()),
            {
                "document_loading",
                "document_chunking",
                "bm25_construction",
                "keyword_search",
                "semantic_search",
                "rrf_fusion",
            },
        )


class ComparisonTimingIntegrationTests(unittest.TestCase):

    def test_semantic_timing_fields(self):
        from unit9_compare import evaluate_one

        result = SimpleNamespace(
            text="Evidence",
            source="test.txt",
            label="test.txt#0",
            distance=0.2,
        )

        with patch("store.search", return_value=[result]):
            evaluated = evaluate_one(
                "Evidence", "semantic", 1,
                "campus_life", "default"
            )

        self.assertIn(
            "semantic_search", evaluated["stage_timings_ms"]
        )
        self.assertIn(
            "relevance_gate", evaluated["stage_timings_ms"]
        )


if __name__ == "__main__":
    unittest.main()