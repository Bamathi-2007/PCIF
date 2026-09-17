"""
PCIF Backend - Main FastAPI Application Server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api import patient, nutrition, mental_wellness, ccee, doctor
from database.mongodb import db_manager

app = FastAPI(
    title=settings.APP_NAME,
    description="Healthcare AI Research Prototype - Patient Context Intelligence Framework",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(patient.router, prefix="/api")
app.include_router(nutrition.router, prefix="/api")
app.include_router(mental_wellness.router, prefix="/api")
app.include_router(ccee.router, prefix="/api")
app.include_router(doctor.router, prefix="/api")


@app.get("/")
async def root():
    """Root Endpoint."""
    return {
        "project": "PCIF - Patient Context Intelligence Framework",
        "status": "Day 9 Shared Database Active",
        "docs_url": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health Check Endpoint."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": db_manager.get_status()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
