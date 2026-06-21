# NVIDIA Startup AI Radar

*Web Application Document (WAD) — versão consolidada, em construção*

## Status de preenchimento

- [x] 1.1 Contexto
- [ ] 1.2 Problema
- [ ] 1.3 Objetivo
- [ ] 1.4 Pergunta Norteadora
- [ ] 2.1 Escopo
- [ ] 2.2 Fluxo Geral
- [x] 3.1 Requisitos Funcionais
- [x] 3.2 Regras de Negócio
- [x] 3.3 Requisitos Não Funcionais
- [x] 4.1 Arquitetura Geral
- [x] 4.2 Fluxo de Dados
- [ ] 4.3 Banco de Dados
- [x] 5. Agentes de IA (9 agentes)
- [ ] 6. Base de Conhecimento NVIDIA
- [ ] 7. Diferenciais do Projeto
- [ ] 8. Stack Tecnológica
- [ ] 9. Roadmap
- [ ] 10. Referências

## Sumário

1. Introdução
2. Visão Geral da Solução
3. Requisitos do Sistema
4. Arquitetura da Solução
5. Agentes de IA
6. Base de Conhecimento NVIDIA
7. Diferenciais do Projeto
8. Stack Tecnológica
9. Roadmap
10. Referências

---

# 1. Introdução

## 1.1 Contexto

Atualmente, existem diversas startups que utilizam IA, mas o foco não está naquelas que apenas utilizam APIs de grandes players do mercado, aplicando-as em um front-end bem construído. Esse modelo vem se tornando cada vez mais frágil: grandes laboratórios como OpenAI, Anthropic e Google DeepMind estão subindo na cadeia de valor, oferecendo cada vez mais funcionalidades prontas que podem substituir startups dependentes apenas de uma API conectada a uma interface, sem dados proprietários, workflow profundo ou otimização técnica própria.

O interesse, portanto, está em startups com potencial real de crescimento, capazes de se diferenciar por meio de uma stack técnica mais robusta, principalmente as que utilizam tecnologias da NVIDIA para evoluir de protótipos baseados em API para sistemas de IA escaláveis e prontos para produção.

Dessa forma, é necessário mapear e identificar as empresas que podem crescer utilizando essa tecnologia, aprimorando continuamente o processo de mapeamento dessas startups.

## 1.2 Problema

[Descreva qual problema a NVIDIA enfrenta]

## 1.3 Objetivo

[Descreva o objetivo geral do projeto]

## 1.4 Pergunta Norteadora

[Defina a pergunta principal do projeto]

---

# 2. Visão Geral da Solução

## 2.1 Escopo

[Defina o que o sistema faz]

## 2.2 Fluxo Geral

[Descreva o fluxo principal]

### Entrada

[Quais dados entram]

### Processamento

[Como o sistema processa]

### Saída

[O que o sistema entrega]

---

# 3. Requisitos do Sistema

## 3.1 Requisitos Funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF001 | O sistema deve permitir que o usuário insira uma consulta de busca (startup, segmento, palavra-chave ou critério livre) | Alta |
| RF002 | O sistema deve transformar a consulta em estratégia de busca (termos e fontes prioritárias) | Alta |
| RF003 | O sistema deve coletar informações públicas sobre startups nas fontes definidas | Alta |
| RF004 | O sistema deve estruturar os dados coletados em informações organizadas sobre cada startup | Alta |
| RF005 | O sistema deve verificar a confiabilidade das fontes e evidências antes que os dados extraídos sejam incorporados à base do projeto | Alta |
| RF006 | O sistema deve classificar a maturidade da startup em relação ao uso de IA | Alta |
| RF007 | O sistema deve consultar a base de conhecimento NVIDIA via RAG | Alta |
| RF008 | O sistema deve gerar recomendações personalizadas de tecnologias NVIDIA | Alta |
| RF009 | O sistema deve estimar o impacto potencial das tecnologias recomendadas | Alta |
| RF010 | O sistema deve gerar um briefing executivo consolidando os resultados da análise | Alta |
| RF011 | O sistema deve exibir os resultados em uma interface web | Média |
| RF012 | O sistema deve permitir a exportação do briefing executivo | Baixa |
| RF013 | O sistema deve apresentar de forma destacada o impacto estimado da tecnologia NVIDIA sobre a startup analisada, como diferencial da solução | Alta |

## 3.2 Regras de Negócio

