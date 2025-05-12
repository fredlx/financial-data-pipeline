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


# Notes on data structure
- Extracts raw to csv
- Load csv, enrich data and save to csv.gz (compressed)
- Loads csv.gz and partitions by year/month to parquet