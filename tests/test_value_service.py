"""Testes do serviço de value betting (app/services/value_service.py)."""

from app.data import mock
from app.models.schemas import Match, Outcome
from app.services import value_service as svc


def test_encontra_alguma_value_bet_no_mock():
    bets = svc.find_value_bets()
    assert len(bets) > 0


def test_resultado_vem_ordenado_por_ev_decrescente():
    bets = svc.find_value_bets()
    evs = [b.ev for b in bets]
    assert evs == sorted(evs, reverse=True)


def test_todas_as_bets_tem_ev_acima_do_limiar():
    min_ev = 0.05
    bets = svc.find_value_bets(min_ev=min_ev)
    assert all(b.ev >= min_ev for b in bets)


def test_jogo_sem_valor_nao_gera_bet():
    # Jogo onde fair_prob == implícita -> EV 0, abaixo de qualquer limiar > 0
    sem_valor = [
        Match(
            id="t-000",
            sport="tennis",
            league="ATP",
            home="A",
            away="B",
            start_time="2026-06-11T18:00:00Z",
            outcomes=[
                Outcome(name="A", odds=2.0, fair_prob=0.50),
                Outcome(name="B", odds=2.0, fair_prob=0.50),
            ],
        )
    ]
    assert svc.find_value_bets(matches=sem_valor) == []


def test_filtro_de_faixa_de_odds_descarta_odd_alta():
    # Mesmo com EV alto, odd acima do teto é descartada (estimativa pouco confiável)
    azarao_extremo = [
        Match(
            id="t-001",
            sport="soccer",
            league="X",
            home="A",
            away="B",
            start_time="2026-06-11T18:00:00Z",
            outcomes=[
                # EV positivo, mas odd 10.0 > max_odds padrão (6.0)
                Outcome(name="A", odds=10.0, fair_prob=0.15),
                Outcome(name="B", odds=1.10, fair_prob=0.85),
            ],
        )
    ]
    bets = svc.find_value_bets(matches=azarao_extremo)
    assert all(b.odds <= svc.DEFAULT_MAX_ODDS for b in bets)


def test_explicacao_menciona_postura_responsavel():
    bets = svc.find_value_bets()
    # Todo sinal deixa claro que não é garantia
    assert all("não garantia" in b.explanation or "não garante" in b.explanation
               or "não garantia de acerto" in b.explanation for b in bets)


def test_get_matches_devolve_copia_isolada():
    a = mock.get_matches()
    a[0].outcomes[0].odds = 999.0
    b = mock.get_matches()
    assert b[0].outcomes[0].odds != 999.0
