# The Unofficial Guide

**Student:** Jean Pierre Joseph
**Selected corpus:** `campus_life`

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

The Unofficial Guide is a retrieval-augmented generation system built over the campus_life corpus, a collection of 88 short documents containing unofficial student information. It answers questions about administrative procedures, dining halls, courses, housing, transportation, study resources, and other aspects of campus life. When a user asks a question, the system searches a local vector store for semantically related document chunks and uses the retrieved information to generate a grounded answer. Each generated answer identifies the source document so the user can see where the information came from.

## Chunking Strategy

**Chunk size:** 500 characters  
**Overlap:** 0 characters

The starter used fixed 800-character windows with 120 characters of overlap.
On the `campus_life` corpus, it produced 88 chunks from 88 documents, with
chunk lengths ranging from 178 to 549 characters. Because almost every
document was shorter than the starter limit, the starter kept every document
as one chunk.

When I read the documents and inspected five starter chunks, I found that the
posts were short and usually focused on one course, residence, dining hall, or
administrative subject. The sampled chunks contained complete thoughts, so I
did not want to divide every document into smaller sentence-level pieces.
However, the longer housing documents contained several paragraph-level
subtopics, including building information, advantages, problems, laundry, and
noise.

I replaced the fixed-character starter with a paragraph-aware strategy using a
500-character target. It keeps 86 of the 88 documents intact and splits only
the two longer, multi-topic housing documents:
`housing_innisfree_hall.txt` and `housing_old_brewhouse.txt`. Splits occur only
between paragraphs, so the function does not cut sentences at arbitrary
character positions.

I selected zero character overlap because the strategy preserves complete
paragraphs rather than sliding character windows. When a document produces
more than one chunk, its title is repeated at the beginning of the later chunk
so that the subject remains identifiable without duplicating the surrounding
content. The final strategy produced 90 chunks averaging 310 characters, with
lengths ranging from 170 to 461 characters.

## Sample Chunks

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```text
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_biol_160_exams.txt#0` — produced by: `chunker.py::split_documents`

```text
BIOL 160 Cell Biology — assessment

Four unit tests and a cumulative final. Not curved.

The unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** — source: `course_math_220_exams.txt#0` — produced by: `chunker.py::split_documents`

```text
MATH 220 Linear Algebra — assessment

Two midterms and a cumulative final. Curved to a b- median.

The problem sets are the course; the lectures make sense afterwards rather than during.
```

**Chunk 4** — source: `dining_the_ridgeway_cafe.txt#0` — produced by: `chunker.py::split_documents`

```text
The Ridgeway Café

Second-year here. Wait times: 10 to 15 minutes at 12:30, none after 2:00. The thing worth going for is the only place on campus with real espresso. The thing to know is that seating is tight; about 40 seats for a building of 900.

Hours are 7:00am to 4:00pm weekdays only. Costs declining balance only, no meal swipes.
```

**Chunk 5** — source: `housing_morrow_house.txt#0` — produced by: `chunker.py::split_documents`

```text
Morrow House — what it's actually like

Just finished a year in this building. Built 1954, partially renovated 2008. Rooms are singles and doubles, hallbathrooms.

The good: cheapest housing tier by about $900 a year, and the singles are real singles.

The bad: known damp problem on the ground floor; two rooms were taken offline in 2024.

Laundry costs $1.50 wash, $1.25 dry, coin or card. On noise: loud until about 1am on weekends, no enforced quiethours.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:**
How much do washing and drying each cost at Old Brewhouse?

**Answer:**

```text
At Old Brewhouse, both washing and drying cost $1.50 each (housing_old_brewhouse.txt and housing_old_brewhouse_laundry.txt).

