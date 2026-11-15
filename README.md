# The Unofficial Guide — Hybrid RAG

**CodePath AI201 | Unit 9 Capstone**
**Student:** Jean Pierre Joseph
**Selected Corpus:** `campus_life` | **Retrieval modes:** semantic and hybrid (BM25 + vector search + RRF)

A retrieval-augmented generation (RAG) application that answers questions using a collection of unofficial campus-life documents. It retrieves relevant passages, checks whether the question is supported by the corpus, and can generate a document-grounded answer with source references. Questions outside the available evidence are refused rather than answered from general model knowledge.

This repository extends the original Unit 1 and Unit 2 semantic RAG implementation with **BM25 keyword retrieval, Reciprocal Rank Fusion (RRF), hybrid search, structured request instrumentation, and repeatable semantic-versus-hybrid evaluation**.

> **Evaluation finding:** On the measured 10-question dataset, semantic and hybrid retrieval both achieved 15/15 in-scope top-1 expected-phrase matches and 15/15 correct out-of-scope gate decisions. Hybrid retrieval did **not** demonstrate an accuracy improvement and generally had higher median latency. These are retrieval-only findings, not a comparison of newly generated model answers.

## Features

- **Semantic retrieval:** ChromaDB vector search using `all-MiniLM-L6-v2` embeddings.
- **Keyword retrieval:** BM25 ranking over the existing document chunks.
- **Hybrid retrieval:** Reciprocal Rank Fusion combines BM25 and semantic candidate rankings without mixing their incompatible raw scores.
- **Relevance gate:** Uses semantic distance (cutoff `0.62`), **not** RRF score, to determine when to refuse unsupported questions.
- **Grounded generation:** Uses retrieved document context to answer supported questions and identify source documents.
- **CLI and HTTP interfaces:** `app.py` and `serve.py` provide application entry points.
- **Instrumentation:** Structured JSONL events capture request and outcome information, timing, and errors.
- **Evaluation and tests:** Repeatable retrieval comparisons and automated coverage of hybrid search, fusion, logging, and evaluation.

## Architecture

```text
                        User question
                              |
                 +------------+------------+
                 |                         |
          Semantic mode                Hybrid mode
                 |                         |
          ChromaDB search       +---------+---------+
                 |              |                   |
                 |          BM25 search       ChromaDB search
                 |              |                   |
                 |              +---------+---------+
                 |                        |
                 |               Reciprocal Rank Fusion
                 |                        |
                 +------------+-----------+
                              |
                   Retrieved document context
                              |
                 Semantic-distance relevance gate
                              |
                   +----------+----------+
                   |                     |
               Unsupported            Supported
                   |                     |
                Refusal          Grounded generation
                                         |
                                 Answer with sources
```

Hybrid search ranks candidate chunks using RRF. The gate continues to assess semantic-distance evidence, so an RRF score is **not** treated as a calibrated relevance threshold.

### Key modules

| File | Responsibility |
|---|---|
| `ingest.py` | Read corpus documents |
| `chunker.py` | Paragraph-aware document chunking |
| `store.py` | ChromaDB semantic retrieval |
| `hybrid.py` | BM25 retrieval and hybrid candidate assembly |
| `rrf.py` | Reciprocal Rank Fusion |
| `gate.py` | Semantic-distance relevance gate |
| `generate.py` | Document-grounded answer generation |
| `app.py` | Command-line entry point |
| `serve.py` | HTTP interface |
| `instrumentation.py` | Structured request and error logging |
| `unit9_compare.py` | Semantic/hybrid retrieval comparison |

## Dataset and configuration

| Setting | Current evaluated configuration |
|---|---|
| Corpus | `campus_life` |
| Source documents | 88 |
| Paragraph-aware chunks | 90 |
| Embedding model | `all-MiniLM-L6-v2` |
| Vector database | ChromaDB |
| Relevance cutoff | `0.62` |
| Default `top-k` | `1` |
| Tested Python environment | Python 3.12, Windows, `.venv312` |

