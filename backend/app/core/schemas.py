from __future__ import annotations

from typing import Any, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


AIClassification = Literal["AI-native", "AI-enabled", "API-consumer", "Non-AI"]
NVIDIATechnology = Literal[
    "NIM",
    "Triton",
    "TensorRT-LLM",
    "NeMo",
    "RAPIDS",
    "CUDA",
    "Riva",
    "Omniverse",
    "Clara",
    "Isaac",
    "Morpheus",
    "AI Enterprise",
    "Inception",
]


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class PipelineInput(ContractModel):
    startup_name: str = Field(min_length=1)
    site_oficial: str | None = None
    categoria: str | None = None
    descricao_curta: str | None = None
    cidade: str | None = None
    estado: str | None = None
    pais: str | None = "Brasil"
    contexto: str | None = None

    @field_validator("site_oficial")
    @classmethod
    def validate_site(cls, value: str | None) -> str | None:
        if value is None:
            return None
        _ensure_absolute_url(value)
        return value


class SearchQuery(ContractModel):
    consulta: str = Field(min_length=1)
    objetivo: str = Field(min_length=1)
    camada: int = Field(ge=1, le=7)


class SearchTask(ContractModel):
    id: str = Field(min_length=1)
    tipo: Literal["busca_web", "busca_site", "acesso_direto", "feed_rss", "api_get"]
    consulta: str | None = None
    url: str | None = None
    extrator: str | None = None
    max_resultados: int | None = Field(default=None, ge=1, le=50)
    camada: int | None = Field(default=None, ge=1, le=7)
    objetivo: str | None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str | None) -> str | None:
        if value:
            _ensure_absolute_url(value)
        return value


class SearchPlanOutput(ContractModel):
    startup: str = Field(min_length=1)
    site_oficial: str | None = None
    hipotese_maturidade: str = Field(min_length=1)
    plano_consultas: list[SearchQuery]
    tarefas: list[SearchTask]
    fontes_prioritarias: list[dict[str, str]] = Field(default_factory=list)
    observacoes: str = ""

    @model_validator(mode="after")
    def validate_query_coverage(self) -> "SearchPlanOutput":
        if len(self.plano_consultas) < 18:
            raise ValueError("plano_consultas deve conter pelo menos 18 consultas")
        weighted = sum(item.camada in {3, 4} for item in self.plano_consultas)
        if weighted / len(self.plano_consultas) < 0.5:
            raise ValueError("as camadas 3 e 4 devem representar pelo menos 50% das consultas")
        return self


class SearchResult(ContractModel):
    titulo: str = Field(min_length=1)
    url: str
    snippet: str = Field(min_length=1)
    potencial_alto: bool = False
    provedor_busca: str | None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        _ensure_absolute_url(value)
        return value


class CollectedPage(ContractModel):
    url: str
    titulo_pagina: str | None = None
    conteudo_markdown: str | None = None
    conteudo_textual: str | None = None
    metadados: dict[str, Any] = Field(default_factory=dict)
    extrator: str | None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        _ensure_absolute_url(value)
        return value


class ScraperOutput(ContractModel):
    startup: str = Field(min_length=1)
    timestamp_coleta: str
    status: Literal["completo", "parcial", "falha"]
    metricas: dict[str, Any] = Field(default_factory=dict)
    resultados: list[dict[str, Any]] = Field(default_factory=list)
    resultados_buscas: list[SearchResult] = Field(default_factory=list)
    paginas_completas: list[CollectedPage] = Field(default_factory=list)
    varredura_complementar: list[dict[str, Any]] = Field(default_factory=list)
    erros: list[dict[str, Any]] = Field(default_factory=list)


class ValidatedEvidence(ContractModel):
    url: str
    dominio: str | None = None
    tipo_fonte: Literal["oficial", "imprensa", "ecossistema", "social", "outro"]
    credibilidade_fonte: float = Field(ge=0, le=1)
    trecho_evidencia: str = ""
    score_confianca: float = Field(ge=0, le=1)
    classificacao: Literal["alta", "media", "baixa"]
    mencao_forte: bool
    contem_evidencia_ia: bool
    declaracao_propria: bool
    tecnologias_detectadas: list[str] = Field(default_factory=list)
    corroborada: bool = False

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        _ensure_absolute_url(value)
        return value


class DiscardedEvidence(ContractModel):
    url: str
    motivo: str = Field(min_length=1)


class EvidenceSummary(ContractModel):
    tecnologias_detectadas: list[str] = Field(default_factory=list)
    fontes_corroboradas: int = Field(ge=0)
    afirmacoes_chave: list[str] = Field(default_factory=list)
    nota_geral_qualidade_evidencias: float = Field(ge=0, le=1)


class EvidenceValidationOutput(ContractModel):
    startup: str = Field(min_length=1)
    evidencias_validadas: list[ValidatedEvidence] = Field(default_factory=list)
    evidencias_medias: list[ValidatedEvidence] = Field(default_factory=list)
    evidencias_descartadas: list[DiscardedEvidence] = Field(default_factory=list)
    resumo_consolidado: EvidenceSummary
    erros_validacao: list[str] = Field(default_factory=list)


