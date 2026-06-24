from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import feedparser
import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - covered by runtime environment
    load_dotenv = None

try:
    from ddgs import DDGS
except ImportError:  # pragma: no cover - covered by runtime environment
    DDGS = None

try:
    import trafilatura
except ImportError:  # pragma: no cover - covered by runtime environment
    trafilatura = None


LOGGER = logging.getLogger(__name__)

FIRECRAWL_SCRAPE_URL = "https://api.firecrawl.dev/v2/scrape"
FIRECRAWL_SEARCH_URL = "https://api.firecrawl.dev/v2/search"
SEARXNG_DEFAULT_BASE_URL = "http://localhost:8080"

if load_dotenv is not None:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

TECH_TERMS = (
    "machine learning",
    "inteligência artificial",
    "inteligencia artificial",
    "deep learning",
    "gpu",
    "nvidia",
    "modelo",
    "algoritmo",
    "dados",
    "predição",
    "predicao",
    "automação",
    "automacao",
    "llm",
    "nlp",
    "pytorch",
    "tensorflow",
    "data scientist",
    "ml engineer",
)

COMPLEMENTARY_SOURCES = [
    "braziljournal.com",
    "distrito.me",
    "startse.com",
    "cubo.network",
    "openstartups.net",
    "endeavor.org.br",
    "neofeed.com.br",
    "exame.com",
    "valor.globo.com",
]


