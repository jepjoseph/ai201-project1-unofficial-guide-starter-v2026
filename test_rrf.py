"""Unit tests for Reciprocal Rank Fusion."""

import unittest
from types import SimpleNamespace

from rrf import reciprocal_rank_fusion


def keyword(label):
    return SimpleNamespace(
        text=f"Text for {label}",
        source="test.txt",
        label=label,
        produced_by="keyword",
        score=2.0,
    )


def semantic(label, distance=0.2):
    return SimpleNamespace(
        text=f"Text for {label}",
        source="test.txt",
        label=label,
        produced_by="semantic",
        distance=distance,
    )


class TestReciprocalRankFusion(unittest.TestCase):

    def test_empty_results(self):
        self.assertEqual(reciprocal_rank_fusion([], []), [])

    def test_shared_result_ranks_first(self):
        results = reciprocal_rank_fusion(
            [keyword("A"), keyword("B")],
            [semantic("C"), semantic("A")],
        )
        self.assertEqual(results[0].label, "A")

    def test_duplicate_is_not_repeated(self):
        results = reciprocal_rank_fusion(
            [keyword("A")],
            [semantic("A")],
        )
        self.assertEqual(len(results), 1)

    def test_semantic_distance_preserved(self):
        results = reciprocal_rank_fusion(
            [keyword("A")],
            [semantic("A", distance=0.15)],
        )
        self.assertEqual(results[0].semantic_distance, 0.15)

    def test_keyword_only_result(self):
        results = reciprocal_rank_fusion(
            [keyword("A")],
            [],
        )
        self.assertEqual(results[0].keyword_rank, 1)
        self.assertIsNone(results[0].semantic_rank)
        self.assertIsNone(results[0].semantic_distance)

    def test_semantic_only_result(self):
        results = reciprocal_rank_fusion(
            [],
            [semantic("A")],
        )
        self.assertIsNone(results[0].keyword_rank)
        self.assertEqual(results[0].semantic_rank, 1)

    def test_top_k(self):
        results = reciprocal_rank_fusion(
            [keyword("A"), keyword("B"), keyword("C")],
            [],
            top_k=2,
        )
        self.assertEqual(len(results), 2)

    def test_deterministic_tie(self):
        results = reciprocal_rank_fusion(
            [keyword("B")],
            [semantic("A")],
        )
        self.assertEqual(
            [item.label for item in results],
            ["A", "B"],
        )

    def test_duplicate_within_one_list(self):
        results = reciprocal_rank_fusion(
            [keyword("A"), keyword("A")],
            [],
        )
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual(results[0].rrf_score, 1 / 61)

    def test_invalid_top_k(self):
        with self.assertRaises(ValueError):
            reciprocal_rank_fusion([], [], top_k=0)

    def test_invalid_k(self):
        with self.assertRaises(ValueError):
            reciprocal_rank_fusion([], [], k=0)


if __name__ == "__main__":
    unittest.main()