"""PPE detection service using the fine-tuned YOLOS-Tiny model.

Uses ikigaiii/yolos-tiny-ppe-detection — a YOLOS-Tiny model fine-tuned on
5 000 construction-site images to detect helmets, exposed heads, and persons.

Labels: head (critical), helmet (safe), person (low).
"""

import logging

import httpx

from app.config import settings
from app.utils.severity import classify_severity

logger = logging.getLogger(__name__)

HF_API_URL = "https://router.huggingface.co/hf-inference/models"


async def run_ppe_detection(image_bytes: bytes) -> list[dict]:
    """
    Run PPE detection using the fine-tuned YOLOS-Tiny model via HF Inference API.

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
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{HF_API_URL}/{settings.ppe_model}",
                content=image_bytes,
                headers=headers,
            )
            if response.status_code != 200:
                logger.error(
                    "PPE detection API error %s: %s",
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
                "source": "ppe-detection-yolos",
            })

        logger.info("PPE detection (YOLOS-Tiny) returned %d results", len(detections))
        return detections

    except Exception as exc:
        logger.warning("PPE detection failed (graceful fallback): %s", exc)
        return []
