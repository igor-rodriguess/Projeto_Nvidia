# NVIDIA Startup AI Radar

Plataforma multiagente de inteligência artificial para identificação, análise e recomendação de tecnologias NVIDIA para startups brasileiras AI-native.

## Objetivo

Apoiar a NVIDIA na identificação de startups brasileiras com uso intensivo de IA, avaliando sua maturidade técnica, possíveis gaps de infraestrutura e oportunidades de adoção de tecnologias NVIDIA.

## Funcionalidades previstas

- Busca de startups brasileiras por nome, setor ou palavra-chave.
- Coleta de informações públicas.
- Extração estruturada de dados.
- Classificação da maturidade AI-native.
- Identificação de gaps técnicos.
- Consulta a uma base RAG com tecnologias NVIDIA.
- Recomendação personalizada de tecnologias NVIDIA.
- Geração de briefing executivo.
- Score de oportunidade para abordagem comercial.

## Diferenciais

- Estimativa de impacto da tecnologia NVIDIA.
- Priorização de startups com maior fit.
- Sugestão de próxima ação para o time NVIDIA.
- Identificação de contatos públicos de founders ou decisores.

## Pipeline atual

```text
Cubo Itaú
  -> dados raw
  -> dados processed
  -> dados curated
  -> Search Planner Agent
  -> Scraper Agent
  -> Evidence Validator Agent
  -> AI Maturity Classifier Agent
  -> NVIDIA Recommender RAG
```

O Evidence Validator Agent audita os resultados coletados, remove URLs quebradas,
homônimos e menções irrelevantes, classifica a credibilidade das fontes e identifica
evidências de IA. O resultado consolidado será a entrada do futuro AI Maturity
Classifier.

O AI Maturity Classifier usa somente evidências com confiança mínima de 0,4 para
classificar a startup como `AI-native`, `AI-enabled`, `API-consumer` ou `Non-AI`.
Ele também registra nível de maturidade, tecnologias encontradas, limitações e as
fontes exatas que sustentam a decisão.

Para investigar uma startup da base curated:

```bash
cd backend
python scripts/investigar_startup_ia.py data/curated/_cubo/<arquivo>.json "Nome da Startup"
```

As coletas brutas são salvas em `backend/data/raw/_evidencias/` e as evidências
validadas em `backend/data/processed/_evidencias/`.
As classificações são salvas em `backend/data/curated/_maturidade_ia/`.

## Execução local

```bash
docker compose up -d qdrant searxng
cd backend
python -m pip install -r requirements.txt
```

Crie `backend/.env` a partir de `backend/.env.example`. O modo padrão usa embeddings
FastEmbed locais e geração determinística, portanto não exige uma chave OpenAI. A
chave Firecrawl continua opcional para páginas que dependem de JavaScript.

Para ingerir a documentação oficial NVIDIA:

```bash
python scripts/ingest_nvidia_knowledge.py
```

Para executar os cinco agentes:

```bash
python scripts/run_enterprise_pipeline.py "Nome da Startup" "https://startup.com"
```

O resultado contém `trace` com a saída, duração, tentativas, tokens e erros de cada
agente. Resultados intermediários são cacheados em `backend/data/cache/pipeline/`.

Mais detalhes estão em [docs/rag_architecture.md](docs/rag_architecture.md) e
[docs/operations.md](docs/operations.md).
