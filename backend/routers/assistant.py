from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
import json
from database import get_db
import crud

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    data: Dict[str, Any]

@router.post("/assistant/query", response_model=QueryResponse)
def process_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Process a natural language query and return relevant data
    """
    query = request.query.lower()
    
    # Get all data
    products = crud.get_products(db)
    orders = crud.get_orders(db)
    clients = crud.get_clients(db)
    campaigns = crud.get_campaigns(db)
    discounts = crud.get_discounts(db)
    
    # Convert SQLAlchemy objects to dictionaries for JSON serialization
    products_data = []
    for product in products:
        product_dict = {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "sale_price": product.sale_price,
            "stock": product.stock,
            "image_url": product.image_url,
            "status": product.status,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None
        }
        products_data.append(product_dict)
    
    orders_data = []
    for order in orders:
        order_dict = {
            "id": order.id,
            "customer_name": order.customer_name,
            "client_id": order.client_id,
            "date": order.date.isoformat() if order.date else None,
            "total": order.total,
            "status": order.status,
            "items": order.items,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None
        }
        orders_data.append(order_dict)
    
    clients_data = []
    for client in clients:
        client_dict = {
            "id": client.id,
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "join_date": client.join_date.isoformat() if client.join_date else None,
            "total_spent": client.total_spent,
            "avatar_url": client.avatar_url,
            "created_at": client.created_at.isoformat() if client.created_at else None,
            "updated_at": client.updated_at.isoformat() if client.updated_at else None
        }
        clients_data.append(client_dict)
    
    campaigns_data = []
    for campaign in campaigns:
        campaign_dict = {
            "id": campaign.id,
            "name": campaign.name,
            "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
            "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
            "status": campaign.status,
            "budget": campaign.budget,
            "clicks": campaign.clicks,
            "conversions": campaign.conversions,
            "image_url": campaign.image_url,
            "product_ids": json.loads(campaign.product_ids) if campaign.product_ids else [],
            "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
            "updated_at": campaign.updated_at.isoformat() if campaign.updated_at else None
        }
        campaigns_data.append(campaign_dict)
    
    discounts_data = []
    for discount in discounts:
        discount_dict = {
            "id": discount.id,
            "name": discount.name,
            "type": discount.type,
            "value": discount.value,
            "target": discount.target,
            "category": discount.category,
            "product_id": discount.product_id,
            "is_active": discount.is_active,
            "created_at": discount.created_at.isoformat() if discount.created_at else None,
            "updated_at": discount.updated_at.isoformat() if discount.updated_at else None
        }
        discounts_data.append(discount_dict)
    
    # Simple query processing (this could be enhanced with NLP)
    response_text = "I found the following information based on your query:"
    
    data = {
        "products": products_data,
        "orders": orders_data,
        "clients": clients_data,
        "campaigns": campaigns_data,
        "discounts": discounts_data,
        "query": request.query
    }
    
    # Basic query analysis
    if "product" in query:
        data["filtered_results"] = {"products": products_data[:10]}
        response_text = f"Found {len(products_data)} products in the database."
    elif "order" in query:
        data["filtered_results"] = {"orders": orders_data[:10]}
        response_text = f"Found {len(orders_data)} orders in the database."
    elif "client" in query or "customer" in query:
        data["filtered_results"] = {"clients": clients_data[:10]}
        response_text = f"Found {len(clients_data)} clients in the database."
    elif "campaign" in query:
        data["filtered_results"] = {"campaigns": campaigns_data}
        response_text = f"Found {len(campaigns_data)} campaigns in the database."
    elif "discount" in query:
        data["filtered_results"] = {"discounts": discounts_data}
        response_text = f"Found {len(discounts_data)} discounts in the database."
    
    return QueryResponse(response=response_text, data=data)

@router.get("/assistant/stats")
def get_assistant_stats(db: Session = Depends(get_db)):
    """
    Get comprehensive stats for the assistant
    """
    dashboard_stats = crud.get_dashboard_stats(db)
    
    # Add more detailed statistics
    products = crud.get_products(db)
    orders = crud.get_orders(db)
    
    # Calculate additional metrics
    low_stock_products = [p for p in products if p.stock < 10]
    high_value_orders = [o for o in orders if o.total > 1000]
    
    stats = {
        **dashboard_stats,
        "low_stock_products": len(low_stock_products),
        "high_value_orders": len(high_value_orders),
        "average_order_value": sum(o.total for o in orders) / len(orders) if orders else 0,
        "top_categories": {},
        "recent_activity": {
            "new_orders_today": 0,
            "new_clients_today": 0
        }
    }
    
    # Calculate top categories
    category_sales = {}
    for product in products:
        if product.category not in category_sales:
            category_sales[product.category] = 0
        category_sales[product.category] += product.stock * product.price
    
    stats["top_categories"] = dict(sorted(category_sales.items(), key=lambda x: x[1], reverse=True)[:5])
    
    return stats