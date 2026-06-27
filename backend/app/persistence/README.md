# Persistência Supabase

Esta camada usa o Supabase PostgreSQL como fonte transacional do projeto. O Qdrant
continua responsável apenas pelos chunks e embeddings da base NVIDIA.

## Estrutura

```text
app/persistence/
  migration.sql
  models.py
  persistence_service.py
  pipeline_with_persistence.py
```

O schema `nvidia_inception` contém:

- `startups`: cadastro consolidado da empresa.
- `pipeline_runs`: execução, status, duração, etapa e erros.
- `search_queries`: consultas planejadas e quantidade de resultados.
- `sources`: URLs, tipo, credibilidade e acessibilidade.
- `evidences`: evidências válidas, médias e descartadas.
- `ai_assessments`: classificação e maturidade de IA.
- `nvidia_recommendations`: saída consolidada do RAG.
- `recommendation_citations`: documentos que fundamentam a recomendação.
- `recommendation_refinements`: tecnologias priorizadas, roadmap e fit final.
- `impact_estimates`: estimativas fundamentadas, KPIs e índice agregado.
- `executive_briefings`: briefing executivo final em Markdown.

## Aplicar a migration

1. Abra o SQL Editor do projeto Supabase.
2. Execute integralmente `app/persistence/migration.sql`.
3. Confirme em Storage que o bucket privado `pipeline-traces` foi criado.

A migration adiciona `nvidia_inception` aos schemas expostos pelo PostgREST sem
remover os schemas que já estavam configurados. Se o projeto não permitir alterar o
papel `authenticator`, adicione o schema manualmente em
`Settings > Data API > Exposed schemas`.

Também é possível aplicar diretamente pela `DATABASE_URL` configurada no `.env`:

```bash
python scripts/apply_supabase_migration.py
```

A migration é idempotente e pode ser executada novamente. Todas as tabelas usam RLS
e somente `service_role` recebe políticas e privilégios de escrita ou leitura.

## Configurar o backend

Adicione ao `backend/.env`:

```dotenv
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SECRET_KEY=sb_secret_sua_chave_secreta
SUPABASE_TRACE_BUCKET=pipeline-traces
```

Nunca envie `SUPABASE_SECRET_KEY` ao navegador ou ao Git. A chave publicável não é
suficiente para esta camada administrativa.

## Executar

```bash
cd backend
python scripts/run_pipeline_with_persistence.py "Clara Pagamentos" "https://clara.com.br"
```

O pipeline cria um `pipeline_run`, persiste cada etapa e envia o trace completo ao
Storage. Uma falha de banco é anexada ao array `errors`, mas scraping, validação,
classificação e RAG continuam em modo degradado.

## Usar em código

```python
from app.persistence import PipelinePersistence, run_pipeline_with_persistence

persistence = PipelinePersistence.from_env()
result = run_pipeline_with_persistence(
    {
        "startup_name": "Clara Pagamentos",
        "site_oficial": "https://clara.com.br",
    },
    persistence=persistence,
)
```

## Testar

```bash
python -m pytest -q tests/test_persistence_service.py
python -m pytest -q tests/test_pipeline_persistence_integration.py
```
