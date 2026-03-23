from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models import Setting
from api.auth import get_current_user
from models import User

router = APIRouter()

# 获取系统设置列表
@router.get("/")
def get_settings(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = db.query(Setting).offset(skip).limit(limit).all()
    return settings

# 获取设置详情
@router.get("/{setting_id}")
def get_setting(
    setting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    setting = db.query(Setting).filter(Setting.id == setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

# 根据键获取设置
@router.get("/key/{key}")
def get_setting_by_key(
    key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

# 创建设置
@router.post("/")
def create_setting(
    key: str,
    value: str,
    description: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查设置键是否已存在
    if db.query(Setting).filter(Setting.key == key).first():
        raise HTTPException(
            status_code=400,
            detail="Setting key already exists"
        )
    # 创建新设置
    new_setting = Setting(
        key=key,
        value=value,
        description=description
    )
    db.add(new_setting)
    db.commit()
    db.refresh(new_setting)
    return new_setting

# 更新设置
@router.put("/{setting_id}")
def update_setting(
    setting_id: int,
    value: str = None,
    description: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    setting = db.query(Setting).filter(Setting.id == setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    if value is not None:
        setting.value = value
    if description is not None:
        setting.description = description
    
    db.commit()
    db.refresh(setting)
    return setting

# 根据键更新设置
@router.put("/key/{key}")
def update_setting_by_key(
    key: str,
    value: str,
    description: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        # 如果设置不存在，创建新设置
        new_setting = Setting(
            key=key,
            value=value,
            description=description
        )
        db.add(new_setting)
        db.commit()
        db.refresh(new_setting)
        return new_setting
    else:
        # 更新现有设置
        setting.value = value
        if description is not None:
            setting.description = description
        db.commit()
        db.refresh(setting)
        return setting

# 删除设置
@router.delete("/{setting_id}")
def delete_setting(
    setting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    setting = db.query(Setting).filter(Setting.id == setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    db.delete(setting)
    db.commit()
    return {"message": "Setting deleted successfully"}