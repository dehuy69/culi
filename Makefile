.PHONY: help setup dev dev-docker up down logs shell db migrate migrate-create test clean

help: ## Show this help message
	@echo "Culi Backend - Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Setup local development environment (see local_dev/README.md for manual steps)
	@echo "Setup guide: See local_dev/README.md for detailed manual setup instructions"
	@echo ""
	@echo "Quick reference:"
	@echo "  1. python3 -m venv venv && source venv/bin/activate"
	@echo "  2. pip install -r requirements.txt"
	@echo "  3. cp .env.example .env && edit .env"
	@echo "  4. cd local_dev && docker-compose up -d postgres"
	@echo "  5. alembic upgrade head"
	@echo "  6. uvicorn app.main:app --reload"

dev: ## Run development server locally (requires venv)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-docker: ## Run development server in Docker (legacy - use dev instead)
	@echo "Note: Use 'make dev' to run locally, or see docker-compose.yml for full Docker setup"

up: ## Start Docker dependencies
	cd local_dev && docker-compose up -d

down: ## Stop Docker dependencies
	cd local_dev && docker-compose down

logs: ## View backend logs
	docker-compose logs -f backend

shell: ## Open shell in backend container
	docker-compose exec backend bash

db: ## Open PostgreSQL shell
	cd local_dev && docker-compose exec postgres psql -U postgres -d culi_db

pgadmin: ## Start pgAdmin (database GUI)
	cd local_dev && docker-compose --profile tools up -d pgadmin
	@echo "pgAdmin available at http://localhost:5050"
	@echo "Email: admin@culi.local"
	@echo "Password: admin"

migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create MESSAGE="description")
	@if [ -z "$(MESSAGE)" ]; then \
		echo "Error: MESSAGE is required. Usage: make migrate-create MESSAGE=\"your message\""; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(MESSAGE)"

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html

lint: ## Run linters
	ruff check app/
	black --check app/

format: ## Format code
	black app/
	ruff check --fix app/

clean: ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f

gen-key: ## Generate encryption key
	python scripts/generate_encryption_key.py

reset-db: ## Reset database (WARNING: deletes all data)
	@echo "⚠️  This will delete all data in the database!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		cd local_dev && docker-compose down -v postgres; \
		cd local_dev && docker-compose up -d postgres; \
		sleep 5; \
		alembic upgrade head; \
		echo "✅ Database reset complete"; \
	fi

