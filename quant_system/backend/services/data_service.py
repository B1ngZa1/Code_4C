from typing import Dict, List, Any
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
from core.config import settings
from models import DataSource
from sqlalchemy.orm import Session

class DataService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_data_source(self, source_id: int) -> DataSource:
        """获取数据源"""
        return self.db.query(DataSource).filter(DataSource.id == source_id).first()
    
    def get_all_data_sources(self) -> List[DataSource]:
        """获取所有数据源"""
        return self.db.query(DataSource).all()
    
    def create_data_source(self, name: str, type: str, url: str, api_key: str = None) -> DataSource:
        """创建数据源"""
        new_source = DataSource(
            name=name,
            type=type,
            url=url,
            api_key=api_key
        )
        self.db.add(new_source)
        self.db.commit()
        self.db.refresh(new_source)
        return new_source
    
    def update_data_source(self, source_id: int, **kwargs) -> DataSource:
        """更新数据源"""
        source = self.get_data_source(source_id)
        if source:
            for key, value in kwargs.items():
                if hasattr(source, key):
                    setattr(source, key, value)
            self.db.commit()
            self.db.refresh(source)
        return source
    
    def delete_data_source(self, source_id: int) -> bool:
        """删除数据源"""
        source = self.get_data_source(source_id)
        if source:
            self.db.delete(source)
            self.db.commit()
            return True
        return False
    
    def get_market_data(self, symbol: str, start_date: str, end_date: str, interval: str = "1d", source: str = "tushare") -> Dict[str, Any]:
        """获取市场数据"""
        if source == "tushare":
            return self._get_tushare_data(symbol, start_date, end_date, interval)
        elif source == "binance":
            return self._get_binance_data(symbol, start_date, end_date, interval)
        else:
            # 模拟数据
            return self._get_mock_data(symbol, start_date, end_date, interval)
    
    def _get_tushare_data(self, symbol: str, start_date: str, end_date: str, interval: str) -> Dict[str, Any]:
        """从Tushare获取数据"""
        try:
            import tushare as ts
            if settings.TUSHARE_TOKEN:
                ts.set_token(settings.TUSHARE_TOKEN)
                pro = ts.pro_api()
                
                # 转换日期格式
                start = start_date.replace("-", "")
                end = end_date.replace("-", "")
                
                # 获取股票数据
                df = pro.daily(
                    ts_code=symbol,
                    start_date=start,
                    end_date=end
                )
                
                # 转换数据格式
                data = []
                for _, row in df.iterrows():
                    data.append({
                        "date": row["trade_date"],
                        "open": row["open"],
                        "high": row["high"],
                        "low": row["low"],
                        "close": row["close"],
                        "volume": row["vol"]
                    })
                
                return {
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "interval": interval,
                    "data": data
                }
            else:
                return self._get_mock_data(symbol, start_date, end_date, interval)
        except Exception as e:
            print(f"Error getting data from Tushare: {e}")
            return self._get_mock_data(symbol, start_date, end_date, interval)
    
    def _get_binance_data(self, symbol: str, start_date: str, end_date: str, interval: str) -> Dict[str, Any]:
        """从Binance获取数据"""
        try:
            # 转换时间戳
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)
            
            # 构建API URL
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "startTime": start_ts,
                "endTime": end_ts,
                "limit": 1000
            }
            
            # 发送请求
            response = requests.get(url, params=params)
            data = response.json()
            
            # 转换数据格式
            result = []
            for item in data:
                result.append({
                    "date": datetime.fromtimestamp(item[0] / 1000).strftime("%Y-%m-%d"),
                    "open": float(item[1]),
                    "high": float(item[2]),
                    "low": float(item[3]),
                    "close": float(item[4]),
                    "volume": float(item[5])
                })
            
            return {
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "interval": interval,
                "data": result
            }
        except Exception as e:
            print(f"Error getting data from Binance: {e}")
            return self._get_mock_data(symbol, start_date, end_date, interval)
    
    def _get_mock_data(self, symbol: str, start_date: str, end_date: str, interval: str) -> Dict[str, Any]:
        """生成模拟数据"""
        import numpy as np
        
        # 生成日期范围
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 生成模拟数据
        data = []
        base_price = 100.0
        for date in dates:
            # 生成随机价格
            change = np.random.normal(0, 2)
            open_price = base_price
            high_price = base_price + np.random.uniform(0, 3)
            low_price = base_price - np.random.uniform(0, 3)
            close_price = base_price + change
            volume = np.random.randint(500000, 2000000)
            
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume
            })
            
            # 更新基础价格
            base_price = close_price
        
        return {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval,
            "data": data
        }
    
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理数据"""
        try:
            # 转换为DataFrame
            df = pd.DataFrame(data.get("data", []))
            
            # 计算技术指标
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma10'] = df['close'].rolling(window=10).mean()
            df['return'] = df['close'].pct_change()
            df['volatility'] = df['return'].rolling(window=20).std() * np.sqrt(252)
            
            # 计算其他指标
            df['high_low_range'] = df['high'] - df['low']
            df['open_close_change'] = df['close'] - df['open']
            
            # 填充NaN值
            df = df.fillna(0)
            
            # 计算统计信息
            summary = {
                "mean_close": float(df['close'].mean()),
                "std_close": float(df['close'].std()),
                "max_close": float(df['close'].max()),
                "min_close": float(df['close'].min()),
                "mean_volume": float(df['volume'].mean()),
                "total_return": float((df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100) if len(df) > 0 else 0
            }
            
            return {
                "original_data": data,
                "processed_data": df.to_dict(orient="records"),
                "summary": summary
            }
        except Exception as e:
            print(f"Error processing data: {e}")
            return {
                "original_data": data,
                "processed_data": [],
                "summary": {},
                "error": str(e)
            }