"""History endpoint — list past analyses."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models.database import Analysis
from app.models.schemas import AnalysisResult, AnalysisSummary, BoundingBox, DetectionResponse

logger = logging.getLogger(__name__)
router = APIRouter()


def _analysis_to_result(analysis: Analysis) -> AnalysisResult:
    """Convert an Analysis ORM object to an AnalysisResult schema."""
    detections = [
        DetectionResponse(
            label=d.label,
            confidence=d.confidence,
            bbox=BoundingBox(x=d.bbox_x, y=d.bbox_y, width=d.bbox_width, height=d.bbox_height),
            severity=d.severity,
            source=d.source,
        )
        for d in analysis.detections
    ]
    return AnalysisResult(
        id=analysis.id,
        image_url=analysis.image_path,
        detections=detections,
        summary=AnalysisSummary(
            total_detections=analysis.total_detections,
            hazards_found=analysis.hazards_found,
            safety_score=analysis.safety_score,
            timestamp=analysis.created_at,
        ),
        created_at=analysis.created_at,
    )


@router.get("/images", response_model=list[AnalysisResult])
async def list_analyses(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[AnalysisResult]:
    """Return a paginated list of past analyses."""
    stmt = (
        select(Analysis)
        .options(selectinload(Analysis.detections))
        .order_by(Analysis.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    analyses = result.scalars().all()
    return [_analysis_to_result(a) for a in analyses]
