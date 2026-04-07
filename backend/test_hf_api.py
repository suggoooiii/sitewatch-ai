"""Find models with warm inference that can help with safety detection."""
import httpx
import sys
sys.path.insert(0, ".")
from app.config import settings

h = {"Authorization": f"Bearer {settings.huggingface_api_token}"}
with open("../test_images/images/hard_hat_workers0.png", "rb") as f:
    img = f.read()

# Search across multiple relevant pipeline tags for warm models
tasks = [
    "zero-shot-image-classification",
    "zero-shot-object-detection",
    "object-detection",
    "image-classification",
]

for task in tasks:
    r = httpx.get(
        "https://huggingface.co/api/models",
        params={
            "pipeline_tag": task,
            "inference_provider": "hf-inference",
            "sort": "downloads",
            "direction": "-1",
            "limit": "5",
        },
        headers=h, timeout=30,
    )
    models = r.json()
    print(f"=== {task} (hf-inference provider) === ({len(models)} results)")
    for m in models:
        print(f"  {m['id']} ({m.get('downloads', '?')} downloads)")
    print()

# Try the top object-detection models that have HF inference
r2 = httpx.get(
    "https://huggingface.co/api/models",
    params={
        "pipeline_tag": "object-detection",
        "inference_provider": "hf-inference",
        "sort": "downloads",
        "direction": "-1",
        "limit": "20",
    },
    headers=h, timeout=30,
)
print("=== All object-detection with hf-inference ===")
for m in r2.json():
    print(f"  {m['id']}")
    # Test it
    url = f"https://router.huggingface.co/hf-inference/models/{m['id']}"
    r3 = httpx.post(url, content=img, headers={**h, "Content-Type": "image/png"}, timeout=60)
    print(f"    -> {r3.status_code} | {r3.text[:150]}")
    if r3.status_code == 200:
        break
