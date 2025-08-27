from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc, and_, or_, select, case, Float
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import models
import schemas

# ==================== PRODUCTS ====================

async def get_product_async(db: AsyncSession, product_id: str):
    """Get a single product by ID"""
    query = select(models.Product).where(models.Product.id == product_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_products_async(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    category: Optional[str] = None
):
    """Get products with optional filtering"""
    query = select(models.Product)
    
    # Apply filters at SQL level
    if status:
        query = query.where(models.Product.status == status)
    if category:
        query = query.where(models.Product.category == category)
    
    # Order by created_at desc and apply pagination
    query = query.order_by(desc(models.Product.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_products_by_category_async(
    db: AsyncSession,
    category: str,
    limit: int = 100,
    offset: int = 0,
    status: str = "Active"
):
    """Get products by category with SQL-level filtering"""
    conditions = [
        models.Product.category == category,
        models.Product.status == status
    ]
    
    query = select(models.Product).where(
        and_(*conditions)
    ).order_by(models.Product.name).offset(offset).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def create_product_async(db: AsyncSession, product: Dict[str, Any], product_id: str):
    """Create a new product"""
    db_product = models.Product(id=product_id, **product)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def update_product_async(db: AsyncSession, product_id: str, product: Dict[str, Any]):
    """Update an existing product"""
    query = select(models.Product).where(models.Product.id == product_id)
    result = await db.execute(query)
    db_product = result.scalar_one_or_none()
    
    if db_product:
        for key, value in product.items():
            setattr(db_product, key, value)
        await db.commit()
        await db.refresh(db_product)
    
    return db_product

async def delete_product_async(db: AsyncSession, product_id: str):
    """Delete a product"""
    query = select(models.Product).where(models.Product.id == product_id)
    result = await db.execute(query)
    db_product = result.scalar_one_or_none()
    
    if db_product:
        await db.delete(db_product)
        await db.commit()

# ==================== ORDERS ====================

async def get_order_async(db: AsyncSession, order_id: str):
    """Get a single order by ID"""
    query = select(models.Order).where(models.Order.id == order_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_orders_async(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    customer_name: Optional[str] = None
):
    """Get orders with optional filtering"""
    query = select(models.Order)
    
    if status:
        query = query.where(models.Order.status == status)
    if customer_name:
        query = query.where(models.Order.customer_name.ilike(f"%{customer_name}%"))
    
    query = query.order_by(desc(models.Order.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def create_order_async(db: AsyncSession, order: Dict[str, Any], order_id: str):
    """Create a new order with auto-generated order number"""
    # Get the next order number
    count_query = select(func.count(models.Order.id))
    count_result = await db.execute(count_query)
    count = count_result.scalar() or 0
    
    if 'order_number' not in order:
        order['order_number'] = f"ORD-{count + 1:06d}"
    
    db_order = models.Order(id=order_id, **order)
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order

async def update_order_async(db: AsyncSession, order_id: str, order: Dict[str, Any]):
    """Update an existing order"""
    query = select(models.Order).where(models.Order.id == order_id)
    result = await db.execute(query)
    db_order = result.scalar_one_or_none()
    
    if db_order:
        for key, value in order.items():
            setattr(db_order, key, value)
        await db.commit()
        await db.refresh(db_order)
    
    return db_order

async def delete_order_async(db: AsyncSession, order_id: str):
    """Delete an order"""
    query = select(models.Order).where(models.Order.id == order_id)
    result = await db.execute(query)
    db_order = result.scalar_one_or_none()
    
    if db_order:
        await db.delete(db_order)
        await db.commit()

# ==================== DISCOUNTS ====================

async def get_discount_async(db: AsyncSession, discount_id: str):
    """Get a single discount by ID"""
    query = select(models.Discount).where(models.Discount.id == discount_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_discounts_async(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get discounts with pagination"""
    query = select(models.Discount).order_by(desc(models.Discount.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_active_discounts_async(db: AsyncSession):
    """Get only active discounts"""
    query = select(models.Discount).where(models.Discount.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()

async def create_discount_async(db: AsyncSession, discount: Dict[str, Any], discount_id: str):
    """Create a new discount"""
    db_discount = models.Discount(id=discount_id, **discount)
    db.add(db_discount)
    await db.commit()
    await db.refresh(db_discount)
    return db_discount

async def update_discount_async(db: AsyncSession, discount_id: str, discount: Dict[str, Any]):
    """Update an existing discount"""
    query = select(models.Discount).where(models.Discount.id == discount_id)
    result = await db.execute(query)
    db_discount = result.scalar_one_or_none()
    
    if db_discount:
        for key, value in discount.items():
            setattr(db_discount, key, value)
        await db.commit()
        await db.refresh(db_discount)
    
    return db_discount

async def delete_discount_async(db: AsyncSession, discount_id: str):
    """Delete a discount"""
    query = select(models.Discount).where(models.Discount.id == discount_id)
    result = await db.execute(query)
    db_discount = result.scalar_one_or_none()
    
    if db_discount:
        await db.delete(db_discount)
        await db.commit()