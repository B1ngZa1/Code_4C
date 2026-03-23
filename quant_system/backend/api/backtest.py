from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models import Backtest, Strategy
from api.auth import get_current_user
from models import User
import json
import pandas as pd
import numpy as np
from datetime import datetime

router = APIRouter()

# 获取回测列表
@router.get("/")
def get_backtests(
    skip: int = 0,
    limit: int = 100,
    strategy_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Backtest).filter(Backtest.user_id == current_user.id)
    if strategy_id:
        query = query.filter(Backtest.strategy_id == strategy_id)
    backtests = query.offset(skip).limit(limit).all()
    return backtests

# 获取回测详情
@router.get("/{backtest_id}")
def get_backtest(
    backtest_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    backtest = db.query(Backtest).filter(Backtest.id == backtest_id, Backtest.user_id == current_user.id).first()
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return backtest

# 创建回测
@router.post("/")
def create_backtest(
    strategy_id: int,
    start_date: str,
    end_date: str,
    parameters: dict = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查策略是否存在且属于当前用户
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.user_id == current_user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # 模拟回测过程
    try:
        # 生成模拟数据
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        returns = np.random.normal(0, 0.01, len(dates))
        equity = (1 + returns).cumprod() * 10000
        
        # 计算绩效指标
        total_return = (equity[-1] / equity[0] - 1) * 100
        max_drawdown = ((equity.cummax() - equity) / equity.cummax()).max() * 100
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
        
        # 保存回测结果
        new_backtest = Backtest(
            strategy_id=strategy_id,
            user_id=current_user.id,
            start_date=datetime.strptime(start_date, "%Y-%m-%d"),
            end_date=datetime.strptime(end_date, "%Y-%m-%d"),
            parameters=json.dumps(parameters) if parameters else None,
            performance=total_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            results=json.dumps({
                "equity": equity.tolist(),
                "returns": returns.tolist(),
                "dates": dates.strftime("%Y-%m-%d").tolist()
            })
        )
        db.add(new_backtest)
        db.commit()
        db.refresh(new_backtest)
        return new_backtest
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running backtest: {str(e)}")

# 删除回测
@router.delete("/{backtest_id}")
def delete_backtest(
    backtest_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    backtest = db.query(Backtest).filter(Backtest.id == backtest_id, Backtest.user_id == current_user.id).first()
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    db.delete(backtest)
    db.commit()
    return {"message": "Backtest deleted successfully"}

# 获取回测结果分析
@router.get("/{backtest_id}/analysis")
def get_backtest_analysis(
    backtest_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    backtest = db.query(Backtest).filter(Backtest.id == backtest_id, Backtest.user_id == current_user.id).first()
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    try:
        results = json.loads(backtest.results)
        equity = np.array(results.get("equity", []))
        returns = np.array(results.get("returns", []))
        
        # 计算更多绩效指标
        annual_return = (equity[-1] / equity[0] - 1) * 100 / ((backtest.end_date - backtest.start_date).days / 365)
        volatility = np.std(returns) * np.sqrt(252) * 100
        sortino_ratio = np.mean(returns) / np.std(returns[returns < 0]) * np.sqrt(252) if np.std(returns[returns < 0]) > 0 else 0
        calmar_ratio = annual_return / backtest.max_drawdown if backtest.max_drawdown > 0 else 0
        
        analysis = {
            "backtest_id": backtest.id,
            "strategy_id": backtest.strategy_id,
            "start_date": backtest.start_date.strftime("%Y-%m-%d"),
            "end_date": backtest.end_date.strftime("%Y-%m-%d"),
            "total_return": backtest.performance,
            "annual_return": annual_return,
            "max_drawdown": backtest.max_drawdown,
            "sharpe_ratio": backtest.sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "calmar_ratio": calmar_ratio,
            "volatility": volatility,
            "equity_curve": results.get("equity", []),
            "returns": results.get("returns", []),
            "dates": results.get("dates", [])
        }
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing backtest results: {str(e)}")