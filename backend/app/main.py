import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/ping")
def ping():
    return {"status": "ok", "service": "jpos-cms-backend", "version": API_VERSION}
