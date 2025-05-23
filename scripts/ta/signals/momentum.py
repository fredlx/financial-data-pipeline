import pandas as pd
import numpy as np

# (TODO) some params are hardcoded!

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


# Awesome Oscilator (AO)
def ao_signals(
    ao: pd.Series,
    ao_smooth: pd.Series, 
    centerline: float = 0.0,
    name: str = "ao"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"ao": ao, "ao_smooth": ao_smooth}
        )
    
    ao = series["ao"]
    ao_smooth = series["ao_smooth"]
    
    signals = {
        f"{name}_center_cross": line_cross(ao, signal=centerline),
        f"{name}_trend": trend_status(ao, baseline=centerline),
        # alt
        f"{name}_center_cross_2": line_cross(ao_smooth, signal=centerline),
        f"{name}_trend_2": trend_status(ao_smooth, baseline=centerline),
    }
    
    return pd.DataFrame(signals)

# Kaufman's Adaptive Moving Average (KAMA)
def kama_signals(
    kama: pd.Series, 
    close: pd.Series, 
    name: str = "kama"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"close": close, "kama": kama}
    )

    close = series["close"]
    kama = series["kama"]

    signals = {
        f"{name}_signal_cross": line_cross(close, signal=kama),
        f"{name}_trend": trend_status(close, baseline=kama),
    }

    return pd.DataFrame(signals)

# Percentage Price Oscillator (PPO)
def ppo_signals(
    ppo: pd.Series, 
    ppo_signal: pd.Series, 
    centerline: float = 0.0,
    name: str = "ppo"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"ppo": ppo, "ppo_signal": ppo_signal}
    )

    ppo = series["ppo"]
    ppo_signal = series["ppo_signal"]
    
    signals = {
        f"{name}_signal_cross": line_cross(ppo, signal=ppo_signal),
        f"{name}_center_cross": line_cross(ppo, signal=centerline),
        f"{name}_trend": trend_status(ppo, baseline=centerline),
        # alt
        f"{name}_center_cross_2": line_cross(ppo_signal, signal=centerline),
        f"{name}_trend_2": trend_status(ppo_signal, baseline=centerline),
    }
    
    return pd.DataFrame(signals)

# Percentage Volume Oscillator (PVO)
def pvo_signals(
    pvo: pd.Series, 
    pvo_signal: pd.Series, 
    centerline: float = 0.0,
    name: str = "pvo"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"pvo": pvo, "pvo_signal": pvo_signal}
    )

    pvo = series["pvo"]
    pvo_signal = series["pvo_signal"]
    
    signals = {
        f"{name}_signal_cross": line_cross(pvo, signal=pvo_signal),
        f"{name}_center_cross": line_cross(pvo, signal=centerline),
        f"{name}_trend": trend_status(pvo, baseline=centerline),
        # alt
        f"{name}_center_cross_2": line_cross(pvo_signal, signal=centerline),
        f"{name}_trend_2": trend_status(pvo_signal, baseline=centerline),
    }
    
    return pd.DataFrame(signals)

# Rate of Change (ROC)
def roc_signals(
    roc: pd.Series,
    roc_smooth: pd.Series, 
    overbought: float = 8.0, 
    oversold: float = -8.0, 
    centerline: float = 0.0,
    name: str = "roc"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"roc": roc, "roc_smooth": roc_smooth}
    )

    roc = series["roc"]
    roc_smooth = series["roc_smooth"]
    
    signals = {
        f"{name}_obos": obos_status(roc, overbought, oversold),
        f"{name}_center_cross": line_cross(roc, signal=centerline),
        f"{name}_trend": trend_status(roc, baseline=centerline),
        # alt
        f"{name}_obos_2": obos_status(roc_smooth, overbought, oversold),
        f"{name}_center_cross_2": line_cross(roc_smooth, signal=centerline),
        f"{name}_trend_2": trend_status(roc_smooth, baseline=centerline),
    }
    
    return pd.DataFrame(signals)

# Relative Strength Index (RSI)
def rsi_signals(
    rsi: pd.Series,
    rsi_smooth: pd.Series,  
    overbought: float = 70.0, 
    oversold: float = 30.0, 
    centerline: float = 50.0,
    name: str = "rsi"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"rsi": rsi, "rsi_smooth": rsi_smooth}
    )

    rsi = series["rsi"]
    rsi_smooth = series["rsi_smooth"]
    
    signals = {
        f"{name}_obos": obos_status(rsi, overbought, oversold),
        f"{name}_center_cross": line_cross(rsi, signal=centerline),
        f"{name}_trend": trend_status(rsi, baseline=centerline),
        # alt
        f"{name}_obos_2": obos_status(rsi_smooth, overbought, oversold),
        f"{name}_center_cross_2": line_cross(rsi_smooth, signal=centerline),
        f"{name}_trend_2": trend_status(rsi_smooth, baseline=centerline),
        }
    
    return pd.DataFrame(signals)

