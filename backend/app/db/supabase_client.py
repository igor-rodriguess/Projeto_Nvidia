import os
from dataclasses import dataclass
from typing import Any, Dict, List

import httpx


@dataclass(frozen=True)
class SupabaseConfig:
    url: str
    service_role_key: str

    @classmethod
    def from_env(cls) -> "SupabaseConfig | None":
        url = os.getenv("SUPABASE_URL", "").rstrip("/")
        service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

        if not url or not service_role_key:
            return None

        return cls(url=url, service_role_key=service_role_key)


class SupabaseRestClient:
    def __init__(self, config: SupabaseConfig):
        self.config = config
        self.base_url = f"{config.url}/rest/v1"
        self.headers = {
            "apikey": config.service_role_key,
            "Authorization": f"Bearer {config.service_role_key}",
            "Content-Type": "application/json",
        }

    def insert(self, table: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self._request(
            "POST",
            table,
            json=payload,
            headers={"Prefer": "return=representation"},
        )
        return response[0] if response else {}

    def bulk_insert(self, table: str, payload: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not payload:
            return []

        return self._request(
            "POST",
            table,
            json=payload,
            headers={"Prefer": "return=representation"},
        )

    def upsert(
        self,
        table: str,
        payload: Dict[str, Any],
        on_conflict: str,
    ) -> Dict[str, Any]:
        response = self._request(
            "POST",
            table,
            params={"on_conflict": on_conflict},
            json=payload,
            headers={"Prefer": "resolution=merge-duplicates,return=representation"},
        )
        return response[0] if response else {}

    def _request(
        self,
        method: str,
        table: str,
        json: Any,
        headers: Dict[str, str] | None = None,
        params: Dict[str, str] | None = None,
    ) -> Any:
        merged_headers = {**self.headers, **(headers or {})}
        url = f"{self.base_url}/{table}"

        with httpx.Client(timeout=30) as client:
            response = client.request(
                method,
                url,
                headers=merged_headers,
                params=params,
                json=json,
            )
            response.raise_for_status()

            if not response.content:
                return []

            return response.json()


def get_supabase_client() -> SupabaseRestClient | None:
    config = SupabaseConfig.from_env()
    if config is None:
        return None

    return SupabaseRestClient(config)
