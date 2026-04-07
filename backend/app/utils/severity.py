"""Severity classification and safety score utilities."""

# Labels that map to each severity level
SEVERITY_LABELS: dict[str, set[str]] = {
    "critical": {
        "head",
        "person without helmet",
        "person in restricted zone",
        "no helmet",
        "worker without ppe",
    },
    "high": {
        "no safety vest",
        "unsecured scaffolding",
        "missing safety vest",
        "no high visibility vest",
    },
    "medium": {
        "vehicle near workers",
        "forklift near workers",
        "vehicle",
    },
    "low": {
        "person",
        "person with helmet",
        "safety vest",
        "hard hat",
        "crane",
        "excavator",
        "scaffolding",
        "worker",
        "helmet",
    },
}

# Points deducted per severity level
SEVERITY_DEDUCTIONS: dict[str, int] = {
    "critical": 20,
    "high": 15,
    "medium": 10,
    "low": 2,
}

# Labels considered hazards (not normal safe observations)
HAZARD_LABELS: set[str] = SEVERITY_LABELS["critical"] | SEVERITY_LABELS["high"] | SEVERITY_LABELS["medium"]


def classify_severity(label: str) -> str:
    """
    Classify the severity of a detection based on its label.

    Returns one of: "critical", "high", "medium", "low"
    """
    label_lower = label.lower().strip()

    for severity, labels in SEVERITY_LABELS.items():
        if label_lower in labels:
            return severity

    # Keyword-based fallback
    if any(k in label_lower for k in ("without helmet", "no helmet", "restricted zone")):
        return "critical"
    if any(k in label_lower for k in ("no safety vest", "unsecured", "no vest")):
        return "high"
    if any(k in label_lower for k in ("vehicle", "forklift", "truck")):
        return "medium"

    return "low"


def is_hazard(label: str) -> bool:
    """Return True if the label represents a safety hazard."""
    label_lower = label.lower().strip()
    if label_lower in HAZARD_LABELS:
        return True
    # Keyword-based fallback
    return any(k in label_lower for k in ("without", "no safety", "no vest", "restricted"))


def calculate_safety_score(detections: list[dict]) -> int:
    """
    Calculate an overall safety score (0–100) based on detections.

    Starts at 100 and deducts points per hazard severity.
    """
    score = 100
    for detection in detections:
        severity = detection.get("severity", "low")
        if is_hazard(detection.get("label", "")):
            score -= SEVERITY_DEDUCTIONS.get(severity, 2)
    return max(0, score)
