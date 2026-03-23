from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models import User
from api.auth import get_current_user

router = APIRouter()

# 获取当前用户信息
@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at
    }

# 获取用户列表（管理员功能）
@router.get("/")
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# 获取用户详情
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# 更新用户信息
@router.put("/me")
def update_user_info(
    email: str = None,
    password: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if email:
        current_user.email = email
    if password:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        current_user.password_hash = pwd_context.hash(password)
    db.commit()
    db.refresh(current_user)
    return {"message": "User updated successfully"}

# 删除用户（管理员功能）
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}