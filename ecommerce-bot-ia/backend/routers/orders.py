from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import uuid4
from database import get_async_db
from models import Order as OrderModel
from schemas import Order, OrderCreate, OrderUpdate
import crud_async

router = APIRouter()

@router.get("/orders", response_model=List[Order])
async def get_orders(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by status"),
    customer_name: Optional[str] = Query(None, description="Filter by customer name"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get orders with optional SQL-level filtering"""
    return await crud_async.get_orders_async(
        db, skip=skip, limit=limit, status=status, 
        customer_name=customer_name
    )

@router.get("/orders/{order_id}", response_model=Order)
async def get_order(
    order_id: str, 
    db: AsyncSession = Depends(get_async_db)
):
    """Get a single order by ID"""
    order = await crud_async.get_order_async(db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/orders", response_model=Order)
async def create_order(
    order: OrderCreate, 
    order_id: str = None, 
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new order with auto-generated order number"""
    if order_id is None:
        order_id = str(uuid4())
    order_data = order.dict()
    return await crud_async.create_order_async(db=db, order=order_data, order_id=order_id)

@router.put("/orders/{order_id}", response_model=Order)
async def update_order(
    order_id: str, 
    order: OrderUpdate, 
    db: AsyncSession = Depends(get_async_db)
):
    """Update an existing order"""
    db_order = await crud_async.get_order_async(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return await crud_async.update_order_async(db=db, order_id=order_id, order=order.dict(exclude_unset=True))

@router.delete("/orders/{order_id}")
async def delete_order(order_id: str, db: AsyncSession = Depends(get_async_db)):
    """Delete an order"""
    db_order = await crud_async.get_order_async(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    await crud_async.delete_order_async(db=db, order_id=order_id)
    return {"message": "Order deleted successfully"}

@router.get("/orders/status/{status}", response_model=List[Order])
async def get_orders_by_status(
    status: str, 
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
):
    """Get orders by status using SQL filtering"""
    return await crud_async.get_orders_by_status_async(db, status=status, skip=skip, limit=limit)

@router.get("/orders/client/{client_id}", response_model=List[Order])
async def get_orders_by_client(
    client_id: str, 
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
):
    """Get orders by client using SQL filtering"""
    return await crud_async.get_orders_by_client_async(db, client_id=client_id, skip=skip, limit=limit)

@router.get("/orders/number/{order_number}", response_model=Order)
async def get_order_by_number(order_number: str, db: AsyncSession = Depends(get_async_db)):
    """Get order by order number"""
    order = await crud_async.get_order_by_number_async(db, order_number=order_number)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order