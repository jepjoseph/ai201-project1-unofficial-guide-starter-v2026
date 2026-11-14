# Unit 9 Capstone — Hybrid RAG

## Project

Hybrid RAG: Improving Document Retrieval with Semantic Search and BM25.

## Existing System

The Unofficial Guide is a Python-based RAG application.

It currently provides:

- Document ingestion and paragraph-aware chunking.
- MiniLM embeddings and ChromaDB cosine similarity search.
- Configurable top-k retrieval.
- A cosine-distance relevance gate.
- Grounded answer generation using Gemini.
- Command-line and Flask HTTP interfaces.
- Previous evaluation evidence from Units 1 and 2.

Baseline Git commit:
74fc8a6f187d75e8e0d6a138bb872bb786f0d1bf

## Capstone Extension

Implement hybrid retrieval combining:

1. Existing ChromaDB semantic search.
2. New BM25 keyword search.
3. Reciprocal Rank Fusion for combining ranked results.

The original semantic retrieval mode will remain available.

The existing relevance gate must not be bypassed by BM25 results.

## In Scope

- BM25 indexing and retrieval over existing document chunks.
- Hybrid ranking with duplicate-result handling.
- Semantic and hybrid retrieval modes.
- Integration with the existing RAG pipeline.
- Structured request logging and latency measurements.
- Reproducible local startup.
- Controlled baseline-versus-hybrid comparison.
- Acceptance testing and one measured improvement.
- Cost estimation and documented limitations.

## Out of Scope

- A new frontend.
- Training or fine-tuning an AI model.
- Replacing Gemini.
- Replacing ChromaDB.
- Changing the embedding model.
- Rewriting the chunking strategy.
- Migrating the application to another database.

## Comparison Strategy

RAG v1:
Project01, branch main, baseline commit 74fc8a6.

RAG v2:
Project09, branch capstone/unit9-hybrid-rag.

Both systems will use the same document corpus and test questions.

Results will be measured rather than assumed.

## Implementation Safeguards

- Preserve the original Project01 working directory.
- Inspect existing files before modification.
- Back up files before editing.
- Make incremental changes and verify them.
- Preserve existing Unit 1 and Unit 2 evidence.
- Commit and push verified milestones.
- Define Unit 9 acceptance criteria before formal acceptance testing.

## Expected Deliverables

- Working hybrid retrieval capability.
- Reproducible local demonstration.
- Structured execution logs.
- Five measurable acceptance criteria written by the student.
- Three test runs per criterion.
- One diagnosed and measured improvement.
- Baseline-versus-hybrid comparison.
- Final Capstone README documentation.