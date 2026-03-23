from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import json
import traceback
from datetime import datetime
from models import Strategy, Backtest
from sqlalchemy.orm import Session
from services.data_service import DataService

class StrategyService:
    def __init__(self, db: Session):
        self.db = db
        self.data_service = DataService(db)
    
    def get_strategy(self, strategy_id: int, user_id: int) -> Optional[Strategy]:
        """获取策略"""
        return self.db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.user_id == user_id).first()
    
    def get_all_strategies(self, user_id: int) -> List[Strategy]:
        """获取用户的所有策略"""
        return self.db.query(Strategy).filter(Strategy.user_id == user_id).all()
    
    def create_strategy(self, name: str, type: str, code: str, parameters: Dict[str, Any], user_id: int) -> Strategy:
        """创建策略"""
        new_strategy = Strategy(
            name=name,
            type=type,
            code=code,
            parameters=json.dumps(parameters) if parameters else None,
            user_id=user_id
        )
        self.db.add(new_strategy)
        self.db.commit()
        self.db.refresh(new_strategy)
        return new_strategy
    
    def update_strategy(self, strategy_id: int, user_id: int, **kwargs) -> Optional[Strategy]:
        """更新策略"""
        strategy = self.get_strategy(strategy_id, user_id)
        if strategy:
            for key, value in kwargs.items():
                if key == "parameters" and value is not None:
                    setattr(strategy, key, json.dumps(value))
                elif hasattr(strategy, key):
                    setattr(strategy, key, value)
            self.db.commit()
            self.db.refresh(strategy)
        return strategy
    
    def delete_strategy(self, strategy_id: int, user_id: int) -> bool:
        """删除策略"""
        strategy = self.get_strategy(strategy_id, user_id)
        if strategy:
            self.db.delete(strategy)
            self.db.commit()
            return True
        return False
    
    def execute_strategy(self, strategy_id: int, user_id: int, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行策略"""
        strategy = self.get_strategy(strategy_id, user_id)
        if not strategy:
            return {"error": "Strategy not found"}
        
        try:
            # 获取策略参数
            strategy_params = json.loads(strategy.parameters) if strategy.parameters else {}
            if parameters:
                strategy_params.update(parameters)
            
            # 执行策略代码
            # 这里使用exec执行策略代码，实际项目中应该使用更安全的方式
            local_vars = {
                "params": strategy_params,
                "data": None,
                "signals": []
            }
            
            # 执行策略代码
            exec(strategy.code, {}, local_vars)
            
            # 获取执行结果
            signals = local_vars.get("signals", [])
            
            return {
                "strategy_id": strategy.id,
                "strategy_name": strategy.name,
                "parameters": strategy_params,
                "status": "executed",
                "signals": signals
            }
        except Exception as e:
            return {
                "strategy_id": strategy.id,
                "strategy_name": strategy.name,
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def run_backtest(self, strategy_id: int, user_id: int, start_date: str, end_date: str, parameters: Dict[str, Any] = None) -> Backtest:
        """运行回测"""
        strategy = self.get_strategy(strategy_id, user_id)
        if not strategy:
            raise ValueError("Strategy not found")
        
        try:
            # 获取策略参数
            strategy_params = json.loads(strategy.parameters) if strategy.parameters else {}
            if parameters:
                strategy_params.update(parameters)
            
            # 获取历史数据
            symbol = strategy_params.get("symbol", "AAPL")
            data = self.data_service.get_market_data(symbol, start_date, end_date)
            df = pd.DataFrame(data.get("data", []))
            
            # 执行策略回测
            local_vars = {
                "params": strategy_params,
                "data": df,
                "signals": [],
                "positions": [],
                "equity": [10000]  # 初始资金
            }
            
            # 执行策略代码
            exec(strategy.code, {}, local_vars)
            
            # 计算绩效指标
            equity = np.array(local_vars.get("equity", [10000]))
            returns = np.diff(equity) / equity[:-1]
            
            total_return = (equity[-1] / equity[0] - 1) * 100
            max_drawdown = ((equity.cummax() - equity) / equity.cummax()).max() * 100
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
            
            # 保存回测结果
            new_backtest = Backtest(
                strategy_id=strategy_id,
                user_id=user_id,
                start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(end_date, "%Y-%m-%d"),
                parameters=json.dumps(parameters) if parameters else None,
                performance=total_return,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                results=json.dumps({
                    "equity": equity.tolist(),
                    "returns": returns.tolist(),
                    "signals": local_vars.get("signals", []),
                    "positions": local_vars.get("positions", [])
                })
            )
            
            self.db.add(new_backtest)
            self.db.commit()
            self.db.refresh(new_backtest)
            
            return new_backtest
        except Exception as e:
            raise Exception(f"Error running backtest: {str(e)}")
    
    def analyze_backtest(self, backtest_id: int, user_id: int) -> Dict[str, Any]:
        """分析回测结果"""
        backtest = self.db.query(Backtest).filter(Backtest.id == backtest_id, Backtest.user_id == user_id).first()
        if not backtest:
            raise ValueError("Backtest not found")
        
        try:
            results = json.loads(backtest.results)
            equity = np.array(results.get("equity", []))
            returns = np.array(results.get("returns", []))
            signals = results.get("signals", [])
            positions = results.get("positions", [])
            
            # 计算更多绩效指标
            annual_return = (equity[-1] / equity[0] - 1) * 100 / ((backtest.end_date - backtest.start_date).days / 365)
            volatility = np.std(returns) * np.sqrt(252) * 100
            sortino_ratio = np.mean(returns) / np.std(returns[returns < 0]) * np.sqrt(252) if np.std(returns[returns < 0]) > 0 else 0
            calmar_ratio = annual_return / backtest.max_drawdown if backtest.max_drawdown > 0 else 0
            
            # 计算胜率
            winning_trades = len([s for s in signals if s.get("signal") == "buy" and s.get("profit", 0) > 0])
            total_trades = len(signals)
            win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0
            
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
                "win_rate": win_rate,
                "total_trades": total_trades,
                "equity_curve": equity.tolist(),
                "returns": returns.tolist(),
                "signals": signals,
                "positions": positions
            }
            
            return analysis
        except Exception as e:
            raise Exception(f"Error analyzing backtest: {str(e)}")