# Revisão de Aceitação

A amostra deve ser gerada somente quando houver pelo menos 10 itens concluídos com
`pipeline_run_id`:

```bash
cd backend
python scripts/generate_acceptance_sample.py <batch_id> --size 10 --seed 20260627
```

Um revisor deve preencher:

- `classification_agreement`: `yes` ou `no`.
- `evidence_agreement`: `yes` ou `no`.
- `recommendation_applicable`: `yes` ou `no`.
- `briefing_utility_1_5`: inteiro de 1 a 5.
- `reviewer` e `review_notes`.

A Onda 1 exige pelo menos 90% de concordância nos três critérios binários. O arquivo
preenchido deve permanecer versionado sem dados pessoais do revisor além do nome ou
identificador profissional autorizado.

Durante a execução, `--allow-incomplete` pode gerar uma amostra preliminar. Depois
que o lote ficar terminal, regenere sem essa flag e publique também o relatório:

```bash
python scripts/generate_batch_acceptance_report.py <batch_id>
```

## Auditoria automatica

Para validar todos os artefatos persistidos, inclusive quando as tabelas ultrapassam
o limite de 1000 linhas da Data API:

```bash
cd backend
python scripts/audit_batch_quality.py <batch_id>
```

O comando falha quando encontra startup sem fonte rastreavel, evidencia qualificada,
trace, classificacao, recomendacao fundamentada, impacto ou briefing. A aprovacao
automatica nao substitui a revisao humana da amostra.
