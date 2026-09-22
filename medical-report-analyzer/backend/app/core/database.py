"""
app/core/database.py
────────────────────
MongoDB Atlas connection management using Motor (async driver) and Beanie ODM.

Responsibilities:
  - Initialize the Motor async client on application startup.
  - Initialize Beanie with all document models so that collections are
    mapped to typed Python classes.
  - Gracefully close the Motor client on application shutdown.
  - Expose a get_database() helper for direct Motor collection access
    when Beanie's higher-level API is not sufficient.

Usage (in app/main.py):
    from contextlib import asynccontextmanager
    from app.core.database import connect_to_mongo, close_mongo_connection

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await connect_to_mongo()
        yield
        await close_mongo_connection()
"""

from __future__ import annotations

import logging
from typing import Optional

import certifi
import motor.motor_asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

# ── Beanie document models ─────────────────────────────────────────────────
# Import all document models so Beanie can map them to MongoDB collections.
from app.models.user import User
from app.models.doctor_profile import DoctorProfile
from app.models.patient_profile import PatientProfile
from app.models.doctor_patient_request import DoctorPatientRequest
from app.models.medical_report import MedicalReport

logger = logging.getLogger(__name__)

# Module-level Motor client (set during startup, cleared during shutdown).
_client: Optional[AsyncIOMotorClient] = None  # type: ignore[type-arg]
_database: Optional[AsyncIOMotorDatabase] = None  # type: ignore[type-arg]


async def connect_to_mongo() -> None:
    """
    Open the Motor async client and initialise Beanie with all document models.
    Called once during FastAPI application startup via the lifespan context manager.
    """
    global _client, _database

    logger.info("Connecting to MongoDB Atlas…")
    # Use certifi's up-to-date CA bundle to fix the TLS handshake error
    # ([SSL: TLSV1_ALERT_INTERNAL_ERROR]) that occurs on Windows with
    # Python 3.10 / OpenSSL 1.1.1 when the system CA store is incomplete
    # or incompatible with MongoDB Atlas's TLS requirements.
    _client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        tlsCAFile=certifi.where(),
    )
    _database = _client[settings.DATABASE_NAME]

    await init_beanie(
        database=_database,
        document_models=[
            User,
            DoctorProfile,
            PatientProfile,
            DoctorPatientRequest,
            MedicalReport,
        ],
    )

    logger.info(
        "MongoDB connection established. Database: '%s'", settings.DATABASE_NAME
    )


async def close_mongo_connection() -> None:
    """
    Close the Motor client.
    Called once during FastAPI application shutdown via the lifespan context manager.
    """
    global _client, _database

    if _client is not None:
        logger.info("Closing MongoDB connection…")
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:  # type: ignore[type-arg]
    """
    Return the active Motor database instance.

    Raises:
        RuntimeError: If called before connect_to_mongo() has been awaited.

    Usage:
        db = get_database()
        raw_collection = db["some_collection"]
    """
    if _database is None:
        raise RuntimeError(
            "Database is not initialised. "
            "Ensure connect_to_mongo() was called during application startup."
        )
    return _database


async def ping_database() -> bool:
    """
    Send a lightweight ping command to verify the MongoDB connection is alive.

    Returns:
        True if the ping succeeds, False otherwise.
    """
    try:
        db = get_database()
        await db.command("ping")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("MongoDB ping failed: %s", exc)
        return False
