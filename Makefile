# Airflow project Makefile for WSL + Python venv setup

AIRFLOW_DIR := $(CURDIR)/airflow_home
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

export AIRFLOW_HOME := $(AIRFLOW_DIR)
export AIRFLOW__CORE__LOAD_EXAMPLES=False  # no examples

.PHONY: init sync run stop clean clean-data clean-logs refresh soft-purge full-reset check-env kill-examples purge-dag-runs clean-history

init:
	@echo "Creating virtualenv and installing requirements..."
	@if [ ! -d "$(VENV)" ]; then \
		python3 -m venv $(VENV); \
	fi
	$(PIP) install --upgrade pip
	$(PIP) install apache-airflow yfinance ta pandas pyarrow pandas-market-calendars
	$(PYTHON) -m airflow db migrate
	mkdir -p $(AIRFLOW_HOME)/dags
	mkdir -p $(AIRFLOW_HOME)/logs
	cp -r dags/* $(AIRFLOW_HOME)/dags/   # sync dags

check-env:
	@echo "VENV         = $(VENV)"
	@echo "PYTHON       = $(PYTHON)"
	@echo "PIP          = $(PIP)"
	@echo "AIRFLOW_HOME = $(AIRFLOW_HOME)"
	@$(PYTHON) -m airflow info

kill-examples:
	@echo "Attempting to remove example DAGs..."
	@if $(PYTHON) -m airflow dags list | grep -q example; then \
		for dag in $$($(PYTHON) -m airflow dags list | grep example | awk '{print $$1}'); do \
			echo "Deleting $$dag..."; \
			$(PYTHON) -m airflow dags delete --yes $$dag || true; \
		done \
	else \
		echo "No example DAGs found."; \
	fi

sync:
	cp -r dags/* $(AIRFLOW_DIR)/dags/

run: sync
	@echo "Starting Airflow standalone (webserver + scheduler)..."
	PYTHONPATH=$(CURDIR) AIRFLOW_HOME=$(AIRFLOW_DIR) $(PYTHON) -m airflow standalone
	

clean-data:
	@read -p "This will delete all contents in data/. Continue? [y/N] " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "Deleting data/* ..."; \
		rm -rf data/*; \
	else \
		echo "Cancelled."; \
	fi

clean-logs:
	@echo "Cleaning all Airflow logs..."
	@rm -rf $(AIRFLOW_DIR)/logs/*
	@echo "All Airflow logs deleted from: $(AIRFLOW_DIR)/logs"

purge-dag-runs:
	@echo "Purging all DAG runs and task instances from metadata DB..."
	@$(PYTHON) -m airflow dags delete extract_enrich_backfill --yes || true
	@echo "Reimporting DAG by refreshing file timestamps..."
	@find $(AIRFLOW_DIR)/dags -name "*.py" -exec touch {} +

clean-history: clean-logs purge-dag-runs
	@echo "Cleanning logs/ folder and Purging DAG runs and task instances from metadata DB..."



refresh:
	find dags -name "*.py" -exec touch {} +

soft-purge: stop
	@echo "Soft purge: clearing logs, cache, and refreshing DAGs..."
	find . -type d -name "__pycache__" -exec rm -r {} +
	find dags -name "*.pyc" -delete
	rm -rf $(AIRFLOW_HOME)/logs/*
	find dags -name "*.py" -exec touch {} +

#full-reset: stop
full-reset:
	@echo "Full reset: removing environment and Airflow home at: $(AIRFLOW_DIR)"
	rm -rf $(AIRFLOW_DIR) $(VENV)


stop:
	@echo "Stopping all Airflow processes safely (WSL workaround)..."
	@bash -c 'sleep 0.1 && pkill -f "airflow webserver"' &
	@bash -c 'sleep 0.1 && pkill -f "airflow scheduler"' &
	@bash -c 'sleep 0.1 && pkill -f "airflow triggerer"' &
	@bash -c 'sleep 0.1 && lsof -ti:8793 | xargs -r kill -9 || true' &
	@bash -c 'sleep 0.1 && lsof -ti:8794 | xargs -r kill -9 || true' &
	@sleep 0.5  # give subprocesses time to act

clean:
	@echo "Cleaning up Airflow logs and PIDs..."
	@rm -rf airflow/logs/*
	@rm -f airflow/airflow-webserver.pid
	@rm -f airflow/airflow-scheduler.pid

#start:
#	@echo "Starting Airflow processes..."
#	@airflow db upgrade
#	@airflow scheduler > logs/scheduler.log 2>&1 &
#	@airflow webserver --port 8793 > logs/webserver.log 2>&1 &

restart: stop clean run
	@echo "Airflow restarted."