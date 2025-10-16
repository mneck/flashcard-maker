# Convenience Makefile for dev workflow

.PHONY: help backend backend-bg stop-backend stop-ports frontend frontend-build frontend-preview

# Default app port; can be overridden: `make backend APP_PORT=8001`
APP_PORT ?= 8000

help:
	@echo "Available targets:"
	@echo "  make backend            # Start FastAPI (foreground) on $${APP_PORT}"
	@echo "  make backend-bg         # Start FastAPI in background on $${APP_PORT}"
	@echo "  make stop-backend       # Kill process listening on $${APP_PORT}"
	@echo "  make stop-ports         # Kill anything on ports 8000,8001,8002"
	@echo "  make frontend           # Run Vite dev server (frontend)"
	@echo "  make frontend-build     # Build frontend"
	@echo "  make frontend-preview   # Preview built frontend"

backend:
	. venv/bin/activate && APP_PORT=$(APP_PORT) python main.py

backend-bg:
	. venv/bin/activate && APP_PORT=$(APP_PORT) nohup python main.py >/tmp/flashcards-backend.out 2>&1 & echo $$! > /tmp/flashcards-backend.pid && echo "Backend started (PID $$(cat /tmp/flashcards-backend.pid)) on port $${APP_PORT}"

stop-backend:
	@pids=$$(lsof -nPiTCP:$(APP_PORT) -sTCP:LISTEN -t 2>/dev/null); \
	if [ -n "$$pids" ]; then \
		kill -9 $$pids; \
		echo "Killed backend on port $(APP_PORT) (PIDs: $$pids)"; \
	else \
		echo "No process listening on port $(APP_PORT)"; \
	fi

stop-ports:
	@for port in 8000 8001 8002; do \
		pids=$$(lsof -nPiTCP:$$port -sTCP:LISTEN -t 2>/dev/null); \
		if [ -n "$$pids" ]; then kill -9 $$pids && echo "Killed processes on port $$port (PIDs: $$pids)"; else echo "Port $$port free"; fi; \
	done

frontend:
	cd frontend && yarn dev

frontend-build:
	cd frontend && yarn build

frontend-preview:
	cd frontend && yarn preview


