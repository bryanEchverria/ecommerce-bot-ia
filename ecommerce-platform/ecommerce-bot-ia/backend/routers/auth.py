from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import get_db
from auth import AuthService, TenantService, get_current_user_and_client
from auth_schemas import (
    UserRegister, UserLogin, TokenRefresh, TokenResponse, 
    AuthResponse, UserResponse, ClientResponse
)
from auth_models import TenantUser, TenantClient
import uuid
import re

router = APIRouter(prefix="/auth", tags=["authentication"])

def validate_slug(slug: str) -> str:
    """Valida y normaliza el slug del client."""
    if not slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client slug is required"
        )
    
    # Normalizar: lowercase, solo letras, números y guiones
    normalized = re.sub(r'[^a-zA-Z0-9-]', '-', slug.lower())
    normalized = re.sub(r'-+', '-', normalized).strip('-')
    
    if len(normalized) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client slug must be at least 3 characters"
        )
    
    return normalized

@router.post("/register", response_model=TokenResponse)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Registro de usuario. Puede crear un nuevo cliente o usar uno existente.
    """
    client = None
    
    if user_data.client_slug:
        # Usar cliente existente
        slug = validate_slug(user_data.client_slug)
        client = TenantService.get_client_by_slug(db, slug)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
    elif user_data.client_name:
        # Crear nuevo cliente
        slug = validate_slug(user_data.client_name)
        
        # Verificar que el slug no exista
        existing_client = TenantService.get_client_by_slug(db, slug)
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client with this name already exists"
            )
        
        client = TenantService.create_client(db, user_data.client_name, slug)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either client_name or client_slug must be provided"
        )
    
    # Verificar que el email no exista en este cliente
    existing_user = TenantService.get_user_by_email(db, user_data.email, client.id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists in this client"
        )
    
    # Crear usuario
    role = "owner" if user_data.client_name else "user"  # Owner si crea el cliente
    user = TenantService.create_user(
        db, user_data.email, user_data.password, client.id, role
    )
    
    # Generar tokens
    token_data = {"sub": user.id, "client_id": client.id, "role": user.role}
    access_token = AuthService.create_access_token(token_data)
    refresh_token = AuthService.create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.from_orm(user),
        client=ClientResponse.from_orm(client)
    )

@router.post("/login", response_model=TokenResponse)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login de usuario con email y password.
    """
    user = None
    client = None
    
    if login_data.client_slug:
        # Login específico para un cliente
        slug = validate_slug(login_data.client_slug)
        client = TenantService.get_client_by_slug(db, slug)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        user = TenantService.get_user_by_email(db, login_data.email, client.id)
    else:
        # Buscar usuario en cualquier cliente (tomar el primero si hay múltiples)
        from sqlalchemy import and_
        user = db.query(TenantUser).filter(TenantUser.email == login_data.email).first()
        if user:
            client = TenantService.get_client_by_id(db, user.client_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or inactive user"
        )
    
    if not AuthService.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generar tokens
    token_data = {"sub": user.id, "client_id": client.id, "role": user.role}
    access_token = AuthService.create_access_token(token_data)
    refresh_token = AuthService.create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.from_orm(user),
        client=ClientResponse.from_orm(client)
    )

@router.post("/refresh", response_model=dict)
def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Renovar access token usando refresh token.
    """
    try:
        payload = AuthService.verify_token(token_data.refresh_token)
        
        # Verificar que sea un refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        client_id = payload.get("client_id")
        
        # Verificar que el usuario siga activo
        user = TenantService.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generar nuevo access token
        token_data = {"sub": user.id, "client_id": client_id, "role": user.role}
        access_token = AuthService.create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.get("/me", response_model=AuthResponse)
def get_me(
    current_user_and_client: tuple[TenantUser, TenantClient] = Depends(get_current_user_and_client)
):
    """
    Obtener información del usuario y cliente autenticado.
    """
    user, client = current_user_and_client
    
    return AuthResponse(
        user=UserResponse.from_orm(user),
        client=ClientResponse.from_orm(client)
    )

@router.post("/bot-proxy/{tenant_id}")
async def bot_proxy_auth(tenant_id: str, request_data: dict):
    """Bot proxy endpoint in auth router (bypasses tenant middleware)"""
    try:
        import requests
        
        test_message = request_data.get("test_message", "")
        
        # Forward request to WhatsApp bot service
        bot_response = requests.post(
            "http://ecommerce-whatsapp-bot:9001/webhook",
            headers={'Content-Type': 'application/json'},
            json={
                'telefono': '+56950915617',
                'mensaje': test_message
            },
            timeout=15.0
        )
        
        if bot_response.status_code == 200:
            result = bot_response.json()
            return {
                "bot_response": result.get('respuesta', ''),
                "status": "success"
            }
        else:
            return {
                "error": f"Bot service error: {bot_response.status_code}",
                "bot_response": "Error connecting to bot service"
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "bot_response": "Error interno del sistema - no se pudo conectar al bot"
        }