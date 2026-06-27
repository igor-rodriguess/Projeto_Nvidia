from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Iterable
from uuid import UUID

from app.persistence.models import BatchItem, BatchItemStatus, BatchRun, BatchStatus
from app.persistence.persistence_service import PersistenceError, PipelinePersistence


TERMINAL_ITEM_STATUSES = {"completed", "partial", "failed", "skipped"}


class BatchRepository:
    """Persist and recover durable batch execution state in Supabase."""

    def __init__(self, persistence: PipelinePersistence) -> None:
        self.persistence = persistence
        self.db = persistence.db

    @classmethod
    def from_env(cls) -> "BatchRepository":
        return cls(PipelinePersistence.from_env())

    def create_batch(
        self,
        source_path: str,
        startups: list[dict[str, Any]],
        options: dict[str, Any] | None = None,
    ) -> UUID:
        if not startups:
            raise ValueError("O lote deve conter pelo menos uma startup")
        run = BatchRun(
            source_path=source_path,
            total_items=len(startups),
            options=options or {},
        )
        try:
            response = self.db.table("batch_runs").insert(
                run.model_dump(
                    mode="json",
                    exclude={"id", "created_at", "updated_at"},
                    exclude_none=True,
                )
            ).execute()
            batch_id = UUID(_first_required(response, "batch_runs.insert")["id"])
            items = [
                BatchItem(
                    batch_run_id=batch_id,
                    startup_external_id=str(startup["startup_id"]),
                    startup_name=str(startup["nome"]),
                    startup_payload=startup,
                ).model_dump(
                    mode="json",
                    exclude={"id", "created_at", "updated_at"},
                    exclude_none=True,
                )
                for startup in startups
            ]
            self.db.table("batch_items").insert(items).execute()
            return batch_id
        except Exception as exc:
            raise PersistenceError(f"create_batch: {exc}") from exc

    def get_batch(self, batch_id: UUID) -> dict[str, Any]:
        response = (
            self.db.table("batch_runs")
            .select("*")
            .eq("id", str(batch_id))
            .limit(1)
            .execute()
        )
        return _first_required(response, f"Lote nao encontrado: {batch_id}")

    def list_items(
        self,
        batch_id: UUID,
        statuses: Iterable[BatchItemStatus | str] | None = None,
    ) -> list[dict[str, Any]]:
        response = (
            self.db.table("batch_items")
            .select("*")
            .eq("batch_run_id", str(batch_id))
            .execute()
        )
        rows = list(getattr(response, "data", None) or [])
        allowed = set(statuses or [])
        if allowed:
            rows = [row for row in rows if row.get("status") in allowed]
        return sorted(rows, key=lambda row: (row.get("created_at") or "", row["startup_name"]))

    def start_batch(self, batch_id: UUID) -> None:
        current = self.get_batch(batch_id)
        if current["status"] == "cancelled":
            raise ValueError("Lote cancelado nao pode ser iniciado")
        updates: dict[str, Any] = {"status": "running", "finished_at": None}
        if not current.get("started_at"):
            updates["started_at"] = datetime.now(UTC).isoformat()
        self._update_batch(batch_id, updates)

    def recover_interrupted_items(self, batch_id: UUID) -> int:
        running = self.list_items(batch_id, statuses={"running"})
        for item in running:
            self._update_item(
                UUID(item["id"]),
                {
                    "status": "pending",
                    "last_error": "Execucao anterior interrompida; item devolvido para a fila.",
                    "started_at": None,
                },
            )
        return len(running)

    def requeue_retryable_items(self, batch_id: UUID, max_attempts: int) -> int:
        failed = self.list_items(batch_id, statuses={"failed"})
        retryable = [item for item in failed if int(item.get("attempt_count") or 0) < max_attempts]
        for item in retryable:
            self._update_item(
                UUID(item["id"]),
                {"status": "pending", "finished_at": None},
            )
        return len(retryable)

    def start_item(self, item_id: UUID) -> None:
        item = self.get_item(item_id)
        self._update_item(
            item_id,
            {
                "status": "running",
                "attempt_count": int(item.get("attempt_count") or 0) + 1,
                "last_error": None,
                "started_at": datetime.now(UTC).isoformat(),
                "finished_at": None,
            },
        )

    def finish_item(
        self,
        item_id: UUID,
        status: BatchItemStatus,
        pipeline_run_id: UUID | None = None,
        result_summary: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        if status not in TERMINAL_ITEM_STATUSES:
            raise ValueError(f"Status final de item invalido: {status}")
        self._update_item(
            item_id,
            {
                "status": status,
                "pipeline_run_id": str(pipeline_run_id) if pipeline_run_id else None,
                "result_summary": result_summary or {},
                "last_error": error,
                "finished_at": datetime.now(UTC).isoformat(),
            },
        )

    def get_item(self, item_id: UUID) -> dict[str, Any]:
        response = (
            self.db.table("batch_items")
            .select("*")
            .eq("id", str(item_id))
            .limit(1)
            .execute()
        )
        return _first_required(response, f"Item de lote nao encontrado: {item_id}")

    def finalize_batch(self, batch_id: UUID) -> dict[str, Any]:
        items = self.list_items(batch_id)
        counts = {status: 0 for status in TERMINAL_ITEM_STATUSES}
        for item in items:
            if item["status"] in counts:
                counts[item["status"]] += 1
        processed = sum(counts.values())
        total = len(items)
        if processed < total:
            status: BatchStatus = "running"
            finished_at = None
        elif counts["failed"] == total:
            status = "failed"
            finished_at = datetime.now(UTC).isoformat()
        elif counts["failed"] or counts["partial"]:
            status = "partial"
            finished_at = datetime.now(UTC).isoformat()
        else:
            status = "completed"
            finished_at = datetime.now(UTC).isoformat()
        self._update_batch(
            batch_id,
            {
                "status": status,
                "processed_items": processed,
                "succeeded_items": counts["completed"],
                "partial_items": counts["partial"],
                "failed_items": counts["failed"],
                "finished_at": finished_at,
            },
        )
        return self.get_batch(batch_id)

    def cancel_batch(self, batch_id: UUID) -> None:
        self._update_batch(
            batch_id,
            {"status": "cancelled", "finished_at": datetime.now(UTC).isoformat()},
        )

    def fail_batch(self, batch_id: UUID, error: str) -> None:
        current = self.get_batch(batch_id)
        errors = list(current.get("errors") or [])
        errors.append(error[:2000])
        self._update_batch(
            batch_id,
            {
                "status": "failed",
                "errors": errors,
                "finished_at": datetime.now(UTC).isoformat(),
            },
        )

    def is_cancelled(self, batch_id: UUID) -> bool:
        return self.get_batch(batch_id)["status"] == "cancelled"

    def list_batches(self, limit: int = 20) -> list[dict[str, Any]]:
        response = (
            self.db.table("batch_runs")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return list(getattr(response, "data", None) or [])

    def _update_batch(self, batch_id: UUID, values: dict[str, Any]) -> None:
        self.db.table("batch_runs").update(values).eq("id", str(batch_id)).execute()

    def _update_item(self, item_id: UUID, values: dict[str, Any]) -> None:
        self.db.table("batch_items").update(values).eq("id", str(item_id)).execute()


def _first_required(response: Any, operation: str) -> dict[str, Any]:
    data = getattr(response, "data", None)
    row = data[0] if isinstance(data, list) and data else data
    if not isinstance(row, dict):
        raise PersistenceError(operation)
    return row
