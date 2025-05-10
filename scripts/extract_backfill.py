import pandas as pd
import yfinance as yf
from pathlib import Path


#import importlib
#import scripts.etl_utils
#importlib.reload(scripts.etl_utils)

from scripts.etl_utils import load_metadata, update_metadata

# (DONE) some refactoring for prod ready, and logger

# @ task: extract data
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
    output_dir = project_root / "data" / symbol / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    suffix = ".csv.gz" if compress else ".csv"
    output_path = output_dir / f"{symbol}_{interval}_raw{suffix}"
    
    df.to_csv(output_path, index=False, compression='gzip' if compress else None)
    
    # Save metadata
    meta = load_metadata()
    meta_key = f"{symbol}_{interval}"
    update_metadata(df['date'], interval, meta, meta_key)
    
    print(f"[SAVE] {symbol} → {output_path.name} ({len(df)} rows)")
    
    return output_path