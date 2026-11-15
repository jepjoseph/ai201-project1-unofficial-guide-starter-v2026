import { useEffect, useState } from 'react'
import { ragApi } from '../services/ragApi'
import { compareEvaluations, percentage } from '../utils/evaluationComparison'

const format = (value, suffix = '') => value == null ? 'N/A' : `${value.toFixed(2)}${suffix}`
const rate = (row, field) => row ? format(percentage(row[field], row.trials), '%') : 'N/A'

export default function HistoricalComparison() {
  const [reports, setReports] = useState([])
  const [baselineId, setBaselineId] = useState('')
  const [currentId, setCurrentId] = useState('')
  const [baseline, setBaseline] = useState(null)
  const [current, setCurrent] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    ragApi.evaluations().then((data) => {
      if (!active) return
      const items = data.reports ?? []
      setReports(items)
      if (items.length >= 2) {
        setBaselineId(items[1].id)
        setCurrentId(items[0].id)
      }
    }).catch((err) => { if (active) setError(err.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [])

  useEffect(() => {
    if (!baselineId || !currentId || baselineId === currentId) return
    let active = true
    Promise.all([ragApi.evaluation(baselineId), ragApi.evaluation(currentId)])
      .then(([oldReport, newReport]) => {
        if (active) { setBaseline(oldReport); setCurrent(newReport); setError('') }
      }).catch((err) => { if (active) { setBaseline(null); setCurrent(null); setError(err.message) } })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [baselineId, currentId])

  const comparison = baseline && current && baselineId !== currentId
    ? compareEvaluations(baseline, current) : null
  return (
    <section className="card historical-comparison">
      <div className="section-heading"><div>
        <h2>Historical Report Comparison</h2>
        <p>Read-only comparison of saved evaluation runs.</p>
      </div></div>
      {loading && <p role="status">Loading comparison...</p>}
      {error && <p className="evaluation-error" role="alert">{error}</p>}
      {!loading && !error && reports.length < 2 && (
        <p role="status">At least two saved evaluation reports are required. Your existing report remains available above.</p>
      )}
      {reports.length >= 2 && <>
        <div className="historical-comparison-selectors">
          <label>Baseline report<select value={baselineId} onChange={(event) => {
            setBaseline(null); setCurrent(null); setLoading(event.target.value !== currentId); setBaselineId(event.target.value)
          }}>{reports.map((item) => <option key={item.id} value={item.id}>{item.id}</option>)}</select></label>
          <label>Comparison report<select value={currentId} onChange={(event) => {
            setBaseline(null); setCurrent(null); setLoading(event.target.value !== baselineId); setCurrentId(event.target.value)
          }}>{reports.map((item) => <option key={item.id} value={item.id}>{item.id}</option>)}</select></label>
        </div>
        {baselineId === currentId && <p role="alert">Choose two different reports.</p>}
      </>}
      {comparison && !loading && <>
        {comparison.warnings.length > 0 && <div className="historical-comparison-warning" role="alert">
          <strong>Comparison limitations</strong>
          <ul>{comparison.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>
          <p>Only rows with matching groups and trial counts show numeric differences. Interpret differences cautiously when configurations vary.</p>
        </div>}
        <div className="table-scroll"><table>
          <thead><tr><th>Mode / scope</th><th>Baseline gate</th><th>Current gate</th><th>Gate Î” (pp)</th><th>Top-1 Î” (pp)</th><th>Top-K Î” (pp)</th><th>Mean Î” (ms)</th><th>Median Î” (ms)</th></tr></thead>
          <tbody>{comparison.rows.map((row) => <tr key={row.key}>
            <td>{row.key.replace('::', ' / ')}</td>
            <td>{rate(row.before, 'gate_correct')}</td><td>{rate(row.after, 'gate_correct')}</td>
            <td>{format(row.gateDelta)}</td><td>{format(row.top1Delta)}</td><td>{format(row.topkDelta)}</td>
            <td>{format(row.meanDelta)}</td><td>{format(row.medianDelta)}</td>
          </tr>)}</tbody>
        </table></div>
        <p className="comparison-note">Î” = comparison minus baseline. Positive latency Î” means slower retrieval. Top-1 and Top-K are expected-source phrase proxies, not Precision@K or Recall@K. Out-of-scope phrase rates are not scored.</p>
        <p className="comparison-note">Trial identity compatibility: {comparison.trialCompatible ? 'matched' : 'not fully matched'}. Individual trial differences are not shown in this initial comparison.</p>
      </>}
    </section>
  )
}
