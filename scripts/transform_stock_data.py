import pandas as pd
from pathlib import Path
from scripts.ta_indicators import daily_log_return, get_all_indicators

import importlib
import scripts.etl_utils
importlib.reload(scripts.etl_utils)

from scripts.etl_utils import read_auto_file

# (DONE) working
# (TODO) logging, compress logic, 
def transform_stock_data(symbol, interval, **kwargs):
    
    symbol = symbol.upper()
    
    # load raw
    project_root = Path(__file__).resolve().parents[1]
    input_dir = project_root / "data" / symbol / "raw"
    input_path = input_dir / f"{symbol}_{interval}_raw.csv"
    
    if not input_path.exists():
        input_path = input_dir / f"{symbol}_{interval}_raw.csv.gz"

    df = read_auto_file(input_path)  
    if df.empty:
        raise ValueError("raw df is empty")
    
    # Transform
    df['date'] = pd.to_datetime(df['date'])
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df = df.sort_values('date')
    
    # daily returns
    df['daily_return'] = df['close'].pct_change().fillna(0)
    
    # daily log returns
    df['daily_log_return'] = daily_log_return(df['close'])
    
    # compute ta_indicators (returns new df)
    df_ta = get_all_indicators(df)
    if df.empty:
        raise ValueError("df_ta is empty")
    
    # output path
    output_dir = project_root / "data" / symbol / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f'{symbol}_{interval}_processed'
    
    compress = True
    # CSV + gzip → higher compression ratio, slow I/O
    df_ta.to_csv(
        output_path.with_suffix(".csv.gz") if compress else output_path.with_suffix(".csv"),
        index=False,
        compression="gzip" if compress else None
        )
    
    # Parquet + snappy → faster I/O, larger file, Parquet + gzip → slower I/O, smallest file
    df_ta.to_parquet(
        output_path.with_suffix(".parquet"),
        index=False,
        compression="snappy" if compress else None, # gzip
        )
    
    print(f"[TRANSFORM] {symbol}: {len(df_ta)} rows saved to {output_path}")
    
    return df_ta