from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from core.database import get_db
from models import DataSource
from api.auth import get_current_user
from models import User
import requests
import pandas as pd
import json

router = APIRouter()

# 获取数据源列表
@router.get("/sources")
def get_data_sources(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sources = db.query(DataSource).offset(skip).limit(limit).all()
    return sources

# 获取数据源详情
@router.get("/sources/{source_id}")
def get_data_source(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    return source

# 创建数据源
@router.post("/sources")
def create_data_source(
    name: str,
    type: str,
    url: str,
    api_key: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查数据源名称是否已存在
    if db.query(DataSource).filter(DataSource.name == name).first():
        raise HTTPException(
            status_code=400,
            detail="Data source name already exists"
        )
    # 创建新数据源
    new_source = DataSource(
        name=name,
        type=type,
        url=url,
        api_key=api_key
    )
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return new_source

# 更新数据源
@router.put("/sources/{source_id}")
def update_data_source(
    source_id: int,
    name: str = None,
    type: str = None,
    url: str = None,
    api_key: str = None,
    is_active: bool = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    if name:
        source.name = name
    if type:
        source.type = type
    if url:
        source.url = url
    if api_key is not None:
        source.api_key = api_key
    if is_active is not None:
        source.is_active = is_active
    
    db.commit()
    db.refresh(source)
    return source

# 删除数据源
@router.delete("/sources/{source_id}")
def delete_data_source(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    db.delete(source)
    db.commit()
    return {"message": "Data source deleted successfully"}

# 获取市场数据
@router.get("/market")
def get_market_data(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
    current_user: User = Depends(get_current_user)
):
    # 这里可以根据不同的数据源获取数据
    # 例如使用Tushare API获取股票数据
    try:
        # 模拟数据返回
        data = {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval,
            "data": [
                {"date": "2026-03-15", "open": 100, "high": 105, "low": 98, "close": 102, "volume": 1000000},
                {"date": "2026-03-16", "open": 102, "high": 108, "low": 100, "close": 106, "volume": 1200000},
                {"date": "2026-03-17", "open": 106, "high": 110, "low": 104, "close": 108, "volume": 1500000},
                {"date": "2026-03-18", "open": 108, "high": 112, "low": 106, "close": 110, "volume": 1800000},
                {"date": "2026-03-19", "open": 110, "high": 115, "low": 108, "close": 113, "volume": 2000000}
            ]
        }
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market data: {str(e)}")

# 处理数据
@router.post("/process")
def process_data(
    data: dict,
    current_user: User = Depends(get_current_user)
):
    try:
        # 模拟数据处理
        df = pd.DataFrame(data.get("data", []))
        # 计算简单的技术指标
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['return'] = df['close'].pct_change()
        
        result = {
            "original_data": data,
            "processed_data": df.to_dict(orient="records"),
            "summary": {
                "mean_close": float(df['close'].mean()),
                "std_close": float(df['close'].std()),
                "max_close": float(df['close'].max()),
                "min_close": float(df['close'].min())
            }
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")