from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
from database import get_db
from models import Client as ClientModel
from schemas import Client, ClientCreate, ClientUpdate
import crud

router = APIRouter()

@router.get("/clients", response_model=List[Client])
def get_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_clients(db, skip=skip, limit=limit)

@router.get("/clients/{client_id}", response_model=Client)
def get_client(client_id: str, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id=client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.get("/clients/email/{email}", response_model=Client)
def get_client_by_email(email: str, db: Session = Depends(get_db)):
    client = crud.get_client_by_email(db, email=email)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.post("/clients", response_model=Client)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    # Check if client with email already exists
    db_client = crud.get_client_by_email(db, email=client.email)
    if db_client:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    client_id = str(uuid4())
    return crud.create_client(db=db, client=client.dict(), client_id=client_id)

@router.put("/clients/{client_id}", response_model=Client)
def update_client(client_id: str, client: ClientUpdate, db: Session = Depends(get_db)):
    db_client = crud.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if email is being updated and if it already exists
    if client.email and client.email != db_client.email:
        existing_client = crud.get_client_by_email(db, email=client.email)
        if existing_client:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.update_client(db=db, client_id=client_id, client=client.dict(exclude_unset=True))

@router.delete("/clients/{client_id}")
def delete_client(client_id: str, db: Session = Depends(get_db)):
    db_client = crud.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    crud.delete_client(db=db, client_id=client_id)
    return {"message": "Client deleted successfully"}

@router.get("/clients/{client_id}/orders")
def get_client_orders(client_id: str, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id=client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    orders = crud.get_orders(db)
    client_orders = [order for order in orders if order.client_id == client_id]
    return client_orders