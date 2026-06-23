from pathlib import Path

from app.rag.ingestion import load_nvidia_documents, split_documents


def test_load_nvidia_documents_reads_markdown_files():
    documents = load_nvidia_documents()

    names = {document.metadata["document_name"] for document in documents}
    assert "nvidia_nim" in names
    assert "nvidia_nemo" in names
    assert "nvidia_inception" in names
    assert "nvidia_api_catalog" in names
    assert "nvidia_ai_enterprise" in names
    assert "nvidia_ai_infrastructure" in names
    assert "nvidia_domain_platforms" in names
    assert "case_ai_services" in names
    assert "cuda_toolkit" in names
    assert "rapids_accelerators" in names
    assert "nemo_guardrails" in names
    assert "triton_inference_server" in names
    assert "tensorrt_llm" in names
    assert "rapids" in names


def test_load_nvidia_documents_adds_traceable_metadata(tmp_path: Path):
    document_path = tmp_path / "sample.md"
    document_path.write_text("# Sample\n\nConteudo NVIDIA.", encoding="utf-8")

    documents = load_nvidia_documents(tmp_path)

    assert len(documents) == 1
    assert documents[0].metadata["source"] == str(document_path)
    assert documents[0].metadata["vendor"] == "NVIDIA"


def test_split_documents_returns_chunks_with_metadata():
    documents = load_nvidia_documents()

    chunks = split_documents(documents)

    assert chunks
    assert all(chunk.page_content for chunk in chunks)
    assert all("document_name" in chunk.metadata for chunk in chunks)
