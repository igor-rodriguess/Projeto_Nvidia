# Plano de Ação para Excelência (Nota 10)

## Resumo Executivo

O NVIDIA Startup AI Radar parte de uma base técnica madura para MVP: pipeline de oito
estágios, contratos Pydantic, RAG híbrido, Supabase, Qdrant, API autenticada, worker
durável, métricas, Docker e 84 testes. A evolução de 7,7 para 10 não depende de criar
mais funcionalidades indiscriminadamente, mas de provar qualidade, segurança e
operação contínua. Este plano organiza seis semanas em três ondas para uma equipe de
2 a 3 pessoas. Cada avanço de nota depende de evidência mensurável, não apenas de
código concluído.

### Papéis sugeridos

- **TL/Backend:** contratos, API, fila, banco e revisão técnica.
- **AI/RAG:** avaliação, evidências, classificação e recomendações.
- **SRE/Security:** CI/CD, segurança, deploy, métricas e continuidade.
- **Revisor NVIDIA/Produto:** validação do conjunto ouro e utilidade dos briefings.

## Onda 1 - Consolidação do MVP (semanas 1-2)

Objetivo: concluir a validação real, corrigir semântica de erros e eliminar riscos
imediatos de credenciais.

| Atividade | Responsável | Esforço estimado | Critério de conclusão | Impacto na nota |
|---|---|---:|---|---:|
| Concluir lote de 50 startups | TL/Backend + AI/RAG | 2 dias de acompanhamento | 50/50 itens em estado terminal; 100% com `pipeline_run_id` ou erro terminal explicado; nenhum item perdido | +0,2 |
| Revisar amostra aleatória estratificada | AI/RAG + Revisor NVIDIA | 2-3 pessoa-dia | 10 startups sorteadas com seed registrada; rubrica preenchida; concordância >= 90% em classificação, evidência principal e recomendação aplicável | +0,2 |
| Separar warnings de erros críticos | TL/Backend | 2-3 pessoa-dia | Contratos possuem `warnings`, `source_errors` e `critical_errors`; `partial` ocorre somente quando falta artefato obrigatório; testes cobrem cada classe | +0,2 |
| Recalibrar status da pipeline | TL/Backend + AI/RAG | 1-2 pessoa-dia | Em reprocessamento controlado, menos de 10% ficam `partial`; todo `completed` possui classificação, recomendação/aviso, impacto e briefing | +0,1 |
| Rotacionar credenciais | SRE/Security + proprietário das contas | 1 pessoa-dia | Chaves antigas de Supabase e Firecrawl revogadas; novas chaves no cofre/ambiente; API e worker reiniciados; smoke test aprovado | +0,1 |
| Implantar scan de segredos | SRE/Security | 0,5-1 pessoa-dia | TruffleHog ou Gitleaks executa no histórico e CI; zero segredo ativo encontrado; falso positivo documentado | +0,1 |

### Ordem de execução

1. Manter o lote atual rodando e registrar duração, erros e consumo por startup.
2. Rotacionar segredos sem esperar o encerramento da onda; reiniciar pelo mecanismo
   de retomada depois da troca.
3. Implementar a taxonomia de erros antes de reprocessar os casos `partial`.
4. Gerar automaticamente a amostra com seed e exportar uma planilha/rubrica de revisão.
5. Publicar um relatório de aceitação com métricas do lote e decisões de correção.

### Artefatos obrigatórios

- `docs/acceptance/lote_50_<data>.md` com duração, status e erros.
- `docs/acceptance/revisao_amostra_10.csv` com rubrica e concordância.
- Relatório de scan de segredos anexado à execução de CI.

## Onda 2 - Robustez e Avaliação (semanas 3-4)

Objetivo: medir a qualidade intelectual do sistema, modelar o fit com o programa
Inception e fortalecer a execução contínua.

