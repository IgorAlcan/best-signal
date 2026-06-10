"""
Serviço de value betting — a "cola" entre os dados e a matemática do núcleo.

Fluxo:
  jogos (mock) ──> para cada resultado, calcula EV/edge/Kelly ──>
  filtra os que têm valor (EV >= min_ev) ──> ordena do melhor pro pior.

É aqui que aplicamos os filtros de negócio (limiar de EV, odd mínima/máxima) e
montamos a explicação em português de cada sinal. A camada de API só chama este
serviço; ela não conhece a matemática.
"""

from __future__ import annotations

from app.core import value
from app.data import mock
from app.models.schemas import Match, Outcome, ValueBet

# Limiares padrão (margem de segurança porque nossa `fair_prob` tem incerteza).
DEFAULT_MIN_EV = 0.03   # só aceita EV >= 3%
DEFAULT_MIN_ODDS = 1.30  # evita odds muito baixas (pouco retorno)
DEFAULT_MAX_ODDS = 6.00  # evita azarões extremos (estimativa pouco confiável)


def find_value_bets(
    matches: list[Match] | None = None,
    min_ev: float = DEFAULT_MIN_EV,
    min_odds: float = DEFAULT_MIN_ODDS,
    max_odds: float = DEFAULT_MAX_ODDS,
) -> list[ValueBet]:
    """Encontra e ranqueia as value bets dos jogos informados.

    Se `matches` for None, usa os dados mock. Devolve a lista ordenada por EV
    decrescente (melhor oportunidade primeiro).
    """
    if matches is None:
        matches = mock.get_matches()

    bets: list[ValueBet] = []
    for match in matches:
        for outcome in match.outcomes:
            bet = _evaluate(match, outcome, min_ev, min_odds, max_odds)
            if bet is not None:
                bets.append(bet)

    # Ordena do maior EV para o menor: a melhor oportunidade aparece primeiro.
    bets.sort(key=lambda b: b.ev, reverse=True)
    return bets


def _evaluate(
    match: Match,
    outcome: Outcome,
    min_ev: float,
    min_odds: float,
    max_odds: float,
) -> ValueBet | None:
    """Avalia um único resultado. Devolve um ValueBet se passar nos filtros, senão None."""
    # Filtro de faixa de odds antes de calcular qualquer coisa.
    if not (min_odds <= outcome.odds <= max_odds):
        return None

    ev = value.expected_value(outcome.fair_prob, outcome.odds)
    if ev < min_ev:
        return None  # sem valor suficiente

    implied = value.implied_probability(outcome.odds)
    edge = value.edge(outcome.fair_prob, outcome.odds)
    kelly = value.kelly_fraction(outcome.fair_prob, outcome.odds)

    return ValueBet(
        match_id=match.id,
        sport=match.sport,
        league=match.league,
        event=f"{match.home} vs {match.away}",
        selection=outcome.name,
        start_time=match.start_time,
        odds=round(outcome.odds, 2),
        fair_prob=round(outcome.fair_prob, 4),
        implied_prob=round(implied, 4),
        edge=round(edge, 4),
        ev=round(ev, 4),
        kelly=round(kelly, 4),
        explanation=_explain(outcome, implied, edge, ev),
    )


def _explain(outcome: Outcome, implied: float, edge: float, ev: float) -> str:
    """Monta uma explicação curta e honesta do sinal, em português.

    A IA/sistema só EXPLICA o número — não promete acerto nem lucro.
    """
    return (
        f"Estimamos {outcome.fair_prob:.0%} de chance para '{outcome.name}', "
        f"enquanto a odd {outcome.odds:.2f} embute apenas {implied:.0%}. "
        f"Isso dá {edge:+.1%} de vantagem e EV de {ev:+.1%} por unidade. "
        f"EV positivo é estatística de longo prazo, não garantia de acerto."
    )
