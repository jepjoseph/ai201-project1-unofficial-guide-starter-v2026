from typing import Literal

from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    corpus: str = "campus_life"
    variant: str = "default"
    retrieval: Literal["semantic", "hybrid"] = "semantic"
    top_k: int = Field(default=5, ge=1, le=20)
    threshold: float = Field(default=0.62, ge=0.0, le=2.0)


class CompareRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    corpus: str = "campus_life"
    variant: str = "default"
    top_k: int = Field(default=5, ge=1, le=20)
    threshold: float = Field(default=0.62, ge=0.0, le=2.0)
