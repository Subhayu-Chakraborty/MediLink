"""
app/main.py
───────────
FastAPI application entry point.

Responsibilities:
  - Create the FastAPI application instance.
  - Register the lifespan context manager (startup/shutdown events).
  - Configure CORS middleware.
  - Include all API routers with correct URL prefixes and tags.
  - Expose a /health endpoint for infrastructure health checks.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, ping_database

# ── Route imports ──────────────────────────────────────────────────────────
from app.api.routes import auth, chat, doctors, patients, reports, analysis

logger = logging.getLogger(__name__)

# ── Lifespan ───────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan context manager.
    Everything before `yield` runs at startup; everything after runs at shutdown.
    """
    # ── Startup ──
    logger.info("Starting up Medical Report Analyzer API…")
    await connect_to_mongo()
    logger.info("Application startup complete.")

    yield  # Application is running here

    # ── Shutdown ──
    logger.info("Shutting down Medical Report Analyzer API…")
    await close_mongo_connection()
    logger.info("Application shutdown complete.")


# ── Application factory ────────────────────────────────────────────────────

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    Returns the configured app for use by Uvicorn.
    """
    app = FastAPI(
        title="AI-Based Medical Report Analyzer",
        description=(
            "API for uploading medical PDFs, extracting text, running analysis "
            "via Ollama AI, and predicting disease risks."
        ),
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────
    app.include_router(auth.router,     prefix="/auth",     tags=["Authentication"])
    app.include_router(doctors.router,  prefix="/doctors",  tags=["Doctors"])
    app.include_router(patients.router, prefix="/patients", tags=["Patients"])
    app.include_router(reports.router,  prefix="/reports",  tags=["Reports"])
    app.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
    app.include_router(chat.router,     prefix="/chat",     tags=["Chat"])

    return app


# ── Application instance ───────────────────────────────────────────────────
app: FastAPI = create_application()


# ── Health endpoint ────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"], summary="Health check")
async def health_check() -> dict:
    """
    Lightweight health check endpoint.
    Returns the application status and a MongoDB Atlas connectivity ping.
    Used by Docker health checks and infrastructure monitoring.
    """
    db_ok = await ping_database()
    return {
        "status": "ok" if db_ok else "degraded",
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_ok else "unreachable",
        "database_mode": "in-memory" if settings.USE_IN_MEMORY_DB else "persistent",
        "analysis_mode": settings.AI_MODE,
        "version": "0.1.0",
    }
