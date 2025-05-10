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


### Makefile:
- make init       # sets up airflow with your existing .venv
- make airflow    # starts the web UI
- make start      # runs the scheduler
- make run        # working Airflow environment
- make stop       # stops airflow processes running in the background
- make clean      # delete venv

Workflow:
- make run     # starts clean
- Ctrl+C       # stops normally (foreground)
- make stop    # emergency kill if anything lingers