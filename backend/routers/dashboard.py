from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from schemas import DashboardStats
import crud_async

router = APIRouter()

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_async_db)):
    """Get dashboard statistics using optimized async SQL queries"""
    return await crud_async.get_dashboard_stats_async(db)

@router.get("/dashboard/recent-orders")
async def get_recent_orders(
    limit: int = Query(10, ge=1, le=100), 
    db: AsyncSession = Depends(get_async_db)
):
    """Get recent orders with async pagination"""
    orders = await crud_async.get_orders_async(db, limit=limit)
    return orders

@router.get("/dashboard/low-stock-products")
async def get_low_stock_products(
    threshold: int = Query(10, ge=0, le=1000), 
    db: AsyncSession = Depends(get_async_db)
):
    """Get low stock products using SQL filtering"""
    return await crud_async.get_low_stock_products_async(db, threshold=threshold)

@router.get("/dashboard/revenue-summary")
async def get_revenue_summary(db: AsyncSession = Depends(get_async_db)):
    """Get revenue summary with optimized SQL aggregation"""
    return await crud_async.get_revenue_summary_async(db)