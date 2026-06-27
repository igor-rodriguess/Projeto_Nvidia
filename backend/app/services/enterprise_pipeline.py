from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import requests
from langchain_core.runnables import Runnable, RunnableLambda

from app.chains.agent_chains import (
    create_classifier_chain,
    create_evidence_validator_chain,
    create_recommender_chain,
    create_scraper_chain,
    create_search_planner_chain,
)
from app.core.cache import JsonFileCache
from app.core.contracts import validate_contract
from app.core.observability import LOGGER
from app.core.retry import execute_with_retry
from app.core.schemas import PipelineInput, PipelineOutput, StageTrace
from app.rag.recommender import NVIDIARecommenderRAG


class EnterprisePipeline:
    def __init__(
        self,
        session: requests.Session | None = None,
        recommender: NVIDIARecommenderRAG | None = None,
        cache: JsonFileCache | None = None,
        use_cache: bool = True,
        delay_seconds: float = 2.0,
        verificar_urls: bool = True,
        retry_wait_multiplier: float = 2.0,
        search_client: Any | None = None,
        firecrawl_client: Any | None = None,
        trafilatura_extractor: Any | None = None,
    ) -> None:
        self.cache = cache or JsonFileCache()
        self.use_cache = use_cache
        self.retry_wait_multiplier = retry_wait_multiplier
        self.search_chain = create_search_planner_chain(enable_retry=False)
        self.scraper_chain = create_scraper_chain(
            session=session,
            delay_seconds=delay_seconds,
            search_client=search_client,
            firecrawl_client=firecrawl_client,
            trafilatura_extractor=trafilatura_extractor,
            enable_retry=False,
        )
        self.validator_chain = create_evidence_validator_chain(
            session=session,
            verificar_urls=verificar_urls,
            enable_retry=False,
        )
        self.classifier_chain = create_classifier_chain(enable_retry=False)
        self.recommender_chain = create_recommender_chain(
            recommender=recommender,
            enable_retry=False,
        )
        self.runnable = self._build_runnable()

    def invoke(self, payload: PipelineInput | dict[str, Any]) -> dict[str, Any]:
        raw = payload.model_dump(mode="json") if isinstance(payload, PipelineInput) else payload
        return self.runnable.invoke(raw)

    def _build_runnable(self) -> Runnable[dict[str, Any], dict[str, Any]]:
        return (
            RunnableLambda(self._initialize)
            | RunnableLambda(self._search_stage)
            | RunnableLambda(self._scraper_stage)
            | RunnableLambda(self._validator_stage)
            | RunnableLambda(self._classifier_stage)
            | RunnableLambda(self._recommender_stage)
            | RunnableLambda(self._finalize)
        )

    def _initialize(self, payload: dict[str, Any]) -> dict[str, Any]:
        pipeline_input = validate_contract(PipelineInput, payload)
        return {
            "input": pipeline_input.model_dump(mode="json"),
            "trace": {},
            "errors": [],
        }

    def _search_stage(self, state: dict[str, Any]) -> dict[str, Any]:
        return self._execute_stage(
            state,
            stage="search_planner",
            input_payload=state["input"],
            output_key="search_plan",
            operation=lambda: self.search_chain.invoke(state["input"]),
        )

    def _scraper_stage(self, state: dict[str, Any]) -> dict[str, Any]:
        return self._execute_dependent_stage(
            state,
            stage="scraper",
            dependency="search_plan",
            output_key="scraper_output",
            input_builder=lambda: state["search_plan"],
            operation=lambda payload: self.scraper_chain.invoke(payload),
        )

    def _validator_stage(self, state: dict[str, Any]) -> dict[str, Any]:
        return self._execute_dependent_stage(
            state,
            stage="evidence_validator",
            dependency="scraper_output",
            output_key="validation_output",
            input_builder=lambda: {
                "site_oficial": state["input"].get("site_oficial"),
                "dados_brutos": state["scraper_output"],
            },
            operation=lambda payload: self.validator_chain.invoke(payload),
        )

    def _classifier_stage(self, state: dict[str, Any]) -> dict[str, Any]:
        return self._execute_dependent_stage(
            state,
            stage="ai_maturity_classifier",
            dependency="validation_output",
            output_key="classification_output",
            input_builder=lambda: {"validacao": state["validation_output"]},
            operation=lambda payload: self.classifier_chain.invoke(payload),
        )

    def _recommender_stage(self, state: dict[str, Any]) -> dict[str, Any]:
        return self._execute_dependent_stage(
            state,
            stage="nvidia_recommender_rag",
            dependency="classification_output",
            output_key="recommendation_output",
            input_builder=lambda: {"classificacao_ia": state["classification_output"]},
            operation=lambda payload: self.recommender_chain.invoke(payload),
        )

    def _execute_dependent_stage(
        self,
        state: dict[str, Any],
        stage: str,
        dependency: str,
        output_key: str,
        input_builder: Callable[[], dict[str, Any]],
        operation: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> dict[str, Any]:
        if dependency not in state:
            message = f"Etapa {stage} não executada porque {dependency} está ausente"
            state["errors"].append(message)
            state["trace"][stage] = StageTrace(
                status="parcial",
                duration_ms=0,
                attempts=0,
                error=message,
            ).model_dump(mode="json")
            return state
        input_payload = input_builder()
        return self._execute_stage(
            state,
            stage=stage,
            input_payload=input_payload,
            output_key=output_key,
            operation=lambda: operation(input_payload),
        )

    def _execute_stage(
        self,
        state: dict[str, Any],
        stage: str,
        input_payload: dict[str, Any],
        output_key: str,
        operation: Callable[[], dict[str, Any]],
    ) -> dict[str, Any]:
        started = time.perf_counter()
        cache_key = self.cache.key_for(f"v1_{stage}", input_payload)
        if self.use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                state[output_key] = cached
                embedded_errors = _embedded_errors(cached)
                state["errors"].extend(f"{stage}: {error}" for error in embedded_errors)
                state["trace"][stage] = StageTrace(
                    status="cache",
                    duration_ms=round((time.perf_counter() - started) * 1000, 2),
                    attempts=0,
                    output=cached,
                ).model_dump(mode="json")
                LOGGER.info("stage_cache_hit", stage=stage, startup=state["input"]["startup_name"])
                return state

        try:
            output, attempts = execute_with_retry(
                operation,
                stage=stage,
                retryable=(Exception,),
                max_attempts=3,
                wait_multiplier=self.retry_wait_multiplier,
            )
            if self.use_cache:
                self.cache.set(cache_key, output)
            duration = round((time.perf_counter() - started) * 1000, 2)
            state[output_key] = output
            embedded_errors = _embedded_errors(output)
            state["errors"].extend(f"{stage}: {error}" for error in embedded_errors)
            state["trace"][stage] = StageTrace(
                status="parcial" if embedded_errors else "completo",
                duration_ms=duration,
                attempts=attempts,
                tokens_consumidos=_tokens_from_output(output),
                output=output,
            ).model_dump(mode="json")
            LOGGER.info(
                "pipeline_stage_completed",
                stage=stage,
                duration_ms=duration,
                attempts=attempts,
                result_count=_result_count(output),
                tokens_consumidos=_tokens_from_output(output),
            )
        except Exception as exc:
            duration = round((time.perf_counter() - started) * 1000, 2)
            message = f"{stage}: {exc}"
            state["errors"].append(message)
            state["trace"][stage] = StageTrace(
                status="parcial",
                duration_ms=duration,
                attempts=3,
                error=str(exc),
            ).model_dump(mode="json")
            LOGGER.error("pipeline_stage_failed", stage=stage, duration_ms=duration, error=str(exc))
        return state

    def _finalize(self, state: dict[str, Any]) -> dict[str, Any]:
        classification = state.get("classification_output") or {}
        recommendation = state.get("recommendation_output")
        output = {
            "startup": state["input"]["startup_name"],
            "status": "parcial" if state["errors"] else "completo",
            "classificacao": classification.get("classificacao"),
            "nivel_maturidade": classification.get("nivel_maturidade"),
            "recomendacao": recommendation,
            "trace": state["trace"],
            "errors": state["errors"],
        }
        return validate_contract(PipelineOutput, output).model_dump(mode="json")


def create_pipeline(**kwargs: Any) -> Runnable[dict[str, Any], dict[str, Any]]:
    return EnterprisePipeline(**kwargs).runnable


def run_enterprise_pipeline(
    payload: PipelineInput | dict[str, Any],
    **kwargs: Any,
) -> dict[str, Any]:
    return EnterprisePipeline(**kwargs).invoke(payload)


def _result_count(output: dict[str, Any]) -> int:
    for key in ("recomendacoes", "evidencias_validadas", "resultados_buscas", "plano_consultas"):
        value = output.get(key)
        if isinstance(value, list):
            return len(value)
    return 1


def _tokens_from_output(output: dict[str, Any]) -> int:
    usage = output.get("usage_metadata") or output.get("token_usage") or {}
    return int(usage.get("total_tokens") or usage.get("total") or 0)


def _embedded_errors(output: dict[str, Any]) -> list[str]:
    errors = output.get("erros") or output.get("erros_validacao") or output.get("errors") or []
    normalized = []
    for error in errors:
        if isinstance(error, dict):
            normalized.append(str(error.get("erro") or error.get("mensagem") or error))
        else:
            normalized.append(str(error))
    if output.get("status") == "falha" and not normalized:
        normalized.append("etapa retornou status falha")
    return normalized
