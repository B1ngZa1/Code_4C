from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models import Strategy
from api.auth import get_current_user
from models import User
import json

router = APIRouter()

# 获取策略列表
@router.get("/")
def get_strategies(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    strategies = db.query(Strategy).filter(Strategy.user_id == current_user.id).offset(skip).limit(limit).all()
    return strategies

# 获取策略详情
@router.get("/{strategy_id}")
def get_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.user_id == current_user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy

# 创建策略
@router.post("/")
def create_strategy(
    name: str,
    type: str,
    code: str,
    parameters: dict = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 创建新策略
    new_strategy = Strategy(
        name=name,
        type=type,
        code=code,
        parameters=json.dumps(parameters) if parameters else None,
        user_id=current_user.id
    )
    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)
    return new_strategy

# 更新策略
@router.put("/{strategy_id}")
def update_strategy(
    strategy_id: int,
    name: str = None,
    type: str = None,
    code: str = None,
    parameters: dict = None,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.user_id == current_user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if name:
        strategy.name = name
    if type:
        strategy.type = type
    if code:
        strategy.code = code
    if parameters:
        strategy.parameters = json.dumps(parameters)
    if status:
        strategy.status = status
    
    db.commit()
    db.refresh(strategy)
    return strategy

# 删除策略
@router.delete("/{strategy_id}")
def delete_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.user_id == current_user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    db.delete(strategy)
    db.commit()
    return {"message": "Strategy deleted successfully"}

# 执行策略
@router.post("/{strategy_id}/execute")
def execute_strategy(
    strategy_id: int,
    parameters: dict = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.user_id == current_user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    try:
        # 模拟策略执行
        # 实际项目中，这里会执行策略代码并返回结果
        result = {
            "strategy_id": strategy.id,
            "strategy_name": strategy.name,
            "parameters": parameters or json.loads(strategy.parameters) if strategy.parameters else {},
            "status": "executed",
            "result": {
                "signal": "buy",
                "symbol": "AAPL",
                "price": 180.5,
                "quantity": 100,
                "timestamp": "2026-03-22T10:00:00Z"
            }
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing strategy: {str(e)}")