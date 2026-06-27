# Backend API e Processamento em Lote

## Objetivo

O backend transforma a base CURATED do Cubo em trabalhos duráveis. Cada startup é
processada pela pipeline de oito estágios e recebe classificação, recomendação,
impacto e briefing. O Supabase guarda o progresso por lote e por item, permitindo
retomar uma execução interrompida.

## Iniciar a API

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- Saúde: `http://127.0.0.1:8000/health`
- Dependências: `http://127.0.0.1:8000/ready`
- Swagger: `http://127.0.0.1:8000/docs`
- OpenAPI: `http://127.0.0.1:8000/openapi.json`

O bind local em `127.0.0.1` é intencional. Antes de expor a API na internet, deve-se
adicionar autenticação e limites de requisição.

## Criar e iniciar um lote

Sem `limit`, todas as startups da versão CURATED mais recente são incluídas:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/batches \
  -H "Content-Type: application/json" \
  -d '{"auto_start": true, "max_attempts": 2}'
```

Para validar com duas startups sem consumir a base inteira:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/batches \
  -H "Content-Type: application/json" \
  -d '{"limit": 2, "auto_start": true}'
```

## Acompanhar e retomar

```text
GET  /api/v1/batches
GET  /api/v1/batches/{batch_id}
GET  /api/v1/batches/{batch_id}/items
POST /api/v1/batches/{batch_id}/run
POST /api/v1/batches/{batch_id}/resume
POST /api/v1/batches/{batch_id}/cancel
```

Itens interrompidos voltam para `pending` no `resume`. Itens `failed` são tentados
novamente enquanto `attempt_count < max_attempts`. Uma falha individual não encerra
as demais startups, salvo quando `stop_on_error=true`.

## Consultar resultados

```text
GET /api/v1/startups
GET /api/v1/startups/{startup_id}
GET /api/v1/runs/{run_id}
GET /api/v1/runs/{run_id}/briefing
```

O último endpoint retorna `text/markdown`. Os demais retornam JSON.

## Operação por CLI

Criar um lote com todas as startups, sem iniciar:

```bash
python scripts/run_startup_batch.py create
```

Criar e executar duas startups:

```bash
python scripts/run_startup_batch.py create --limit 2 --run
```

Retomar e consultar:

```bash
python scripts/run_startup_batch.py resume <batch_id>
python scripts/run_startup_batch.py status <batch_id>
```

O processamento completo é deliberadamente sequencial para respeitar limites das
fontes e APIs. Com 50 startups, a execução pode levar horas. O processo pode ser
interrompido e retomado sem perder itens concluídos.
