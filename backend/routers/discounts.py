from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
from database import get_db
from models import Discount as DiscountModel
from schemas import Discount, DiscountCreate, DiscountUpdate
import crud

router = APIRouter()

@router.get("/discounts", response_model=List[Discount])
def get_discounts(db: Session = Depends(get_db)):
    return crud.get_discounts(db)

@router.get("/discounts/{discount_id}", response_model=Discount)
def get_discount(discount_id: str, db: Session = Depends(get_db)):
    discount = crud.get_discount(db, discount_id=discount_id)
    if discount is None:
        raise HTTPException(status_code=404, detail="Discount not found")
    return discount

@router.get("/discounts/active/list", response_model=List[Discount])
def get_active_discounts(db: Session = Depends(get_db)):
    return crud.get_active_discounts(db)

@router.post("/discounts", response_model=Discount)
def create_discount(discount: DiscountCreate, db: Session = Depends(get_db)):
    discount_id = str(uuid4())
    return crud.create_discount(db=db, discount=discount.dict(), discount_id=discount_id)

@router.put("/discounts/{discount_id}", response_model=Discount)
def update_discount(discount_id: str, discount: DiscountUpdate, db: Session = Depends(get_db)):
    db_discount = crud.get_discount(db, discount_id=discount_id)
    if db_discount is None:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    return crud.update_discount(db=db, discount_id=discount_id, discount=discount.dict(exclude_unset=True))

@router.delete("/discounts/{discount_id}")
def delete_discount(discount_id: str, db: Session = Depends(get_db)):
    db_discount = crud.get_discount(db, discount_id=discount_id)
    if db_discount is None:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    crud.delete_discount(db=db, discount_id=discount_id)
    return {"message": "Discount deleted successfully"}