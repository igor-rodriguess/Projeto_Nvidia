from langchain_core.documents import Document

from app.rag.retriever import retrieve_nvidia_context


class FakeVectorStore:
    def similarity_search(self, query: str, k: int):
        return [
            Document(
                page_content=f"Resultado para {query}",
                metadata={"document_name": "nvidia_nim", "rank": 1},
            )
        ][:k]


def test_retrieve_nvidia_context_returns_serializable_results():
    results = retrieve_nvidia_context(
        "startup com LLM em produção",
        vector_store=FakeVectorStore(),
    )

    assert results == [
        {
            "content": "Resultado para startup com LLM em produção",
            "metadata": {"document_name": "nvidia_nim", "rank": 1},
        }
    ]


def test_retrieve_nvidia_context_ignores_empty_query():
    results = retrieve_nvidia_context(" ", vector_store=FakeVectorStore())

    assert results == []
