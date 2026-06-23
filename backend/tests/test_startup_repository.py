from app.db.startup_repository import persist_startup_discovery_result


class FakeSupabaseClient:
    def __init__(self):
        self.calls = []
        self.counter = 0

    def _next_id(self, table):
        self.counter += 1
        return f"{table}-{self.counter}"

    def insert(self, table, payload):
        self.calls.append(("insert", table, payload))
        return {"id": self._next_id(table), **payload}

    def bulk_insert(self, table, payload):
        self.calls.append(("bulk_insert", table, payload))
        return [
            {"id": self._next_id(table), **item}
            for item in payload
        ]

    def upsert(self, table, payload, on_conflict):
        self.calls.append(("upsert", table, payload, on_conflict))
        return {"id": self._next_id(table), **payload}


def _sample_pipeline_result():
    return {
        "query": "healthtech IA Brasil",
        "search_terms": ["healthtech IA Brasil", "healthtech IA Brasil startup Brasil"],
        "sources": [
            {
                "title": "DiagIA - healthtech",
                "url": "https://example.com/diagia",
                "snippet": "Startup usa IA em diagnóstico.",
                "source_type": "public_search",
                "collected_at": "2026-06-23T00:00:00+00:00",
            }
        ],
        "startups": [
            {
                "name": "DiagIA",
                "description": "Startup usa IA em diagnóstico.",
                "sector": "healthtech",
                "possible_ai_signals": ["IA"],
                "sources": [
                    {
                        "title": "DiagIA - healthtech",
                        "url": "https://example.com/diagia",
                    }
                ],
                "evidence_validation": {
                    "is_publicly_supported": True,
                    "has_ai_evidence": True,
                    "source_count": 1,
                    "reliable_source_count": 0,
                    "confidence_level": "low",
                },
                "ai_maturity": {
                    "level": "emerging",
                    "score": 2,
                    "method": "keyword_and_evidence_rules",
                },
            }
        ],
        "nvidia_recommendations": [
            {
                "startup_name": "DiagIA",
                "recommendations": [
                    {
                        "technology_id": "nvidia_clara",
                        "confidence": "medium",
                        "match_score": 7,
                        "reason": "Healthtech match.",
                        "matched_startup_signals": [],
                        "matched_ai_signals": ["IA"],
                        "matched_sector": "healthtech",
                        "retrieved_from_vector_store": True,
                        "guardrails": ["Do not imply clinical validation."],
                        "missing_evidence": [],
                        "sources": [
                            {
                                "source_id": "nvidia_clara",
                                "title": "NVIDIA Clara",
                                "url": "https://www.nvidia.com/en-us/industries/healthcare-life-sciences/",
                                "source_type": "nvidia_official",
                            }
                        ],
                    }
                ],
                "evidence_gap": None,
            }
        ],
        "attempt_count": 1,
        "errors": [],
    }


def test_persist_startup_discovery_result_saves_pipeline_entities():
    client = FakeSupabaseClient()

    result = persist_startup_discovery_result(_sample_pipeline_result(), client=client)

    assert result["saved"] is True
    assert result["company_count"] == 1

    called_tables = [call[1] for call in client.calls]
    assert "discovery_runs" in called_tables
    assert "discovery_search_terms" in called_tables
    assert "companies" in called_tables
    assert "company_sources" in called_tables
    assert "company_ai_signals" in called_tables
    assert "company_evidence_validations" in called_tables
    assert "company_ai_maturity_assessments" in called_tables
    assert "company_nvidia_recommendations" in called_tables
    assert "company_nvidia_recommendation_sources" in called_tables
    assert "company_snapshots" in called_tables


def test_persist_startup_discovery_result_is_disabled_without_client(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

    result = persist_startup_discovery_result(_sample_pipeline_result())

    assert result["enabled"] is False
    assert result["saved"] is False
