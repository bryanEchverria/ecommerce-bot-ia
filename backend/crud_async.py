from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc, and_, or_, select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import models
import schemas

# ==================== PRODUCTS ====================

async def get_product_async(db: AsyncSession, product_id: str, client_id: Optional[str] = None):
    """Get a single product by ID - optionally filtered by client"""
    query = select(models.Product).where(models.Product.id == product_id)
    
    # Add client filter if provided (for multi-tenant isolation)
    if client_id:
        query = query.where(models.Product.client_id == client_id)
    
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
    """Get products with optional filtering - filtered by client"""
    query = select(models.Product)
    
    # Apply client filter first (CRITICAL for multi-tenant isolation)
    if client_id:
        query = query.where(models.Product.client_id == client_id)
    
    # Apply other filters at SQL level
    if status:
        query = query.where(models.Product.status == status)
    if category:
        query = query.where(models.Product.category == category)
    
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
) -> List[models.Product]:
    """Search products using SQL ILIKE for better performance - filtered by client"""
    search_term = f"%{search_query.lower()}%"
    
    conditions = [
        models.Product.status == status,
        or_(
            func.lower(models.Product.name).like(search_term),
            func.lower(models.Product.category).like(search_term)
        )
    ]
    
    # Add client filter (CRITICAL for multi-tenant isolation)
    if client_id:
        conditions.append(models.Product.client_id == client_id)
    
    query = select(models.Product).where(
        and_(*conditions)
    ).order_by(
        # Prioritize name matches over category matches
        desc(func.lower(models.Product.name).like(search_term)),
        models.Product.name
    ).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_products_by_category_async(
    db: AsyncSession,
    category: str,
    limit: int = 10,
    offset: int = 0,
    status: str = "Active",
    client_id: Optional[str] = None
) -> List[models.Product]:
    """Get products by category with pagination - filtered by client"""
    conditions = [
        models.Product.status == status,
        func.lower(models.Product.category) == category.lower()
    ]
    
    # Add client filter (CRITICAL for multi-tenant isolation)
    if client_id:
        conditions.append(models.Product.client_id == client_id)
    
    query = select(models.Product).where(
        and_(*conditions)
    ).order_by(
        models.Product.name
    ).offset(offset).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def create_product_async(db: AsyncSession, product: Dict[str, Any], product_id: str):
    """Create a new product"""
    db_product = models.Product(id=product_id, **product)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def update_product_async(db: AsyncSession, product_id: str, product: Dict[str, Any], client_id: Optional[str] = None):
    """Update an existing product - optionally filtered by client"""
    query = select(models.Product).where(models.Product.id == product_id)
    
    # Add client filter if provided (for multi-tenant isolation)
    if client_id:
        query = query.where(models.Product.client_id == client_id)
    
    result = await db.execute(query)
    db_product = result.scalar_one_or_none()
    
    if db_product:
        for key, value in product.items():
            setattr(db_product, key, value)
        db_product.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_product)
    return db_product

async def delete_product_async(db: AsyncSession, product_id: str, client_id: Optional[str] = None):
    """Delete a product - optionally filtered by client"""
    query = select(models.Product).where(models.Product.id == product_id)
    
    # Add client filter if provided (for multi-tenant isolation)
    if client_id:
        query = query.where(models.Product.client_id == client_id)
    
    result = await db.execute(query)
    db_product = result.scalar_one_or_none()
    
    if db_product:
        await db.delete(db_product)
        await db.commit()
    return db_product

async def get_low_stock_products_async(db: AsyncSession, threshold: int = 10, client_id: Optional[str] = None):
    """Get products with stock below threshold using SQL filtering - filtered by client"""
    query = select(models.Product).where(
        and_(
            models.Product.stock <= threshold,
            models.Product.status == "Active"
        )
    )
    
    # Apply client filter (CRITICAL for multi-tenant isolation)
    if client_id:
        query = query.where(models.Product.client_id == client_id)
    
    query = query.order_by(models.Product.stock.asc(), models.Product.name)
    
    result = await db.execute(query)
    return result.scalars().all()

# ==================== CLIENTS ====================

async def get_client_async(db: AsyncSession, client_id: str):
    """Get a single client by ID"""
    result = await db.execute(
        select(models.Client).where(models.Client.id == client_id)
    )
    return result.scalar_one_or_none()

