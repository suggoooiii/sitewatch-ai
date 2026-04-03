"""Health check endpoint."""

import logging

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import get_db
from app.config import settings
from app.models.schemas import HealthStatus

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """
    Return API health status including DB and HF API connectivity.
    """
    # Check database connectivity
    db_status = "unavailable"
    try:
        async for session in get_db():
            await session.execute(text("SELECT 1"))
            db_status = "ok"
            break
    except Exception as exc:
        logger.warning("Database health check failed: %s", exc)
        db_status = "unavailable"

    # Check HF API token presence (lightweight check — no network call needed)
    hf_status = "ok" if settings.huggingface_api_token else "missing_token"

    overall = "ok" if db_status == "ok" else "degraded"

    return HealthStatus(
        status=overall,
        database=db_status,
        huggingface_api=hf_status,
    )
