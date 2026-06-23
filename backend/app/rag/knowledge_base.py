import json
from pathlib import Path
from typing import Any, Dict, List


KNOWLEDGE_BASE_PATH = Path(__file__).resolve().parent / "knowledge_base.json"


def load_knowledge_base(path: Path = KNOWLEDGE_BASE_PATH) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sources_for_ids(source_ids: List[str], sources: Dict[str, Any]) -> List[Dict[str, str]]:
    return [
        {
            "source_id": source_id,
            "title": sources[source_id]["title"],
            "url": sources[source_id]["url"],
            "source_type": sources[source_id]["source_type"],
        }
        for source_id in source_ids
    ]


def _format_list(title: str, values: List[str]) -> str:
    if not values:
        return f"{title}: none"

    lines = [f"{title}:"]
    lines.extend(f"- {value}" for value in values)
    return "\n".join(lines)


def build_technology_documents(path: Path = KNOWLEDGE_BASE_PATH) -> List[Dict[str, Any]]:
    knowledge_base = load_knowledge_base(path)
    sources = knowledge_base["sources"]
    documents = []

    for technology in knowledge_base["technologies"]:
        linked_sources = _sources_for_ids(technology["source_ids"], sources)
        content = "\n\n".join(
            [
                f"Technology: {technology['name']}",
                f"Category: {technology['category']}",
                f"What it is: {technology['what_it_is']}",
                _format_list("Recommend when", technology["recommend_when"]),
                _format_list("Do not overclaim", technology["do_not_overclaim"]),
                _format_list("Startup signals", technology["startup_signals"]),
                _format_list("Maturity fit", technology["maturity_fit"]),
                "Sources:",
                *[
                    f"- {source['title']}: {source['url']}"
                    for source in linked_sources
                ],
            ]
        )
        documents.append(
            {
                "page_content": content,
                "metadata": {
                    "document_name": technology["id"],
                    "knowledge_type": "nvidia_technology",
                    "technology_id": technology["id"],
                    "technology_name": technology["name"],
                    "category": technology["category"],
                    "source_ids": technology["source_ids"],
                    "sources": linked_sources,
                    "curation": "structured_manual_review",
                },
            }
        )

    for framework in knowledge_base["frameworks"]:
        linked_sources = _sources_for_ids(framework["source_ids"], sources)
        content = "\n\n".join(
            [
                f"Framework: {framework['name']}",
                f"Summary: {framework['summary']}",
                _format_list("Startup signals", framework["startup_signals"]),
                "Sources:",
                *[
                    f"- {source['title']}: {source['url']}"
                    for source in linked_sources
                ],
            ]
        )
        documents.append(
            {
                "page_content": content,
                "metadata": {
                    "document_name": framework["id"],
                    "knowledge_type": "case_framework",
                    "framework_id": framework["id"],
                    "source_ids": framework["source_ids"],
                    "sources": linked_sources,
                    "curation": "structured_manual_review",
                },
            }
        )

    return documents


def validate_knowledge_base(path: Path = KNOWLEDGE_BASE_PATH) -> List[str]:
    knowledge_base = load_knowledge_base(path)
    source_ids = set(knowledge_base["sources"].keys())
    errors = []

    for technology in knowledge_base["technologies"]:
        if not technology.get("source_ids"):
            errors.append(f"{technology['id']}: missing source_ids")
        for source_id in technology.get("source_ids", []):
            if source_id not in source_ids:
                errors.append(f"{technology['id']}: unknown source_id {source_id}")
        if not technology.get("recommend_when"):
            errors.append(f"{technology['id']}: missing recommend_when")
        if not technology.get("do_not_overclaim"):
            errors.append(f"{technology['id']}: missing do_not_overclaim")

    for framework in knowledge_base["frameworks"]:
        for source_id in framework.get("source_ids", []):
            if source_id not in source_ids:
                errors.append(f"{framework['id']}: unknown source_id {source_id}")

    return errors
