.PHONY: setup dev dev-docker lint format test build help

help:
	@echo "🛡️ SentinelOps Development Commands"
	@echo ""
	@echo "  setup         Install dependencies and setup environment"
	@echo "  dev           Start frontend and backend in development mode"
	@echo "  dev-docker    Start frontend locally and backend via Docker Compose"
	@echo "  lint          Run linters for both frontend and backend"
	@echo "  format        Run formatters (black, isort, prettier)"
	@echo "  test          Run tests for both frontend and backend"
	@echo "  build         Build the frontend for production"
	@echo ""

setup:
	bash scripts/setup.sh

dev:
	npm run dev

dev-docker:
	npm run dev:docker

lint:
	@echo "🔍 Linting Frontend..."
	cd sentinelops-frontend && npm run lint
	@echo "🔍 Linting Backend..."
	cd sentinelops-backend && .venv/bin/python3 -m flake8 .

format:
	@echo "🎨 Formatting Backend..."
	cd sentinelops-backend && .venv/bin/python3 -m black . && .venv/bin/python3 -m isort .
	@echo "🎨 Formatting Frontend..."
	cd sentinelops-frontend && npx prettier --write .

test:
	@echo "🧪 Testing Backend..."
	cd sentinelops-backend && .venv/bin/python3 -m pytest
	@echo "🧪 Testing Frontend..."
	# Add frontend tests here if any exist

build:
	npm run build
