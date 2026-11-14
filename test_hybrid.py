"""Unit tests for the Unit 9 BM25 keyword retriever."""

import unittest

from chunker import Chunk
from hybrid import BM25Retriever, tokenize


class TestBM25Retriever(unittest.TestCase):

    def setUp(self):
        self.chunks = [
            Chunk(
                text="Housing lottery applications open in September.",
                source="housing.txt",
                index=0,
                produced_by="chunker.py::split_documents",
            ),
            Chunk(
                text="Library books can be renewed online.",
                source="library.txt",
                index=0,
                produced_by="chunker.py::split_documents",
            ),
            Chunk(
                text="Parking permits are available to students.",
                source="parking.txt",
                index=0,
                produced_by="chunker.py::split_documents",
            ),
        ]

        self.retriever = BM25Retriever(self.chunks)

    def test_tokenization(self):
        self.assertEqual(
            tokenize("Housing-Lottery, 2026!"),
            ["housing", "lottery", "2026"],
        )

    def test_keyword_match(self):
        results = self.retriever.search("housing lottery")
        self.assertTrue(results)
        self.assertEqual(results[0].source, "housing.txt")

    def test_chunk_identity(self):
        results = self.retriever.search("parking permits")
        self.assertTrue(results)
        self.assertEqual(results[0].label, "parking.txt#0")

    def test_no_matching_terms(self):
        results = self.retriever.search("astronomy telescope")
        self.assertEqual(results, [])

    def test_empty_question(self):
        self.assertEqual(self.retriever.search(""), [])

    def test_top_k_limit(self):
        results = self.retriever.search("students", top_k=1)
        self.assertLessEqual(len(results), 1)

    def test_invalid_top_k(self):
        with self.assertRaises(ValueError):
            self.retriever.search("housing", top_k=0)

    def test_empty_corpus(self):
        retriever = BM25Retriever([])
        self.assertEqual(retriever.search("housing"), [])


if __name__ == "__main__":
    unittest.main()