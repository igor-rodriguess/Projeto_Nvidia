__all__ = [
    "build_technology_documents",
    "get_qdrant_client",
    "get_vector_store",
    "ingest_nvidia_documents",
    "list_rag_sources",
    "load_knowledge_base",
    "load_nvidia_documents",
    "load_source_catalog",
    "retrieve_nvidia_context",
    "validate_knowledge_base",
]


def __getattr__(name):
    if name in {"ingest_nvidia_documents", "load_nvidia_documents"}:
        from app.rag.ingestion import ingest_nvidia_documents, load_nvidia_documents

        return {
            "ingest_nvidia_documents": ingest_nvidia_documents,
            "load_nvidia_documents": load_nvidia_documents,
        }[name]

    if name in {
        "build_technology_documents",
        "load_knowledge_base",
        "validate_knowledge_base",
    }:
        from app.rag.knowledge_base import (
            build_technology_documents,
            load_knowledge_base,
            validate_knowledge_base,
        )

        return {
            "build_technology_documents": build_technology_documents,
            "load_knowledge_base": load_knowledge_base,
            "validate_knowledge_base": validate_knowledge_base,
        }[name]

    if name == "retrieve_nvidia_context":
        from app.rag.retriever import retrieve_nvidia_context

        return retrieve_nvidia_context

    if name in {"list_rag_sources", "load_source_catalog"}:
        from app.rag.source_catalog import list_rag_sources, load_source_catalog

        return {
            "list_rag_sources": list_rag_sources,
            "load_source_catalog": load_source_catalog,
        }[name]

    if name in {"get_qdrant_client", "get_vector_store"}:
        from app.rag.vector_store import get_qdrant_client, get_vector_store

        return {
            "get_qdrant_client": get_qdrant_client,
            "get_vector_store": get_vector_store,
        }[name]

    raise AttributeError(f"module 'app.rag' has no attribute {name!r}")
