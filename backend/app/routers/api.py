"""CRM / WMS / ERP API endpointlari."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/api", tags=["api"])


# ---------- CRM: Mijozlar ----------
@router.get("/customers", response_model=list[schemas.CustomerOut])
def list_customers(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Customer).order_by(models.Customer.id.desc()).all()


@router.post("/customers", response_model=schemas.CustomerOut)
def create_customer(c: schemas.CustomerIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = models.Customer(**c.dict())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.delete("/customers/{cid}")
def delete_customer(cid: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = db.query(models.Customer).get(cid)
    if not obj:
        raise HTTPException(404, "Mijoz topilmadi")
    db.delete(obj); db.commit()
    return {"ok": True}


# ---------- WMS: Mahsulotlar ----------
@router.get("/products", response_model=list[schemas.ProductOut])
def list_products(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Product).order_by(models.Product.id.desc()).all()


@router.post("/products", response_model=schemas.ProductOut)
def create_product(p: schemas.ProductIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if db.query(models.Product).filter_by(sku=p.sku).first():
        raise HTTPException(400, "Bu SKU mavjud")
    obj = models.Product(**p.dict())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.delete("/products/{pid}")
def delete_product(pid: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = db.query(models.Product).get(pid)
    if not obj:
        raise HTTPException(404, "Mahsulot topilmadi")
    db.delete(obj); db.commit()
    return {"ok": True}


# ---------- ERP: Buyurtmalar ----------
@router.get("/orders", response_model=list[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Order).order_by(models.Order.id.desc()).all()


@router.post("/orders", response_model=schemas.OrderOut)
def create_order(o: schemas.OrderIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not db.query(models.Customer).get(o.customer_id):
        raise HTTPException(400, "Mijoz topilmadi")
    order = models.Order(customer_id=o.customer_id, note=o.note)
    db.add(order); db.flush()
    total = 0.0
    for it in o.items:
        prod = db.query(models.Product).get(it.product_id)
        if not prod:
            raise HTTPException(400, f"Mahsulot {it.product_id} topilmadi")
        if prod.stock < it.quantity:
            raise HTTPException(400, f"'{prod.name}' uchun ombor yetarli emas")
        prod.stock -= it.quantity
        total += prod.price * it.quantity
        db.add(models.OrderItem(order_id=order.id, product_id=prod.id,
                                quantity=it.quantity, unit_price=prod.price))
    order.total = total
    db.commit(); db.refresh(order)
    return order


@router.put("/orders/{oid}/status")
def update_status(oid: int, status: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = db.query(models.Order).get(oid)
    if not order:
        raise HTTPException(404, "Buyurtma topilmadi")
    order.status = status
    db.commit()
    return {"ok": True, "status": status}


# ---------- Dashboard statistikasi ----------
@router.get("/stats")
def stats(db: Session = Depends(get_db), user=Depends(get_current_user)):
    revenue = db.query(func.coalesce(func.sum(models.Order.total), 0)).scalar()
    low_stock = db.query(models.Product).filter(
        models.Product.stock <= models.Product.reorder_level).count()
    return {
        "customers": db.query(models.Customer).count(),
        "products": db.query(models.Product).count(),
        "orders": db.query(models.Order).count(),
        "revenue": round(revenue, 2),
        "low_stock": low_stock,
        "pending": db.query(models.Order).filter_by(status="Pending").count(),
    }
