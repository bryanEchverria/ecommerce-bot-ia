from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import DashboardStats
import crud

router = APIRouter()

@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)

@router.get("/dashboard/recent-orders")
def get_recent_orders(limit: int = 10, db: Session = Depends(get_db)):
    orders = crud.get_orders(db, limit=limit)
    return orders

@router.get("/dashboard/low-stock-products")
def get_low_stock_products(threshold: int = 10, db: Session = Depends(get_db)):
    products = crud.get_products(db)
    return [product for product in products if product.stock <= threshold]

@router.get("/dashboard/revenue-summary")
def get_revenue_summary(db: Session = Depends(get_db)):
    orders = crud.get_orders(db)
    
    total_revenue = sum(order.total for order in orders if order.status in ['Shipped', 'Delivered'])
    pending_revenue = sum(order.total for order in orders if order.status == 'Pending')
    cancelled_revenue = sum(order.total for order in orders if order.status == 'Cancelled')
    
    return {
        "total_revenue": total_revenue,
        "pending_revenue": pending_revenue,
        "cancelled_revenue": cancelled_revenue,
        "completed_orders": len([o for o in orders if o.status in ['Shipped', 'Delivered']]),
        "pending_orders": len([o for o in orders if o.status == 'Pending']),
        "cancelled_orders": len([o for o in orders if o.status == 'Cancelled'])
    }