"""
Dados mock (de mentira) para a demo rodar sem nenhuma chave de API.

Por que curado e fixo, em vez de aleatório?
- A demo fica estável (mesmos números a cada execução) — bom para screenshots,
  testes e CI.
- Dá pra montar de propósito uma mistura realista: alguns jogos COM valor e
  outros SEM, pra mostrar que o filtro de fato separa os dois casos.

Cada jogo tem `outcomes` com `fair_prob` somando ~1.0 (nossa distribuição de
probabilidade) e `odds` da casa cuja implícita soma > 1.0 (a margem da casa).
Onde `fair_prob > 1/odds`, existe value.

Num sistema real este módulo seria trocado por um coletor de odds de verdade
(ex.: The Odds API) — a interface `get_matches()` continuaria a mesma.
"""

from __future__ import annotations

from app.models.schemas import Match, Outcome


# Conjunto curado de jogos. Datas fixas e no futuro (relativo à demo) só para
# parecerem "próximos jogos"; não influenciam os cálculos.
_MATCHES: list[Match] = [
    Match(
        id="ten-001",
        sport="tennis",
        league="ATP",
        home="Sinner",
        away="Alcaraz",
        start_time="2026-06-11T18:00:00Z",
        outcomes=[
            # VALUE: achamos 58%, a casa precifica ~54% (odd 1.85) -> EV +7%
            Outcome(name="Sinner", odds=1.85, fair_prob=0.58),
            Outcome(name="Alcaraz", odds=2.10, fair_prob=0.42),
        ],
    ),
    Match(
        id="ten-002",
        sport="tennis",
        league="WTA",
        home="Swiatek",
        away="Sabalenka",
        start_time="2026-06-11T20:30:00Z",
        outcomes=[
            # SEM value: nossa prob bate com a implícita; mercado eficiente
            Outcome(name="Swiatek", odds=1.66, fair_prob=0.60),
            Outcome(name="Sabalenka", odds=2.30, fair_prob=0.40),
        ],
    ),
    Match(
        id="bas-001",
        sport="basketball",
        league="NBA",
        home="Celtics",
        away="Nuggets",
        start_time="2026-06-12T00:00:00Z",
        outcomes=[
            # VALUE forte no azarão: achamos 46%, casa precifica ~40% (odd 2.50)
            Outcome(name="Celtics", odds=1.55, fair_prob=0.54),
            Outcome(name="Nuggets", odds=2.50, fair_prob=0.46),
        ],
    ),
    Match(
        id="soc-001",
        sport="soccer",
        league="Brasileirão",
        home="Flamengo",
        away="Palmeiras",
        start_time="2026-06-12T22:00:00Z",
        outcomes=[
            # Futebol tem 3 resultados (1/X/2). VALUE leve no empate.
            Outcome(name="Flamengo", odds=2.20, fair_prob=0.45),
            Outcome(name="Empate", odds=3.30, fair_prob=0.32),
            Outcome(name="Palmeiras", odds=3.60, fair_prob=0.23),
        ],
    ),
    Match(
        id="soc-002",
        sport="soccer",
        league="Premier League",
        home="Arsenal",
        away="Chelsea",
        start_time="2026-06-13T16:00:00Z",
        outcomes=[
            # SEM value em nenhum resultado (mercado eficiente / margem alta)
            Outcome(name="Arsenal", odds=1.90, fair_prob=0.50),
            Outcome(name="Empate", odds=3.50, fair_prob=0.27),
            Outcome(name="Chelsea", odds=4.20, fair_prob=0.23),
        ],
    ),
]


def get_matches() -> list[Match]:
    """Devolve a lista de jogos mock.

    Retorna cópias para o chamador não conseguir alterar o dataset por engano.
    """
    return [m.model_copy(deep=True) for m in _MATCHES]
