import pandas as pd
#from scripts.ta_indicators import daily_log_return, get_all_indicators

import logging
log = logging.getLogger("airflow.task")


def enrich_with_indicators(df):
    
    from scripts.ta_indicators import daily_log_return, get_all_indicators
    
    # Normalize for safety (no need if parquet)
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
    
    if df_ta.empty:
        raise ValueError("No data enriched")
    
    return df_ta
