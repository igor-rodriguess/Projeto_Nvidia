from __future__ import annotations

import json
import logging
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote_plus, unquote, urljoin, urlparse
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup


LOGGER = logging.getLogger(__name__)

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
    "startse.com",
    "distrito.me",
    "cubo.network",
    "openstartups.net",
    "endeavor.org.br",
    "braziljournal.com",
    "neofeed.com.br",
    "exame.com",
    "valor.globo.com",
]


class ScraperAgent:
    def __init__(
        self,
        session: requests.Session | None = None,
        timeout: int = 10,
        delay_seconds: float = 2.0,
        respect_robots: bool = True,
    ) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout
        self.delay_seconds = delay_seconds
        self.respect_robots = respect_robots
        self.headers = {"User-Agent": USER_AGENT}
        self._last_domain_access: dict[str, float] = {}
        self._robots_cache: dict[str, RobotFileParser | None] = {}

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
            if resultado.get("conteudo_textual"):
                metricas["total_paginas_coletadas"] += 1

        complementary = []
        if plano.get("varredura_complementar"):
            complementary = self._executar_varredura_complementar(startup)
            metricas["fontes_complementares_consultadas"] = len(complementary)
            metricas["total_resultados_busca"] += sum(len(item["resultados"]) for item in complementary)

        metricas["tempo_total_execucao_segundos"] = round(time.perf_counter() - started_at, 2)

        return {
            "startup": startup,
            "timestamp_coleta": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "status": "parcial" if erros else "completo",
            "metricas": metricas,
            "resultados": resultados,
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
            if tipo == "api_get":
                return self._executar_api_get(tarefa), []
            if tipo == "feed_rss":
                return self._executar_feed_rss(tarefa), []
            raise ValueError(f"Tipo de tarefa não suportado: {tipo}")
        except requests.RequestException as exc:
            return _resultado_base(tarefa), [_erro(tarefa, tarefa.get("url"), str(exc))]
        except ValueError as exc:
            return _resultado_base(tarefa), [_erro(tarefa, tarefa.get("url"), str(exc))]
        except ElementTree.ParseError as exc:
            return _resultado_base(tarefa), [_erro(tarefa, tarefa.get("url"), f"Feed/XML inválido: {exc}")]

    def _executar_busca_web(self, tarefa: dict[str, Any]) -> dict[str, Any]:
        consulta = _clean(tarefa.get("consulta"))
        max_resultados = int(tarefa.get("max_resultados") or 10)
        search_results = self._buscar_duckduckgo(consulta, max_resultados)
        full_pages = []

        for item in search_results:
            item["alto_potencial"] = _has_tech_terms(item.get("snippet", ""))
            if not item["alto_potencial"] or len(full_pages) >= 3:
                continue
            try:
                page = self._coletar_pagina(item["url"])
                full_pages.append(page)
            except requests.RequestException as exc:
                LOGGER.warning("Falha ao coletar página de resultado %s: %s", item["url"], exc)

        return {
            **_resultado_base(tarefa),
            "consulta": consulta,
            "resultados_busca": search_results,
            "paginas_completas": full_pages,
        }

    def _executar_acesso_direto(self, tarefa: dict[str, Any]) -> dict[str, Any]:
        url = _clean(tarefa.get("url"))
        page = self._coletar_pagina(url)
        return {
            **_resultado_base(tarefa),
            "url": url,
            "conteudo_textual": page["conteudo_textual"],
            "titulo_pagina": page["titulo_pagina"],
            "metadados": page["metadados"],
        }

    def _executar_api_get(self, tarefa: dict[str, Any]) -> dict[str, Any]:
        headers = dict(tarefa.get("headers") or {})
        if any("{{" in str(value) and "}}" in str(value) for value in headers.values()):
            raise ValueError("chave necessária para executar api_get")

        url = _clean(tarefa.get("url"))
        response = self._get(url, headers=headers)
        response.raise_for_status()
        payload = response.json()
        campo_dados = tarefa.get("campo_dados")

        return {
            **_resultado_base(tarefa),
            "url": url,
            "dados_json": payload.get(campo_dados) if campo_dados and isinstance(payload, dict) else payload,
        }

    def _executar_feed_rss(self, tarefa: dict[str, Any]) -> dict[str, Any]:
        url = _clean(tarefa.get("url"))
        filtro = _clean(tarefa.get("filtro_titulo")).lower()
        response = self._get(url)
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)
        items = []

        for item in root.findall(".//item"):
            title = _xml_text(item, "title")
            description = _xml_text(item, "description")
            if filtro and filtro not in f"{title} {description}".lower():
                continue
            items.append(
                {
                    "titulo": title,
                    "link": _xml_text(item, "link"),
                    "descricao": description,
                    "data": _xml_text(item, "pubDate"),
                }
            )

        return {
            **_resultado_base(tarefa),
            "url_feed": url,
            "itens_filtrados": items,
        }

    def _executar_varredura_complementar(self, startup: str) -> list[dict[str, Any]]:
        output = []
        for source in COMPLEMENTARY_SOURCES:
            consulta = f'"{startup}" (IA OR "inteligência artificial" OR "machine learning") site:{source}'
            try:
                results = self._buscar_duckduckgo(consulta, 5)
            except requests.RequestException as exc:
                LOGGER.warning("Falha na varredura complementar %s: %s", source, exc)
                results = []
            output.append(
                {
                    "fonte": source,
                    "consulta_usada": consulta,
                    "resultados": results,
                }
            )
        return output

    def _buscar_duckduckgo(self, consulta: str, max_resultados: int) -> list[dict[str, Any]]:
        url = f"https://duckduckgo.com/html/?q={quote_plus(consulta)}"
        response = self._get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for result in soup.select(".result"):
            title_node = result.select_one(".result__a")
            snippet_node = result.select_one(".result__snippet")
            if not title_node:
                continue

            link = _resolve_duckduckgo_url(title_node.get("href") or "")
            title = _clean(title_node.get_text(" ", strip=True))
            snippet = _clean(snippet_node.get_text(" ", strip=True) if snippet_node else "")
            if not title or not link:
                continue

            results.append(
                {
                    "titulo": title,
                    "url": link,
                    "snippet": snippet,
                    "alto_potencial": _has_tech_terms(snippet),
                }
            )
            if len(results) >= max_resultados:
                break

        return results

    def _coletar_pagina(self, url: str) -> dict[str, Any]:
        response = self._get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for node in soup(["script", "style", "noscript", "svg", "img", "form"]):
            node.decompose()

        title = _clean(soup.title.get_text(" ", strip=True) if soup.title else "")
        text = _clean_visible_text(soup)
        return {
            "url": response.url,
            "titulo_pagina": title,
            "conteudo_textual": text,
            "metadados": _extract_metadata(soup),
        }

    def _get(self, url: str, headers: dict[str, str] | None = None) -> requests.Response:
        if not url:
            raise ValueError("URL ausente")
        if self.respect_robots and not self._allowed_by_robots(url):
            raise ValueError("Bloqueado por robots.txt")

        self._wait_domain(url)
        request_headers = {**self.headers, **(headers or {})}
        return self.session.get(
            url,
            headers=request_headers,
            timeout=self.timeout,
            allow_redirects=True,
        )

    def _wait_domain(self, url: str) -> None:
        domain = urlparse(url).netloc
        if not domain or self.delay_seconds <= 0:
            return
        elapsed = time.perf_counter() - self._last_domain_access.get(domain, 0)
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self._last_domain_access[domain] = time.perf_counter()

    def _allowed_by_robots(self, url: str) -> bool:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return True
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self._robots_cache:
            self._robots_cache[base] = self._load_robots(base)
        parser = self._robots_cache[base]
        return True if parser is None else parser.can_fetch(USER_AGENT, url)

    def _load_robots(self, base_url: str) -> RobotFileParser | None:
        robots_url = urljoin(base_url, "/robots.txt")
        try:
            response = self.session.get(robots_url, headers=self.headers, timeout=self.timeout)
            if response.status_code >= 400:
                return None
            parser = RobotFileParser()
            parser.parse(response.text.splitlines())
            return parser
        except requests.RequestException:
            return None