| ID | Regra | RF Associado |
|---|---|---|
| RN001 | Uma informação só pode ser tratada como "confirmada" se houver evidência rastreável em pelo menos uma fonte pública verificável; caso contrário, é marcada como "parcial" ou "não confirmada" | RF005 |
| RN002 | A coleta de dados deve se restringir a fontes públicas, respeitando termos de uso, sem acesso a bases fechadas ou pagas | RF003 |
| RN003 | A classificação de maturidade em IA (Non-AI, AI-Enabled, AI-Native, LLM Wrapper) deve seguir critérios objetivos predefinidos, não inferências subjetivas do modelo | RF006 |
| RN004 | Toda tecnologia NVIDIA recomendada deve estar vinculada a pelo menos um gap técnico identificado na startup analisada | RF008 |
| RN005 | A estimativa de impacto deve sempre considerar conjuntamente o ganho potencial e o esforço/complexidade de implementação, nunca apenas um dos dois | RF009, RF013 |
| RN006 | O briefing executivo final não pode conter nenhuma afirmação sem evidência ou fonte associada | RF010 |

## 3.3 Requisitos Não Funcionais

| ID | Requisito |
|---|---|
| RNF001 | Rastreabilidade — toda informação apresentada deve poder ser rastreada até sua fonte original |
| RNF002 | Confiabilidade — o sistema deve minimizar alucinações, distinguindo claramente dados confirmados de inferências |
| RNF003 | Escalabilidade — o pipeline deve suportar o crescimento do volume de startups analisadas sem degradação relevante de desempenho |
| RNF004 | Observabilidade — cada execução do pipeline multiagente deve gerar logs auditáveis por etapa |
| RNF005 | Modularidade — os agentes devem poder ser atualizados ou substituídos individualmente sem impactar o restante do pipeline |
| RNF006 | Conformidade — a coleta de dados deve respeitar termos de uso e políticas de acesso das fontes consultadas |
| RNF007 | Privacidade — o sistema deve armazenar apenas dados públicos, sem coleta de informações sensíveis |
| RNF008 | Desempenho — o tempo de processamento de uma consulta deve ser compatível com uso prático pelo gerente de Startups & VCs |

---

# 4. Arquitetura da Solução

## 4.1 Arquitetura Geral

A arquitetura multiagente foi desenhada para analisar startups brasileiras de forma estruturada, rastreável e auditável. Em vez de uma única chamada a um modelo de IA, o processo é dividido em agentes especializados, cada um com responsabilidade única dentro do pipeline — da coleta de dados até a geração do briefing executivo final.

![Fluxo geral da arquitetura](diagrama_arquitetura.svg)

O pipeline é organizado em quatro fases:

1. **Planejamento e coleta** — definição da estratégia de busca e coleta de dados públicos sobre a startup.
2. **Validação e classificação** — checagem de evidências e classificação da maturidade em IA.
3. **Conhecimento e recomendação** — consulta à base NVIDIA e geração de recomendações com estimativa de impacto.
4. **Entrega** — consolidação de todo o processo no briefing executivo.

## 4.2 Fluxo de Dados

**Entrada**
- Nome de uma startup específica
- Segmento de mercado
- Palavra-chave relacionada a IA
- Critério de busca definido pelo usuário

```json
{
  "query": "startups brasileiras de saúde que usam inteligência artificial"
}
```

**Processamento**
Os dados percorrem as quatro fases descritas em 4.1, passando pelos nove agentes especializados (detalhados na Seção 5), até a geração do resultado consolidado.

**Saída**
- Nome da startup
- Setor
- Descrição do produto
- Evidências encontradas
- Classificação de maturidade em IA
- Gaps técnicos identificados
- Tecnologias NVIDIA recomendadas
- Estimativa de impacto
- Score de oportunidade
- Próxima ação sugerida
- Briefing executivo final

## 4.3 Banco de Dados

[Inserir modelagem]

---

# 5. Agentes de IA

## 5.1 Search Planner Agent

**Responsabilidade**
Transforma a entrada do usuário (startup específica, segmento, palavra-chave ou critério livre) em uma estratégia de busca, definindo termos e fontes prioritárias.

| Entrada | Saída |
|---|---|
| Consulta do usuário <br> Critério de busca <br> Segmento desejado | Lista de termos de busca <br> Fontes prioritárias <br> Estratégia inicial de pesquisa |

## 5.2 Source Collector Agent

**Responsabilidade**
Executa a estratégia definida pelo Search Planner, buscando informações públicas em sites oficiais, notícias, blogs e diretórios.

| Entrada | Saída |
|---|---|
| Lista de termos de busca <br> Fontes sugeridas | Lista de startups encontradas <br> Links das fontes <br> Textos coletados <br> Metadados das fontes |

## 5.3 Data Extractor Agent

**Responsabilidade**
Converte o conteúdo não estruturado coletado em dados organizados sobre cada startup.

