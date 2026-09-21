# Milestone 1 Notes

## Selected Corpus

`campus_life`

# We will read these four documents covering different types of information:

1.  admin_housing_lottery.txt — administrative procedure
2.  dining_kestrel_commons.txt — dining review
3.  course_cs_210.txt — course information
4.  housing_old_brewhouse.txt — housing review and one of the longer files

## Comand and results

1.  Get-Content -Raw .\corpora\campus_life\documents\admin_housing_lottery.txt
    - The housing lottery is not random in the way most people assume. Rising sophomores get a number drawn at random, but juniors and seniors are ordered by accumulated credit hours first, and only tie-break randomly. That means a senior who took summer courses reliably beats a senior who didn't. Numbers come out the second week of March and selection runs over four evenings.

2.  Get-Content -Raw .\corpora\campus_life\documents\dining_kestrel_commons.txt
    - Kestrel Commons

    I'm a junior and I've done this twice now. Wait times: 20 to 25 minutes between 12:15 and 1:00, under 5 minutes before 11:45. The thing worth going for is the stir-fry station, made to order. The thing to know is that the salad bar wilts after 1:30.

    Hours are 7:00am to 9:00pm weekdays, 9:00am to 8:00pm weekends. Costs one meal swipe, or $12.50 cash.

3.  Get-Content -Raw .\corpora\campus_life\documents\course_cs_210.txt
    - CS 210 Data Structures

    I'm a junior and I've done this twice now. Format is lecture with weekly labs; slides go up after class, not before. Assessment: two midterms and a final, all drawn from lecture material rather than the textbook. Midterms are curved, the final is not.

    Expect 8 to 10 hours a week outside class.

    The one piece of advice: do the labs even though they're only 10% — the exams reuse the lab problems.

4.  Get-Content -Raw .\corpora\campus_life\documents\housing_old_brewhouse.txt - Old Brewhouse — what it's actually like

        Took this last spring. Built 1902 as a brewery, converted to housing in 1998. Rooms are doubles and triples with unusual floor plans, no two alike.

        The good: the most characterful building on campus and people get attached to it.

        The bad: the heating is uneven — some rooms run hot all winter and can't be adjusted.

        Laundry costs $1.50 wash, $1.50 dry, coin only, and the machines are old. On noise: sound carries strangely because of the original brick; a room two floors up can be louder than next door.

## Corpus Observations

### 1. `admin_housing_lottery.txt`

- **Topic:** How the housing lottery works.
- **Approximate file size:** 401 bytes.
- **Structure:** One paragraph containing four sentences.
- **Useful information:** The lottery is not completely random. Rising sophomores receive random numbers, while juniors and seniors are ranked by accumulated credit hours before random tie-breaking.
- **Chunking observation:** The first sentence gives a short answer, but the following sentences provide necessary context. Keeping the complete short document together may preserve that explanation.
- **Source information:** The filename clearly identifies the administrative topic.
- **Cleaning needed:** No navigation, advertisements, or unrelated content were visible.

### 2. `dining_kestrel_commons.txt`

- **Topic:** Practical information about Kestrel Commons.
- **Approximate file size:** 375 bytes.
- **Structure:** A title followed by two content paragraphs.
- **Useful information:** Wait times, food recommendations, opening hours, and cost.
- **Chunking observation:** Individual sentences answer specific questions, but the complete document provides a short overview of the same dining location.
- **Source information:** The filename identifies both the dining category and the location.
- **Cleaning needed:** No navigation, advertisements, or unrelated content were visible.

### 3. `course_cs_210.txt`

- **Topic:** The format, assessments, workload, and study advice for CS 210.
- **Approximate file size:** 432 bytes.
- **Structure:** A title followed by three content paragraphs.
- **Useful information:** Lecture and lab format, examination structure, expected weekly workload, and advice about completing the labs.
- **Chunking observation:** Different sentences answer different course questions, but all the information concerns the same course. Keeping the short document together may preserve useful context.
- **Source information:** The filename identifies the exact course.
- **Cleaning needed:** No navigation, advertisements, or unrelated content were visible.

