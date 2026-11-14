"""Milestone 4 integration tests: no model calls or live index required."""
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from app import ask_pipeline
from hybrid import hybrid_search
from rrf import reciprocal_rank_fusion


def sem(label, distance):
    return SimpleNamespace(label=label, source="test.txt", text="Evidence " + label,
                           produced_by="test", distance=distance)

def key(label):
    return SimpleNamespace(label=label, source="test.txt", text="Evidence " + label,
                           produced_by="test", score=2.0)


class TestHybridPipeline(unittest.TestCase):
    @patch("store.search")
    @patch("ingest.load_documents")
    @patch("chunker.split_documents")
    def test_hybrid_fuses_and_keeps_semantic_candidates(self, split, load, search):
        split.return_value = [SimpleNamespace(text="Evidence A", source="test.txt",
                            label="A", produced_by="test")]
        search.return_value = [sem("A", 0.2), sem("B", 0.8)]
        fused, semantic = hybrid_search("Evidence", top_k=2)
        self.assertEqual(semantic[0].distance, 0.2)
        self.assertEqual(fused[0].label, "A")
        self.assertEqual(fused[0].semantic_distance, 0.2)

    @patch("generate.answer_from_chunks", return_value="Grounded answer")
    @patch("hybrid.hybrid_search")
    def test_hybrid_answer_uses_fused_context(self, retrieve, answer):
        fused = reciprocal_rank_fusion([key("A")], [sem("A", 0.2)], top_k=1)
        retrieve.return_value = (fused, [sem("A", 0.2)])
        result = ask_pipeline("Question", retrieval="hybrid")
        self.assertFalse(result["refused"])
        self.assertEqual(result["answer"], "Grounded answer")
        self.assertEqual(answer.call_args.args[1][0].label, "A")

    @patch("generate.answer_from_chunks")
    @patch("hybrid.hybrid_search")
    def test_keyword_only_cannot_bypass_semantic_gate(self, retrieve, answer):
        fused = reciprocal_rank_fusion([key("A")], [sem("B", 0.9)], top_k=2)
        retrieve.return_value = (fused, [sem("B", 0.9)])
        result = ask_pipeline("Unknown question", retrieval="hybrid")
        self.assertTrue(result["refused"])
        answer.assert_not_called()

    @patch("generate.answer_from_chunks")
    @patch("hybrid.hybrid_search")
    def test_no_semantic_candidates_refuses(self, retrieve, answer):
        retrieve.return_value = (reciprocal_rank_fusion([key("A")], []), [])
        result = ask_pipeline("Unknown question", retrieval="hybrid")
        self.assertTrue(result["refused"])
        answer.assert_not_called()

    @patch("generate.answer_from_chunks", return_value="Semantic answer")
    @patch("store.search")
    def test_default_mode_remains_semantic(self, search, answer):
        search.return_value = [sem("A", 0.2)]
        result = ask_pipeline("Question")
        self.assertFalse(result["refused"])
        self.assertEqual(result["answer"], "Semantic answer")

    def test_invalid_mode_rejected(self):
        with self.assertRaises(ValueError):
            ask_pipeline("Question", retrieval="other")


if __name__ == "__main__":
    unittest.main()
