from datetime import UTC, datetime, timedelta

from app.evaluation.batch_report import render_batch_report


def test_batch_report_calculates_progress_cost_and_gates():
    now = datetime.now(UTC)
    batch = {
        "id": "batch-1",
        "status": "completed",
        "total_items": 2,
        "started_at": (now - timedelta(seconds=10)).isoformat(),
        "finished_at": now.isoformat(),
    }
    items = [
        {
            "status": "completed",
            "pipeline_run_id": "run-1",
            "result_summary": {"classificacao": "AI-enabled"},
        },
        {
            "status": "failed",
            "last_error": "Falha controlada",
            "result_summary": {},
        },
    ]
    runs = [{"warnings": ["w"], "source_errors": ["s"], "errors": []}]
    usage = [
        {
            "units": 1,
            "cache_hit": False,
            "success": True,
            "estimated_cost_usd": 0.01,
        }
    ]

    report = render_batch_report(batch, items, runs, usage)

    assert "**Estado do relatorio:** FINAL" in report
    assert "Terminais: 2" in report
    assert "USD 0.0100" in report
    assert "[x] 50/50 em estado terminal" in report
    assert "[x] 100% dos terminais rastreaveis" in report