Sources retrieved: housing_calder_annexe_laundry.txt, housing_fenwick_court_laundry.txt, housing_innisfree_hall_laundry.txt, housing_old_brewhouse.txt, housing_old_brewhouse_laundry.txt
```

The best retrieved distance was `0.221`, which passed the final relevance
cutoff of `0.62`. The generated answer was supported by
`housing_old_brewhouse.txt` and `housing_old_brewhouse_laundry.txt`, and it
named both source documents.

I also tested the relevance gate with the out-of-corpus question, “What is the
capital of Mongolia?” Its best distance was `0.825`, so the gate stopped it and
returned:

```text
I don't have enough information about that.
```

The refusal used zero model calls.

**My relevance cutoff:** `0.62`

The highest best distance among the five in-corpus questions was `0.4158`.
The lowest best distance among the five out-of-corpus questions was `0.8246`.
This created a gap of `0.4088`. I selected `0.62` because it is approximately
the midpoint of that gap:

```text
(0.4158 + 0.8246) / 2 = 0.6202
```

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

This cutoff allowed all five in-corpus questions to pass and caused all five
out-of-corpus questions to be refused.

| Question                                                                                 | In corpus? | Best distance |
| ---------------------------------------------------------------------------------------- | ---------- | ------------- |
|                                                                                          |            |               |
| How are juniors and seniors ordered in the housing lottery?                              | Yes        | 0.2250        |
| How long is the wait at Kestrel Commons between 12:15 and 1:00?                          | Yes        | 0.2129        |
| Why should students complete the CS 210 labs even though they are only 10% of the grade? | Yes        | 0.4158        |
| How much do washing and drying each cost at Old Brewhouse?                               | Yes        | 0.2213        |
| Which campus shuttle stop may be skipped when the driver is behind schedule?             | Yes        | 0.3853        |
| What is the capital of Mongolia?                                                         | No         | 0.8246        |
| How do I change the oil in a diesel engine?                                              | No         | 0.9340        |
| Who won the 1994 World Cup?                                                              | No         | 0.8859        |
| What is the recommended dosage of ibuprofen for a headache?                              | No         | 0.8442        |
| How do I write a for loop in Rust?                                                       | No         | 0.8960        |

## How I Used AI

**1.** Understanding the provided corpora: I asked AI where the documents created by python app.py corpora came from and whether every student received the same text. AI explained that the corpora were supplied with the starter project and were written for the course rather than downloaded from the internet. I compared that explanation with corpora/README.md, which confirmed that the documents were course-created and that no real people were named. This helped me understand that campus_life was a fixed project dataset rather than live university information.

**2.** Evaluating the starter chunking behavior: I asked AI to help me examine four campus_life documents and distinguish direct observations from chunking interpretations. The initial interpretation was that a complete document might be a reasonable chunk because the documents were short and focused. I did not accept that as a final chunking decision. I ran the starter index and recorded that 88 documents produced 88 chunks, with lengths ranging from 178 to 549 characters. I kept the conclusion preliminary until I could implement and inspect my own chunking strategy in Milestone 3.

**3.** For Unit 2, I used AI to help organize the run logs and question whether the scorer’s phrase matches proved my acceptance criteria. I checked the verdicts against the saved answers, retrieved chunks, source documents, and original criteria. AI also helped me identify the risk of using only one retrieved chunk.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

## Run Log — Before

I ran `python run_eval.py --label before` against `campus_life` with `top-k: 5` and a relevance cutoff of `0.62`. Each in-corpus question was asked three times with caching off. The complete report is in `results/run_2026-09-23_2103_before.md`.

| Criterion                                               | Original target | Run 1 | Run 2 | Run 3 | Before verdict |
| ------------------------------------------------------- | --------------- | ----- | ----- | ----- | -------------- |
| 1. Retrieved chunks contain the answer                  | 4 of 5          | 5/5   | 5/5   | 5/5   | **MET**        |
| 2. Every answer names a source                          | 5 of 5          | 5/5   | 5/5   | 5/5   | **MET**        |
| 3. Gate refuses out-of-corpus questions                 | 4 of 5          | 5/5   | 5/5   | 5/5   | **MET**        |
| 4. Sampled chunks stand alone and have intact sentences | 4 of 5          | 5/5   | 5/5   | 5/5   | **MET**        |
| 5. Named documents support the answers                  | 4 of 5          | 5/5   | 5/5   | 5/5   | **MET**        |

Retrieval, the relevance gate, and the five-chunk sample were deterministic in this test, so their counts repeat across the three columns. I checked source naming and source support against the generated answers from all three runs. A `pass` from `scorer.py` alone was not enough to establish all five criteria: that scorer only checks for the expected phrase in the generated answer.

### Real output — before

The answers and gate results below were produced by `run_eval.py::main` and `run_eval.py::check_out_of_scope`. Retrieved passages came from `store.py::search`; chunks were produced by `chunker.py::split_documents`. The full 15-answer output is in `results/run_2026-09-23_2103_before.md`.

**Criteria 1, 2, and 5 — answer-bearing chunk, generated answer, and supporting source:**

```text
Question: Which campus shuttle stop may be skipped when the driver is behind schedule?

