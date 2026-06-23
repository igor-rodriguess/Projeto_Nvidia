import os
from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agents.nvidia_rag_agent import nvidia_rag_agent
from app.rag.ingestion import load_nvidia_documents, split_documents
from app.rag.knowledge_base import (
    build_technology_documents,
    load_knowledge_base,
    validate_knowledge_base,
)
from app.rag.vector_store import DEFAULT_COLLECTION_NAME, get_qdrant_client


router = APIRouter(prefix="/rag", tags=["rag"])


class StartupRagRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    sector: str = Field(default="tech")
    possible_ai_signals: List[str] = Field(default_factory=list)
    ai_maturity: Dict[str, Any] = Field(default_factory=dict)
    sources: List[Dict[str, Any]] = Field(default_factory=list)


@router.get("/health")
def rag_health():
    knowledge_base = load_knowledge_base()
    documents = load_nvidia_documents()
    chunks = split_documents(documents)
    validation_errors = validate_knowledge_base()
    qdrant_status = _qdrant_status()

    return {
        "status": "ok" if not validation_errors else "invalid",
        "retrieval_mode": (
            "qdrant"
            if os.getenv("NVIDIA_RAG_USE_QDRANT", "false").lower() == "true"
            else "curated_local"
        ),
        "sources": len(knowledge_base["sources"]),
        "frameworks": len(knowledge_base["frameworks"]),
        "technologies": len(knowledge_base["technologies"]),
        "documents": len(build_technology_documents()),
        "chunks": len(chunks),
        "qdrant": qdrant_status,
        "validation_errors": validation_errors,
    }


@router.post("/recommend")
def recommend_nvidia_technologies(payload: StartupRagRequest):
    state = {
        "startups": [payload.model_dump()],
        "errors": [],
    }
    result = nvidia_rag_agent(state)
    return {
        "startup": payload.name,
        "nvidia_recommendations": result["nvidia_recommendations"],
        "errors": result.get("errors", []),
    }


def _qdrant_status() -> Dict[str, Any]:
    try:
        client = get_qdrant_client()
        info = client.get_collection(DEFAULT_COLLECTION_NAME)
        return {
            "available": True,
            "collection": DEFAULT_COLLECTION_NAME,
            "points_count": info.points_count,
            "status": str(info.status),
        }
    except Exception as exc:
        return {
            "available": False,
            "collection": DEFAULT_COLLECTION_NAME,
            "error": str(exc),
        }
