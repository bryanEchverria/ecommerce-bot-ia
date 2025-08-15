from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
from database import get_db
from models import Product as ProductModel
from schemas import Product, ProductCreate, ProductUpdate
import crud

router = APIRouter()

@router.get("/products", response_model=List[Product])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_products(db, skip=skip, limit=limit)

@router.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    product_id = str(uuid4())
    return crud.create_product(db=db, product=product.dict(), product_id=product_id)

@router.put("/products/{product_id}", response_model=Product)
def update_product(product_id: str, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return crud.update_product(db=db, product_id=product_id, product=product.dict(exclude_unset=True))

@router.delete("/products/{product_id}")
def delete_product(product_id: str, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    crud.delete_product(db=db, product_id=product_id)
    return {"message": "Product deleted successfully"}

@router.get("/products/category/{category}", response_model=List[Product])
def get_products_by_category(category: str, db: Session = Depends(get_db)):
    products = crud.get_products(db)
    return [product for product in products if product.category.lower() == category.lower()]

@router.get("/products/status/{status}", response_model=List[Product])
def get_products_by_status(status: str, db: Session = Depends(get_db)):
    products = crud.get_products(db)
    return [product for product in products if product.status.lower() == status.lower()]