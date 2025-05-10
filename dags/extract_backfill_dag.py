from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from datetime import datetime, timedelta
from config.settings import get_symbols, get_period, get_interval

from scripts.extract_backfill import fetch_stock_data, clean_stock_data, save_stock_data
from scripts.transform_stock_data import transform_stock_data
from scripts.validators import validate_time_series

is_update = False  # for backfill
symbols = get_symbols(is_update)
period = get_period(is_update)
interval = get_interval(is_update)

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    }

@dag(
    dag_id='extract_backfill_manual',
    start_date=datetime(2025, 5, 1),
    schedule=None,
    catchup=False,
    #default_args=default_args,
    tags=["backfill", "manual"],
    )

def extract_backfill_dag():

    @task
    def extract(symbol: str, period: str, interval: str):
        return fetch_stock_data(symbol, period, interval)
    
    @task
    def clean(raw):
        return clean_stock_data(raw)
    
    @task   
    def validate_and_save(df, symbol, interval, compress=False, date_col='date', freq='D', use_calendar=False):
        missing = validate_time_series(df, date_col, freq, use_calendar)
        if missing:
            raise AirflowException(
                f"Validation failed: {len(missing)} missing timestamps. Example: {missing[:5]}")
            
        save_stock_data(df, symbol, interval, compress)
        return df
                    
    @task
    def transform(symbol: str, interval : str):
        transform_stock_data(symbol, interval)


    # Dynamic task mapping
    # Pre-build shared task params
    task_args = [
        {"symbol": s, "period": period, "interval": interval}
        for s in symbols
    ]

    # Task flow
    extracted = extract.expand_kwargs(task_args)
    cleaned = clean.expand(raw=extracted)
    validated = validate_and_save.expand_kwargs([
        {**args, "df": df} for args, df in zip(task_args, cleaned)
    ])
    transformed = transform.expand_kwargs(task_args)

    # all other tasks are linked already
    validated >> transformed

dag = extract_backfill_dag()
