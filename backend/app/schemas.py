"""Pydantic sxemalari (API kirish/chiqish) — Pydantic v2 uchun optimallashtirilgan."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class CustomerIn(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    segment: Optional[str] = "Retail"


class CustomerOut(CustomerIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class ProductIn(BaseModel):
    sku: str
    name: str
    category: Optional[str] = None
    price: float = 0.0
    stock: int = 0
    reorder_level: int = 10


class ProductOut(ProductIn):
    model_config = ConfigDict(from_attributes=True)

    id: int


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = 1


class OrderIn(BaseModel):
    customer_id: int
    note: Optional[str] = None
    items: List[OrderItemIn] = []


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    status: str
    total: float
    note: Optional[str]
    created_at: datetime
