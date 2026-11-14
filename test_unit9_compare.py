"""Offline tests for Unit 9 comparison helpers."""
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from unit9_compare import evaluate_one, summarize


class CompareTests(unittest.TestCase):
    def test_semantic_gate(self):
        r = SimpleNamespace(source='a.txt', label='a#0', distance=0.2, text='Evidence')
        with patch('store.search', return_value=[r]):
            item = evaluate_one('Q', 'semantic', 5, 'campus_life', 'default')
        self.assertFalse(item['refused'])
        self.assertEqual(item['sources'], ['a.txt'])

    def test_hybrid_gate_uses_semantic_not_fusion(self):
        fused = SimpleNamespace(source='keyword.txt', label='k#0', text='Keyword evidence')
        semantic = SimpleNamespace(source='semantic.txt', label='s#0', distance=0.9, text='Semantic evidence')
        with patch('hybrid.hybrid_search', return_value=([fused], [semantic])):
            item = evaluate_one('Q', 'hybrid', 5, 'campus_life', 'default')
        self.assertTrue(item['refused'])
        self.assertEqual(item['sources'], ['keyword.txt'])

    def test_summary(self):
        rows = [{'mode':'semantic','scope':'in','duration_ms':10,'gate_correct':True,'expected_source_top1':True,'expected_source_topk':True},
                {'mode':'semantic','scope':'in','duration_ms':20,'gate_correct':False,'expected_source_top1':False,'expected_source_topk':True}]
        summary = summarize(rows)
        self.assertEqual(summary[0]['mean_ms'], 15)
        self.assertEqual(summary[0]['expected_source_topk'], 2)


if __name__ == '__main__':
    unittest.main()
