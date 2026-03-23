from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_root():
    r = client.get("/")
    assert r.status_code == 200


def test_login_success():
    r = client.post("/api/auth/login", json={"username": "admin", "password": "123456"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_market_data_and_process():
    r = client.get("/api/data/market", params={"symbol": "000001", "interval": "1d", "source": "mock"})
    assert r.status_code == 200
    payload = r.json()
    assert payload["symbol"] == "000001"
    assert isinstance(payload["data"], list)
    assert len(payload["data"]) > 0

    r2 = client.post("/api/data/process", json={"data": payload["data"]})
    assert r2.status_code == 200
    out = r2.json()
    assert "processed_data" in out
    assert "summary" in out


def test_backtest_flow():
    r = client.post(
        "/api/backtest",
        json={"strategy_id": 1, "start_date": "2026-01-01", "end_date": "2026-01-31", "parameters": {}},
    )
    assert r.status_code == 200
    b = r.json()
    assert "id" in b

    r2 = client.get(f"/api/backtest/{b['id']}/analysis")
    assert r2.status_code == 200
    a = r2.json()
    assert a["backtest_id"] == b["id"]
