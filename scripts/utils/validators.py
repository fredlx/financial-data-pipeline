import pandas as pd
import pandas_market_calendars as mcal
from pathlib import Path

from scripts.utils.etl_utils import yf_interval_to_pandas_freq

  
def validate_missing_time_full_year(df, date_col='date', freq='D'):
    """Checks for missing days in a year"""
    
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)

    actual = df[date_col].dt.round(freq).drop_duplicates()
    expected = pd.date_range(start=actual.min(), end=actual.max(), freq=freq)

    missing = expected.difference(actual)

    # If only the last timestamp is missing, skip it
    if len(missing) == 1 and missing[0] == expected[-1]:
        return []

    return missing.to_list()


def validate_missing_time_trading_days(df, date_col='date', freq='D', calendar='NYSE'):
    """Checks for missing days in a trading calendar year"""
    
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    
    cal = mcal.get_calendar(calendar)
    schedule = cal.schedule(start_date=df[date_col].min().date(), end_date=df[date_col].max().date())

    if freq == 'D':
        # Use trading days only (normalize both datetime at midnight just in case)
        expected = schedule.index.normalize()[:-1]
        actual = df[date_col].dt.normalize().unique()
    else:
        # Intraday validation on trading days (15T, 30T)
        expected = []
        for _, row in schedule.iterrows():
            intraday = pd.date_range(start=row['market_open'], end=row['market_close'], freq=freq)
            expected.extend(intraday)
        expected = pd.to_datetime(expected)[:-1]
        actual = df[date_col].dt.round(freq).drop_duplicates()

    missing = pd.DatetimeIndex(expected).difference(actual)
    
    # If only the last timestamp is missing, skip it
    if len(missing) == 1 and missing[0] == expected[-1]:
        return []
    
    return missing.to_list()


def validate_time_series(df, interval, use_calendar=True, date_col='date'):
    """
    Checks for missing days in both year/trading calendar.
    Accepts interval and converts to frequency
    """
    
    # convert yfinance interval to pandas frequency
    freq = yf_interval_to_pandas_freq(interval)
    
    if use_calendar:
        missing = validate_missing_time_trading_days(df, date_col, freq)
    else:
        missing = validate_missing_time_full_year(df, date_col, freq)
        
    #if missing:
    #    raise Exception(f"{len(missing)} missing timestamps. Example: {missing[:5]}") 
        
    return missing


def get_existing_dates(symbol, interval, year, month=None):
    """
    storage_check for processed parquet files
    Usage: date(2025, 5, 9) in existing
    """
    
    base_path = Path(f"data/{symbol}/processed")
    
    if month:
        filename = f"{symbol}_{interval}_{year}-{month:02d}.parquet"
    else:
        filename = f"{symbol}_{interval}_{year}.parquet"

    path = base_path / filename
    if not path.exists():
        return set()

    df = pd.read_parquet(path, columns=["date"])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return set(df["date"])