The paragraph-aware chunker uses a **500-character target with zero overlap**, preserving complete paragraphs and splitting only longer documents. The existing index is reused for Unit 9; **do not rebuild it merely to run the retrieval examples or comparison**.

## Getting started

Follow [`RUNNING.md`](RUNNING.md) for the original environment setup and project-specific prerequisites. Use the existing configured Python environment, installed dependencies, corpus, and ChromaDB index.

From the project root on Windows PowerShell, the following commands run **retrieval only**, without model generation:

**Semantic retrieval**

```powershell
.\.venv312\Scripts\python.exe app.py --corpus campus_life retrieve "How much do washing and drying each cost at Old Brewhouse?" --retrieval semantic
```

**Hybrid retrieval**

```powershell
.\.venv312\Scripts\python.exe app.py --corpus campus_life retrieve "How much do washing and drying each cost at Old Brewhouse?" --retrieval hybrid
```

The `retrieve` and `ask` subcommands support `--retrieval semantic` and `--retrieval hybrid`; the default is semantic. To inspect the available answer-generation options without invoking a model:

```powershell
.\.venv312\Scripts\python.exe app.py --help
.\.venv312\Scripts\python.exe app.py ask --help
```

Answer generation may use a configured model provider and incur API usage. See [`RUNNING.md`](RUNNING.md) for the starter's setup details. No API key should be committed to Git.

## Automated tests

Run the six Unit 9 test modules:

```powershell
.\.venv312\Scripts\python.exe -m unittest test_hybrid test_rrf test_hybrid_pipeline test_instrumentation test_unit9_compare test_instrumentation_output
```

**Last verified result:** 39 tests passed (November 14, 2026). Tests cover BM25 retrieval, RRF, hybrid integration, instrumentation, output logging, and evaluation behavior.

## Semantic vs. hybrid evaluation

The evaluation used five in-scope and five out-of-scope questions, with three trials per question per retrieval mode: **60 retrieval records total**. Both modes used the same corpus and semantic relevance threshold.

| Metric | Semantic | Hybrid |
|---|---:|---:|
| In-scope trials | 15 | 15 |
| Correct in-scope gate decisions | 15/15 | 15/15 |
| Top-1 expected-phrase matches | 15/15 | 15/15 |
| Top-k expected-phrase matches | 15/15 | 15/15 |
| Correct out-of-scope gate decisions | 15/15 | 15/15 |
| In-scope mean retrieval latency | 54.444 ms | 52.573 ms |
| In-scope median retrieval latency | 41.615 ms | 51.586 ms |
| Out-of-scope mean retrieval latency | 40.748 ms | 51.013 ms |
| Out-of-scope median retrieval latency | 40.899 ms | 50.629 ms |

**Interpretation:** Both methods found the expected answer phrases and made the same gate decisions on this small test set. Hybrid retrieval's in-scope median latency was approximately **24% higher**, despite a slightly lower mean. Out-of-scope hybrid latency was higher by both measures. These measurements cover **local retrieval**, not end-to-end HTTP or model-generation latency. The evaluation did **not** make Gemini generation calls or establish answer-quality improvements.

Saved evidence:

- `results/unit9_compare_20261114-181537-592760.json`
- `results/unit9_compare_20261114-181537-592760.csv`
- `results/unit9_compare_20261114-181537-592760.md`

## Instrumentation

Structured JSONL events record applicable request inputs, outputs, timestamps, duration, status, retrieval context, and error details. This supports debugging and comparing behavior across retrieval modes.

The final Milestone 7 evidence contains **22 events**: 10 successful retrievals, 10 out-of-scope refusals, one HTTP validation error, and one Python exception. Retrieval and gate checks used the real local index; generation was **mocked** in this evidence run to avoid unnecessary model calls.

Evidence files:

- `results/milestone5_real_requests.jsonl`
- `results/milestone7_real_requests_20261114-182032.jsonl`

For production use, request logging would need sensitive-data redaction, access controls, retention/rotation, and centralized monitoring.

## Tradeoffs and limitations

