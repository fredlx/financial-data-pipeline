# Airflow project Makefile for WSL + Python venv setup

AIRFLOW_DIR := $(CURDIR)/airflow_home
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

export AIRFLOW_HOME := $(AIRFLOW_DIR)
export AIRFLOW__CORE__LOAD_EXAMPLES=False  # no examples

.PHONY: init sync run stop clean

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

stop:
	@echo "Stopping all Airflow processes..."
	#pkill -f "airflow" || true
	pkill -f "airflow webserver" || true
	pkill -f "airflow scheduler" || true
	pkill -f "airflow triggerer" || true
	
	# Option 1: Kill gunicorns that listen on 8793/8794
	lsof -ti:8793 | xargs -r kill -9 || true
	lsof -ti:8794 | xargs -r kill -9 || true
	
	# Option 2: for windows WSL-safe
	#ss -ltnp | grep 8793 | awk -F 'pid=' '{print $2}' | cut -d, -f1 | xargs -r kill -9 || true
	#ss -ltnp | grep 8794 | awk -F 'pid=' '{print $2}' | cut -d, -f1 | xargs -r kill -9 || true

clean-data:
	@read -p "This will delete all contents in data/. Continue? [y/N] " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "🧹 Deleting data/* ..."; \
		rm -rf data/*; \
	else \
		echo "Cancelled."; \
	fi

refresh:
	find dags -name "*.py" -exec touch {} +

soft-purge: stop
	@echo "Soft purge: clearing logs, cache, and refreshing DAGs..."
	find . -type d -name "__pycache__" -exec rm -r {} +
	find dags -name "*.pyc" -delete
	rm -rf $(AIRFLOW_HOME)/logs/*
	touch dags/extract_enrich_backfill_dag.py

#full-reset: stop
full-reset:
	@echo "Full reset: removing environment and Airflow home at: $(AIRFLOW_DIR)"
	rm -rf $(AIRFLOW_DIR) $(VENV)