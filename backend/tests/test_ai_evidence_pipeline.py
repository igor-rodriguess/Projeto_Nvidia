from app.services.ai_evidence_pipeline import executar_pipeline_investigacao_ia
from tests.test_scraper_agent import FakeSession


def test_ai_evidence_pipeline_runs_planner_and_scraper_together(tmp_path):
    startup = {
        "nome": "Clara Pagamentos",
        "site": "https://clara.com.br",
        "categoria": "Financeiro",
        "descricao_curta": "Plataforma de gestão de gastos corporativos com automação.",
    }

    resultado = executar_pipeline_investigacao_ia(
        startup,
        session=FakeSession(),
        delay_seconds=0,
        respect_robots=False,
        salvar_resultado=True,
        output_dir=tmp_path,
    )

    assert resultado["startup"] == "Clara Pagamentos"
    assert resultado["status"] == "completo"
    assert resultado["plano"]["tarefas"]
    assert len(resultado["plano"]["tarefas"]) == len(resultado["plano"]["plano_consultas"])
    assert resultado["coleta"]["metricas"]["tarefas_executadas"] == len(resultado["plano"]["tarefas"])
    assert resultado["arquivo_saida"] is not None
