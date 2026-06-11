"""
Rotas da API (FastAPI APIRouter).

A camada de rotas é fina: cada endpoint só traduz HTTP em chamada de serviço e
devolve o resultado. Toda a regra de negócio mora em app/services.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.schemas import (
    AlertPreview,
    CalculateEVRequest,
    CalculateEVResponse,
    StakeRequest,
    StakeResponse,
)
from app.config import MIN_EV_PERCENT, PROJECT_NAME
from app.services import alert_service, bankroll_service, ev_calculator, odds_service

router = APIRouter()


@router.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Checagem de saúde da API."""
    return {"status": "ok", "project": PROJECT_NAME}


@router.get("/odds", tags=["odds"])
def get_odds() -> list[dict]:
    """Todos os eventos simulados, enriquecidos com EV."""
    odds = odds_service.load_sample_odds()
    return odds_service.enrich_odds_with_ev(odds, MIN_EV_PERCENT)


@router.get("/value-bets", tags=["odds"])
def get_value_bets(
    min_ev: float = Query(MIN_EV_PERCENT, description="EV mínimo em % (ex.: 3.0)"),
) -> list[dict]:
    """Somente as oportunidades com EV maior ou igual a `min_ev`."""
    odds = odds_service.load_sample_odds()
    return odds_service.get_value_bets(odds, min_ev)


@router.post("/calculate-ev", response_model=CalculateEVResponse, tags=["ev"])
def calculate_ev(payload: CalculateEVRequest) -> CalculateEVResponse:
    """Calcula EV, probabilidade implícita e status de value bet para um par de odds."""
    return CalculateEVResponse(
        bookmaker_odds=payload.bookmaker_odds,
        sharp_odds=payload.sharp_odds,
        implied_probability=ev_calculator.implied_probability(payload.bookmaker_odds),
        ev_percent=ev_calculator.calculate_ev(payload.bookmaker_odds, payload.sharp_odds),
        is_value_bet=ev_calculator.is_value_bet(
            payload.bookmaker_odds, payload.sharp_odds, payload.min_ev
        ),
    )


@router.get("/alerts", response_model=list[AlertPreview], tags=["alerts"])
def get_alerts(
    min_ev: float = Query(MIN_EV_PERCENT, description="EV mínimo em % (ex.: 3.0)"),
) -> list[AlertPreview]:
    """Pré-visualização SIMULADA dos alertas das value bets atuais.

    Nenhuma mensagem é enviada (sem Telegram, token ou rede): apenas montamos o
    texto que um sistema real dispararia.
    """
    odds = odds_service.load_sample_odds()
    value_bets = odds_service.get_value_bets(odds, min_ev)
    return [
        AlertPreview(
            sport=bet["sport"],
            event=bet["event"],
            selection=bet["selection"],
            ev_percent=bet["ev_percent"],
            message=alert_service.build_alert_message(bet),
        )
        for bet in value_bets
    ]


@router.post("/suggest-stake", response_model=StakeResponse, tags=["bankroll"])
def suggest_stake(payload: StakeRequest) -> StakeResponse:
    """Sugere o valor da aposta como percentual fixo da banca (gestão de risco)."""
    return StakeResponse(
        bankroll=payload.bankroll,
        risk_percent=payload.risk_percent,
        stake=bankroll_service.suggest_stake(payload.bankroll, payload.risk_percent),
    )
