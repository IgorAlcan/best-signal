"""
Modelos de dados (schemas) do projeto, usando Pydantic.

Pydantic valida os dados automaticamente e gera o JSON da API. Separar os
"modelos de entrada" (o que vem dos dados/mock) dos "modelos de saída" (o que a
API devolve já calculado) deixa claro o que é dado bruto e o que é resultado.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Outcome(BaseModel):
    """Um resultado possível de um jogo (ex.: vitória do mandante).

    - `odds`: odd decimal oferecida pela casa de apostas.
    - `fair_prob`: NOSSA estimativa de probabilidade "justa" (o "modelo").
      Num projeto real viria de um modelo estatístico; aqui é mock curado.
    """

    name: str = Field(..., description="Nome do resultado, ex.: 'Sinner'")
    odds: float = Field(..., gt=1.0, description="Odd decimal da casa")
    fair_prob: float = Field(..., gt=0.0, lt=1.0, description="Probabilidade justa estimada")


class Match(BaseModel):
    """Um jogo/partida com seus resultados possíveis (dado de entrada/mock)."""

    id: str
    sport: str = Field(..., description="Esporte: tennis, soccer, basketball")
    league: str
    home: str
    away: str
    start_time: str = Field(..., description="Início do jogo em ISO 8601 (UTC)")
    outcomes: list[Outcome]


class ValueBet(BaseModel):
    """Resultado calculado: uma seleção com valor positivo (modelo de saída).

    Tudo aqui já é derivado de um `Outcome` + a matemática do núcleo. É o que a
    API entrega e o dashboard exibe.
    """

    match_id: str
    sport: str
    league: str
    event: str = Field(..., description="Confronto, ex.: 'Sinner vs Alcaraz'")
    selection: str = Field(..., description="O resultado apostado, ex.: 'Sinner'")
    start_time: str

    odds: float
    fair_prob: float
    implied_prob: float = Field(..., description="Probabilidade embutida na odd (1/odd)")
    edge: float = Field(..., description="fair_prob − implied_prob")
    ev: float = Field(..., description="Valor esperado por unidade apostada")
    kelly: float = Field(..., description="Fração de Kelly sugerida (banca)")

    explanation: str = Field(..., description="Explicação em PT do porquê do sinal")
