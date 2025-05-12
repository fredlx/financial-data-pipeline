# Extract, transfom stocks

Extraction:
- Yfinance (pip install yfinance)

Transformations:
- TA Library (pip install ta)
- pandas-market-calendars (pip install pandas-market-calendars)

Pipeline Management:
- Airflow

Loading:
- CSV, CSV + gzip
- Parquet, Parquet + snappy, Parquet + gzip (pip install pyarrow)


Start Airflow services (in terminal):

If Terminal:
- airflow standalone

If Docker Compose:
- docker-compose up

Access the UI:
- Go to http://localhost:8080
- Login: admin / admin (default for standalone)


### Makefile commands:
- make init           # sets up airflow with new or existing .venv
- make check-env
- make kill-examples  # cleans startup examples (refactored in init, not needed anymore)
- make sync           # syncs dags folder with airflow_home
- make run            # working Airflow environment (UI + scheduler)
- make stop           # stops airflow processes running in the background
- make clean-data     # clears data folder
- make refresh        # refresh dags folder
- soft-purge          # clears logs, cache, syncs dags folder
- make clean          # delete venv (hard-reset)

Workflow:
- make run     # starts clean
- Ctrl+C       # stops normally (foreground)
- make stop    # emergency kill if anything lingers
- make refresh
- make run


# Know issues 

(WSL + Airflow + Pyarrow)
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
- parquet without partition (use only monthly folders but no Pyarrow partition_cols)
- Reduce memory load by processing only 1 year of data per task (also headaches...)


# move heavy imports and I/O operations inside functions
- yfinance
- 