#import importlib
#import config.settings
#importlib.reload(config.settings)

from airflow.decorators import dag, task
from datetime import datetime, timedelta
from scripts.etl_utils import extract_data, enrich_data, merge_and_save

from config.settings import get_symbols, get_period, get_interval

# For backfills: manual trigger, no auto-schedulling

is_update = True
symbols = get_symbols(is_update)
period = get_period(is_update)
interval = get_interval(is_update)

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

@dag(
    dag_id="daily_market_update",
    start_date=datetime(2025, 5, 7),
    schedule="@daily",
    catchup=False,
    #default_args=default_args,
    tags=["update", "daily"],
)

def daily_market_update_dag():

    @task
    def extract(symbol: str):
        extract_data(symbol)

    @task
    def enrich(symbol: str):
        enrich_data(symbol)

    @task
    def merge(symbol: str):
        merge_and_save(symbol)

    for symbol in symbols:
        raw = extract(symbol)
        enriched = enrich(symbol)
        final = merge(symbol)

        raw >> enriched >> final

dag = daily_market_update_dag()