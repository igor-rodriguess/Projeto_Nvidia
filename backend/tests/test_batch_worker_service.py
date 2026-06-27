import json

from app.persistence.batch_repository import BatchRepository
from app.persistence.persistence_service import PipelinePersistence
from app.services.batch_processing_service import BatchProcessingService, CuratedStartupLoader
from app.services.batch_worker_service import BatchWorkerService
from tests.test_persistence_service import FakeSupabase


def test_worker_claims_and_completes_queued_batch(tmp_path):
    curated = tmp_path / "curated.json"
    curated.write_text(
        json.dumps(
            {
                "startups": [
                    {
                        "startup_id": "cubo_alpha",
                        "nome": "Alpha",
                        "site": "https://alpha.example",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    repository = BatchRepository(PipelinePersistence(client=FakeSupabase()))
    service = BatchProcessingService(
        repository,
        loader=CuratedStartupLoader(tmp_path),
        pipeline_runner=lambda payload: {"status": "completo", "errors": []},
    )
    batch_id = service.create_batch("curated.json")
    worker = BatchWorkerService(service, "worker-test")

    assert worker.run_once() is True
    assert repository.get_batch(batch_id)["status"] == "completed"
    assert worker.run_once() is False
