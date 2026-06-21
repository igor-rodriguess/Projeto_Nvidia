# Arquitetura — NVIDIA Startup AI Radar

## Visão Geral

A solução é baseada em um pipeline multiagente orquestrado via LangGraph, composto por 9 agentes especializados que operam de forma sequencial e modular.

## Componentes Principais

### Backend (FastAPI)
- **agents/** — agentes especializados do pipeline
- **core/** — estado compartilhado do pipeline (`StartupAnalysisState`)
- **services/** — orquestração do pipeline (`startup_search_pipeline.py`)
- **routes/** — endpoints REST expostos ao frontend

### Pipeline Multiagente

```
Entrada do usuário
       │
       ▼
SearchPlannerAgent
       │
       ▼
SourceCollectorAgent
       │
       ▼
DataExtractorAgent
       │
       ▼
EvidenceValidatorAgent
       │
       ▼
AIMaturityClassifierAgent
       │
       ▼
NVIDIARagAgent
       │
       ▼
RecommendationAgent
       │
       ▼
ImpactEstimatorAgent
       │
       ▼
BriefingGeneratorAgent
       │
       ▼
Briefing Executivo Final
```

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Orquestração | LangGraph |
| Backend | FastAPI |
| LLM | (a definir) |
| Embeddings / RAG | (a definir) |
| Frontend | (a definir) |

## Diagrama de Dados

Ver [startup_analysis_state.md](startup_analysis_state.md) para a modelagem do estado compartilhado entre os agentes.
