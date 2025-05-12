from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from airflow.utils.log.logging_mixin import LoggingMixin
from datetime import datetime#, timedelta
from pathlib import Path
import pandas as pd

#from config.settings import get_symbols, get_period, get_interval

#from scripts.extract_stock_data import fetch_stock_data, clean_stock_data#, save_stock_data
#from scripts.enrich_stock_data import enrich_with_indicators
#from scripts.utils.validators import validate_time_series
#from scripts.utils.storage_utils import save_parquet#, save_monthly_parquet#safe_partition
#from scripts.utils.etl_utils import update_metadata


log = LoggingMixin().log

@dag(
    dag_id='extract_enrich_backfill',
    start_date=datetime(2025, 5, 1),
    schedule=None,
    catchup=False,
    #default_args = {
    #    "owner": "airflow",
    #    "retries": 1,
    #    "retry_delay": timedelta(minutes=1)
    #    },
    #dagrun_timeout=timedelta(minutes=5),
    tags=["stocks","backfill", "manual"]
    )

def extract_enrich_backfill_dag():

    @task
    @task
    def get_task_args():
        from config.settings import get_symbols, get_period, get_interval
        is_update = False
        symbols = get_symbols(is_update)
        period = get_period(is_update)
        interval = get_interval(is_update)
        return [
            {"symbol": s, "period": period, "interval": interval}
            for s in symbols
        ]
    
    @task
    def extract_and_validate(symbol: str, period: str, interval: str):
        
        from scripts.extract_stock_data import fetch_stock_data, clean_stock_data
        from scripts.utils.validators import validate_time_series
        from scripts.utils.etl_utils import update_metadata
        from scripts.utils.storage_utils import save_parquet
        
        # extract
        df_raw = fetch_stock_data(symbol, period, interval)
        if df_raw.empty:
            raise AirflowException(f"No data returned for {symbol} with {period=} and {interval=}")
        
        # clean
        df_clean = clean_stock_data(df_raw)

        # validate
        missing = validate_time_series(df_clean, interval, use_calendar=False, date_col="date")
        if missing:
            msg = f"Validation failed: {len(missing)} missing timestamps. Example: {missing[:5]}"
            log.warning(msg)
            #raise AirflowException(msg)
        
        # v2
        raw_path = Path(f"data/{symbol}/raw/{symbol}_{interval}")
        raw_file_path = save_parquet(df_clean, raw_path, compress=True)
        
        # update metadata
        update_metadata(df_clean["date"], symbol, interval)
        
        #return str(raw_file_path)
        return {"file_path": str(raw_file_path), "symbol": symbol, "interval": interval}
                     
    @task
    def enrich(file_path: str, symbol: str, interval: str):
        
        from scripts.enrich_stock_data import enrich_with_indicators
        from scripts.utils.storage_utils import save_parquet
        
        # Load
        df = pd.read_parquet(file_path)

        # Enrich
        df_enriched = enrich_with_indicators(df)
        if df_enriched.empty:
            raise AirflowException(f"{file_path} is empty and could not be enriched.")
        
        # v2
        enriched_path = Path(f"data/{symbol}/enriched/{symbol}_{interval}")
        enriched_file_path = save_parquet(df_enriched, enriched_path, compress=True)
        
        #return str(enriched_file_path)
        return {"file_path": str(enriched_file_path), "symbol": symbol, "interval": interval}
        
    @task
    def monthly_load(file_path: str, symbol: str, interval: str):
        
        from scripts.utils.storage_utils import save_monthly_parquet
        
        df_enriched = pd.read_parquet(file_path)
        save_monthly_parquet(df_enriched, symbol, interval, compress=True)

  
    # Task flow
    
    task_args = get_task_args()
    extracted = extract_and_validate.expand_kwargs(task_args)
    enriched = enrich.expand_kwargs(extracted)
    monthly_load.expand_kwargs(enriched)

    # for clarity
    #extracted >> enriched

dag = extract_enrich_backfill_dag()
