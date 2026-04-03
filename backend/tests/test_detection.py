"""Tests for the detection endpoint and core pipeline logic."""

from io import BytesIO
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from PIL import Image

from app.utils.severity import calculate_safety_score, classify_severity, is_hazard

# ---------------------------------------------------------------------------
# Unit tests — severity logic
# ---------------------------------------------------------------------------


def test_classify_severity_critical():
    assert classify_severity("person without helmet") == "critical"


def test_classify_severity_high():
    assert classify_severity("no safety vest") == "high"


def test_classify_severity_medium():
    assert classify_severity("vehicle") == "medium"


def test_classify_severity_low():
    assert classify_severity("person with helmet") == "low"
    assert classify_severity("crane") == "low"


def test_classify_severity_unknown_defaults_to_low():
    assert classify_severity("random unknown label") == "low"


def test_is_hazard_returns_true_for_critical():
    assert is_hazard("person without helmet") is True


def test_is_hazard_returns_false_for_safe():
    assert is_hazard("person with helmet") is False
    assert is_hazard("crane") is False


def test_calculate_safety_score_no_hazards():
    detections = [
        {"label": "person with helmet", "severity": "low"},
        {"label": "crane", "severity": "low"},
    ]
    assert calculate_safety_score(detections) == 100


def test_calculate_safety_score_with_hazards():
    detections = [
        {"label": "person without helmet", "severity": "critical"},
        {"label": "no safety vest", "severity": "high"},
    ]
    # 100 - 20 (critical) - 15 (high) = 65
    assert calculate_safety_score(detections) == 65


def test_calculate_safety_score_floors_at_zero():
    detections = [
        {"label": "person without helmet", "severity": "critical"},
    ] * 10  # -200 points
    assert calculate_safety_score(detections) == 0


# ---------------------------------------------------------------------------
# Integration tests — detection endpoint (HF API mocked)
# ---------------------------------------------------------------------------


def _make_test_image() -> bytes:
    """Create a small valid PNG image for testing."""
    img = Image.new("RGB", (100, 100), color=(128, 128, 128))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_detect_endpoint_rejects_non_image(async_client: AsyncClient):
    """Should return 415 for non-image content type."""
    response = await async_client.post(
        "/api/detect",
        files={"file": ("test.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 415


@pytest.mark.asyncio
async def test_detect_endpoint_with_mocked_hf_api(async_client: AsyncClient, tmp_path):
    """Detection endpoint returns structured results with mocked HF API."""
    mock_detections = [
        {
            "label": "person",
            "confidence": 0.9,
            "bbox": {"x": 10.0, "y": 20.0, "width": 50.0, "height": 100.0},
            "severity": "low",
            "source": "object-detection",
        }
    ]

    with (
        patch(
            "app.api.routes.detection.run_object_detection",
            new_callable=AsyncMock,
            return_value=mock_detections,
        ),
        patch(
            "app.api.routes.detection.run_zero_shot_detection",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch(
            "app.api.routes.detection.save_image",
            new_callable=AsyncMock,
            return_value="/uploads/test.png",
        ),
    ):
        image_bytes = _make_test_image()
        response = await async_client.post(
            "/api/detect",
            files={"file": ("test.png", image_bytes, "image/png")},
        )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "image_url" in data
    assert "detections" in data
    assert "summary" in data
    assert "created_at" in data
    assert data["summary"]["total_detections"] == 1
    assert data["summary"]["safety_score"] == 100  # No hazards


@pytest.mark.asyncio
async def test_detect_endpoint_calculates_hazard_score(async_client: AsyncClient):
    """Safety score drops when hazards are detected."""
    mock_detections = [
        {
            "label": "person without helmet",
            "confidence": 0.85,
            "bbox": {"x": 10.0, "y": 20.0, "width": 50.0, "height": 100.0},
            "severity": "critical",
            "source": "zero-shot",
        }
    ]

    with (
        patch(
            "app.api.routes.detection.run_object_detection",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch(
            "app.api.routes.detection.run_zero_shot_detection",
            new_callable=AsyncMock,
            return_value=mock_detections,
        ),
        patch(
            "app.api.routes.detection.save_image",
            new_callable=AsyncMock,
            return_value="/uploads/test2.png",
        ),
    ):
        image_bytes = _make_test_image()
        response = await async_client.post(
            "/api/detect",
            files={"file": ("test.png", image_bytes, "image/png")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["safety_score"] == 80  # 100 - 20 (critical)
    assert data["summary"]["hazards_found"] == 1


@pytest.mark.asyncio
async def test_images_endpoint_returns_list(async_client: AsyncClient):
    """GET /api/images should return a list."""
    response = await async_client.get("/api/images")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_images_endpoint_pagination(async_client: AsyncClient):
    """GET /api/images should accept limit and offset parameters."""
    response = await async_client.get("/api/images?limit=5&offset=0")
    assert response.status_code == 200
