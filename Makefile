.PHONY: dev api web test lint docker-up docker-down streamlit

dev:
	@echo "Run in two terminals: 'make api' and 'make web'"

api:
	cd backend && uvicorn app.main:app --reload --port 8000

web:
	cd frontend && npm run dev

test:
	cd backend && pytest -q

lint:
	cd backend && ruff check app tests
	cd frontend && npm run lint

docker-up:
	docker compose up --build

docker-down:
	docker compose down

streamlit:
	streamlit run streamlit/streamlit_app.py