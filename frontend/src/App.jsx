import { useEffect, useRef, useState } from 'react'
import { ragApi } from './services/ragApi'
import HistoricalComparison from './components/HistoricalComparison'
import './App.css'

function ResultCard({ document, mode }) {
  const [expanded, setExpanded] = useState(false)

  const score = mode === 'semantic'
    ? document.distance
    : document.rrf_score

  return (
    <article className="document-card">
      <div className="document-header">
        <span className="rank">#{document.rank}</span>
        <div className="document-title">
          <strong>{document.source}</strong>
          <small>{document.label}</small>
        </div>
      </div>

      <div className="document-metadata">
        <span>
          {mode === 'semantic' ? 'Cosine distance' : 'RRF score'}:
          {' '}{typeof score === 'number' ? score.toFixed(4) : 'N/A'}
        </span>
        {mode === 'hybrid' && (
          <span>
            Semantic rank: {document.semantic_rank ?? '—'}
            {' · '}
            Keyword rank: {document.keyword_rank ?? '—'}
          </span>
        )}
      </div>

      <p className="document-preview">
        {expanded
          ? document.text
          : `${document.text.slice(0, 220)}${document.text.length > 220 ? '…' : ''}`}
      </p>

      <button
        className="text-button"
        type="button"
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? 'Show less' : 'View full chunk'}
      </button>
    </article>
  )
}

function ResultsPanel({ title, result }) {
  if (!result) return null

  return (
    <section className="results-panel">
      <div className="panel-heading">
        <h2>{title}</h2>
        <span className={result.gate.passed ? 'status passed' : 'status refused'}>
          {result.gate.passed ? 'Gate passed' : 'Gate refused'}
        </span>
      </div>

      <div className="metrics">
        <div>
          <small>Retrieval time</small>
          <strong>{result.duration_ms.toFixed(2)} ms</strong>
        </div>
        <div>
          <small>Documents</small>
          <strong>{result.result_count}</strong>
        </div>
        <div>
          <small>Best semantic distance</small>
          <strong>{result.gate.best_distance.toFixed(4)}</strong>
        </div>
      </div>

      <p className="gate-explanation">{result.gate.explanation}</p>

      {result.documents.length === 0 ? (
        <p>No documents returned.</p>
      ) : (
        <div className="document-list">
          {result.documents.map((document) => (
            <ResultCard
              key={`${result.retrieval}-${document.label}`}
              document={document}
              mode={result.retrieval}
            />
          ))}
        </div>
      )}
    </section>
  )
}

