from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models import Trade, Strategy
from api.auth import get_current_user
from models import User
from datetime import datetime

router = APIRouter()

# 获取交易列表
@router.get("/")
def get_trades(
    skip: int = 0,
    limit: int = 100,
    strategy_id: int = None,
    trade_type: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Trade).filter(Trade.user_id == current_user.id)
    if strategy_id:
        query = query.filter(Trade.strategy_id == strategy_id)
    if trade_type:
        query = query.filter(Trade.trade_type == trade_type)
    trades = query.order_by(Trade.created_at.desc()).offset(skip).limit(limit).all()
    return trades

# 获取交易详情
@router.get("/{trade_id}")
def get_trade(
    trade_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trade = db.query(Trade).filter(Trade.id == trade_id, Trade.user_id == current_user.id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

# 创建交易
@router.post("/")
def create_trade(
    symbol: str,
    direction: str,  # buy or sell
    price: float,
    quantity: float,
    strategy_id: int = None,
    trade_type: str = "paper",  # paper or real
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查策略是否存在且属于当前用户
    if strategy_id:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.user_id == current_user.id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
    
    # 计算交易金额
    amount = price * quantity
    
    # 模拟交易执行
    try:
        # 在实际项目中，这里会调用券商API执行交易
        # 这里我们只模拟交易执行
        new_trade = Trade(
            user_id=current_user.id,
            strategy_id=strategy_id,
            symbol=symbol,
            direction=direction,
            price=price,
            quantity=quantity,
            amount=amount,
            trade_type=trade_type,
            status="completed",
            executed_at=datetime.utcnow()
        )
        db.add(new_trade)
        db.commit()
        db.refresh(new_trade)
        return new_trade
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing trade: {str(e)}")

# 取消交易
@router.put("/{trade_id}/cancel")
def cancel_trade(
    trade_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trade = db.query(Trade).filter(Trade.id == trade_id, Trade.user_id == current_user.id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    if trade.status != "pending":
        raise HTTPException(status_code=400, detail="Cannot cancel completed trade")
    
    trade.status = "cancelled"
    db.commit()
    db.refresh(trade)
    return trade

# 获取交易统计
@router.get("/stats/summary")
def get_trade_stats(
    start_date: str = None,
    end_date: str = None,
    trade_type: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Trade).filter(Trade.user_id == current_user.id)
    if start_date:
        query = query.filter(Trade.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        query = query.filter(Trade.created_at <= datetime.strptime(end_date, "%Y-%m-%d"))
    if trade_type:
        query = query.filter(Trade.trade_type == trade_type)
    
    trades = query.all()
    
    # 计算统计指标
    total_trades = len(trades)
    total_buy = len([t for t in trades if t.direction == "buy"])
    total_sell = len([t for t in trades if t.direction == "sell"])
    total_amount = sum(t.amount for t in trades)
    
    # 计算盈利
    # 这里简化处理，实际项目中需要根据买入和卖出价格计算
    profit = 0
    buy_trades = {}
    for trade in trades:
        if trade.direction == "buy":
            if trade.symbol not in buy_trades:
                buy_trades[trade.symbol] = []
            buy_trades[trade.symbol].append(trade)
        else:
            if trade.symbol in buy_trades and buy_trades[trade.symbol]:
                buy_trade = buy_trades[trade.symbol].pop(0)
                profit += (trade.price - buy_trade.price) * trade.quantity
    
    stats = {
        "total_trades": total_trades,
        "total_buy": total_buy,
        "total_sell": total_sell,
        "total_amount": total_amount,
        "profit": profit,
        "profit_rate": (profit / total_amount * 100) if total_amount > 0 else 0
    }
    
    return stats