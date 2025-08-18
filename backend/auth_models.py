from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid

class TenantClient(Base):
    """Tabla de clientes para modelo multi-tenant"""
    __tablename__ = "tenant_clients"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("TenantUser", back_populates="client")
    orders = relationship("TenantOrder", back_populates="client")

class TenantUser(Base):
    """Tabla de usuarios con tenant isolation"""
    __tablename__ = "tenant_users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    client_id = Column(String, ForeignKey("tenant_clients.id"), nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")  # owner, admin, user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    client = relationship("TenantClient", back_populates="users")
    
    # Unique constraint per tenant
    __table_args__ = (
        Index('ix_tenant_users_client_email', 'client_id', 'email', unique=True),
    )

class TenantOrder(Base):
    """Tabla de órdenes tenant-aware"""
    __tablename__ = "tenant_orders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    client_id = Column(String, ForeignKey("tenant_clients.id"), nullable=False, index=True)
    code = Column(String, nullable=False)  # Código de orden único por tenant
    customer_name = Column(String, nullable=False)
    total = Column(String, nullable=False)  # Guardamos como string para manejar diferentes monedas
    status = Column(String, default="pending")  # pending, confirmed, shipped, delivered, cancelled
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    client = relationship("TenantClient", back_populates="orders")
    
    # Unique constraint per tenant
    __table_args__ = (
        Index('ix_tenant_orders_client_code', 'client_id', 'code', unique=True),
        Index('ix_tenant_orders_client_created', 'client_id', 'created_at'),
    )