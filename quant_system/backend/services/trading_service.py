from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import json
from datetime import datetime
from models import Trade, Strategy
from sqlalchemy.orm import Session
from core.config import settings

class TradingService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_trade(self, trade_id: int, user_id: int) -> Optional[Trade]:
        """获取交易"""
        return self.db.query(Trade).filter(Trade.id == trade_id, Trade.user_id == user_id).first()
    
    def get_all_trades(self, user_id: int, strategy_id: int = None, trade_type: str = None) -> List[Trade]:
        """获取用户的所有交易"""
        query = self.db.query(Trade).filter(Trade.user_id == user_id)
        if strategy_id:
            query = query.filter(Trade.strategy_id == strategy_id)
        if trade_type:
            query = query.filter(Trade.trade_type == trade_type)
        return query.order_by(Trade.created_at.desc()).all()
    
    def create_trade(self, symbol: str, direction: str, price: float, quantity: float, 
                    strategy_id: int = None, trade_type: str = "paper", user_id: int = None) -> Trade:
        """创建交易"""
        # 检查策略是否存在且属于当前用户
        if strategy_id and user_id:
            strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.user_id == user_id).first()
            if not strategy:
                raise ValueError("Strategy not found")
        
        # 计算交易金额
        amount = price * quantity
        
        # 创建交易记录
        new_trade = Trade(
            user_id=user_id,
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
        
        # 如果是实盘交易，调用券商API执行交易
        if trade_type == "real":
            try:
                # 这里应该调用券商API执行实际交易
                # 模拟实盘交易执行
                print(f"Executing real trade: {direction} {quantity} {symbol} at {price}")
            except Exception as e:
                new_trade.status = "failed"
                print(f"Error executing real trade: {e}")
        
        # 保存交易记录
        self.db.add(new_trade)
        self.db.commit()
        self.db.refresh(new_trade)
        
        return new_trade
    
    def cancel_trade(self, trade_id: int, user_id: int) -> Optional[Trade]:
        """取消交易"""
        trade = self.get_trade(trade_id, user_id)
        if not trade:
            return None
        
        if trade.status != "pending":
            raise ValueError("Cannot cancel completed trade")
        
        trade.status = "cancelled"
        self.db.commit()
        self.db.refresh(trade)
        
        return trade
    
    def get_trade_stats(self, user_id: int, start_date: str = None, end_date: str = None, trade_type: str = None) -> Dict[str, Any]:
        """获取交易统计"""
        query = self.db.query(Trade).filter(Trade.user_id == user_id)
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
    
    def get_portfolio(self, user_id: int, trade_type: str = "paper") -> Dict[str, Any]:
        """获取投资组合"""
        # 获取所有交易
        trades = self.get_all_trades(user_id, trade_type=trade_type)
        
        # 计算持仓
        holdings = {}
        for trade in trades:
            if trade.symbol not in holdings:
                holdings[trade.symbol] = {"quantity": 0, "avg_price": 0, "total_cost": 0}
            
            if trade.direction == "buy":
                total_quantity = holdings[trade.symbol]["quantity"] + trade.quantity
                total_cost = holdings[trade.symbol]["total_cost"] + trade.amount
                holdings[trade.symbol]["quantity"] = total_quantity
                holdings[trade.symbol]["total_cost"] = total_cost
                holdings[trade.symbol]["avg_price"] = total_cost / total_quantity
            else:
                holdings[trade.symbol]["quantity"] -= trade.quantity
                holdings[trade.symbol]["total_cost"] -= trade.amount
                if holdings[trade.symbol]["quantity"] > 0:
                    holdings[trade.symbol]["avg_price"] = holdings[trade.symbol]["total_cost"] / holdings[trade.symbol]["quantity"]
        
        # 过滤掉数量为0的持仓
        holdings = {k: v for k, v in holdings.items() if v["quantity"] > 0}
        
        # 计算总市值（这里使用当前价格，实际项目中应该从市场获取最新价格）
        total_value = 0
        for symbol, info in holdings.items():
            # 模拟当前价格
            current_price = info["avg_price"] * (1 + np.random.normal(0, 0.05))
            holdings[symbol]["current_price"] = round(current_price, 2)
            holdings[symbol]["market_value"] = round(current_price * info["quantity"], 2)
            holdings[symbol]["profit"] = round(holdings[symbol]["market_value"] - info["total_cost"], 2)
            holdings[symbol]["profit_rate"] = round((holdings[symbol]["profit"] / info["total_cost"]) * 100, 2)
            total_value += holdings[symbol]["market_value"]
        
        portfolio = {
            "holdings": holdings,
            "total_value": round(total_value, 2),
            "total_cost": round(sum(info["total_cost"] for info in holdings.values()), 2),
            "total_profit": round(total_value - sum(info["total_cost"] for info in holdings.values()), 2),
            "total_profit_rate": round((total_value - sum(info["total_cost"] for info in holdings.values())) / sum(info["total_cost"] for info in holdings.values()) * 100, 2) if sum(info["total_cost"] for info in holdings.values()) > 0 else 0
        }
        
        return portfolio
    
    def execute_strategy_trades(self, strategy_id: int, user_id: int, signals: List[Dict[str, Any]], trade_type: str = "paper") -> List[Trade]:
        """执行策略生成的交易信号"""
        trades = []
        for signal in signals:
            try:
                trade = self.create_trade(
                    symbol=signal.get("symbol"),
                    direction=signal.get("signal"),
                    price=signal.get("price"),
                    quantity=signal.get("quantity"),
                    strategy_id=strategy_id,
                    trade_type=trade_type,
                    user_id=user_id
                )
                trades.append(trade)
            except Exception as e:
                print(f"Error executing trade for signal {signal}: {e}")
        return trades