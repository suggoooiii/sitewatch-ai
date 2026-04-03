"""Object detection service using Hugging Face Inference API.

Uses the facebook/detr-resnet-50 model for general object detection.
"""

import logging

from huggingface_hub import InferenceClient

from app.config import settings
from app.utils.severity import classify_severity

logger = logging.getLogger(__name__)

DETECTION_MODEL = "facebook/detr-resnet-50"


def _get_client() -> InferenceClient:
    """Return an InferenceClient configured with the HF token."""
    return InferenceClient(token=settings.huggingface_api_token)


async def run_object_detection(image_bytes: bytes) -> list[dict]:
    """
    Run object detection using facebook/detr-resnet-50 via HF Inference API.

    Args:
        image_bytes: Raw image bytes.

    Returns:
        List of detection dicts with label, confidence, bbox, severity, source.
        Returns an empty list on error (graceful fallback).
    """
    try:
        client = _get_client()

        # The InferenceClient.object_detection returns a list of ObjectDetectionOutput
        results = client.object_detection(image=image_bytes, model=DETECTION_MODEL)

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
                "source": "object-detection",
            })

        logger.info("Object detection returned %d results", len(detections))
        return detections

    except Exception as exc:
        logger.warning("Object detection failed (graceful fallback): %s", exc)
        return []
