# StartupAnalysisState — Estado Compartilhado do Pipeline

O `StartupAnalysisState` é o objeto de estado tipado que circula por todos os agentes do pipeline via LangGraph. Cada agente lê campos relevantes e escreve seus resultados de volta ao estado.

## Campos do Estado

| Campo | Tipo | Produzido por | Consumido por |
|---|---|---|---|
| `query` | `str` | Usuário | SearchPlannerAgent |
| `search_terms` | `list[str]` | SearchPlannerAgent | SourceCollectorAgent |
| `priority_sources` | `list[str]` | SearchPlannerAgent | SourceCollectorAgent |
| `collected_sources` | `list[dict]` | SourceCollectorAgent | DataExtractorAgent |
| `raw_texts` | `list[str]` | SourceCollectorAgent | DataExtractorAgent |
| `structured_data` | `list[dict]` | DataExtractorAgent | EvidenceValidatorAgent, AIMaturityClassifierAgent |
| `evidence` | `list[dict]` | EvidenceValidatorAgent | AIMaturityClassifierAgent, BriefingGeneratorAgent |
| `maturity_classification` | `str` | AIMaturityClassifierAgent | NVIDIARagAgent, RecommendationAgent |
| `technical_gaps` | `list[str]` | AIMaturityClassifierAgent | NVIDIARagAgent, RecommendationAgent |
| `nvidia_candidates` | `list[dict]` | NVIDIARagAgent | RecommendationAgent |
| `recommendations` | `list[dict]` | RecommendationAgent | ImpactEstimatorAgent, BriefingGeneratorAgent |
| `impact_estimate` | `dict` | ImpactEstimatorAgent | BriefingGeneratorAgent |
| `briefing` | `str` | BriefingGeneratorAgent | Saída final |

## Implementação

Ver [backend/app/core/startup_analysis_state.py](../backend/app/core/startup_analysis_state.py).