RETRIEVED: transit_shuttle.txt#0
DISTANCE: 0.3853
It's free with a student ID. The stop outside Fenwick Court is the one
that gets skipped when the driver is behind, which is worth knowing
if you live there.

Run 1 answer:
The stop outside Fenwick Court may be skipped when the driver is behind
schedule (from transit_shuttle.txt).
```

The text above is in the retrieved chunk and in the named `transit_shuttle.txt` document. I also checked the answer-bearing chunk and named documents for the other four questions.

**Criterion 3 — out-of-corpus gate output:**

```text
What is the capital of Mongolia? | best distance 0.825 | refused
How do I change the oil in a diesel engine? | best distance 0.934 | refused
Who won the 1994 World Cup? | best distance 0.886 | refused
What is the recommended dosage of ibuprofen for a headache? | best distance 0.844 | refused
How do I write a for loop in Rust? | best distance 0.896 | refused
```

**Criterion 4 — one of the five sampled chunks:** Produced by `chunker.py::split_documents` and printed by `python app.py --corpus campus_life chunks -n 5`.

```text
Chunk 2 | source: course_biol_160_exams.txt#0
BIOL 160 Cell Biology — assessment

Four unit tests and a cumulative final. Not curved.

The unit tests come fast, roughly every three weeks; falling behind once
is very hard to recover from.
```

This chunk can answer “How many unit tests does BIOL 160 have?” without a neighboring chunk. I inspected all five printed chunks for a standalone answerable fact and intact sentence boundaries.

## Verdicts

| #   | Criterion                        | Verdict | How I decided                                                     |
| --- | -------------------------------- | ------- | ----------------------------------------------------------------- |
| 1   | Answer in retrieved chunks       | MET     | Answer found for 5/5 questions in all three runs.                 |
| 2   | Answer names a source            | MET     | All 15 answers named a document.                                  |
| 3   | Gate refuses unrelated questions | MET     | The gate refused 5/5.                                             |
| 4   | Chunks stand alone               | MET     | All five sampled chunks were answerable and had intact sentences. |
| 5   | Named source supports answer     | MET     | Sources supported 5/5 answers in all three runs.                  |

I made no revisions to the original criteria in `criteria.md`.

## Diagnoses

None of my five original acceptance criteria was missed, so there was no failed criterion to assign to a pipeline stage. These targets were safe for this particular five-question set: the answer was already in the first retrieved chunk for every question.

I did find a **retrieval-stage weakness** that the original targets did not count as a miss. For the shuttle question, `store.py::search` returned the correct `transit_shuttle.txt#0` chunk first, followed by four dining chunks that did not answer the question. The mechanism was that `TOP_K = 5` included the four next-ranked chunks even though the first chunk already contained the full answer. I chose to measure whether reducing that extra context preserved the five original targets.

## The Improvement

**What I changed:** I changed only the RAG setting `TOP_K` in `config.py` from `5` to `1`. The corpus, existing index, chunking strategy, embedding model, five questions, scorer, relevance cutoff, and grounding prompt remained the same.

**Why I picked it:** The before-run diagnosis showed four unnecessary dining chunks retrieved with the shuttle answer. Since the first chunk contained the answer for each of my five questions, I tested whether retrieving one chunk would remove those distractors without losing answer facts or source citations. One chunk might be insufficient for questions that need multiple sources; the after run tests only the existing five questions.

### Run Log — After

I ran `python run_eval.py --corpus campus_life --label after` with `top-k: 1`, the same `0.62` cutoff, and three uncached runs per question. The complete report is `results/run_2026-09-25_1815_after.md`.