- **Small benchmark:** Five supported and five unsupported questions cannot establish general retrieval superiority.
- **No observed accuracy gain:** Hybrid search did not improve expected-phrase matching in this evaluation.
- **Additional retrieval overhead:** The implementation prepares BM25 data during hybrid searches rather than relying on a persistent keyword index.
- **Generation quality not re-evaluated:** Unit 9's comparison does not measure newly generated answer accuracy or citation support.
- **`top-k=1` limitation:** A single retrieved chunk may be insufficient for questions requiring multiple sources.
- **Production readiness:** More robust monitoring, redaction, concurrency testing, and cost accounting would be needed before enterprise deployment.

Next steps include caching or persisting BM25 data, expanding the benchmark, evaluating multi-document questions, measuring answer citation support, and testing end-to-end latency under concurrent requests.

## Development history and supporting documentation

This project evolved through three course stages:

| Stage | Contribution |
|---|---|
| Unit 1 | Corpus inspection, paragraph-aware chunking, semantic retrieval, grounded generation, and a calibrated relevance gate |
| Unit 2 | Acceptance-criteria evaluation, reducing `TOP_K` from 5 to 1, and a measured fixed-window chunking experiment |
| Unit 9 | BM25, RRF, hybrid retrieval, structured instrumentation, comparison tests, and capstone documentation |

Unit 2 found that reducing `TOP_K` from 5 to 1 preserved all five original acceptance criteria on the measured questions while reducing retrieved context. A separate fixed-window chunking experiment performed worse than paragraph-aware chunking. Those results are historical experiments, not evidence that the current hybrid mode is universally superior.

- [`RUNNING.md`](RUNNING.md) — original setup and usage instructions (unchanged)
- [`criteria.md`](criteria.md) — original acceptance criteria (unchanged)
- [`docs/UNIT1_UNIT2_EXPERIMENTS.md`](docs/UNIT1_UNIT2_EXPERIMENTS.md) — archived Unit 1 and Unit 2 README evidence (add alongside this README)
- `results/` — saved evaluation and instrumentation evidence

## How I used AI

I used AI assistance to reason about BM25, semantic search, and RRF; plan changes; prepare controlled PowerShell inspections and backups; organize tests; and interpret evaluation results. I verified changes through local execution, reviewed source evidence rather than accepting generated conclusions, and committed implementation milestones after testing. AI assistance was a development aid, **not** a substitute for the code, test results, and saved evaluation evidence.

## Conclusion

The updated application provides two working retrieval approaches behind a common relevance gate and grounded-answer workflow. Hybrid retrieval adds a useful architectural option, but the measured dataset did not demonstrate an accuracy advantage over semantic search. The strongest outcome of the capstone is a **testable, instrumented retrieval pipeline** with documented tradeoffs and evidence-based conclusions.

## What This Extends

This capstone extends the earlier campus-life RAG system. The earlier system used document chunking, ChromaDB semantic retrieval, a relevance gate, and grounded answer generation.

Unit 9 adds BM25 keyword retrieval, Reciprocal Rank Fusion (RRF), semantic-versus-hybrid evaluation, structured request instrumentation, and a React/FastAPI evaluation dashboard.

The original semantic retrieval path remains available.

## The Shape

The primary local application has three layers:

- A: React/Vite frontend for submitting questions and viewing retrieval comparisons.
- B: FastAPI backend for validation, retrieval, comparison, and evaluation-report access.
- C: Local RAG components: document chunks, BM25, ChromaDB, RRF, and the semantic-distance relevance gate.

The dashboard's retrieval endpoints do not generate model answers. They evaluate retrieval results and gate decisions.

The original CLI and Flask interfaces remain separate run paths.

Out of scope for this capstone are production authentication, distributed deployment, and guarantees about generated-answer correctness based solely on retrieval evaluation.

## Running It

See [RUNNING.md](RUNNING.md), particularly "Current Unit 9 Dashboard", for the local startup procedure.

The verified development environment uses Python 3.12.7. The dashboard uses FastAPI on port 8000 and React/Vite on port 5173.

The local embedding system uses ChromaDB and all-MiniLM-L6-v2. The corpus and existing vector index must be available before retrieval can succeed.

