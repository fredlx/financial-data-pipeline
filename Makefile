# === Environment Setup ===
AIRFLOW_DIR := $(CURDIR)/airflow_home
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

export AIRFLOW_HOME := $(AIRFLOW_DIR)
export AIRFLOW__CORE__LOAD_EXAMPLES=False

.PHONY: init run stop restart check-env kill-examples clean-core clean-logs clean-data \
        purge-dag-runs purge-dag-runs-soft full-reset refresh-dags soft-purge status

# === Setup ===
init:
	@echo "[init] Creating virtualenv and installing dependencies..."
	@if [ ! -d "$(VENV)" ]; then \
		python3 -m venv $(VENV); \
	fi
	$(PIP) install --upgrade pip
	$(PIP) install apache-airflow yfinance ta pandas pyarrow pandas-market-calendars
	$(PYTHON) -m airflow db migrate
	mkdir -p $(AIRFLOW_HOME)/dags
	mkdir -p $(AIRFLOW_HOME)/logs
	cp -r dags/* $(AIRFLOW_HOME)/dags/

check-env:
	@echo "[check-env] Showing environment configuration:"
	@echo "VENV         = $(VENV)"
	@echo "PYTHON       = $(PYTHON)"
	@echo "PIP          = $(PIP)"
	@echo "AIRFLOW_HOME = $(AIRFLOW_HOME)"
	@$(PYTHON) -m airflow info

kill-examples:
	@echo "[kill-examples] Removing example DAGs..."
	@if $(PYTHON) -m airflow dags list | grep -q example; then \
		for dag in $$($(PYTHON) -m airflow dags list | grep example | awk '{print $$1}'); do \
			echo "Deleting $$dag..."; \
			$(PYTHON) -m airflow dags delete --yes $$dag || true; \
		done \
	else \
		echo "No example DAGs found."; \
	fi

# === Execution ===
run:
	@echo "[run] Syncing Dags and Starting Airflow standalone..."
	@cp -r dags/* $(AIRFLOW_HOME)/dags/
	PYTHONPATH=$(CURDIR) AIRFLOW_HOME=$(AIRFLOW_DIR) $(PYTHON) -m airflow standalone

stop:
	@echo "[stop] Stopping all Airflow processes..."
	@bash -c 'sleep 0.1 && pkill -f "airflow webserver"' &
	@bash -c 'sleep 0.1 && pkill -f "airflow scheduler"' &
	@bash -c 'sleep 0.1 && pkill -f "airflow triggerer"' &
	@bash -c 'sleep 0.1 && lsof -ti:8793 | xargs -r kill -9 || true' &
	@bash -c 'sleep 0.1 && lsof -ti:8794 | xargs -r kill -9 || true' &
	@sleep 0.5

restart: stop clean-core refresh-dags run
	@echo "[restart] Airflow restarted with DAGs refreshed."

status:
	@echo "[status] Listing active DAGs and running Airflow processes..."
	@$(PYTHON) -m airflow dags list
	@echo "\n[status] Running processes:"
	@ps aux | grep 'airflow ' | grep -v grep

# === Cleaning ===
clean-core:
	@echo "[clean-core] Cleaning Airflow logs and PIDs..."
	@rm -rf $(AIRFLOW_DIR)/logs/*
	@rm -f $(AIRFLOW_DIR)/airflow-webserver.pid
	@rm -f $(AIRFLOW_DIR)/airflow-scheduler.pid

clean-logs:
	@echo "[clean-logs] Deleting all logs..."
	@rm -rf $(AIRFLOW_DIR)/logs/*

clean-data:
	@read -p "[clean-data] This will delete all contents in data/. Continue? [y/N] " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "Deleting data/* ..."; \
		rm -rf data/*; \
	else \
		echo "Cancelled."; \
	fi

# === DAG and Metadata Management ===
purge-dag-runs:
	@echo "[purge-dag-runs] Deleting all DAGs and their history from metadata DB..."
	@for dag in $$($(PYTHON) -m airflow dags list | awk 'NR>2 {print $$1}'); do \
		echo "Deleting DAG: $$dag"; \
		$(PYTHON) -m airflow dags delete --yes $$dag || true; \
	done
	@find $(AIRFLOW_HOME)/dags -name "*.py" -exec touch {} +

purge-dag-runs-soft:
	@echo "[purge-dag-runs-soft] Clearing DAG runs (preserving DAGs)..."
	@$(PYTHON) -m airflow dags list | awk 'NR>2 {print $$1}' | while read dag; do \
		echo "Clearing runs for DAG: $$dag"; \
		$(PYTHON) -m airflow dags clear $$dag --yes; \
	done

refresh-dags:
	@echo "[refresh-dags] Touching DAG files to force reload..."
	@find dags -name "*.py" -exec touch {} +

soft-purge: stop
	@echo "[soft-purge] Clearing logs, pycache, and refreshing DAGs..."
	@find . -type d -name "__pycache__" -exec rm -r {} +
	@find dags -name "*.pyc" -delete
	@rm -rf $(AIRFLOW_HOME)/logs/*
	@find dags -name "*.py" -exec touch {} +

# === Hard Reset ===
full-reset:
	@echo "[full-reset] Removing virtualenv and airflow_home..."
	rm -rf $(AIRFLOW_DIR) $(VENV)



# === Docs ===
doc:
	@echo "## 🛠 Makefile Commands"
	@echo ""
	@echo "| Target | Description | When to Use |"
	@echo "|--------|-------------|--------------|"
	@echo "| init | Creating virtualenv and installing dependencies... | First time setup or after full-reset |"
	@echo "| check-env | Showing environment configuration... | Confirm Airflow paths and config |"
	@echo "| kill-examples | Removing example DAGs... | Cleanup after initial install |"
	@echo "| run | Starting Airflow standalone... | Start Airflow services |"
	@echo "| stop | Stopping all Airflow processes... | Stop safely (WSL fix) |"
	@echo "| restart | Airflow restarted with DAGs refreshed. | Full dev restart |"
	@echo "| status | Listing active DAGs and running Airflow processes... | Debug DAGs & services |"
	@echo "| refresh-dags | Touching DAG files to force reload... | When DAGs don’t reload automatically |"
	@echo "| clean-core | Cleaning Airflow logs and PIDs... | Reset stale log/PID state |"
	@echo "| clean-logs | Deleting all logs... | Free space or reset logs |"
	@echo "| clean-data | Deletes data/* (prompts confirmation) | Reset data pipeline outputs |"
	@echo "| soft-purge | Clearing logs, pycache, and refreshing DAGs... | Lightweight dev cleanup |"
	@echo "| purge-dag-runs | Deleting all DAGs and history | Full metadata wipe |"
	@echo "| purge-dag-runs-soft | Clearing DAG runs only | Clean run history |"
	@echo "| full-reset | Removing virtualenv and airflow_home... | Nuke from orbit |"