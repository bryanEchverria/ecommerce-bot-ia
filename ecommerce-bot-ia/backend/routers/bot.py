from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from database import get_async_db, get_db
from models import Product, Campaign, Discount, FlowPedido
from auth import get_current_client, TenantClient
import crud_async
import sys
import os

# Import tenant middleware functions for debugging
try:
    from tenant_middleware import get_tenant_id, get_cache_stats
except ImportError:
    get_tenant_id = None
    get_cache_stats = None

# Import Flow chat service with proper order processing
try:
    from services.flow_chat_service import procesar_mensaje_flow as procesar_mensaje
except ImportError:
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
async def process_chat_message(data: ChatMessage, db: AsyncSession = Depends(get_async_db)):
    """
    Endpoint principal del bot que procesa cualquier mensaje del usuario
    usando IA para analizar y responder
    """
    if not procesar_mensaje:
        return {"error": "Chat service not available"}
    
    try:
        # Get tenant_id from middleware context
        if get_tenant_id is None:
            raise HTTPException(status_code=500, detail="Tenant middleware not available")
        
        tenant_id = get_tenant_id()
        
        # Procesar mensaje con el servicio de chat Flow (sync)
        # Convertir AsyncSession a Session para Flow service
        from database import SessionLocal
        sync_db = SessionLocal()
        try:
            # Pass tenant_id to the processing function
            respuesta = procesar_mensaje(sync_db, data.telefono, data.mensaje, tenant_id)
        finally:
            sync_db.close()
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

