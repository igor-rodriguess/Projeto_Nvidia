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
```

O Evidence Validator Agent audita os resultados coletados, remove URLs quebradas,
homônimos e menções irrelevantes, classifica a credibilidade das fontes e identifica
evidências de IA. O resultado consolidado será a entrada do futuro AI Maturity
Classifier.

Para investigar uma startup da base curated:

```bash
cd backend
python scripts/investigar_startup_ia.py data/curated/_cubo/<arquivo>.json "Nome da Startup"
```

As coletas brutas são salvas em `backend/data/raw/_evidencias/` e as evidências
validadas em `backend/data/processed/_evidencias/`.
