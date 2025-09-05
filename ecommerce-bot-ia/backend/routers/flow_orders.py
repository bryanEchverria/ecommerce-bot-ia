"""
Router para consultar pedidos Flow desde el backoffice
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import FlowPedido
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/flow-orders/")
async def get_flow_orders(
    limit: int = 50,
    offset: int = 0,
    client_id: Optional[str] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtener lista de pedidos Flow para el backoffice
    """
    try:
        query = db.query(FlowPedido)
        
        # Filtrar por cliente si se especifica (skip para single tenant)
        # if client_id:
        #     query = query.filter(FlowPedido.client_id == client_id)
            
        # Filtrar por estado si se especifica
        if estado:
            query = query.filter(FlowPedido.estado == estado)
            
        # Ordenar por fecha de creación descendente
        query = query.order_by(FlowPedido.created_at.desc())
        
        # Aplicar paginación
        pedidos = query.offset(offset).limit(limit).all()
        
        # Contar total de pedidos
        total = query.count()
        
        return {
            "pedidos": [
                {
                    "id": pedido.id,
                    "code": f"WA{pedido.id}",  # Código para compatibilidad con frontend
                    "customer_name": f"Cliente WhatsApp ({pedido.telefono})",
                    "telefono": pedido.telefono,
                    "client_id": "sintestesia",  # Single tenant
                    "total": pedido.total,
                    "status": "Completed" if pedido.estado == "pagado" else "Pending" if pedido.estado == "pendiente_pago" else "Cancelled",
                    "estado": pedido.estado,
                    "token": pedido.token,
                    "created_at": pedido.created_at,
                    "updated_at": pedido.updated_at,
                    "items": 1  # Valor por defecto para compatibilidad
                }
                for pedido in pedidos
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting Flow orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/flow-orders/stats")
async def get_flow_stats(db: Session = Depends(get_db)):
    """
    Estadísticas básicas de pedidos Flow
    """
    try:
        total_pedidos = db.query(FlowPedido).count()
        pedidos_pagados = db.query(FlowPedido).filter(FlowPedido.estado == "pagado").count()
        pedidos_pendientes = db.query(FlowPedido).filter(FlowPedido.estado == "pendiente_pago").count()
        
        # Calcular total vendido (solo pedidos pagados)
        from sqlalchemy import func
        total_vendido = db.query(func.sum(FlowPedido.total)).filter(FlowPedido.estado == "pagado").scalar() or 0
        
        return {
            "total_pedidos": total_pedidos,
            "pedidos_pagados": pedidos_pagados,
            "pedidos_pendientes": pedidos_pendientes,
            "total_vendido": total_vendido,
            "tasa_conversion": round((pedidos_pagados / total_pedidos * 100) if total_pedidos > 0 else 0, 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting Flow stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/flow-orders/{order_id}")
async def get_flow_order(order_id: str, db: Session = Depends(get_db)):
    """
    Obtener detalles de un pedido específico
    """
    try:
        pedido = db.query(FlowPedido).filter(FlowPedido.id == order_id).first()
        
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
            
        return {
            "id": pedido.id,
            "code": f"WA{pedido.id}",
            "customer_name": f"Cliente WhatsApp ({pedido.telefono})",
            "telefono": pedido.telefono,
            "client_id": "sintestesia",  # Single tenant
            "total": pedido.total,
            "status": "Completed" if pedido.estado == "pagado" else "Pending" if pedido.estado == "pendiente_pago" else "Cancelled",
            "estado": pedido.estado,
            "token": pedido.token,
            "created_at": pedido.created_at,
            "updated_at": pedido.updated_at,
            "items": 1,
            "flow_url": f"https://sandbox.flow.cl/app/web/pay.php?token={pedido.token}" if pedido.token else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Flow order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))