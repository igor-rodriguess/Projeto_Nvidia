# Relatorio de Auditoria - Frontend NVIDIA Startup AI Radar

**Data:** 30/06/2026  
**Escopo:** frontend React, contratos REST, fluxos autenticados e amostra integral dos 50 perfis mais recentes no Supabase.  
**Limitacao:** a automacao visual do navegador nao estava disponivel nesta sessao. A auditoria foi realizada por inspecao do codigo, chamadas reais a API, build/lint/testes e verificacao semantica dos dados persistidos. Responsividade e detalhes visuais ainda precisam de uma rodada manual em navegadores reais.

## 1. Resumo

- **24 problemas encontrados:** 5 criticos, 5 de nomenclatura/semantica, 4 de dados e 10 de usabilidade ou completude.
- **Avaliacao geral:** regular. O nucleo de dados esta funcional, mas faltam correcoes importantes antes de uma apresentacao final para gestores de Startups & VCs.
- **Base validada:** 50 startups, 50 execucoes mais recentes concluidas, 50 classificacoes, 50 recomendacoes e 50 briefings.
- **Pontos positivos:** nao foram encontradas URLs estruturalmente invalidas nem duplicatas exatas entre as 1.000 fontes das execucoes mais recentes. As combinacoes gerais entre classe e nivel sao majoritariamente coerentes.
- **Risco principal:** a interface nao permite auditar as evidencias que sustentam classificacao e recomendacao, embora existam 6.958 evidencias no banco.

## 2. Problemas Criticos (bloqueiam uso)

### BUG-001 - Detalhe de lote redireciona para o dashboard
- **Pagina/Componente:** `BatchCard` e roteamento.
- **Descricao:** o botao "Detalhes" navega para `/batches/:id`, mas essa rota e pagina nao existem em `App.tsx`. A rota curinga redireciona silenciosamente para `/`.
- **Esperado:** abrir itens, progresso, erros e dead letters do lote.
- **Correcao:** criar `BatchDetailPage`, registrar `/batches/:id` e usar os hooks `getBatchItems` e `getDeadLetters` ja existentes.

### BUG-002 - Contadores e progresso de lotes usam campos inexistentes
- **Pagina/Componente:** `BatchCard`, `BatchProgressBar`, dashboard.
- **Descricao:** o frontend espera `completed_items`; a API retorna `succeeded_items` e `processed_items`. Isso produz valores vazios e calculos `NaN`.
- **Esperado:** contadores e barra coerentes com os 50 itens concluidos do lote real.
- **Correcao:** normalizar a resposta no backend ou alterar o tipo `Batch` e componentes para `succeeded_items`; adicionar teste de contrato API-frontend.

### BUG-003 - Lote recem-criado nao pode ser executado pela interface
- **Pagina/Componente:** `BatchCard`.
- **Descricao:** `canRun` exige status `created`, mas o backend cria lotes com status `pending`.
- **Esperado:** o botao Executar deve aparecer para lote `pending`.
- **Correcao:** padronizar o enum compartilhado e substituir `created` por `pending` no frontend.

### BUG-004 - Timeline concluida aparece como pendente
- **Pagina/Componente:** `PipelineTimeline`.
- **Descricao:** execucoes concluidas possuem `current_stage="completed"`, valor ausente da lista de estagios. O indice fica `-1` e todos os agentes aparecem pendentes.
- **Esperado:** todos os estagios com check quando `run.status === "completed"`.
- **Correcao:** tratar estados terminais antes de calcular o indice e alinhar os nomes reais do pipeline, incluindo `recommendation_refiner`.

### BUG-005 - Evidencias nao sao acessiveis pela API nem pela interface
- **Pagina/Componente:** detalhe da startup.
- **Descricao:** nao existe aba de evidencias nem endpoint de leitura com fonte, URL, trecho e confianca. Isso impede rastreabilidade e validacao das conclusoes dos agentes.
- **Esperado:** tabela filtravel, expansivel e ligada a execucao selecionada.
- **Correcao:** criar `GET /api/v1/runs/{id}/evidences` com join de `evidences` e `sources`, e implementar a aba com classificacao, score e link externo.

## 3. Problemas de Nomenclatura e Rotulos

