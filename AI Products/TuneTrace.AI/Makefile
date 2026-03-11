.PHONY: help install install-frontend dev dev-backend dev-frontend build clean test

help:
	@echo "TuneTrace.AI - Makefile Commands"
	@echo "================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install           - Install all dependencies (backend + frontend)"
	@echo "  make install-frontend  - Install frontend dependencies only"
	@echo ""
	@echo "Development:"
	@echo "  make dev               - Run full stack (backend + frontend)"
	@echo "  make dev-backend       - Run backend API only (port 8000)"
	@echo "  make dev-frontend      - Run frontend only (port 3000)"
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run all tests"
	@echo "  make test-integration  - Run integration tests"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean             - Clean build artifacts"
	@echo "  make build             - Build frontend for production"
	@echo ""

install:
	@echo "📦 Installing backend dependencies..."
	pip install -e ".[dev]"
	pip install fastapi uvicorn[standard] pydantic
	@echo ""
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo ""
	@echo "✅ Installation complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Set GOOGLE_API_KEY: export GOOGLE_API_KEY='your-key'"
	@echo "2. Run: make dev"

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Frontend dependencies installed!"

dev:
	@echo "🚀 Starting TuneTrace.AI full stack..."
	@echo ""
	@echo "Backend will run on: http://localhost:8000"
	@echo "Frontend will run on: http://localhost:3000"
	@echo ""
	@echo "Press Ctrl+C to stop both servers"
	@echo ""
	@make -j2 dev-backend dev-frontend

dev-backend:
	@echo "🔧 Starting backend API..."
	@if [ -f .env ]; then \
		echo "📄 Loading configuration from .env file..."; \
	fi
	@bash -c 'set -a; [ -f .env ] && source .env; set +a; cd app && python main.py'

dev-frontend:
	@echo "⚛️  Starting frontend..."
	cd frontend && npm run dev

build:
	@echo "🏗️  Building frontend for production..."
	cd frontend && npm run build
	@echo "✅ Build complete! Output in frontend/dist/"

test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

test-integration:
	@echo "🧪 Running integration tests..."
	python deployment/test_deployment.py

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf frontend/dist
	rm -rf frontend/node_modules
	rm -rf **/__pycache__
	rm -rf **/*.pyc
	rm -rf .pytest_cache
	rm -rf *.egg-info
	@echo "✅ Clean complete!"


