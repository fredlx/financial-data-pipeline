# Airflow project Makefile for WSL + Python venv setup

AIRFLOW_DIR := $(CURDIR)/airflow_home
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: init sync run stop clean

init:
	@echo "Creating virtualenv and installing requirements..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install apache-airflow yfinance pandas pyarrow
	AIRFLOW_HOME=$(AIRFLOW_DIR) $(PYTHON) -m airflow db init
	mkdir -p $(AIRFLOW_DIR)/dags
	cp -r dags/* $(AIRFLOW_DIR)/dags/

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
	# Kill gunicorns that listen on 8793/8794
	lsof -ti:8793 | xargs -r kill -9 || true
	lsof -ti:8794 | xargs -r kill -9 || true
	# WSL-safe
	#ss -ltnp | grep 8793 | awk -F 'pid=' '{print $2}' | cut -d, -f1 | xargs -r kill -9 || true
	#ss -ltnp | grep 8794 | awk -F 'pid=' '{print $2}' | cut -d, -f1 | xargs -r kill -9 || true

restart:
	- make stop
	sleep 2
	make run

purge: stop
	@echo "Removing stale DAGs and caches..."
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -rf $(AIRFLOW_DIR)/dags/*

clean: stop
	@echo "Cleaning environment..."
	rm -rf $(AIRFLOW_DIR) $(VENV)