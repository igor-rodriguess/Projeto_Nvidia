from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.persistence.persistence_service import PipelinePersistence
from app.routes.dependencies import get_persistence
from app.routes.security import enforce_security


router = APIRouter(
    prefix="/api/v1",
    tags=["analyses"],
    dependencies=[Depends(enforce_security)],
)


@router.get("/startups")
def list_startups(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    persistence: PipelinePersistence = Depends(get_persistence),
) -> list[dict[str, Any]]:
    response = (
        persistence.db.table("startups")
        .select("id,external_id,nome,site_oficial,categoria,cidade,estado,pais,created_at")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return list(response.data or [])


@router.get("/startups/{startup_id}")
def get_startup(
    startup_id: UUID,
    persistence: PipelinePersistence = Depends(get_persistence),
) -> dict[str, Any]:
    startup = _one(
        persistence.db.table("startups").select("*").eq("id", str(startup_id)).limit(1).execute()
    )
    if not startup:
        raise HTTPException(status_code=404, detail="Startup nao encontrada")
    runs = (
        persistence.db.table("pipeline_runs")
        .select("id,status,current_stage,started_at,finished_at,duration_ms,created_at")
        .eq("startup_id", str(startup_id))
        .order("created_at", desc=True)
        .execute()
        .data
        or []
    )
    return {**startup, "pipeline_runs": runs}


@router.get("/runs/{run_id}")
def get_analysis(
    run_id: UUID,
    persistence: PipelinePersistence = Depends(get_persistence),
) -> dict[str, Any]:
    run = _one(
        persistence.db.table("pipeline_runs").select("*").eq("id", str(run_id)).limit(1).execute()
    )
    if not run:
        raise HTTPException(status_code=404, detail="Execucao nao encontrada")
    return {
        "run": run,
        "assessment": _artifact(persistence, "ai_assessments", run_id),
        "inception_fit": _artifact(persistence, "inception_fit_assessments", run_id),
        "recommendation": _artifact(persistence, "nvidia_recommendations", run_id),
        "refinement": _artifact(persistence, "recommendation_refinements", run_id),
        "impact": _artifact(persistence, "impact_estimates", run_id),
        "briefing": _artifact(persistence, "executive_briefings", run_id),
    }


@router.get("/runs/{run_id}/briefing", response_class=Response)
def get_briefing(
    run_id: UUID,
    persistence: PipelinePersistence = Depends(get_persistence),
) -> Response:
    briefing = _artifact(persistence, "executive_briefings", run_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing nao encontrado")
    return Response(content=briefing["markdown"], media_type="text/markdown; charset=utf-8")


def _artifact(
    persistence: PipelinePersistence,
    table: str,
    run_id: UUID,
) -> dict[str, Any] | None:
    return _one(
        persistence.db.table(table)
        .select("*")
        .eq("pipeline_run_id", str(run_id))
        .limit(1)
        .execute()
    )


def _one(response: Any) -> dict[str, Any] | None:
    data = getattr(response, "data", None)
    return data[0] if isinstance(data, list) and data else None