function RankingComparison({ result }) {
  const semantic = result.semantic
  const hybrid = result.hybrid
  const comparison = result.rank_comparison

  const shared = comparison.filter(
    (item) => item.semantic_rank != null && item.hybrid_rank != null
  )

  const semanticOnly = comparison.filter(
    (item) => item.semantic_rank != null && item.hybrid_rank == null
  )

  const hybridOnly = comparison.filter(
    (item) => item.semantic_rank == null && item.hybrid_rank != null
  )

  const overlapPercent = semantic.result_count
    ? (shared.length / semantic.result_count) * 100
    : 0

  const latencyDifference = hybrid.duration_ms - semantic.duration_ms

  function movement(item) {
    if (item.semantic_rank == null) {
      return { label: 'Hybrid only', type: 'unique' }
    }

    if (item.hybrid_rank == null) {
      return { label: 'Semantic only', type: 'unique' }
    }

    const difference = item.semantic_rank - item.hybrid_rank

    if (difference > 0) {
      return { label: `Up ${difference}`, type: 'up' }
    }

    if (difference < 0) {
      return { label: `Down ${Math.abs(difference)}`, type: 'down' }
    }

    return { label: 'Unchanged', type: 'same' }
  }

  return (
    <div className="card rank-comparison">
      <div className="comparison-heading">
        <div>
          <h2>Ranking Comparison</h2>
          <p>
            Compare document overlap, rank movement, and retrieval latency.
          </p>
        </div>
      </div>

      <div className="comparison-metrics">
        <div className="comparison-metric">
          <small>Shared documents</small>
          <strong>{shared.length}</strong>
          <span>{overlapPercent.toFixed(1)}% of Semantic results</span>
        </div>

        <div className="comparison-metric">
          <small>Semantic only</small>
          <strong>{semanticOnly.length}</strong>
          <span>Not returned by Hybrid</span>
        </div>

        <div className="comparison-metric">
          <small>Hybrid only</small>
          <strong>{hybridOnly.length}</strong>
          <span>Not returned by Semantic</span>
        </div>

        <div className="comparison-metric">
          <small>Latency difference</small>
          <strong>
            {latencyDifference > 0 ? '+' : ''}
            {latencyDifference.toFixed(2)} ms
          </strong>
          <span>
            {latencyDifference > 0
              ? 'Hybrid took longer'
              : latencyDifference < 0
                ? 'Hybrid was faster'
                : 'Equal reported duration'}
          </span>
        </div>
      </div>

      <div className="comparison-latencies">
        <span>
          Semantic: <strong>{semantic.duration_ms.toFixed(2)} ms</strong>
        </span>
        <span>
          Hybrid: <strong>{hybrid.duration_ms.toFixed(2)} ms</strong>
        </span>
      </div>

      <div className="table-scroll">
        <table className="comparison-table">
          <thead>
            <tr>
              <th>Document chunk</th>
              <th>Semantic rank</th>
              <th>Hybrid rank</th>
              <th>Movement</th>
            </tr>
          </thead>

          <tbody>
            {comparison.map((item) => {
              const change = movement(item)

              return (
                <tr key={item.label}>
                  <td>{item.label}</td>
                  <td>{item.semantic_rank ?? '—'}</td>
                  <td>{item.hybrid_rank ?? '—'}</td>
                  <td>
                    <span className={`movement movement-${change.type}`}>
                      {change.label}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <p className="comparison-note">
        Rank movement is measured from Semantic to Hybrid.
        Up means a better numerical rank. Latency is the reported
        retrieval duration, not a benchmark average.
      </p>
    </div>
  )
}
function HistoricalEvaluation() {
  const [reports, setReports] = useState([])
  const [selected, setSelected] = useState('')
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    ragApi.evaluations()
      .then((data) => {
        if (!active) return

        const items = data.reports ?? []
        setReports(items)

        if (items.length) {
          setSelected(items[0].id)
        } else {
          setLoading(false)
        }
      })
      .catch((err) => {
        if (active) {
          setError(err.message)
          setLoading(false)
        }
      })

    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    if (!selected) return

    let active = true

    ragApi.evaluation(selected)
      .then((data) => {
        if (active) {
          setReport(data)
          setError('')
        }
      })
      .catch((err) => {
        if (active) {
          setReport(null)
          setError(err.message)
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })

    return () => {
      active = false
    }
  }, [selected])

  return (
    <section className="card historical-evaluation">
      <div className="section-heading">
        <div>
          <h2>Historical Evaluation</h2>
          <p>Saved Unit 9 evaluation runs. Read-only.</p>
        </div>
      </div>

      <label>
        Evaluation report
        <select
          value={selected}
          disabled={!reports.length}
          onChange={(event) => {
            setReport(null)
            setLoading(true)
            setSelected(event.target.value)
          }}
        >
          {!reports.length && (
            <option value="">
              No reports available
            </option>
          )}

          {reports.map((item) => (
            <option key={item.id} value={item.id}>
              {item.id}
            </option>
          ))}
        </select>
      </label>

      {loading && (
        <p role="status">Loading evaluation...</p>
      )}

      {error && (
        <p className="evaluation-error" role="alert">
          {error}
        </p>
      )}

      {!loading && !error && !report && (
        <p>No historical evaluation report found.</p>
      )}

      {report && !loading && (
        <>
          <div className="evaluation-metadata">
            <span>
              Corpus: <strong>{report.metadata.corpus}</strong>
            </span>

            <span>
              Variant: <strong>{report.metadata.variant}</strong>
            </span>

            <span>
              Top-K: <strong>{report.metadata.top_k}</strong>
            </span>

            <span>
              Runs: <strong>{report.metadata.runs}</strong>
            </span>

            <span>
              Records: <strong>{report.records.length}</strong>
            </span>

            <span>
              Generation calls:
              <strong> {report.metadata.generation_calls}</strong>
            </span>
          </div>

          <h3>Evaluation summary</h3>

          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Mode</th>
                  <th>Scope</th>
                  <th>Trials</th>
                  <th>Gate correct</th>
                  <th>Expected phrase Top-1</th>
                  <th>Expected phrase Top-K</th>
                  <th>Mean ms</th>
                  <th>Median ms</th>
                </tr>
              </thead>

              <tbody>
                {report.summary.map((row) => (
                  <tr key={`${row.mode}-${row.scope}`}>
                    <td>{row.mode}</td>
                    <td>{row.scope}</td>
                    <td>{row.trials}</td>

                    <td>
                      {row.gate_correct} / {row.trials}
                    </td>

                    <td>
                      {row.expected_source_top1} / {row.trials}
                    </td>

                    <td>
                      {row.expected_source_topk} / {row.trials}
                    </td>

                    <td>
                      {Number(row.mean_ms).toFixed(2)}
                    </td>

                    <td>
                      {Number(row.median_ms).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h3>Individual trials</h3>

          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Mode</th>
                  <th>Scope</th>
                  <th>Trial</th>
                  <th>Question</th>
                  <th>Gate</th>
                  <th>Top-1 phrase</th>
                  <th>Top-K phrase</th>
                  <th>Latency ms</th>
                </tr>
              </thead>

              <tbody>
                {report.records.map((row, index) => (
                  <tr
                    key={`${row.mode}-${row.scope}-${row.trial}-${index}`}
                  >
                    <td>{row.mode}</td>
                    <td>{row.scope}</td>
                    <td>{row.trial}</td>
                    <td>{row.question}</td>

                    <td>
                      {row.gate_correct ? 'Correct' : 'Incorrect'}
                    </td>

                    <td>
                      {row.expected_source_top1 ? 'Yes' : 'No'}
                    </td>

                    <td>
                      {row.expected_source_topk ? 'Yes' : 'No'}
                    </td>

                    <td>
                      {Number(row.duration_ms).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="comparison-note">
            Expected-phrase matches are text-based proxies,
            not manually verified Precision@K or Recall@K.
            Latency reflects the original experiment.
          </p>
        </>
      )}
    </section>
  )
}
function App() {
  const [config, setConfig] = useState(null)
  const [health, setHealth] = useState(null)
  const [question, setQuestion] = useState(
    'What are the exam arrangements for HIST 118?'
  )
  const [index, setIndex] = useState('')
  const [mode, setMode] = useState('compare')
  const [topK, setTopK] = useState(5)
  const [threshold, setThreshold] = useState(0.62)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [initializing, setInitializing] = useState(true)
  const requestIdRef = useRef(0)

  const selectedIndex = config?.indexes.find(
    (item) => `${item.corpus}::${item.variant}` === index
  )

  const resultMatchesInputs = Boolean(
    result &&
    selectedIndex &&
    result.question === question.trim() &&
    result.corpus === selectedIndex.corpus &&
    result.variant === selectedIndex.variant &&
    result.semantic?.top_k === Number(topK) &&
    result.semantic?.threshold === Number(threshold)
  )

  const resultsOutdated = Boolean(result && !resultMatchesInputs)

  useEffect(() => {
    let active = true

    async function initialize() {
      try {
        const [healthData, configData] = await Promise.all([
          ragApi.health(),
          ragApi.config(),
        ])

        if (!active) return

        setHealth(healthData)
        setConfig(configData)

        const preferred = configData.indexes.find(
          (item) =>
            item.corpus === configData.defaults.corpus &&
            item.variant === configData.defaults.variant
        )

        const first = preferred ?? configData.indexes[0]

        if (first) {
          setIndex(`${first.corpus}::${first.variant}`)
        }

        setThreshold(configData.defaults.threshold)
      } catch (err) {
        if (active) setError(err.message)
      } finally {
        if (active) setInitializing(false)
      }
    }

    initialize()

    return () => {
      active = false
    }
  }, [])

  async function runSearch(event) {
    event.preventDefault()

    if (!question.trim() || !index) return

    const selected = config.indexes.find(
      (item) => `${item.corpus}::${item.variant}` === index
    )

    if (!selected) {
      setError('Select a valid indexed corpus.')
      return
    }

    const payload = {
      question: question.trim(),
      corpus: selected.corpus,
      variant: selected.variant,
      top_k: Number(topK),
      threshold: Number(threshold),
    }

    const requestId = ++requestIdRef.current

    setLoading(true)
    setError('')
    setResult(null)

    try {
      // Fetch both modes once; the selector only controls presentation.
      const response = await ragApi.compare(payload)

      if (requestId === requestIdRef.current) {
        setResult(response)
      }
    } catch (err) {
      if (requestId === requestIdRef.current) {
        setError(err.message)
      }
    } finally {
      if (requestId === requestIdRef.current) {
        setLoading(false)
      }
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <span className="eyebrow">AI201 · PROJECT09</span>
          <h1>RAG Evaluation Studio</h1>
          <p>Explore, inspect, and compare retrieval strategies.</p>
        </div>

        <div className="connection-status">
          <span className={health?.index_ready ? 'dot online' : 'dot'} />
          {health?.index_ready ? 'Index ready' : 'Not connected'}
        </div>
      </header>

      <main className="main-content">
        <section className="card">
          <div className="section-heading">
            <div>
              <h2>Retrieval Playground</h2>
              <p>Configure your retrieval experiment.</p>
            </div>
          </div>

          <form onSubmit={runSearch}>
            <div className="form-grid">
              <label>
                Indexed corpus
                <select
                  value={index}
                  onChange={(event) => setIndex(event.target.value)}
                  disabled={loading || initializing}
                >
                  {config?.indexes.length ? (
                    config.indexes.map((item) => (
                      <option
                        key={item.collection}
                        value={`${item.corpus}::${item.variant}`}
                      >
                        {item.corpus} / {item.variant}
                      </option>
                    ))
                  ) : (
                    <option value="">No indexed corpus available</option>
                  )}
                </select>
              </label>

              <label>
                Retrieval mode
                <select
                  value={mode}
                  onChange={(event) => setMode(event.target.value)}
                  disabled={loading}
                >
                  <option value="compare">Compare both</option>
                  <option value="semantic">Semantic</option>
                  <option value="hybrid">Hybrid (BM25 + RRF)</option>
                </select>
              </label>

              <label>
                Top-K: {topK}
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={topK}
                  onChange={(event) => setTopK(Number(event.target.value))}
                  disabled={loading}
                />
              </label>

              <label>
                Relevance threshold: {Number(threshold).toFixed(2)}
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={threshold}
                  onChange={(event) => setThreshold(Number(event.target.value))}
                  disabled={loading}
                />
              </label>
            </div>

            <label className="question-label">
              Your question
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                rows="3"
                maxLength="2000"
                placeholder="Enter a question about your indexed documents..."
                disabled={loading}
              />
            </label>

            <div className="form-footer">
              <p>Retrieval only · No Gemini API call</p>
              <button
                className="primary-button"
                type="submit"
                disabled={loading || initializing || !index || !question.trim()}
              >
                {loading ? 'Running retrieval…' : 'Run retrieval'}
              </button>
            </div>
          </form>
        </section>

        {error && (
          <div className="error-message" role="alert">
            <strong>Request failed</strong>
            <p>{error}</p>
          </div>
        )}

        {resultsOutdated && (
          <div className="empty-state" role="status">
            <h2>Settings changed</h2>
            <p>
              These inputs differ from the last retrieval.
              Run retrieval again to update the results.
            </p>
          </div>
        )}

        {resultMatchesInputs && (
          <section className="results-section">
            <div className="section-heading">
              <div>
                <h2>Retrieval Results</h2>
                <p>Scores and rankings returned by your Project09 engine.</p>
              </div>
            </div>

            <div className={mode === 'compare' ? 'comparison-grid' : 'single-grid'}>
              {(mode === 'compare' || mode === 'semantic') && (
                <ResultsPanel
                  title="Semantic Search"
                  result={result.semantic}
                />
              )}
              {(mode === 'compare' || mode === 'hybrid') && (
                <ResultsPanel
                  title="Hybrid Search"
                  result={result.hybrid}
                />
              )}
            </div>

            {mode === 'compare' && (
              <RankingComparison result={result} />
            )}
          </section>
        )}

        {!result && !error && !loading && (
          <div className="empty-state">
            <h2>Ready to evaluate</h2>
            <p>Choose your settings and run a retrieval experiment.</p>
          </div>
        )}
        <HistoricalEvaluation />
        <HistoricalComparison />
      </main>
    </div>
  )
}

export default App
