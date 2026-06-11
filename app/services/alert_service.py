"""
Serviço de alerta SIMULADO.

Monta a mensagem de texto que, num sistema real, seria enviada a um canal (ex.:
Telegram). Aqui ela é apenas RETORNADA como string.

IMPORTANTE: não envia nada de verdade, não usa token, não acessa a internet.
"""

from __future__ import annotations


def build_alert_message(value_bet: dict) -> str:
    """Monta a mensagem de alerta a partir de um evento já enriquecido.

    Espera que `value_bet` tenha a chave `ev_percent` (vinda do odds_service).
    A mensagem é construída a partir dos dados — nada é fixo no código.
    """
    sport = str(value_bet["sport"]).title()
    market = _humanize(str(value_bet["market"]))

    return (
        "🚨 BestSignal Alert\n"
        "\n"
        f"Sport: {sport}\n"
        f"Event: {value_bet['event']}\n"
        f"Market: {market}\n"
        f"Selection: {value_bet['selection']}\n"
        "\n"
        f"Bookmaker Odds: {value_bet['bookmaker_odds']}\n"
        f"Sharp Odds: {value_bet['sharp_odds']}\n"
        f"EV: {value_bet['ev_percent']}%\n"
        "\n"
        "Status: Positive EV detected"
    )


def _humanize(market: str) -> str:
    """Transforma 'match_winner' em 'Match Winner' para a mensagem."""
    return market.replace("_", " ").title()
