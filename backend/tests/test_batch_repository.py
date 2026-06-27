from uuid import UUID, uuid4

from app.persistence.batch_repository import BatchRepository
from app.persistence.persistence_service import PipelinePersistence
from tests.test_persistence_service import FakeSupabase


def _startup(index):
    return {
        "startup_id": f"cubo_startup_{index}",
        "nome": f"Startup {index}",
        "site": f"https://startup{index}.example",
    }


def test_batch_repository_tracks_progress_and_partial_result():
    client = FakeSupabase()
    repository = BatchRepository(PipelinePersistence(client=client))
    batch_id = repository.create_batch("data/curated/base.json", [_startup(1), _startup(2)])

    repository.start_batch(batch_id)
    items = repository.list_items(batch_id)
    repository.start_item(UUID(items[0]["id"]))
    repository.finish_item(
        UUID(items[0]["id"]),
        "completed",
        pipeline_run_id=uuid4(),
        result_summary={"classificacao": "AI-enabled"},
    )
    repository.start_item(UUID(items[1]["id"]))
    repository.finish_item(UUID(items[1]["id"]), "failed", error="Falha controlada")
    batch = repository.finalize_batch(batch_id)

    assert batch["status"] == "partial"
    assert batch["processed_items"] == 2
    assert batch["succeeded_items"] == 1
    assert batch["failed_items"] == 1


def test_batch_repository_recovers_interrupted_items():
    client = FakeSupabase()
    repository = BatchRepository(PipelinePersistence(client=client))
    batch_id = repository.create_batch("data/curated/base.json", [_startup(1)])
    item_id = UUID(repository.list_items(batch_id)[0]["id"])
    repository.start_item(item_id)

    recovered = repository.recover_interrupted_items(batch_id)
    item = repository.get_item(item_id)

    assert recovered == 1
    assert item["status"] == "pending"
    assert "interrompida" in item["last_error"]
