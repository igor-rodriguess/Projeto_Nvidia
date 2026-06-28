# Teste Sintético de Carga e Caos - 2026-06-28

## Configuração

- 100 startups sintéticas em dois lotes de 50.
- Dois workers concorrentes.
- Pipeline determinística equivalente a cache hit, sem rede externa.
- Persistência em fake transacional usada pelos testes do repositório.

## Resultado

- Tempo da chamada de carga: 0,10 segundo.
- Itens terminais: 100/100.
- Duplicatas: 0.
- Falhas críticas: 0.
- Meta cached de menos de 30 minutos: atingida.

O teste de caos expirou o lease de um worker após marcar um item como `running`. Um
worker substituto recuperou o lote, devolveu o item para `pending` e o concluiu uma
única vez.

Este resultado valida coordenação e idempotência do caminho cached. Ele não representa
latência live de SearXNG, sites públicos, Firecrawl, Supabase ou Qdrant; o baseline
live deve ser calculado com o lote real de 50 startups.
