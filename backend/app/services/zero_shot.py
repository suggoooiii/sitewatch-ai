"""Secondary object detection service using Hugging Face Inference API.

Uses facebook/detr-resnet-101 as a second, higher-capacity object detection
model to complement the primary DETR-resnet-50 pipeline. Both models run
concurrently; their results are merged via IoU-based deduplication.

Note: The original design used OWL-ViT / OWLv2 for zero-shot PPE detection,
but those models are not available on HF's free serverless inference tier.
DETR-101 provides more robust general detection as a practical alternative.
"""

import logging

import httpx

from app.config import settings
from app.utils.severity import classify_severity

logger = logging.getLogger(__name__)

HF_API_URL = "https://router.huggingface.co/hf-inference/models"


async def run_zero_shot_detection(image_bytes: bytes) -> list[dict]:
    """
    Run secondary object detection using facebook/detr-resnet-101.

    Keeps the same function signature for backward compatibility with the
    detection route which calls both pipelines via asyncio.gather.

    Args:
        image_bytes: Raw image bytes.

    Returns:
        List of detection dicts with label, confidence, bbox, severity, source.
        Returns an empty list on error (graceful fallback).
    """
    def _mime_type(data: bytes) -> str:
        if data[:4] == b'\x89PNG':
            return "image/png"
        if data[:3] == b'\xff\xd8\xff':
            return "image/jpeg"
        if data[:4] in (b'GIF8', b'GIF9'):
            return "image/gif"
        return "image/jpeg"

    try:
        headers = {
            "Authorization": f"Bearer {settings.huggingface_api_token}",
            "Content-Type": _mime_type(image_bytes),
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{HF_API_URL}/{settings.secondary_model}",
                content=image_bytes,
                headers=headers,
            )
            if response.status_code != 200:
                logger.error(
                    "Secondary detection API error %s: %s",
                    response.status_code,
                    response.text[:500],
                )
                return []
            results = response.json()

        detections = []
        for item in results:
            label = item.get("label", "unknown")
            score = item.get("score", 0.0)
            box = item.get("box", {})
            x = box.get("xmin", 0)
            y = box.get("ymin", 0)
            w = box.get("xmax", 0) - x
            h = box.get("ymax", 0) - y
            severity = classify_severity(label)
            detections.append({
                "label": label,
                "confidence": float(score),
                "bbox": {"x": float(x), "y": float(y), "width": float(w), "height": float(h)},
                "severity": severity,
                "source": "object-detection-resnet101",
            })

        logger.info("Secondary detection (DETR-101) returned %d results", len(detections))
        return detections

    except Exception as exc:
        logger.warning("Secondary detection failed (graceful fallback): %s", exc)
        return []


def deduplicate_detections(
    object_detections: list[dict],
    zero_shot_detections: list[dict],
    iou_threshold: float = 0.5,
) -> list[dict]:
    """
    Combine and deduplicate detections from both models using IoU overlap.

    Zero-shot detections with construction-specific labels take precedence.
    """
    combined = list(zero_shot_detections)

    for od in object_detections:
        is_duplicate = False
        for zs in zero_shot_detections:
            if _iou(od["bbox"], zs["bbox"]) > iou_threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            combined.append(od)

    return combined


def _iou(box_a: dict, box_b: dict) -> float:
    """Compute Intersection over Union (IoU) for two bounding boxes."""
    ax1, ay1 = box_a["x"], box_a["y"]
    ax2, ay2 = ax1 + box_a["width"], ay1 + box_a["height"]

    bx1, by1 = box_b["x"], box_b["y"]
    bx2, by2 = bx1 + box_b["width"], by1 + box_b["height"]

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    union_area = (
        (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter_area
    )

    if union_area <= 0:
        return 0.0
    return inter_area / union_area
