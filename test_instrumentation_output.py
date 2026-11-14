"""Unit 9 Milestone 7: explicit input/output logging tests."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app import ask_pipeline
from serve import app


def result(distance=0.2):
    return SimpleNamespace(
        text="Evidence",
        source="test.txt",
        label="test.txt#0",
        produced_by="test",
        distance=distance,
    )


class TestInstrumentationOutput(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.log = Path(self.temp.name) / "events.jsonl"
        self.env = patch.dict(
            os.environ, {"AI201_LOG_PATH": str(self.log)}
        )
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def record(self):
        lines = self.log.read_text(encoding="utf-8").splitlines()
        return json.loads(lines[-1])

    @patch("generate.answer_from_chunks", return_value="Verified answer")
    @patch("store.search", return_value=[result()])
    def test_success_output(self, search, generate):
        ask_pipeline("Housing?")
        record = self.record()
        self.assertEqual(record["input"]["question"], "Housing?")
        self.assertEqual(record["output"], "Verified answer")
        self.assertEqual(record["status"], "success")

    @patch("generate.answer_from_chunks")
    @patch("store.search", return_value=[result(0.9)])
    def test_refusal_output(self, search, generate):
        from gate import REFUSAL
        ask_pipeline("Unknown?")
        record = self.record()
        self.assertEqual(record["output"], REFUSAL)
        self.assertEqual(record["status"], "refused")
        generate.assert_not_called()

    @patch("store.search", side_effect=RuntimeError("secret detail"))
    def test_exception_output(self, search):
        with self.assertRaises(RuntimeError):
            ask_pipeline("Failure?")
        record = self.record()
        self.assertEqual(
            record["output"], {"error_type": "RuntimeError"}
        )
        self.assertNotIn("secret detail", json.dumps(record))
        self.assertEqual(record["status"], "error")

    def test_http_error_output(self):
        with app.test_client() as client:
            response = client.post(
                "/ask",
                json={"question": "Test", "retrieval": "invalid"},
            )
        self.assertEqual(response.status_code, 400)
        record = self.record()
        self.assertEqual(record["output"]["http_status"], 400)
        self.assertEqual(record["input"]["question"], "Test")

    @patch("generate.answer_from_chunks", return_value="Hybrid answer")
    @patch("hybrid.hybrid_search")
    def test_hybrid_output(self, hybrid, generate):
        hybrid.return_value = ([result()], [result()])
        ask_pipeline("Hybrid?", retrieval="hybrid")
        record = self.record()
        self.assertEqual(record["output"], "Hybrid answer")
        self.assertEqual(record["retrieval_mode"], "hybrid")


if __name__ == "__main__":
    unittest.main()