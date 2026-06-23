from pathlib import Path

from app.rag.url_ingestion import fetch_and_write_sources


class FakeResponse:
    status_code = 200
    url = "https://example.com/final"
    text = """
    <html>
      <head><title>NVIDIA Example</title></head>
      <body>
        <nav>Navigation</nav>
        <main>
          <h1>NVIDIA Example</h1>
          <p>This official NVIDIA page explains a platform for startups using artificial intelligence.</p>
          <ul>
            <li>It helps teams deploy models in production with reliable infrastructure.</li>
          </ul>
        </main>
      </body>
    </html>
    """

    def raise_for_status(self):
        return None


class FakeClient:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def get(self, url: str):
        return FakeResponse()


def test_fetch_and_write_sources_generates_markdown(monkeypatch, tmp_path: Path):
    import app.rag.url_ingestion as module

    monkeypatch.setattr(module.httpx, "Client", FakeClient)
    sources = [
        {
            "name": "NVIDIA Example",
            "url": "https://example.com",
            "category": "nvidia_official_docs",
            "source_type": "nvidia_official",
            "format": "documentation",
            "priority": "high",
        }
    ]

    results = fetch_and_write_sources(sources=sources, output_dir=tmp_path)

    assert results[0]["status"] == "written"
    output_path = Path(results[0]["output_path"])
    content = output_path.read_text(encoding="utf-8")
    assert "URL: https://example.com" in content
    assert "This official NVIDIA page explains" in content
    assert "Navigation" not in content


def test_fetch_and_write_sources_skips_youtube_without_transcript(tmp_path: Path):
    sources = [
        {
            "name": "Video",
            "url": "https://www.youtube.com/watch?v=abc",
            "category": "case_materials",
            "source_type": "case_material",
            "format": "youtube_video",
            "priority": "medium",
        }
    ]

    results = fetch_and_write_sources(sources=sources, output_dir=tmp_path)

    assert results[0]["status"] == "skipped"
    assert list(tmp_path.glob("*.md")) == []
