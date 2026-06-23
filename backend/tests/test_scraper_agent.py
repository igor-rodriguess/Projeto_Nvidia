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
    ):
        self.text = text
        self.status_code = status_code
        self.url = url
        self._json_payload = json_payload
        self.content = text.encode("utf-8")

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._json_payload


class FakeSession:
    def __init__(self):
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if "duckduckgo.com/html" in url:
            return FakeResponse(
                text="""
                <html><body>
                  <div class="result">
                    <a class="result__a" href="https://example.com/ia">Caso IA</a>
                    <a class="result__snippet">Startup usa machine learning e NVIDIA para modelos.</a>
                  </div>
                  <div class="result">
                    <a class="result__a" href="https://example.com/sobre">Sobre</a>
                    <a class="result__snippet">Página institucional.</a>
                  </div>
                </body></html>
                """,
                url=url,
            )
        if url == "https://example.com/ia":
            return FakeResponse(
                text="""
                <html>
                  <head><title>Caso IA</title><meta name="author" content="Equipe"></head>
                  <body><h1>IA em produção</h1><p>Usamos modelos de machine learning.</p></body>
                </html>
                """,
                url=url,
            )
        if url == "https://api.example.com/startups":
            return FakeResponse(json_payload={"data": [{"nome": "Startup API"}]}, url=url)
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


def test_scraper_agent_executes_web_search_and_collects_high_potential_pages():
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

    resultado = executar_scraper_agent(
        plano,
        session=FakeSession(),
        delay_seconds=0,
        respect_robots=False,
    )

    assert resultado["status"] == "completo"
    assert resultado["metricas"]["tarefas_executadas"] == 1
    assert resultado["metricas"]["total_resultados_busca"] == 2
    assert resultado["metricas"]["total_paginas_coletadas"] == 1
    search_result = resultado["resultados"][0]["resultados_busca"][0]
    assert search_result["alto_potencial"] is True
    assert resultado["resultados"][0]["paginas_completas"][0]["titulo_pagina"] == "Caso IA"


def test_scraper_agent_converts_search_planner_plan_to_tasks():
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

    resultado = executar_scraper_agent(
        plano,
        session=FakeSession(),
        delay_seconds=0,
        respect_robots=False,
    )

    assert resultado["resultados"][0]["task_id"] == "task_1"
    assert resultado["resultados"][0]["tipo"] == "busca_web"
    assert resultado["resultados"][0]["camada"] == 3


def test_scraper_agent_executes_api_get_and_feed_rss():
    plano = {
        "startup": "Clara Pagamentos",
        "tarefas": [
            {
                "id": "task_api",
                "tipo": "api_get",
                "url": "https://api.example.com/startups",
                "campo_dados": "data",
            },
            {
                "id": "task_feed",
                "tipo": "feed_rss",
                "url": "https://feed.example.com/rss",
                "filtro_titulo": "Clara Pagamentos",
            },
        ],
    }

    resultado = executar_scraper_agent(
        plano,
        session=FakeSession(),
        delay_seconds=0,
        respect_robots=False,
    )

    assert resultado["status"] == "completo"
    assert resultado["resultados"][0]["dados_json"] == [{"nome": "Startup API"}]
    assert len(resultado["resultados"][1]["itens_filtrados"]) == 1
    assert resultado["resultados"][1]["itens_filtrados"][0]["titulo"] == "Clara Pagamentos usa IA"


def test_scraper_agent_registers_api_key_placeholder_error():
    plano = {
        "startup": "Clara Pagamentos",
        "tarefas": [
            {
                "id": "task_api",
                "tipo": "api_get",
                "url": "https://api.example.com/startups",
                "headers": {"Authorization": "Bearer {{CHAVE_API}}"},
            }
        ],
    }

    resultado = executar_scraper_agent(
        plano,
        session=FakeSession(),
        delay_seconds=0,
        respect_robots=False,
    )

    assert resultado["status"] == "parcial"
    assert resultado["metricas"]["tarefas_com_erro"] == 1
    assert "chave necessária" in resultado["erros"][0]["erro"]


def test_salvar_resultado_scraper_writes_json(tmp_path):
    resultado = {
        "startup": "Clara Pagamentos",
        "timestamp_coleta": "2026-06-23T14:30:00Z",
        "status": "completo",
        "metricas": {},
        "resultados": [],
        "varredura_complementar": [],
        "erros": [],
    }

    path = salvar_resultado_scraper(resultado, tmp_path)
    saved = json.loads(path.read_text(encoding="utf-8"))

    assert path.name.startswith("evidencias_clara-pagamentos_")
    assert saved["startup"] == "Clara Pagamentos"
