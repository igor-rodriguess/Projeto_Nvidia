from pathlib import Path
from typing import Any, Iterable, List


DOCUMENTS_DIR = Path(__file__).resolve().parent / "documents"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 120


def load_nvidia_documents(
    documents_dir: Path = DOCUMENTS_DIR,
    include_knowledge_base: bool = True,
    include_manual_documents: bool = False,
) -> List[Any]:
    from langchain_core.documents import Document

    from app.rag.knowledge_base import build_technology_documents

    documents = []

    if include_knowledge_base:
        documents.extend(
            Document(
                page_content=item["page_content"],
                metadata=item["metadata"],
            )
            for item in build_technology_documents()
        )

    if not include_manual_documents:
        return documents

    for path in sorted(documents_dir.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": str(path),
                    "document_name": path.stem,
                    "vendor": "NVIDIA",
                    "curation": "manual_markdown",
                },
            )
        )

    return documents


def split_documents(documents: Iterable[Any]) -> List[Any]:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ModuleNotFoundError:
        return _split_documents_locally(documents)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(list(documents))


def _split_documents_locally(documents: Iterable[Any]) -> List[Any]:
    from langchain_core.documents import Document

    chunks = []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    for document in documents:
        text = document.page_content
        for start in range(0, len(text), step):
            content = text[start : start + CHUNK_SIZE]
            if not content.strip():
                continue

            chunks.append(
                Document(
                    page_content=content,
                    metadata={**document.metadata, "chunk_start": start},
                )
            )

    return chunks


def ingest_nvidia_documents(
    collection_name: str | None = None,
    qdrant_url: str | None = None,
    documents_dir: Path = DOCUMENTS_DIR,
    embeddings: Any | None = None,
) -> int:
    from langchain_qdrant import QdrantVectorStore

    from app.rag.vector_store import (
        DEFAULT_COLLECTION_NAME,
        DEFAULT_QDRANT_URL,
        get_embeddings,
    )

    documents = load_nvidia_documents(documents_dir)
    chunks = split_documents(documents)

    if not chunks:
        return 0

    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings or get_embeddings(),
        url=qdrant_url or DEFAULT_QDRANT_URL,
        collection_name=collection_name or DEFAULT_COLLECTION_NAME,
        force_recreate=True,
    )

    return len(chunks)


if __name__ == "__main__":
    ingested_chunks = ingest_nvidia_documents()
    print(f"Ingested {ingested_chunks} NVIDIA RAG chunks.")
