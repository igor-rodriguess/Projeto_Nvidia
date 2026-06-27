from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.persistence.persistence_service import PipelinePersistence
from app.routes.auth import require_api_key
from app.routes.dependencies import get_persistence


router = APIRouter(tags=["metrics"], dependencies=[Depends(require_api_key)])


@router.get("/api/v1/metrics")
def metrics_json(
    persistence: PipelinePersistence = Depends(get_persistence),
) -> dict[str, object]:
    return _collect_metrics(persistence)


@router.get("/metrics", response_class=PlainTextResponse, include_in_schema=False)
def metrics_prometheus(
    persistence: PipelinePersistence = Depends(get_persistence),
) -> PlainTextResponse:
    metrics = _collect_metrics(persistence)
    lines = []
    for group, values in metrics.items():
        for label, count in values.items():
            metric = f"nvidia_radar_{group}_total"
            lines.append(f'{metric}{{status="{label}"}} {count}')
    return PlainTextResponse("\n".join(lines) + "\n")


def _collect_metrics(persistence: PipelinePersistence) -> dict[str, dict[str, int]]:
    return {
        "pipeline_runs": _status_counts(persistence, "pipeline_runs"),
        "batch_runs": _status_counts(persistence, "batch_runs"),
        "batch_items": _status_counts(persistence, "batch_items"),
    }


def _status_counts(persistence: PipelinePersistence, table: str) -> dict[str, int]:
    response = persistence.db.table(table).select("status").execute()
    return dict(Counter(row["status"] for row in (response.data or [])))
