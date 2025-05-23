import pandas as pd
import numpy as np
import ast

from config.settings import get_ta_params_file

# ---------- INDICATORS helpers ------------# 

def safe_eval_series(series: pd.Series) -> pd.Series:
    
    def safe_eval(val):
        try:
            return ast.literal_eval(val) if pd.notna(val) else () # None
        except Exception:
            return () # None
    
    return series.map(safe_eval)


def get_ta_params(default_params=True, to_dictionary=False):
    
    ta_params_path = get_ta_params_file()
    params_col = "params_default" if default_params else "params_custom"
    
    ta_params_df = pd.read_csv(ta_params_path, encoding="utf-8-sig", index_col="short_name")[params_col]
    
    if to_dictionary:
        # as dict
        ta_params = ta_params_df.to_dict()
    else:
        # as normalized series
        ta_params = safe_eval_series(ta_params_df)

    return ta_params


def get_ohlcv(df):
    df.columns = [col.lower() for col in df.columns]
    
    for col in ["open", "high", "low", "close", "volume"]:
        if col not in df.columns:
            raise KeyError(f"Missing column: {col}")
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    open = df["open"]
    high = df["high"]
    low = df["low"]
    close = df["close"]
    volume = df["volume"]
    
    return open, high, low, close, volume


# ---------- SIGNALS helpers ------------#

def validate_and_align_series(series_dict: dict[str, pd.Series]) -> dict[str, pd.Series]:
    """Validates numeric values and index alignment"""
    validated = {}
    base_index = None

    for name, series in series_dict.items():
        if not isinstance(series, pd.Series):
            raise TypeError(f"Expected pd.Series for '{name}', got {type(series).__name__}")
        
        numeric_series = pd.to_numeric(series, errors="coerce")

        if numeric_series.isnull().all():
            raise ValueError(f"'{name}' contains no valid numeric values.")
        
        if base_index is None:
            base_index = numeric_series.index
        elif not numeric_series.index.equals(base_index):
            raise ValueError(f"'{name}' index does not match the base index.")
        
        validated[name] = numeric_series

    return validated

def line_cross(line, signal, safe_margin=0.0):
    """
    Detects crosses between a line and a signal line/value
    Returns: +1, -1, or 0
    """
    return (line > signal + safe_margin).astype(int).diff().fillna(0).astype(int) 

def trend_status(line, baseline, safe_margin=0.0):
    """
    Detects if line is above/below a baseline
    Accespts a margin
    Returns: +1, -1, or 0
    """
    return (line > baseline + safe_margin).astype(int) - (line < baseline - safe_margin).astype(int)

def obos_status(series: pd.Series, overbought: float, oversold: float) -> pd.Series:
    """
    Classifies series into oversold (+1 = buy), overbought (-1 = sell), or neutral (0).
    """
    return pd.Series(
        np.where(
            series < oversold, 1,
            np.where(series > overbought, -1, 0)
        ),
        index=series.index
    )

def below_threshold(series: pd.Series, threshold: float) -> pd.Series:
    """Returns 1 if value < threshold, else 0"""
    return (series < threshold).astype(int) 
    
def above_threshold(series: pd.Series, threshold: float) -> pd.Series:
    """Returns 1 if value > threshold, else 0."""
    return (series > threshold).astype(int) 

