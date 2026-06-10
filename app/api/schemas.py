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
