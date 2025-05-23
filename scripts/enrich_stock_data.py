import pandas as pd
#from scripts.ta_indicators import daily_log_return, get_all_indicators

import logging
log = logging.getLogger("airflow.task")

# (TODO) df_signals
def enrich_with_indicators(df):
    
    from scripts.ta.indicators.others import daily_rets, daily_log_rets
    from scripts.ta.ta_indicators import get_all_indicators
    # from scripts.ta.ta_signals import get_all_signals
    
    # Normalize for safety (no need if parquet)
    df['date'] = pd.to_datetime(df['date'])
    num_cols = ['open', 'high', 'low', 'close', 'volume']
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
    
    # Sort
    df = df.sort_values('date')
    
    # Daily returns
    df['daily_return'] = daily_rets(df["close"]) #df['close'].pct_change().fillna(0)
    df['daily_log_return'] = daily_log_rets(df['close'])
    
    # Compute ta_indicators (returns new df)
    df_ta = get_all_indicators(df)
    
    if df_ta.empty:
        raise ValueError("No data enriched")
    
    # (TODO) df_signals
    # df_signals = get_all_signals(df_ta)
    
    
    
    return df_ta
