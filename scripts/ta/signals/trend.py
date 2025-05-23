import pandas as pd
import numpy as np

from scripts.ta.ta_helpers import (
    validate_and_align_series,
    line_cross, 
    trend_status,
    obos_status,
    above_threshold
    )


# (TODO) some params are hardcoded!
# (TODO) Ichimoku

# (TODO) Schaff Trend Cycle (STC)


# Average Directional Movement Index (ADX)
def adx_signals(
    adx: pd.Series, 
    adx_pos: pd.Series, 
    adx_neg: pd.Series, 
    adx_threshold: float = 20.0, 
    name: str = 'adx'
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"adx": adx, "adx_pos": adx_pos, 'adx_neg': adx_neg}
    )
    
    adx = series["adx"]
    adx_pos = series["adx_pos"]
    adx_neg = series["adx_neg"]
    
    signals = {
        f"{name}_strength": above_threshold(adx, threshold=adx_threshold), # or 25
        f"{name}_signal_cross": line_cross(adx_pos, signal=adx_neg),
    }
    
    return pd.DataFrame(signals)


# Aroon Up, Down and Oscillator
def aroon_signals(
    aroon_up: pd.Series, 
    aroon_down: pd.Series, 
    aroon_osc: pd.Series,
    centerline: float = 0.0,
    name: str = "aroon"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {
            "aroon_up": aroon_up, 
            "aroon_down": aroon_down, 
            'aroon_osc': aroon_osc,
        }
    )
    
    aroon_up = series["aroon_up"]
    aroon_down = series["aroon_down"]
    aroon_osc = series["aroon_osc"]
    
    # Trend confirmation: bull or bear
    def aroon_trend(
        aroon_up: pd.Series,
        aroon_down: pd.Series,
        bull_level: float = 50.0,
        bear_level: float = 50.0,
        no_trend_level: float = 20.0,
        fill: bool = False
    ) -> pd.Series:
        """Returns trend confirmed by aroon"""
        bull = (aroon_up > bull_level) & (aroon_down < bull_level)
        bear = (aroon_down > bear_level) & (aroon_up < bear_level)
        no_trend = (aroon_up < no_trend_level) & (aroon_down < no_trend_level) 

        signal = pd.Series(
            np.select([bull, bear, no_trend], [1, -1, 0], default=np.nan),
            index=aroon_up.index
        )
        
        return signal.fillna(0).astype(int) if fill else signal
        
    signals = {
        f"{name}_osc_cross": line_cross(aroon_osc, signal=centerline),
        f"{name}_osc_trend": trend_status(aroon_osc, baseline=centerline),
        f"{name}_trend": aroon_trend(aroon_up, aroon_down),
    }
    
    return pd.DataFrame(signals)


# Commodity Channel Index (CCI)
def cci_signals(
    cci: pd.Series,
    cci_smooth: pd.Series, 
    overbought: float = 200.0, 
    oversold: float = -200.0,
    centerline: float = 0.0, 
    name: str = "cci"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"cci": cci, "cci_smooth": cci_smooth}
    )
    
    cci = series["cci"]
    cci_smooth = series["cci_smooth"]
    
    signals = {
        f"{name}_obos_1": obos_status(cci, overbought, oversold),
        f"{name}_center_cross_1": line_cross(cci, signal=centerline),
        f"{name}_trend_1": trend_status(cci, baseline=centerline),
        f"{name}_obos_2": obos_status(cci_smooth, overbought, oversold),
        f"{name}_center_cross_2": line_cross(cci_smooth, signal=centerline),
        f"{name}_trend_2": trend_status(cci_smooth, baseline=centerline),
    }
    
    return pd.DataFrame(signals)
    
# Detrended Price Oscillator (DPO)
def dpo_signals(
    dpo: pd.Series,
    dpo_smooth: pd.Series, 
    centerline: float = 0.0, 
    name: str = "dpo"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"dpo": dpo, "dpo_smooth":dpo_smooth}
    )
    
    dpo = series["dpo"]
    dpo_smooth = series["dpo_smooth"]
    
    signals = {
        f"{name}_center_cross_1": line_cross(dpo, signal=centerline),
        f"{name}_center_cross_2": line_cross(dpo_smooth, signal=centerline),
        f"{name}_trend_1": trend_status(dpo, baseline=centerline),
        f"{name}_trend_2": trend_status(dpo_smooth, baseline=centerline),
    }
    
    return pd.DataFrame(signals)


# Exponential Moving Average (EMA)
def ema_signals(
    close: pd.Series, 
    ema_1: pd.Series, 
    ema_2: pd.Series, 
    name: str = "ema"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"close": close, "ema_1": ema_1, 'ema_2': ema_2}
    )
    
    close = series["close"]
    ema_1 = series["ema_1"]
    ema_2 = series["ema_2"]
    
    signals = {
        f"{name}_signal_cross": line_cross(ema_1, signal=ema_2),
        f"{name}_short_cross": line_cross(close, signal=ema_1),
        f"{name}_long_cross": line_cross(close, signal=ema_2),
        f"{name}_short_trend": trend_status(close, baseline=ema_1),
        f"{name}_long_trend": trend_status(close, baseline=ema_2),
    }
    
    return pd.DataFrame(signals)


# Simple Moving Average (SMA)
def sma_signals(
    close: pd.Series, 
    sma_1: pd.Series, 
    sma_2: pd.Series, 
    name: str = "sma"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"close": close, "sma_1": sma_1, 'sma_2': sma_2}
    )
    
    close = series["close"]
    sma_1 = series["sma_1"]
    sma_2 = series["sma_2"]
    
    signals = {
        f"{name}_signal_cross": line_cross(sma_1, signal=sma_2),
        f"{name}_short_cross": line_cross(close, signal=sma_1),
        f"{name}_long_cross": line_cross(close, signal=sma_2),
        f"{name}_short_trend": trend_status(close, baseline=sma_1),
        f"{name}_long_trend": trend_status(close, baseline=sma_2),
    }
    
    return pd.DataFrame(signals)


