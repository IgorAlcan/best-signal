"""Testes do núcleo de value betting (app/core/value.py)."""

import math

import pytest

from app.core import value


# --- implied_probability ---------------------------------------------------

def test_implied_probability_odd_2_eh_50_porcento():
    assert value.implied_probability(2.0) == pytest.approx(0.5)


def test_implied_probability_odd_4_eh_25_porcento():
    assert value.implied_probability(4.0) == pytest.approx(0.25)


def test_implied_probability_rejeita_odd_invalida():
    with pytest.raises(ValueError):
        value.implied_probability(1.0)  # odd <= 1.0 não faz sentido


# --- edge ------------------------------------------------------------------

def test_edge_positivo_quando_prob_maior_que_implicita():
    # prob 0.55 vs implícita 0.50 -> edge de 0.05
    assert value.edge(0.55, 2.0) == pytest.approx(0.05)


def test_edge_negativo_quando_prob_menor_que_implicita():
    # prob 0.40 vs implícita 0.50 -> edge negativo
    assert value.edge(0.40, 2.0) == pytest.approx(-0.10)


# --- expected_value --------------------------------------------------------

def test_ev_zero_quando_prob_igual_implicita():
    # prob 0.50 e odd 2.00 -> jogo "justo", EV = 0
    assert value.expected_value(0.5, 2.0) == pytest.approx(0.0)


def test_ev_positivo_em_value_bet():
    # prob 0.55, odd 2.00 -> EV = 0.55*2 - 1 = 0.10
    assert value.expected_value(0.55, 2.0) == pytest.approx(0.10)


def test_ev_negativo_sem_valor():
    # prob 0.45, odd 2.00 -> EV = 0.45*2 - 1 = -0.10
    assert value.expected_value(0.45, 2.0) == pytest.approx(-0.10)


# --- kelly_fraction --------------------------------------------------------

def test_kelly_zero_sem_valor():
    # EV <= 0 -> Kelly não recomenda apostar
    assert value.kelly_fraction(0.45, 2.0) == 0.0


def test_kelly_positivo_em_value_bet():
    # f* = EV / (odds - 1) = 0.10 / 1.0 = 0.10
    assert value.kelly_fraction(0.55, 2.0) == pytest.approx(0.10)


def test_kelly_nunca_passa_de_1():
    # Mesmo num caso extremo, a fração fica em [0, 1]
    f = value.kelly_fraction(0.99, 5.0)
    assert 0.0 <= f <= 1.0


# --- is_value_bet ----------------------------------------------------------

def test_is_value_bet_true_acima_do_limiar():
    assert value.is_value_bet(0.55, 2.0, min_ev=0.05) is True


def test_is_value_bet_false_abaixo_do_limiar():
    # EV = 0.02, mas exigimos >= 0.05
    assert value.is_value_bet(0.51, 2.0, min_ev=0.05) is False


# --- validação de probabilidade -------------------------------------------

@pytest.mark.parametrize("prob_invalida", [0.0, 1.0, -0.1, 1.5])
def test_funcoes_rejeitam_probabilidade_fora_de_0_1(prob_invalida):
    with pytest.raises(ValueError):
        value.expected_value(prob_invalida, 2.0)
