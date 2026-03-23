from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Order, OrderItem, Product
from api.auth import get_current_user
from models import User

router = APIRouter()

# 创建订单
@router.post("/")
def create_order(
    items: list[dict],  # 格式: [{"product_id": int, "quantity": int}]
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 计算总金额并检查库存
    total_amount = 0
    order_items = []
    
    for item in items:
        product = db.query(Product).filter(Product.id == item["product_id"]).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item['product_id']} not found")
        if product.stock < item["quantity"]:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.name}")
        total_amount += product.price * item["quantity"]
        order_items.append({
            "product": product,
            "quantity": item["quantity"]
        })
    
    # 创建订单
    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status="待付款"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # 创建订单商品
    for item in order_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            price=item["product"].price
        )
        db.add(order_item)
        # 更新库存
        item["product"].stock -= item["quantity"]
    
    db.commit()
    
    return new_order

# 获取当前用户的订单列表
@router.get("/")
def get_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    orders = db.query(Order).filter(Order.user_id == current_user.id).offset(skip).limit(limit).all()
    return orders

# 获取订单详情
@router.get("/{order_id}")
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return order

# 更新订单状态
@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    order.status = status
    db.commit()
    db.refresh(order)
    return order