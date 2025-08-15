from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    price = Column(Float)
    sale_price = Column(Float, nullable=True)
    stock = Column(Integer)
    image_url = Column(String)
    status = Column(String)  # Active, Archived, OutOfStock
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    join_date = Column(DateTime)
    total_spent = Column(Float, default=0.0)
    avatar_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orders = relationship("Order", back_populates="client")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, index=True)
    customer_name = Column(String)
    client_id = Column(String, ForeignKey("clients.id"), nullable=True)
    date = Column(DateTime)
    total = Column(Float)
    status = Column(String)  # Pending, Shipped, Delivered, Cancelled
    items = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    client = relationship("Client", back_populates="orders")

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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)