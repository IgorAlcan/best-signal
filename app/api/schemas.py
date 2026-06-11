"""
Schemas Pydantic da API: o "contrato" de entrada e saída do endpoint de EV.

Separar os schemas da API dos modelos de domínio (app/models.py) deixa claro o
que é forma de dado interno e o que é contrato público da API.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CalculateEVRequest(BaseModel):
    """Corpo do POST /calculate-ev."""

    # gt=1: odds inválidas (<= 1) são rejeitadas pelo FastAPI com HTTP 422.
    bookmaker_odds: float = Field(..., gt=1, description="Odd decimal da casa comum")
    sharp_odds: float = Field(..., gt=1, description="Odd decimal da casa sharp (referência)")
    min_ev: float = Field(3.0, description="EV mínimo em % para considerar value bet")


class CalculateEVResponse(BaseModel):
    """Resposta do POST /calculate-ev."""

    bookmaker_odds: float
    sharp_odds: float
    implied_probability: float = Field(..., description="Prob. implícita da casa comum (1/bookmaker_odds)")
    ev_percent: float = Field(..., description="Valor esperado em %")
    is_value_bet: bool


class StakeRequest(BaseModel):
    """Corpo do POST /suggest-stake (gestão de banca por percentual fixo)."""

    # gt=0 / le=100: valores fora da faixa são rejeitados com HTTP 422.
    bankroll: float = Field(..., gt=0, description="Tamanho da banca")
    risk_percent: float = Field(1.0, gt=0, le=100, description="Percentual da banca por aposta")


class StakeResponse(BaseModel):
    """Resposta do POST /suggest-stake."""

    bankroll: float
    risk_percent: float
    stake: float = Field(..., description="Valor sugerido para a aposta")


class AlertPreview(BaseModel):
    """Pré-visualização (simulada) de um alerta de value bet."""

    sport: str
    event: str
    selection: str
    ev_percent: float
    message: str = Field(..., description="Mensagem de alerta simulada (não enviada a lugar nenhum)")