class SearXNGSearchClient:
    def __init__(
        self,
        session: requests.Session,
        base_url: str | None = None,
        delay_seconds: float = 1.0,
        timeout: int = 10,
    ) -> None:
        self.session = session
        self.base_url = (base_url or os.getenv("SEARXNG_BASE_URL") or SEARXNG_DEFAULT_BASE_URL).rstrip("/")
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self._last_request_at = 0.0
        self.provider_name = "searxng"

    def search(self, query: str, count: int) -> list[dict[str, Any]]:
        self._wait()
        response = self.session.get(
            f"{self.base_url}/search",
            params={
                "q": query,
                "format": "json",
                "categories": "general",
                "language": "pt-BR",
            },
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        results = []

        for item in payload.get("results", [])[:count]:
            snippet = _clean(item.get("content"))
            results.append(
                {
                    "titulo": _clean(item.get("title")),
                    "url": _clean(item.get("url")),
                    "snippet": snippet,
                    "potencial_alto": _has_tech_terms(snippet),
                    "provedor_busca": self.provider_name,
                }
            )

        return [item for item in results if item["titulo"] and item["url"]]

    def _wait(self) -> None:
        if self.delay_seconds <= 0:
            return
        elapsed = time.perf_counter() - self._last_request_at
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self._last_request_at = time.perf_counter()


class DDGSSearchClient:
    def __init__(self, delay_seconds: float = 1.0) -> None:
        self.delay_seconds = delay_seconds
        self._last_request_at = 0.0
        self.provider_name = "ddgs"

    def search(self, query: str, count: int) -> list[dict[str, Any]]:
        if DDGS is None:
            raise ValueError("Dependência ddgs não instalada")

        self._wait()
        results = []
        with DDGS() as client:
            for item in client.text(query, max_results=count):
                snippet = _clean(item.get("body"))
                results.append(
                    {
                        "titulo": _clean(item.get("title")),
                        "url": _clean(item.get("href")),
                        "snippet": snippet,
                        "potencial_alto": _has_tech_terms(snippet),
                        "provedor_busca": self.provider_name,
                    }
                )
        return [item for item in results if item["titulo"] and item["url"]]

    def _wait(self) -> None:
        if self.delay_seconds <= 0:
            return
        elapsed = time.perf_counter() - self._last_request_at
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self._last_request_at = time.perf_counter()


class FirecrawlSearchClient:
    def __init__(
        self,
        session: requests.Session,
        api_key: str | None = None,
        delay_seconds: float = 2.0,
        timeout: int = 30,
    ) -> None:
        self.session = session
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self._last_request_at = 0.0
        self.provider_name = "firecrawl"

    def search(self, query: str, count: int) -> list[dict[str, Any]]:
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY não configurada")

        self._wait()
        response = self.session.post(
            FIRECRAWL_SEARCH_URL,
            json={
                "query": query,
                "sources": ["web"],
                "categories": [],
                "limit": count,
                "scrapeOptions": {
                    "onlyMainContent": True,
                    "maxAge": 172800000,
                    "formats": [],
                },
            },
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        raw_results = payload.get("data") or payload.get("results") or []
        results = []

        for item in raw_results[:count]:
            snippet = _clean(item.get("description") or item.get("snippet") or item.get("markdown"))
            results.append(
                {
                    "titulo": _clean(item.get("title")),
                    "url": _clean(item.get("url")),
                    "snippet": snippet,
                    "potencial_alto": _has_tech_terms(snippet),
                    "provedor_busca": self.provider_name,
                }
            )

        return [item for item in results if item["titulo"] and item["url"]]

    def _wait(self) -> None:
        if self.delay_seconds <= 0:
            return
        elapsed = time.perf_counter() - self._last_request_at
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self._last_request_at = time.perf_counter()


class SearchProviderRouter:
    def __init__(
        self,
        session: requests.Session,
        provider: str | None = None,
        delay_seconds: float = 1.0,
        timeout: int = 10,
    ) -> None:
        self.provider = (provider or os.getenv("SEARCH_PROVIDER") or "searxng").lower()
        self.clients = self._build_clients(session, delay_seconds, timeout)

    def search(self, query: str, count: int) -> list[dict[str, Any]]:
        errors = []
        for client in self.clients:
            try:
                results = client.search(query, count)
                if results:
                    return results
                errors.append(f"{client.provider_name}: sem resultados")
            except (requests.RequestException, ValueError) as exc:
                errors.append(f"{client.provider_name}: {exc}")
                LOGGER.warning("Provedor de busca falhou (%s): %s", client.provider_name, exc)
        raise ValueError("Nenhum provedor de busca disponível. Erros: " + " | ".join(errors))

    def _build_clients(
        self,
        session: requests.Session,
        delay_seconds: float,
        timeout: int,
    ) -> list[Any]:
        searxng = SearXNGSearchClient(session, delay_seconds=delay_seconds, timeout=timeout)
        ddgs = DDGSSearchClient(delay_seconds=delay_seconds)
        firecrawl = FirecrawlSearchClient(session, delay_seconds=delay_seconds, timeout=timeout)

        if self.provider == "ddgs":
            return [ddgs, searxng, firecrawl]
        if self.provider == "firecrawl":
            return [firecrawl, searxng, ddgs]
        if self.provider == "all":
            return [searxng, ddgs, firecrawl]
        return [searxng, ddgs, firecrawl]


class FirecrawlClient:
    def __init__(
        self,
        session: requests.Session,
        api_key: str | None = None,
        delay_seconds: float = 2.0,
        timeout: int = 30,
    ) -> None:
        self.session = session
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self._last_request_at = 0.0
        self.provider_name = "firecrawl"

    def scrape(self, url: str) -> dict[str, Any]:
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY não configurada")

        self._wait()
        response = self.session.post(
            FIRECRAWL_SCRAPE_URL,
            json={"url": url, "formats": ["markdown"]},
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data") or payload
        metadata = data.get("metadata") or {}

        return {
            "url": _clean(metadata.get("sourceURL") or metadata.get("url") or url),
            "titulo_pagina": _clean(metadata.get("title")),
            "conteudo_markdown": _clean(data.get("markdown") or data.get("content")),
            "metadados": metadata,
            "extrator": "firecrawl",
        }

    def _wait(self) -> None:
        if self.delay_seconds <= 0:
            return
        elapsed = time.perf_counter() - self._last_request_at
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self._last_request_at = time.perf_counter()


class TrafilaturaExtractor:
    def __init__(self, session: requests.Session, timeout: int = 10) -> None:
        self.session = session
        self.timeout = timeout
        self.provider_name = "trafilatura"

    def extract(self, url: str) -> dict[str, Any]:
        if trafilatura is None:
            raise ValueError("Dependência trafilatura não instalada")

        response = self.session.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=self.timeout,
        )
        response.raise_for_status()
        text = trafilatura.extract(
            response.text,
            include_comments=False,
            include_tables=False,
            output_format="txt",
        )
        if not text:
            raise ValueError("trafilatura não conseguiu extrair conteúdo principal; tente Firecrawl")

        metadata = trafilatura.extract_metadata(response.text)
        return {
            "url": response.url,
            "titulo_pagina": _clean(getattr(metadata, "title", "")),
            "conteudo_textual": _clean(text),
            "metadados": _metadata_to_dict(metadata),
            "extrator": "trafilatura",
        }


class ScraperAgent:
    def __init__(
        self,
        session: requests.Session | None = None,
        search_client: Any | None = None,
        firecrawl_client: FirecrawlClient | None = None,
        trafilatura_extractor: TrafilaturaExtractor | None = None,
        timeout: int = 10,
        search_delay_seconds: float = 1.0,
        firecrawl_delay_seconds: float = 2.0,
    ) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout
        self.search_client = search_client or SearchProviderRouter(
            self.session,
            delay_seconds=search_delay_seconds,
            timeout=timeout,
        )
        self.firecrawl = firecrawl_client or FirecrawlClient(
            self.session,
            delay_seconds=firecrawl_delay_seconds,
        )
        self.trafilatura = trafilatura_extractor or TrafilaturaExtractor(self.session, timeout=timeout)

    def executar(self, plano: dict[str, Any]) -> dict[str, Any]:
        started_at = time.perf_counter()
        startup = _clean(plano.get("startup"))
        tarefas = _normalizar_tarefas(plano)
        resultados = []
        erros = []

        metricas = {
            "tarefas_executadas": 0,
            "tarefas_com_erro": 0,
            "total_resultados_busca": 0,
            "total_paginas_coletadas": 0,
            "fontes_complementares_consultadas": 0,
            "tempo_total_execucao_segundos": 0.0,
        }

        for tarefa in tarefas:
            resultado, task_errors = self._executar_tarefa(tarefa)
            resultados.append(resultado)
            erros.extend(task_errors)
            metricas["tarefas_executadas"] += 1
            metricas["tarefas_com_erro"] += 1 if task_errors else 0
            metricas["total_resultados_busca"] += len(resultado.get("resultados_busca", []))
            metricas["total_paginas_coletadas"] += len(resultado.get("paginas_completas", []))
            if resultado.get("conteudo_markdown") or resultado.get("conteudo_textual"):
                metricas["total_paginas_coletadas"] += 1

        complementary = []
        if plano.get("varredura_complementar"):
            complementary, complementary_errors = self._executar_varredura_complementar(startup)
            erros.extend(complementary_errors)
            metricas["fontes_complementares_consultadas"] = len(complementary)
            metricas["total_resultados_busca"] += sum(len(item["resultados"]) for item in complementary)

        metricas["tempo_total_execucao_segundos"] = round(time.perf_counter() - started_at, 2)

        return {
            "startup": startup,
            "timestamp_coleta": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "status": "parcial" if erros else "completo",
            "metricas": metricas,
            "resultados": resultados,
            "resultados_buscas": _flatten_search_results(resultados),
            "paginas_completas": _flatten_full_pages(resultados),
            "varredura_complementar": complementary,
            "erros": erros,
        }

    def _executar_tarefa(self, tarefa: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        tipo = tarefa.get("tipo")
        try:
            if tipo in {"busca_web", "busca_site"}:
                return self._executar_busca_web(tarefa), []
            if tipo == "acesso_direto":
                return self._executar_acesso_direto(tarefa), []
            if tipo == "feed_rss":
                return self._executar_feed_rss(tarefa), []
            if tipo == "api_get":
                return _resultado_base(tarefa), [_erro(tarefa, tarefa.get("url"), "api_get não é suportado nesta versão; use SearXNG, DDGS, Firecrawl, trafilatura ou feed_rss")]
            raise ValueError(f"Tipo de tarefa não suportado: {tipo}")
        except (requests.RequestException, ValueError) as exc:
            return _resultado_base(tarefa), [_erro(tarefa, tarefa.get("url"), str(exc))]

    def _executar_busca_web(self, tarefa: dict[str, Any]) -> dict[str, Any]:
        consulta = _clean(tarefa.get("consulta"))
        max_resultados = int(tarefa.get("max_resultados") or 10)
        search_results = self.search_client.search(consulta, max_resultados)
        full_pages = []

        for item in search_results:
            if not item["potencial_alto"] or len(full_pages) >= 3:
                continue
            try:
                page = self._extrair_pagina(item["url"], preferred_extractor="firecrawl")
                full_pages.append(page)
            except (requests.RequestException, ValueError) as exc:
                LOGGER.warning("Extração falhou para %s: %s", item["url"], exc)

        return {
            **_resultado_base(tarefa),
            "consulta": consulta,
            "resultados_busca": search_results,
            "paginas_completas": full_pages,
        }

    def _executar_acesso_direto(self, tarefa: dict[str, Any]) -> dict[str, Any]:
        url = _clean(tarefa.get("url"))
        extractor = _clean(tarefa.get("extrator") or "firecrawl").lower()
        page = self._extrair_pagina(url, preferred_extractor=extractor)

        return {
            **_resultado_base(tarefa),
            "url": url,
            **page,
        }

    def _executar_feed_rss(self, tarefa: dict[str, Any]) -> dict[str, Any]:
        url = _clean(tarefa.get("url"))
        filtro = _clean(tarefa.get("filtro_titulo") or tarefa.get("startup")).lower()
        response = self.session.get(url, headers={"User-Agent": USER_AGENT}, timeout=self.timeout)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        items = []

        for entry in feed.entries:
            title = _clean(getattr(entry, "title", ""))
            description = _clean(getattr(entry, "summary", ""))
            if filtro and filtro not in f"{title} {description}".lower():
                continue
            items.append(
                {
                    "titulo": title,
                    "link": _clean(getattr(entry, "link", "")),
                    "descricao": description,
                    "data": _clean(getattr(entry, "published", "")),
                }
            )

        return {
            **_resultado_base(tarefa),
            "url_feed": url,
            "itens_filtrados": items,
        }

    def _executar_varredura_complementar(
        self,
        startup: str,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        output = []
        errors = []
        for source in COMPLEMENTARY_SOURCES:
            consulta = f'"{startup}" (IA OR "inteligência artificial" OR "machine learning") site:{source}'
            try:
                results = self.search_client.search(consulta, 5)
            except (requests.RequestException, ValueError) as exc:
                results = []
                errors.append({"task_id": "varredura_complementar", "url": source, "erro": str(exc)})
            output.append(
                {
                    "fonte": source,
                    "consulta_usada": consulta,
                    "resultados": results,
                }
            )
        return output, errors

    def _extrair_pagina(self, url: str, preferred_extractor: str = "firecrawl") -> dict[str, Any]:
        if preferred_extractor == "trafilatura":
            return self.trafilatura.extract(url)
        if preferred_extractor != "firecrawl":
            raise ValueError(f"Extrator não suportado: {preferred_extractor}")

        try:
            return self.firecrawl.scrape(url)
        except (requests.RequestException, ValueError) as exc:
            LOGGER.warning("Firecrawl indisponível para %s; tentando trafilatura: %s", url, exc)
            return self.trafilatura.extract(url)


def executar_scraper_agent(
    plano: dict[str, Any],
    session: requests.Session | None = None,
    delay_seconds: float | None = None,
    respect_robots: bool | None = None,
    search_client: Any | None = None,
    firecrawl_client: FirecrawlClient | None = None,
    trafilatura_extractor: TrafilaturaExtractor | None = None,
) -> dict[str, Any]:
    search_delay = 1.0 if delay_seconds is None else delay_seconds
    firecrawl_delay = 2.0 if delay_seconds is None else delay_seconds
    return ScraperAgent(
        session=session,
        search_client=search_client,
        firecrawl_client=firecrawl_client,
        trafilatura_extractor=trafilatura_extractor,
        search_delay_seconds=search_delay,
        firecrawl_delay_seconds=firecrawl_delay,
    ).executar(plano)


def salvar_resultado_scraper(resultado: dict[str, Any], output_dir: Path | None = None) -> Path:
    output_dir = output_dir or Path("data/raw/_evidencias")
    output_dir.mkdir(parents=True, exist_ok=True)
    startup_slug = _slugify(resultado.get("startup", "startup"))
    timestamp = resultado["timestamp_coleta"].replace("-", "").replace(":", "").replace("Z", "Z")
    path = output_dir / f"evidencias_{startup_slug}_{timestamp}.json"
    path.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _normalizar_tarefas(plano: dict[str, Any]) -> list[dict[str, Any]]:
    tarefas = plano.get("tarefas")
    if isinstance(tarefas, list) and tarefas:
        return tarefas

    normalized = []
    for index, item in enumerate(plano.get("plano_consultas", []), start=1):
        normalized.append(
            {
                "id": f"task_{index}",
                "tipo": "busca_web",
                "consulta": item["consulta"],
                "motor": "searxng",
                "max_resultados": item.get("max_resultados", 10),
                "camada": item.get("camada"),
                "objetivo": item.get("objetivo"),
            }
        )
    return normalized


def _resultado_base(tarefa: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": tarefa.get("id"),
        "tipo": tarefa.get("tipo"),
        "camada": tarefa.get("camada"),
        "objetivo": tarefa.get("objetivo"),
    }


def _erro(tarefa: dict[str, Any], url: str | None, message: str) -> dict[str, Any]:
    return {
        "task_id": tarefa.get("id"),
        "url": url,
        "erro": message,
    }


def _flatten_search_results(resultados: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flattened = []
    for resultado in resultados:
        for item in resultado.get("resultados_busca", []):
            flattened.append(
                {
                    "task_id": resultado.get("task_id"),
                    "camada": resultado.get("camada"),
                    "consulta": resultado.get("consulta"),
                    **item,
                }
            )
    return flattened


def _flatten_full_pages(resultados: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flattened = []
    for resultado in resultados:
        if resultado.get("conteudo_markdown") or resultado.get("conteudo_textual"):
            flattened.append(
                {
                    "task_id": resultado.get("task_id"),
                    "camada": resultado.get("camada"),
                    "url": resultado.get("url"),
                    "titulo_pagina": resultado.get("titulo_pagina"),
                    "conteudo_markdown": resultado.get("conteudo_markdown"),
                    "conteudo_textual": resultado.get("conteudo_textual"),
                    "metadados": resultado.get("metadados", {}),
                    "extrator": resultado.get("extrator"),
                }
            )
        for page in resultado.get("paginas_completas", []):
            flattened.append(
                {
                    "task_id": resultado.get("task_id"),
                    "camada": resultado.get("camada"),
                    **page,
                }
            )
    return flattened


def _has_tech_terms(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in TECH_TERMS)


def _metadata_to_dict(metadata: Any) -> dict[str, str]:
    if not metadata:
        return {}
    fields = ("title", "author", "date", "description", "sitename")
    return {field: _clean(getattr(metadata, field, "")) for field in fields if _clean(getattr(metadata, field, ""))}


def _slugify(value: str) -> str:
    value = _clean(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "startup"


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split()).strip()
