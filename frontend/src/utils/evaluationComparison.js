export const summaryKey = (row) => `${row.mode}::${row.scope}`
export const trialKey = (row) => JSON.stringify([row.mode, row.scope, row.question, row.trial])
export const percentage = (count, total) => total > 0 ? (100 * count) / total : null
export const numericDelta = (baseline, current) =>
  Number.isFinite(Number(baseline)) && Number.isFinite(Number(current))
    ? Number(current) - Number(baseline) : null

export function compareEvaluations(baseline, current) {
  const keys = ['corpus', 'variant', 'top_k']
  const warnings = keys.filter((key) => baseline.metadata?.[key] !== current.metadata?.[key])
    .map((key) => `${key}: ${baseline.metadata?.[key] ?? 'N/A'} vs ${current.metadata?.[key] ?? 'N/A'}`)
  const oldRows = new Map(baseline.summary.map((row) => [summaryKey(row), row]))
  const newRows = new Map(current.summary.map((row) => [summaryKey(row), row]))
  const allKeys = [...new Set([...oldRows.keys(), ...newRows.keys()])].sort()
  const rows = allKeys.map((key) => {
    const before = oldRows.get(key)
    const after = newRows.get(key)
    const comparable = Boolean(before && after && before.trials === after.trials)
    if (!before || !after) warnings.push(`Missing summary group: ${key}`)
    else if (!comparable) warnings.push(`Different trial counts: ${key}`)
    return { key, before, after, comparable,
      gateDelta: comparable ? numericDelta(percentage(before.gate_correct, before.trials), percentage(after.gate_correct, after.trials)) : null,
      top1Delta: comparable && before.scope === 'in' ? numericDelta(percentage(before.expected_source_top1, before.trials), percentage(after.expected_source_top1, after.trials)) : null,
      topkDelta: comparable && before.scope === 'in' ? numericDelta(percentage(before.expected_source_topk, before.trials), percentage(after.expected_source_topk, after.trials)) : null,
      meanDelta: comparable ? numericDelta(before.mean_ms, after.mean_ms) : null,
      medianDelta: comparable ? numericDelta(before.median_ms, after.median_ms) : null,
    }
  })
  const countKeys = (records) => {
    const counts = new Map()
    for (const row of records) counts.set(trialKey(row), (counts.get(trialKey(row)) ?? 0) + 1)
    return counts
  }
  const oldTrials = countKeys(baseline.records)
  const newTrials = countKeys(current.records)
  const sameTrials = oldTrials.size === newTrials.size && [...oldTrials].every(([key, count]) => newTrials.get(key) === count)
  if (!sameTrials) warnings.push('Trial identities or duplicate counts differ; trial-by-trial comparison is unavailable.')
  if (baseline.metadata?.runs !== current.metadata?.runs) warnings.push('Run counts differ.')
  return { rows, warnings, trialCompatible: sameTrials && warnings.length === 0 }
}
