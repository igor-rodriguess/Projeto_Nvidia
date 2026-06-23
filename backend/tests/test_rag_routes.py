from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_rag_health_returns_curated_base_status():
    response = client.get("/rag/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["retrieval_mode"] in {"curated_local", "qdrant"}
    assert payload["technologies"] >= 15
    assert "qdrant" in payload
    assert payload["validation_errors"] == []


def test_rag_recommend_returns_cited_recommendations():
    response = client.post(
        "/rag/recommend",
        json={
            "name": "ModeloAI",
            "description": "Startup com LLM self-hosted, agentes e inferência em produção.",
            "sector": "tech",
            "possible_ai_signals": ["LLM", "modelo", "machine learning"],
            "ai_maturity": {"level": "advanced", "score": 7},
            "sources": [{"title": "Fonte", "url": "https://example.com"}],
        },
    )

    assert response.status_code == 200
    recommendations = response.json()["nvidia_recommendations"][0]["recommendations"]
    assert recommendations
    assert all(recommendation["sources"] for recommendation in recommendations)
