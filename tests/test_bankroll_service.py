"""Testes do serviço de banca (app/services/bankroll_service.py)."""

import pytest

from app.services import bankroll_service as bk


def test_suggest_stake_valores_validos():
    assert bk.suggest_stake(1000, 1.0) == 10.0
    assert bk.suggest_stake(500, 2.0) == 10.0
    assert bk.suggest_stake(250.0, 1.0) == 2.5


def test_suggest_stake_usa_default_de_1_porcento():
    assert bk.suggest_stake(1000) == 10.0


def test_suggest_stake_bankroll_invalido():
    with pytest.raises(ValueError):
        bk.suggest_stake(0, 1.0)
    with pytest.raises(ValueError):
        bk.suggest_stake(-100, 1.0)


def test_suggest_stake_risk_percent_invalido():
    with pytest.raises(ValueError):
        bk.suggest_stake(1000, 0)
    with pytest.raises(ValueError):
        bk.suggest_stake(1000, 150)
