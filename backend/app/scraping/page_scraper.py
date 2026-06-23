import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.core.startup_analysis_state import StartupAnalysisState


MAX_SOURCES_TO_SCRAPE = 10
MAX_PAGE_TEXT_CHARS = 12000
REQUEST_TIMEOUT_SECONDS = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 Chrome/120 Safari/537.36"
)
SKIPPED_DOMAINS = {
    "youtube.com",
    "youtu.be",
    "instagram.com",
    "facebook.com",
    "x.com",
    "twitter.com",
    "linkedin.com",
}
SKIPPED_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower().replace("www.", "")


def _should_skip_url(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return "invalid_url"

    domain = _domain(url)
    if any(
        domain == skipped or domain.endswith(f".{skipped}")
        for skipped in SKIPPED_DOMAINS
    ):
        return "unsupported_domain"

    if parsed.path.lower().endswith(SKIPPED_EXTENSIONS):
        return "unsupported_file_type"

    return None


def _fetch_page_html(url: str) -> str:
    response = httpx.get(
        url,
        follow_redirects=True,
        timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type and "application/xhtml" not in content_type:
        raise ValueError(f"unsupported content type: {content_type}")

    return response.text


def _fetch_page(url: str) -> Dict[str, Any]:
    response = httpx.get(
        url,
        follow_redirects=True,
        timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type and "application/xhtml" not in content_type:
        raise ValueError(f"unsupported content type: {content_type}")

    return {
        "html": response.text,
        "http_status": response.status_code,
        "final_url": str(response.url),
        "content_type": content_type,
    }


def _clean_text(value: str) -> str:
    return " ".join(value.split()).strip()


def _remove_noise(soup: BeautifulSoup) -> None:
    for tag in soup(["script", "style", "noscript", "svg", "iframe", "form"]):
        tag.decompose()

    for selector in ("nav", "footer", "header", "aside", "[role='navigation']"):
        for tag in soup.select(selector):
            tag.decompose()


def _meta_content(soup: BeautifulSoup, **attrs) -> str | None:
    tag = soup.find("meta", attrs=attrs)
    content = tag.get("content", "") if tag else ""
    return _clean_text(content) or None


def _link_href(soup: BeautifulSoup, rel: str) -> str | None:
    tag = soup.find("link", rel=rel)
    href = tag.get("href", "") if tag else ""
    return _clean_text(href) or None


def _extract_title(soup: BeautifulSoup) -> str | None:
    if soup.title and soup.title.string:
        return _clean_text(soup.title.string)

    heading = soup.find("h1")
    if heading:
        return _clean_text(heading.get_text(" "))

    return None


def _extract_page_text(soup: BeautifulSoup) -> str:
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
        if len(text) < 35 and tag.name not in {"h1", "h2", "h3"}:
            continue
        pieces.append(text)

    if not pieces:
        for line in soup.get_text("\n").splitlines():
            text = _clean_text(line)
            if len(text) >= 50:
                pieces.append(text)

    deduped = list(dict.fromkeys(pieces))
    return "\n\n".join(deduped)[:MAX_PAGE_TEXT_CHARS]


def _extract_schema_types(soup: BeautifulSoup) -> List[str]:
    schema_types = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            payload = json.loads(script.string or "{}")
        except json.JSONDecodeError:
            continue

        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if not isinstance(item, dict):
                continue
            schema_type = item.get("@type")
            if isinstance(schema_type, list):
                schema_types.extend(str(value) for value in schema_type)
            elif schema_type:
                schema_types.append(str(schema_type))

    return sorted(set(schema_types))


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _extraction_quality(page_text: str, description: str | None) -> str:
    if len(page_text) >= 1200 and description:
        return "high"
    if len(page_text) >= 400:
        return "medium"
    if page_text:
        return "low"
    return "empty"


def _parse_page(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    description = (
        _meta_content(soup, name="description")
        or _meta_content(soup, property="og:description")
        or _meta_content(soup, name="twitter:description")
    )
    page_text = _extract_page_text(soup)

    return {
        "page_title": _extract_title(soup),
        "page_description": description,
        "page_text": page_text,
        "canonical_url": _link_href(soup, "canonical"),
        "published_at": _meta_content(soup, property="article:published_time"),
        "modified_at": _meta_content(soup, property="article:modified_time"),
        "language": (soup.html.get("lang") if soup.html else None),
        "schema_types": _extract_schema_types(soup),
        "content_hash": _content_hash(page_text) if page_text else None,
        "text_char_count": len(page_text),
        "extraction_quality": _extraction_quality(page_text, description),
    }


def _scrape_source(source: Dict[str, Any]) -> Dict[str, Any]:
    url = source.get("url", "")
    skip_reason = _should_skip_url(url)
    if skip_reason:
        return {
            **source,
            "scrape_status": "skipped",
            "scrape_error": skip_reason,
            "scraped_at": _now(),
        }

    try:
        fetched = _fetch_page(url)
        parsed = _parse_page(fetched["html"])
        page_text = parsed.get("page_text", "")
        return {
            **source,
            **parsed,
            "http_status": fetched["http_status"],
            "final_url": fetched["final_url"],
            "content_type": fetched["content_type"],
            "page_text_excerpt": page_text[:600],
            "source_domain": _domain(url),
            "scrape_status": "success" if page_text else "empty",
            "scrape_error": None,
            "scraped_at": _now(),
        }
    except Exception as exc:
        return {
            **source,
            "source_domain": _domain(url),
            "scrape_status": "failed",
            "scrape_error": str(exc)[:500],
            "scraped_at": _now(),
        }


def page_scraper_agent(state: StartupAnalysisState) -> StartupAnalysisState:
    sources = state.get("sources", [])

    if not sources:
        state.setdefault("errors", []).append("page_scraper_agent: no sources found")
        return state

    enriched_sources = []
    scraped_count = 0
    failed_count = 0
    skipped_count = 0

    for index, source in enumerate(sources):
        if index >= MAX_SOURCES_TO_SCRAPE:
            enriched_sources.append(
                {
                    **source,
                    "scrape_status": "skipped",
                    "scrape_error": "max_sources_to_scrape_reached",
                    "scraped_at": _now(),
                }
            )
            skipped_count += 1
            continue

        enriched = _scrape_source(source)
        enriched_sources.append(enriched)
        if enriched.get("scrape_status") in {"success", "empty"}:
            scraped_count += 1
        elif enriched.get("scrape_status") == "failed":
            failed_count += 1
        else:
            skipped_count += 1

    state["sources"] = enriched_sources
    state["scrape_stats"] = {
        "total_sources": len(sources),
        "scraped": scraped_count,
        "failed": failed_count,
        "skipped": skipped_count,
        "max_sources_to_scrape": MAX_SOURCES_TO_SCRAPE,
    }
    return state