### 4. `housing_old_brewhouse.txt`

- **Topic:** What it is like to live in Old Brewhouse.
- **Approximate file size:** 563 bytes.
- **Structure:** A title followed by four content paragraphs.
- **Useful information:** Building history, room layouts, advantages, heating problems, laundry costs, and noise.
- **Chunking observation:** This document contains several subtopics that could potentially be separated. However, it remains short and focused on one residence, so keeping it together may provide useful context.
- **Source information:** The filename identifies the housing category and the specific residence.
- **Cleaning needed:** No navigation, advertisements, or unrelated content were visible.

## Preliminary Corpus Finding

The four documents are short and focused. Each discusses one main subject, and each filename provides useful source information. Useful facts often appear in individual sentences, while surrounding sentences provide supporting context.

Based on these examples, one complete document may already be a reasonable chunk. This is only a preliminary observation. I will inspect the starter chunking results before selecting my final chunk size and overlap.

## Starter Index Results

- **Documents loaded:** 88
- **Total document characters:** 27,908
- **Average document length:** Approximately 317 characters
- **Chunks created:** 88
- **Average chunk length:** 317 characters
- **Shortest chunk:** 178 characters
- **Longest chunk:** 549 characters
- **Chunking function:** `chunker.py::fallback_split`
- **Indexing time:** 18.6 seconds

### Initial Index Observation

The starter created 88 chunks from 88 documents, so each document
produced one chunk. The starter uses an 800-character limit, but the
longest cleaned document contained only 549 characters. Therefore, none
of the `campus_life` documents needed to be divided by the starter
chunker.

This result establishes the baseline. It does not yet prove that keeping
every document as one chunk is the best final strategy. I will evaluate
that decision during Milestone 3.

## Baseline Question

- **Question:** Is the housing lottery random?
- **Best distance:** 0.254
- **Current cutoff:** 0.6
- **Gate result:** Passed because 0.254 is below the 0.6 cutoff.
- **Model calls:** 1
- **Token usage:** 677 total tokens — 617 input and 60 output

### Answer

> The housing lottery is not entirely random in the way most people
> assume. While rising sophomores get a number drawn at random, juniors
> andseniors are ordered by accumulated credit hours first, with random
> tie-breaks used only after that.
>
> Source: `admin_housing_lottery.txt`

### Sources Retrieved

1. `admin_housing_lottery.txt`
2. `admin_parking_permits.txt`
3. `advising_registration.txt`
4. `housing_morrow_house.txt`
5. `housing_tamsin_court.txt`

### Baseline Result

The retrieval system returned a relevant answer and named
`admin_housing_lottery.txt` as its source. The answer is supported by
the retrieved document. It contains a minor spacing error in “andseniors,”
but that does not change the meaning of the answer.

## Required Advice Threads Count

Command used:

```powershell

- **Command:** `python app.py --corpus advice_threads chunks -n 1`
- **Number immediately before “chunks total”:** 26
- **Function shown:** `chunker.py::fallback_split`
- **Displayed sample source:** `thread_bike_commute.txt#0`
- **Note:** My selected project corpus remains `campus_life`.

### Preliminary corpus finding

The four documents are short and focused. Each one discusses one main
subject, and the filenames provide useful source information. Useful
facts often appear in individual sentences, while nearby sentences
provide supporting context. Based on these four examples, one complete
document may already be a reasonable chunk, but I will inspect the
starter chunking results before choosing my final strategy.

This file is your working notebook; these observations do not belong in the Sample Chunks section of README.md yet.

## Milestone 1 Completion Checklist

- [x] `python test.py` passes.
- [x] Selected `campus_life`.
- [x] Recorded my name and corpus in `README.md`.
- [x] Read at least four `campus_life` documents.
- [x] Ran `python app.py --corpus campus_life index`.
- [x] Recorded the document and chunk statistics.
- [x] Asked, “Is the housing lottery random?”
- [x] Confirmed that the response names a source document.
- [x] Recorded the required `advice_threads` chunk count: 26.
- [x] Committed and pushed the completed Milestone 1 work.
```
