"""
Modelos de domínio (Pydantic) que descrevem a forma dos dados de odds.

Dar um modelo explícito ao evento de odds tem valor real: documenta o schema do
`sample_odds.json`, valida os tipos e ainda serve de base para os schemas da API.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class OddsEvent(BaseModel):
    """Um evento de odds simulado, como vem do sample_odds.json (dado cru)."""

    sport: str = Field(..., description="Esporte: tennis, football, basketball")
    event: str = Field(..., description="Confronto, ex.: 'Simulated A vs Simulated B'")
    market: str = Field(..., description="Mercado, ex.: 'match_winner'")
    selection: str = Field(..., description="Seleção apostada")
    bookmaker: str = Field(..., description="Casa comum")
    bookmaker_odds: float = Field(..., gt=1, description="Odd decimal da casa comum")
    sharp_bookmaker: str = Field(..., description="Casa sharp (referência)")
    sharp_odds: float = Field(..., gt=1, description="Odd decimal da casa sharp")
    timestamp: str = Field(..., description="Momento da coleta (ISO 8601)")


class EnrichedOddsEvent(OddsEvent):
    """Um evento já enriquecido com os cálculos de value (dado de saída)."""

    implied_probability: float = Field(..., description="1 / bookmaker_odds")
    ev_percent: float = Field(..., description="Valor esperado em %")
    is_value_bet: bool = Field(..., description="EV >= limiar mínimo?")
