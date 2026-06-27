# Evidência de Scan de Segredos

## Execução de 2026-06-27

- Ferramenta: Gitleaks em container oficial.
- Escopo: histórico Git completo disponível localmente.
- Commits analisados: 46.
- Volume analisado: aproximadamente 1,22 MB.
- Achados: 0.
- Resultado: aprovado.

Comando reproduzível:

```bash
docker run --rm -v "${PWD}:/repo" zricethezav/gitleaks:latest \
  detect --source=/repo --redact --no-banner
```

O resultado confirma que segredos ativos não foram versionados. Ele não substitui a
rotação das credenciais compartilhadas fora do Git.

## Estado da rotação

- `BACKEND_API_KEY`: rotacionada localmente com aleatoriedade criptográfica.
- `SEARXNG_SECRET`: rotacionada localmente com aleatoriedade criptográfica.
- `SUPABASE_SECRET_KEY`: pendente de revogação e nova emissão no painel Supabase.
- `FIRECRAWL_API_KEY`: pendente de revogação e nova emissão no painel Firecrawl.

Após cada rotação externa, atualizar somente `backend/.env`, reiniciar API/worker e
executar `python scripts/smoke_backend.py`. Nenhum valor de chave deve ser incluído em
evidências, issues ou documentação.
