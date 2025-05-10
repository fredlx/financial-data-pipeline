import pandas as pd
import pandas_market_calendars as mcal



# @task: validate_data (full_year)
# 15T, 30T, D    
def validate_missing_time_full_year(df, date_col='date', freq='D'):
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)

    actual = df[date_col].dt.round(freq).drop_duplicates()
    expected = pd.date_range(start=actual.min(), end=actual.max(), freq=freq)

    missing = expected.difference(actual)

    # If only the last timestamp is missing, skip it
    if len(missing) == 1 and missing[0] == expected[-1]:
        return []

    return missing.to_list()


# @task: validate_data (use trading calendar)
def validate_missing_time_trading_days(df, date_col='date', freq='D', calendar='NYSE'):
    
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


def validate_time_series(df, date_col='date', freq='D', use_calendar=True):
    
    if use_calendar:
        missing = validate_missing_time_trading_days(df, date_col, freq)
    else:
        missing = validate_missing_time_full_year(df, date_col, freq)
        
    if missing:
        raise Exception(f"{len(missing)} missing timestamps. Example: {missing[:5]}") 
        
    return missing