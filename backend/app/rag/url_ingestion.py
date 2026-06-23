import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.rag.source_catalog import list_rag_sources


GENERATED_DOCUMENTS_DIR = Path(__file__).resolve().parent / "documents" / "generated"
MAX_CONTENT_CHARS = 18000
REQUEST_TIMEOUT_SECONDS = 30
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 Chrome/120 Safari/537.36"
)
SKIPPED_FORMATS = {"youtube_video", "youtube_playlist"}


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")
    return normalized or "source"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _extract_title(soup: BeautifulSoup, fallback: str) -> str:
    if soup.title and soup.title.string:
        return _clean_text(soup.title.string)

    heading = soup.find("h1")
    if heading:
        return _clean_text(heading.get_text(" "))

    return fallback


def _remove_noise(soup: BeautifulSoup) -> None:
    for tag in soup(["script", "style", "noscript", "svg", "form", "iframe"]):
        tag.decompose()

    for selector in ("nav", "footer", "header", "[role='navigation']"):
        for tag in soup.select(selector):
            tag.decompose()


def _extract_main_text(soup: BeautifulSoup) -> str:
    _remove_noise(soup)
    container = (
        soup.find("main")
        or soup.find("article")
        or soup.find(attrs={"role": "main"})
        or soup.body
        or soup
    )
    pieces = []

    for tag in container.find_all(["h1", "h2", "h3", "p", "li"], recursive=True):
        text = _clean_text(tag.get_text(" "))
        if len(text) < 30 and tag.name not in {"h1", "h2", "h3"}:
            continue
        pieces.append(text)

    deduped = list(dict.fromkeys(pieces))
    extracted = "\n\n".join(deduped).strip()
    if extracted:
        return extracted[:MAX_CONTENT_CHARS]

    fallback_pieces = _extract_metadata_text(soup) + _extract_visible_text(soup)
    fallback_deduped = list(dict.fromkeys(fallback_pieces))
    return "\n\n".join(fallback_deduped)[:MAX_CONTENT_CHARS].strip()


def _extract_metadata_text(soup: BeautifulSoup) -> List[str]:
    pieces = []
    for attrs in (
        {"name": "description"},
        {"property": "og:title"},
        {"property": "og:description"},
        {"name": "twitter:title"},
        {"name": "twitter:description"},
    ):
        tag = soup.find("meta", attrs=attrs)
        content = tag.get("content", "") if tag else ""
        text = _clean_text(content)
        if text:
            pieces.append(text)

    return pieces


def _extract_visible_text(soup: BeautifulSoup) -> List[str]:
    raw_text = soup.get_text("\n")
    pieces = []
    for line in raw_text.splitlines():
        text = _clean_text(line)
        if len(text) >= 40:
            pieces.append(text)

    return pieces


def _render_markdown(source: Dict[str, Any], title: str, content: str) -> str:
    fetched_at = datetime.now(timezone.utc).isoformat()
    return "\n".join(
        [
            f"# {source['name']}",
            "",
            f"Titulo extraido: {title}",
            f"URL: {source['url']}",
            f"Categoria: {source['category']}",
            f"Tipo: {source['source_type']}",
            f"Formato: {source['format']}",
            f"Prioridade: {source['priority']}",
            f"Coletado em: {fetched_at}",
            "",
            "## Conteudo extraido",
            "",
            content or "Nenhum conteudo textual relevante foi extraido automaticamente.",
            "",
        ]
    )


def _is_fetchable(source: Dict[str, Any]) -> bool:
    url = source.get("url", "")
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and source.get("format") not in SKIPPED_FORMATS


def fetch_source_content(source: Dict[str, Any], client: httpx.Client) -> Dict[str, Any]:
    response = client.get(source["url"])
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    title = _extract_title(soup, source["name"])
    content = _extract_main_text(soup)

    return {
        "source": source,
        "title": title,
        "content": content,
        "status_code": response.status_code,
        "final_url": str(response.url),
    }


def write_extracted_source(result: Dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    source = result["source"]
    filename = f"{_slugify(source['category'])}_{_slugify(source['name'])}.md"
    output_path = output_dir / filename
    markdown = _render_markdown(source, result["title"], result["content"])
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def fetch_and_write_sources(
    sources: Iterable[Dict[str, Any]] | None = None,
    output_dir: Path = GENERATED_DOCUMENTS_DIR,
) -> List[Dict[str, Any]]:
    selected_sources = list(sources or list_rag_sources())
    results = []

    with httpx.Client(
        follow_redirects=True,
        timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        for source in selected_sources:
            if not _is_fetchable(source):
                results.append(
                    {
                        "name": source["name"],
                        "url": source["url"],
                        "status": "skipped",
                        "reason": f"format {source.get('format')} requires transcript handling",
                    }
                )
                continue

            try:
                extracted = fetch_source_content(source, client)
                output_path = write_extracted_source(extracted, output_dir)
                results.append(
                    {
                        "name": source["name"],
                        "url": source["url"],
                        "status": "written",
                        "output_path": str(output_path),
                        "content_chars": len(extracted["content"]),
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "name": source["name"],
                        "url": source["url"],
                        "status": "error",
                        "reason": str(exc),
                    }
                )

    return results


if __name__ == "__main__":
    for result in fetch_and_write_sources():
        print(result)
