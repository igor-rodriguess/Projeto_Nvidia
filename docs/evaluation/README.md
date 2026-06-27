# Avaliação do Pipeline

O conjunto ouro é independente das respostas produzidas pelo pipeline. Um revisor
humano deve preencher pelo menos dez casos com classificação, maturidade, evidências
aceitas, tecnologias NVIDIA esperadas e utilidade do briefing.

Enquanto `status` for `draft`, o harness recusa gerar métricas oficiais. Depois da
revisão, atualize a versão, registre o commit e a versão dos documentos, preencha
`reviewed_by` em todos os casos e altere o status para `approved`.

```bash
cd backend
python scripts/prepare_golden_set.py ../docs/acceptance/revisao_amostra_10.csv
python scripts/evaluate_golden_set.py
```

O relatório mede acurácia de classificação, erro absoluto de maturidade, precisão e
recall de evidências, precisão top-3 das recomendações, groundedness das citações e
utilidade humana do briefing. A execução retorna código `2` quando algum limiar não
é atingido, permitindo uso futuro no CI.
