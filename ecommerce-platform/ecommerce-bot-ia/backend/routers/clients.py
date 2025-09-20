from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import uuid4
from database import get_async_db
from models import Client as ClientModel
from schemas import Client, ClientCreate, ClientUpdate
import crud_async

router = APIRouter()

@router.get("/clients", response_model=List[Client])
async def get_clients(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000), 
    db: AsyncSession = Depends(get_async_db)
):
    """Get clients with async pagination"""
    return await crud_async.get_clients_async(db, skip=skip, limit=limit)

@router.get("/clients/{client_id}", response_model=Client)
async def get_client(client_id: str, db: AsyncSession = Depends(get_async_db)):
    """Get a single client by ID"""
    client = await crud_async.get_client_async(db, client_id=client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.get("/clients/email/{email}", response_model=Client)
async def get_client_by_email(email: str, db: AsyncSession = Depends(get_async_db)):
    """Get client by email address"""
    client = await crud_async.get_client_by_email_async(db, email=email)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.post("/clients", response_model=Client)
async def create_client(client: ClientCreate, db: AsyncSession = Depends(get_async_db)):
    """Create a new client with email uniqueness validation"""
    # Check if client with email already exists
    db_client = await crud_async.get_client_by_email_async(db, email=client.email)
    if db_client:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    client_id = str(uuid4())
    return await crud_async.create_client_async(db=db, client=client.dict(), client_id=client_id)

@router.put("/clients/{client_id}", response_model=Client)
async def update_client(client_id: str, client: ClientUpdate, db: AsyncSession = Depends(get_async_db)):
    """Update an existing client"""
    db_client = await crud_async.get_client_async(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if email is being updated and if it already exists
    if client.email and client.email != db_client.email:
        existing_client = await crud_async.get_client_by_email_async(db, email=client.email)
        if existing_client:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    return await crud_async.update_client_async(db=db, client_id=client_id, client=client.dict(exclude_unset=True))

@router.delete("/clients/{client_id}")
async def delete_client(client_id: str, db: AsyncSession = Depends(get_async_db)):
    """Delete a client"""
    db_client = await crud_async.get_client_async(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    await crud_async.delete_client_async(db=db, client_id=client_id)
    return {"message": "Client deleted successfully"}

@router.get("/clients/{client_id}/orders")
async def get_client_orders(
    client_id: str, 
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
):
    """Get orders for a specific client using SQL filtering"""
    client = await crud_async.get_client_async(db, client_id=client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Use optimized SQL filtering instead of Python filtering
    return await crud_async.get_orders_by_client_async(db, client_id=client_id, skip=skip, limit=limit)