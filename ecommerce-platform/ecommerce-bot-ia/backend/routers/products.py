from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import uuid4
from database import get_async_db
from models import Product as ProductModel
from schemas import Product, ProductCreate, ProductUpdate
from auth import get_current_client, TenantClient
from tenant_middleware import get_tenant_id
import crud_async

router = APIRouter()

@router.get("/products", response_model=List[Product])
async def get_products(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get products with optional filtering using SQL WHERE clauses - filtered by tenant"""
    # Get tenant_id from middleware context
    tenant_id = get_tenant_id()
    print(f"DEBUG: Products endpoint - tenant_id = {tenant_id}")  # DEBUG
    
    return await crud_async.get_products_async(
        db, skip=skip, limit=limit, status=status, category=category, client_id=tenant_id
    )

@router.get("/products/{product_id}", response_model=Product)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a single product by ID - filtered by tenant"""
    # Get tenant_id from middleware context
    tenant_id = get_tenant_id()
    
    product = await crud_async.get_product_async(db, product_id=product_id, client_id=tenant_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products", response_model=Product)
async def create_product(
    product: ProductCreate,
    current_client: TenantClient = Depends(get_current_client), 
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new product - assigned to current tenant"""
    product_id = str(uuid4())
    product_data = product.dict()
    product_data['client_id'] = current_client.id  # Assign to current tenant
    return await crud_async.create_product_async(db=db, product=product_data, product_id=product_id)

@router.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: str, 
    product: ProductUpdate, 
    db: AsyncSession = Depends(get_async_db)
):
    """Update an existing product"""
    db_product = await crud_async.get_product_async(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return await crud_async.update_product_async(
        db=db, product_id=product_id, product=product.dict(exclude_unset=True)
    )

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: str, 
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a product"""
    db_product = await crud_async.get_product_async(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await crud_async.delete_product_async(db=db, product_id=product_id)
    return {"message": "Product deleted successfully"}

@router.get("/products/category/{category}", response_model=List[Product])
async def get_products_by_category(
    category: str, 
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db)
):
    """Get products by category using optimized SQL filtering"""
    return await crud_async.get_products_by_category_async(
        db=db, category=category, limit=limit, offset=offset, status="Active"
    )

@router.get("/products/status/{status}", response_model=List[Product])
async def get_products_by_status(
    status: str, 
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db)
):
    """Get products by status using optimized SQL filtering"""
    return await crud_async.get_products_async(
        db=db, skip=offset, limit=limit, status=status
    )