### LABEL-001 - "Maturidade" exibe classificacao, nao nivel
A coluna e o filtro de maturidade usam `AI-native`, `AI-enabled`, `API-consumer` e `Non-AI`. Esses valores representam **Classificacao de IA**. Renomear coluna/filtro para "Classificacao" e adicionar "Nivel de maturidade" numerico de 1 a 5.

### LABEL-002 - Diagnostico mistura classificacao e maturidade
O painel "Classificacao de Maturidade" combina classe, nivel, confianca e tecnologias. Separar em: Classificacao de IA, Nivel de maturidade, Confianca e Tecnologias utilizadas.

### LABEL-003 - Fit Score foi renomeado para Score de Oportunidade
O backend converte `fit_score` para escala 0-10 e a UI chama o valor de "Score de Oportunidade". Isso muda o significado. Exibir "Fit NVIDIA: 86%" ou manter 0,86 com escala explicita.

### LABEL-004 - Nomes de produtos NVIDIA nao estao canonicos
Foram persistidos `Triton`, `NIM`, `NeMo` e `AI Enterprise`. Na interface, exibir NVIDIA Triton Inference Server, NVIDIA NIM, NVIDIA NeMo e NVIDIA AI Enterprise. Acronomos devem ter tooltip ou descricao curta.

### LABEL-005 - Escala declarada 1-5 recebe nivel zero
As seis startups `Non-AI` estao no nivel `0/5`, mas o produto descreve escala de 1 a 5. Definir formalmente 0 como "Nao demonstrado" ou migrar para nivel 1. A UI deve mostrar as descricoes: Experimental, Adocao inicial, Integracao, Avancado e Otimizado.

## 4. Inconsistencias nos Dados dos Agentes

### DATA-001 - Sete classificacoes AI-native precisam de revisao humana
Delend, Descola, Plugin, PIA, AutoU, Excuela e Company Hero nao apresentaram, no resumo/evidencias usadas pelo classificador, termos fortes facilmente verificaveis como treinamento de modelos, PyTorch, TensorFlow, equipe de ML ou modelo proprio. Isso nao prova erro, mas e um alerta de sustentacao insuficiente para `AI-native`.

**Correcao:** exigir ao menos uma evidencia primaria de desenvolvimento proprio para AI-native; sem isso, rebaixar para AI-enabled ou marcar `review_required`.

### DATA-002 - NVIDIA Inception aparece como tecnologia recomendada
O programa Inception foi retornado como tecnologia em 8 das 50 recomendacoes. Ele e um programa de beneficios, nao componente da stack.

**Correcao:** validar recomendacoes contra um catalogo tipado (`technology`, `platform`, `program`, `benefit`) e mover Inception para a secao de aderencia ao programa.

### DATA-003 - Localizacao praticamente ausente
49 das 50 startups nao possuem cidade nem estado. O filtro de cidade e, portanto, pouco util e a promessa de mapeamento geografico nao esta atendida.

**Correcao:** enriquecer a partir de pagina oficial, perfil Cubo e fontes institucionais, preservando fonte e confianca do campo.

### DATA-004 - Alegacao numerica sem citacao adjacente
O briefing da DeltaAI afirma economia de ate 40% dos custos juridicos. O texto pode vir da descricao publica da empresa, mas a UI nao mostra a fonte ao lado da alegacao.

**Correcao:** exigir `claim -> source_id` no Briefing Agent e renderizar nota/citacao para qualquer percentual, benchmark ou impacto quantitativo.

## 5. Problemas de Usabilidade e Experiencia

### UX-001 - Busca global e notificacoes sao decorativas
O campo de busca do cabecalho nao possui estado, evento ou navegacao. O sino tambem nao executa acao e sempre mostra um indicador. Implementar ou remover ate que exista funcionalidade.

### UX-002 - Nao existe fluxo de "Nova Analise" individual
O usuario pode criar lote a partir do arquivo CURATED, mas nao informar uma startup/URL e acompanhar uma investigacao individual. Criar formulario validado e endpoint correspondente.

### UX-003 - Acompanhamento nao atualiza automaticamente
A listagem de lotes exige clique em Atualizar; nao existe detalhe funcional nem polling visivel. Adicionar polling enquanto houver status `pending` ou `running`, com intervalo e cancelamento controlados.

