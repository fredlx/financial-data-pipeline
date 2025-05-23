import pandas as pd
import numpy as np

# (TODO) some params are hardcoded!
# move helpres to ta_helpers

import importlib
import scripts.ta.ta_helpers
importlib.reload(scripts.ta.ta_helpers)


from scripts.ta.ta_helpers import (
    validate_and_align_series,
    line_cross, 
    trend_status,
    obos_status,
    above_threshold
    )

# (TODO) Accumulation/Distribution Index (ADI)

# Money Flow Index (MFI)
def mfi_signals(
    mfi: pd.Series,
    mfi_smooth: pd.Series,
    overbought: float = 80.0, 
    oversold: float = 20.0,
    centerline: float = 50.0, 
    name: str = 'mfi'
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"mfi": mfi, "mfi_smooth": mfi_smooth}
    )
    
    mfi = series["mfi"]
    mfi_smooth = series["mfi_smooth"]

    signals = {
        f"{name}_obos": obos_status(mfi, overbought, oversold),
        f"{name}_center_cross": line_cross(mfi, signal=centerline),
        f"{name}_trend": trend_status(mfi, baseline=centerline),
        # alt
        f"{name}_obos_2": obos_status(mfi_smooth, overbought, oversold),
        f"{name}_center_cross_2": line_cross(mfi_smooth, signal=centerline),
        f"{name}_trend_2": trend_status(mfi_smooth, baseline=centerline),
    }
    
    return pd.DataFrame(signals)


# Chaikin Money Flow (CMF)
def cmf_signals(
    cmf: pd.Series,
    cmf_smooth: pd.Series,  
    centerline: float = 0.0,
    safe_margin: float = 0.05,
    name: str = 'cmf'
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"cmf": cmf, "cmf_smooth": cmf_smooth}
    )
    
    cmf = series["cmf"]
    cmf_smooth = series["cmf_smooth"]
    
    signals = {
       f"{name}_center_cross": line_cross(cmf, signal=centerline, safe_margin=safe_margin), # no margin?
       f"{name}_trend": trend_status(cmf, baseline=centerline, safe_margin=safe_margin),
       # alt
       f"{name}_center_cross_2": line_cross(cmf_smooth, signal=centerline, safe_margin=safe_margin), # no margin?
       f"{name}_trend_2": trend_status(cmf_smooth, baseline=centerline, safe_margin=safe_margin),
    }
    
    return pd.DataFrame(signals)

# Ease of movement (EMV)
def emv_signals(
    emv: pd.Series, 
    emv_signal: pd.Series,
    centerline: float = 0.0,
    name: str ='emv',
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"emv": emv, "emv_signal": emv_signal}
    )
    
    emv = series["emv"]
    emv_signal = series["emv_signal"]
    
    signals = {
        f"{name}_signal_cross": line_cross(emv, signal=emv_signal),
        f"{name}_center_cross": line_cross(emv, signal=centerline),
        f"{name}_trend": trend_status(emv, baseline=centerline),
        # alt
        f"{name}_center_cross_2": line_cross(emv_signal, signal=centerline),
        f"{name}_trend_2": trend_status(emv_signal, baseline=centerline),
    }
    
    return pd.DataFrame(signals)

# Force Index (FI)
def fi_signals(
    fi: pd.Series,
    fi_smooth: pd.Series,
    centerline: float = 0.0, 
    name: str = 'fi',
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"fi": fi, "fi_smooth": fi_smooth}
    )
    
    fi = series["fi"]
    fi_smooth = series["fi_smooth"]
    
    signals = {
        f"{name}_center_cross": line_cross(fi, signal=centerline),
        f"{name}_trend": trend_status(fi, baseline=centerline),
        # alt
        f"{name}_center_cross_2": line_cross(fi_smooth, signal=centerline),
        f"{name}_trend_2": trend_status(fi_smooth, baseline=centerline),
    }
    
    return pd.DataFrame(signals)

# Negative Volume Index (NVI)
def nvi_signals(
    nvi: pd.Series, 
    nvi_signal: pd.Series, 
    name: str = 'nvi'
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"nvi": nvi, "nvi_signal": nvi_signal}
    )
    
    nvi = series["nvi"]
    nvi_signal = series["nvi_signal"]

    signals = {
        f"{name}_signal_cross": line_cross(nvi, signal=nvi_signal),
    }
    
    return pd.DataFrame(signals)


# On-balance volume (OBV)
def obv_signals(
    obv: pd.Series, 
    obv_signal: pd.Series, 
    name: str = 'obv'
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"obv": obv, "obv_signal": obv_signal}
    )
    
    obv = series["obv"]
    obv_signal = series["obv_signal"]
    
    signals = {
        f"{name}_trend": trend_status(obv, baseline=obv_signal),
    }
    
    return pd.DataFrame(signals)


# (TODO) Volume-price trend (VPT)


# Volume Weighted Average Price (VWAP)
def vwap_signals(
    vwap: pd.Series, 
    close: pd.Series, 
    name: str = 'vwap'
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"vwap": vwap, "close": close}
    )
    
    vwap = series["vwap"]
    close = series["close"]

    signals = {
        f"{name}_signal_cross": line_cross(close, signal=vwap),
        f"{name}_trend": trend_status(close, baseline=vwap),
    }
    
    return pd.DataFrame(signals)