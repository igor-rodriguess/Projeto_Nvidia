from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
import os
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.persistence.persistence_service import PipelinePersistence
from app.routes.auth import require_metrics_token
from app.routes.security import enforce_security
from app.routes.dependencies import get_persistence


router = APIRouter(tags=["metrics"])


@router.get("/api/v1/metrics", dependencies=[Depends(enforce_security)])
def metrics_json(
    persistence: PipelinePersistence = Depends(get_persistence),
) -> dict[str, object]:
    return _collect_metrics(persistence)


@router.get(
    "/metrics",
    response_class=PlainTextResponse,
    include_in_schema=False,
    dependencies=[Depends(require_metrics_token)],
)
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


def _collect_metrics(persistence: PipelinePersistence) -> dict[str, dict[str, int | float]]:
    metrics: dict[str, dict[str, int | float]] = {
        "pipeline_runs": _status_counts(persistence, "pipeline_runs"),
        "batch_runs": _status_counts(persistence, "batch_runs"),
        "batch_items": _status_counts(persistence, "batch_items"),
    }
    metrics.update(_worker_metrics(persistence))
    metrics.update(_external_api_metrics(persistence))
    metrics["alerts"] = _derive_alerts(metrics)
    return metrics


def _status_counts(persistence: PipelinePersistence, table: str) -> dict[str, int]:
    response = persistence.db.table(table).select("status").execute()
    return dict(Counter(row["status"] for row in (response.data or [])))


def _worker_metrics(persistence: PipelinePersistence) -> dict[str, dict[str, int]]:
    response = (
        persistence.db.table("batch_runs")
        .select("status,lease_expires_at")
        .eq("status", "running")
        .execute()
    )
    active = list(response.data or [])
    now = datetime.now(UTC)
    stale = sum(
        1
        for row in active
        if _parse_datetime(row.get("lease_expires_at")) is None
        or _parse_datetime(row.get("lease_expires_at")) <= now
    )
    return {"workers": {"active_leases": len(active), "stale_leases": stale}}


def _external_api_metrics(
    persistence: PipelinePersistence,
) -> dict[str, dict[str, int | float]]:
    rpc = getattr(persistence.db, "rpc", None)
    if not callable(rpc):
        return {}
    response = rpc("external_api_metrics", {}).execute()
    requests: dict[str, int | float] = {}
    cache_hits: dict[str, int | float] = {}
    failures: dict[str, int | float] = {}
    costs: dict[str, int | float] = {}
    for row in response.data or []:
        provider = str(row["provider"])
        requests[provider] = int(row.get("requests") or 0)
        cache_hits[provider] = int(row.get("cache_hits") or 0)
        failures[provider] = int(row.get("failures") or 0)
        costs[provider] = round(float(row.get("estimated_cost_usd") or 0), 6)
    return {
        "external_api_requests": requests,
        "external_api_cache_hits": cache_hits,
        "external_api_failures": failures,
        "external_api_estimated_cost_usd": costs,
    }


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _derive_alerts(
    metrics: dict[str, dict[str, int | float]],
) -> dict[str, int]:
    workers = metrics.get("workers", {})
    batch_items = metrics.get("batch_items", {})
    requests = metrics.get("external_api_requests", {})
    failures = metrics.get("external_api_failures", {})
    pending = int(batch_items.get("pending", 0))
    backlog_threshold = int(os.getenv("BACKLOG_ALERT_THRESHOLD", "20"))
    firecrawl_requests = int(requests.get("firecrawl", 0))
    firecrawl_failures = int(failures.get("firecrawl", 0))
    return {
        "worker_stale": int(workers.get("stale_leases", 0) > 0),
        "worker_missing_with_backlog": int(
            pending > 0 and workers.get("active_leases", 0) == 0
        ),
        "backlog_high": int(pending >= backlog_threshold),
        "firecrawl_failure_ratio_high": int(
            firecrawl_requests >= 5 and firecrawl_failures / firecrawl_requests >= 0.5
        ),
    }
