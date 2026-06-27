from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.routes.dependencies import get_batch_service, get_persistence


class FakeBatchRepository:
    def __init__(self):
        self.batch_id = uuid4()
        self.batch = {
            "id": str(self.batch_id),
            "status": "pending",
            "total_items": 2,
            "processed_items": 0,
        }
        self.items = [{"id": str(uuid4()), "startup_name": "Alpha", "status": "pending"}]

    def get_batch(self, batch_id):
        return dict(self.batch)

    def list_items(self, batch_id, statuses=None):
        return list(self.items)

    def list_batches(self, limit=20):
        return [dict(self.batch)]

    def cancel_batch(self, batch_id):
        self.batch["status"] = "cancelled"

    def fail_batch(self, batch_id, error):
        self.batch["status"] = "failed"


class FakeBatchService:
    def __init__(self):
        self.repository = FakeBatchRepository()
        self.runs = []

    def create_batch(self, source_file, options):
        return self.repository.batch_id

    def run_batch(self, batch_id, resume=False):
        self.runs.append((batch_id, resume))
        self.repository.batch["status"] = "completed"
        return self.repository.batch


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows

    def select(self, *args): return self
    def order(self, *args, **kwargs): return self
    def range(self, start, end): self.rows = self.rows[start:end + 1]; return self
    def eq(self, field, value): self.rows = [row for row in self.rows if str(row.get(field)) == str(value)]; return self
    def limit(self, value): self.rows = self.rows[:value]; return self
    def execute(self):
        class Response: pass
        response = Response()
        response.data = self.rows
        return response


class FakeDatabase:
    def table(self, name):
        if name == "startups":
            return FakeQuery([{"id": str(uuid4()), "nome": "Alpha"}])
        return FakeQuery([])


class FakePersistence:
    db = FakeDatabase()


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_batch_schedules_background_execution():
    service = FakeBatchService()
    app.dependency_overrides[get_batch_service] = lambda: service
    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/batches", json={"limit": 2, "auto_start": True})
        assert response.status_code == 202
        assert service.runs == [(service.repository.batch_id, False)]
    finally:
        app.dependency_overrides.clear()


def test_list_startups_uses_backend_persistence():
    app.dependency_overrides[get_persistence] = lambda: FakePersistence()
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/startups")
        assert response.status_code == 200
        assert response.json()[0]["nome"] == "Alpha"
    finally:
        app.dependency_overrides.clear()
