from __future__ import annotations

from functools import lru_cache

from app.persistence.batch_repository import BatchRepository
from app.persistence.persistence_service import PipelinePersistence
from app.services.batch_processing_service import BatchProcessingService


@lru_cache(maxsize=1)
def get_persistence() -> PipelinePersistence:
    return PipelinePersistence.from_env()


@lru_cache(maxsize=1)
def get_batch_service() -> BatchProcessingService:
    persistence = get_persistence()
    return BatchProcessingService(BatchRepository(persistence))
