# Autenticação e Autorização

A API valida tokens de acesso Supabase pelo endpoint JWKS. Assinatura, emissor,
audience e expiração são obrigatórios. O papel da aplicação deve ser informado em
`app_metadata.radar_role` como `admin`, `analyst` ou `readonly`; valores ausentes ou
desconhecidos recebem `readonly`.

Permissões:

- `readonly`: consultas de startups, execuções, briefings, lotes e métricas.
- `analyst`: leitura e criação, execução ou retomada de lotes.
- `admin`: todas as anteriores, cancelamento, replay da DLQ e revogação de tokens.

Tokens revogados são identificados por `jti` ou `session_id`. O endpoint
`POST /api/v1/auth/revoke` insere o identificador na denylist compartilhada. O rate
limit também é atômico no PostgreSQL e responde `429` com `Retry-After`.

Em produção configure:

```dotenv
ENVIRONMENT=production
ALLOW_LEGACY_API_KEY=false
SUPABASE_JWKS_URL=https://<projeto>.supabase.co/auth/v1/.well-known/jwks.json
SUPABASE_JWT_ISSUER=https://<projeto>.supabase.co/auth/v1
SUPABASE_JWT_AUDIENCE=authenticated
```

A API key legada existe apenas para desenvolvimento e migração local. Ela não é
aceita quando `ENVIRONMENT=production`, salvo liberação explícita que deve ser
tratada como exceção temporária.
