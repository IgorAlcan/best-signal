"""Testes do serviço de odds (app/services/odds_service.py)."""

from app.models import OddsEvent
from app.services import odds_service


def test_carrega_sample_odds():
    odds = odds_service.load_sample_odds()
    assert isinstance(odds, list)
    assert len(odds) >= 12


def test_sample_odds_tem_schema_valido():
    # Cada evento deve bater com o modelo OddsEvent (valida tipos e odds > 1).
    for event in odds_service.load_sample_odds():
        OddsEvent(**event)  # levanta se inválido


def test_enriquecimento_adiciona_campos():
    odds = odds_service.load_sample_odds()
    enriched = odds_service.enrich_odds_with_ev(odds)
    for item in enriched:
        assert "implied_probability" in item
        assert "ev_percent" in item
        assert "is_value_bet" in item


def test_enriquecimento_nao_altera_original():
    odds = odds_service.load_sample_odds()
    odds_service.enrich_odds_with_ev(odds)
    assert "ev_percent" not in odds[0]  # o dict original continua intacto


def test_filtro_de_value_bets():
    odds = odds_service.load_sample_odds()
    value_bets = odds_service.get_value_bets(odds, min_ev=3.0)
    assert len(value_bets) > 0
    assert all(b["is_value_bet"] for b in value_bets)
    assert all(b["ev_percent"] >= 3.0 for b in value_bets)
