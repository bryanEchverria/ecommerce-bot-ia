from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc, and_, or_, select, case, Float
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import models
import schemas

# ==================== PRODUCTS ====================

async def get_product_async(db: AsyncSession, product_id: str, client_id: Optional[str] = None):
    """Get a single product by ID with optional client filtering"""
    conditions = [models.Product.id == product_id]
    if client_id:
        conditions.append(models.Product.client_id == client_id)
    
    query = select(models.Product).where(and_(*conditions))
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_products_async(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    category: Optional[str] = None,
    client_id: Optional[str] = None
):
    """Get products with optional filtering including client filtering"""
    query = select(models.Product)
    
    # Apply filters at SQL level
    conditions = []
    if status:
        conditions.append(models.Product.status == status)
    if category:
        conditions.append(models.Product.category == category)
    
    # IMPORTANT: Always filter by client_id in multi-tenant mode
    # If client_id is provided, only return products for that client
    # If client_id is None, return empty result (no products for no tenant)
    if client_id is not None:
        conditions.append(models.Product.client_id == client_id)
    else:
        # No tenant = no products (secure by default)
        conditions.append(models.Product.client_id == 'NO_TENANT_MATCH')
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Order by created_at desc and apply pagination
    query = query.order_by(desc(models.Product.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def search_products_async(
    db: AsyncSession,
    search_query: str,
    limit: int = 10,
    status: str = "Active",
    client_id: Optional[str] = None
):
    """Search products by name or description with tenant filtering"""
    query = select(models.Product)
    
    # Apply search filters
    search_conditions = [
        or_(
            models.Product.name.ilike(f"%{search_query}%"),
            models.Product.description.ilike(f"%{search_query}%")
        )
    ]
    
    # Apply status filter
    if status:
        search_conditions.append(models.Product.status == status)
    
    # IMPORTANT: Always filter by client_id in multi-tenant mode
    if client_id is not None:
        search_conditions.append(models.Product.client_id == client_id)
    else:
        # No tenant = no products (secure by default)
        search_conditions.append(models.Product.client_id == 'NO_TENANT_MATCH')
    
    query = query.where(and_(*search_conditions))
    query = query.order_by(desc(models.Product.created_at)).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_products_by_category_async(
    db: AsyncSession,
    category: str,
    limit: int = 100,
    offset: int = 0,
    status: str = "Active",
    client_id: Optional[str] = None
):
    """Get products by category with SQL-level filtering and tenant isolation"""
    conditions = [
        models.Product.category == category,
        models.Product.status == status
    ]
    
    # IMPORTANT: Always filter by client_id in multi-tenant mode
    if client_id is not None:
        conditions.append(models.Product.client_id == client_id)
    else:
        # No tenant = no products (secure by default)
        conditions.append(models.Product.client_id == 'NO_TENANT_MATCH')
    
    query = select(models.Product).where(
        and_(*conditions)
    ).order_by(models.Product.name).offset(offset).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_catalog_summary_async(db: AsyncSession, client_id: Optional[str] = None):
    """Get catalog summary with category count and total products - tenant filtered"""
    
    # IMPORTANT: Always filter by client_id in multi-tenant mode
    conditions = []
    if client_id is not None:
        conditions.append(models.Product.client_id == client_id)
    else:
        # No tenant = no products (secure by default)
        conditions.append(models.Product.client_id == 'NO_TENANT_MATCH')
    
    # Get total products count
    total_query = select(func.count(models.Product.id))
    if conditions:
        total_query = total_query.where(and_(*conditions))
    
    total_result = await db.execute(total_query)
    total_products = total_result.scalar() or 0
    
    # Get categories with product counts
    category_query = select(
        models.Product.category,
        func.count(models.Product.id).label('count')
    ).group_by(models.Product.category)
    
    if conditions:
        category_query = category_query.where(and_(*conditions))
    
    category_result = await db.execute(category_query)
    categories = [
        {"name": row[0], "count": row[1]} 
        for row in category_result.fetchall()
    ]
    
    return {
        "categories": categories,
        "total_products": total_products,
        "total_categories": len(categories)
    }

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

async def get_discounts_async(db: AsyncSession, skip: int = 0, limit: int = 100, client_id: Optional[str] = None):
    """Get discounts with pagination and optional client filtering"""
    query = select(models.Discount)
    
    # IMPORTANT: Always filter by client_id in multi-tenant mode
    if client_id is not None:
        query = query.where(models.Discount.client_id == client_id)
    else:
        # No tenant = no discounts (secure by default)
        query = query.where(models.Discount.client_id == 'NO_TENANT_MATCH')
    
    query = query.order_by(desc(models.Discount.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

# ==================== CAMPAIGNS ====================

async def get_campaigns_async(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    client_id: Optional[str] = None
):
    """Get campaigns with optional filtering including client filtering"""
    query = select(models.Campaign)
    
    # Apply filters at SQL level
    conditions = []
    if status:
        conditions.append(models.Campaign.status == status)
    
    # IMPORTANT: Always filter by client_id in multi-tenant mode
    if client_id is not None:
        conditions.append(models.Campaign.client_id == client_id)
    else:
        # No tenant = no campaigns (secure by default)
        conditions.append(models.Campaign.client_id == 'NO_TENANT_MATCH')
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Order by created_at desc and apply pagination
    query = query.order_by(desc(models.Campaign.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_campaign_async(db: AsyncSession, campaign_id: str, client_id: Optional[str] = None):
    """Get a single campaign by ID with optional client filtering"""
    conditions = [models.Campaign.id == campaign_id]
    if client_id:
        conditions.append(models.Campaign.client_id == client_id)
    
    query = select(models.Campaign).where(and_(*conditions))
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_campaign_async(db: AsyncSession, campaign: Dict[str, Any], campaign_id: str):
    """Create a new campaign"""
    db_campaign = models.Campaign(id=campaign_id, **campaign)
    db.add(db_campaign)
    await db.commit()
    await db.refresh(db_campaign)
    return db_campaign

# ==================== DISCOUNTS ====================

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