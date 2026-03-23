from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "个人量化分析与交易系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./quant_system.db"
    
    # Redis配置
    REDIS_URL: Optional[str] = None
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 数据API配置
    TUSHARE_TOKEN: Optional[str] = None
    
    # 交易API配置
    BROKER_API_KEY: Optional[str] = None
    BROKER_SECRET_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()