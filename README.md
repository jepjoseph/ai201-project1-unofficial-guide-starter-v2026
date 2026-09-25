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

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion                                               | Original target | Run 1 | Run 2 | Run 3 | Before verdict |
| ------------------------------------------------------- | --------------- | ----- | ----- | ----- | -------------- |
| 1. Retrieved chunks contain the answer                  | 4 of 5          | 5/5   | 5/5   | 5/5   | **MET**        |
| 2. Every answer names a source                          | 5 of 5          | 5/5   | 5/5   | 5/5   | **MET**        |
| 3. Gate refuses out-of-corpus questions                 | 4 of 5          | 5/5   | 5/5   | 5/5   | **MET**        |
| 4. Sampled chunks stand alone and have intact sentences | 4 of 5          | 5/5   | 5/5   | 5/5   | **MET**        |
| 5. Named documents support the answers                  | 4 of 5          | 5/5   | 5/5   | 5/5   | **MET**        |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

Produced by: run_eval.py::main
Retrieval: store.py::search
Chunks produced by: chunker.py::split_documents

Criterion 1 — retrieved chunk for the shuttle question:
RETRIEVED: transit_shuttle.txt#0
DISTANCE: 0.3853
It's free with a student ID. The stop outside Fenwick Court is the one that
gets skipped when the driver is behind, which is worth knowing if you live there.

Criterion 2 — generated answer, shuttle question, run 1:
The stop outside Fenwick Court may be skipped when the driver is behind
schedule (from transit_shuttle.txt).

Criterion 3 — run_eval.py::check_out_of_scope:
What is the capital of Mongolia? | 0.825 | refused

Criterion 4 — sampled chunk:
Chunk 2 | source: course_biol_160_exams.txt#0
Four unit tests and a cumulative final. Not curved.
The unit tests come fast, roughly every three weeks; falling behind once
is very hard to recover from.

Criterion 5 — named supporting document:
SOURCE DOCUMENT: transit_shuttle.txt
It's free with a student ID. The stop outside Fenwick Court is the one that
gets skipped when the driver is behind, which is worth knowing if you live there.

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| #   | Criterion | Verdict | How I decided |
| --- | --------- | ------- | ------------- |
| 1   |           |         |               |
| 2   |           |         |               |
| 3   |           |         |               |
| 4   |           |         |               |
| 5   |           |         |               |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 |       |       |       |         |
| 2. Every answer names a source         | 5 of 5 |       |       |       |         |
| 3. Gate stops out-of-corpus questions  | 4 of 5 |       |       |       |         |
| 4.                                     |        |       |       |       |         |
| 5.                                     |        |       |       |       |         |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
