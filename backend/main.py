"""
Voxy - AI-Powered Scam Call Detector
FastAPI application entrypoint.

Run locally:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Voxy - AI-Powered Scam Call Shield",
    description=(
        "Real-time, multi-layer detection and prevention of AI voice-"
        "cloning impersonation scam calls. Team VoxVeritas - SIH 2026 "
        "(PS ID 26104)."
    ),
    version="0.1.0",
)

# In production, restrict allow_origins to the mobile app / bank & telecom
# integration domains rather than "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root() -> dict:
    return {
        "service": "Voxy AI-Powered Scam Call Shield",
        "team": "VoxVeritas",
        "status": "running",
    }
