# Runbook de Produção

## Deploy

1. Exigir CI verde e imagem identificada pelo SHA do commit.
2. Aplicar `migration.sql` em ambiente protegido e revisar o log.
3. Implantar API e worker como serviços separados, com os mesmos contratos e secrets.
4. Verificar `/health`, `/ready`, `/api/v1/metrics` e um lote canário.

## Rollback

1. Pausar novos lotes e aguardar ou cancelar apenas o item ativo.
2. Reimplantar a imagem anterior pelo SHA; migrations são aditivas e não devem ser
   revertidas automaticamente.
3. Reiniciar o worker; leases vencidos devolvem itens interrompidos para a fila.

## Credenciais

1. Emitir nova chave no provedor e atualizar o cofre do ambiente.
2. Reiniciar API/worker e executar smoke autenticado.
3. Revogar a chave anterior e registrar data, responsável e evidência, nunca o valor.

## Incidentes

- **Worker parado:** confirmar `worker_missing_with_backlog`, processo e lease; iniciar
  substituto com recuperação de stale batches.
- **DLQ:** consultar `/batches/{id}/dead-letters`, corrigir a causa e usar replay como admin.
- **Firecrawl indisponível:** confirmar alerta e fallback; não elevar o teto para contornar 402.
- **SearXNG indisponível:** verificar container e fallback DDGS; reduzir carga se houver bloqueio.
- **Qdrant indisponível:** interromper recomendações, preservar coleta e restaurar a collection.
- **Supabase indisponível:** pausar worker para evitar execuções sem rastreabilidade.

## Backup e Retenção

- Backup diário, checksum e teste mensal de restauração isolada.
- `apply_retention.py` em dry-run, revisão do relatório e depois `--execute`.
- Traces: 90 dias; raw: 180 dias; cache da pipeline: 30 dias.

## Responsabilidades

- Responsável técnico: definir antes do go-live.
- Responsável por segurança/credenciais: definir antes do go-live.
- Responsável pelo programa NVIDIA/revisão de qualidade: definir antes do go-live.
- Canal de incidente e escalonamento: definir antes do go-live.
