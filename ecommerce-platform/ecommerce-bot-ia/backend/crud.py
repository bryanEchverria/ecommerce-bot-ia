from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta
import models
import schemas

# PRODUCTS
def get_product(db: Session, product_id: str):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: Dict[str, Any], product_id: str):
    db_product = models.Product(id=product_id, **product)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: str, product: Dict[str, Any]):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        for key, value in product.items():
            setattr(db_product, key, value)
        db_product.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: str):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product

# CLIENTS
def get_client(db: Session, client_id: str):
    return db.query(models.Client).filter(models.Client.id == client_id).first()

def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Client).offset(skip).limit(limit).all()

def get_client_by_email(db: Session, email: str):
    return db.query(models.Client).filter(models.Client.email == email).first()

def create_client(db: Session, client: Dict[str, Any], client_id: str):
    db_client = models.Client(id=client_id, **client)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def update_client(db: Session, client_id: str, client: Dict[str, Any]):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client:
        for key, value in client.items():
            setattr(db_client, key, value)
        db_client.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_client)
    return db_client

def delete_client(db: Session, client_id: str):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client:
        db.delete(db_client)
        db.commit()
    return db_client

# ORDERS
def get_order(db: Session, order_id: str):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def get_order_by_number(db: Session, order_number: str):
    return db.query(models.Order).filter(models.Order.order_number == order_number).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).order_by(desc(models.Order.date)).offset(skip).limit(limit).all()

def generate_order_number(db: Session) -> str:
    """Generate sequential order number"""
    # Get the latest order number
    latest_order = db.query(models.Order).filter(
        models.Order.order_number.isnot(None)
    ).order_by(desc(models.Order.created_at)).first()
    
    if latest_order and latest_order.order_number:
        # Extract number from format ORD-XXXXXX
        try:
            current_number = int(latest_order.order_number.split('-')[1])
            next_number = current_number + 1
        except (IndexError, ValueError):
            next_number = 1
    else:
        next_number = 1
    
    return f"ORD-{next_number:06d}"

def create_order(db: Session, order: Dict[str, Any], order_id: str):
    # Generate order number if not provided
    if 'order_number' not in order or not order['order_number']:
        order['order_number'] = generate_order_number(db)
    
    db_order = models.Order(id=order_id, **order)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def update_order(db: Session, order_id: str, order: Dict[str, Any]):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        for key, value in order.items():
            setattr(db_order, key, value)
        db_order.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_order)
    return db_order

def delete_order(db: Session, order_id: str):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        db.delete(db_order)
        db.commit()
    return db_order

# CAMPAIGNS
def get_campaign(db: Session, campaign_id: str):
    return db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()

def get_campaigns(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Campaign).offset(skip).limit(limit).all()

def create_campaign(db: Session, campaign: Dict[str, Any], campaign_id: str):
    db_campaign = models.Campaign(id=campaign_id, **campaign)
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def update_campaign(db: Session, campaign_id: str, campaign: Dict[str, Any]):
    db_campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if db_campaign:
        for key, value in campaign.items():
            setattr(db_campaign, key, value)
        db_campaign.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_campaign)
    return db_campaign

def delete_campaign(db: Session, campaign_id: str):
    db_campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if db_campaign:
        db.delete(db_campaign)
        db.commit()
    return db_campaign

# DISCOUNTS
def get_discount(db: Session, discount_id: str):
    return db.query(models.Discount).filter(models.Discount.id == discount_id).first()

def get_discounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Discount).offset(skip).limit(limit).all()

def get_active_discounts(db: Session):
    return db.query(models.Discount).filter(models.Discount.is_active == True).all()

def create_discount(db: Session, discount: Dict[str, Any], discount_id: str):
    db_discount = models.Discount(id=discount_id, **discount)
    db.add(db_discount)
    db.commit()
    db.refresh(db_discount)
    return db_discount

def update_discount(db: Session, discount_id: str, discount: Dict[str, Any]):
    db_discount = db.query(models.Discount).filter(models.Discount.id == discount_id).first()
    if db_discount:
        for key, value in discount.items():
            setattr(db_discount, key, value)
        db_discount.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_discount)
    return db_discount

def delete_discount(db: Session, discount_id: str):
    db_discount = db.query(models.Discount).filter(models.Discount.id == discount_id).first()
    if db_discount:
        db.delete(db_discount)
        db.commit()
    return db_discount

# DASHBOARD STATS
def get_dashboard_stats(db: Session):
    total_products = db.query(models.Product).count()
    active_products = db.query(models.Product).filter(models.Product.status == 'Active').count()
    total_orders = db.query(models.Order).count()
    pending_orders = db.query(models.Order).filter(models.Order.status == 'Pending').count()
    total_clients = db.query(models.Client).count()
    
    # Calculate total revenue from completed orders
    total_revenue = db.query(func.sum(models.Order.total)).filter(
        models.Order.status.in_(['Shipped', 'Delivered'])
    ).scalar() or 0.0
    
    # Get sales data for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    sales_data = []
    
    for i in range(30):
        day = thirty_days_ago + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        daily_sales = db.query(func.sum(models.Order.total)).filter(
            models.Order.date >= day_start,
            models.Order.date <= day_end,
            models.Order.status.in_(['Shipped', 'Delivered'])
        ).scalar() or 0.0
        
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