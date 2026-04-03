"""SQLAlchemy async database models and setup."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class Analysis(Base):
    """Stores analysis results for uploaded images."""

    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    image_path: Mapped[str] = mapped_column(String, nullable=False)
    safety_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    total_detections: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hazards_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    detections: Mapped[list["Detection"]] = relationship(
        "Detection", back_populates="analysis", cascade="all, delete-orphan"
    )


class Detection(Base):
    """Stores individual detection results linked to an analysis."""

    __tablename__ = "detections"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id: Mapped[str] = mapped_column(
        String, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    label: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    bbox_y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    bbox_width: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    bbox_height: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    severity: Mapped[str] = mapped_column(String, nullable=False, default="low")
    source: Mapped[str] = mapped_column(String, nullable=False, default="object-detection")

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="detections")


# Database engine and session factory
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize the database, creating tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:  # type: ignore[override]
    """Dependency that provides a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
