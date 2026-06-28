# Observabilidade e Alertas

O endpoint Prometheus `/metrics` usa um Bearer token exclusivo, separado dos tokens
de usuário. Grave o mesmo valor de `METRICS_BEARER_TOKEN` em
`infra/secrets/metrics_token` e inicie:

```bash
docker compose --profile backend --profile observability up -d
```

Prometheus fica em `http://localhost:9090` e coleta status da pipeline, lotes, itens,
leases, chamadas externas, cache hits, falhas e custo estimado. Quatro regras foram
validadas com `promtool`:

- lease de worker vencido;
- backlog sem worker;
- backlog acima do limite;
- taxa de falhas Firecrawl acima de 50%.

Em produção, encaminhe os alertas para um Alertmanager ou plataforma equivalente e
restrinja a porta 9090 à rede administrativa. Logs estruturados JSON incluem
`request_id`, etapa, duração e erro, podendo ser enviados ao coletor do provedor.
