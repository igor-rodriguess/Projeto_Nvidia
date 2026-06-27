# Arquitetura Enterprise e NVIDIA RAG

## Fluxo

```text
PipelineInput
  -> Search Planner Chain
  -> Scraper Chain
  -> Evidence Validator Chain
  -> AI Maturity Classifier Chain
  -> NVIDIA Recommender RAG Chain
  -> PipelineOutput
```

Cada agente é uma `RunnableLambda` independente. Entradas e saídas são validadas
por Pydantic e novamente contra o JSON Schema gerado pelo próprio contrato.

## Confiabilidade

- Até três tentativas com backoff exponencial.
- Falhas irrecuperáveis geram `status: parcial` e permanecem no `trace`.
- Logs estruturados em JSON registram etapa, duração, tentativas, contagens e tokens.
- Cache em arquivo usa SHA-256 do payload canônico e gravação atômica.
- Chaves são lidas somente de variáveis de ambiente.
- Testes não chamam APIs pagas nem consomem créditos.

## Base NVIDIA

O catálogo em `backend/app/rag/knowledge_sources.py` contém fontes oficiais para
NIM, Triton, TensorRT-LLM, NeMo, RAPIDS, CUDA, Riva, Omniverse, Clara, Isaac,
Morpheus, AI Enterprise e Inception, além de blog técnico, resources.nvidia.com e
GitHub da NVIDIA.

O pipeline de ingestão:

1. Extrai HTML em Markdown com Firecrawl e usa Trafilatura como fallback.
2. Extrai PDFs com PyMuPDF.
3. Normaliza Unicode e remove linhas repetidas de navegação.
4. Divide o conteúdo em chunks de 800 caracteres com overlap de 100.
5. Anexa tecnologia, tipo, dores, perfis, seção e URL.
6. Gera vetores densos e vetores BM25.
7. Faz upsert idempotente no Qdrant em lotes de 100.

## Recuperação

O Qdrant mantém os vetores nomeados `dense` e `bm25`. A consulta recupera até 20
chunks por busca semântica e lexical, combina os rankings com RRF e filtra pelo
perfil de maturidade. O reranker reduz o conjunto para cinco chunks.

O padrão gratuito usa reranking lexical. O adaptador BGE está disponível quando
`sentence-transformers` estiver instalado e `RERANKER_PROVIDER=bge` estiver
configurado.

## Geração fundamentada

O gerador padrão é determinístico: agrupa os chunks por tecnologia, cruza dores e
perfil e só recomenda produtos presentes nos metadados recuperados. Cada item exige
uma citação com `chunk_id`, URL, seção e trecho.

O gerador OpenAI é opcional. Quando ativado, usa saída estruturada validada pelo
mesmo contrato e recebe somente o perfil da startup e os cinco chunks rerankeados.

## Limites deliberados

- Brave não faz parte da solução porque o projeto adotou SearXNG, DDGS e Firecrawl.
- O modo lexical não equivale à qualidade de um cross-encoder BGE; ele é o fallback
  gratuito e reproduzível.
- A ingestão precisa ser executada antes de recomendar para startups com IA.
- O catálogo aponta para páginas oficiais, mas alterações externas podem exigir
  atualização das URLs.