def executar_scraper_agent(
    plano: dict[str, Any],
    session: requests.Session | None = None,
    delay_seconds: float = 2.0,
    respect_robots: bool = True,
) -> dict[str, Any]:
    return ScraperAgent(
        session=session,
        delay_seconds=delay_seconds,
        respect_robots=respect_robots,
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
                "motor": "duckduckgo",
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


def _has_tech_terms(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in TECH_TERMS)


def _resolve_duckduckgo_url(href: str) -> str:
    if href.startswith("//duckduckgo.com/l/"):
        href = "https:" + href
    parsed = urlparse(href)
    query = parse_qs(parsed.query)
    if "uddg" in query:
        return unquote(query["uddg"][0])
    return href


def _clean_visible_text(soup: BeautifulSoup) -> str:
    chunks = []
    for node in soup.find_all(["h1", "h2", "h3", "p", "li", "article", "section"]):
        text = _clean(node.get_text(" ", strip=True))
        if text and text not in chunks:
            chunks.append(text)
    if not chunks:
        chunks = [_clean(soup.get_text(" ", strip=True))]
    return "\n".join(chunks)


def _extract_metadata(soup: BeautifulSoup) -> dict[str, str]:
    metadata = {}
    for name in ("author", "date", "article:published_time", "published_time", "description"):
        node = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": name})
        if node and node.get("content"):
            metadata[name] = _clean(node["content"])
    return metadata


def _xml_text(item: ElementTree.Element, tag: str) -> str:
    node = item.find(tag)
    return _clean(node.text if node is not None else "")


def _slugify(value: str) -> str:
    value = _clean(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "startup"


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split()).strip()