## What It Costs

The Unit 9 comparison uses local retrieval without answer-generation model calls. Its report metadata records `generation_calls: 0`.

The existing comparison reports measure retrieval latency, not hosted-model billing. The historical Unit 2 experiments contain separate token-usage observations and should not be presented as Unit 9 API charges.

At 100 retrieval-only evaluations per day, the workload would be 100 times the measured per-evaluation retrieval work. This is a workload projection, not a verified cloud bill. Exact dollar cost depends on deployment infrastructure, power, hosting, and any additional model calls.

A defensible monetary estimate requires an explicitly stated pricing assumption and measured resource usage; no unverified dollar figure is claimed here.

## What's Still Broken

The current fixed-question comparison does not establish generated-answer correctness, source citation quality, or performance on questions requiring multiple independent source chunks.

The hybrid implementation rebuilds the BM25 index on each request. This may contribute to additional latency, but stage-level timing is needed to determine the dominant cost.

The benchmark is small and uses a fixed corpus. It does not establish production reliability, concurrency behavior, or performance under sustained load.

The first follow-up would be a broader evaluation containing questions that require evidence from multiple chunks. This would directly test the limitations of top-k=1 before optimizing retrieval speed.

## Unit 9 Performance Experiment — Advance Declaration

**Status:** Declared before implementing the performance instrumentation or optimization described below.

### Observed problem

The existing Unit 9 comparison shows that hybrid retrieval is slower than semantic retrieval on the current fixed-question dataset.

In the repeat comparison, the in-scope median was 42.066 ms for semantic retrieval and 51.051 ms for hybrid retrieval. The out-of-scope median was 41.926 ms for semantic retrieval and 49.440 ms for hybrid retrieval.

Both modes achieved the same expected-phrase and relevance-gate results on this dataset. These measurements do not establish generated-answer accuracy or prove which hybrid stage causes the additional latency.

### Planned diagnostic measurement

I will measure the following stages separately:

1. Document loading.
2. Document chunking.
3. BM25 construction and keyword search.
4. ChromaDB semantic retrieval.
5. Reciprocal Rank Fusion.
6. Relevance-gate evaluation.

I will retain the existing total `duration_ms` field for compatibility.

### Planned improvement

If stage measurements show that repeated BM25 construction is a significant cost, I will test reusing the BM25 index for repeated requests against the same corpus and chunking configuration.

The optimization must preserve retrieval ranking, source labels, semantic distances, and gate decisions.

If BM25 construction is not a significant cost, I will document that finding and select an improvement supported by the measured bottleneck instead.

### Evaluation method

I will compare before and after runs using the same corpus, questions, retrieval settings, top-k, threshold, and trial count.

I will record latency distributions and retrieval correctness separately. I will also run the existing automated tests and add targeted tests for any changed behavior.

A successful performance result requires lower hybrid latency without a regression in the measured retrieval outcomes. If the optimization does not help, I will report that result rather than claiming success.

### Additional stretch observation

After completing the required evaluation, I plan to test approximately ten times the normal request rate and record response times, failures, and resource observations where available.

The load test will use retrieval-only endpoints. It will not intentionally trigger paid model-generation calls.

### Evidence boundaries

The existing Unit 2 top-k improvement is historical evidence and is not a Unit 9 hybrid-performance optimization.

The current Unit 9 comparison reports are baseline evidence, not proof of the proposed improvement.

Stage timing, optimized results, and load-test results will be added only after they have been measured.

## Unit 9 Final Evaluation Evidence

### Baseline versus optimized retrieval

| Mode | Baseline mean | Final mean | Improvement |
|---|---:|---:|---:|
| Semantic | 46.154 ms | 27.402 ms | 40.63% |
| Hybrid | 52.067 ms | 25.030 ms | 51.93% |

Both benchmark runs contain 60 retrieval records: five in-scope
and five out-of-scope questions, three trials each, in both modes.

Each run achieved 60/60 correct gate decisions and 30/30
in-scope top-ranked expected-source matches.

