from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from models import Product, Campaign, Discount
import crud
import sys
import os

# Add WhatsApp bot path to import chat service
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'whatsapp-bot-fastapi'))

try:
    from services.chat_service import procesar_mensaje
except ImportError:
    procesar_mensaje = None

router = APIRouter()

# Modelo para el webhook de mensajes
class ChatMessage(BaseModel):
    telefono: str
    mensaje: str

@router.post("/bot/chat")
def process_chat_message(data: ChatMessage, db: Session = Depends(get_db)):
    """
    Endpoint principal del bot que procesa cualquier mensaje del usuario
    usando IA para analizar y responder
    """
    if not procesar_mensaje:
        return {"error": "Chat service not available"}
    
    try:
        respuesta = procesar_mensaje(db, data.telefono, data.mensaje)
        return {
            "telefono": data.telefono,
            "mensaje_usuario": data.mensaje,
            "respuesta_bot": respuesta,
            "status": "success"
        }
    except Exception as e:
        return {
            "telefono": data.telefono,
            "mensaje_usuario": data.mensaje,
            "error": str(e),
            "status": "error"
        }

@router.get("/bot/products/search")
def search_products_for_bot(
    query: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """
    Search products for WhatsApp bot responses
    Returns simplified product information
    """
    products = crud.get_products(db)
    
    # Simple keyword search
    query_lower = query.lower()
    found_products = []
    
    for product in products:
        if product.status != 'Active':
            continue
            
        name_match = query_lower in product.name.lower()
        category_match = query_lower in product.category.lower()
        
        if name_match or category_match:
            found_products.append({
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "sale_price": product.sale_price,
                "stock": product.stock,
                "status": product.status,
                "display_price": product.sale_price if product.sale_price else product.price
            })
    
    return found_products[:limit]

@router.get("/bot/products/by-category")
def get_products_by_category_for_bot(
    category: str = Query(..., description="Product category"),
    limit: int = Query(10, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """
    Get products by category for bot responses
    """
    products = crud.get_products(db)
    
    category_products = [
        {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "sale_price": product.sale_price,
            "stock": product.stock,
            "display_price": product.sale_price if product.sale_price else product.price
        }
        for product in products 
        if product.status == 'Active' and product.category.lower() == category.lower()
    ]
    
    return category_products[:limit]

@router.get("/bot/products/catalog")
def get_catalog_for_bot(db: Session = Depends(get_db)):
    """
    Get catalog summary for bot responses
    """
    products = crud.get_products(db)
    active_products = [p for p in products if p.status == 'Active']
    
    # Group by category
    categories = {}
    for product in active_products:
        if product.category not in categories:
            categories[product.category] = []
        categories[product.category].append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "sale_price": product.sale_price,
            "stock": product.stock,
            "display_price": product.sale_price if product.sale_price else product.price
        })
    
    return {
        "categories": categories,
        "total_products": len(active_products),
        "total_categories": len(categories)
    }

@router.get("/bot/campaigns/active")
def get_active_campaigns_for_bot(db: Session = Depends(get_db)):
    """
    Get active campaigns for bot responses
    """
    campaigns = crud.get_campaigns(db)
    active_campaigns = [
        {
            "id": campaign.id,
            "name": campaign.name,
            "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
            "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
            "status": campaign.status,
            "budget": campaign.budget,
            "clicks": campaign.clicks,
            "conversions": campaign.conversions
        }
        for campaign in campaigns 
        if campaign.status == "Active"
    ]
    
    return active_campaigns

@router.get("/bot/discounts/active")
def get_active_discounts_for_bot(db: Session = Depends(get_db)):
    """
    Get active discounts for bot responses
    """
    discounts = crud.get_active_discounts(db)
    
    return [
        {
            "id": discount.id,
            "name": discount.name,
            "type": discount.type,
            "value": discount.value,
            "target": discount.target,
            "category": discount.category,
            "product_id": discount.product_id,
            "is_active": discount.is_active
        }
        for discount in discounts
    ]

@router.get("/bot/product/{product_id}")
def get_product_details_for_bot(product_id: str, db: Session = Depends(get_db)):
    """
    Get detailed product information for bot
    """
    product = crud.get_product(db, product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get applicable discounts
    discounts = crud.get_active_discounts(db)
    applicable_discounts = []
    
    for discount in discounts:
        applies = (
            discount.target == 'All' or
            (discount.target == 'Category' and discount.category == product.category) or
            (discount.target == 'Product' and discount.product_id == product.id)
        )
        if applies:
            applicable_discounts.append({
                "name": discount.name,
                "type": discount.type,
                "value": discount.value
            })
    
    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "price": product.price,
        "sale_price": product.sale_price,
        "stock": product.stock,
        "status": product.status,
        "image_url": product.image_url,
        "display_price": product.sale_price if product.sale_price else product.price,
        "applicable_discounts": applicable_discounts
    }