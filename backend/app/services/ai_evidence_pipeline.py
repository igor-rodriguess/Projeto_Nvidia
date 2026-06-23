from __future__ import annotations

from pathlib import Path
from typing import Any

import requests

from app.agents.scraper_agent import executar_scraper_agent, salvar_resultado_scraper
from app.agents.search_planner_agent import planejar_busca_ia_startup


def executar_pipeline_investigacao_ia(
    startup: dict[str, Any],
    contexto: str | None = None,
    session: requests.Session | None = None,
    delay_seconds: float = 2.0,
    respect_robots: bool = True,
    salvar_resultado: bool = True,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    plano = planejar_busca_ia_startup(startup, contexto=contexto)
    coleta = executar_scraper_agent(
        plano,
        session=session,
        delay_seconds=delay_seconds,
        respect_robots=respect_robots,
    )

    output_path = None
    if salvar_resultado:
        output_path = salvar_resultado_scraper(coleta, output_dir=output_dir)

    return {
        "startup": plano["startup"],
        "status": coleta["status"],
        "plano": plano,
        "coleta": coleta,
        "arquivo_saida": str(output_path) if output_path else None,
    }
