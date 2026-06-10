"""Testes da API FastAPI (app/main.py + app/api/routes.py)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_retorna_200():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["project"] == "ValueBetAI Portfolio Demo"


def test_odds_retorna_lista_enriquecida():
    r = client.get("/odds")
    assert r.status_code == 200
    odds = r.json()
    assert isinstance(odds, list)
    assert len(odds) >= 12
    assert "ev_percent" in odds[0]
    assert "is_value_bet" in odds[0]


def test_value_bets_retorna_lista():
    r = client.get("/value-bets")
    assert r.status_code == 200
    bets = r.json()
    assert isinstance(bets, list)
    assert all(b["is_value_bet"] for b in bets)


def test_value_bets_respeita_min_ev():
    r = client.get("/value-bets", params={"min_ev": 10.0})
    assert r.status_code == 200
    assert all(b["ev_percent"] >= 10.0 for b in r.json())


def test_calculate_ev_retorna_ev_correto():
    r = client.post("/calculate-ev", json={"bookmaker_odds": 2.10, "sharp_odds": 1.85})
    assert r.status_code == 200
    body = r.json()
    assert body["ev_percent"] == 13.51
    assert body["is_value_bet"] is True
    assert body["implied_probability"] == 0.4762  # 1 / 2.10 (odd da casa comum)


def test_calculate_ev_valida_odds_invalidas():
    # odds <= 1 são rejeitadas pelo schema Pydantic -> HTTP 422
    r = client.post("/calculate-ev", json={"bookmaker_odds": 1.0, "sharp_odds": 1.85})
    assert r.status_code == 422
