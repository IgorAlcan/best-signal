"""Testes do serviço de alerta simulado (app/services/alert_service.py)."""

from app.services import alert_service


def _exemplo_value_bet() -> dict:
    return {
        "sport": "tennis",
        "event": "Simulated Player A vs Simulated Player B",
        "market": "match_winner",
        "selection": "Simulated Player A",
        "bookmaker": "DemoBook",
        "bookmaker_odds": 2.10,
        "sharp_bookmaker": "SharpDemo",
        "sharp_odds": 1.85,
        "ev_percent": 13.51,
    }


def test_mensagem_contem_secoes_principais():
    msg = alert_service.build_alert_message(_exemplo_value_bet())
    assert "Sport:" in msg
    assert "Event:" in msg
    assert "EV:" in msg
    assert "Status:" in msg


def test_mensagem_usa_dados_do_evento():
    msg = alert_service.build_alert_message(_exemplo_value_bet())
    assert "Simulated Player A vs Simulated Player B" in msg
    assert "13.51%" in msg          # vem do ev_percent, não fixo no código
    assert "Match Winner" in msg    # market 'match_winner' humanizado
    assert "Tennis" in msg          # sport capitalizado
