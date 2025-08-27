from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    price: float
    sale_price: Optional[float] = None
    stock: int
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None
    image_url: str
    status: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    sale_price: Optional[float] = None
    stock: Optional[int] = None
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None
    image_url: Optional[str] = None
    status: Optional[str] = None

class Product(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ClientBase(BaseModel):
    name: str
    email: str
    phone: str
    join_date: datetime
    total_spent: float = 0.0
    avatar_url: str

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    join_date: Optional[datetime] = None
    total_spent: Optional[float] = None
    avatar_url: Optional[str] = None

class Client(ClientBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_name: str
    date: datetime
    total: float
    status: str
    items: int

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    date: Optional[datetime] = None
    total: Optional[float] = None
    status: Optional[str] = None
    items: Optional[int] = None

class Order(OrderBase):
    id: str
    order_number: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CampaignBase(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    status: str
    budget: float
    clicks: int = 0
    conversions: int = 0
    image_url: str
    product_ids: List[str] = []

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    budget: Optional[float] = None
    clicks: Optional[int] = None
    conversions: Optional[int] = None
    image_url: Optional[str] = None
    product_ids: Optional[List[str]] = None

class Campaign(CampaignBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DiscountBase(BaseModel):
    name: str
    type: str
    value: float
    target: str
    category: Optional[str] = None
    product_id: Optional[str] = None
    is_active: bool = True

class DiscountCreate(DiscountBase):
    pass

class DiscountUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[float] = None
    target: Optional[str] = None
    category: Optional[str] = None
    product_id: Optional[str] = None
    is_active: Optional[bool] = None

class Discount(DiscountBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SalesData(BaseModel):
    name: str
    sales: float

class DashboardStats(BaseModel):
    total_products: int
    active_products: int
    total_orders: int
    pending_orders: int
    total_clients: int
    total_revenue: float
    sales_data: List[SalesData]