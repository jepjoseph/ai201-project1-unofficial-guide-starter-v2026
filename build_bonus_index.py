"""Build a separate fixed-window index for the Unit 2 bonus experiment."""

from chunker import describe, fallback_split
from ingest import load_documents
from store import build_index

CORPUS = "campus_life"
VARIANT = "fixed300"
WINDOW = 300
OVERLAP = 60

documents = load_documents(CORPUS)
chunks = fallback_split(documents, chunk_size=WINDOW, overlap=OVERLAP)

print(f"Strategy: {WINDOW}-character windows, {OVERLAP}-character overlap")
print(describe(chunks))
count = build_index(chunks, corpus=CORPUS, variant=VARIANT)
print(f"Stored {count} chunks in variant {VARIANT!r}")