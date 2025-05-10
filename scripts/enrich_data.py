import pandas as pd
from pathlib import Path
from scripts.ta_indicators import daily_log_return, get_all_indicators
from scripts.etl_utils import read_auto_file


# (REMOVE) use read_auto_file directly
def load_file(file_path):
    df = read_auto_file(file_path)
    return df


def enrich_with_indicators(df):
    
    # Normalize
    df['date'] = pd.to_datetime(df['date'])
    num_cols = ['open', 'high', 'low', 'close', 'volume']
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
    
    # Sort
    df = df.sort_values('date')
    
    # Daily returns
    df['daily_return'] = df['close'].pct_change().fillna(0)
    df['daily_log_return'] = daily_log_return(df['close'])
    
    # Compute ta_indicators (returns new df)
    df_ta = get_all_indicators(df)
    
    return df_ta


def save_to_file(df, symbol, interval, data_folder="processed", file_format="parquet", compress=True):
    
    symbol = symbol.upper()
    
    # output path
    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / "data" / symbol / data_folder
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f'{symbol}_{interval}_{data_folder}' # no ext
    
    if file_format == "csv":
        # CSV + gzip: slow I/O, higher compression ratio
        full_path = output_path.with_suffix(".csv.gz") if compress else output_path.with_suffix(".csv")
        df.to_csv(
            full_path,
            index=False,
            compression="gzip" if compress else None
            )
        
    elif file_format == "parquet":
        # Parquet + snappy: faster I/O, larger file
        # Parquet + gzip: slower I/O, smallest file
        full_path = output_path.with_suffix(".parquet")
        df.to_parquet(
            full_path,
            index=False,
            compression="snappy" if compress else None, # gzip
            )  
    else:
        raise ValueError(f"Unsupported file format: {file_format}")
    
    return str(full_path)  # no Path, for airflow