# Stochastic Oscillator (STOCH)
def stoch_signals(
    stoch: pd.Series, 
    stoch_signal: pd.Series, 
    overbought: float = 80.0, 
    oversold: float = 20.0,
    centerline: float = 50.0,
    name: str = "stoch"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"stoch": stoch, "stoch_signal": stoch_signal}
    )
    
    stoch = series["stoch"]
    stoch_signal = series["stoch_signal"]
    
    signals = {
        f"{name}_obos": obos_status(stoch, overbought, oversold),
        f"{name}_signal_cross": line_cross(stoch, signal=stoch_signal),
        f"{name}_center_cross": line_cross(stoch, signal=centerline),
        f"{name}_trend": trend_status(stoch, baseline=centerline),
        # alt
        f"{name}_obos_2": obos_status(stoch_signal, overbought, oversold),
        f"{name}_center_cross_2": line_cross(stoch_signal, signal=centerline),
        f"{name}_trend_2": trend_status(stoch_signal, baseline=centerline),
    }
    
    return pd.DataFrame(signals)

# Stochastic RSI (STOCHRSI)
def stochrsi_signals(
    stochrsi: pd.Series,
    stochrsi_d: pd.Series, # signal line
    overbought: float = 0.9, 
    oversold: float = 0.1,
    centerline: float = 0.5, 
    name: str = 'stochrsi'
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"stochrsi": stochrsi, "stochrsi_d": stochrsi_d}
    )
    
    stochrsi = series["stochrsi"]
    stochrsi_d = series["stochrsi_d"]
    
    signals = {
        f"{name}_obos": obos_status(stochrsi, overbought, oversold),
        f"{name}_signal_cross": line_cross(stochrsi, signal=stochrsi_d),
        f"{name}_center_cross": line_cross(stochrsi, signal=centerline),
        f"{name}_trend": trend_status(stochrsi, baseline=centerline),
        # alt
        f"{name}_obos_2": obos_status(stochrsi_d, overbought, oversold),
        f"{name}_center_cross_2": line_cross(stochrsi_d, signal=centerline),
        f"{name}_trend_2": trend_status(stochrsi_d, baseline=centerline),
    }
    
    return pd.DataFrame(signals)

# True strength index (TSI)
def tsi_signals(
    tsi: pd.Series, 
    tsi_signal: pd.Series,
    overbought: float = 30.0, # 20
    oversold: float = -20.0,
    centerline: float = 0.0, 
    name: str = 'tsi'
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"tsi": tsi, "tsi_signal": tsi_signal}
    )
    
    tsi = series["tsi"]
    tsi_signal = series["tsi_signal"]

    signals = {
        f"{name}_obos": obos_status(tsi, overbought, oversold),
        f"{name}_signal_cross": line_cross(tsi, signal=tsi_signal),
        f"{name}_center_cross": line_cross(tsi, signal=centerline),
        f"{name}_trend": trend_status(tsi, baseline=centerline),
        # alt
        f"{name}_obos_2": obos_status(tsi_signal, overbought, oversold),
        f"{name}_center_cross_2": line_cross(tsi_signal, signal=centerline),
        f"{name}_trend_2": trend_status(tsi_signal, baseline=centerline),
    }
    
    return pd.DataFrame(signals)

# Ultimate Oscillator (UO)
def uo_signals(
    uo: pd.Series,
    uo_smooth: pd.Series,
    overbought: float = 70.0, 
    oversold: float = 40.0,  # 30
    centerline: float = 50.0,
    name: str = 'uo'
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"uo": uo, "uo_smooth": uo_smooth}
    )
    
    uo = series["uo"]
    uo_smooth = series["uo_smooth"]
    
    signals = {
        f"{name}_obos": obos_status(uo, overbought, oversold),
        f"{name}_center_cross": line_cross(uo, signal=centerline),
        f"{name}_trend": trend_status(uo, baseline=centerline),
        # alt
        f"{name}_obos_2": obos_status(uo, overbought, oversold),
        f"{name}_center_cross_2": line_cross(uo, signal=centerline),
        f"{name}_trend_2": trend_status(uo, baseline=centerline),
    }
    
    return pd.DataFrame(signals)

# Williams %R (WILLR)
def willr_signals(
    willr: pd.Series,
    willr_smooth: pd.Series,
    overbought: float = -20.0, 
    oversold: float = -80.0,
    centerline: float = -50.0,
    name: str = 'willr'
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"willr": willr, "willr_smooth": willr_smooth}
    )
    
    willr = series["willr"]
    willr_smooth = series["willr_smooth"]
    
    signals = {
        f"{name}_obos": obos_status(willr, overbought, oversold),
        f"{name}_center_cross": line_cross(willr, signal=centerline),
        f"{name}_trend": trend_status(willr, baseline=centerline),
        # alt
        f"{name}_obos_2": obos_status(willr_smooth, overbought, oversold),
        f"{name}_center_cross_2": line_cross(willr_smooth, signal=centerline),
        f"{name}_trend_2": trend_status(willr_smooth, baseline=centerline),
    }
    
    return pd.DataFrame(signals)