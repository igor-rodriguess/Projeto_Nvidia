from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.persistence.persistence_service import PersistenceError
from app.routes.dependencies import get_batch_service
from app.routes.auth import require_api_key
from app.services.batch_processing_service import BatchExecutionOptions, BatchProcessingService


router = APIRouter(
    prefix="/api/v1/batches",
    tags=["batches"],
    dependencies=[Depends(require_api_key)],
)


class BatchCreateRequest(BaseModel):
    source_file: str | None = None
    limit: int | None = Field(default=None, ge=1, le=50)
    startup_ids: list[str] = Field(default_factory=list, max_length=50)
    include_ineligible: bool = True
    max_attempts: int = Field(default=2, ge=1, le=3)
    stop_on_error: bool = False


@router.post("", status_code=status.HTTP_202_ACCEPTED)
def create_batch(
    request: BatchCreateRequest,
    service: BatchProcessingService = Depends(get_batch_service),
) -> dict[str, Any]:
    try:
        options = BatchExecutionOptions.model_validate(
            request.model_dump(exclude={"source_file"})
        )
        batch_id = service.create_batch(request.source_file, options)
        return _batch_response(service, batch_id)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except PersistenceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("")
def list_batches(
    limit: int = Query(default=20, ge=1, le=100),
    service: BatchProcessingService = Depends(get_batch_service),
) -> list[dict[str, Any]]:
    return service.repository.list_batches(limit=limit)


@router.get("/{batch_id}")
def get_batch(
    batch_id: UUID,
    service: BatchProcessingService = Depends(get_batch_service),
) -> dict[str, Any]:
    return _batch_response(service, batch_id)


@router.get("/{batch_id}/items")
def get_batch_items(
    batch_id: UUID,
    item_status: str | None = Query(default=None, alias="status"),
    service: BatchProcessingService = Depends(get_batch_service),
) -> list[dict[str, Any]]:
    statuses = {item_status} if item_status else None
    return service.repository.list_items(batch_id, statuses=statuses)


@router.post("/{batch_id}/run", status_code=status.HTTP_202_ACCEPTED)
def run_batch(
    batch_id: UUID,
    service: BatchProcessingService = Depends(get_batch_service),
) -> dict[str, Any]:
    batch = service.repository.get_batch(batch_id)
    if batch["status"] == "running":
        raise HTTPException(status_code=409, detail="Lote ja esta em execucao")
    try:
        return service.queue_batch(batch_id, resume=False)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{batch_id}/resume", status_code=status.HTTP_202_ACCEPTED)
def resume_batch(
    batch_id: UUID,
    service: BatchProcessingService = Depends(get_batch_service),
) -> dict[str, Any]:
    try:
        return service.queue_batch(batch_id, resume=True)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{batch_id}/cancel")
def cancel_batch(
    batch_id: UUID,
    service: BatchProcessingService = Depends(get_batch_service),
) -> dict[str, Any]:
    service.repository.cancel_batch(batch_id)
    return service.repository.get_batch(batch_id)


@router.get("/{batch_id}/dead-letters")
def get_dead_letters(
    batch_id: UUID,
    service: BatchProcessingService = Depends(get_batch_service),
) -> list[dict[str, Any]]:
    return service.repository.list_dead_letters(batch_id)


@router.post("/dead-letters/{dead_letter_id}/replay", status_code=status.HTTP_202_ACCEPTED)
def replay_dead_letter(
    dead_letter_id: UUID,
    service: BatchProcessingService = Depends(get_batch_service),
) -> dict[str, str]:
    item_id = service.repository.replay_dead_letter(dead_letter_id)
    return {"status": "queued", "batch_item_id": str(item_id)}


def _batch_response(service: BatchProcessingService, batch_id: UUID) -> dict[str, Any]:
    try:
        batch = service.repository.get_batch(batch_id)
        batch["items"] = service.repository.list_items(batch_id)
        return batch
    except PersistenceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
