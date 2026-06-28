# Deploy Remoto

O pacote `infra/production` executa Caddy com HTTPS automático, API e worker em
processos separados, Qdrant persistente e SearXNG interno. Apenas portas 80/443 são
expostas; API, busca e banco vetorial permanecem na rede Docker.

```bash
cd infra/production
cp .env.example .env
docker compose pull
docker compose up -d
docker compose ps
curl --fail https://$DOMAIN/health
```

`BACKEND_IMAGE` deve usar a tag SHA publicada pelo CI, nunca somente `latest`. O
arquivo apontado por `BACKEND_ENV_FILE` fica fora do repositório, com permissão de
leitura restrita, e contém Supabase, JWKS, Firecrawl e token de métricas.

Rollback:

1. Troque `BACKEND_IMAGE` para o SHA anterior.
2. Execute `docker compose pull api worker`.
3. Execute `docker compose up -d api worker`.
4. Confirme health, ready, heartbeat e um lote canário.

A configuração foi validada localmente com `docker compose config`. A implantação
remota exige servidor Linux, DNS apontado, portas 80/443 liberadas e acesso ao GHCR;
esses dados não fazem parte do repositório.
