import os
from functools import lru_cache
from typing import Any


DEFAULT_QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
DEFAULT_COLLECTION_NAME = os.getenv(
    "NVIDIA_RAG_COLLECTION", "nvidia_startup_ai_radar"
)
DEFAULT_EMBEDDING_MODEL = os.getenv(
    "NVIDIA_RAG_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"
)


def get_qdrant_client(url: str = DEFAULT_QDRANT_URL):
    from qdrant_client import QdrantClient

    return QdrantClient(url=url)


@lru_cache(maxsize=1)
def get_embeddings(model_name: str = DEFAULT_EMBEDDING_MODEL):
    from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

    return FastEmbedEmbeddings(model_name=model_name)


def get_vector_store(
    collection_name: str = DEFAULT_COLLECTION_NAME,
    qdrant_url: str = DEFAULT_QDRANT_URL,
    embeddings: Any | None = None,
):
    from langchain_qdrant import QdrantVectorStore

    return QdrantVectorStore.from_existing_collection(
        collection_name=collection_name,
        embedding=embeddings or get_embeddings(),
        url=qdrant_url,
    )