| Atividade | Responsável | Esforço estimado | Critério de conclusão | Impacto na nota |
|---|---|---:|---|---:|
| Criar conjunto ouro de 10 startups | AI/RAG + Revisor NVIDIA | 3-4 pessoa-dia | Ground truth versionado com classe de IA, evidências aceitas, tecnologias esperadas e justificativa aprovada | +0,2 |
| Construir harness de avaliação | AI/RAG | 3-4 pessoa-dia | Comando reproduzível calcula acurácia >= 85%, precisão top-3, groundedness >= 90% e utilidade média >= 4/5 | +0,25 |
| Criar `InceptionFitAgent` | AI/RAG + Produto | 3-4 pessoa-dia | Contrato separado para elegibilidade, estágio, necessidades e benefícios; ausência de dado resulta em `unknown`, nunca em inferência não sustentada | +0,15 |
| Integrar fit ao briefing | TL/Backend | 1-2 pessoa-dia | Briefing inclui seção “Aderência ao NVIDIA Inception”, fontes, lacunas e próximas perguntas; persistência e API atualizadas | +0,1 |
| Implementar lease renovável | TL/Backend + SRE | 2-3 pessoa-dia | Heartbeat periódico durante chamadas longas; lease tem proprietário e expiração; dois workers não processam o mesmo item em teste de caos | +0,15 |
| Implementar dead-letter queue | TL/Backend | 1-2 pessoa-dia | Item após máximo de tentativas vai para DLQ com stack, categoria e ação de replay; nenhum loop infinito | +0,05 |
| Cache e orçamento Firecrawl | Backend + SRE | 2-3 pessoa-dia | Cache por URL e hash de opções no Supabase, TTL 7 dias, limite por lote e alerta em 80% do orçamento | +0,1 |
| Medir custo por startup | SRE/Security | 1 pessoa-dia | Dashboard registra chamadas, cache hit, sucesso e custo estimado; média Firecrawl <= USD 0,10/startup no conjunto de teste | +0,05 |

### Protocolo de avaliação

- Fixar versão do conjunto ouro, documentos NVIDIA e código avaliado.
- Executar cada caso sem cache e registrar seed/configuração.
- Groundedness deve verificar afirmação, trecho e URL, não apenas presença de citação.
- A revisão de utilidade deve ser cega para reduzir viés da equipe que implementou.
- Falhas devem gerar backlog com severidade e exemplo reproduzível.

### InceptionFitAgent: contrato mínimo

- `eligibility_status`: `eligible`, `ineligible`, `unknown`.
- `startup_stage`: `early`, `growth`, `scale`, `unknown`.
- `needs`: créditos, suporte técnico, infraestrutura, go-to-market e networking.
- `benefit_matches`: benefício, justificativa, fonte e confiança.
- `open_questions`: dados que o time NVIDIA deve confirmar.

## Onda 3 - Produção Enterprise (semanas 5-6)

Objetivo: implantar com segurança, automação, limites operacionais conhecidos e
governança de dados.

| Atividade | Responsável | Esforço estimado | Critério de conclusão | Impacto na nota |
|---|---|---:|---|---:|
| Criar CI/CD | SRE + TL/Backend | 2-3 pessoa-dia | Pull request executa lint, type check, testes, scan de segredos e build; main publica imagem imutável; migration exige aprovação do ambiente | +0,15 |
| Smoke test em Docker | SRE | 1 pessoa-dia | CI sobe Qdrant, SearXNG, API e worker; executa fluxo mínimo; coleta logs; encerra recursos sem vazamento | +0,05 |
| Migrar para Supabase Auth JWT | Backend + Security | 3-4 pessoa-dia | JWT validado por JWKS; chave estática removida dos endpoints de negócio; expiração e revogação testadas | +0,15 |
| Implementar RBAC e rate limit | Backend + Security | 2-3 pessoa-dia | Roles `admin`, `analyst`, `readonly`; testes 401/403; limites por usuário e IP com resposta 429 e métricas | +0,1 |
| Implantar API e worker remotamente | SRE | 3-5 pessoa-dia | HTTPS válido, serviços separados, health checks, rollback documentado e zero segredo na imagem | +0,15 |
| Centralizar métricas, logs e alertas | SRE | 2-3 pessoa-dia | Dashboard mostra latência, 5xx, fila, heartbeat, Firecrawl e RAG; alertas testados para worker parado e backlog crescente | +0,1 |
| Testar backup e restauração | SRE + Backend | 1-2 pessoa-dia | Backup diário configurado; restauração em ambiente isolado executada; RPO/RTO medidos e documentados | +0,05 |
| Executar testes de carga e caos | SRE + Backend | 2-3 pessoa-dia | Dois workers, interrupção de processo e retomada sem duplicata; CPU, memória, duração e erros documentados | +0,1 |
| Definir retenção e LGPD | Produto + Security + Backend | 2-3 pessoa-dia | Política aprovada; traces com TTL 90 dias, raw com TTL 6 meses; job de limpeza testado em dry-run e execução real | +0,05 |
| Publicar runbook de produção | SRE + TL/Backend | 1-2 pessoa-dia | Runbook cobre deploy, rollback, rotação, DLQ, indisponibilidade de APIs, restauração e contato responsável | +0,05 |

