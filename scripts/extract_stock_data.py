import pandas as pd
from pathlib import Path
#import yfinance as yf
#from scripts.utils.etl_utils import load_metadata, update_metadata

import logging
log = logging.getLogger("airflow.task")

def fetch_stock_data(
    symbol, 
    period='10y', 
    interval='1d', 
    start_date=None, 
    end_date=None
    ):
    """
    Returns stock data from yfinance
    Period is omitted if start and end dates provided
    """
    
    import yfinance as yf
    
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
        raise ValueError("No data returned from cleaning")
    
    return df
