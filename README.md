# Extract, transfom stocks

Extraction:
- Yfinance (pip install yfinance)

Transformations:
- TA Library (pip install ta)
- pandas-market-calendars (pip install pandas-market-calendars)

Pipeline Management:
- Airflow

Save and Loading:
- Parquet + snappy
- Final: symbol / interval / year + month


Start Airflow services (in terminal):

If Terminal:
- airflow standalone

If Docker Compose:
- docker-compose up

Access the UI:
- Go to http://localhost:8080
- Login: admin / admin (default for standalone)


## 🛠 Makefile Commands

| Target | Description | When to Use |
|--------|-------------|--------------|
| init | Creating virtualenv and installing dependencies... | First time setup or after full-reset |
| check-env | Showing environment configuration... | Confirm Airflow paths and config |
| kill-examples | Removing example DAGs... | Cleanup after initial install |
| run | Starting Airflow standalone... | Start Airflow services |
| stop | Stopping all Airflow processes... | Stop safely (WSL fix) |
| restart | Airflow restarted with DAGs refreshed. | Full dev restart |
| status | Listing active DAGs and running Airflow processes... | Debug DAGs & services |
| refresh-dags | Touching DAG files to force reload... | When DAGs don’t reload automatically |
| clean-core | Cleaning Airflow logs and PIDs... | Reset stale log/PID state |
| clean-logs | Deleting all logs... | Free space or reset logs |
| clean-data | Deletes data/* (prompts confirmation) | Reset data pipeline outputs |
| soft-purge | Clearing logs, pycache, and refreshing DAGs... | Lightweight dev cleanup |
| purge-dag-runs | Deleting all DAGs and history | Full metadata wipe |
| purge-dag-runs-soft | Clearing DAG runs only | Clean run history |
| full-reset | Removing virtualenv and airflow_home... | Nuke from orbit |


# Know issues 

### WSL + Airflow + Pyarrow partition_cols
1. WSL (resource limits by default)
    - WSL2 will use all available RAM unless .wslconfig is set
    - When it runs out, the kernel kills processes with SIGKILL (your Airflow task)
2. Airflow running Python tasks inside WSL
    - Airflow tasks are independent processes, and each may load large DataFrames
    - If not carefully managed, each task can consume >1GB easily (especially on to_parquet())
3. pyarrow writing partitioned Parquet files
    - df.to_parquet(..., partition_cols=...) can trigger internal parallelism + memory usage spikes
For large DataFrames (even 500MB+), this is enough to OOM WSL without swap

Solutions: 
- stick to csv
- use parquet without partition (use only monthly folders but no Pyarrow partition_cols)
- Reduce memory load by processing only 1 year of data per task (also headaches...)


### move heavy imports and I/O operations inside functions
- yfinance, pandas_market_calendars, etc
Solution: move all imports inside function and tasks for Airflow to parse it only when they are needed

### metadata file incomplete
- A race condition: multiple tasks writing to the same JSON file (metadata.json) in parallel — and the last one to finish overwrites others.
Solutions: get its own task, or use filelock (pip install filelock), but careful with the returned dictionary. 
How to fix:
- additional dag task to return needed dictionary
- remove unnecessary key at expand_kwargs level
- or simply make task accept an unusued param


# convert Airflow project into a production-ready Docker + Airflow Compose setup

Steps:

1. Project structure
project_name/
├── dags/
│   └── yfinance_stocks_etl_backfill.py
├── scripts/
│   └── ...
├── config/
│   ├── config.ini
│   └── settings.py
├── data/  # Mounted volume
├── logs/  # Mounted volume
├── plugins/  # Optional
├── requirements.txt
├── Dockerfile  # optional
├── .env
└── docker-compose.yaml

2. requirements.txt
pip freeze > requirements.txt

3. .env file (Airflow config)
AIRFLOW_UID=50000

4. docker-compose.yaml (clean and functional)
yaml:

version: '3.8'

services:
  airflow:
    image: apache/airflow:2.8.1-python3.10
    restart: always
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: "false"
      AIRFLOW__CORE__LOAD_EXAMPLES: "false"
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: sqlite:////opt/airflow/airflow.db
      _AIRFLOW_WWW_USER_USERNAME: airflow
      _AIRFLOW_WWW_USER_PASSWORD: airflow
    env_file: .env
    volumes:
      - ./dags:/opt/airflow/dags
      - ./scripts:/opt/airflow/scripts
      - ./config:/opt/airflow/config
      - ./data:/opt/airflow/data
      - ./logs:/opt/airflow/logs
      - ./requirements.txt:/requirements.txt
    command: >
      bash -c "
        pip install -r /requirements.txt &&
        airflow db upgrade &&
        airflow users create --username airflow --password airflow --firstname admin --lastname user --role Admin --email admin@example.com &&
        airflow webserver"
    ports:
      - "8080:8080"

  airflow-scheduler:
    image: apache/airflow:2.8.1-python3.10
    restart: always
    depends_on:
      - airflow
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
    volumes:
      - ./dags:/opt/airflow/dags
      - ./scripts:/opt/airflow/scripts
      - ./config:/opt/airflow/config
      - ./data:/opt/airflow/data
      - ./logs:/opt/airflow/logs
      - ./requirements.txt:/requirements.txt
    command: >
      bash -c "
        pip install -r /requirements.txt &&
        airflow db upgrade &&
        airflow scheduler"

5. Run
```bash
docker compose up --build
```

6. Access Airflow UI
Go to: http://localhost:8080
Login: airflow / airflow   # (as per yaml file)

7. Improvements:

- Use Postgres instead of SQLite: Replace connection string and add a postgres service in docker-compose
    - Add PostgreSQL service to docker-compose.yaml
        postgres:
            image: postgres:15
            environment:
                POSTGRES_USER: airflow
                POSTGRES_PASSWORD: airflow
                POSTGRES_DB: airflow
            volumes:
                - postgres-db-volume:/var/lib/postgresql/data
            ports:
                - "5432:5432"

    - Configure Airflow to use PostgreSQL
        environment:
            AIRFLOW__CORE__EXECUTOR: CeleryExecutor
            AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
            AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
            AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres:5432/airflow

    - Add required Python packages to requirements.txt: psycopg2-binary
    - Add volume for PostgreSQL data (bottom of file):
        volumes:
            postgres-db-volume:

    - Initialize the database
        docker compose up airflow-init
        (or) airflow db upgrade

- Add volume-based metadata JSON: Mount ./data and persist it (mapping a host folder (like ./data) into the Docker container)
    - volumes:
        - ./data:/opt/airflow/data
- Use CeleryExecutor for scale: Add Redis + Celery workers in docker-compose.yaml
    - Airflow’s default LocalExecutor runs all tasks sequentially or in threads on the same machine. If horizontal scalability (e.g. run tasks in parallel across machines or multiple containers), you need:
        - CeleryExecutor — enables distributed task execution. Celery allows task parallelism per symbol — e.g. run 20 extract_and_validate tasks at once.
        - Redis (or RabbitMQ) — message broker to queue and distribute tasks (task broker). Redis is only the broker — Airflow stores results in the result backend.
            redis:
                image: redis:7
                ports:
                    - "6379:6379"
        - Celery workers — process tasks in parallel
            airflow-worker:
                image: apache/airflow:2.8.1-python3.10
                depends_on:
                    - redis
                    - airflow
                environment:
                    AIRFLOW__CORE__EXECUTOR: CeleryExecutor
                    AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
                    AIRFLOW__CELERY__RESULT_BACKEND: db+sqlite:////opt/airflow/airflow.db
                volumes:
                    - ./dags:/opt/airflow/dags
                    - ./scripts:/opt/airflow/scripts
                    - ./config:/opt/airflow/config
                    - ./data:/opt/airflow/data
                    - ./logs:/opt/airflow/logs
                    - ./requirements.txt:/requirements.txt
                command: >
                    bash -c "
                    pip install -r /requirements.txt &&
                    airflow celery worker"

            environment:
                AIRFLOW__CORE__EXECUTOR: CeleryExecutor
                AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
                AIRFLOW__CELERY__RESULT_BACKEND: db+sqlite:////opt/airflow/airflow.db  (change to postgres)

- Refactor Makefile for prod: Automate DAG trigger, cleanup, volume pruning, etc.
