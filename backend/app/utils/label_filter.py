"""Post-processing for COCO labels from generic DETR models.

DETR models detect 80 COCO classes, many of which are irrelevant on
construction sites (e.g. "banana", "pizza").  Worse, some labels are
systematic misclassifications — red helmets → "traffic light",
safety vests → "sports ball", etc.

This module provides:
  - remap_label(): fix known COCO misclassifications in a construction context
  - is_construction_relevant(): filter out labels that add noise
"""

# COCO labels that commonly appear on construction sites
CONSTRUCTION_RELEVANT: set[str] = {
    "person",
    "bicycle",
    "car",
    "motorcycle",
    "bus",
    "truck",
    "fire hydrant",
    "stop sign",
    "backpack",
    # Labels produced by remap (below)
    "helmet",
    "head",
    "safety vest",
}

# Known DETR misclassifications in construction imagery.
# Maps the wrong COCO label to the corrected construction label.
LABEL_REMAP: dict[str, str] = {
    "traffic light": "helmet",
    "sports ball": "helmet",
    "frisbee": "helmet",
    "bowl": "helmet",
    "kite": "safety vest",
    "umbrella": "helmet",
}


def remap_label(label: str) -> str:
    """Return the corrected label if this is a known COCO misclassification."""
    return LABEL_REMAP.get(label.lower().strip(), label)


def is_construction_relevant(label: str) -> bool:
    """Return True if the (possibly remapped) label is useful on a construction site."""
    lower = label.lower().strip()
    if lower in CONSTRUCTION_RELEVANT:
        return True
    # Keep any label that has a non-low severity (it's a known hazard/PPE term)
    from app.utils.severity import classify_severity
    return classify_severity(lower) != "low"


def postprocess_detections(detections: list[dict]) -> list[dict]:
    """Remap and filter a list of detections in-place.

    1. Remap known misclassifications (traffic light → helmet, etc.)
    2. Drop detections whose labels are irrelevant to construction sites.
    """
    from app.utils.severity import classify_severity

    result = []
    for det in detections:
        original = det["label"]
        remapped = remap_label(original)
        if not is_construction_relevant(remapped):
            continue
        det["label"] = remapped
        if remapped != original:
            det["severity"] = classify_severity(remapped)
        result.append(det)
    return result
