"""Milestone 5 instrumentation tests: no Gemini calls or live Chroma index."""
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
    return SimpleNamespace(text='Evidence', source='test.txt', label='test.txt#0',
                           produced_by='test', distance=distance)


class TestInstrumentation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.log = Path(self.temp.name) / 'events.jsonl'
        self.env = patch.dict(os.environ, {'AI201_LOG_PATH': str(self.log)})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def records(self):
        return [json.loads(line) for line in self.log.read_text(encoding='utf-8').splitlines()]

    @patch('generate.answer_from_chunks', return_value='Answer')
    @patch('store.search', return_value=[result()])
    def test_semantic_success(self, search, answer):
        self.assertEqual(ask_pipeline('Housing?')['answer'], 'Answer')
        record = self.records()[0]
        self.assertEqual(record['status'], 'success')
        self.assertEqual(record['retrieval_mode'], 'semantic')
        self.assertEqual(record['sources'], ['test.txt'])
        self.assertGreaterEqual(record['duration_ms'], 0)
        self.assertIn('timestamp', record)

    @patch('generate.answer_from_chunks')
    @patch('store.search', return_value=[result(0.9)])
    def test_refusal(self, search, answer):
        self.assertTrue(ask_pipeline('Unknown?')['refused'])
        self.assertEqual(self.records()[0]['status'], 'refused')
        answer.assert_not_called()

    @patch('store.search', side_effect=RuntimeError('test failure'))
    def test_exception(self, search):
        with self.assertRaises(RuntimeError):
            ask_pipeline('Failure?')
        self.assertEqual(self.records()[0]['error_type'], 'RuntimeError')

    @patch('generate.answer_from_chunks', return_value='Hybrid answer')
    @patch('hybrid.hybrid_search')
    def test_hybrid(self, hybrid, answer):
        hybrid.return_value = ([result()], [result()])
        ask_pipeline('Housing?', retrieval='hybrid')
        self.assertEqual(self.records()[0]['retrieval_mode'], 'hybrid')

    def test_http_validation_failure(self):
        with app.test_client() as client:
            response = client.post('/ask', json={'question': 'x', 'retrieval': 'invalid'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.records()[0]['event'], 'http_request_error')

    def test_json_lines_append(self):
        with patch('store.search', return_value=[result(0.9)]):
            ask_pipeline('One')
            ask_pipeline('Two')
        self.assertEqual(len(self.records()), 2)


if __name__ == '__main__':
    unittest.main()
