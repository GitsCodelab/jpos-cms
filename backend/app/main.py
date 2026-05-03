import os
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text

from app.db import init_db
from app.security import access_token_ttl_seconds, authenticate_user, create_access_token, require_jwt_token
from app.routers import auth, transactions, reconciliation, fraud, settlement, net, dashboard, config
from app.routers import menu as menu_router
from app.seed.menu_seed import seed_menu_profiles

API_TITLE = os.getenv("API_TITLE", "jPOS CMS API")
API_VERSION = os.getenv("API_VERSION", "1.0.0")

app = FastAPI(title=API_TITLE, version=API_VERSION, docs_url="/docs", redoc_url="/redoc")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Create database tables and seed initial data on application startup."""
    init_db()
    from app.db import SessionLocal
    db = SessionLocal()
    try:
        # Inline migration: add is_active to menu_items if it doesn't exist yet
        db.execute(text(
            "ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE"
        ))
        db.commit()
        seed_menu_profiles(db)
    finally:
        db.close()

# CORS Configuration - restrict to specific origins
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(reconciliation.router)
app.include_router(fraud.router)
app.include_router(settlement.router)
app.include_router(net.router)
app.include_router(dashboard.router)
app.include_router(config.router)
app.include_router(menu_router.router)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "jpos-cms-backend", "version": API_VERSION}


@app.get("/ping")
def ping(_: Dict[str, Any] = Depends(require_jwt_token)):
    """Protected ping endpoint - requires authentication."""
    return {"status": "ok", "service": "jpos-cms-backend", "version": API_VERSION}