# Weighted Moving Average (WMA)
def wma_signals(
    close: pd.Series, 
    wma_1: pd.Series, 
    wma_2: pd.Series, 
    name: str = "wma"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"close": close, "wma_1": wma_1, 'wma_2': wma_2}
    )
    
    close = series["close"]
    wma_1 = series["wma_1"]
    wma_2 = series["wma_2"]
    
    signals = {
        f"{name}_signal_cross": line_cross(wma_1, signal=wma_2),
        f"{name}_short_cross": line_cross(close, signal=wma_1),
        f"{name}_long_cross": line_cross(close, signal=wma_2),
        f"{name}_short_trend": trend_status(close, baseline=wma_1),
        f"{name}_long_trend": trend_status(close, baseline=wma_2),
    }
    
    return pd.DataFrame(signals)


# Pring's Know Sure Thing Oscillator (KST)
def kst_signals(
    kst: pd.Series, 
    kst_signal: pd.Series,
    centerline: float = 0.0,
    name: str ="kst"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"kst": kst, "kst_signal": kst_signal}
    )
    
    kst = series["kst"]
    kst_signal = series["kst_signal"]
    
    signals = {
        f"{name}_signal_cross": line_cross(kst, signal=kst_signal),
        f"{name}_center_cross": line_cross(kst, signal=centerline),
        f"{name}_trend": trend_status(kst, baseline=centerline),
    }
    
    return pd.DataFrame(signals)


# Moving Average Convergence Divergence (MACD)
def macd_signals(
    macd: pd.Series, 
    macd_signal: pd.Series,
    macd_diff: pd.Series,
    centerline: float = 0.0,
    name: str = "macd"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"macd": macd, "macd_signal": macd_signal, "macd_diff": macd_diff}
    )
    
    macd = series["macd"]
    macd_signal = series["macd_signal"]
    macd_diff = series["macd_diff"]

    signals = {
        f"{name}_center_cross": line_cross(macd, signal=centerline),
        f"{name}_signal_cross": line_cross(macd, signal=macd_signal),
        f"{name}_trend_1": trend_status(macd, baseline=centerline),
        f"{name}_trend_2": trend_status(macd_diff, baseline=centerline),
    }
    
    return pd.DataFrame(signals)


# Mass Index (MI)
def mi_signals(
    mi: pd.Series,
    mi_smooth: pd.Series, 
    centerline: float = 26.5, 
    name: str = "mi"
) -> pd.DataFrame:
    series = validate_and_align_series({"mi": mi, "mi_smooth": mi_smooth})
    
    mi = series["mi"]
    mi_smooth = series["mi_smooth"]
    
    signals = {
        f"{name}_signal_cross": line_cross(mi, signal=mi_smooth), # custom
        f"{name}_center_cross": line_cross(mi, signal=centerline),
        f"{name}_trend": trend_status(mi, baseline=centerline),
    }
    
    return pd.DataFrame(signals)

# Parabolic Stop and Reverse (Parabolic SAR)
def psar_signals(
    psar_down: pd.Series,
    psar_up: pd.Series,
    psar_down_ind: pd.Series,
    psar_up_ind: pd.Series,
    name: str = "psar"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {
            "psar_down": psar_down, 
            "psar_up": psar_up,
            "psar_down_ind": psar_down_ind, 
            "psar_up_ind": psar_up_ind
        }
    )
    
    psar_down = series["psar_down"]
    psar_up = series["psar_up"]
    psar_down_ind = series["psar_down_ind"]
    psar_up_ind = series["psar_up_ind"]
    
    def psar_reversals(psar_down_ind, psar_up_ind):
        """
        Returns:
            +1 for uptrend reversal, 
            -1 for downtrend reversal
            0 for no reversal
        """
        return psar_up_ind + psar_down_ind.replace(1, -1)
    
    def psar_trend(psar_down, psar_up):
        bear = psar_down.notna().astype(int)
        bull = psar_up.notna().astype(int)
        return bear + bull
    
    signals = {
        f"{name}_signal_cross": psar_reversals(psar_down_ind, psar_up_ind),
        f"{name}_trend": psar_trend(psar_down, psar_up)
    }

    return pd.DataFrame(signals)


# Triple Exponentially Smoothed Moving Average (TRIX)
def trix_signals(
    trix: pd.Series, 
    trix_signal: pd.Series,
    centerline: float = 0.0,
    name: str = "trix"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"trix": trix, "trix_signal": trix_signal}
    )
    
    trix = series["trix"]
    trix_signal = series["trix_signal"]

    signals = {
        f"{name}_signal_cross": line_cross(trix, signal=trix_signal),
        f"{name}_center_cross": line_cross(trix, signal=centerline),
        f"{name}_trend": trend_status(trix, baseline=centerline),
    }
    
    return pd.DataFrame(signals)


# Vortex Indicator (VI)
def vi_signals(
    vi_pos: pd.Series, 
    vi_neg: pd.Series, 
    name: str = "vi"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"vi_pos": vi_pos, "vi_neg": vi_neg}
    )
    
    vi_pos = series["vi_pos"]
    vi_neg = series["vi_neg"]
    
    signals = {
        f"{name}_signal_cross": line_cross(vi_pos, signal=vi_neg),
    }
    
    return pd.DataFrame(signals)