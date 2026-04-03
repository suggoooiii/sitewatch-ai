"""Zero-shot object detection service using Hugging Face Inference API.

Uses google/owlvit-base-patch32 for construction safety-specific detection.
"""

import logging

from huggingface_hub import InferenceClient

from app.config import settings
from app.utils.severity import classify_severity

logger = logging.getLogger(__name__)

ZERO_SHOT_MODEL = "google/owlvit-base-patch32"

CONSTRUCTION_SAFETY_LABELS = [
    "person without helmet",
    "person with helmet",
    "safety vest",
    "no safety vest",
    "scaffolding",
    "crane",
    "excavator",
    "hard hat",
    "person",
    "vehicle",
]


def _get_client() -> InferenceClient:
    """Return an InferenceClient configured with the HF token."""
    return InferenceClient(token=settings.huggingface_api_token)


async def run_zero_shot_detection(image_bytes: bytes) -> list[dict]:
    """
    Run zero-shot object detection using google/owlvit-base-patch32.

    Args:
        image_bytes: Raw image bytes.

    Returns:
        List of detection dicts with label, confidence, bbox, severity, source.
        Returns an empty list on error (graceful fallback).
    """
    try:
        client = _get_client()

        results = client.zero_shot_object_detection(
            image=image_bytes,
            candidate_labels=CONSTRUCTION_SAFETY_LABELS,
            model=ZERO_SHOT_MODEL,
        )

        detections = []
        for item in results:
            label = item.label if hasattr(item, "label") else item.get("label", "unknown")
            score = item.score if hasattr(item, "score") else item.get("score", 0.0)
            box = item.box if hasattr(item, "box") else item.get("box", {})

            if hasattr(box, "xmin"):
                x = box.xmin
                y = box.ymin
                w = box.xmax - box.xmin
                h = box.ymax - box.ymin
            else:
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
                "source": "zero-shot",
            })

        logger.info("Zero-shot detection returned %d results", len(detections))
        return detections

    except Exception as exc:
        logger.warning("Zero-shot detection failed (graceful fallback): %s", exc)
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
