import pandas as pd
from pathlib import Path
#import pandas_market_calendars as mcal
#from scripts.utils.etl_utils import yf_interval_to_pandas_freq

import logging
log = logging.getLogger("airflow.task")
  
def validate_missing_time_full_year(df, date_col='date', freq='D'):
    """Checks for missing days in a year"""
    
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)

    actual = df[date_col].dt.round(freq).drop_duplicates()
    expected = pd.date_range(start=actual.min(), end=actual.max(), freq=freq)

    missing = expected.difference(actual)

    # If only the last timestamp is missing, skip it
    if len(missing) == 1 and missing[0] == expected[-1]:
        log.warning(f"Missing last timestamp: {missing[0]}")
        return []

    return missing.to_list()


def validate_missing_time_trading_days(df, calendar, date_col='date', freq='D'):
    """Checks for missing days in a trading calendar year"""
    
    import pandas_market_calendars as mcal
    cal = mcal.get_calendar(calendar)
    
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    
    #cal = mcal.get_calendar(calendar)
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
    
    if len(missing) == 1 and missing[0] == expected[-1]:
        log.warning(f"Missing last timestamp: {missing[0]}")
        return []
    
    return missing.to_list()


def validate_time_series(df, interval, use_calendar=True, date_col='date', calendar="NYSE"):
    """
    Checks for missing days in both year/trading calendar.
    Accepts interval and converts to frequency
    """
    
    from scripts.utils.etl_utils import yf_interval_to_pandas_freq
    freq = yf_interval_to_pandas_freq(interval)
    
    if use_calendar:
        missing = validate_missing_time_trading_days(df, calendar, date_col, freq)
    else:
        missing = validate_missing_time_full_year(df, date_col, freq)
           
    return missing
