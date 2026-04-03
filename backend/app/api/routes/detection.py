"""Detection endpoint — POST /api/detect."""

import logging
import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.database import Analysis, Detection
from app.models.schemas import AnalysisResult, AnalysisSummary, BoundingBox, DetectionResponse
from app.services.detection import run_object_detection
from app.services.image_storage import save_image
from app.services.zero_shot import deduplicate_detections, run_zero_shot_detection
from app.utils.severity import calculate_safety_score, is_hazard

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/detect", response_model=AnalysisResult, status_code=status.HTTP_200_OK)
async def detect(
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(..., description="Image file to analyze (jpg, png, webp, max 10MB)"),
) -> AnalysisResult:
    """
    Upload an image, run safety detection, and return structured results.

    - Runs DETR object detection + OWL-ViT zero-shot detection via HF Inference API
    - Classifies severity of each detection
    - Calculates an overall safety score (0–100)
    - Stores results in PostgreSQL
    """
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {ALLOWED_CONTENT_TYPES}",
        )

    # Read image bytes
    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds 10 MB limit",
        )

    # Save image to disk
    image_url = await save_image(image_bytes, file.filename or "upload.jpg")

    # Run both detection pipelines concurrently (graceful fallback on error)
    import asyncio

    object_results, zero_shot_results = await asyncio.gather(
        run_object_detection(image_bytes),
        run_zero_shot_detection(image_bytes),
    )

    # Combine and deduplicate detections
    all_detections = deduplicate_detections(object_results, zero_shot_results)

    # Calculate summary stats
    hazards = [d for d in all_detections if is_hazard(d["label"])]
    safety_score = calculate_safety_score(all_detections)
    now = datetime.now(UTC)

    # Persist to database
    analysis_id = str(uuid.uuid4())
    analysis = Analysis(
        id=analysis_id,
        image_path=image_url,
        safety_score=safety_score,
        total_detections=len(all_detections),
        hazards_found=len(hazards),
        created_at=now,
    )
    db.add(analysis)

    detection_rows = []
    for d in all_detections:
        bbox = d["bbox"]
        det = Detection(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            label=d["label"],
            confidence=d["confidence"],
            bbox_x=bbox["x"],
            bbox_y=bbox["y"],
            bbox_width=bbox["width"],
            bbox_height=bbox["height"],
            severity=d["severity"],
            source=d["source"],
        )
        db.add(det)
        detection_rows.append(det)

    await db.flush()

    # Build response
    detection_responses = [
        DetectionResponse(
            label=d["label"],
            confidence=d["confidence"],
            bbox=BoundingBox(**d["bbox"]),
            severity=d["severity"],
            source=d["source"],
        )
        for d in all_detections
    ]

    return AnalysisResult(
        id=analysis_id,
        image_url=image_url,
        detections=detection_responses,
        summary=AnalysisSummary(
            total_detections=len(all_detections),
            hazards_found=len(hazards),
            safety_score=safety_score,
            timestamp=now,
        ),
        created_at=now,
    )
