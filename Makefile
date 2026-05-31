# ─── Candidate Finder API — Makefile ──────────────────────────────────────
# Convenience commands for development, testing, and demos.
#
# IMPORTANT: Commands use venv/bin/ paths directly instead of relying on
# 'source venv/bin/activate' because Make runs each line in a separate shell.
#
# Usage:
#   make install     — Set up virtual environment and install dependencies
#   make run         — Start the API server
#   make test        — Run all unit tests
#   make demo        — Start the API (for demo purposes, with extra logging)
#   make health      — Quick health check via curl
#   make search      — Run a sample search via curl
#   make clean       — Remove venv and cache files

.PHONY: install run test demo health search clean

# ── Setup ─────────────────────────────────────────────────────────────────

install:
	python3 -m venv venv && \
	venv/bin/pip install -r requirements.txt
	@echo "✅ Done! Activate with: source venv/bin/activate"

# ── Run / Demo ────────────────────────────────────────────────────────────
# Using venv/bin/uvicorn directly so Make doesn't need a sourced environment

run:
	venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000

demo:
	@echo "🚀 Starting Candidate Finder API..."
	@echo "   Swagger UI: http://localhost:8000/docs"
	@echo "   Health:     http://localhost:8000/"
	@echo ""
	venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level info

# ── Testing ───────────────────────────────────────────────────────────────

test:
	venv/bin/pytest tests/ -v

test-quick:
	venv/bin/pytest tests/ -q

# ── API Calls (requires running server) ───────────────────────────────────

health:
	@curl -s http://localhost:8000/ | python3 -m json.tool

search:
	@echo "Searching: Customer Success Manager, 3+ years, fintech background, Bangalore"
	@echo ""
	@curl -s -X POST http://localhost:8000/search \
		-H "Content-Type: application/json" \
		-d '{"requirement": "Customer Success Manager, 3+ years, fintech / financial services background, in Bangalore or Delhi NCR."}' | \
		python3 -m json.tool

# ── Cleanup ───────────────────────────────────────────────────────────────

clean:
	rm -rf venv/
	rm -rf __pycache__/ .pytest_cache/
	rm -rf app/__pycache__/ tests/__pycache__/
	rm -f output/*.json
	@echo "✅ Cleaned up!"
