import json

import requests

from app.agents.scraper_agent import executar_scraper_agent, salvar_resultado_scraper


class FakeResponse:
    def __init__(
        self,
        text="",
        status_code=200,
        url="https://example.com",
        json_payload=None,
        content=None,
    ):
        self.text = text
        self.status_code = status_code
        self.url = url
        self._json_payload = json_payload
        self.content = content if content is not None else text.encode("utf-8")

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._json_payload


class FakeSession:
    def __init__(self):
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append(("GET", url, kwargs))
        if "api.search.brave.com" in url:
            return FakeResponse(
                url=url,
                json_payload={
                    "web": {
                        "results": [
                            {
                                "title": "Caso IA",
                                "url": "https://example.com/ia",
                                "description": "Startup usa machine learning e NVIDIA para modelos.",
                            },
                            {
                                "title": "Sobre",
                                "url": "https://example.com/sobre",
                                "description": "Página institucional.",
                            },
                        ]
                    }
                },
            )
        if url == "https://static.example.com/artigo":
            return FakeResponse(
                text="""
                <html>
                  <head><title>Artigo Técnico</title></head>
                  <body><article><h1>Artigo Técnico</h1><p>Texto sobre machine learning em produção.</p></article></body>
                </html>
                """,
                url=url,
            )
        if url == "https://feed.example.com/rss":
            return FakeResponse(
                text="""
                <rss><channel>
                  <item>
                    <title>Clara Pagamentos usa IA</title>
                    <link>https://news.example.com/clara</link>
                    <description>Notícia sobre machine learning.</description>
                    <pubDate>Tue, 23 Jun 2026 10:00:00 GMT</pubDate>
                  </item>
                  <item>
                    <title>Outra empresa</title>
                    <link>https://news.example.com/outra</link>
                    <description>Sem relação.</description>
                  </item>
                </channel></rss>
                """,
                url=url,
            )
        return FakeResponse(status_code=404, url=url)

    def post(self, url, **kwargs):
        self.calls.append(("POST", url, kwargs))
        if "api.firecrawl.dev" in url:
            target_url = kwargs["json"]["url"]
            return FakeResponse(
                url=url,
                json_payload={
                    "success": True,
                    "data": {
                        "markdown": "# Caso IA\n\nUsamos machine learning e NVIDIA.",
                        "metadata": {
                            "title": "Caso IA",
                            "sourceURL": target_url,
                        },
                    },
                },
            )
        return FakeResponse(status_code=404, url=url)


def test_scraper_agent_uses_brave_and_firecrawl_for_web_search(monkeypatch):
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "brave-test")
    monkeypatch.setenv("FIRECRAWL_API_KEY", "firecrawl-test")
    session = FakeSession()
    plano = {
        "startup": "Clara Pagamentos",
        "tarefas": [
            {
                "id": "task_1",
                "tipo": "busca_web",
                "consulta": '"Clara Pagamentos" "machine learning"',
                "max_resultados": 2,
                "camada": 1,
                "objetivo": "Detectar menções diretas a ML",
            }
        ],
    }

    resultado = executar_scraper_agent(plano, session=session, delay_seconds=0)

    assert resultado["status"] == "completo"
    assert resultado["metricas"]["tarefas_executadas"] == 1
    assert resultado["metricas"]["total_resultados_busca"] == 2
    assert resultado["metricas"]["total_paginas_coletadas"] == 1
    assert resultado["resultados_buscas"][0]["potencial_alto"] is True
    assert resultado["paginas_completas"][0]["conteudo_markdown"].startswith("# Caso IA")
    assert any(call[0] == "GET" and "api.search.brave.com" in call[1] for call in session.calls)
    assert any(call[0] == "POST" and "api.firecrawl.dev" in call[1] for call in session.calls)


