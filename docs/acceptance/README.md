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