| Criterion                                               | Original target | Run 1 | Run 2 | Run 3 | Verdict |
| ------------------------------------------------------- | --------------: | ----: | ----: | ----: | ------- |
| 1. Retrieved chunks contain the answer                  |    At least 4/5 |   5/5 |   5/5 |   5/5 | MET     |
| 2. Every answer names a source                          |             5/5 |   5/5 |   5/5 |   5/5 | MET     |
| 3. Gate stops out-of-corpus questions                   |    At least 4/5 |   5/5 |   5/5 |   5/5 | MET     |
| 4. Sampled chunks stand alone and have intact sentences |    At least 4/5 |   5/5 |   5/5 |   5/5 | MET     |
| 5. Named document supports the answer                   |    At least 4/5 |   5/5 |   5/5 |   5/5 | MET     |

The chunk sample for criterion 4 did not change because `TOP_K` affects retrieval count, not chunk creation. The out-of-corpus gate again refused 5/5. I inspected each generated answer for its source and checked the supporting source documents.

**Real after-run output:** Produced by `run_eval.py::main`, with retrieval from `store.py::search` and chunks from `chunker.py::split_documents`.

```text
Question: How long is the wait at Kestrel Commons between 12:15 and 1:00?
Run 1 — best distance: 0.2129 (passed the gate)
Sources retrieved: dining_kestrel_commons_followup.txt

The wait at Kestrel Commons between 12:15 and 1:00 is 20 to 25 minutes.

Source: dining_kestrel_commons_followup.txt
```

The sole retrieved chunk, `dining_kestrel_commons_followup.txt#0`, says that the wait is “20 to 25 minutes between 12:15 and 1:00.” The generated answer names that supporting document.

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

On these five questions, reducing `TOP_K` from 5 to 1 removed four extra chunks per question while all five original criteria remained MET in all three runs. The completed `TOP_K = 5` repeat reported 10,114 session tokens, compared with 3,833 for the `TOP_K = 1` after run—about 62% fewer session tokens. Those totals are from two separate runs, so they are evidence of reduced context use here, not an exact per-answer cost estimate. The best distances were unchanged because the closest chunk stayed the same.

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

No original criterion remained missed after the improvement. The test set does not check questions whose answers require two distinct chunks or documents. `TOP_K = 1` could fail such a question by withholding a needed second passage. I stopped after one pipeline change so I could measure its effect without mixing in another change. My next test would specify a question requiring two source facts before running it, then compare the retrieved evidence and answer at `TOP_K = 1` and a larger value.

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

For a future evaluation, I would tighten criterion 1 to require the **first** retrieved chunk to contain the answer for at least four of five questions, rather than allowing the answer anywhere among five results. I would also include a question whose complete answer requires more than one chunk, with its expected facts written before testing. These are lessons for a future test; I did not rewrite my original Unit 1 target after seeing the results.

### Stretch feature declared before implementation

I will test a second chunking strategy as a separate index variant. My
`TOP_K = 1` result depends entirely on the first chunk containing enough
context. I will keep the same five questions and acceptance targets, run each
three times against the new variant, and compare the third run log with my
`TOP_K = 1` after log. I will report whether the change helped, hurt, or made
no measurable difference.

## Bonus — Second Measured Improvement

I declared this experiment in the README before implementing it. I built the
`fixed300` index with `build_bonus_index.py`, using
`chunker.py::fallback_split`: 300-character windows and 60-character overlap.
It produced 164 chunks, compared with 90 from the paragraph-aware strategy.
I kept `TOP_K = 1`, the five questions, the embedding model, and the 0.62
cutoff unchanged.

I ran `python run_eval.py --corpus campus_life --variant fixed300 --label
bonus_fixed300`. The complete three-run report is
`results/run_2026-09-25_2207_bonus_fixed300.md`. The five fixed-window sample
chunks are in `results/bonus_fixed300_chunks.txt`.

| Criterion                                              | Original target | Run 1 | Run 2 | Run 3 | Verdict |
| ------------------------------------------------------ | --------------: | ----: | ----: | ----: | ------- |
| 1. Retrieved chunks contain the answer                 |    At least 4/5 |   4/5 |   4/5 |   4/5 | MET     |
| 2. Every answer names a source                         |             5/5 |   5/5 |   5/5 |   5/5 | MET     |
| 3. Gate stops out-of-corpus questions                  |    At least 4/5 |   5/5 |   5/5 |   5/5 | MET     |
| 4. Chunk quality, revised variant-specific measurement |    At least 4/5 |   1/5 |   1/5 |   1/5 | MISSED  |
| 5. Named source supports the expected answer           |    At least 4/5 |   4/5 |   4/5 |   4/5 | MET     |

