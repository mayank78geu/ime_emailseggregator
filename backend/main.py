"""
Shipping Email Segregation & Data Extraction System
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from routers.extract import router as extract_router
from routers.upload import router as upload_router
from routers.search import router as search_router

# ── FastAPI app ──
app = FastAPI(
    title="Shipping Email Segregation API",
    description=(
        "Extracts structured data (TONNAGE / CARGO_VC / CARGO_TC) "
        "from raw shipping emails. Always returns a JSON array."
    ),
    version="1.0.0",
)

# ── CORS (allow React frontend on any port during dev) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──
app.include_router(extract_router)
app.include_router(upload_router)
app.include_router(search_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "message": "Shipping Email Segregation API is live",
        "docs": "/docs",
        "primary_endpoint": "POST /extract-email",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
