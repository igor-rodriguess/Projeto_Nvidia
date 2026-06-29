from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.routes.dependencies import get_batch_service, get_persistence


AUTH = {"X-API-Key": "test-api-key"}


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


class RunDatabase:
    def __init__(self, run_id):
        self.run_id = str(run_id)

    def table(self, name):
        if name == "pipeline_runs":
            return FakeQuery([{"id": self.run_id, "status": "completed"}])
        if name == "inception_fit_assessments":
            return FakeQuery(
                [
                    {
                        "id": str(uuid4()),
                        "pipeline_run_id": self.run_id,
                        "eligibility_status": "unknown",
                        "startup_stage": "unknown",
                        "fit_json": {"open_questions": ["Confirmar elegibilidade."]},
                    }
                ]
            )
        return FakeQuery([])


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_cors_preflight_allows_local_frontend():
    with TestClient(app) as client:
        response = client.options(
            "/api/v1/startups",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_preflight_rejects_unknown_origin():
    with TestClient(app) as client:
        response = client.options(
            "/api/v1/startups",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_create_batch_queues_for_external_worker(monkeypatch):
    monkeypatch.setenv("BACKEND_API_KEY", "test-api-key")
    service = FakeBatchService()
    app.dependency_overrides[get_batch_service] = lambda: service
    app.dependency_overrides[get_persistence] = lambda: FakePersistence()
    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/batches", json={"limit": 2}, headers=AUTH)
        assert response.status_code == 202
        assert service.runs == []
    finally:
        app.dependency_overrides.clear()


def test_list_startups_uses_backend_persistence(monkeypatch):
    monkeypatch.setenv("BACKEND_API_KEY", "test-api-key")
    app.dependency_overrides[get_persistence] = lambda: FakePersistence()
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/startups", headers=AUTH)
        assert response.status_code == 200
        assert response.json()[0]["nome"] == "Alpha"
    finally:
        app.dependency_overrides.clear()


def test_protected_endpoint_rejects_missing_api_key(monkeypatch):
    monkeypatch.setenv("BACKEND_API_KEY", "test-api-key")
    app.dependency_overrides[get_persistence] = lambda: FakePersistence()
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/startups")
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_run_detail_exposes_inception_fit(monkeypatch):
    monkeypatch.setenv("BACKEND_API_KEY", "test-api-key")
    run_id = uuid4()
    persistence = type("Persistence", (), {"db": RunDatabase(run_id)})()
    app.dependency_overrides[get_persistence] = lambda: persistence
    try:
        with TestClient(app) as client:
            response = client.get(f"/api/v1/runs/{run_id}", headers=AUTH)
        assert response.status_code == 200
        assert response.json()["inception_fit"]["eligibility_status"] == "unknown"
    finally:
        app.dependency_overrides.clear()


def test_metrics_are_exposed_with_authentication(monkeypatch):
    monkeypatch.setenv("METRICS_BEARER_TOKEN", "test-metrics-token")
    app.dependency_overrides[get_persistence] = lambda: FakePersistence()
    try:
        with TestClient(app) as client:
            response = client.get(
                "/metrics", headers={"Authorization": "Bearer test-metrics-token"}
            )
        assert response.status_code == 200
        assert "nvidia_radar_pipeline_runs_total" not in response.text
    finally:
        app.dependency_overrides.clear()
