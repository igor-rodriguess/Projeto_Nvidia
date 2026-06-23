from datetime import datetime, timezone
from typing import Any, Dict, List

from app.core.startup_analysis_state import StartupAnalysisState
from app.db.supabase_client import SupabaseRestClient, get_supabase_client


def persist_startup_discovery_result(
    result: StartupAnalysisState,
    client: SupabaseRestClient | None = None,
) -> Dict[str, Any]:
    supabase = client or get_supabase_client()
    if supabase is None:
        return {
            "enabled": False,
            "saved": False,
            "reason": "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are not configured",
        }

    try:
        run = _save_discovery_run(supabase, result)
        run_id = run["id"]
        _save_search_terms(supabase, run_id, result.get("search_terms", []))

        recommendations_by_startup = _recommendations_by_startup(
            result.get("nvidia_recommendations", [])
        )

        companies_to_persist = _companies_to_persist(result)
        saved_companies = []
        for startup in companies_to_persist:
            company = _upsert_company(supabase, startup)
            company_id = company["id"]
            saved_companies.append(company_id)

            _save_company_discovery(supabase, company_id, run_id, startup)
            source_ids = _save_company_sources(
                supabase,
                company_id,
                run_id,
                startup.get("sources", []),
                result.get("sources", []),
            )
            _save_ai_signals(supabase, company_id, startup, source_ids)
            _save_evidence_validation(supabase, company_id, run_id, startup)
            _save_ai_maturity(supabase, company_id, run_id, startup)
            _save_nvidia_recommendations(
                supabase,
                company_id,
                run_id,
                recommendations_by_startup.get(startup.get("name", ""), {}),
            )
            _save_company_snapshot(supabase, company_id, run_id, startup)

        _mark_run_completed(supabase, run_id, result)

        return {
            "enabled": True,
            "saved": True,
            "discovery_run_id": run_id,
            "company_count": len(saved_companies),
        }
    except Exception as exc:
        return {
            "enabled": True,
            "saved": False,
            "error": str(exc),
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _companies_to_persist(result: StartupAnalysisState) -> List[Dict[str, Any]]:
    return result.get("startups", [])


def _save_discovery_run(
    client: SupabaseRestClient,
    result: StartupAnalysisState,
) -> Dict[str, Any]:
    return client.insert(
        "discovery_runs",
        {
            "query": result.get("query", ""),
            "status": "running",
            "attempt_count": result.get("attempt_count", 0),
            "errors": result.get("errors", []),
            "raw_result": result,
            "started_at": _utc_now(),
        },
    )


def _mark_run_completed(
    client: SupabaseRestClient,
    run_id: str,
    result: StartupAnalysisState,
) -> None:
    status = "completed" if not result.get("errors") else "partial"
    client.upsert(
        "discovery_runs",
        {
            "id": run_id,
            "query": result.get("query", ""),
            "status": status,
            "attempt_count": result.get("attempt_count", 0),
            "errors": result.get("errors", []),
            "raw_result": result,
            "completed_at": _utc_now(),
        },
        on_conflict="id",
    )


def _save_search_terms(
    client: SupabaseRestClient,
    run_id: str,
    search_terms: List[str],
) -> None:
    payload = [
        {
            "discovery_run_id": run_id,
            "term": term,
            "position": index,
        }
        for index, term in enumerate(search_terms)
    ]
    client.bulk_insert("discovery_search_terms", payload)


def _upsert_company(
    client: SupabaseRestClient,
    startup: Dict[str, Any],
) -> Dict[str, Any]:
    return client.upsert(
        "companies",
        {
            "name": startup.get("name", "Unknown startup"),
            "description": startup.get("description"),
            "sector": startup.get("sector"),
            "website_url": startup.get("website_url"),
            "country": startup.get("country"),
            "city": startup.get("city"),
            "state_region": startup.get("state_region"),
            "founded_year": startup.get("founded_year"),
            "status": "validated"
            if startup.get("evidence_validation", {}).get("is_publicly_supported")
            else "discovered",
            "last_seen_at": _utc_now(),
        },
        on_conflict="normalized_name",
    )


def _save_company_discovery(
    client: SupabaseRestClient,
    company_id: str,
    run_id: str,
    startup: Dict[str, Any],
) -> None:
    client.upsert(
        "company_discoveries",
        {
            "company_id": company_id,
            "discovery_run_id": run_id,
            "extracted_name": startup.get("name", ""),
            "extracted_description": startup.get("description"),
            "extracted_sector": startup.get("sector"),
            "raw_startup": startup,
        },
        on_conflict="company_id,discovery_run_id",
    )


def _source_lookup(global_sources: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {source.get("url", ""): source for source in global_sources if source.get("url")}


def _save_company_sources(
    client: SupabaseRestClient,
    company_id: str,
    run_id: str,
    startup_sources: List[Dict[str, Any]],
    global_sources: List[Dict[str, Any]],
) -> Dict[str, str]:
    lookup = _source_lookup(global_sources)
    saved_source_ids = {}

    for source in startup_sources:
        url = source.get("url", "")
        enriched = {**lookup.get(url, {}), **source}
        saved = client.upsert(
            "company_sources",
            {
                "company_id": company_id,
                "discovery_run_id": run_id,
                "title": enriched.get("title", "Untitled source"),
                "url": url,
                "snippet": enriched.get("snippet"),
                "source_type": enriched.get("source_type", "public_search"),
                "collected_at": enriched.get("collected_at") or _utc_now(),
                "metadata": enriched,
            },
            on_conflict="company_id,url_hash",
        )
        if saved.get("id"):
            saved_source_ids[url] = saved["id"]

    return saved_source_ids


def _save_ai_signals(
    client: SupabaseRestClient,
    company_id: str,
    startup: Dict[str, Any],
    source_ids: Dict[str, str],
) -> None:
    first_source_id = next(iter(source_ids.values()), None)
    for signal in startup.get("possible_ai_signals", []):
        client.upsert(
            "company_ai_signals",
            {
                "company_id": company_id,
                "signal": signal,
                "signal_type": "keyword",
                "evidence_source_id": first_source_id,
                "confidence": "medium",
            },
            on_conflict="company_id,signal,signal_type",
        )


def _save_evidence_validation(
    client: SupabaseRestClient,
    company_id: str,
    run_id: str,
    startup: Dict[str, Any],
) -> None:
    validation = startup.get("evidence_validation")
    if not validation:
        return

    client.insert(
        "company_evidence_validations",
        {
            "company_id": company_id,
            "discovery_run_id": run_id,
            "is_publicly_supported": validation.get("is_publicly_supported", False),
            "has_ai_evidence": validation.get("has_ai_evidence", False),
            "source_count": validation.get("source_count", 0),
            "reliable_source_count": validation.get("reliable_source_count", 0),
            "confidence_level": validation.get("confidence_level", "none"),
            "validation_payload": validation,
        },
    )


def _save_ai_maturity(
    client: SupabaseRestClient,
    company_id: str,
    run_id: str,
    startup: Dict[str, Any],
) -> None:
    maturity = startup.get("ai_maturity")
    if not maturity:
        return

    client.insert(
        "company_ai_maturity_assessments",
        {
            "company_id": company_id,
            "discovery_run_id": run_id,
            "level": maturity.get("level", "unclear"),
            "score": maturity.get("score", 0),
            "method": maturity.get("method", "keyword_and_evidence_rules"),
            "assessment_payload": maturity,
        },
    )


def _recommendations_by_startup(
    recommendations: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    return {
        recommendation.get("startup_name", ""): recommendation
        for recommendation in recommendations
    }


def _save_nvidia_recommendations(
    client: SupabaseRestClient,
    company_id: str,
    run_id: str,
    recommendation_group: Dict[str, Any],
) -> None:
    for recommendation in recommendation_group.get("recommendations", []):
        saved = client.insert(
            "company_nvidia_recommendations",
            {
                "company_id": company_id,
                "discovery_run_id": run_id,
                "technology_id": recommendation.get("technology_id"),
                "confidence": recommendation.get("confidence", "low"),
                "match_score": recommendation.get("match_score", 0),
                "reason": recommendation.get("reason", ""),
                "matched_startup_signals": recommendation.get("matched_startup_signals", []),
                "matched_ai_signals": recommendation.get("matched_ai_signals", []),
                "matched_sector": recommendation.get("matched_sector"),
                "retrieved_from_vector_store": recommendation.get(
                    "retrieved_from_vector_store", False
                ),
                "guardrails": recommendation.get("guardrails", []),
                "missing_evidence": recommendation.get("missing_evidence", []),
                "recommendation_payload": recommendation,
            },
        )
        recommendation_id = saved.get("id")
        if not recommendation_id:
            continue

        client.bulk_insert(
            "company_nvidia_recommendation_sources",
            [
                {
                    "recommendation_id": recommendation_id,
                    "source_id": source.get("source_id", ""),
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                    "source_type": source.get("source_type", ""),
                }
                for source in recommendation.get("sources", [])
            ],
        )


def _save_company_snapshot(
    client: SupabaseRestClient,
    company_id: str,
    run_id: str,
    startup: Dict[str, Any],
) -> None:
    client.insert(
        "company_snapshots",
        {
            "company_id": company_id,
            "discovery_run_id": run_id,
            "snapshot_type": "pipeline_startup_result",
            "payload": startup,
        },
    )
