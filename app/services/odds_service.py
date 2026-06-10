"""
Serviço de odds — carrega os dados simulados e os enriquece com os cálculos.

É a camada que junta os dados (JSON) com a matemática (ev_calculator). A API e o
dashboard consomem este serviço; nenhum dos dois conhece os detalhes do cálculo.

100% offline: os dados vêm de um arquivo local. Nenhuma API externa, chave ou
serviço pago é usado.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.services import ev_calculator

# Caminho do arquivo de dados simulados (app/data/sample_odds.json).
_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_odds.json"


def load_sample_odds() -> list[dict]:
    """Carrega os eventos simulados do arquivo JSON."""
    with open(_DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def enrich_odds_with_ev(odds: list[dict], min_ev: float = 3.0) -> list[dict]:
    """Acrescenta a cada evento: implied_probability, ev_percent e is_value_bet.

    Não altera os dicts originais (trabalha em cópias), para evitar efeitos
    colaterais em quem passou a lista.
    """
    enriched: list[dict] = []
    for event in odds:
        item = dict(event)  # cópia rasa: não mexe no original
        item["implied_probability"] = ev_calculator.implied_probability(event["bookmaker_odds"])
        item["ev_percent"] = ev_calculator.calculate_ev(event["bookmaker_odds"], event["sharp_odds"])
        item["is_value_bet"] = ev_calculator.is_value_bet(
            event["bookmaker_odds"], event["sharp_odds"], min_ev
        )
        enriched.append(item)
    return enriched


def get_value_bets(odds: list[dict], min_ev: float = 3.0) -> list[dict]:
    """Devolve só os eventos com valor (is_value_bet = True), já enriquecidos.

    Aceita a lista crua: enriquece internamente e depois filtra.
    """
    return [e for e in enrich_odds_with_ev(odds, min_ev) if e["is_value_bet"]]