| Entrada | Saída |
|---|---|
| Textos coletados <br> Links das fontes <br> Nome das startups encontradas | Nome da startup <br> Setor de atuação <br> Produto/serviço <br> Sinais de uso de IA <br> Founders/decisores públicos <br> Clientes, funding ou tecnologias citadas |

## 5.4 Evidence Validator Agent

**Responsabilidade**
Valida se as informações extraídas têm evidência suficiente nas fontes, reduzindo o risco de alucinação e aumentando a confiabilidade da análise.

| Entrada | Saída |
|---|---|
| Dados estruturados <br> Fontes utilizadas <br> Afirmações geradas pelos agentes anteriores | Evidências associadas a cada afirmação <br> Nível de confiança <br> Classificação (confirmado / parcialmente confirmado / não confirmado) |

## 5.5 AI Maturity Classifier Agent

**Responsabilidade**
Classifica a maturidade da startup quanto ao uso de IA e identifica possíveis gaps técnicos.

| Entrada | Saída |
|---|---|
| Dados estruturados da startup <br> Evidências validadas <br> Sinais de uso de IA | Classificação (Non-AI / AI-Enabled / AI-Native / LLM Wrapper) <br> Justificativa <br> Gaps técnicos |

## 5.6 NVIDIA RAG Agent

**Responsabilidade**
Consulta a base de conhecimento NVIDIA via RAG para recuperar tecnologias relevantes ao perfil e aos gaps da startup analisada.

| Entrada | Saída |
|---|---|
| Perfil da startup <br> Classificação de maturidade <br> Gaps técnicos identificados | Tecnologias NVIDIA candidatas <br> Trechos da base de conhecimento <br> Justificativas técnicas |

## 5.7 Recommendation Agent

**Responsabilidade**
Cruza o perfil da startup com as tecnologias recuperadas pelo RAG para gerar recomendações personalizadas.

| Entrada | Saída |
|---|---|
| Perfil da startup <br> Gaps técnicos <br> Tecnologias NVIDIA candidatas <br> Evidências coletadas | Tecnologias recomendadas <br> Justificativa técnica <br> Justificativa de negócio <br> Prioridade <br> Complexidade de implementação |

## 5.8 Impact Estimator Agent

**Responsabilidade**
Estima o impacto potencial da adoção das tecnologias recomendadas, considerando ganho, esforço e riscos.

| Entrada | Saída |
|---|---|
| Recomendações geradas <br> Perfil da startup <br> Gaps técnicos <br> Maturidade em IA | Impacto esperado <br> Tipo de ganho <br> Nível de impacto <br> Esforço estimado <br> Riscos/limitações |

## 5.9 Briefing Generator Agent

**Responsabilidade**
Consolida todos os dados gerados pelo pipeline em um relatório executivo final para apoiar a atuação da NVIDIA.

| Entrada | Saída |
|---|---|
| Perfil da startup <br> Evidências <br> Classificação <br> Gaps <br> Recomendações <br> Estimativa de impacto | Briefing executivo <br> Resumo da oportunidade <br> Próxima melhor ação <br> Evidências utilizadas <br> Recomendação final |

---

# 6. Base de Conhecimento NVIDIA

## 6.1 Fontes Utilizadas

[Adicionar fontes]

## 6.2 Tecnologias NVIDIA

### NVIDIA Inception

[Descrição]

### NVIDIA NIM

[Descrição]

### NVIDIA NeMo

[Descrição]

### NeMo Guardrails

[Descrição]

### NVIDIA Triton Inference Server

[Descrição]

### TensorRT-LLM

[Descrição]

### NVIDIA RAPIDS

[Descrição]

### cuDF

[Descrição]

### cuML

[Descrição]

### CUDA

[Descrição]

### NVIDIA Riva

[Descrição]

### NVIDIA Omniverse

[Descrição]

### NVIDIA Isaac

[Descrição]

### NVIDIA Clara

[Descrição]

### NVIDIA Morpheus

[Descrição]

### NVIDIA AI Enterprise

[Descrição]

---

# 7. Diferenciais do Projeto

## D001 - Opportunity Score

[Descrição]

## D002 - Estimativa de Impacto

[Descrição]

## D003 - Próxima Melhor Ação

[Descrição]

## D004 - Mapeamento de Stakeholders

[Descrição]

## D005 - Diferencial Competitivo

[Descrição]

---

# 8. Stack Tecnológica

## Backend

[Descrição]

## Frontend

[Descrição]

## IA

[Descrição]

## Banco de Dados

[Descrição]

## Infraestrutura

[Descrição]

---

# 9. Roadmap

## MVP

[Descrição]

## V1

[Descrição]

## V2

[Descrição]

## Melhorias Futuras

[Descrição]

---

# 10. Referências

[Adicionar referências]