Criterion 4's **original command**, if run literally, still samples the
paragraph-aware chunker and scores 5/5. It cannot measure the `fixed300`
variant. The revised, variant-specific sample scores 1/5. The unchanged 4/5
target is applied to the strategy actually used for this bonus index.

**Real output:** `run_eval.py::main` used `store.py::search` against the
`fixed300` index, whose chunks were produced by
`chunker.py::fallback_split`. For the shuttle question, run 1 recorded:

```text
Best distance: 0.4537 (passed the gate)
Sources retrieved: transit_shuttle.txt

I do not have enough information to answer this question from the provided document. (Source: transit_shuttle.txt)
```

Inspection of the exact retrieved `transit_shuttle.txt#0` chunk showed that
it ends:

```text
It's free with a student ID. The stop outside Fenwick Court is the one that ge
```

The source document contains the answer, but this retrieved chunk stops
before the stop's name appears. The phrase scorer failed the shuttle
question in all three runs. For criterion 5, I count only the four correct
answers as supported answers; the shuttle refusal does not answer its
question.

The sample produced by `chunker.py::fallback_split` includes chunks
beginning `eputation.` and `learning the format.`, one ending `seats f`,
and one consisting only of a sentence fragment. Four of five fail the
intact-boundary condition.

**Did it help?** No. Compared with the paragraph-aware `TOP_K = 1` run,
the fixed-window strategy reduced answer success from 5/5 to 4/5 on every
run and reduced the variant-specific chunk-quality sample from 5/5 to
1/5. The 0.62 gate still passed the shuttle question because its nearest
chunk had distance 0.4537; the gate checks similarity, not whether the
chunk contains the entire answer. The paragraph-aware index remains the
better choice for these documents and this test set.

---

# Unit 9 — Hybrid RAG Capstone

## What This Extends

This capstone extends **The Unofficial Guide**, the retrieval-augmented generation (RAG) system developed during Units 1 and 2 of CodePath AI201.

The original system retrieves information from the `campus_life` corpus using semantic search, checks relevance using a distance threshold, and generates answers grounded in retrieved documents.

Unit 9 extends that system with:

1. **BM25 keyword retrieval** to find documents using lexical relevance.
2. **Reciprocal Rank Fusion (RRF)** to combine keyword and semantic rankings.
3. **Hybrid retrieval** that uses both BM25 and ChromaDB semantic search.
4. **Structured instrumentation** to record request inputs, outputs, execution times, statuses, and errors.
5. **Comparative evaluation** to measure semantic and hybrid retrieval using the same questions.

The existing paragraph-aware chunking strategy, ChromaDB index, relevance threshold, and original acceptance criteria remain unchanged.

The objective is not to assume that hybrid retrieval is better, but to implement it, measure its behavior, and report the results.

## The Shape

### System Architecture

The application supports two retrieval modes: semantic and hybrid.

**Semantic retrieval pipeline**

```text
User Question
     |
     v
Semantic Search (ChromaDB)
     |
     v
Retrieved Document Chunks
     |
     v
Semantic Distance Relevance Gate
     |
     +---- Not Relevant ----> Refusal
     |
     v
Grounded Answer Generation
     |
     v
Answer with Source Documents
```

**Hybrid retrieval pipeline**

```text
                   User Question
                         |
              +----------+----------+
              |                     |
              v                     v
       BM25 Keyword Search   ChromaDB Semantic Search
              |                     |
              v                     v
       Keyword Candidates    Semantic Candidates
              |                     |
              +----------+----------+
                         |
                         v
              Reciprocal Rank Fusion
                         |
                         v
                Fused Document Chunks
                         |
                         v
             Semantic Distance Relevance Gate
                         |
              +----------+----------+
              |                     |
           Refuse                Accept
              |                     |
              v                     v
       Refusal Message     Grounded Generation
                                    |
                                    v
                         Answer with Sources
```

The relevance gate continues to use semantic distances. RRF scores are used to rank combined retrieval results, not to determine whether a question is within the corpus.

### Main Components

