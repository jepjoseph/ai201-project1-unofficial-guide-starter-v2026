import test from 'node:test'
import assert from 'node:assert/strict'
import { compareEvaluations } from './evaluationComparison.js'
const report = (gate, ms, trials = 15) => ({ metadata: { corpus: 'campus_life', variant: 'default', top_k: 5, runs: 3 },
  summary: [{ mode: 'hybrid', scope: 'in', trials, gate_correct: gate, expected_source_top1: gate, expected_source_topk: gate, mean_ms: ms, median_ms: ms }],
  records: [{ mode: 'hybrid', scope: 'in', question: 'test', trial: 1 }] })
test('computes percentage-point and millisecond differences', () => {
 const result = compareEvaluations(report(12, 50), report(15, 40))
 assert.equal(result.rows[0].gateDelta, 20)
 assert.equal(result.rows[0].meanDelta, -10)
 assert.equal(result.trialCompatible, true)
})
test('refuses numerical comparison with mismatched trial counts', () => {
 const result = compareEvaluations(report(12, 50), report(15, 40, 20))
 assert.equal(result.rows[0].gateDelta, null)
 assert.ok(result.warnings.length > 0)
})
test('detects incompatible configuration', () => {
 const next = report(15, 40); next.metadata.top_k = 1
 assert.equal(compareEvaluations(report(12, 50), next).trialCompatible, false)
})
