# Retenção de Dados e LGPD

Política técnica padrão:

- traces completos no Storage: 90 dias;
- arquivos brutos de scraping: 180 dias;
- cache local da pipeline: 30 dias;
- cache web: até a expiração registrada;
- janelas de rate limit: 2 dias;
- tokens revogados: até a expiração do token.

O serviço nunca segue links simbólicos e valida que cada arquivo permanece dentro
de `data/raw` ou `data/cache/pipeline`. O modo padrão é dry-run:

```bash
cd backend
python scripts/apply_retention.py
python scripts/apply_retention.py --execute
```

A aprovação jurídica da política continua obrigatória antes de produção. O job
técnico implementa minimização e descarte, mas não substitui definição de base legal,
canal de atendimento ao titular ou registro das atividades de tratamento.