| File | Responsibility |
|---|---|
| `ingest.py` | Loads documents from the selected corpus |
| `chunker.py` | Divides documents into meaningful chunks |
| `store.py` | Performs ChromaDB semantic retrieval |
| `hybrid.py` | Implements BM25 and coordinates hybrid retrieval |
| `rrf.py` | Combines ranked results using Reciprocal Rank Fusion |
| `gate.py` | Determines whether retrieved semantic evidence is sufficiently relevant |
| `generate.py` | Produces grounded answers from retrieved context |
| `app.py` | Provides the command-line interface |
| `serve.py` | Exposes the RAG application through HTTP |
| `instrumentation.py` | Records structured execution events |
| `unit9_compare.py` | Evaluates semantic and hybrid retrieval |

### BM25 Keyword Retrieval

BM25 ranks documents according to the relevance of query terms within each document.

Unlike semantic retrieval, which compares vector representations, BM25 emphasizes lexical matches.

This can be useful for questions containing exact terminology, course names, building names, or other specific identifiers.

The implementation uses the existing corpus and chunking strategy to construct BM25 search candidates.

### Reciprocal Rank Fusion

Reciprocal Rank Fusion combines rankings from multiple retrieval methods.

The general formula is:

```text
RRF(d) = SUM [1 / (k + rank_i(d))]
```

Where:

- `d` represents a retrieved document chunk.
- `rank_i(d)` represents the chunk's position in retrieval list `i`.
- `k` is a rank-smoothing constant.
- The sum combines contributions from the retrieval lists containing that chunk.

RRF uses ranking positions rather than requiring BM25 relevance scores and semantic distances to have the same numerical scale.

The implementation also uses stable chunk identifiers to combine matching results without treating the same chunk as separate documents.

### Hybrid Retrieval

The hybrid retrieval process:

1. Receives the question.
2. Retrieves keyword candidates using BM25.
3. Retrieves semantic candidates from ChromaDB.
4. Combines both rankings using RRF.
5. Returns the highest-ranked fused chunks.
6. Retains semantic retrieval results for the relevance gate.

This preserves the original refusal behavior while allowing keyword and semantic retrieval to contribute to document ranking.

## Running It

The original project setup instructions remain available in `RUNNING.md`.

### Development Environment

The Unit 9 implementation was developed and tested using:

| Component | Configuration |
|---|---|
| Operating system | Windows |
| Python | 3.12.7 |
| Virtual environment | `.venv312` |
| Vector database | ChromaDB 0.6.3 |
| Embedding model | `all-MiniLM-L6-v2` |
| Corpus | `campus_life` |
| Corpus documents | 88 |
| Paragraph-aware chunks | 90 |
| Relevance threshold | 0.62 |
| Default top-k | 1 |

The existing ChromaDB index is reused. Rebuilding the index is unnecessary for the Unit 9 comparison.

### Run Semantic Retrieval

From the project root:

```powershell
.\.venv312\Scripts\python.exe app.py --corpus campus_life retrieve "How much do washing and drying each cost at Old Brewhouse?" --retrieval semantic
```

### Run Hybrid Retrieval

```powershell
.\.venv312\Scripts\python.exe app.py --corpus campus_life retrieve "How much do washing and drying each cost at Old Brewhouse?" --retrieval hybrid
```

These commands demonstrate retrieval without requiring a model-generated answer.

### Run Automated Tests

```powershell
.\.venv312\Scripts\python.exe -m unittest test_hybrid test_rrf test_hybrid_pipeline test_instrumentation test_unit9_compare test_instrumentation_output
```

The Milestone 7 validation completed successfully:

```text
Ran 39 tests in 0.263s

OK
```

The test suite covers BM25 retrieval, RRF behavior, hybrid integration, instrumentation, and evaluation functionality.

## Semantic vs. Hybrid Evaluation

### Evaluation Method

The comparison used the existing five in-scope questions and five out-of-scope questions from `questions.py`.

Each question was evaluated three times in each retrieval mode.

| Category | Semantic | Hybrid |
|---|---:|---:|
| In-scope questions | 5 | 5 |
| Out-of-scope questions | 5 | 5 |
| Trials per question | 3 | 3 |
| Total trials | 30 | 30 |

**Total evaluation records: 60.**

Both modes used the same corpus and existing semantic relevance threshold.

The evaluation measured retrieval behavior rather than newly generated Gemini answers.

### Evaluation Results

