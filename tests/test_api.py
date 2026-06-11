"""Testes da API FastAPI (app/main.py + app/api/routes.py)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_retorna_200():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["project"] == "BestSignal Portfolio Demo"


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


def test_alerts_retorna_mensagens_simuladas():
    r = client.get("/alerts")
    assert r.status_code == 200
    alerts = r.json()
    assert len(alerts) > 0
    assert all("Alert" in a["message"] for a in alerts)
    assert all("Status:" in a["message"] for a in alerts)


def test_suggest_stake_calcula_valor():
    r = client.post("/suggest-stake", json={"bankroll": 1000, "risk_percent": 1.0})
    assert r.status_code == 200
    body = r.json()
    assert body["stake"] == 10.0


def test_suggest_stake_valida_bankroll_invalido():
    # bankroll <= 0 é rejeitado pelo schema Pydantic -> HTTP 422
    r = client.post("/suggest-stake", json={"bankroll": 0, "risk_percent": 1.0})
    assert r.status_code == 422