@router.get("/bot-products-search")
async def search_products_for_bot(
    query: str = Query(..., description="Search query", min_length=1),
    limit: int = Query(5, description="Number of results to return", ge=1, le=50),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Search products for WhatsApp bot responses using optimized SQL queries
    Returns simplified product information with SQL-level filtering - filtered by tenant
    """
    # Get tenant_id from middleware context (no auth required for bot)
    if get_tenant_id is None:
        raise HTTPException(status_code=500, detail="Tenant middleware not available")
    
    tenant_id = get_tenant_id()
    print(f"DEBUG: Bot search - tenant_id = {tenant_id}")  # DEBUG
    
    # Use optimized async search with SQL ILIKE - filtered by tenant
    products = await crud_async.search_products_async(
        db=db,
        search_query=query,
        limit=limit,
        status="Active",
        client_id=tenant_id
    )
    
    # Transform to bot-friendly format
    return [
        {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": float(product.price),
            "sale_price": float(product.sale_price) if product.sale_price else None,
            "stock": product.stock,
            "status": product.status,
            "display_price": float(product.sale_price if product.sale_price else product.price)
        }
        for product in products
    ]

@router.get("/bot/products/by-category")
async def get_products_by_category_for_bot(
    category: str = Query(..., description="Product category", min_length=1),
    limit: int = Query(10, description="Number of results to return", ge=1, le=100),
    offset: int = Query(0, description="Pagination offset", ge=0),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get products by category for bot responses with SQL-level filtering and pagination - filtered by tenant
    """
    # Get tenant_id from middleware context (no auth required for bot)
    if get_tenant_id is None:
        raise HTTPException(status_code=500, detail="Tenant middleware not available")
    
    tenant_id = get_tenant_id()
    
    # Use optimized async query with SQL WHERE clause - filtered by tenant
    products = await crud_async.get_products_by_category_async(
        db=db,
        category=category,
        limit=limit,
        offset=offset,
        status="Active",
        client_id=tenant_id
    )
    
    # Transform to bot-friendly format
    return [
        {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": float(product.price),
            "sale_price": float(product.sale_price) if product.sale_price else None,
            "stock": product.stock,
            "display_price": float(product.sale_price if product.sale_price else product.price)
        }
        for product in products
    ]

@router.get("/bot/products/catalog")
async def get_catalog_for_bot(
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get catalog summary for bot responses using optimized SQL aggregation - filtered by tenant
    """
    # Get tenant_id from middleware context (no auth required for bot)
    if get_tenant_id is None:
        raise HTTPException(status_code=500, detail="Tenant middleware not available")
    
    tenant_id = get_tenant_id()
    
    # Use optimized catalog summary with SQL GROUP BY - filtered by tenant
    catalog_summary = await crud_async.get_catalog_summary_async(db, client_id=tenant_id)
    
    return {
        "categories": catalog_summary['categories'],
        "total_products": catalog_summary['total_products'],
        "total_categories": catalog_summary['total_categories']
    }

@router.get("/bot/campaigns/active")
async def get_active_campaigns_for_bot(db: AsyncSession = Depends(get_async_db)):
    """
    Get active campaigns for bot responses using SQL filtering
    """
    campaigns = await crud_async.get_campaigns_async(db=db, status="Active", limit=100)
    
    return [
        {
            "id": campaign.id,
            "name": campaign.name,
            "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
            "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
            "status": campaign.status,
            "budget": float(campaign.budget) if campaign.budget else 0.0,
            "clicks": campaign.clicks or 0,
            "conversions": campaign.conversions or 0
        }
        for campaign in campaigns
    ]

@router.get("/bot/discounts/active")
async def get_active_discounts_for_bot(db: AsyncSession = Depends(get_async_db)):
    """
    Get active discounts for bot responses using SQL filtering
    """
    discounts = await crud_async.get_active_discounts_async(db)
    
    return [
        {
            "id": discount.id,
            "name": discount.name,
            "type": discount.type,
            "value": float(discount.value),
            "target": discount.target,
            "category": discount.category,
            "product_id": discount.product_id,
            "is_active": discount.is_active
        }
        for discount in discounts
    ]

@router.get("/bot/product/{product_id}")
async def get_product_details_for_bot(product_id: str, db: AsyncSession = Depends(get_async_db)):
    """
    Get detailed product information for bot with optimized discount lookup
    """
    # Use optimized function that gets product and discounts in one go
    product_with_discounts = await crud_async.get_products_with_discounts_async(
        db=db, 
        product_id=product_id
    )
    
    if not product_with_discounts:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_data = product_with_discounts[0]
    product = product_data['product']
    discounts = product_data['discounts']
    
    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "price": float(product.price),
        "sale_price": float(product.sale_price) if product.sale_price else None,
        "stock": product.stock,
        "status": product.status,
        "image_url": product.image_url,
        "display_price": float(product.sale_price if product.sale_price else product.price),
        "applicable_discounts": discounts
    }

@router.get("/bot/flow-orders")
async def get_flow_orders_for_backoffice(
    limit: int = Query(50, description="Number of results to return", ge=1, le=200),
    offset: int = Query(0, description="Pagination offset", ge=0),
    db: Session = Depends(get_db)
):
    """
    Get Flow orders for backoffice management
    """
    try:
        from tenant_middleware import get_tenant_id
        tenant_id = get_tenant_id()
        
        # Query Flow orders filtered by tenant
        query = db.query(FlowPedido).filter(
            FlowPedido.tenant_id == tenant_id
        ).order_by(FlowPedido.created_at.desc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        pedidos = query.offset(offset).limit(limit).all()
        
        return {
            "pedidos": [
                {
                    "id": pedido.id,
                    "telefono": pedido.telefono,
                    "tenant_id": pedido.tenant_id,
                    "total": pedido.total,
                    "estado": pedido.estado,
                    "token": pedido.token,
                    "created_at": pedido.created_at.isoformat() if pedido.created_at else None,
                    "updated_at": pedido.updated_at.isoformat() if pedido.updated_at else None,
                    "flow_url": f"https://sandbox.flow.cl/app/web/pay.php?token={pedido.token}" if pedido.token else None
                }
                for pedido in pedidos
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Flow orders: {str(e)}")

@router.get("/bot/flow-stats")
async def get_flow_stats_for_backoffice(db: Session = Depends(get_db)):
    """
    Get Flow statistics for backoffice dashboard
    """
    try:
        from tenant_middleware import get_tenant_id
        tenant_id = get_tenant_id()
        
        total_pedidos = db.query(FlowPedido).filter(FlowPedido.tenant_id == tenant_id).count()
        pedidos_pagados = db.query(FlowPedido).filter(
            FlowPedido.tenant_id == tenant_id,
            FlowPedido.estado == "pagado"
        ).count()
        pedidos_pendientes = db.query(FlowPedido).filter(
            FlowPedido.tenant_id == tenant_id,
            FlowPedido.estado == "pendiente_pago"
        ).count()
        
        # Calculate total sold (only paid orders)
        total_vendido = db.query(db.func.sum(FlowPedido.total)).filter(
            FlowPedido.tenant_id == tenant_id,
            FlowPedido.estado == "pagado"
        ).scalar() or 0
        
        return {
            "total_pedidos": total_pedidos,
            "pedidos_pagados": pedidos_pagados,
            "pedidos_pendientes": pedidos_pendientes,
            "total_vendido": int(total_vendido),
            "tasa_conversion": round((pedidos_pagados / total_pedidos * 100) if total_pedidos > 0 else 0, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Flow stats: {str(e)}")


# TEMPORARY DEBUG ENDPOINTS - REMOVE IN PRODUCTION
@router.get("/bot/debug/tenant")
async def debug_tenant_info() -> Dict[str, Any]:
    """
    TEMPORARY: Debug endpoint to test tenant resolution.
    Remove this endpoint in production.
    """
    try:
        if get_tenant_id is None:
            return {
                "error": "Tenant middleware not available",
                "tenant_id": None,
                "resolved": False
            }
        
        tenant_id = get_tenant_id()
        return {
            "tenant_id": tenant_id,
            "resolved": True,
            "message": "Tenant successfully resolved",
            "endpoint": "TEMPORARY DEBUG - REMOVE IN PRODUCTION"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tenant: {str(e)}")


@router.get("/bot/debug/cache")
async def debug_cache_stats() -> Dict[str, Any]:
    """
    TEMPORARY: Debug endpoint to view cache statistics.
    Remove this endpoint in production.
    """
    try:
        if get_cache_stats is None:
            return {
                "error": "Cache stats not available",
                "cache_stats": {}
            }
        
        stats = get_cache_stats()
        return {
            "cache_stats": stats,
            "message": "Cache statistics retrieved",
            "endpoint": "TEMPORARY DEBUG - REMOVE IN PRODUCTION"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")