### UX-004 - Briefing nao possui copiar ou exportar
O Markdown e renderizado, mas faltam copiar, baixar `.md` e exportar PDF. Implementar comandos com feedback de sucesso/erro.

### UX-005 - Layout mobile fica obstruido pela sidebar
Em ate 768 px o conteudo perde a margem esquerda, mas a sidebar fixa continua visivel com largura integral configurada. Criar navegacao mobile recolhivel e testar em 375x812 e 768x1024.

### UX-006 - Login nao valida localmente nem traduz erros
O formulario usa `noValidate`, nao verifica email/senha antes da chamada e exibe mensagens cruas do Supabase. Adicionar validacao acessivel e mapear credenciais invalidas, conta nao confirmada e indisponibilidade de rede.

### UX-007 - Acoes ignoram o papel do usuario
Usuarios `readonly` veem Novo Lote, Executar, Retomar e Cancelar, embora o backend retorne 403. Ocultar ou desabilitar comandos conforme `radar_role`, mantendo o backend como autoridade.

### UX-008 - Indicador "Sistema Online" e fixo
A sidebar sempre informa Online, sem consultar `/health` ou `/ready`. Vincular o indicador a health check real e exibir estado degradado para Supabase/Qdrant.

### UX-009 - Falha ao carregar analise e silenciosa
`StartupPage` envia o erro ao console e depois mostra conteudo indisponivel, sem explicar a falha ou oferecer retry. Criar estado de erro separado para `getRunAnalysis`.

### UX-010 - Impacto e roadmap refinado nao sao exibidos
A API retorna impacto e refinamento, mas a pagina usa somente a recomendacao inicial. Mostrar impacto com premissas/fontes e o roadmap refinado por horizonte, sem converter estimativas internas em promessas.

## 6. Recomendacoes Gerais

1. Definir schemas OpenAPI/Pydantic de resposta e gerar os tipos TypeScript automaticamente para eliminar divergencias como `completed_items` versus `succeeded_items`.
2. Criar testes end-to-end autenticados para login, dashboard, filtros, detalhe, criacao de lote, polling e logout.
3. Adicionar testes de contrato com fixtures reais anonimizadas para classificacao, recomendacao, impacto e briefing.
4. Implementar catalogo canonico NVIDIA com nome oficial, tipo, descricao, URL oficial e aliases aceitos.
5. Exibir proveniencia em todo campo inferido: fonte, data da coleta, confianca e execucao responsavel.
6. Fazer code splitting por rota; o bundle atual tem aproximadamente 1,1 MB antes de gzip e gera alerta no build.
7. Adicionar paginacao server-side antes de superar 100 startups; a tela atual carrega no maximo 100 registros.
8. Incluir testes de acessibilidade com teclado, foco, contraste e leitores de tela.

## 7. Checklist de Verificacao Final

- [ ] Login valida campos, traduz erros, redireciona e faz logout corretamente.
- [ ] Dashboard confere com `/api/v1/metrics` e explica periodo/denominador da taxa de sucesso.
- [ ] Busca global, notificacoes e indicador de saude sao funcionais ou foram removidos.
- [ ] Classificacao e nivel de maturidade aparecem como conceitos distintos.
- [ ] Filtros combinados produzem os mesmos resultados da API.
- [ ] Cards e progresso de lote usam o contrato real do backend.
- [ ] Lote pendente pode ser iniciado e sua pagina de detalhe abre corretamente.
- [ ] Polling acompanha cada estagio sem duplicar requisicoes.
- [ ] Timeline concluida marca todos os agentes como concluidos.
- [ ] Evidencias exibem fonte, URL, trecho, confianca e classificacao.
- [ ] Toda alegacao quantitativa possui citacao rastreavel.
- [ ] Recomendacoes usam nomes NVIDIA oficiais e separam tecnologia de programa.
- [ ] Impacto deixa claras premissas, incertezas e necessidade de POC.
- [ ] Briefing pode ser copiado e exportado sem truncamento.
- [ ] Perfis `readonly`, `analyst` e `admin` exibem apenas acoes permitidas.
- [ ] Layout passa em 375x812, 768x1024, 1366x768 e 1920x1080.
- [ ] Console permanece sem erros em estados cheio, vazio, carregando, 401, 403, 404 e 500.
- [ ] Build, lint, testes unitarios, integracao, contrato e E2E estao aprovados.
