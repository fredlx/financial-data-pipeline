import pandas as pd
from pathlib import Path
from datetime import datetime
import shutil
import hashlib

from config.constants import DEFAULT_HASH_ALGO

import logging
log = logging.getLogger("airflow.task")


def save_parquet(df, base_file_path, compress, hash_algo=DEFAULT_HASH_ALGO):
    
    compression = "snappy" if compress else None
    filename_ext = ".parquet"
    
    base_file_path.parent.mkdir(parents=True, exist_ok=True)
    output_path = Path(base_file_path).with_suffix(filename_ext)
    
    df.to_parquet(output_path, index=False, engine="pyarrow", compression=compression)
    
    log_file_summary(output_path, df_len=len(df), hash_algo=hash_algo)
    
    return output_path



def load_parquet(file_path):
    
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File {file_path} not found")
        
    df = pd.read_parquet(file_path)
        
    if df.empty:
        raise ValueError(f"No raw data available to enrich - {file_path}")
    
    return df


def save_csv(df, base_file_path, compress, hash_algo=DEFAULT_HASH_ALGO):
    
    compression = "gzip" if compress else None
    filename_ext = ".csv.gz" if compress else ".csv"
    
    base_file_path.parent.mkdir(parents=True, exist_ok=True)
    output_path = Path(base_file_path).with_suffix(filename_ext)

    df.to_csv(output_path, index=False, compression=compression)
    
    log_file_summary(output_path, df_len=len(df), hash_algo=hash_algo)
    
    return output_path


def save_monthly_parquet(df, symbol: str, interval: str, compress: bool, hash_algo: str =DEFAULT_HASH_ALGO):
    """
    WSL-airflow friendly
    Saves one Parquet file per (year, month) in the format:
    {symbol}_{interval}_{yyyy-mm}.parquet
    """

    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    base_path = Path(f"data/{symbol}/{interval}")
    
    compression = "snappy" if compress else None

    for (year, month), group in df.groupby(["year", "month"]):
        base_path.mkdir(parents=True, exist_ok=True)
        filename = f"{symbol}_{interval}_{year}-{month:02d}.parquet"
        
        full_path = base_path / filename
        group.drop(columns=["year", "month"]).to_parquet(full_path, index=False, engine="pyarrow", compression=compression)

        # log
        log_file_summary(full_path, df_len=len(group), hash_algo=hash_algo)


def log_file_summary(file_path: Path, df_len: int = None, hash_algo: str = "sha256"):
    """
    Logs file size, optional row count, and optional file hash.
    
    Args:
        file_path (Path): Path to the file to log.
        df_len (int, optional): Number of rows in DataFrame (if known).
        hash_algo (str, optional): 'sha256', 'md5', or None.
    """
    size_kb = file_path.stat().st_size / 1024

    hash = None
    if hash_algo:
        algo = hash_algo.lower()
        if algo == "sha256":
            hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
        elif algo == "md5":
            hash = hashlib.md5(file_path.read_bytes()).hexdigest()

    message = f"Saved {file_path} ({size_kb:.1f} KB"
    if df_len is not None:
        message += f", {df_len} rows"
    if hash:
        message += f", {hash_algo.upper()}: {hash}"
    message += ")"

    log.info(message)






# ------------- PARTITION ---------------
# too much headaches with this WSL, Airflow, Pyarrow setup

# (NOTUSED)
def safe_partition(input_path, output_base_path):
    """
    Reduce memory load by processing only 1 year of data per task
    Avoids memory spikes, write collisions, or race conditions
    PyArrow should handle small batch writes safely in WSL without triggering SIGKILL
    
    """
    
    df = pd.read_parquet(input_path)
    
    # Normalize date and extract year, month
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    output_base_path.mkdir(parents=True, exist_ok=True)

    # v1: for loop + unique and mask (less efficient)
    #for year in df['year'].unique():
    #    df_year = df[df['year'] == year]
    
    # v2: for and groupby
    for year, df_year in df.groupby('year'):
        
        # Write to a year-specific temp folder to keep writes isolated
        year_path = output_base_path / f"tmp_write_{year}"
        year_path.mkdir(parents=True, exist_ok=True)
        
        df_year.to_parquet(
            year_path,
            partition_cols=["year", "month"],
            engine="pyarrow",
            compression="snappy",
            index=False
        )
        
        # Move results to final folder after successful write
        for subdir in year_path.glob("year=*"):
                final_dest = output_base_path / subdir.name
                if final_dest.exists():
                    # (TODO) skip if exists? Now, it overwrites
                    for file in subdir.glob("*.parquet"):
                        file.replace(final_dest / file.name)
                    #shutil.rmtree(subdir)
                else:
                    subdir.replace(final_dest)
            
        # Remove temp folder
        #shutil.rmtree(year_path)
        
# (NOTUSED)        
def cleanup_temps(symbol: str, interval: str):
    """Clean up temp folders from partition operation"""
    
    base_path = Path(f"data/{symbol}/{interval}")
    for tmp_dir in base_path.glob("tmp_write_*"):
        try:
            shutil.rmtree(tmp_dir)
            print(f"Deleted temp folder: {tmp_dir}")
        except Exception as e:
            print(f"Failed to delete {tmp_dir}: {e}")