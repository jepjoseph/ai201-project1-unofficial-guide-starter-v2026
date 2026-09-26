# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. _"Retrieval works"_ is an opinion. _"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"_ is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; _"80% seemed reasonable"_ does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
My five questions cover five different areas of the `campus_life` corpus:
administrative procedures, dining, courses, housing, and transportation.
Because semantic retrieval may handle the wording of one topic less accurately
than the others, I allow one unsuccessful question while still requiring the
system to retrieve the answer for at least 80% of the test set.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
Every stored chunk retains its source filename, and the generation prompt
instructs the model to identify its source. My baseline housing-lottery answer
successfully named `admin_housing_lottery.txt`, so requiring a source for every
produced answer is achievable and necessary for verifying that answers come
from the `campus_life` documents.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
The relevance gate makes its decision by comparing the best semantic distance
with a cutoff. An unrelated question could still share words or concepts with
a campus document and accidentally receive a close distance, so I allow one
incorrect gate decision while requiring the gate to refuse at least 80% of the
five out-of-corpus questions.

---

## 4. Something about your chunks

For at least 4 of the 5 chunks printed by
`python app.py --corpus campus_life chunks -n 5`, a reader must be able to
write at least one question that the chunk can answer without reading a
neighboring chunk, and the chunk must not begin or end with a sentence cut in
half.

**Why this target:**
The `campus_life` documents are short and focused, with the starter producing
chunks between 178 and 549 characters. However, several documents contain
multiple related facts, so I want to verify that my chunking strategy preserves
enough context to answer a question independently. I allow one imperfect sample
because the documents vary in structure and paragraph count.

> **Revised in Unit 2 for index-variant comparisons:** For at least 4 of
> 5 chunks sampled at evenly spaced positions from the strategy used to
> build the evaluated index variant, a reader can write a question the
> chunk answers without a neighboring chunk, and the chunk does not begin
> or end with a sentence cut in half.
>
> **Why revised:** The original `app.py chunks -n 5` command always calls
> `chunker.py::split_documents`, even when the evaluation uses the
> `fixed300` index built with `chunker.py::fallback_split`. It therefore
> measures the paragraph-aware strategy instead of the strategy under
> test. The target remains 4 of 5; only the sample source changes to
> match the evaluated index.

---

## 5. Your choice

For at least 4 of my 5 test questions, the source document named in the
generated answer must contain the expected phrase recorded in `questions.py`
or an equivalent fact that directly supports the answer.

**Why this target:**

Naming a source is not sufficient if that source does not support the generated
answer. Each test question has an `expects` value chosen from its corresponding
`campus_life` document, so comparing the answer and named source with that value
provides a repeatable way to check source accuracy. I allow one failure because
the model may paraphrase a fact or cite a relevant document without reproducing
the expected phrase exactly.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
