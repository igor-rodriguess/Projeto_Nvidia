# Arquitetura - NVIDIA Startup AI Radar

## Visão Geral

A solução usa uma pipeline multiagente orquestrada com LangChain Runnables. Os oito
estágios operacionais são sequenciais, modulares, cacheáveis e observáveis.

## Pipeline Operacional

```text
Entrada da startup
  -> Search Planner Agent
  -> Scraper Agent
  -> Evidence Validator Agent
  -> AI Maturity Classifier Agent
  -> NVIDIA Recommender RAG
  -> Recommendation Agent
  -> Impact Estimator Agent
  -> Briefing Generator Agent
  -> Briefing executivo em Markdown
```

O `Scraper Agent` concentra busca web e extração de páginas. O `NVIDIA Recommender
RAG` consulta o Qdrant e entrega recomendações brutas fundamentadas. Os três últimos
agentes priorizam a adoção, estimam impacto sem inventar benchmarks e consolidam o
resultado para decisão executiva.

## Armazenamento

- **Supabase PostgreSQL:** startups, execuções, fontes, evidências, classificações,
  recomendações, impactos e briefings.
- **Supabase Storage:** traces completos em JSON no bucket privado.
- **Qdrant:** chunks e embeddings da documentação oficial NVIDIA.
- **Cache local:** resultados intermediários determinísticos por estágio.

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Orquestração | LangChain Runnables |
| Coleta web | SearXNG, DDGS, Firecrawl e trafilatura |
| Contratos | Pydantic e JSON Schema |
| RAG | Qdrant, busca híbrida dense + BM25 e reranking |
| Persistência | Supabase PostgreSQL e Storage privado |
| Geração | Determinística por padrão; OpenAI opcional no RAG |

## Resiliência

Cada estágio registra duração, tentativas, erros e output no `trace`. Falhas de
persistência ativam modo degradado e não interrompem a investigação. Estimativas
quantitativas exigem benchmark recuperado com URL; na ausência dele, o sistema
retorna KPIs e incertezas para validação em prova de conceito.