async def get_clients_async(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get clients with pagination"""
    query = select(models.Client).order_by(desc(models.Client.join_date)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_client_by_email_async(db: AsyncSession, email: str):
    """Get client by email"""
    result = await db.execute(
        select(models.Client).where(models.Client.email == email)
    )
    return result.scalar_one_or_none()

async def create_client_async(db: AsyncSession, client: Dict[str, Any], client_id: str):
    """Create a new client"""
    db_client = models.Client(id=client_id, **client)
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client

async def update_client_async(db: AsyncSession, client_id: str, client: Dict[str, Any]):
    """Update an existing client"""
    result = await db.execute(
        select(models.Client).where(models.Client.id == client_id)
    )
    db_client = result.scalar_one_or_none()
    
    if db_client:
        for key, value in client.items():
            setattr(db_client, key, value)
        db_client.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_client)
    return db_client

async def delete_client_async(db: AsyncSession, client_id: str):
    """Delete a client"""
    result = await db.execute(
        select(models.Client).where(models.Client.id == client_id)
    )
    db_client = result.scalar_one_or_none()
    
    if db_client:
        await db.delete(db_client)
        await db.commit()
    return db_client

# ==================== ORDERS ====================

async def create_order_async(db: AsyncSession, order: Dict[str, Any], order_id: str):
    """Create a new order with generated order number"""
    # Generate order number if not provided
    if 'order_number' not in order or not order['order_number']:
        order['order_number'] = await generate_order_number_async(db)
    
    db_order = models.Order(id=order_id, **order)
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order

async def update_order_async(db: AsyncSession, order_id: str, order: Dict[str, Any]):
    """Update an existing order"""
    result = await db.execute(
        select(models.Order).where(models.Order.id == order_id)
    )
    db_order = result.scalar_one_or_none()
    
    if db_order:
        for key, value in order.items():
            setattr(db_order, key, value)
        db_order.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_order)
    return db_order

async def delete_order_async(db: AsyncSession, order_id: str):
    """Delete an order"""
    result = await db.execute(
        select(models.Order).where(models.Order.id == order_id)
    )
    db_order = result.scalar_one_or_none()
    
    if db_order:
        await db.delete(db_order)
        await db.commit()
    return db_order

async def get_order_async(db: AsyncSession, order_id: str, client_id: Optional[str] = None):
    """Get a single order by ID - optionally filtered by client"""
    query = select(models.Order).where(models.Order.id == order_id)
    
    # Add client filter if provided (for multi-tenant isolation)
    if client_id:
        query = query.where(models.Order.client_id == client_id)
    
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_order_by_number_async(db: AsyncSession, order_number: str):
    """Get order by order number"""
    result = await db.execute(
        select(models.Order).where(models.Order.order_number == order_number)
    )
    return result.scalar_one_or_none()

async def get_orders_async(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    customer_name: Optional[str] = None,
    client_id: Optional[str] = None
):
    """Get orders with optional filtering"""
    query = select(models.Order)
    
    # Apply filters at SQL level
    if status:
        query = query.where(models.Order.status == status)
    if customer_name:
        query = query.where(
            func.lower(models.Order.customer_name).like(f"%{customer_name.lower()}%")
        )
    if client_id:
        query = query.where(models.Order.client_id == client_id)
    
    query = query.order_by(desc(models.Order.date)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_orders_by_status_async(
    db: AsyncSession,
    status: str,
    skip: int = 0,
    limit: int = 100
):
    """Get orders by status with SQL filtering"""
    query = select(models.Order).where(
        func.lower(models.Order.status) == status.lower()
    ).order_by(desc(models.Order.date)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_orders_by_client_async(
    db: AsyncSession,
    client_id: str,
    skip: int = 0,
    limit: int = 100
):
    """Get orders by client ID with SQL filtering"""
    query = select(models.Order).where(
        models.Order.client_id == client_id
    ).order_by(desc(models.Order.date)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def generate_order_number_async(db: AsyncSession) -> str:
    """Generate sequential order number"""
    result = await db.execute(
        select(models.Order)
        .where(models.Order.order_number.isnot(None))
        .order_by(desc(models.Order.created_at))
        .limit(1)
    )
    latest_order = result.scalar_one_or_none()
    
    if latest_order and latest_order.order_number:
        try:
            current_number = int(latest_order.order_number.split('-')[1])
            next_number = current_number + 1
        except (IndexError, ValueError):
            next_number = 1
    else:
        next_number = 1
    
    return f"ORD-{next_number:06d}"

# ==================== CAMPAIGNS ====================

async def get_campaign_async(db: AsyncSession, campaign_id: str):
    """Get a single campaign by ID"""
    result = await db.execute(
        select(models.Campaign).where(models.Campaign.id == campaign_id)
    )
    return result.scalar_one_or_none()

async def get_campaigns_async(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None
):
    """Get campaigns with optional filtering"""
    query = select(models.Campaign)
    
    if status:
        query = query.where(models.Campaign.status == status)
    
    query = query.order_by(desc(models.Campaign.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def create_campaign_async(db: AsyncSession, campaign: Dict[str, Any], campaign_id: str):
    """Create a new campaign"""
    db_campaign = models.Campaign(id=campaign_id, **campaign)
    db.add(db_campaign)
    await db.commit()
    await db.refresh(db_campaign)
    return db_campaign

async def update_campaign_async(db: AsyncSession, campaign_id: str, campaign: Dict[str, Any]):
    """Update an existing campaign"""
    result = await db.execute(
        select(models.Campaign).where(models.Campaign.id == campaign_id)
    )
    db_campaign = result.scalar_one_or_none()
    
    if db_campaign:
        for key, value in campaign.items():
            setattr(db_campaign, key, value)
        db_campaign.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_campaign)
    return db_campaign

async def delete_campaign_async(db: AsyncSession, campaign_id: str):
    """Delete a campaign"""
    result = await db.execute(
        select(models.Campaign).where(models.Campaign.id == campaign_id)
    )
    db_campaign = result.scalar_one_or_none()
    
    if db_campaign:
        await db.delete(db_campaign)
        await db.commit()
    return db_campaign

# ==================== DISCOUNTS ====================

async def get_discount_async(db: AsyncSession, discount_id: str, client_id: Optional[str] = None):
    """Get a single discount by ID - optionally filtered by client"""
    query = select(models.Discount).where(models.Discount.id == discount_id)
    
    # Add client filter if provided (for multi-tenant isolation)
    if client_id:
        query = query.where(models.Discount.client_id == client_id)
    
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_discounts_async(db: AsyncSession, skip: int = 0, limit: int = 100, client_id: Optional[str] = None):
    """Get discounts with pagination - filtered by client"""
    query = select(models.Discount)
    
    # Apply client filter first (CRITICAL for multi-tenant isolation)
    if client_id:
        query = query.where(models.Discount.client_id == client_id)
    
    # Order by created_at desc and apply pagination
    query = query.order_by(desc(models.Discount.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_active_discounts_async(db: AsyncSession, client_id: Optional[str] = None):
    """Get only active discounts - filtered by client"""
    query = select(models.Discount).where(models.Discount.is_active == True)
    
    # Apply client filter (CRITICAL for multi-tenant isolation)
    if client_id:
        query = query.where(models.Discount.client_id == client_id)
    
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
    result = await db.execute(
        select(models.Discount).where(models.Discount.id == discount_id)
    )
    db_discount = result.scalar_one_or_none()
    
    if db_discount:
        for key, value in discount.items():
            setattr(db_discount, key, value)
        db_discount.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_discount)
    return db_discount

async def delete_discount_async(db: AsyncSession, discount_id: str):
    """Delete a discount"""
    result = await db.execute(
        select(models.Discount).where(models.Discount.id == discount_id)
    )
    db_discount = result.scalar_one_or_none()
    
    if db_discount:
        await db.delete(db_discount)
        await db.commit()
    return db_discount

# ==================== DASHBOARD STATS ====================

async def get_dashboard_stats_async(db: AsyncSession):
    """Get dashboard statistics with async queries"""
    # Count queries
    total_products_result = await db.execute(select(func.count(models.Product.id)))
    total_products = total_products_result.scalar()
    
    active_products_result = await db.execute(
        select(func.count(models.Product.id)).where(models.Product.status == 'Active')
    )
    active_products = active_products_result.scalar()
    
    total_orders_result = await db.execute(select(func.count(models.Order.id)))
    total_orders = total_orders_result.scalar()
    
    pending_orders_result = await db.execute(
        select(func.count(models.Order.id)).where(models.Order.status == 'Pending')
    )
    pending_orders = pending_orders_result.scalar()
    
    total_clients_result = await db.execute(select(func.count(models.Client.id)))
    total_clients = total_clients_result.scalar()
    
    # Revenue calculation
    revenue_result = await db.execute(
        select(func.sum(models.Order.total)).where(
            models.Order.status.in_(['Shipped', 'Delivered'])
        )
    )
    total_revenue = revenue_result.scalar() or 0.0
    
    # Sales data for last 30 days (optimized with single query)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # This could be further optimized with window functions, but for now keep it simple
    sales_data = []
    for i in range(30):
        day = thirty_days_ago + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        daily_sales_result = await db.execute(
            select(func.sum(models.Order.total)).where(
                and_(
                    models.Order.date >= day_start,
                    models.Order.date <= day_end,
                    models.Order.status.in_(['Shipped', 'Delivered'])
                )
            )
        )
        daily_sales = daily_sales_result.scalar() or 0.0
        
        sales_data.append({
            "name": day.strftime("%b %d"),
            "sales": daily_sales
        })
    
    return {
        "total_products": total_products,
        "active_products": active_products,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_clients": total_clients,
        "total_revenue": total_revenue,
        "sales_data": sales_data
    }

async def get_revenue_summary_async(db: AsyncSession):
    """Get revenue summary with SQL aggregation for better performance"""
    # Get all revenue totals in a single query using CASE statements
    revenue_query = select(
        func.sum(
            func.case(
                (models.Order.status.in_(['Shipped', 'Delivered']), models.Order.total),
                else_=0
            )
        ).label('total_revenue'),
        func.sum(
            func.case(
                (models.Order.status == 'Pending', models.Order.total),
                else_=0
            )
        ).label('pending_revenue'),
        func.sum(
            func.case(
                (models.Order.status == 'Cancelled', models.Order.total),
                else_=0
            )
        ).label('cancelled_revenue'),
        func.count(
            func.case(
                (models.Order.status.in_(['Shipped', 'Delivered']), 1),
                else_=None
            )
        ).label('completed_orders'),
        func.count(
            func.case(
                (models.Order.status == 'Pending', 1),
                else_=None
            )
        ).label('pending_orders'),
        func.count(
            func.case(
                (models.Order.status == 'Cancelled', 1),
                else_=None
            )
        ).label('cancelled_orders')
    )
    
    result = await db.execute(revenue_query)
    row = result.first()
    
    return {
        "total_revenue": float(row.total_revenue or 0.0),
        "pending_revenue": float(row.pending_revenue or 0.0),
        "cancelled_revenue": float(row.cancelled_revenue or 0.0),
        "completed_orders": int(row.completed_orders or 0),
        "pending_orders": int(row.pending_orders or 0),
        "cancelled_orders": int(row.cancelled_orders or 0)
    }

# ==================== CATALOG FUNCTIONS FOR BOT ====================

async def get_catalog_summary_async(db: AsyncSession, client_id: Optional[str] = None):
    """Get catalog summary grouped by category (optimized for bot responses) - filtered by client"""
    # Get all active products with category grouping in SQL
    query = select(
        models.Product.category,
        func.count(models.Product.id).label('product_count'),
        func.min(models.Product.price).label('min_price'),
        func.max(models.Product.price).label('max_price')
    ).where(models.Product.status == 'Active')
    
    # Add client filter if provided (CRITICAL for multi-tenant isolation)
    if client_id:
        query = query.where(models.Product.client_id == client_id)
    
    query = query.group_by(models.Product.category).order_by(models.Product.category)
    
    result = await db.execute(query)
    
    categories = {}
    total_products = 0
    
    for row in result:
        categories[row.category] = {
            'count': row.product_count,
            'price_range': {
                'min': float(row.min_price),
                'max': float(row.max_price)
            }
        }
        total_products += row.product_count
    
    return {
        'categories': categories,
        'total_products': total_products,
        'total_categories': len(categories)
    }

async def get_products_with_discounts_async(
    db: AsyncSession,
    product_id: Optional[str] = None,
    category: Optional[str] = None
):
    """Get products with applicable discounts in a single optimized query"""
    # Base product query
    product_query = select(models.Product).where(models.Product.status == 'Active')
    
    if product_id:
        product_query = product_query.where(models.Product.id == product_id)
    elif category:
        product_query = product_query.where(
            func.lower(models.Product.category) == category.lower()
        )
    
    # Get products
    product_result = await db.execute(product_query)
    products = product_result.scalars().all()
    
    if not products:
        return []
    
    # Get all active discounts in one query
    discount_result = await db.execute(
        select(models.Discount).where(models.Discount.is_active == True)
    )
    discounts = discount_result.scalars().all()
    
    # Apply discounts to products in Python (this is unavoidable for complex logic)
    result = []
    for product in products:
        applicable_discounts = []
        
        for discount in discounts:
            applies = (
                discount.target == 'All' or
                (discount.target == 'Category' and discount.category == product.category) or
                (discount.target == 'Product' and discount.product_id == product.id)
            )
            if applies:
                applicable_discounts.append({
                    'name': discount.name,
                    'type': discount.type,
                    'value': discount.value
                })
        
        result.append({
            'product': product,
            'discounts': applicable_discounts
        })
    
    return result