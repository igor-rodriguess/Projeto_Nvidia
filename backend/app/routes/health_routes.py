from __future__ import annotations

import requests
from fastapi import APIRouter, Depends

from app.persistence.persistence_service import PipelinePersistence
from app.rag.config import RAGConfig
from app.routes.dependencies import get_persistence


router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "nvidia-startup-ai-radar"}


@router.get("/ready")
def ready(
    persistence: PipelinePersistence = Depends(get_persistence),
) -> dict[str, object]:
    checks: dict[str, bool] = {"supabase": False, "qdrant": False}
    try:
        persistence.db.table("pipeline_runs").select("id").limit(1).execute()
        checks["supabase"] = True
    except Exception:
        pass
    try:
        checks["qdrant"] = requests.get(RAGConfig.from_env().qdrant_url, timeout=3).ok
    except requests.RequestException:
        pass
    return {"status": "ready" if all(checks.values()) else "degraded", "checks": checks}
