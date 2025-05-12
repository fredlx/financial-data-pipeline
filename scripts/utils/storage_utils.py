import pandas as pd
from pathlib import Path
from datetime import datetime


def _merge_and_save(path: Path, df_new: pd.DataFrame) -> pd.DataFrame:
    """
    Atomic writes
    File corruption check before overwrite
    Post-write integrity validation
    Safe skip for empty DataFrames (non trading days)
    """
    
    if df_new.empty:
        print(f"Skipping empty input for: {path}")
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        if path.stat().st_size < 8:
            print(f"Deleting corrupt file before overwrite: {path}")
            path.unlink()
            df = df_new
        else:
            df_old = pd.read_parquet(path)
            df = pd.concat([df_old, df_new])
            df = df.drop_duplicates(subset="date", keep="last")
    else:
        df = df_new

    df = df.sort_values("date")
    df = df.drop(columns=["year", "month"], errors="ignore")

    # Atomic write: write to .tmp and rename
    tmp_path = path.with_suffix(".tmp")
    df.to_parquet(tmp_path, index=False, compression="snappy")

    try:
        pd.read_parquet(tmp_path, columns=["date"])  # integrity check
    except Exception as e:
        raise RuntimeError(f"File integrity check failed for {tmp_path}: {e}")

    tmp_path.rename(path)
    print(f"Atomically wrote to {path} with {len(df)} total rows")
    return df


# v2: accepts csv.gz
def save_partition_hybrid(file_path: str, symbol: str, interval: str):
    """
    Accepts a compressed CSV file, normalizes and partitions data into Parquet files:
    - All previous years => one file per year
    - Current year => one file per month
    """
    # Load enriched data from CSV
    df_new = pd.read_csv(file_path, compression="gzip")
    
    # Normalize date and extract time components
    df_new["date"] = pd.to_datetime(df_new["date"])
    df_new["year"] = df_new["date"].dt.year
    df_new["month"] = df_new["date"].dt.month

    # Prepare paths
    base_path = Path(f"data/{symbol}/processed")
    base_filename = f"{symbol}_{interval}_processed"
    current_year = datetime.now().year

    # Partition logic
    for year in df_new["year"].unique():
        df_year = df_new[df_new["year"] == year]
        if year == current_year:
            for month in df_year["month"].unique():
                df_month = df_year[df_year["month"] == month]
                month_str = f"{year}-{month:02d}"
                path = base_path / f"{base_filename}_{month_str}.parquet"
                _merge_and_save(path, df_month)
        else:
            path = base_path / f"{base_filename}_{year}.parquet"
            _merge_and_save(path, df_year)



# v1: accepts parquet
def save_partition_hybrid_parquet(file_path: str, symbol: str, interval: str):
    """Partitions by year, except current year: monthly partitions"""
    df_new = pd.read_parquet(file_path)
    
    base_path = Path(f"data/{symbol}/processed")
    base_filename = f"{symbol}_{interval}_processed"
    
    df_new["date"] = pd.to_datetime(df_new["date"])
    df_new["year"] = df_new["date"].dt.year
    df_new["month"] = df_new["date"].dt.month

    current_year = datetime.now().year

    for year in df_new["year"].unique():
        df_year = df_new[df_new["year"] == year]
        if year == current_year:
            # partition by month
            for month in df_year["month"].unique():
                df_month = df_year[df_year["month"] == month]
                month_str = f"{year}-{month:02d}"
                path = base_path / f"{base_filename}_{month_str}.parquet"
                _merge_and_save(path, df_month)
        else:
            # partition by year
            path = base_path / f"{base_filename}_{year}.parquet"
            _merge_and_save(path, df_year)
            
            

def merge_monthly_to_yearly(symbol: str, interval: str, year: int, delete_monthly: bool = False):
    
    base_path = Path(f"data/{symbol}/processed")
    base_filename = f"{symbol}_{interval}"
    monthly_files = sorted(base_path.glob(f"*{year}-*.parquet"))

    if not monthly_files:
        raise FileNotFoundError(f"No monthly files found for {symbol} in {year}")

    all_months = []
    for file in monthly_files:
        df = pd.read_parquet(file)
        all_months.append(df)

    df_year = pd.concat(all_months)
    df_year = df_year.drop_duplicates(subset="date", keep="last").sort_values("date")

    output_path = base_path / f"{base_filename}_{year}.parquet"
    df_year.to_parquet(output_path, index=False, compression="snappy")

    print(f"Merged {len(monthly_files)} files into {output_path}")

    if delete_monthly:
        for file in monthly_files:
            file.unlink()
        print(f"Deleted {len(monthly_files)} monthly files for {year}")

    return output_path