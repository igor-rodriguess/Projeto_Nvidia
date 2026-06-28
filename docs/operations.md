# Operação do Pipeline

## Pré-requisitos

- Python compatível com as dependências em `backend/requirements.txt`.
- Docker com Qdrant e, preferencialmente, SearXNG.
- Firecrawl opcional para conteúdo JavaScript.
- OpenAI opcional para embeddings ou geração.

## Subir serviços

Antes da primeira execução, crie o `.env` da raiz com um segredo aleatório para o
SearXNG, conforme o arquivo `.env.example`.

```bash
docker compose up -d qdrant searxng
docker compose ps
```

Verificações:

- Qdrant: `http://localhost:6333/dashboard`
- SearXNG: `http://localhost:8080`

## Configurar

Use `backend/.env.example` como referência. Nunca versione `backend/.env`.

Configuração gratuita recomendada:

```dotenv
SEARCH_PROVIDER=searxng
QDRANT_URL=http://localhost:6333
EMBEDDING_PROVIDER=fastembed
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
RAG_GENERATOR_PROVIDER=deterministic
```

## Ingerir conhecimento

```bash
cd backend
python scripts/ingest_nvidia_knowledge.py
```

O relatório informa fontes processadas, erros, chunks gerados e chunks inseridos.
Uma fonte com falha não interrompe as demais.

## Executar investigação

```bash
python scripts/run_enterprise_pipeline.py "Clara Pagamentos" "https://clara.com.br"
```

O cache evita repetir chamadas para o mesmo payload. Para invalidar manualmente uma
execução, remova apenas os arquivos correspondentes em `backend/data/cache/pipeline`.

O endpoint autenticado `/api/v1/metrics` inclui leases ativos/vencidos e, por
provedor externo, requisições, cache hits, falhas e custo estimado. O Firecrawl usa
reserva atômica no Supabase, teto por lote e alerta a partir de 80%.

## Testar

```bash
cd backend
python -m pytest -q
```

## Integração contínua

O workflow `.github/workflows/backend-ci.yml` executa em pull requests e pushes para
`main`: lint de erros críticos, type check dos contratos e da avaliação, testes,
scan Gitleaks do histórico completo e build da imagem Docker sem segredos.

Para reproduzir a etapa de qualidade localmente:

```bash
cd backend
pip install -r requirements-dev.txt
python -m ruff check app tests scripts
python -m mypy
pytest -q
```

## Diagnóstico

- `status: parcial`: consulte `errors` e a etapa correspondente em `trace`.
- Erro de dimensão Qdrant: o modelo de embeddings mudou. Use outra coleção ou
  recrie conscientemente a coleção existente.
- Firecrawl ausente: o loader tenta Trafilatura em HTML estático.
- SearXNG indisponível: o router tenta DDGS e depois Firecrawl Search.
- RAG sem resultados: confirme que a ingestão terminou e que a coleção configurada
  é a mesma usada pelo pipeline.

## Segurança

- Chaves são carregadas por ambiente e `.env` está ignorado pelo Git.
- O trace pode conter conteúdo público coletado; aplique política de retenção antes
  de utilizá-lo em produção.
- Não use o pipeline para contornar autenticação, paywalls ou restrições de acesso.
