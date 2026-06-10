"""Testes do cálculo de EV (app/services/ev_calculator.py)."""

import pytest

from app.services import ev_calculator as ev


# --- implied_probability ---------------------------------------------------

def test_implied_probability_odds_validas():
    assert ev.implied_probability(1.85) == 0.5405
    assert ev.implied_probability(2.0) == 0.5


def test_implied_probability_odds_invalidas():
    with pytest.raises(ValueError):
        ev.implied_probability(1.0)
    with pytest.raises(ValueError):
        ev.implied_probability(0.5)


# --- calculate_ev ----------------------------------------------------------

def test_calculate_ev_positivo():
    # bookmaker 2.10, sharp 1.85 -> +13.51%
    assert ev.calculate_ev(2.10, 1.85) == 13.51


def test_calculate_ev_negativo():
    # bookmaker 1.80, sharp 1.90 -> negativo
    assert ev.calculate_ev(1.80, 1.90) < 0


def test_calculate_ev_valida_odds():
    with pytest.raises(ValueError):
        ev.calculate_ev(1.0, 1.85)
    with pytest.raises(ValueError):
        ev.calculate_ev(2.10, 1.0)


# --- is_value_bet ----------------------------------------------------------

def test_is_value_bet_true():
    # EV de +13.51% >= 3.0
    assert ev.is_value_bet(2.10, 1.85) is True


def test_is_value_bet_false():
    # EV negativo < 3.0
    assert ev.is_value_bet(1.80, 1.90) is False


def test_is_value_bet_respeita_limiar_customizado():
    # EV de +2.5% (2.05/2.00) fica abaixo de min_ev=3.0
    assert ev.is_value_bet(2.05, 2.00, min_ev=3.0) is False
    # mas passa com um limiar menor
    assert ev.is_value_bet(2.05, 2.00, min_ev=2.0) is True
