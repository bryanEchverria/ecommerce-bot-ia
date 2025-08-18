from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from auth import get_current_user_and_client, get_current_client, tenant_filter_query
from auth_schemas import TenantOrderCreate, TenantOrderUpdate, TenantOrderResponse
from auth_models import TenantUser, TenantClient, TenantOrder

router = APIRouter(prefix="/tenant-orders", tags=["tenant-orders"])

@router.post("/", response_model=TenantOrderResponse)
def create_order(
    order_data: TenantOrderCreate,
    db: Session = Depends(get_db),
    current_client: TenantClient = Depends(get_current_client)
):
    """
    Crear nueva orden para el cliente autenticado.
    Demuestra UNIQUE(client_id, code).
    """
    # Verificar que el código no exista para este cliente
    existing = db.query(TenantOrder).filter(
        TenantOrder.client_id == current_client.id,
        TenantOrder.code == order_data.code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order with code '{order_data.code}' already exists for this client"
        )
    
    # Crear orden
    db_order = TenantOrder(
        client_id=current_client.id,
        code=order_data.code,
        customer_name=order_data.customer_name,
        total=order_data.total,
        status=order_data.status
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return TenantOrderResponse.from_orm(db_order)

@router.get("/", response_model=List[TenantOrderResponse])
def get_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_client: TenantClient = Depends(get_current_client)
):
    """
    Obtener órdenes del cliente autenticado.
    Automáticamente filtradas por client_id.
    """
    query = db.query(TenantOrder)
    query = tenant_filter_query(query, TenantOrder, current_client.id)
    
    orders = query.order_by(TenantOrder.created_at.desc()).offset(skip).limit(limit).all()
    return [TenantOrderResponse.from_orm(order) for order in orders]

@router.get("/{order_id}", response_model=TenantOrderResponse)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_client: TenantClient = Depends(get_current_client)
):
    """
    Obtener orden específica del cliente autenticado.
    """
    query = db.query(TenantOrder).filter(TenantOrder.id == order_id)
    query = tenant_filter_query(query, TenantOrder, current_client.id)
    
    order = query.first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return TenantOrderResponse.from_orm(order)

@router.put("/{order_id}", response_model=TenantOrderResponse)
def update_order(
    order_id: str,
    order_data: TenantOrderUpdate,
    db: Session = Depends(get_db),
    current_client: TenantClient = Depends(get_current_client)
):
    """
    Actualizar orden del cliente autenticado.
    """
    query = db.query(TenantOrder).filter(TenantOrder.id == order_id)
    query = tenant_filter_query(query, TenantOrder, current_client.id)
    
    order = query.first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Actualizar campos no nulos
    update_data = order_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    return TenantOrderResponse.from_orm(order)

@router.delete("/{order_id}")
def delete_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_client: TenantClient = Depends(get_current_client)
):
    """
    Eliminar orden del cliente autenticado.
    """
    query = db.query(TenantOrder).filter(TenantOrder.id == order_id)
    query = tenant_filter_query(query, TenantOrder, current_client.id)
    
    order = query.first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    db.delete(order)
    db.commit()
    
    return {"message": "Order deleted successfully"}

@router.get("/by-code/{code}", response_model=TenantOrderResponse)
def get_order_by_code(
    code: str,
    db: Session = Depends(get_db),
    current_client: TenantClient = Depends(get_current_client)
):
    """
    Obtener orden por código del cliente autenticado.
    Demuestra búsqueda por código único por tenant.
    """
    order = db.query(TenantOrder).filter(
        TenantOrder.client_id == current_client.id,
        TenantOrder.code == code
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return TenantOrderResponse.from_orm(order)