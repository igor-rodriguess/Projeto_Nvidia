from typing import Any, Dict, List

from app.rag.vector_store import DEFAULT_COLLECTION_NAME, DEFAULT_QDRANT_URL


def retrieve_nvidia_context(
    query: str,
    k: int = 4,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    qdrant_url: str = DEFAULT_QDRANT_URL,
    vector_store: Any | None = None,
) -> List[Dict[str, Any]]:
    if not query.strip():
        return []

    if vector_store is None:
        from app.rag.vector_store import get_vector_store

        vector_store = get_vector_store(
            collection_name=collection_name,
            qdrant_url=qdrant_url,
        )

    documents = vector_store.similarity_search(query, k=k)
    return [
        {
            "content": document.page_content,
            "metadata": document.metadata,
        }
        for document in documents
    ]
