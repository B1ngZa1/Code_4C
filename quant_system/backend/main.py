from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI(
    title="个人量化分析与交易系统 API",
    description="个人量化分析与交易系统的后端API接口",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
FRONTEND_DIST_DIR = PROJECT_DIR / "frontend" / "dist"

_cors_origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

users = [
    {"id": 1, "username": "admin", "email": "admin@example.com", "password": "123456"}
]

mock_data_sources: list[dict[str, Any]] = [
    {"id": 1, "name": "模拟数据源", "type": "mock", "url": "", "api_key": "", "is_active": True}
]

mock_strategies: list[dict[str, Any]] = [
    {"id": 1, "name": "MACD策略", "type": "趋势", "description": "基于MACD指标的交易策略", "status": "active"},
    {"id": 2, "name": "RSI策略", "type": "震荡", "description": "基于RSI指标的交易策略", "status": "inactive"},
]

mock_backtests: list[dict[str, Any]] = []

mock_orders: list[dict[str, Any]] = []

@app.get("/")
def read_root():
    index = FRONTEND_DIST_DIR / "index.html"
    if index.is_file():
        return FileResponse(index)
    return {"ok": True, "message": "frontend_not_built"}

# 认证路由
@app.post("/api/auth/login")
def login(username: str = Body(...), password: str = Body(...)):
    user = next((u for u in users if u["username"] == username and u["password"] == password), None)
    if user:
        return {"access_token": "mock_token", "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

@app.post("/api/auth/register")
def register(username: str = Body(...), email: str = Body(...), password: str = Body(...)):
    if any(u["username"] == username for u in users):
        raise HTTPException(status_code=400, detail="Username already registered")
    if any(u["email"] == email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = {"id": len(users) + 1, "username": username, "email": email, "password": password}
    users.append(new_user)
    return {"message": "User created successfully"}

# 用户路由
@app.get("/api/user/me")
def get_current_user():
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "created_at": "2024-01-01T00:00:00"
    }

@app.get("/api/data/sources")
def list_data_sources():
    return mock_data_sources


@app.post("/api/data/sources")
def create_data_source(payload: dict[str, Any] = Body(...)):
    next_id = max([d["id"] for d in mock_data_sources] + [0]) + 1
    item = {
        "id": next_id,
        "name": payload.get("name", ""),
        "type": payload.get("type", ""),
        "url": payload.get("url", ""),
        "api_key": payload.get("api_key", ""),
        "is_active": bool(payload.get("is_active", True)),
    }
    mock_data_sources.append(item)
    return item


@app.put("/api/data/sources/{source_id}")
def update_data_source(source_id: int, payload: dict[str, Any] = Body(...)):
    item = next((d for d in mock_data_sources if d["id"] == source_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Data source not found")
    for k in ["name", "type", "url", "api_key", "is_active"]:
        if k in payload:
            item[k] = payload[k]
    return item


@app.delete("/api/data/sources/{source_id}")
def delete_data_source(source_id: int):
    idx = next((i for i, d in enumerate(mock_data_sources) if d["id"] == source_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Data source not found")
    mock_data_sources.pop(idx)
    return {"message": "deleted"}


@app.get("/api/data/market")
def get_market_data(symbol: str, startDate: Optional[str] = None, endDate: Optional[str] = None, interval: str = "1d", source: str = "mock"):
    if interval != "1d":
        raise HTTPException(status_code=400, detail="only_1d_supported_in_mock")
    start = _parse_date(startDate) if startDate else date.today() - timedelta(days=90)
    end = _parse_date(endDate) if endDate else date.today()
    if end < start:
        raise HTTPException(status_code=400, detail="end_before_start")
    if source != "mock":
        raise HTTPException(status_code=400, detail="only_mock_source_enabled_in_mvp")

    df = _gen_mock_ohlcv(start=start, end=end, seed=hash(symbol) % 2**32)
    out = df.reset_index().rename(columns={"index": "date"})
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    return {"symbol": symbol, "data": out.to_dict(orient="records")}


@app.post("/api/data/process")
def process_market_data(payload: dict[str, Any] = Body(...)):
    data = payload.get("data") or []
    if not isinstance(data, list) or len(data) == 0:
        raise HTTPException(status_code=400, detail="missing_data")
    df = pd.DataFrame(data)
    if "date" not in df.columns or "close" not in df.columns:
        raise HTTPException(status_code=400, detail="invalid_schema")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["ma5"] = df["close"].rolling(5).mean()
    df["ma10"] = df["close"].rolling(10).mean()
    df["return"] = df["close"].pct_change()
    df["volatility"] = df["return"].rolling(10).std()

    summary = {
        "mean_close": float(df["close"].mean()),
        "std_close": float(df["close"].std(ddof=0)),
        "max_close": float(df["close"].max()),
        "min_close": float(df["close"].min()),
        "mean_volume": float(pd.to_numeric(df.get("volume"), errors="coerce").mean()) if "volume" in df.columns else None,
        "total_return": float((df["close"].iloc[-1] / df["close"].iloc[0] - 1) * 100) if len(df) >= 2 else 0.0,
    }
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    processed = df[["date", "close", "ma5", "ma10", "return", "volatility"]].fillna("").to_dict(orient="records")
    return {"processed_data": processed, "summary": summary}

# 策略路由
@app.get("/api/strategy")
def get_strategies():
    return mock_strategies


@app.post("/api/strategy")
def create_strategy(payload: dict[str, Any] = Body(...)):
    next_id = max([s["id"] for s in mock_strategies] + [0]) + 1
    item = {
        "id": next_id,
        "name": payload.get("name", ""),
        "type": payload.get("type", ""),
        "description": payload.get("description", ""),
        "status": payload.get("status", "inactive"),
        "created_at": datetime.utcnow().isoformat(),
    }
    mock_strategies.append(item)
    return item


@app.put("/api/strategy/{strategy_id}")
def update_strategy(strategy_id: int, payload: dict[str, Any] = Body(...)):
    item = next((s for s in mock_strategies if s["id"] == strategy_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Strategy not found")
    for k in ["name", "type", "description", "status"]:
        if k in payload:
            item[k] = payload[k]
    return item


@app.delete("/api/strategy/{strategy_id}")
def delete_strategy(strategy_id: int):
    idx = next((i for i, s in enumerate(mock_strategies) if s["id"] == strategy_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    mock_strategies.pop(idx)
    return {"message": "deleted"}


@app.post("/api/strategy/{strategy_id}/execute")
def execute_strategy(strategy_id: int):
    item = next((s for s in mock_strategies if s["id"] == strategy_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"message": "executed", "strategy_id": strategy_id}

# 回测路由
@app.get("/api/backtest")
def get_backtests():
    return mock_backtests


@app.post("/api/backtest")
def create_backtest(payload: dict[str, Any] = Body(...)):
    strategy_id = payload.get("strategy_id")
    if not strategy_id:
        raise HTTPException(status_code=400, detail="missing_strategy_id")
    start = str(payload.get("start_date") or "")
    end = str(payload.get("end_date") or "")
    if not start or not end:
        raise HTTPException(status_code=400, detail="missing_dates")
    dates = pd.date_range(start=start, end=end, freq="B")
    if len(dates) == 0:
        raise HTTPException(status_code=400, detail="empty_date_range")
    rng = np.random.default_rng(int(strategy_id) * 997)
    rets = rng.normal(0, 0.01, len(dates))
    equity = (1 + rets).cumprod() * 10000
    profit = float(equity[-1] / equity[0] - 1)
    peak = np.maximum.accumulate(equity)
    drawdown = float(np.min(equity / peak - 1))

    next_id = max([b["id"] for b in mock_backtests] + [0]) + 1
    item = {
        "id": next_id,
        "strategy_id": int(strategy_id),
        "start_date": start,
        "end_date": end,
        "profit": profit,
        "drawdown": abs(drawdown),
        "equity_curve": equity.tolist(),
        "dates": [d.strftime("%Y-%m-%d") for d in dates],
    }
    mock_backtests.append(item)
    return item


@app.delete("/api/backtest/{backtest_id}")
def delete_backtest(backtest_id: int):
    idx = next((i for i, b in enumerate(mock_backtests) if b["id"] == backtest_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Backtest not found")
    mock_backtests.pop(idx)
    return {"message": "deleted"}


@app.get("/api/backtest/{backtest_id}/analysis")
def analyze_backtest(backtest_id: int):
    item = next((b for b in mock_backtests if b["id"] == backtest_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Backtest not found")
    eq = np.array(item.get("equity_curve", []), dtype="float64")
    if eq.size == 0:
        raise HTTPException(status_code=500, detail="missing_equity")
    daily_ret = pd.Series(eq).pct_change().fillna(0.0)
    sharpe = float(daily_ret.mean() / daily_ret.std(ddof=0) * np.sqrt(252.0)) if float(daily_ret.std(ddof=0)) != 0 else 0.0
    return {
        "backtest_id": backtest_id,
        "strategy_id": item["strategy_id"],
        "start_date": item["start_date"],
        "end_date": item["end_date"],
        "total_return": float(item["profit"] * 100),
        "max_drawdown": float(item["drawdown"] * 100),
        "sharpe_ratio": sharpe,
        "equity_curve": item.get("equity_curve", []),
        "dates": item.get("dates", []),
    }

# 交易路由
@app.get("/api/trading")
def list_orders(status: Optional[str] = None, symbol: Optional[str] = None, type: Optional[str] = None):
    items = mock_orders
    if status:
        items = [o for o in items if o.get("status") == status]
    if symbol:
        items = [o for o in items if o.get("symbol") == symbol]
    if type:
        items = [o for o in items if o.get("type") == type]
    return items


@app.post("/api/trading")
def create_order(payload: dict[str, Any] = Body(...)):
    next_id = max([o["id"] for o in mock_orders] + [0]) + 1
    item = {
        "id": next_id,
        "symbol": payload.get("symbol", ""),
        "type": payload.get("type", "buy"),
        "price": float(payload.get("price") or 0),
        "quantity": int(payload.get("quantity") or 0),
        "status": "open",
        "timestamp": datetime.utcnow().isoformat(),
    }
    mock_orders.append(item)
    return item


@app.put("/api/trading/{order_id}/cancel")
def cancel_order(order_id: int):
    item = next((o for o in mock_orders if o["id"] == order_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Order not found")
    item["status"] = "canceled"
    return {"message": "canceled"}


@app.get("/api/trading/portfolio")
def get_portfolio():
    positions: dict[str, int] = {}
    for o in mock_orders:
        if o.get("status") != "open":
            continue
        qty = int(o.get("quantity") or 0)
        sym = str(o.get("symbol") or "")
        if not sym:
            continue
        positions[sym] = positions.get(sym, 0) + (qty if o.get("type") == "buy" else -qty)
    out = [{"symbol": k, "quantity": v} for k, v in positions.items()]
    return {"positions": out}


@app.get("/api/trading/stats/summary")
def trading_summary():
    total = len(mock_orders)
    open_cnt = len([o for o in mock_orders if o.get("status") == "open"])
    canceled = len([o for o in mock_orders if o.get("status") == "canceled"])
    return {"total_orders": total, "open_orders": open_cnt, "canceled_orders": canceled}


@app.get("/{path:path}", include_in_schema=False)
def spa_fallback(path: str):
    if path.startswith("api"):
        raise HTTPException(status_code=404, detail="not_found")
    index = FRONTEND_DIST_DIR / "index.html"
    if index.is_file():
        candidate = FRONTEND_DIST_DIR / path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index)
    raise HTTPException(status_code=404, detail="frontend_not_built")


def _parse_date(s: str) -> date:
    return datetime.strptime(s[:10], "%Y-%m-%d").date()


def _gen_mock_ohlcv(start: date, end: date, seed: int) -> pd.DataFrame:
    dates = pd.date_range(start=start, end=end, freq="B")
    rng = np.random.default_rng(seed)
    price = 10.0
    rows = []
    for _ in range(len(dates)):
        ret = float(rng.normal(0, 0.01))
        close = max(0.5, price * (1 + ret))
        open_ = price
        high = max(open_, close) * (1 + float(rng.random()) * 0.01)
        low = min(open_, close) * (1 - float(rng.random()) * 0.01)
        vol = int(rng.integers(100000, 2000000))
        rows.append((open_, high, low, close, vol))
        price = close
    df = pd.DataFrame(rows, index=dates, columns=["open", "high", "low", "close", "volume"])
    return df

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
