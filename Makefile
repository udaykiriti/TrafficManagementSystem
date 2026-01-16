# AI Traffic Management System Makefile

# Variables
DC_PROD := docker-compose
DC_DEV  := docker-compose -f docker-compose.dev.yml
SHELL   := /bin/bash

# Colors for terminal output
BLUE   := \033[34m
CYAN   := \033[36m
GREEN  := \033[32m
RESET  := \033[0m
BOLD   := \033[1m

.PHONY: help setup up down logs status clean dev restart shell-backend shell-frontend

# --- HELP ---
define HEADER
    ___    ____   ______ ____   ___     ______ ______  ____  ______
   /   |  /  _/  /_  __// __ \ /   |   / ____// ____/ /  _/ / ____/
  / /| |  / /     / /  / /_/ // /| |  / /_   / /_     / /  / /     
 / ___ | _/ /    / /  / _, _// ___ | / __/  / __/   _/ /  / /___   
/_/  |_|/___/   /_/  /_/ |_|/_/  |_|/_/    /_/     /___/  \____/   
                                                                   
endef
export HEADER

help:
	@echo -e "$(BLUE)$$HEADER$(RESET)"
	@echo -e "$(BOLD)Management Commands:$(RESET)"
	@echo -e "  $(CYAN)make setup$(RESET)          Download weights and build Docker images"
	@echo -e "  $(CYAN)make up$(RESET)             Start services in production mode (detached)"
	@echo -e "  $(CYAN)make dev$(RESET)            Start services in development mode"
	@echo -e "  $(CYAN)make down$(RESET)           Stop all services"
	@echo -e "  $(CYAN)make restart$(RESET)        Restart all services"
	@echo -e "  $(CYAN)make logs$(RESET)           View logs from all services"
	@echo -e "  $(CYAN)make status$(RESET)         Check status of containers"
	@echo -e "  $(CYAN)make clean$(RESET)          Remove containers, volumes, and local images"
	@echo -e ""
	@echo -e "$(BOLD)Shell Access:$(RESET)"
	@echo -e "  $(CYAN)make shell-backend$(RESET)   Access backend container"
	@echo -e "  $(CYAN)make shell-frontend$(RESET)  Access frontend container"

# --- CORE COMMANDS ---

setup:
	@echo -e "$(GREEN)>>> Downloading YOLO weights...$(RESET)"
	cd backend && bash download.sh
	@echo -e "$(GREEN)>>> Building Docker images...$(RESET)"
	$(DC_PROD) build

up:
	@echo -e "$(GREEN)>>> Starting services (Production)...$(RESET)"
	$(DC_PROD) up -d
	@echo -e "$(BOLD)Services available at:$(RESET)"
	@echo -e "  Frontend: http://localhost:3000"
	@echo -e "  Backend:  http://localhost:5000"

dev:
	@echo -e "$(GREEN)>>> Starting services (Development)...$(RESET)"
	$(DC_DEV) up --build

down:
	@echo -e "$(CYAN)>>> Stopping services...$(RESET)"
	$(DC_PROD) down

restart: down up

logs:
	$(DC_PROD) logs -f

status:
	$(DC_PROD) ps

clean:
	@echo -e "$(CYAN)>>> Deep cleaning containers and volumes...$(RESET)"
	$(DC_PROD) down -v --rmi local
	@echo -e "$(GREEN)>>> Clean complete.$(RESET)"

# --- SHELL ACCESS ---

shell-backend:
	$(DC_PROD) exec backend bash

shell-frontend:
	$(DC_PROD) exec frontend sh