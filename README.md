# SiteWatch AI 🏗️

> **AI-Powered Construction Site Safety Monitoring**

[![CI](https://github.com/suggoooiii/sitewatch-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/suggoooiii/sitewatch-ai/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Node](https://img.shields.io/badge/Node-20%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

SiteWatch AI is a real-time, multimodal safety monitoring platform for construction sites. Upload a photo or camera frame, and the platform instantly detects PPE violations, site hazards, and unsafe behaviors using state-of-the-art computer vision from Hugging Face — no GPU required.

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│  Camera Feeds /  │────▶│  Ingestion API   │────▶│  ML Pipeline         │
│  Drone / Mobile  │     │  (FastAPI)       │     │                      │
│  Upload          │     └──────────────────┘     │  ┌─DETR (Detection)  │
└─────────────────┘              │                │  ├─OWL-ViT (Zero-   │
                                 │                │  │  Shot Detection)   │
┌─────────────────┐              │                │  └─Safety Scoring    │
│  Next.js 15      │◀────────────┘                └──────────────────────┘
│  Dashboard       │◀──────Results──────────────────────────┘
│  (Real-time)     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL +    │
│  Redis           │
└─────────────────┘
```

---

## Features

- **🔍 Dual-model detection** — DETR object detection + OWL-ViT zero-shot detection running concurrently via Hugging Face Inference API
- **⚠️ Severity classification** — detections classified as critical / high / medium / low
- **📊 Safety score** — 0–100 score deducted per hazard severity
- **🎨 Bounding box overlay** — HTML5 Canvas draws color-coded boxes over your image
- **📋 History** — all analyses stored in PostgreSQL, browsable in the history page
- **☁️ Cloud inference** — no local GPU needed; works on M1 MacBook Air
- **🐳 Docker Compose** — one command to run the full stack

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS, Radix UI |
| **Backend** | FastAPI, Python 3.11+, SQLAlchemy async |
| **ML Inference** | Hugging Face Inference API (cloud) |
| **Database** | PostgreSQL 16 + SQLite (for tests) |
| **Cache / Queue** | Redis 7 |
| **Containerization** | Docker Compose |
| **CI/CD** | GitHub Actions |

---

## Hugging Face Tasks Used

| Task | Model | Purpose |
|---|---|---|
| **Object Detection** | `facebook/detr-resnet-50` | Detect people, vehicles, equipment |
| **Zero-Shot Object Detection** | `google/owlvit-base-patch32` | Detect PPE violations without retraining |

---

## Quick Start (Docker)

```bash
# 1. Clone the repository
git clone https://github.com/suggoooiii/sitewatch-ai.git
cd sitewatch-ai

# 2. Create your .env file
cp .env.example .env
# Edit .env and add your HUGGINGFACE_API_TOKEN

# 3. Start the full stack
docker-compose up
```

Open http://localhost:3000 in your browser.

---

## Manual Setup

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Add your HUGGINGFACE_API_TOKEN to .env

# Start the API server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `HUGGINGFACE_API_TOKEN` | HF API token (required) | — |
| `DATABASE_URL` | PostgreSQL connection string | SQLite (dev) |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `UPLOAD_DIR` | Image upload directory | `./uploads` |
| `ALLOWED_ORIGINS` | CORS origins | `http://localhost:3000` |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend | `http://localhost:8000` |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/detect` | Upload image and run safety detection |
| `GET` | `/api/health` | Health check (DB + HF API status) |
| `GET` | `/api/images` | List past analyses (pagination: `limit`, `offset`) |
| `GET` | `/uploads/{filename}` | Serve uploaded images as static files |

### Example Response (`POST /api/detect`)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "image_url": "/uploads/abc123.jpg",
  "detections": [
    {
      "label": "person without helmet",
      "confidence": 0.87,
      "bbox": { "x": 120, "y": 45, "width": 80, "height": 200 },
      "severity": "critical",
      "source": "zero-shot"
    }
  ],
  "summary": {
    "total_detections": 5,
    "hazards_found": 2,
    "safety_score": 65,
    "timestamp": "2026-04-03T12:00:00Z"
  },
  "created_at": "2026-04-03T12:00:00Z"
}
```

---

## Severity Logic

| Severity | Labels | Score Deduction |
|---|---|---|
| `critical` | person without helmet, restricted zone | −20 |
| `high` | no safety vest, unsecured scaffolding | −15 |
| `medium` | vehicle near workers | −10 |
| `low` | person with helmet, crane, excavator | −2 |

---

## Screenshots

> _Upload a construction site photo on the Detect page to see it in action._

---

## Roadmap

| Phase | ETA | Description |
|---|---|---|
| ✅ **Phase 1** | Done | Core detection pipeline (DETR + OWL-ViT), FastAPI, Next.js dashboard |
| 🔜 **Phase 2** | Weeks 4–6 | Multimodal reports (ASR, VQA, auto-summarization) |
| 🔜 **Phase 3** | Weeks 7–9 | WebSocket dashboard, time-series forecasting, risk heatmaps |
| 🔜 **Phase 4** | Weeks 10–12 | Auth/RBAC, Hugging Face Space demo, production deployment |

---

## Running Tests

```bash
cd backend
python -m pytest tests/ -v --tb=short
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "feat: add my feature"`
4. Push and open a Pull Request

---

## License

MIT — see [LICENSE](LICENSE) for details.
