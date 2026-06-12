"""Pydantic sxemalari (API kirish/chiqish)."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CustomerIn(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    segment: Optional[str] = "Retail"


class CustomerOut(CustomerIn):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True


class ProductIn(BaseModel):
    sku: str
    name: str
    category: Optional[str] = None
    price: float = 0.0
    stock: int = 0
    reorder_level: int = 10


class ProductOut(ProductIn):
    id: int
    class Config:
        from_attributes = True


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = 1


class OrderIn(BaseModel):
    customer_id: int
    note: Optional[str] = None
    items: List[OrderItemIn] = []


class OrderOut(BaseModel):
    id: int
    customer_id: int
    status: str
    total: float
    note: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True
