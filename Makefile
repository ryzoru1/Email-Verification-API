.PHONY: install dev run test lint format clean docker-build docker-run

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

test:
	pytest -q

lint:
	ruff check .

format:
	ruff check . --fix

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +

docker-build:
	docker build -t email-verification-api .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env email-verification-api
