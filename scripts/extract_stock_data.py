import pandas as pd
#import yfinance as yf
from pathlib import Path
#from scripts.utils.etl_utils import load_metadata, update_metadata

def fetch_stock_data(
    symbol, 
    period='10y', 
    interval='1d', 
    start_date=None, 
    end_date=None, 
    **kwargs
    ):
    """
    Returns stock data from yfinance
    Period is omitted if start and end dates provided
    """
    import yfinance as yf  # DAG-slowdown offender
    
    symbol = symbol.upper()
    
    print(f"[FETCH] Downloading {symbol}")
    df = yf.download(
        tickers=symbol, 
        period=period,
        start=start_date,
        end=end_date,
        interval=interval, 
        auto_adjust=True, 
        progress=False
        )
    if df.empty:
        raise ValueError(f"No data returned for {symbol} with {period=} and {interval=}")
        
    return df


def clean_stock_data(df):
    
    df = df.reset_index()
    date_col = "Date" if "Date" in df.columns else "Datetime"  # intraday
    df = df[[date_col, 'Open', 'High', 'Low', 'Close', 'Volume']]
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    
    if df.empty:
        raise ValueError(f"No data")
    
    return df


def save_stock_data(df, symbol, interval, compress=True):
    
    symbol = symbol.upper()
    
    project_root = Path(__file__).resolve().parents[1]
    base_path = project_root / "data" / symbol / "raw"
    base_path.mkdir(parents=True, exist_ok=True)
    file_path = base_path / f"{symbol}_{interval}_raw"
    full_file_path = file_path.with_suffix(".csv.gz") if compress else file_path.with_suffix(".csv")
    
    # Save csv
    df.to_csv(
        full_file_path, 
        index=False, 
        compression='gzip' if compress else None)
    
    # Save metadata
    from scripts.utils.etl_utils import load_metadata, update_metadata  # for airflow
    
    meta = load_metadata()
    meta_key = f"{symbol}_{interval}"
    update_metadata(df['date'], interval, meta, meta_key)
    
    print(f"[SAVE] {symbol} → {full_file_path.name} ({len(df)} rows)")
    
    return str(full_file_path)  # no Path, for airflow

