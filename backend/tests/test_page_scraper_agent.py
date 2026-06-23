from app.scraping import page_scraper as scraper_module
from app.scraping.page_scraper import page_scraper_agent


def test_page_scraper_agent_extracts_clean_page_content(monkeypatch):
    html = """
    <html>
      <head>
        <title>DiagIA - Healthtech</title>
        <meta name="description" content="Healthtech fundada em 2021 com sede em São Paulo, SP.">
      </head>
      <body>
        <nav>Menu inútil</nav>
        <main>
          <h1>DiagIA</h1>
          <p>A DiagIA usa inteligência artificial e machine learning para apoiar diagnósticos médicos.</p>
          <p>A startup brasileira tem sede em São Paulo, SP e atende hospitais.</p>
        </main>
      </body>
    </html>
    """
    monkeypatch.setattr(
        scraper_module,
        "_fetch_page",
        lambda url: {
            "html": html,
            "http_status": 200,
            "final_url": url,
            "content_type": "text/html; charset=utf-8",
        },
    )
    state = {
        "sources": [
            {
                "title": "DiagIA - Healthtech",
                "url": "https://diagia.example.com",
                "snippet": "Startup usa IA em saúde.",
                "source_type": "public_search",
            }
        ],
        "errors": [],
    }

    result = page_scraper_agent(state)

    source = result["sources"][0]
    assert source["scrape_status"] == "success"
    assert source["page_title"] == "DiagIA - Healthtech"
    assert source["page_description"] == "Healthtech fundada em 2021 com sede em São Paulo, SP."
    assert "inteligência artificial" in source["page_text"]
    assert "Menu inútil" not in source["page_text"]
    assert source["http_status"] == 200
    assert source["final_url"] == "https://diagia.example.com"
    assert source["content_hash"]
    assert source["text_char_count"] > 0
    assert source["extraction_quality"] in {"low", "medium", "high"}
    assert result["scrape_stats"]["scraped"] == 1


def test_page_scraper_agent_skips_unsupported_domains():
    state = {
        "sources": [
            {
                "title": "Vídeo",
                "url": "https://www.youtube.com/watch?v=abc",
                "snippet": "Vídeo sobre startup.",
            }
        ],
        "errors": [],
    }

    result = page_scraper_agent(state)

    assert result["sources"][0]["scrape_status"] == "skipped"
    assert result["sources"][0]["scrape_error"] == "unsupported_domain"
    assert result["scrape_stats"]["skipped"] == 1


def test_page_scraper_agent_preserves_source_when_fetch_fails(monkeypatch):
    def fail(url):
        raise RuntimeError("timeout")

    monkeypatch.setattr(scraper_module, "_fetch_page", fail)
    state = {
        "sources": [
            {
                "title": "Fonte",
                "url": "https://example.com/fonte",
                "snippet": "Snippet.",
            }
        ],
        "errors": [],
    }

    result = page_scraper_agent(state)

    assert result["sources"][0]["title"] == "Fonte"
    assert result["sources"][0]["scrape_status"] == "failed"
    assert "timeout" in result["sources"][0]["scrape_error"]
