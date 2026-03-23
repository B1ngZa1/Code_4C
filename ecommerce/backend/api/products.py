from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Product

router = APIRouter()

# 获取商品列表
@router.get("/")
def get_products(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    products = query.offset(skip).limit(limit).all()
    return products

# 获取商品详情
@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# 创建商品（管理员功能）
@router.post("/")
def create_product(
    name: str,
    description: str,
    price: float,
    stock: int,
    category: str,
    image_url: str,
    db: Session = Depends(get_db)
):
    new_product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        category=category,
        image_url=image_url
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# 更新商品（管理员功能）
@router.put("/{product_id}")
def update_product(
    product_id: int,
    name: str = None,
    description: str = None,
    price: float = None,
    stock: int = None,
    category: str = None,
    image_url: str = None,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if name:
        product.name = name
    if description:
        product.description = description
    if price:
        product.price = price
    if stock:
        product.stock = stock
    if category:
        product.category = category
    if image_url:
        product.image_url = image_url
    
    db.commit()
    db.refresh(product)
    return product

# 删除商品（管理员功能）
@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}