### Five criteria and three-trial verdicts

| Criterion | Evidence | Verdict |
|---|---|---|
| U9-1 Hybrid source | 15/15 in-scope trials | MET |
| U9-2 Hybrid gate | 30/30 trials | MET |
| U9-3 Semantic regression | 15/15 sources, 30/30 gate | MET |
| U9-4 Timing | 60/60 records | MET |
| U9-5 Performance | 51.93% hybrid improvement | MET |

The individual question, trial, retrieval result, gate decision,
and timing records are available in the benchmark JSON files.

### Diagnosis and improvement

The original hybrid path performed repeated BM25 preparation.
Stage profiling identified additional cache-signature scanning
and ChromaDB client construction overhead.

The implemented improvements were BM25 index reuse,
`os.scandir` signature scanning, and process-local
ChromaDB client caching.

The measured improvements preserved the evaluated retrieval
correctness while reducing latency.

### Measured cost and daily projection

The optimized benchmark measured 27.402 ms per semantic
request and 25.030 ms per hybrid request.

At 100 retrieval-only requests per day:

- Semantic: 100 × 27.402 ms = 2.740 seconds
  of accumulated measured retrieval time per day.
- Hybrid: 100 × 25.030 ms = 2.503 seconds
  of accumulated measured retrieval time per day.

These measurements represent local elapsed retrieval time,
not CPU consumption or hosting cost.

No answer-generation model calls were made during these
benchmarks, so observed generation API charges were $0.
Hosting, electricity, and operational costs are not measured.

### Limitations and next priority

The evaluation uses only ten fixed questions and does not
measure generated-answer quality, concurrency, or sustained load.

A full-directory ChromaDB reset can fail on Windows when
database files are open. Isolated collection deletion and
rebuilding were verified successfully.

The next priority would be evaluating multi-document questions
and generated-answer citation quality.


## Unit 9 — What I Implemented

For my AI201 Unit 9 Capstone, I extended my existing
Retrieval-Augmented Generation (RAG) system with hybrid retrieval,
performance optimizations, instrumentation, and a comparison dashboard.

### Implemented Features

1. **Hybrid Search:** Combined semantic vector retrieval with BM25
   keyword retrieval using Reciprocal Rank Fusion (RRF).
2. **Relevance Protection:** Preserved the semantic-distance relevance
   gate to reject unsupported questions.
3. **Performance Optimization:** Implemented BM25 index caching,
   optimized cache-signature scanning, and ChromaDB client reuse.
4. **Instrumentation:** Added structured request logging,
   retrieval-stage timing, and error tracking.
5. **Evaluation:** Compared semantic and hybrid retrieval using
   60 recorded trials per benchmark.
6. **Visualization:** Added a React dashboard for comparing
   historical RAG evaluation results.

### Measured Results

| Metric | Before | After | Improvement |
|---|---:|---:|---:|
| Semantic retrieval | 46.154 ms | 27.402 ms | 40.63% |
| Hybrid retrieval | 52.067 ms | 25.030 ms | 51.93% |

- **60/60** correct relevance-gate decisions per benchmark.
- **30/30** expected top-ranked source matches per benchmark.
- **55** automated Python tests passed.

### Implementation Evidence

| Evidence | Location |
|---|---|
| Acceptance criteria and verdicts | `criteria.md` |
| Execution instructions | `RUNNING.md` |
| Hybrid retrieval implementation | `hybrid.py` |
| BM25 caching | `hybrid_cache.py` |
| ChromaDB client reuse | `store.py` |
| Retrieval instrumentation | `retrieval_timing.py` |
| Benchmark implementation | `unit9_compare.py` |
| Recorded benchmark results | `results/` |
| Development history | Git commit history |

The evaluation focuses on retrieval quality and performance.
It does not establish end-to-end generated-answer accuracy.

---

### Benchmark evidence

- Baseline: `results/unit9_compare_20261114-213958-711410.json`
- Final: `results/unit9_compare_20261114-221740-516295.json`

The criteria in `criteria.md` were documented retrospectively;
they are not represented as pre-experiment declarations.
