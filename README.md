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

