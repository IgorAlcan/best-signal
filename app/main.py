"""
API FastAPI do ValueBet AI (demo de portfólio).

Endpoints:
  GET /api/health      -> checagem de saúde (a API está de pé?)
  GET /api/matches     -> jogos crus (dados mock de entrada)
  GET /api/value-bets  -> value bets calculadas e ranqueadas (com filtros)

A camada de API é "fina": ela só recebe a requisição, chama o serviço e devolve
o resultado. Toda a lógica de value betting mora em app/services e app/core.

Rode localmente com:
    .venv/bin/uvicorn app.main:app --reload
E acesse a documentação interativa em http://127.0.0.1:8000/docs
"""

from __future__ import annotations

from fastapi import FastAPI, Query

from app.data import mock
from app.models.schemas import Match, ValueBet
from app.services import value_service as svc

app = FastAPI(
    title="ValueBet AI — Demo",
    description=(
        "Demo de portfólio: encontra apostas de valor (EV+) em dados mock. "
        "Não promete lucro nem garante acerto — apenas mede valor estatístico."
    ),
    version="0.1.0",
)


@app.get("/api/health", tags=["meta"])
def health() -> dict[str, str]:
    """Diz se a API está no ar. Útil para CI e monitoramento."""
    return {"status": "ok", "service": "valuebet-ai-demo"}


@app.get("/api/matches", response_model=list[Match], tags=["dados"])
def list_matches() -> list[Match]:
    """Lista os jogos crus (dados de entrada), antes de qualquer cálculo."""
    return mock.get_matches()


@app.get("/api/value-bets", response_model=list[ValueBet], tags=["value"])
def list_value_bets(
    min_ev: float = Query(svc.DEFAULT_MIN_EV, ge=0.0, description="EV mínimo (ex.: 0.03 = 3%)"),
    min_odds: float = Query(svc.DEFAULT_MIN_ODDS, gt=1.0, description="Odd decimal mínima"),
    max_odds: float = Query(svc.DEFAULT_MAX_ODDS, gt=1.0, description="Odd decimal máxima"),
    sport: str | None = Query(None, description="Filtra por esporte: tennis, soccer, basketball"),
) -> list[ValueBet]:
    """Devolve as value bets ranqueadas por EV (maior primeiro).

    Os parâmetros permitem ajustar os filtros sem mexer no código.
    """
    bets = svc.find_value_bets(min_ev=min_ev, min_odds=min_odds, max_odds=max_odds)
    if sport is not None:
        bets = [b for b in bets if b.sport == sport]
    return bets
