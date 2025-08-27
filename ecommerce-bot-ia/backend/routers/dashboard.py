from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from schemas import DashboardStats
import crud_async
from auth import get_current_client

router = APIRouter()

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_async_db),
    current_client = Depends(get_current_client)
):
    """Get dashboard statistics using optimized async SQL queries - filtered by client"""
    return await crud_async.get_dashboard_stats_async(db, client_id=current_client.id)

@router.get("/dashboard/recent-orders")
async def get_recent_orders(
    limit: int = Query(10, ge=1, le=100), 
    db: AsyncSession = Depends(get_async_db),
    current_client = Depends(get_current_client)
):
    """Get recent orders with async pagination - filtered by client"""
    orders = await crud_async.get_orders_async(db, limit=limit, client_id=current_client.id)
    return orders

@router.get("/dashboard/low-stock-products")
async def get_low_stock_products(
    threshold: int = Query(10, ge=0, le=1000), 
    db: AsyncSession = Depends(get_async_db),
    current_client = Depends(get_current_client)
):
    """Get low stock products using SQL filtering - filtered by client"""
    return await crud_async.get_low_stock_products_async(db, threshold=threshold, client_id=current_client.id)

@router.get("/dashboard/revenue-summary")
async def get_revenue_summary(
    db: AsyncSession = Depends(get_async_db),
    current_client = Depends(get_current_client)
):
    """Get revenue summary with optimized SQL aggregation - filtered by client"""
    return await crud_async.get_revenue_summary_async(db, client_id=current_client.id)