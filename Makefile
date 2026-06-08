# DevLens — developer shortcuts
# Note: targets are placeholders for the skeleton; wire up as phases land.

.PHONY: help dev backend frontend test lint deploy bq-views

help:
	@echo "Targets:"
	@echo "  dev        - run backend + frontend + Firestore emulator (docker-compose)"
	@echo "  backend    - run FastAPI locally (uvicorn, reload)"
	@echo "  frontend   - run Next.js dev server"
	@echo "  test       - run backend pytest"
	@echo "  lint       - ruff (backend) + eslint (frontend)"
	@echo "  bq-views   - apply BigQuery metric views (infra/bigquery/sql)"
	@echo "  deploy     - build + deploy backend & frontend to Cloud Run"

dev:
	docker compose up --build

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

bq-views:
	@echo "TODO: apply infra/bigquery/sql/*.sql via bq query --use_legacy_sql=false"

deploy:
	@echo "TODO: gcloud run deploy for backend and frontend (see infra/cloudrun)"
