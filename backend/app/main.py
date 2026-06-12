"""
TrendWear Distribution Ltd — Bulutli ERP/CRM/WMS platformasi
Frontend (HTML/JS) va Backend (REST API) BITTA portda (8000) ishlaydi.
"""
import os
from fastapi import FastAPI, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models, auth
from .routers import api

BASE_DIR = os.path.dirname(__file__)

app = FastAPI(title="TrendWear Cloud Platform", version="1.0")

# Static fayllar
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Backend API'ni shu ilovaga ulaymiz (bitta port)
app.include_router(api.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    _seed()


def _seed():
    """Boshlang'ich admin va demo ma'lumotlar."""
    db = next(get_db())
    if not db.query(models.User).first():
        db.add(models.User(
            username="admin",
            full_name="Tizim administratori",
            hashed_password=auth.hash_password("admin123"),
            role="admin",
        ))
        # Demo mahsulotlar
        demo = [
            ("TW-1001", "Erkaklar ko'ylagi", "Ko'ylak", 120000, 250),
            ("TW-1002", "Ayollar bluzkasi", "Bluzka", 95000, 180),
            ("TW-1003", "Jinsi shim", "Shim", 180000, 120),
            ("TW-1004", "Sport futbolka", "Futbolka", 65000, 8),
            ("TW-1005", "Qishki kurtka", "Ustki kiyim", 420000, 40),
        ]
        for sku, name, cat, price, stock in demo:
            db.add(models.Product(sku=sku, name=name, category=cat, price=price, stock=stock))
        # Demo mijozlar
        for n, c, seg in [("Anvar Tekstil MChJ", "Toshkent", "Wholesale"),
                          ("Style Market", "Samarqand", "Retail"),
                          ("Fashion House", "Buxoro", "VIP")]:
            db.add(models.Customer(name=n, city=c, segment=seg, phone="+998900000000"))
        db.commit()
    db.close()


# ---------- HEALTH CHECK (Load Balancer uchun) ----------
@app.get("/health")
def health():
    return {"status": "healthy", "service": "trendwear"}


# ---------- AUTENTIFIKATSIYA ----------
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.post("/login")
def login(response: Response, username: str = Form(...),
          password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return RedirectResponse("/login?error=1", status_code=303)
    token = auth.create_token({"sub": user.username})
    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie("access_token", token, httponly=True, max_age=60*60*8)
    return resp


@app.get("/logout")
def logout():
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie("access_token")
    return resp


# ---------- FRONTEND (dashboard) ----------
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(request, "index.html")
