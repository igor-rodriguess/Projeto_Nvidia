from __future__ import annotations

from typing import Any

import requests
from langchain_core.runnables import Runnable, RunnableLambda

from app.agents.ai_maturity_classifier_agent import classificar_maturidade_ia
from app.agents.evidence_validator_agent import validar_evidencias_scraper
from app.agents.scraper_agent import executar_scraper_agent
from app.agents.search_planner_agent import planejar_busca_ia_startup
from app.core.contracts import validate_contract
from app.core.schemas import (
    AIMaturityOutput,
    EvidenceValidationOutput,
    EvidenceValidatorInput,
    MaturityClassifierInput,
    PipelineInput,
    RecommenderInput,
    NVIDIARecommendationOutput,
    ScraperOutput,
    SearchPlanOutput,
)
from app.rag.recommender import NVIDIARecommenderRAG


def create_search_planner_chain(
    enable_retry: bool = True,
) -> Runnable[dict[str, Any], dict[str, Any]]:
    def invoke(payload: dict[str, Any]) -> dict[str, Any]:
        pipeline_input = validate_contract(PipelineInput, payload)
        startup = {
            "nome": pipeline_input.startup_name,
            "site": pipeline_input.site_oficial,
            "categoria": pipeline_input.categoria,
            "descricao_curta": pipeline_input.descricao_curta,
            "cidade": pipeline_input.cidade,
            "estado": pipeline_input.estado,
            "pais": pipeline_input.pais,
        }
        output = planejar_busca_ia_startup(startup, contexto=pipeline_input.contexto)
        return validate_contract(SearchPlanOutput, output).model_dump(mode="json")

    return _maybe_with_retry(RunnableLambda(invoke), enable_retry)


def create_scraper_chain(
    session: requests.Session | None = None,
    delay_seconds: float = 2.0,
    search_client: Any | None = None,
    firecrawl_client: Any | None = None,
    trafilatura_extractor: Any | None = None,
    enable_retry: bool = True,
) -> Runnable[dict[str, Any], dict[str, Any]]:
    def invoke(payload: dict[str, Any]) -> dict[str, Any]:
        plan = validate_contract(SearchPlanOutput, payload)
        output = executar_scraper_agent(
            plan.model_dump(mode="json"),
            session=session,
            delay_seconds=delay_seconds,
            search_client=search_client,
            firecrawl_client=firecrawl_client,
            trafilatura_extractor=trafilatura_extractor,
        )
        return validate_contract(ScraperOutput, output).model_dump(mode="json")

    return _maybe_with_retry(RunnableLambda(invoke), enable_retry)


def create_evidence_validator_chain(
    session: requests.Session | None = None,
    verificar_urls: bool = True,
    enable_retry: bool = True,
) -> Runnable[dict[str, Any], dict[str, Any]]:
    def invoke(payload: dict[str, Any]) -> dict[str, Any]:
        validator_input = validate_contract(EvidenceValidatorInput, payload)
        output = validar_evidencias_scraper(
            validator_input.dados_brutos.model_dump(mode="json"),
            site_oficial=validator_input.site_oficial,
            session=session,
            verificar_urls=verificar_urls,
        )
        return validate_contract(EvidenceValidationOutput, output).model_dump(mode="json")

    return _maybe_with_retry(RunnableLambda(invoke), enable_retry)


def create_classifier_chain(
    enable_retry: bool = True,
) -> Runnable[dict[str, Any], dict[str, Any]]:
    def invoke(payload: dict[str, Any]) -> dict[str, Any]:
        classifier_input = validate_contract(MaturityClassifierInput, payload)
        output = classificar_maturidade_ia(
            classifier_input.validacao.model_dump(mode="json")
        )
        return validate_contract(AIMaturityOutput, output).model_dump(mode="json")

    return _maybe_with_retry(RunnableLambda(invoke), enable_retry)


def create_recommender_chain(
    recommender: NVIDIARecommenderRAG | None = None,
    enable_retry: bool = True,
) -> Runnable[dict[str, Any], dict[str, Any]]:
    rag = recommender or NVIDIARecommenderRAG()

    def invoke(payload: dict[str, Any]) -> dict[str, Any]:
        recommender_input = validate_contract(RecommenderInput, payload)
        output = rag.recommend(recommender_input.classificacao_ia)
        return validate_contract(NVIDIARecommendationOutput, output).model_dump(mode="json")

    return _maybe_with_retry(RunnableLambda(invoke), enable_retry)


def _maybe_with_retry(
    runnable: Runnable[Any, Any],
    enable_retry: bool,
) -> Runnable[Any, Any]:
    if not enable_retry:
        return runnable
    return runnable.with_retry(
        retry_if_exception_type=(requests.RequestException, ValueError),
        wait_exponential_jitter=True,
        exponential_jitter_params={"initial": 2, "max": 8, "exp_base": 2, "jitter": 0},
        stop_after_attempt=3,
    )
