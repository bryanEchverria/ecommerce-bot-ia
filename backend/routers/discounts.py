from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import uuid4
from database import get_async_db
from models import Discount as DiscountModel
from schemas import Discount, DiscountCreate, DiscountUpdate
import crud_async
from auth import get_current_client

router = APIRouter()

@router.get("/discounts", response_model=List[Discount])
async def get_discounts(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000), 
    db: AsyncSession = Depends(get_async_db),
    current_client = Depends(get_current_client)
):
    """Get discounts with async pagination - filtered by client"""
    return await crud_async.get_discounts_async(db, skip=skip, limit=limit, client_id=current_client.id)

@router.get("/discounts/{discount_id}", response_model=Discount)
async def get_discount(
    discount_id: str, 
    db: AsyncSession = Depends(get_async_db),
    current_client = Depends(get_current_client)
):
    """Get a single discount by ID - filtered by client"""
    discount = await crud_async.get_discount_async(db, discount_id=discount_id, client_id=current_client.id)
    if discount is None:
        raise HTTPException(status_code=404, detail="Discount not found")
    return discount

@router.get("/discounts/active/list", response_model=List[Discount])
async def get_active_discounts(
    db: AsyncSession = Depends(get_async_db),
    current_client = Depends(get_current_client)
):
    """Get only active discounts using SQL filtering - filtered by client"""
    return await crud_async.get_active_discounts_async(db, client_id=current_client.id)

@router.post("/discounts", response_model=Discount)
async def create_discount(
    discount: DiscountCreate, 
    db: AsyncSession = Depends(get_async_db),
    current_client = Depends(get_current_client)
):
    """Create a new discount - associated with current client"""
    discount_id = str(uuid4())
    discount_data = discount.dict()
    discount_data['client_id'] = current_client.id  # Associate with current client
    return await crud_async.create_discount_async(db=db, discount=discount_data, discount_id=discount_id)

@router.put("/discounts/{discount_id}", response_model=Discount)
async def update_discount(
    discount_id: str, 
    discount: DiscountUpdate, 
    db: AsyncSession = Depends(get_async_db),
    current_client = Depends(get_current_client)
):
    """Update an existing discount - only if belongs to current client"""
    db_discount = await crud_async.get_discount_async(db, discount_id=discount_id, client_id=current_client.id)
    if db_discount is None:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    return await crud_async.update_discount_async(db=db, discount_id=discount_id, discount=discount.dict(exclude_unset=True))

@router.delete("/discounts/{discount_id}")
async def delete_discount(
    discount_id: str, 
    db: AsyncSession = Depends(get_async_db),
    current_client = Depends(get_current_client)
):
    """Delete a discount - only if belongs to current client"""
    db_discount = await crud_async.get_discount_async(db, discount_id=discount_id, client_id=current_client.id)
    if db_discount is None:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    await crud_async.delete_discount_async(db=db, discount_id=discount_id)
    return {"message": "Discount deleted successfully"}