class EvidenceValidatorInput(ContractModel):
    site_oficial: str | None = None
    dados_brutos: ScraperOutput


class MaturityClassifierInput(ContractModel):
    validacao: EvidenceValidationOutput


class DetectedTechnologies(ContractModel):
    frameworks: list[str] = Field(default_factory=list)
    modelos_apis: list[str] = Field(default_factory=list)
    infraestrutura: list[str] = Field(default_factory=list)
    ferramentas_mlops: list[str] = Field(default_factory=list)


class AIMaturityOutput(ContractModel):
    startup: str = Field(min_length=1)
    classificacao: AIClassification
    nivel_maturidade: int = Field(ge=0, le=5)
    confianca_classificacao: float = Field(ge=0, le=1)
    justificativa: str = Field(min_length=1)
    tecnologias_utilizadas: DetectedTechnologies
    necessidades_limitacoes: list[str] = Field(default_factory=list)
    sugestao_inicial_stack_nvidia: str = ""
    evidencias_suporte: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_maturity_for_class(self) -> "AIMaturityOutput":
        if self.classificacao == "Non-AI" and self.nivel_maturidade != 0:
            raise ValueError("Non-AI deve ter nivel_maturidade 0")
        if self.classificacao != "Non-AI" and self.nivel_maturidade == 0:
            raise ValueError("classes com IA devem ter nivel_maturidade entre 1 e 5")
        return self


class KnowledgeMetadata(ContractModel):
    tecnologia: NVIDIATechnology
    tipo: Literal["documentacao", "whitepaper", "blog", "case_study", "github"]
    dores_relacionadas: list[
        Literal["custo", "latencia", "escalabilidade", "governanca", "privacidade", "vendor_lockin"]
    ] = Field(default_factory=list)
    perfil_aplicavel: list[Literal["AI-native", "AI-enabled", "API-consumer"]]
    titulo_secao: str = Field(min_length=1)
    url_fonte: str

    @field_validator("url_fonte")
    @classmethod
    def validate_url(cls, value: str) -> str:
        _ensure_absolute_url(value)
        return value


class KnowledgeChunk(ContractModel):
    chunk_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    metadata: KnowledgeMetadata


class KnowledgeSourceInput(ContractModel):
    titulo: str = Field(min_length=1)
    url: str
    tecnologia: NVIDIATechnology
    tipo: Literal["documentacao", "whitepaper", "blog", "case_study", "github"]
    dores_relacionadas: list[
        Literal["custo", "latencia", "escalabilidade", "governanca", "privacidade", "vendor_lockin"]
    ] = Field(default_factory=list)
    perfil_aplicavel: list[Literal["AI-native", "AI-enabled", "API-consumer"]]

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        _ensure_absolute_url(value)
        return value


class LoadedKnowledgeDocument(ContractModel):
    titulo: str
    content: str = Field(min_length=1)
    source: KnowledgeSourceInput


class IngestionReport(ContractModel):
    status: Literal["completo", "parcial", "falha"]
    fontes_processadas: int = Field(ge=0)
    fontes_com_erro: int = Field(ge=0)
    chunks_gerados: int = Field(ge=0)
    chunks_inseridos: int = Field(ge=0)
    collection_name: str
    errors: list[str] = Field(default_factory=list)


class RetrievedChunk(KnowledgeChunk):
    retrieval_score: float
    rerank_score: float | None = None


class RecommendationItem(ContractModel):
    tecnologia: NVIDIATechnology
    fit_score: float = Field(ge=0, le=1)
    justificativa: str = Field(min_length=1)
    dores_atendidas: list[str] = Field(default_factory=list)
    citacoes: list[str] = Field(min_length=1)


class NVIDIARecommendationOutput(ContractModel):
    startup: str = Field(min_length=1)
    recomendacoes: list[RecommendationItem] = Field(default_factory=list)
    chunks_utilizados: list[RetrievedChunk] = Field(default_factory=list, max_length=5)
    aviso: str | None = None


class RecommenderInput(ContractModel):
    classificacao_ia: AIMaturityOutput


class StageTrace(ContractModel):
    status: Literal["completo", "cache", "parcial", "falha"]
    duration_ms: float = Field(ge=0)
    attempts: int = Field(ge=0)
    tokens_consumidos: int = Field(ge=0, default=0)
    output: dict[str, Any] | None = None
    error: str | None = None


class PipelineOutput(ContractModel):
    startup: str
    status: Literal["completo", "parcial", "falha"]
    classificacao: AIClassification | None = None
    nivel_maturidade: int | None = Field(default=None, ge=0, le=5)
    recomendacao: NVIDIARecommendationOutput | None = None
    trace: dict[str, StageTrace]
    errors: list[str] = Field(default_factory=list)


def _ensure_absolute_url(value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL deve ser absoluta e usar http ou https")
