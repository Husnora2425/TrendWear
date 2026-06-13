"""
TrendWear Distribution Ltd — Backend (FAQAT REST API)
Bu servis HTML bermaydi — u faqat JSON API, autentifikatsiya va health-check beradi.
Frontend (nginx) statik sahifalarni beradi va /api, /login, /logout ni shu backendga yo'naltiradi.
"""
import os
from fastapi import FastAPI, Depends, Form, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models, auth
from .routers import api

app = FastAPI(title="TrendWear Backend API", version="2.0")

# Frontend (nginx) bilan ishlash uchun CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API endpointlari (/api/...)
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
        demo = [
            ("TW-1001", "Erkaklar ko'ylagi", "Ko'ylak", 120000, 250),
            ("TW-1002", "Ayollar bluzkasi", "Bluzka", 95000, 180),
            ("TW-1003", "Jinsi shim", "Shim", 180000, 120),
            ("TW-1004", "Sport futbolka", "Futbolka", 65000, 8),
            ("TW-1005", "Qishki kurtka", "Ustki kiyim", 420000, 40),
        ]
        for sku, name, cat, price, stock in demo:
            db.add(models.Product(sku=sku, name=name, category=cat, price=price, stock=stock))
        for n, c, seg in [("Anvar Tekstil MChJ", "Toshkent", "Wholesale"),
                          ("Style Market", "Samarqand", "Retail"),
                          ("Fashion House", "Buxoro", "VIP")]:
            db.add(models.Customer(name=n, city=c, segment=seg, phone="+998900000000"))
        db.commit()
    db.close()


def _redirect(request: Request, path: str, status_code: int = 303):
    """Port saqlab qoluvchi redirect — nginx orqali kelgan so'rovlarda portni saqlaydi."""
    base = str(request.base_url).rstrip("/")
    return RedirectResponse(f"{base}{path}", status_code=status_code)


# ---------- HEALTH CHECK ----------
@app.get("/health")
def health():
    return {"status": "healthy", "service": "trendwear-backend"}


# ---------- AUTENTIFIKATSIYA ----------
@app.post("/login")
def login(request: Request, username: str = Form(...),
          password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return _redirect(request, "/login.html?error=1")
    token = auth.create_token({"sub": user.username})
    resp = _redirect(request, "/")
    resp.set_cookie("access_token", token, httponly=True, max_age=60 * 60 * 8)
    return resp


@app.get("/logout")
def logout(request: Request):
    resp = _redirect(request, "/login.html")
    resp.delete_cookie("access_token")
    return resp


# ---------- Joriy foydalanuvchini tekshirish (frontend uchun) ----------
@app.get("/api/me")
def me(user=Depends(auth.get_current_user)):
    return {"username": user.username, "full_name": user.full_name, "role": user.role}
