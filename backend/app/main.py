import os
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.security import access_token_ttl_seconds, authenticate_user, create_access_token, require_jwt_token

API_TITLE = os.getenv("API_TITLE", "jPOS CMS API")
API_VERSION = os.getenv("API_VERSION", "1.0.0")

app = FastAPI(title=API_TITLE, version=API_VERSION, docs_url="/docs", redoc_url="/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/auth/login")
def login(payload: LoginRequest):
    if not authenticate_user(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(subject=payload.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": access_token_ttl_seconds(),
        "username": payload.username,
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "jpos-cms-backend", "version": API_VERSION}


@app.get("/ping")
def ping(_: Dict[str, Any] = Depends(require_jwt_token)):
    return {"status": "ok", "service": "jpos-cms-backend", "version": API_VERSION}
