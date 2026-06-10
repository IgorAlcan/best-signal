"""Testes da API FastAPI (app/main.py), usando o TestClient."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_responde_ok():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_matches_lista_os_jogos():
    r = client.get("/api/matches")
    assert r.status_code == 200
    jogos = r.json()
    assert len(jogos) == 5
    assert jogos[0]["sport"] in {"tennis", "soccer", "basketball"}


def test_value_bets_vem_ordenado_por_ev():
    r = client.get("/api/value-bets")
    assert r.status_code == 200
    bets = r.json()
    assert len(bets) > 0
    evs = [b["ev"] for b in bets]
    assert evs == sorted(evs, reverse=True)


def test_value_bets_respeita_min_ev():
    r = client.get("/api/value-bets", params={"min_ev": 0.10})
    assert r.status_code == 200
    assert all(b["ev"] >= 0.10 for b in r.json())


def test_value_bets_filtra_por_esporte():
    r = client.get("/api/value-bets", params={"sport": "tennis"})
    assert r.status_code == 200
    assert all(b["sport"] == "tennis" for b in r.json())


def test_value_bets_rejeita_parametro_invalido():
    # min_odds deve ser > 1.0; 0.5 é inválido -> 422 do FastAPI
    r = client.get("/api/value-bets", params={"min_odds": 0.5})
    assert r.status_code == 422
