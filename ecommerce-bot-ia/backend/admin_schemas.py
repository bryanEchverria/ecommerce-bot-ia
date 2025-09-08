"""
Schemas para el panel de administración de clientes
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class TenantClientCreate(BaseModel):
    name: str
    slug: str

class TenantUserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"

class TenantClientWithUsers(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime
    user_count: int
    status: str = "active"

class TenantUserResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

class TenantClientDetail(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime
    users: List[TenantUserResponse]

class AdminClientCreate(BaseModel):
    name: str
    slug: str
    admin_email: EmailStr
    admin_password: str

class AdminClientUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    status: Optional[str] = None

class AdminUserCreate(BaseModel):
    client_id: str
    email: EmailStr
    password: str
    role: str = "user"

class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None