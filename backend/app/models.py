"""
TrendWear Distribution Ltd — ERP/CRM/WMS
Ma'lumotlar bazasi modellari (SQLAlchemy)
"""
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(120), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="staff")  # admin / staff
    created_at = Column(DateTime, default=datetime.utcnow)


class Customer(Base):
    """CRM — Mijozlar"""
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120))
    phone = Column(String(40))
    city = Column(String(80))
    segment = Column(String(40), default="Retail")  # Retail / Wholesale / VIP
    created_at = Column(DateTime, default=datetime.utcnow)
    orders = relationship("Order", back_populates="customer")


class Product(Base):
    """WMS — Mahsulotlar / ombor"""
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(40), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    category = Column(String(60))
    price = Column(Float, default=0.0)
    stock = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    """ERP — Buyurtmalar"""
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(String(30), default="Pending")  # Pending/Shipped/Delivered/Cancelled
    total = Column(Float, default=0.0)
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
