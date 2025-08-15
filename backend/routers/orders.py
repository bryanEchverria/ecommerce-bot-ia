from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
from database import get_db
from models import Order as OrderModel
from schemas import Order, OrderCreate, OrderUpdate
import crud

router = APIRouter()

@router.get("/orders", response_model=List[Order])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_orders(db, skip=skip, limit=limit)

@router.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/orders", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    order_id = str(uuid4())
    return crud.create_order(db=db, order=order.dict(), order_id=order_id)

@router.put("/orders/{order_id}", response_model=Order)
def update_order(order_id: str, order: OrderUpdate, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return crud.update_order(db=db, order_id=order_id, order=order.dict(exclude_unset=True))

@router.delete("/orders/{order_id}")
def delete_order(order_id: str, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    crud.delete_order(db=db, order_id=order_id)
    return {"message": "Order deleted successfully"}

@router.get("/orders/status/{status}", response_model=List[Order])
def get_orders_by_status(status: str, db: Session = Depends(get_db)):
    orders = crud.get_orders(db)
    return [order for order in orders if order.status.lower() == status.lower()]

@router.get("/orders/client/{client_id}", response_model=List[Order])
def get_orders_by_client(client_id: str, db: Session = Depends(get_db)):
    orders = crud.get_orders(db)
    return [order for order in orders if order.client_id == client_id]