| Metric | Semantic | Hybrid |
|---|---:|---:|
| In-scope trials | 15 | 15 |
| Correct in-scope gate decisions | 15/15 | 15/15 |
| Top-1 expected-phrase matches | 15/15 | 15/15 |
| Top-k expected-phrase matches | 15/15 | 15/15 |
| Correct out-of-scope gate decisions | 15/15 | 15/15 |
| In-scope mean latency | 54.444 ms | 52.573 ms |
| In-scope median latency | 41.615 ms | 51.586 ms |
| Out-of-scope mean latency | 40.748 ms | 51.013 ms |
| Out-of-scope median latency | 40.899 ms | 50.629 ms |

### Analysis

Both retrieval methods successfully retrieved the expected answer phrase for all 15 in-scope trials.

Both methods also correctly classified all 15 out-of-scope trials.

Therefore, hybrid retrieval did not demonstrate an improvement in expected-phrase retrieval accuracy on this evaluation set.

Latency results were mixed.

For in-scope questions, hybrid retrieval had a slightly lower mean latency but a higher median latency.

For out-of-scope questions, hybrid retrieval had both higher mean and median latency.

These measurements show that adding BM25 and RRF introduces additional computational work, but the exact performance impact depends on the questions and execution conditions.

The benchmark does not establish whether hybrid retrieval improves generated-answer quality or source citation accuracy.

### Evaluation Evidence

The complete evaluation results are stored in:

- `results/unit9_compare_20261114-181537-592760.json`
- `results/unit9_compare_20261114-181537-592760.csv`
- `results/unit9_compare_20261114-181537-592760.md`

The JSON file contains structured evaluation data, the CSV supports tabular analysis, and the Markdown file summarizes the results.

## Instrumentation

### Purpose

Instrumentation provides visibility into application execution.

Instead of only observing the final answer, the application records information about requests, outcomes, and execution time.

This helps with debugging, evaluation, performance analysis, and identifying unexpected failures.

### Recorded Information

Structured JSONL events include applicable fields such as:

| Field | Purpose |
|---|---|
| Timestamp | Identifies when the event occurred |
| Event kind | Identifies the operation being recorded |
| Input | Records the request or question |
| Output | Records the result or refusal |
| Duration | Measures execution time in milliseconds |
| Status | Distinguishes success, refusal, and error outcomes |
| Retrieval context | Identifies relevant retrieval settings |
| Error type | Identifies the exception category when an error occurs |

JSONL stores one JSON object per line, making logs easier to inspect and process programmatically.

### Milestone 7 Execution Evidence

The final instrumentation verification produced 22 records.

| Event category | Count |
|---|---:|
| Successful retrieval | 10 |
| Out-of-scope refusals | 10 |
| HTTP validation error | 1 |
| Python exception | 1 |
| **Total** | **22** |

The retrieval and relevance-gate operations used the existing local corpus and ChromaDB index.

Generation was deliberately mocked during this evidence run to avoid unnecessary Gemini API calls.

This means the records validate retrieval, gate decisions, request logging, and error instrumentation, but they should not be interpreted as 22 independently generated Gemini answers.

### Instrumentation Evidence

- `results/milestone5_real_requests.jsonl`
- `results/milestone7_real_requests_20261114-182032.jsonl`

Automated instrumentation tests also verify the expected structure and behavior of recorded events.

### Production Considerations

Request logs can contain user questions, answers, document references, and other application information.

Before deploying this instrumentation in a corporate environment, I would add:

- Sensitive-data redaction.
- Appropriate access controls.
- Log rotation and retention policies.
- Centralized log collection.
- Monitoring and alerting.
- Protection against recording API keys or other credentials.

## What It Costs

### Computational Cost

Semantic retrieval searches the existing vector index.

Hybrid retrieval performs additional operations:

1. Load and chunk the corpus for keyword retrieval.
2. Prepare BM25 search data.
3. Rank keyword candidates.
4. Retrieve semantic candidates.
5. Fuse both result lists using RRF.

In the current implementation, BM25 preparation occurs during hybrid search rather than through a persistent keyword index.

This can increase the work performed per request.

### Measured Latency

For in-scope questions:

| Metric | Semantic | Hybrid |
|---|---:|---:|
| Mean | 54.444 ms | 52.573 ms |
| Median | 41.615 ms | 51.586 ms |

The hybrid median was approximately 24% higher than the semantic median.

