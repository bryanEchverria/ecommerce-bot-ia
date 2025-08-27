from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Request schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    client_name: Optional[str] = None  # Para crear nuevo client
    client_slug: Optional[str] = None  # Para usar client existente

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    client_slug: Optional[str] = None  # Opcional si solo hay un client

class TokenRefresh(BaseModel):
    refresh_token: str

# Response schemas
class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ClientResponse(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
    client: ClientResponse

class AuthResponse(BaseModel):
    user: UserResponse
    client: ClientResponse

# Tenant Order schemas
class TenantOrderCreate(BaseModel):
    code: str
    customer_name: str
    total: str
    status: Optional[str] = "pending"

class TenantOrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    total: Optional[str] = None
    status: Optional[str] = None

class TenantOrderResponse(BaseModel):
    id: str
    client_id: str
    code: str
    customer_name: str
    total: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True