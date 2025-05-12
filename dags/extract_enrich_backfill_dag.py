from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from airflow.utils.log.logging_mixin import LoggingMixin
from datetime import datetime, timedelta
from config.settings import get_symbols, get_period, get_interval

from scripts.extract_stock_data import fetch_stock_data, clean_stock_data, save_stock_data
from scripts.enrich_stock_data import enrich_with_indicators, save_to_file

from scripts.utils.validators import validate_time_series
from scripts.utils.etl_utils import read_auto_file
from scripts.utils.storage_utils import save_partition_hybrid

from pathlib import Path
import pandas as pd

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
    tags=["stocks","backfill", "manual"]
    )

def extract_enrich_backfill_dag():
    
    is_update = False  # for backfill
    symbols = get_symbols(is_update)
    period = get_period(is_update)
    interval = get_interval(is_update)
    
    @task
    def extract_and_validate(symbol: str, period: str, interval: str):
        
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
        
        # save temp raw
        raw_path = Path(f"data/{symbol}/raw/{symbol}_{interval}_full.parquet")
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        df_clean.to_parquet(raw_path, index=False, engine="pyarrow")
        
        return str(raw_path)
        
                    
    @task
    def enrich(raw_path: str, symbol: str, interval: str):
        
        # Load
        df = pd.read_parquet(raw_path)

        # Enrich
        df_ta = enrich_with_indicators(df)
        if df_ta.empty:
            raise AirflowException(f"{raw_path} is empty and could not be enriched.")
        
        # save temp processed
        enriched_path = Path(f"data/{symbol}/enriched/{symbol}_{interval}_full.parquet")
        enriched_path.parent.mkdir(parents=True, exist_ok=True)
        df_ta.to_parquet(enriched_path, index=False, engine="pyarrow", compression="snappy")
        
        return str(enriched_path)
        
    
    @task
    def save_partition(enriched_path: str, symbol: str, interval: str):
        
        df = pd.read_parquet(enriched_path)
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        current_year = datetime.now().year

        base_path = Path(f"data/{symbol}/final/{symbol}_{interval}")
        
        for year in df['year'].unique():
            df_year = df[df['year'] == year]
            if year == current_year:
                # monthly partitions
                for month in df_year['month'].unique():
                    df_month = df_year[df_year['month'] == month]
                    part_path = base_path / f"year={year}/month={month:02d}/{symbol}_{interval}_{year}-{month:02d}.parquet"
                    part_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    df_month.drop(columns=['year', 'month']).to_parquet(part_path, index=False, engine="pyarrow" ,compression="snappy")
            else:
                # yearly
                part_path = base_path / f"year={year}/{symbol}_{interval}_{year}.parquet"
                part_path.parent.mkdir(parents=True, exist_ok=True)
                
                df_year.drop(columns=['year', 'month']).to_parquet(part_path, index=False, engine="pyarrow", compression="snappy")
        
        
    # Dynamic task mapping
    # Pre-build shared task params
    task_args = [
        {"symbol": s, "period": period, "interval": interval}
        for s in symbols]

    # Task flow
    extracted = extract_and_validate.expand_kwargs(task_args)
    enriched = enrich.expand(
        raw_path=extracted,
        symbol=[d["symbol"] for d in task_args],
        interval=[d["interval"] for d in task_args]
        )
    partitioned = save_partition.expand(
        enriched_path=enriched,
        symbol=[d["symbol"] for d in task_args],
        interval=[d["interval"] for d in task_args]
        )

    # for clarity
    extracted >> enriched >> partitioned

dag = extract_enrich_backfill_dag()
