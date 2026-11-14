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
