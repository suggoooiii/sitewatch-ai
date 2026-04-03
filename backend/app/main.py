"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import detection, health, images
from app.config import settings
from app.models.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — initialize DB on startup."""
    logger.info("Starting SiteWatch AI backend...")
    await init_db()
    # Ensure uploads directory exists
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    logger.info("Database initialized. Uploads dir: %s", settings.upload_dir)
    yield
    logger.info("Shutting down SiteWatch AI backend.")


app = FastAPI(
    title="SiteWatch AI",
    description="AI-powered construction site safety monitoring platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded images
uploads_path = Path(settings.upload_dir)
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# Register API routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(detection.router, prefix="/api", tags=["detection"])
app.include_router(images.router, prefix="/api", tags=["images"])


@app.get("/")
async def root() -> dict:
    """Root endpoint — redirect users to API docs."""
    return {
        "message": "SiteWatch AI API",
        "docs": "/docs",
        "health": "/api/health",
    }
