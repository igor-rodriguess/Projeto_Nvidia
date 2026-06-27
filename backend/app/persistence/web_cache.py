from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlparse

from app.persistence.persistence_service import PipelinePersistence


class SupabaseWebContentCache:
    """Seven-day cache and usage ledger for paid web extraction calls."""

    def __init__(self, persistence: PipelinePersistence, ttl_seconds: int = 604800) -> None:
        self.persistence = persistence
        self.db = persistence.db
        self.ttl_seconds = ttl_seconds

    def get(self, url: str, extractor: str = "firecrawl") -> dict[str, Any] | None:
        cache_key = _cache_key(url, extractor)
        response = (
            self.db.table("web_content_cache")
            .select("response_json,expires_at")
            .eq("cache_key", cache_key)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return None
        expires_at = datetime.fromisoformat(str(rows[0]["expires_at"]).replace("Z", "+00:00"))
        if expires_at <= datetime.now(UTC):
            return None
        return rows[0]["response_json"]

    def set(self, url: str, value: dict[str, Any], extractor: str = "firecrawl") -> None:
        self.db.table("web_content_cache").upsert(
            {
                "cache_key": _cache_key(url, extractor),
                "url": url,
                "extractor": extractor,
                "response_json": value,
                "expires_at": (datetime.now(UTC) + timedelta(seconds=self.ttl_seconds)).isoformat(),
            },
            on_conflict="cache_key",
        ).execute()

    def record_usage(
        self,
        url: str,
        cache_hit: bool,
        success: bool,
        estimated_cost_usd: float = 0.0,
    ) -> None:
        self.db.table("external_api_usage").insert(
            {
                "provider": "firecrawl",
                "operation": "scrape",
                "source_domain": urlparse(url).netloc.lower() or None,
                "units": 0 if cache_hit else 1,
                "estimated_cost_usd": 0.0 if cache_hit else estimated_cost_usd,
                "cache_hit": cache_hit,
                "success": success,
            }
        ).execute()


def _cache_key(url: str, extractor: str) -> str:
    return hashlib.sha256(f"v1:{extractor}:{url.strip()}".encode("utf-8")).hexdigest()