### Meta de desempenho realista

O requisito “100 startups em menos de 30 minutos com 2 workers” não é compatível com
uma investigação web profunda que atualmente leva vários minutos por startup e
depende de limites externos. Ele deve ser dividido em dois testes:

1. **Carga sintética/cached:** 100 itens, 2 workers, menos de 30 minutos, menos de 1%
   de falhas críticas e nenhuma duplicação.
2. **Carga live:** 100 startups, 2 workers, orçamento de consultas fixado, tempo-alvo
   definido após o baseline da Onda 1. Meta inicial realista: menos de 6 horas, com
   possibilidade de reduzir após cache, busca adaptativa e paralelismo controlado.

Qualquer meta live mais agressiva exige diminuir consultas por startup, aumentar
workers e negociar limites de Firecrawl/fontes. A qualidade não deve ser sacrificada
para cumprir uma duração arbitrária.

## Nota Projetada por Onda

| Marco | Nota projetada | Evidência necessária para conceder a nota |
|---|---:|---|
| Estado atual | 7,7 | Backend funcional, lote real iniciado, 84 testes e smoke operacional |
| Onda 1 concluída | 8,5 | Lote 50/50, concordância >= 90%, status recalibrado e segredos rotacionados |
| Onda 2 concluída | 9,3 | Métricas do conjunto ouro atingidas, InceptionFit integrado, lease/DLQ e custo controlado |
| Onda 3 concluída | 10,0 | Deploy remoto seguro, CI/CD, JWT/RBAC, observabilidade, restore e carga comprovados |

## Riscos e Dependências

| Risco ou dependência | Impacto | Mitigação |
|---|---|---|
| Disponibilidade de especialista NVIDIA | Sem ground truth confiável para fit e utilidade | Reservar duas sessões de 90 minutos nas ondas 1 e 2; registrar decisões na rubrica |
| Limites e custo Firecrawl | Lotes lentos ou caros | Cache, orçamento por lote, busca adaptativa e fallback gratuito |
| Mudanças em sites e motores de busca | Queda de cobertura | Monitoramento por fonte, contratos de extrator e testes canário |
| Poucos exemplos AI-native conhecidos | Avaliação enviesada | Conjunto ouro estratificado por classe, setor e maturidade |
| Rotação de Supabase/Firecrawl depende do proprietário | Risco permanece aberto | Tratar como bloqueador P0 e registrar evidência de revogação, nunca a chave |
| Meta de carga incompatível com APIs externas | Incentivo a reduzir qualidade | Separar testes cached e live; definir SLO após baseline |
| Dois ou três membros com muitas frentes | Atraso e troca excessiva de contexto | Donos claros por atividade, limite de trabalho em progresso e revisão semanal |
| Requisitos LGPD ainda não aprovados | Retenção inadequada | Envolver responsável legal/produto antes do job destrutivo |

## Governança de Execução

- Reunião semanal de 30 minutos baseada apenas em métricas e bloqueios.
- Cada atividade deve produzir evidência verificável anexada ao repositório ou CI.
- Nenhuma nota intermediária sobe com tarefa “em andamento”. O critério precisa estar
  medido e aprovado.
- Mudanças em classificação, RAG ou prompts exigem reexecução do conjunto ouro.
- A definição de pronto para produção exige duas semanas sem incidente crítico no
  ambiente remoto e um exercício de restauração concluído.

## Registro de Execução

Atualizado em 27 de junho de 2026:

- Concluído: taxonomia de warnings, erros de fonte e erros críticos.
- Concluído: recalibração de status e reprocessamento controlado.
- Concluído: gerador determinístico da amostra de aceitação.
- Concluído: scan Gitleaks do histórico, sem achados versionados.
- Concluído: lease com heartbeat, tentativas limitadas, DLQ e replay.
- Concluído: `InceptionFitAgent` conservador, persistência e seção de aderência no briefing.
- Concluído: CI de pull request com Ruff, mypy, 104 testes, Gitleaks e build Docker.
- Parcial: cache Firecrawl de sete dias, limite por startup e ledger de custo estão
  ativos; limite agregado por lote e alerta de 80% ainda precisam ser implementados.
- Pendente externo: rotação das chaves Supabase e Firecrawl pelo proprietário.
- Pendente humano: revisão da amostra e aprovação do conjunto ouro.
