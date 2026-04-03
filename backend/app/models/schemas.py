"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box coordinates for a detection."""

    x: float = Field(..., description="X coordinate (left edge)")
    y: float = Field(..., description="Y coordinate (top edge)")
    width: float = Field(..., description="Width of the bounding box")
    height: float = Field(..., description="Height of the bounding box")


class DetectionResponse(BaseModel):
    """Single detection result."""

    label: str
    confidence: float
    bbox: BoundingBox
    severity: str  # "critical" | "high" | "medium" | "low"
    source: str  # "object-detection" | "zero-shot"


class AnalysisSummary(BaseModel):
    """Summary statistics for an analysis run."""

    total_detections: int
    hazards_found: int
    safety_score: int
    timestamp: datetime


class AnalysisResult(BaseModel):
    """Full analysis result returned from the detect endpoint."""

    id: str
    image_url: str
    detections: list[DetectionResponse]
    summary: AnalysisSummary
    created_at: datetime


class HealthStatus(BaseModel):
    """Health check response."""

    status: str
    database: str
    huggingface_api: str
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    detail: str | None = None
