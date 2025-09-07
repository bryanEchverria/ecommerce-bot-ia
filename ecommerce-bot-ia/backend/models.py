from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)  # Descripción del producto
    category = Column(String, index=True)
    price = Column(Float)
    sale_price = Column(Float, nullable=True)
    stock = Column(Integer)
    width_cm = Column(Float, nullable=True)  # Ancho en centímetros
    height_cm = Column(Float, nullable=True)  # Alto en centímetros
    image_url = Column(String)
    status = Column(String)  # Active, Archived, OutOfStock
    client_id = Column(String, nullable=True, index=True)  # Multi-tenant support
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)  # Changed from unique=True for multi-tenant
    phone = Column(String)
    join_date = Column(DateTime)
    total_spent = Column(Float, default=0.0)
    avatar_url = Column(String)
    client_id = Column(String, nullable=True, index=True)  # Multi-tenant support
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # orders = relationship("Order", back_populates="client")  # Removed multi-tenant

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)  # Número de orden secuencial
    customer_name = Column(String)
    customer_email = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    date = Column(DateTime)
    total = Column(Float)
    status = Column(String)  # Pending, Received, Shipping, Delivered, Cancelled
    items = Column(Integer)
    client_id = Column(String, nullable=True, index=True)  # Multi-tenant support
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String)  # Active, Paused, Completed
    budget = Column(Float)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    image_url = Column(String)
    product_ids = Column(Text)  # JSON string of product IDs
    client_id = Column(String, nullable=True, index=True)  # Multi-tenant support
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Discount(Base):
    __tablename__ = "discounts"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)  # Percentage, FixedAmount
    value = Column(Float)
    target = Column(String)  # All, Category, Product
    category = Column(String, nullable=True)
    product_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    client_id = Column(String, nullable=True, index=True)  # Multi-tenant support
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============ MODELOS PARA INTEGRACIÓN CON FLOW ============

class FlowProduct(Base):
    __tablename__ = "flow_products"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    precio = Column(Float)
    descripcion = Column(Text, nullable=True)
    tenant_id = Column(String, nullable=False, index=True)  # Multi-tenant support
    created_at = Column(DateTime, default=datetime.utcnow)

class FlowPedido(Base):
    __tablename__ = "flow_pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    telefono = Column(String, index=True)
    tenant_id = Column(String, nullable=False, index=True)  # Multi-tenant support
    total = Column(Float)
    estado = Column(String, default="pendiente_pago")  # pendiente_pago, pagado, cancelado
    token = Column(String, nullable=True)  # Token de Flow para verificar pago
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FlowProductoPedido(Base):
    __tablename__ = "flow_producto_pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("flow_pedidos.id"))
    producto_id = Column(Integer, ForeignKey("flow_products.id"))
    cantidad = Column(Integer)
    precio_unitario = Column(Float)

class FlowSesion(Base):
    __tablename__ = "flow_sesiones"
    
    id = Column(Integer, primary_key=True, index=True)
    telefono = Column(String, index=False)  # No index on telefono alone - only composite
    tenant_id = Column(String, nullable=False, index=True)  # Multi-tenant support
    estado = Column(String, default="INITIAL")
    datos = Column(Text)  # JSON con datos de la sesión
    last_message_at = Column(DateTime, default=datetime.utcnow)  # Último mensaje del usuario
    timeout_warning_sent = Column(Boolean, default=False)  # Si ya se envió advertencia de timeout
    conversation_active = Column(Boolean, default=True)  # Si la conversación está activa
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define composite unique index at table level
    __table_args__ = (
        # Unique constraint on tenant_id + telefono combination
        Index('ux_flow_sesiones_tenant_phone', 'tenant_id', 'telefono', unique=True),
    )

class WhatsAppSettings(Base):
    """Configuración global de canal WhatsApp (single tenant)"""
    __tablename__ = "whatsapp_settings"
    
    id = Column(Integer, primary_key=True, index=True)  # Solo habrá un registro (id=1)
    provider = Column(String, nullable=False)  # "twilio" o "meta"
    
    # Configuración Twilio
    twilio_account_sid = Column(String, nullable=True)
    twilio_auth_token = Column(String, nullable=True)  # Encriptado
    twilio_from = Column(String, nullable=True)  # Número WhatsApp de Twilio
    
    # Configuración Meta
    meta_token = Column(String, nullable=True)  # Encriptado
    meta_phone_number_id = Column(String, nullable=True)
    meta_graph_api_version = Column(String, default="v21.0")
    
    # Estado
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)