For out-of-scope questions:

| Metric | Semantic | Hybrid |
|---|---:|---:|
| Mean | 40.748 ms | 51.013 ms |
| Median | 40.899 ms | 50.629 ms |

These measurements describe local retrieval execution, not full HTTP request latency or hosted service performance.

### Model API Cost

The Unit 9 comparison did not require Gemini-generated answers.

Consequently, the comparison itself did not incur Gemini generation calls.

Normal grounded-answer generation can consume model API requests and tokens depending on the configured provider, model, and account.

### Possible Optimizations

A future implementation could:

- Cache or persist the BM25 index.
- Avoid repeatedly loading and chunking the same corpus.
- Benchmark larger document collections.
- Measure end-to-end latency separately from retrieval latency.
- Track model token usage and actual API costs.

## Limitations and Next Steps

### Current Limitations

**1. Small evaluation dataset**

The comparison uses five in-scope and five out-of-scope questions. This is useful for a controlled course experiment but insufficient for broad performance claims.

**2. No demonstrated retrieval-accuracy improvement**

Both modes achieved the same expected-phrase results.

Hybrid retrieval therefore did not demonstrate better accuracy on this test set.

**3. No new generated-answer evaluation**

The Unit 9 comparison measures retrieval and relevance-gate behavior.

It does not independently establish that hybrid-generated answers satisfy the original source-naming and source-support criteria.

**4. BM25 initialization overhead**

The current implementation prepares keyword retrieval data during hybrid searches.

This could become inefficient for larger corpora or higher request volumes.

**5. Limited production observability**

The instrumentation captures structured events, but a production deployment would require additional monitoring, security, and log-management controls.

### Future Improvements

I would extend the system by:

1. Evaluating more diverse questions and document types.
2. Testing questions requiring information from multiple documents.
3. Comparing generated answers and source citations across retrieval modes.
4. Persisting or caching the BM25 keyword index.
5. Measuring latency under concurrent HTTP requests.
6. Adding production-grade log redaction, retention, and monitoring.

## How I Used AI — Unit 9

I used AI assistance throughout the Unit 9 capstone to support planning, implementation, testing, and documentation.

**Architecture and design:** AI helped me reason about the differences between BM25 keyword search, semantic retrieval, and Reciprocal Rank Fusion. I used those explanations to plan the hybrid retrieval architecture while preserving the existing relevance gate.

**Implementation support:** AI assisted with reviewing code structure, identifying relevant integration points, and preparing PowerShell scripts for controlled inspections and changes.

**Testing and debugging:** AI helped organize test cases, interpret test results, and investigate implementation problems. I verified proposed changes through local execution rather than accepting generated suggestions without testing.

**Evaluation:** AI helped structure the semantic-versus-hybrid comparison and interpret the results. I checked the reported measurements against saved evaluation evidence and avoided claiming improvements that the results did not demonstrate.

**Version control and documentation:** AI assisted with preparing documentation and Git workflows. I used separate commits for implementation milestones and verified changes before pushing them.

My development process prioritized:

- Read-only inspection before modifying existing files.
- Backups before potentially destructive changes.
- Preserving the existing corpus and ChromaDB index.
- Automated testing after implementation changes.
- Reviewing Git changes before committing.
- Separating observed results from assumptions.

AI assistance supported the development process, but the saved code, tests, execution logs, and evaluation results provide the evidence for the conclusions reported here.

## Final Reflection

This capstone demonstrated that combining retrieval methods is technically straightforward compared with proving that the combination improves the application.

BM25 and semantic retrieval use different approaches to finding relevant information. Reciprocal Rank Fusion provides a practical way to combine their rankings without directly comparing incompatible relevance scores.

However, my evaluation showed that hybrid retrieval did not outperform semantic retrieval on the selected questions.

Both modes achieved the same expected-phrase and relevance-gate results, while hybrid retrieval generally had higher median latency.

The instrumentation work was also valuable because it made request behavior measurable and easier to investigate.

The main lesson I learned is that adding complexity to a RAG system should be justified by measurable improvements, not simply by the availability of another retrieval technique.

For this dataset, the existing semantic approach remains a strong baseline. Hybrid retrieval is implemented and available for further evaluation, but broader testing is needed before selecting it as the preferred production retrieval method.
