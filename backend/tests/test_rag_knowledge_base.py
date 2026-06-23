from app.rag.ingestion import load_nvidia_documents
from app.rag.knowledge_base import (
    build_technology_documents,
    load_knowledge_base,
    validate_knowledge_base,
)


def test_knowledge_base_has_no_validation_errors():
    assert validate_knowledge_base() == []


def test_knowledge_base_covers_required_nvidia_technologies():
    knowledge_base = load_knowledge_base()
    technology_ids = {item["id"] for item in knowledge_base["technologies"]}

    assert "nvidia_nim" in technology_ids
    assert "nvidia_nemo" in technology_ids
    assert "nemo_guardrails" in technology_ids
    assert "triton_inference_server" in technology_ids
    assert "tensorrt_llm" in technology_ids
    assert "rapids_cudf_cuml" in technology_ids
    assert "nvidia_inception" in technology_ids
    assert "nvidia_ai_enterprise" in technology_ids


def test_technology_documents_include_citations_and_guardrails():
    documents = build_technology_documents()
    nim_document = next(
        document
        for document in documents
        if document["metadata"].get("technology_id") == "nvidia_nim"
    )

    assert "Recommend when" in nim_document["page_content"]
    assert "Do not overclaim" in nim_document["page_content"]
    assert nim_document["metadata"]["sources"]
    assert nim_document["metadata"]["curation"] == "structured_manual_review"


def test_load_nvidia_documents_prefers_structured_knowledge_base():
    documents = load_nvidia_documents()

    assert documents
    assert all(
        document.metadata.get("curation") == "structured_manual_review"
        for document in documents
    )
    assert any(
        document.metadata.get("technology_id") == "nvidia_ai_enterprise"
        for document in documents
    )
