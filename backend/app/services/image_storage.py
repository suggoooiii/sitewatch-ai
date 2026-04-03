"""Image storage service for saving and retrieving uploaded images."""

import uuid
from pathlib import Path

from app.config import settings


def get_upload_dir() -> Path:
    """Return the upload directory, creating it if it doesn't exist."""
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


async def save_image(file_bytes: bytes, filename: str) -> str:
    """
    Save image bytes to the uploads directory.

    Returns:
        The relative URL path for the saved image (e.g. /uploads/abc123.jpg).
    """
    upload_dir = get_upload_dir()
    ext = Path(filename).suffix.lower() or ".jpg"
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = upload_dir / unique_name

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return f"/uploads/{unique_name}"


def get_image_path(image_url: str) -> Path:
    """Resolve a /uploads/<filename> URL to a local file path."""
    filename = image_url.lstrip("/uploads/")
    return get_upload_dir() / filename


def read_image(image_url: str) -> bytes | None:
    """Read image bytes from an /uploads/ URL. Returns None if not found."""
    path = get_image_path(image_url)
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return f.read()
