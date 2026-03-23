from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    strategies = relationship("Strategy", back_populates="user")
    backtests = relationship("Backtest", back_populates="user")
    trades = relationship("Trade", back_populates="user")

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    code = Column(Text)
    parameters = Column(Text)
    status = Column(String, default="inactive")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # 关系
    user = relationship("User", back_populates="strategies")
    backtests = relationship("Backtest", back_populates="strategy")
    trades = relationship("Trade", back_populates="strategy")

class Backtest(Base):
    __tablename__ = "backtests"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    parameters = Column(Text)
    performance = Column(Float)
    max_drawdown = Column(Float)
    sharpe_ratio = Column(Float)
    results = Column(Text)
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    strategy = relationship("Strategy", back_populates="backtests")
    user = relationship("User", back_populates="backtests")

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    symbol = Column(String)
    direction = Column(String)  # buy or sell
    price = Column(Float)
    quantity = Column(Float)
    amount = Column(Float)
    status = Column(String, default="completed")
    trade_type = Column(String)  # paper or real
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime)
    
    # 关系
    user = relationship("User", back_populates="trades")
    strategy = relationship("Strategy", back_populates="trades")

class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    type = Column(String)
    url = Column(String)
    api_key = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Setting(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True)
    value = Column(Text)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)