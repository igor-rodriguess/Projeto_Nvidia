import json
from pathlib import Path
from typing import Any, Dict, List


SOURCE_CATALOG_PATH = Path(__file__).resolve().parent / "source_catalog.json"


def load_source_catalog(catalog_path: Path = SOURCE_CATALOG_PATH) -> Dict[str, Any]:
    return json.loads(catalog_path.read_text(encoding="utf-8"))


def list_rag_sources(catalog_path: Path = SOURCE_CATALOG_PATH) -> List[Dict[str, Any]]:
    catalog = load_source_catalog(catalog_path)
    sources = []
    for category, entries in catalog.items():
        for entry in entries:
            sources.append({**entry, "category": category})
    return sources
