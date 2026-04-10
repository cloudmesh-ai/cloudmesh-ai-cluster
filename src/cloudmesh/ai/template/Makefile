# --- Slurm Docker Cluster Makefile ---

# Variables
COMPOSE  = docker compose
EXEC_CTL = docker exec slurmctld
LOG_DIR  = /var/log/slurm

.PHONY: help build up down restart status test logs shell check-munge clean install

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build the Docker images
	$(COMPOSE) build

up: ## Start the cluster and stabilize
	@echo "Starting Slurm cluster..."
	$(COMPOSE) up -d
	@echo "Waiting 10 seconds for stabilization..."
	@sleep 10
	@echo "Waking up nodes..."
	-$(EXEC_CTL) scontrol update nodename=node[01-02] state=resume
	@$(MAKE) status

down: ## Stop cluster and remove containers
	$(COMPOSE) down

clean: ## Stop cluster and WIPE all volumes/state (Clean slate)
	@echo "Wiping all cluster state and volumes..."
	$(COMPOSE) down -v

install: clean ## Full Clean Install: Wipe state, rebuild no-cache, and start
	@echo "Performing fresh no-cache build..."
	$(COMPOSE) build --no-cache
	@$(MAKE) up
	@echo "------------------------------------------------"
	@echo "Clean Install Complete. Testing..."
	@$(MAKE) test

status: ## Check the current status
	@echo "--- Cluster Status ---"
	@$(EXEC_CTL) sinfo
	@echo "\n--- Node Details ---"
	@$(EXEC_CTL) scontrol show nodes | grep -E 'NodeName|State'

test: ## Run a smoke test job across both nodes
	@echo "Running test: srun -N2 hostname"
	-@$(EXEC_CTL) srun -N2 hostname

check-munge: ## Verify Munge handshake
	@$(EXEC_CTL) munge -n | docker exec node01 unmunge && echo "Munge Handshake: SUCCESS" || echo "Munge Handshake: FAILED"