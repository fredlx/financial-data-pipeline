from airflow.decorators import dag, task
from datetime import datetime, timedelta
from scripts.fetch_stock_data import fetch_stock_data
from scripts.transform_stock_data import transform_stock_data
from config.settings import get_symbols, get_period, get_interval

# For backfills: manual trigger, no auto-schedulling

is_update = False
symbols = get_symbols(is_update)
period = get_period(is_update)
interval = get_interval(is_update)

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

@dag(
    dag_id='extract_enrich_backfill',
    start_date=datetime(2025, 5, 1),
    schedule=None,
    catchup=False,
    #default_args=default_args,
    tags=["backfill", "manual"],
    )

def extract_transform_dag():

    @task
    def extract(symbol: str, period: str, interval: str):
        fetch_stock_data(symbol, period, interval)

    @task
    def transform(symbol: str, interval : str):
        transform_stock_data(symbol, interval)

    extracted = extract.expand_kwargs([
        {"symbol": s, "period": period, "interval": interval} for s in symbols
        ])
    transformed = transform.expand_kwargs([
        {"symbol": s, "interval": interval} for s in symbols
        ])

    extracted >> transformed

dag = extract_transform_dag()