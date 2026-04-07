.PHONY: dev backend frontend install

# Run backend + frontend together (Ctrl+C stops both)
dev:
	@echo "Starting backend (:8000) and frontend (:3000)..."
	@trap 'kill 0' EXIT; \
	(cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000) & \
	(cd frontend && npm run dev) & \
	wait

backend:
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
