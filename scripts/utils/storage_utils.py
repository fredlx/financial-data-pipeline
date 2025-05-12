import pandas as pd
from pathlib import Path
from datetime import datetime
import shutil


def save_parquet(df, base_file_path, compress):
    
    compression = "snappy" if compress else None
    filename_ext = ".parquet"
    
    base_file_path.parent.mkdir(parents=True, exist_ok=True)
    output_path = Path(base_file_path).with_suffix(filename_ext)
    
    df.to_parquet(output_path, index=False, engine="pyarrow", compression=compression)
    
    return output_path


def save_csv(df, base_file_path, compress):
    
    compression = "gzip" if compress else None
    filename_ext = ".csv.gz" if compress else ".csv"
    
    base_file_path.parent.mkdir(parents=True, exist_ok=True)
    output_path = Path(base_file_path).with_suffix(filename_ext)

    df.to_csv(output_path, index=False, compression=compression)
    
    return output_path


def save_monthly_parquet(df, symbol: str, interval: str, compress: bool):
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




# ------------- PARTITION ---------------
# too much headaches with this WSL, Airflow, Pyarrow setup

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
        
        
def cleanup_temps(symbol: str, interval: str):
    """Clean up temp folders from partition operation"""
    
    base_path = Path(f"data/{symbol}/{interval}")
    for tmp_dir in base_path.glob("tmp_write_*"):
        try:
            shutil.rmtree(tmp_dir)
            print(f"Deleted temp folder: {tmp_dir}")
        except Exception as e:
            print(f"Failed to delete {tmp_dir}: {e}")