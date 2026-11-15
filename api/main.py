import config

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.evaluation_reports import get_report, list_reports
from api.schemas import CompareRequest, RetrievalRequest
from api.retrieval_service import (
    available_indexes,
    compare_retrievals,
    run_retrieval,
)

app = FastAPI(
    title="RAG Evaluation Studio API",
    version="0.1.0",
    description="Semantic and Hybrid RAG evaluation interface",
)

# Local React development server only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/rag/health")
def health():
    indexes = available_indexes()
    return {
        "status": "ok",
        "index_ready": bool(indexes),
        "indexed_collections": len(indexes),
    }


@app.get("/api/rag/config")
def configuration():
    return {
        "retrieval_modes": ["semantic", "hybrid"],
        "comparison_available": True,
        "indexes": available_indexes(),
        "defaults": {
            "corpus": config.CORPUS,
            "variant": "default",
            "top_k": config.TOP_K,
            "threshold": config.THRESHOLD,
            "embedding_model": config.EMBEDDING_MODEL,
            "chunk_size": config.CHUNK_SIZE,
            "chunk_overlap": config.CHUNK_OVERLAP,
        },
    }


@app.post("/api/rag/retrieve")
def retrieve(payload: RetrievalRequest):
    try:
        return run_retrieval(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/rag/compare")
def compare(payload: CompareRequest):
    try:
        return compare_retrievals(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/rag/evaluations")
def evaluation_reports():
    return {"reports": list_reports()}


@app.get("/api/rag/evaluations/{report_id}")
def evaluation_report(report_id: str):
    try:
        return get_report(report_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except (ValueError, OSError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc