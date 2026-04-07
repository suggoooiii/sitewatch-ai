# SiteWatch AI — Copilot Instructions

Full-stack construction-site safety monitoring: FastAPI backend + Next.js 15 frontend, triple ML pipeline (DETR-ResNet-50 + DETR-ResNet-101 + YOLOS-Tiny-PPE) via Hugging Face Inference API, PostgreSQL + Redis via Docker Compose.

---

## Build & Test

**Full stack:**

```bash
docker compose up --build       # start all services
docker compose up -d db         # start only Postgres (for local backend dev)
```

**Backend:**

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Tests (uses in-memory SQLite — no running DB required):**

```bash
cd backend
pytest          # asyncio_mode=auto — no @pytest.mark.asyncio needed
pytest -v       # verbose
```

**Lint/format:**

```bash
ruff check .
ruff format .
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev     # :3000
```

---

## Architecture

```
Next.js :3000  →  FastAPI :8000  →  HF Inference API (cloud)
                       │
                 PostgreSQL :5432   (Docker: pgdata volume)
                 Redis :6379        (Docker; not yet used in routes)
```

Key modules:

| File                                    | Role                                                                                                                                                 |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `backend/app/api/routes/detection.py`   | Full request lifecycle: validate → save image → concurrent HF calls → persist → respond                                                              |
| `backend/app/models/database.py`        | ORM models (`Analysis`, `Detection`) + engine + `init_db()` (called at startup via lifespan)                                                         |
| `backend/app/utils/severity.py`         | Label→severity mapping and `calculate_safety_score()` — primary domain logic                                                                         |
| `backend/app/services/zero_shot.py`     | DETR-ResNet-101 secondary detection; `deduplicate_detections()` merges pipelines via IoU. File retains its original name for backward compatibility. |
| `backend/app/services/ppe_detection.py` | Fine-tuned YOLOS-Tiny PPE detection (`ikigaiii/yolos-tiny-ppe-detection`); detects `head`, `helmet`, `person` with construction-specific accuracy.   |
| `frontend/lib/api.ts`                   | All backend fetch calls; reads `NEXT_PUBLIC_API_URL`                                                                                                 |
| `frontend/types/detection.ts`           | TypeScript interfaces mirroring backend Pydantic schemas                                                                                             |

---

## Conventions

- **Triple detection:** Every image runs DETR-ResNet-50 + DETR-ResNet-101 + YOLOS-Tiny-PPE concurrently via `asyncio.gather`. Each detection carries `source: "object-detection" | "object-detection-resnet101" | "ppe-detection-yolos"`. DETR results are merged first, then YOLOS PPE results are merged with priority via IoU-based deduplication.
- **Severity is label-based, not confidence-based.** `classify_severity()` in `severity.py` uses hardcoded label sets. Confidence is stored but doesn't affect severity.
- **Safety score:** start at 100, deduct per hazard (`critical=-20`, `high=-15`, `medium=-10`, `low=-2`), floor 0.
- **UUID PKs as strings:** `String` columns with `default=lambda: str(uuid.uuid4())`, not native DB UUID type.
- **BBox flattened in DB:** stored as `bbox_x/y/width/height`, reassembled into `BoundingBox` at read time.
- **No auth** on any endpoint.
- **`get_db()` exists in two places:** `deps.py` (used by most routes via DI) and `database.py` (used directly by the health route). Do not add a third.
- **SQLAlchemy 2.0 style:** Use `Mapped`/`mapped_column` typed declarative — not legacy `Column()`.
- **Pydantic v2 + pydantic-settings:** Use `model_config = SettingsConfigDict(...)`, not `class Config`.

---

## Pitfalls

- **`HUGGINGFACE_API_TOKEN` missing:** Both services silently return `[]` — endpoint returns 200 with empty detections and `safety_score: 100`. Always set the token in `.env`.
- **No Alembic migrations:** Tables are created by `Base.metadata.create_all` at startup. Adding a column to a model requires dropping the table or running a manual `ALTER TABLE`. There is no `alembic/` directory.
- **Local dev uses SQLite, Docker uses Postgres.** Behavioral differences (UUID handling, cascades) won't surface in `pytest`. Run integration tests against the Docker stack for full coverage.
- **`psql` needs `-h localhost`.** Postgres runs only in Docker; the local Unix socket (`/tmp/.s.PGSQL.5432`) does not exist. Connect with: `psql -h localhost -U sitewatch -d sitewatch` (password: `sitewatch`).
- **Redis is installed but unused.** The `redis` package and `REDIS_URL` setting exist; no caching or queuing code is wired to routes yet.
- **`asyncio_mode=auto` + session-scoped event loop in conftest** may emit deprecation warnings with newer `pytest-asyncio` (≥0.24). This is a known issue in the test setup.

---

## Environment Variables

| Variable                | Default                              | Notes                                                                            |
| ----------------------- | ------------------------------------ | -------------------------------------------------------------------------------- |
| `HUGGINGFACE_API_TOKEN` | `""`                                 | **Required** for real detections                                                 |
| `DATABASE_URL`          | `sqlite+aiosqlite:///./sitewatch.db` | Docker overrides to `postgresql+asyncpg://sitewatch:sitewatch@db:5432/sitewatch` |
| `REDIS_URL`             | `redis://localhost:6379`             | Not yet consumed by routes                                                       |
| `UPLOAD_DIR`            | `./uploads`                          | Images served at `/uploads/{filename}`                                           |
| `ALLOWED_ORIGINS`       | `http://localhost:3000`              | Comma-separated; parsed by `settings.allowed_origins_list`                       |
| `NEXT_PUBLIC_API_URL`   | `http://localhost:8000`              | Frontend only; used in `frontend/lib/api.ts`                                     |

Copy `.env.example` → `.env` in the repo root and in `backend/` before starting.
