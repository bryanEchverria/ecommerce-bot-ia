"""
Router para panel de administración de clientes multi-tenant
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import uuid
from datetime import datetime

from database import get_db
from auth_models import TenantClient, TenantUser
from admin_schemas import (
    TenantClientCreate, TenantUserCreate, TenantClientWithUsers,
    TenantClientDetail, AdminClientCreate, AdminClientUpdate,
    AdminUserCreate, AdminUserUpdate, TenantUserResponse
)
from auth import AuthService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

# TODO: Add proper admin authentication middleware
# For now, this is a basic implementation without admin auth

@router.get("/clients", response_model=List[TenantClientWithUsers])
async def get_all_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los clientes (tenants) con información básica
    """
    try:
        clients = db.query(TenantClient).offset(skip).limit(limit).all()
        
        result = []
        for client in clients:
            user_count = db.query(TenantUser).filter(TenantUser.client_id == client.id).count()
            result.append(TenantClientWithUsers(
                id=client.id,
                name=client.name,
                slug=client.slug,
                created_at=client.created_at,
                user_count=user_count,
                status="active"
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting clients: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving clients")

@router.get("/clients/{client_id}", response_model=TenantClientDetail)
async def get_client_detail(client_id: str, db: Session = Depends(get_db)):
    """
    Obtener detalles completos de un cliente específico
    """
    try:
        client = db.query(TenantClient).filter(TenantClient.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        users = db.query(TenantUser).filter(TenantUser.client_id == client_id).all()
        
        user_responses = [
            TenantUserResponse(
                id=user.id,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at
            )
            for user in users
        ]
        
        return TenantClientDetail(
            id=client.id,
            name=client.name,
            slug=client.slug,
            created_at=client.created_at,
            users=user_responses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client detail: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving client details")

@router.post("/clients", response_model=TenantClientDetail)
async def create_client(
    client_data: AdminClientCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo cliente (tenant) con usuario administrador
    """
    try:
        # Check if slug already exists
        existing_client = db.query(TenantClient).filter(TenantClient.slug == client_data.slug).first()
        if existing_client:
            raise HTTPException(status_code=400, detail="Client slug already exists")
        
        # Check if admin email already exists for any tenant
        existing_user = db.query(TenantUser).filter(TenantUser.email == client_data.admin_email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Admin email already exists")
        
        # Create client
        new_client = TenantClient(
            id=str(uuid.uuid4()),
            name=client_data.name,
            slug=client_data.slug,
            created_at=datetime.utcnow()
        )
        db.add(new_client)
        db.commit()
        db.refresh(new_client)
        
        # Create admin user
        hashed_password = AuthService.get_password_hash(client_data.admin_password)
        admin_user = TenantUser(
            id=str(uuid.uuid4()),
            email=client_data.admin_email,
            password_hash=hashed_password,
            client_id=new_client.id,
            role="admin",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        logger.info(f"Created client {client_data.slug} with admin user {client_data.admin_email}")
        
        # Return client detail
        return TenantClientDetail(
            id=new_client.id,
            name=new_client.name,
            slug=new_client.slug,
            created_at=new_client.created_at,
            users=[TenantUserResponse(
                id=admin_user.id,
                email=admin_user.email,
                role=admin_user.role,
                is_active=admin_user.is_active,
                created_at=admin_user.created_at
            )]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating client")

@router.put("/clients/{client_id}", response_model=TenantClientDetail)
async def update_client(
    client_id: str,
    update_data: AdminClientUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar información de un cliente
    """
    try:
        client = db.query(TenantClient).filter(TenantClient.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Update fields if provided
        if update_data.name is not None:
            client.name = update_data.name
        
        if update_data.slug is not None:
            # Check if new slug already exists
            existing_client = db.query(TenantClient).filter(
                TenantClient.slug == update_data.slug,
                TenantClient.id != client_id
            ).first()
            if existing_client:
                raise HTTPException(status_code=400, detail="Slug already exists")
            client.slug = update_data.slug
        
        db.commit()
        db.refresh(client)
        
        # Get users
        users = db.query(TenantUser).filter(TenantUser.client_id == client_id).all()
        user_responses = [
            TenantUserResponse(
                id=user.id,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at
            )
            for user in users
        ]
        
        logger.info(f"Updated client {client_id}")
        
        return TenantClientDetail(
            id=client.id,
            name=client.name,
            slug=client.slug,
            created_at=client.created_at,
            users=user_responses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating client")

@router.delete("/clients/{client_id}")
async def delete_client(client_id: str, db: Session = Depends(get_db)):
    """
    Eliminar un cliente y todos sus usuarios (PELIGROSO)
    """
    try:
        client = db.query(TenantClient).filter(TenantClient.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Delete all users for this client first
        db.query(TenantUser).filter(TenantUser.client_id == client_id).delete()
        
        # Delete client
        db.delete(client)
        db.commit()
        
        logger.warning(f"DELETED client {client_id} ({client.slug}) and all its users")
        
        return {"message": f"Client {client.slug} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting client")

@router.post("/clients/{client_id}/users", response_model=TenantUserResponse)
async def create_user_for_client(
    client_id: str,
    user_data: TenantUserCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo usuario para un cliente específico
    """
    try:
        # Check if client exists
        client = db.query(TenantClient).filter(TenantClient.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Check if email already exists for this tenant
        existing_user = db.query(TenantUser).filter(
            TenantUser.email == user_data.email,
            TenantUser.client_id == client_id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User email already exists for this client")
        
        # Create user
        hashed_password = AuthService.get_password_hash(user_data.password)
        new_user = TenantUser(
            id=str(uuid.uuid4()),
            email=user_data.email,
            password_hash=hashed_password,
            client_id=client_id,
            role=user_data.role,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Created user {user_data.email} for client {client_id}")
        
        return TenantUserResponse(
            id=new_user.id,
            email=new_user.email,
            role=new_user.role,
            is_active=new_user.is_active,
            created_at=new_user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating user")

@router.get("/users", response_model=List[TenantUserResponse])
async def get_all_users(
    client_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los usuarios, opcionalmente filtrados por cliente
    """
    try:
        query = db.query(TenantUser)
        
        if client_id:
            query = query.filter(TenantUser.client_id == client_id)
        
        users = query.offset(skip).limit(limit).all()
        
        return [
            TenantUserResponse(
                id=user.id,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at
            )
            for user in users
        ]
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving users")

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """
    Eliminar un usuario específico
    """
    try:
        user = db.query(TenantUser).filter(TenantUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Don't allow deleting the last admin user of a client
        if user.role == "admin":
            admin_count = db.query(TenantUser).filter(
                TenantUser.client_id == user.client_id,
                TenantUser.role == "admin"
            ).count()
            
            if admin_count <= 1:
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot delete the last admin user of a client"
                )
        
        db.delete(user)
        db.commit()
        
        logger.info(f"Deleted user {user_id} ({user.email})")
        
        return {"message": f"User {user.email} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting user")