def test_scraper_agent_converts_search_planner_plan_to_brave_tasks(monkeypatch):
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "brave-test")
    monkeypatch.setenv("FIRECRAWL_API_KEY", "firecrawl-test")
    plano = {
        "startup": "Clara Pagamentos",
        "plano_consultas": [
            {
                "consulta": '"Clara Pagamentos" "NVIDIA"',
                "objetivo": "Buscar stack NVIDIA",
                "camada": 3,
            }
        ],
    }

    resultado = executar_scraper_agent(plano, session=FakeSession(), delay_seconds=0)

    assert resultado["resultados"][0]["task_id"] == "task_1"
    assert resultado["resultados"][0]["tipo"] == "busca_web"
    assert resultado["resultados"][0]["camada"] == 3


def test_scraper_agent_uses_firecrawl_for_direct_access(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "firecrawl-test")
    plano = {
        "startup": "Clara Pagamentos",
        "tarefas": [
            {
                "id": "task_site",
                "tipo": "acesso_direto",
                "url": "https://example.com/ia",
                "extrator": "firecrawl",
                "camada": 6,
                "objetivo": "Coletar site com Firecrawl.",
            }
        ],
    }

    resultado = executar_scraper_agent(plano, session=FakeSession(), delay_seconds=0)

    assert resultado["status"] == "completo"
    assert resultado["paginas_completas"][0]["extrator"] == "firecrawl"
    assert resultado["paginas_completas"][0]["titulo_pagina"] == "Caso IA"


def test_scraper_agent_uses_trafilatura_for_direct_access():
    plano = {
        "startup": "Clara Pagamentos",
        "tarefas": [
            {
                "id": "task_static",
                "tipo": "acesso_direto",
                "url": "https://static.example.com/artigo",
                "extrator": "trafilatura",
                "camada": 6,
                "objetivo": "Coletar artigo estático.",
            }
        ],
    }

    resultado = executar_scraper_agent(plano, session=FakeSession(), delay_seconds=0)

    assert resultado["status"] == "completo"
    assert resultado["paginas_completas"][0]["extrator"] == "trafilatura"
    assert "machine learning" in resultado["paginas_completas"][0]["conteudo_textual"]


def test_scraper_agent_executes_feed_rss():
    plano = {
        "startup": "Clara Pagamentos",
        "tarefas": [
            {
                "id": "task_feed",
                "tipo": "feed_rss",
                "url": "https://feed.example.com/rss",
                "filtro_titulo": "Clara Pagamentos",
            }
        ],
    }

    resultado = executar_scraper_agent(plano, session=FakeSession(), delay_seconds=0)

    assert resultado["status"] == "completo"
    assert len(resultado["resultados"][0]["itens_filtrados"]) == 1
    assert resultado["resultados"][0]["itens_filtrados"][0]["titulo"] == "Clara Pagamentos usa IA"


def test_scraper_agent_registers_missing_api_key_error(monkeypatch):
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)
    plano = {
        "startup": "Clara Pagamentos",
        "tarefas": [
            {
                "id": "task_1",
                "tipo": "busca_web",
                "consulta": '"Clara Pagamentos" "machine learning"',
            }
        ],
    }

    resultado = executar_scraper_agent(plano, session=FakeSession(), delay_seconds=0)

    assert resultado["status"] == "parcial"
    assert resultado["metricas"]["tarefas_com_erro"] == 1
    assert "BRAVE_SEARCH_API_KEY" in resultado["erros"][0]["erro"]


def test_salvar_resultado_scraper_writes_json(tmp_path):
    resultado = {
        "startup": "Clara Pagamentos",
        "timestamp_coleta": "2026-06-23T14:30:00Z",
        "status": "completo",
        "metricas": {},
        "resultados": [],
        "resultados_buscas": [],
        "paginas_completas": [],
        "varredura_complementar": [],
        "erros": [],
    }

    path = salvar_resultado_scraper(resultado, tmp_path)
    saved = json.loads(path.read_text(encoding="utf-8"))

    assert path.name.startswith("evidencias_clara-pagamentos_")
    assert saved["startup"] == "Clara Pagamentos"
