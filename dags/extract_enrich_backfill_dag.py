from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from datetime import datetime, timedelta
from config.settings import get_symbols, get_period, get_interval
from scripts.extract_backfill import fetch_stock_data, clean_stock_data, save_stock_data
#from scripts.transform_stock_data import transform_stock_data
from scripts.validators import validate_time_series
from scripts.etl_utils import read_auto_file
from scripts.enrich_data import enrich_with_indicators, save_to_file

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
    dag_id='extract_enrich_backfill',
    start_date=datetime(2025, 5, 1),
    schedule=None,
    catchup=False,
    #default_args=default_args,
    tags=["backfill", "manual"],
    )

def extract_enrich_backfill_dag():

    @task
    def extract_and_validate(symbol: str, period: str, interval: str):
        
        # extract
        df_raw = fetch_stock_data(symbol, period, interval)
        if df_raw.empty:
            raise AirflowException(f"No data returned for {symbol} with {period=} and {interval=}")
        
        # clean
        df_clean = clean_stock_data(df_raw)

        # validate
        missing = validate_time_series(df_clean, date_col="date", freq="D", use_calendar=False)
        if missing: # fail fast
            raise AirflowException(
                f"Validation failed: {len(missing)} missing timestamps. Example: {missing[:5]}")
        
        # save  
        file_path = save_stock_data(df_clean, symbol, interval, compress=False)
        return file_path
                    
    @task
    def enrich(file_path: str, symbol: str, interval: str):
        
        # Load
        df = read_auto_file(file_path)
        if df.empty:
            raise AirflowException(f"{file_path} is empty and could not be loaded.")
        
        # Enrich
        df_ta = enrich_with_indicators(df)
        if df_ta.empty:
            raise AirflowException(f"{file_path} is empty and could not be enriched.")
        
        # Save
        file_path = save_to_file(
            df_ta, 
            symbol, 
            interval, 
            data_folder="processed", 
            file_format="parquet", 
            compress=True
            )
        
        return file_path
        
    # Dynamic task mapping
    
    # Pre-build shared task params
    task_args = [
        {"symbol": s, "period": period, "interval": interval}
        for s in symbols]

    # Task flow
    extracted = extract_and_validate.expand_kwargs(task_args)
    enriched = enrich.expand(
        file_path=extracted,
        symbol=[d["symbol"] for d in task_args],
        interval=[d["interval"] for d in task_args]
        )

    # for clarity
    extracted >> enriched

dag = extract_enrich_backfill_dag()
