# Backup e Restauração

Em 28 de junho de 2026 foi executado um backup real do schema `nvidia_inception`
com `pg_dump` em formato custom e manifesto SHA-256. A primeira execução, incluindo
download da imagem PostgreSQL, levou 92,6 segundos.

O dump foi restaurado em PostgreSQL 17 isolado no Docker. Depois do ajuste de
compatibilidade com `auth.role()`, a restauração levou 34,1 segundos e confirmou 19
tabelas e 19 policies. O container temporário foi removido após a verificação.

```bash
cd backend
python scripts/backup_database.py

set RESTORE_DATABASE_URL=postgresql://usuario:senha@destino-isolado:5432/postgres
python scripts/restore_database.py data/backups/<arquivo>.dump \
  --manifest data/backups/<arquivo>.manifest.json \
  --confirm-isolated-target
```

O restore recusa um destino com o mesmo host, porta e banco da origem. O RTO técnico
observado foi inferior a um minuto, sem contar provisionamento. O RPO depende da
agenda externa: para RPO de 24 horas, programe `backup_database.py` diariamente em
um runner seguro e envie o dump para storage criptografado com ciclo de vida.
