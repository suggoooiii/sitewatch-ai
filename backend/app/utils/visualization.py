"""Bounding box drawing utilities using Pillow."""

from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

# Color mapping per severity level (RGBA)
SEVERITY_COLORS: dict[str, tuple[int, int, int, int]] = {
    "critical": (239, 68, 68, 220),   # red-500
    "high": (249, 115, 22, 220),      # orange-500
    "medium": (234, 179, 8, 220),     # yellow-500
    "low": (34, 197, 94, 220),        # green-500
}

LABEL_BG_COLORS: dict[str, tuple[int, int, int, int]] = {
    "critical": (239, 68, 68, 200),
    "high": (249, 115, 22, 200),
    "medium": (234, 179, 8, 200),
    "low": (34, 197, 94, 200),
}


def draw_detections(image_bytes: bytes, detections: list[dict]) -> bytes:
    """
    Draw bounding boxes and labels on an image.

    Args:
        image_bytes: Raw image bytes.
        detections: List of detection dicts with bbox, label, confidence, severity.

    Returns:
        PNG image bytes with bounding boxes drawn.
    """
    image = Image.open(BytesIO(image_bytes)).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        small_font = font
    except OSError:
        font = ImageFont.load_default()
        small_font = font

    for detection in detections:
        bbox = detection.get("bbox", {})
        x = float(bbox.get("x", 0))
        y = float(bbox.get("y", 0))
        w = float(bbox.get("width", 0))
        h = float(bbox.get("height", 0))
        label = detection.get("label", "unknown")
        confidence = detection.get("confidence", 0.0)
        severity = detection.get("severity", "low")

        color = SEVERITY_COLORS.get(severity, SEVERITY_COLORS["low"])
        label_bg = LABEL_BG_COLORS.get(severity, LABEL_BG_COLORS["low"])

        # Draw bounding box rectangle
        draw.rectangle(
            [(x, y), (x + w, y + h)],
            outline=color,
            width=3,
        )

        # Draw label background and text
        label_text = f"{label} {confidence:.0%}"
        text_bbox = draw.textbbox((0, 0), label_text, font=small_font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        label_y = max(0, y - text_h - 6)

        draw.rectangle(
            [(x, label_y), (x + text_w + 8, label_y + text_h + 6)],
            fill=label_bg,
        )
        draw.text(
            (x + 4, label_y + 3),
            label_text,
            fill=(255, 255, 255, 255),
            font=small_font,
        )

    combined = Image.alpha_composite(image, overlay)
    output = BytesIO()
    combined.convert("RGB").save(output, format="PNG")
    return output.getvalue()
