from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

import logging
log = logging.getLogger("airflow.task")

@dag(
    dag_id='stocks_etl_backfill',
    start_date=datetime(2025, 5, 1),
    schedule=None,
    catchup=False,
    default_args = {
        "owner": "airflow",
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
        #"email_on_failure": True,
        #"email": ["alerts@yourdomain.com"]
        },
    #dagrun_timeout=timedelta(minutes=5),
    tags=["stocks","backfill", "manual"]
    )


def stocks_etl_backfill_dag():
    
    @task
    def get_task_args():
        
        from config.settings import get_symbols, get_period, get_interval
        
        log.info("Loading symbols...")
        
        is_update = False
        symbols = get_symbols(is_update)
        period = get_period(is_update)
        interval = get_interval(is_update)
        
        task_args = [
            {"symbol": s, "period": period, "interval": interval}
            for s in symbols
            ]
        
        if not task_args:
            log.error(f"No symbols found. Period={period}, Interval={interval}")
            raise AirflowException("No task args available from config")
        
        return task_args
    
    @task
    def extract_and_validate(symbol: str, period: str, interval: str):
        
        from scripts.extract_stock_data import fetch_stock_data, clean_stock_data
        from scripts.utils.validators import validate_time_series
        from scripts.utils.etl_utils import update_metadata
        from scripts.utils.storage_utils import save_parquet
        from config.settings import get_metadata_file
        
        # extract
        log.info(f"Fetching {symbol} for period {period} with interval {interval}...")
        df_raw = fetch_stock_data(symbol, period, interval)

        # clean
        log.info("Cleaning data...")
        df_clean = clean_stock_data(df_raw)

        # validate
        log.info("Validating data...")
        missing = validate_time_series(df_clean, interval, use_calendar=False, date_col="date")
        if missing:
            msg = f"Gaps detected: {len(missing)} missing timestamps. Example: {missing[:5]}"
            log.warning(msg)
        
        # save temp raw
        log.info("Saving raw data...")
        raw_path = Path(f"data/{symbol}/raw/{symbol}_{interval}")
        raw_file_path = save_parquet(df_clean, raw_path, compress=True)
        
        # update metadata
        meta_file_path = get_metadata_file()
        update_metadata(df_clean["date"], symbol, interval, meta_file_path)
        
        return {"file_path": str(raw_file_path), "symbol": symbol, "interval": interval}
                     
    @task
    def enrich(file_path: str, symbol: str, interval: str):
        
        from scripts.enrich_stock_data import enrich_with_indicators
        from scripts.utils.storage_utils import save_parquet
        
        # Load
        log.info(f"Loading file {file_path}...")
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File {file_path} not found")
        
        df = pd.read_parquet(file_path)
        
        if df.empty:
            raise ValueError(f"No raw data available to enrich - {file_path}")

        # Enrich
        log.info("Enriching data with technical indicators...")
        df_enriched = enrich_with_indicators(df)
        
        # (TODO) missing some validation (number columns)
        
        # save temp enriched
        log.info("Saving enriched data...")
        enriched_path = Path(f"data/{symbol}/enriched/{symbol}_{interval}")
        enriched_file_path = save_parquet(df_enriched, enriched_path, compress=True)
        
        return {"file_path": str(enriched_file_path), "symbol": symbol, "interval": interval}
        
    @task
    def monthly_load(file_path: str, symbol: str, interval: str):
        
        from scripts.utils.storage_utils import save_monthly_parquet
        
        log.info("Partitioning by year-month...")
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File {file_path} not found")
        
        df_enriched = pd.read_parquet(file_path)
        
        if df_enriched.empty:
            raise ValueError(f"No enriched data available - {file_path}")
        
        save_monthly_parquet(df_enriched, symbol, interval, compress=True)

  
    # Task flow
    
    task_args = get_task_args()
    extracted = extract_and_validate.expand_kwargs(task_args)
    enriched = enrich.expand_kwargs(extracted)
    monthly_load.expand_kwargs(enriched)

    # for clarity
    #extracted >> enriched

dag = stocks_etl_backfill_dag()
