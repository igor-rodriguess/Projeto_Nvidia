from app.rag.source_catalog import list_rag_sources, load_source_catalog


def test_source_catalog_loads_case_materials_and_nvidia_docs():
    catalog = load_source_catalog()

    assert "case_materials" in catalog
    assert "nvidia_official_docs" in catalog
    assert len(catalog["case_materials"]) == 6
    assert len(catalog["nvidia_official_docs"]) == 18


def test_source_catalog_contains_required_urls():
    urls = {source["url"] for source in list_rag_sources()}

    assert "https://sequoiacap.com/article/services-the-new-software/" in urls
    assert "https://www.emcap.com/thoughts/the-ai-native-services-playbook" in urls
    assert "https://blogs.nvidia.com/blog/ai-5-layer-cake/" in urls
    assert "https://www.nvidia.com/en-us/startups/" in urls
    assert "https://build.nvidia.com/" in urls
    assert "https://developer.nvidia.com/dynamo-triton" in urls
    assert "https://github.com/NVIDIA-NeMo/Guardrails" in urls
    assert "https://developer.nvidia.com/morpheus-cybersecurity" in urls


def test_list_rag_sources_adds_category_to_each_source():
    sources = list_rag_sources()

    assert sources
    assert all("category" in source for source in sources)
    assert {source["category"] for source in sources} == {
        "case_materials",
        "nvidia_official_docs",
    }
